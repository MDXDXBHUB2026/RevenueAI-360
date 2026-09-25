"""
RevenueAI 360 - Escalation Agent
Determines target department (Engineering, Customer Success, Management),
prepares internal incident briefings, and executes escalation via registered internal tools.
"""

import time
from agents.base_agent import BaseAgent
from shared.state import SharedWorkflowState, EscalationResult
from tools.registry import tool_registry


class EscalationAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            name="Escalation Agent",
            description="Evaluates operational severity, routes incidents to responsible departments, and dispatches internal briefings.",
            provider=provider,
        )

    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        start_time = time.time()
        
        target = "Engineering"
        priority = "URGENT"
        account_name = state.customer_identity.account_name if state.customer_identity else "Client Account"
        
        briefing = (
            f"URGENT ESCALATION for {account_name}:\n"
            f"Customer has submitted a repeat complaint regarding tracking update failures. "
            f"SLA status: BREACHED. Severity: CRITICAL.\n"
            f"Assigned Action: Engineering on-call to inspect TMS carrier webhook ingestion pipeline immediately."
        )

        customer_ack = (
            f"Your issue has been formally escalated to our Engineering and Support Operations Leadership. "
            f"An incident commander has been assigned."
        )

        # Execute internal notification tool (Tier 1 auto)
        await tool_registry.execute(
            name="post_internal_notification",
            input_args={
                "target_channel": "#engineering-escalations",
                "title": f"Incident Escalation: {account_name}",
                "message": briefing,
                "priority": priority,
            },
            caller_agent=self.name,
        )

        result = EscalationResult(
            escalation_target=target,
            priority=priority,
            internal_briefing=briefing,
            customer_acknowledgement=customer_ack,
            assigned_lead="DevOps / Support Incident Commander",
        )

        state.escalation_output = result
        duration_ms = int((time.time() - start_time) * 1000)
        state.current_stage = "escalated"
        return state
