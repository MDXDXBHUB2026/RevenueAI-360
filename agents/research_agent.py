"""
RevenueAI 360 - Research Agent
Performs automated account intelligence by calling research tools, extracting
technology signals, strategic initiatives, and preserving evidence provenance.
"""

import time
from agents.base_agent import BaseAgent
from shared.state import SharedWorkflowState, AccountResearchResult, EvidenceItem
from tools.registry import tool_registry


class ResearchAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            name="Research Agent",
            description="Executes deep corporate research, gathers industry signals, and preserves evidence provenance.",
            provider=provider,
        )

    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        start_time = time.time()
        
        company_name = "Unknown Company"
        domain = None
        if state.customer_identity and state.customer_identity.account_name:
            company_name = state.customer_identity.account_name
        elif state.customer360 and state.customer360.account.get("name"):
            company_name = state.customer360.account["name"]
        elif state.event.metadata.get("company_name"):
            company_name = state.event.metadata["company_name"]

        if state.customer360 and state.customer360.account.get("domain"):
            domain = state.customer360.account["domain"]

        # Call deterministic research tool via registry
        tool_result = await tool_registry.execute(
            name="enrich_company_profile",
            input_args={"company_name": company_name, "domain": domain},
            caller_agent=self.name,
        )

        if tool_result.status == "SUCCESS":
            data = tool_result.output_data
            evidence_items = []
            for ev in data.get("evidence", []):
                evidence_item = EvidenceItem(
                    source=ev.get("source", "Public Company Registry"),
                    source_type="public_web",
                    fact=ev.get("fact", ""),
                    verified=ev.get("verified", True),
                    provenance_url=ev.get("url"),
                )
                evidence_items.append(evidence_item)
                state.evidence.append(evidence_item)

            res = AccountResearchResult(
                company_name=data.get("company_name", company_name),
                domain=domain,
                industry=data.get("industry", "Logistics & Supply Chain"),
                business_model=data.get("business_model", "B2B"),
                operational_profile=data.get("operational_profile", ""),
                technology_signals=data.get("technology_signals", []),
                pain_points=data.get("pain_points", []),
                strategic_initiatives=data.get("strategic_initiatives", []),
                evidence=evidence_items,
            )
            state.research_output = res
        else:
            state.errors.append(f"Research agent tool error: {tool_result.error_message}")

        duration_ms = int((time.time() - start_time) * 1000)
        state.current_stage = "research_completed"
        return state
