"""
RevenueAI 360 - End-to-End & Unit Test Suite
Validates the complete First Vertical Slice and required test scenarios:
1. Inbound Lead -> Identity -> Research -> Qualification -> Knowledge -> Sales -> Guardrail -> Evaluator -> Communication -> Approval
2. Support Case -> Context -> RAG -> Customer Service Response
3. Repeat Complaint -> SLA Breach -> Escalation -> Internal Slack Tool -> Customer Ack
4. Guardrail REVISE trigger -> Revision loop -> Evaluator PASS
"""

import os
os.environ["LLM_PROVIDER"] = "deterministic_demo"

import pytest
import asyncio
from domain.database import init_db, SessionLocal
from domain.models import CustomerAccount, Person, ChannelIdentity, Lead, PendingAction
from shared.state import NormalisedEvent, SharedWorkflowState
from agents.manager import customer_journey_manager
from services.demo_seeder import seed_demo_data
from services.identity import identity_service
from services.customer360 import customer360_service
from services.next_best_action import next_best_action_service
from services.ai_demo_builder import ai_demo_builder
from tools.registry import tool_registry


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure database and seed data are initialized."""
    init_db()
    asyncio.run(seed_demo_data())


@pytest.mark.asyncio
async def test_scenario_1_inbound_lead_vertical_slice():
    """
    E2E SCENARIO 1:
    Inbound lead enquiry from Nexa Logistics
    -> Normalised event
    -> Identity resolution
    -> Journey Manager
    -> Research Agent
    -> Qualification Agent (DISCOVERY_REQUIRED)
    -> Knowledge Agent (RAG)
    -> Sales Agent
    -> Guardrail (PASS)
    -> Evaluator (PASS)
    -> Communication Agent (tier2_approval)
    -> Pending Action created.
    """
    event = NormalisedEvent(
        event_id="test-evt-001",
        channel="email",
        external_identity="marcus.vance@nexalogistics.com",
        subject="AI Customer Service Automation inquiry for Nexa Logistics",
        content="We handle 12,000 shipments weekly. Repetitive carrier tracking inquiries are overwhelming our dispatch desks. Looking for an AI copilot solution.",
    )

    state = SharedWorkflowState(
        workflow_id="wf-lead-test-01",
        trace_id="trc-lead-test-01",
        event=event,
    )

    final_state = await customer_journey_manager.execute_workflow(state)

    # 1. Assert Identity Resolved
    assert final_state.customer_identity is not None
    assert "Nexa" in final_state.customer_identity.account_name
    assert final_state.customer_identity.person_name == "Marcus Vance"

    # 2. Assert Intent & Plan
    assert final_state.intent == "lead"
    assert "Account Research" in final_state.execution_plan

    # 3. Assert Research Agent Output
    assert final_state.research_output is not None
    assert len(final_state.research_output.technology_signals) > 0
    assert len(final_state.evidence) > 0

    # 4. Assert Qualification Agent Output (explainable DISCOVERY_REQUIRED)
    assert final_state.qualification_output is not None
    assert final_state.qualification_output.status == "DISCOVERY_REQUIRED"
    assert len(final_state.qualification_output.unknowns) >= 1
    assert len(final_state.qualification_output.discovery_questions) >= 1

    # 5. Assert RAG Citations
    assert len(final_state.citations) > 0
    assert any("Copilot" in c.document_title or "SLA" in c.document_title for c in final_state.citations)

    # 6. Assert Sales Strategy Output
    assert final_state.sales_output is not None
    assert "Marcus" in final_state.sales_output.draft_outreach_message

    # 7. Assert Guardrail & Evaluator Verdict
    assert len(final_state.guardrail_results) > 0
    assert final_state.guardrail_results[-1].verdict == "PASS"
    assert len(final_state.evaluations) > 0
    assert final_state.evaluations[-1].verdict == "PASS"

    # 8. Assert Communication & HITL Tier 2 Action
    assert final_state.final_response is not None
    assert final_state.final_response.approval_tier == "tier2_approval"
    assert len(final_state.pending_actions) == 1
    assert final_state.pending_actions[0].status == "PENDING"
    assert final_state.status == "WAITING_APPROVAL"


@pytest.mark.asyncio
async def test_scenario_2_customer_support_request():
    """
    E2E SCENARIO 2:
    Customer raises operational support ticket
    -> Customer360 Context retrieved
    -> Knowledge / RAG Agent
    -> Customer Service Agent
    -> Guardrail & Evaluator
    -> Service response formatted.
    """
    event = NormalisedEvent(
        event_id="test-evt-002",
        channel="webchat",
        external_identity="elena.rostova@nexalogistics.com",
        subject="Freight Tracking Status",
        content="Can you provide updated ETA for shipment container MSCU-948192 from Chicago to Detroit?",
    )

    state = SharedWorkflowState(
        workflow_id="wf-support-test-02",
        trace_id="trc-support-test-02",
        event=event,
    )

    final_state = await customer_journey_manager.execute_workflow(state)

    assert final_state.intent == "support"
    assert final_state.service_output is not None
    assert "tracking telemetry" in final_state.service_output.recommended_solution.lower()
    assert final_state.guardrail_results[-1].verdict == "PASS"


@pytest.mark.asyncio
async def test_scenario_3_repeat_complaint_and_escalation():
    """
    E2E SCENARIO 3:
    Customer complains that issue was reported multiple times
    -> Complaint Resolution Agent detects repeat complaint & SLA breach
    -> Escalation Agent notifies Engineering via internal tool
    -> Customer acknowledgement prepared.
    """
    event = NormalisedEvent(
        event_id="test-evt-003",
        channel="email",
        external_identity="marcus.vance@nexalogistics.com",
        subject="URGENT: Issue reported multiple times without resolution",
        content="I have complained about the GPS telemetry outage multiple times now and we have had zero updates! Our clients are furious. Why is this still not fixed?",
    )

    state = SharedWorkflowState(
        workflow_id="wf-complaint-test-03",
        trace_id="trc-complaint-test-03",
        event=event,
    )

    final_state = await customer_journey_manager.execute_workflow(state)

    assert final_state.intent == "complaint"
    assert final_state.complaint_output is not None
    assert final_state.complaint_output.repeat_occurrence_detected is True
    assert final_state.complaint_output.sla_breached is True
    assert final_state.complaint_output.escalation_required is True

    # Escalation Agent Output
    assert final_state.escalation_output is not None
    assert final_state.escalation_output.escalation_target == "Engineering"
    assert final_state.escalation_output.priority == "URGENT"


@pytest.mark.asyncio
async def test_scenario_4_next_best_action_complaint_suppression():
    """
    NBA TEST:
    Verifies that when an account has an active critical complaint,
    the Next-Best-Action service strictly prioritizes complaint de-escalation
    and sets suppress_promotions=True.
    """
    db = SessionLocal()
    try:
        acc = db.query(CustomerAccount).filter(CustomerAccount.domain == "nexalogistics.com").first()
        c360 = customer360_service.get_context(acc.id, db_session=db)
        
        # Inject simulated critical complaint in c360
        c360.complaints.append({
            "id": "comp-crit-01",
            "severity": "CRITICAL",
            "complaint_text": "Missed carrier SLA",
            "repeat_count": 3,
            "sla_breached": True,
        })

        nba = next_best_action_service.evaluate(c360)
        assert nba.action_type == "ESCALATE_AND_RESOLVE_COMPLAINT"
        assert nba.suppress_promotions is True
        assert "SUPPRESSED" in nba.explainable_reason
    finally:
        db.close()


def test_customer_ai_demo_builder():
    """
    Feature TEST:
    Verifies Create Customer AI Demo solution architecture generation.
    """
    spec = ai_demo_builder.generate_demo(
        account_name="Nexa Logistics (Fictional Demo)",
        customer_problem="Manual customer service overhead handling 12,000 weekly freight status inquiries.",
        discovery_notes="Legacy SAP and 4 regional operating centers.",
    )

    assert spec.account_name == "Nexa Logistics (Fictional Demo)"
    assert len(spec.proposed_agents) == 3
    assert len(spec.proposed_tools) == 4
    assert len(spec.prototype_to_production_roadmap) == 3
    assert "disclaimer" in spec.model_dump()
    assert "solution_architecture_diagram" in spec.model_dump()


@pytest.mark.asyncio
async def test_scenario_5_guardrail_revision_cycle():
    """
    E2E SCENARIO 4 from Section 29:
    Unsupported claim / unauthorized discount
    -> Guardrail flags REVISE
    -> Sales Agent revises draft
    -> Evaluator PASS
    """
    from agents.guardrail_agent import GuardrailAgent
    from agents.sales_agent import SalesAgent
    from shared.state import SalesStrategyResult, GuardrailResult

    event = NormalisedEvent(
        event_id="test-gr-01",
        channel="email",
        external_identity="marcus.vance@nexalogistics.com",
        subject="Pricing Inquiry",
        content="What discounts can you offer?",
    )

    state = SharedWorkflowState(
        workflow_id="wf-gr-test-01",
        trace_id="trc-gr-test-01",
        event=event,
    )
    from shared.state import ResolvedIdentity, QualificationResult
    state.customer_identity = ResolvedIdentity(
        account_name="Nexa Logistics",
        person_name="Marcus Vance",
        is_known=True,
    )
    state.intent = "lead"
    state.qualification_output = QualificationResult(
        status="DISCOVERY_REQUIRED",
        business_problem="Automation of tracking",
        intent_level="HIGH",
        technical_fit="Strong",
        unknowns=["Budget"],
        discovery_questions=["What is the budget?"],
        recommended_next_action="Discovery call",
    )

    # 1. Simulate an unauthorized financial commitment drafted by agent
    state.sales_output = SalesStrategyResult(
        sales_objective="Close deal quickly",
        tailored_value_proposition="Fast tracking",
        recommended_commercial_motion="Direct purchase",
        draft_outreach_message="We promise 100% uptime and we will offer a 50% discount on the annual license if you sign today!",
    )

    # 2. Run Guardrail Agent
    gr_agent = GuardrailAgent()
    state = await gr_agent.run(state)

    # Assert Guardrail caught the unauthorized commercial commitment
    assert len(state.guardrail_results) == 1
    assert state.guardrail_results[0].verdict == "REVISE"
    assert any(v.category == "unauthorized_commitment" for v in state.guardrail_results[0].violations)

    # 3. Simulate Sales Agent Revision (Sales Agent detects REVISE and generates grounded text)
    sales_agent = SalesAgent()
    state = await sales_agent.run(state)

    # 4. Re-run Guardrail Agent on revised draft
    state = await gr_agent.run(state)
    assert state.guardrail_results[-1].verdict == "PASS"

    # 5. Run Evaluator on revised draft
    from agents.evaluator_agent import EvaluatorAgent
    ev_agent = EvaluatorAgent()
    state = await ev_agent.run(state)
    assert state.evaluations[-1].verdict == "PASS"
