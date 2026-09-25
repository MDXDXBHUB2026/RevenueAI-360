"""
RevenueAI 360 - Identity & Context Agent
Reviews inbound normalised events, resolves identity across multiple channels,
hydrates full Customer 360 context, and classifies intent.
"""

import time
from typing import Optional
from agents.base_agent import BaseAgent
from shared.state import SharedWorkflowState
from services.identity import identity_service
from services.customer360 import customer360_service


class IdentityAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            name="Identity & Context Agent",
            description="Resolves cross-channel identities, loads Customer 360 context, and identifies customer intent.",
            provider=provider,
        )

    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        start_time = time.time()
        
        # 1. Resolve identity via deterministic identity resolution
        resolved = identity_service.resolve_event(state.event)
        state.customer_identity = resolved

        # 2. Hydrate Customer 360 context
        if resolved.account_id:
            c360 = customer360_service.get_context(resolved.account_id)
            state.customer360 = c360

        # 3. Classify intent
        text_lower = f"{state.event.subject or ''} {state.event.content or ''}".lower()
        if any(w in text_lower for w in ["complain", "multiple times", "repeated", "frustrated", "unresolved issue", "escalat"]):
            state.intent = "complaint"
            state.objective = "De-escalate customer grievance, perform SLA analysis, and alert engineering/management."
        elif any(w in text_lower for w in ["pricing", "demo", "proposal", "contract", "buy", "sales", "automate", "automation", "inquiry", "solution", "copilot", "looking for"]):
            state.intent = "lead"
            state.objective = "Enrich prospect profile, qualify commercial fit, and prepare personalized discovery strategy."
        elif any(w in text_lower for w in ["broken", "error", "down", "not working", "bug", "support", "help with", "transit issue", "eta", "tracking", "container", "where is", "delivery status"]):
            state.intent = "support"
            state.objective = "Diagnose operational issue, ground against knowledge base, and provide resolution."
        else:
            state.intent = "lead"
            state.objective = "Analyze inbound query, enrich context, and coordinate discovery."

        duration_ms = int((time.time() - start_time) * 1000)
        state.current_stage = "identity_resolved"
        return state
