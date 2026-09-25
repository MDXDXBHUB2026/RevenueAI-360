"""
RevenueAI 360 - Customer Journey Manager & LangGraph Orchestration
Master multi-agent orchestrator utilizing LangGraph conditional routing,
inspecting Customer 360 state, creating dynamic execution plans, controlling iteration limits,
and persisting execution traces to PostgreSQL / SQLite.
"""

from typing import Dict, Any, List, Optional
import time
import uuid
from datetime import datetime, timezone
from langgraph.graph import StateGraph, END
from shared.state import SharedWorkflowState
from agents.identity_agent import IdentityAgent
from agents.research_agent import ResearchAgent
from agents.qualification_agent import QualificationAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.sales_agent import SalesAgent
from agents.customer_service_agent import CustomerServiceAgent
from agents.complaint_agent import ComplaintResolutionAgent
from agents.escalation_agent import EscalationAgent
from agents.guardrail_agent import GuardrailAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.communication_agent import CommunicationAgent
from domain.database import SessionLocal
from domain.models import WorkflowRun, AgentRun, PendingAction, AuditEvent


class CustomerJourneyManager:
    def __init__(self):
        # Instantiate specialized agents
        self.identity_agent = IdentityAgent()
        self.research_agent = ResearchAgent()
        self.qualification_agent = QualificationAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.sales_agent = SalesAgent()
        self.service_agent = CustomerServiceAgent()
        self.complaint_agent = ComplaintResolutionAgent()
        self.escalation_agent = EscalationAgent()
        self.guardrail_agent = GuardrailAgent()
        self.evaluator_agent = EvaluatorAgent()
        self.comm_agent = CommunicationAgent()
        
        # Build compiled LangGraph workflow
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(SharedWorkflowState)

        # Register Graph Nodes
        builder.add_node("identity_node", self._wrap_agent(self.identity_agent))
        builder.add_node("manager_plan", self._plan_node)
        builder.add_node("research_node", self._wrap_agent(self.research_agent))
        builder.add_node("qualification_node", self._wrap_agent(self.qualification_agent))
        builder.add_node("knowledge_node", self._wrap_agent(self.knowledge_agent))
        builder.add_node("sales_node", self._wrap_agent(self.sales_agent))
        builder.add_node("service_node", self._wrap_agent(self.service_agent))
        builder.add_node("complaint_node", self._wrap_agent(self.complaint_agent))
        builder.add_node("escalation_node", self._wrap_agent(self.escalation_agent))
        builder.add_node("guardrail_node", self._wrap_agent(self.guardrail_agent))
        builder.add_node("evaluator_node", self._wrap_agent(self.evaluator_agent))
        builder.add_node("communication_node", self._wrap_agent(self.comm_agent))

        # Entry point
        builder.set_entry_point("identity_node")
        builder.add_edge("identity_node", "manager_plan")

        # Conditional branching from Manager Planner
        def route_after_plan(state: SharedWorkflowState) -> str:
            # Rule: If an account has an active critical complaint, suppress sales and prioritise complaint!
            if state.customer360 and any(c.get("severity") in ["HIGH", "CRITICAL"] for c in state.customer360.complaints):
                if state.intent == "lead":
                    state.objective = "Prioritize existing complaint resolution before advancing commercial sales outreach."
                return "complaint_node"

            if state.intent == "complaint":
                return "complaint_node"
            elif state.intent == "support":
                return "knowledge_node"
            else:  # lead or sales
                return "research_node"

        builder.add_conditional_edges(
            "manager_plan",
            route_after_plan,
            {
                "complaint_node": "complaint_node",
                "knowledge_node": "knowledge_node",
                "research_node": "research_node",
            },
        )

        # Lead branch
        builder.add_edge("research_node", "qualification_node")
        builder.add_edge("qualification_node", "knowledge_node")

        # Branch from Knowledge
        def route_after_knowledge(state: SharedWorkflowState) -> str:
            if state.intent == "support":
                return "service_node"
            elif state.intent == "complaint":
                return "complaint_node"
            return "sales_node"

        builder.add_conditional_edges(
            "knowledge_node",
            route_after_knowledge,
            {
                "service_node": "service_node",
                "complaint_node": "complaint_node",
                "sales_node": "sales_node",
            },
        )

        # Branch from Complaint
        def route_after_complaint(state: SharedWorkflowState) -> str:
            if state.complaint_output and state.complaint_output.escalation_required:
                return "escalation_node"
            return "guardrail_node"

        builder.add_conditional_edges(
            "complaint_node",
            route_after_complaint,
            {
                "escalation_node": "escalation_node",
                "guardrail_node": "guardrail_node",
            },
        )

        builder.add_edge("escalation_node", "guardrail_node")
        builder.add_edge("sales_node", "guardrail_node")
        builder.add_edge("service_node", "guardrail_node")

        # Conditional Branching from Guardrail
        def route_after_guardrail(state: SharedWorkflowState) -> str:
            last_gr = state.guardrail_results[-1] if state.guardrail_results else None
            if not last_gr:
                return "evaluator_node"
            if last_gr.verdict == "BLOCK":
                state.status = "FAILED"
                return END
            if last_gr.verdict == "REVISE":
                if state.iteration_count < state.max_iterations:
                    state.iteration_count += 1
                    # Route back to responsible agent
                    if state.intent == "lead" or state.intent == "sales":
                        return "sales_node"
                    elif state.intent == "support":
                        return "service_node"
                    else:
                        return "complaint_node"
                else:
                    state.status = "FAILED"
                    return END
            return "evaluator_node"

        builder.add_conditional_edges(
            "guardrail_node",
            route_after_guardrail,
            {
                "sales_node": "sales_node",
                "service_node": "service_node",
                "complaint_node": "complaint_node",
                "evaluator_node": "evaluator_node",
                END: END,
            },
        )

        # Evaluator Branch
        def route_after_evaluator(state: SharedWorkflowState) -> str:
            last_ev = state.evaluations[-1] if state.evaluations else None
            if last_ev and last_ev.verdict == "PASS":
                return "communication_node"
            elif state.iteration_count < state.max_iterations:
                state.iteration_count += 1
                return "manager_plan"
            return "communication_node"

        builder.add_conditional_edges(
            "evaluator_node",
            route_after_evaluator,
            {
                "communication_node": "communication_node",
                "manager_plan": "manager_plan",
            },
        )

        builder.add_edge("communication_node", END)
        return builder.compile()

    def _wrap_agent(self, agent):
        """Wraps agent execution with performance tracking and database telemetry persistence."""
        async def node_func(state: SharedWorkflowState) -> Dict[str, Any]:
            start_t = time.time()
            # Execute agent
            updated_state = await agent.run(state)
            duration_ms = int((time.time() - start_t) * 1000)

            # Persist agent run into DB
            self._persist_agent_run(
                workflow_id=state.workflow_id,
                agent_name=agent.name,
                duration_ms=duration_ms,
                state=updated_state,
            )
            return updated_state.model_dump()
        return node_func

    async def _plan_node(self, state: SharedWorkflowState) -> Dict[str, Any]:
        """Manager inspects Customer360 state and formulates conditional execution plan."""
        plan = []
        if state.intent == "complaint":
            plan = ["Complaint Analysis", "Escalation Routing", "Guardrail Verification", "Evaluation", "Customer Acknowledgement Draft"]
        elif state.intent == "support":
            plan = ["Knowledge Retrieval", "Service Diagnosis", "Guardrail Verification", "Evaluation", "Response Formatting"]
        else:
            plan = ["Account Research", "Lead Qualification", "Enterprise Knowledge Retrieval", "Sales Strategy Formulation", "Guardrail Verification", "Evaluation", "Communication Formatting", "HITL Approval"]

        state.execution_plan = plan
        state.current_stage = "planned"
        return state.model_dump()

    def _persist_agent_run(self, workflow_id: str, agent_name: str, duration_ms: int, state: SharedWorkflowState):
        """Stores AgentRun row in DB for full observability."""
        db = SessionLocal()
        try:
            ar = AgentRun(
                workflow_id=workflow_id,
                agent_name=agent_name,
                status="COMPLETED",
                duration_ms=duration_ms,
                model_provider="openai" if state.intent == "lead" else "deterministic",
                model_name="gpt-4o-mini",
                execution_rationale=f"Executed task for stage: {state.current_stage}",
                input_payload={"event_id": state.event.event_id, "channel": state.event.channel},
                structured_output={"stage": state.current_stage, "status": state.status},
                evidence_items=[ev.model_dump() for ev in state.evidence[-2:]] if state.evidence else [],
                citations=[c.model_dump() for c in state.citations[-2:]] if state.citations else [],
            )
            db.add(ar)
            db.commit()
        except Exception as e:
            # Don't fail execution if DB logging has an issue
            pass
        finally:
            db.close()

    async def execute_workflow(self, state: SharedWorkflowState) -> SharedWorkflowState:
        """Executes the full compiled LangGraph workflow from end to end."""
        # Initial workflow run row in DB
        db = SessionLocal()
        try:
            w_run = WorkflowRun(
                id=state.workflow_id,
                trace_id=state.trace_id,
                account_id=state.customer_identity.account_id if state.customer_identity else None,
                trigger_channel=state.event.channel,
                intent=state.intent or "lead",
                status="RUNNING",
                current_stage="started",
            )
            db.add(w_run)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()

        # Run compiled LangGraph
        result_dict = await self.graph.ainvoke(state)
        final_state = SharedWorkflowState.model_validate(result_dict)

        # Update final state in DB
        db = SessionLocal()
        try:
            run_record = db.query(WorkflowRun).filter(WorkflowRun.id == final_state.workflow_id).first()
            if run_record:
                run_record.status = final_state.status
                run_record.current_stage = final_state.current_stage
                run_record.execution_plan = final_state.execution_plan
                run_record.state_snapshot = final_state.model_dump(mode="json")
                run_record.completed_at = datetime.now(timezone.utc)
                if final_state.customer_identity and final_state.customer_identity.account_id:
                    run_record.account_id = final_state.customer_identity.account_id

                # Save pending action if created
                for pa in final_state.pending_actions:
                    db_pa = PendingAction(
                        id=pa.id or str(uuid.uuid4()),
                        workflow_id=final_state.workflow_id,
                        action_type=pa.action_type,
                        requested_by_agent=pa.requested_by_agent,
                        risk_level=pa.risk_level,
                        approval_required=pa.approval_required,
                        payload=pa.payload,
                        status=pa.status,
                    )
                    db.add(db_pa)
                db.commit()
        except Exception as e:
            print(f"[Workflow DB Warning]: {e}")
        finally:
            db.close()

        return final_state


customer_journey_manager = CustomerJourneyManager()
