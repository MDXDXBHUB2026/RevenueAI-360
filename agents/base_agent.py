"""
RevenueAI 360 - Base Agent Class
Provides common foundation for all 12 specialized agents, ensuring execution tracking,
model provider selection, telemetry, error handling, and structured output formatting.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
from datetime import datetime, timezone
from shared.state import SharedWorkflowState
from services.llm.provider import get_llm_provider, BaseLLMProvider


from pydantic import BaseModel


class AgentExecutionRecord(BaseModel):
    pass


class BaseAgent(ABC):
    def __init__(self, name: str, description: str, provider: Optional[BaseLLMProvider] = None):
        self.name = name
        self.description = description
        self.provider = provider or get_llm_provider()

    @abstractmethod
    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        """Executes the agent's specialized task against the shared workflow state."""
        pass

    def log_execution(
        self,
        state: SharedWorkflowState,
        status: str,
        rationale: str,
        structured_output: Dict[str, Any],
        duration_ms: int,
        evidence: Optional[List[Any]] = None,
        citations: Optional[List[Any]] = None,
    ):
        """Records agent telemetry into state for observability and frontend Control Room."""
        # Telemetry will be persisted to DB by the workflow runner
        pass
