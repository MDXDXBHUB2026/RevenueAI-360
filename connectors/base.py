"""
RevenueAI 360 - Omnichannel Connector Abstraction
Defines common interface for inbound event normalization and outbound dispatch across
Email, WhatsApp, WebChat, Slack, and Social messaging.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field
from shared.state import NormalisedEvent, FormattedMessage


class DispatchResult(BaseModel):
    success: bool
    channel: str
    external_message_id: str
    recipient: str
    status: str  # DISPATCHED, QUEUED, SIMULATED, FAILED
    error: Optional[str] = None
    dispatched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChannelConnector(ABC):
    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Name of the channel, e.g., 'email', 'whatsapp', 'webchat'."""
        pass

    @abstractmethod
    async def receive_event(self, raw_payload: Dict[str, Any]) -> NormalisedEvent:
        """Normalises arbitrary inbound vendor payload into standard schema."""
        pass

    @abstractmethod
    async def send_message(self, message: FormattedMessage) -> DispatchResult:
        """Dispatches an approved outbound communication."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validates network connectivity and credentials."""
        pass
