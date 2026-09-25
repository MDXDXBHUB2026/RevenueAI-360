"""
RevenueAI 360 - Knowledge / RAG Agent
Executes semantic vector queries against enterprise product catalogues,
SLA policies, and case studies, returning cited excerpts with safety sanitization.
"""

import time
from agents.base_agent import BaseAgent
from shared.state import SharedWorkflowState
from services.rag.knowledge_service import knowledge_service


class KnowledgeAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            name="Knowledge / RAG Agent",
            description="Performs semantic vector search across enterprise knowledge, attaching citations to supported claims.",
            provider=provider,
        )

    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        start_time = time.time()
        
        # Determine query from intent or research
        if state.intent == "lead":
            query = "AI Customer Service Copilot capabilities integration TMS automated shipment tracking"
        elif state.intent == "complaint":
            query = "complaint escalation repeat complaint SLA breach procedure"
        elif state.intent == "support":
            query = state.event.content
        else:
            query = state.event.content or "Enterprise capabilities"

        citations = await knowledge_service.search(query=query, top_k=3)
        state.citations.extend(citations)

        duration_ms = int((time.time() - start_time) * 1000)
        state.current_stage = "knowledge_retrieved"
        return state
