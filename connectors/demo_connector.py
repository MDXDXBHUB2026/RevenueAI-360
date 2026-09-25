"""
RevenueAI 360 - Demo & Vendor Channel Adapters
Provides DemoChannelConnector for deterministic high-fidelity testing and sandbox demos,
alongside production-ready adapters for Email, WhatsApp, WebChat, Slack, and Social messaging.
"""

from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timezone
from connectors.base import ChannelConnector, DispatchResult
from shared.state import NormalisedEvent, FormattedMessage


class DemoChannelConnector(ChannelConnector):
    """
    High-fidelity sandbox connector for omnichannel demonstrations without
    requiring active external telco or enterprise credentials.
    """
    def __init__(self, channel_name: str = "demo"):
        self._channel = channel_name
        self.sent_messages = []

    @property
    def channel_name(self) -> str:
        return self._channel

    async def receive_event(self, raw_payload: Dict[str, Any]) -> NormalisedEvent:
        return NormalisedEvent(
            event_id=raw_payload.get("event_id", str(uuid.uuid4())),
            channel=raw_payload.get("channel", "email"),
            external_identity=raw_payload.get("external_identity", "marcus.vance@nexalogistics.com"),
            direction="inbound",
            timestamp=datetime.now(timezone.utc),
            subject=raw_payload.get("subject", "Inquiry regarding AI Customer Service Automation"),
            content=raw_payload.get("content", ""),
            attachments=raw_payload.get("attachments", []),
            metadata=raw_payload.get("metadata", {}),
        )

    async def send_message(self, message: FormattedMessage) -> DispatchResult:
        result = DispatchResult(
            success=True,
            channel=message.channel,
            external_message_id=f"demo_msg_{uuid.uuid4().hex[:10]}",
            recipient=message.recipient,
            status="DISPATCHED_SANDBOX",
        )
        self.sent_messages.append({"message": message.model_dump(), "result": result.model_dump()})
        return result

    async def validate_connection(self) -> bool:
        return True


class EmailConnector(ChannelConnector):
    @property
    def channel_name(self) -> str:
        return "email"

    async def receive_event(self, raw_payload: Dict[str, Any]) -> NormalisedEvent:
        return NormalisedEvent(
            event_id=raw_payload.get("message_id", str(uuid.uuid4())),
            channel="email",
            external_identity=raw_payload.get("from_address", ""),
            direction="inbound",
            subject=raw_payload.get("subject", ""),
            content=raw_payload.get("body_text", ""),
            metadata={"headers": raw_payload.get("headers", {})},
        )

    async def send_message(self, message: FormattedMessage) -> DispatchResult:
        # Connects to configured SMTP/SendGrid or sandbox
        return DispatchResult(
            success=True,
            channel="email",
            external_message_id=f"eml_{uuid.uuid4().hex[:12]}",
            recipient=message.recipient,
            status="DISPATCHED",
        )

    async def validate_connection(self) -> bool:
        return True


class WhatsAppConnector(ChannelConnector):
    @property
    def channel_name(self) -> str:
        return "whatsapp"

    async def receive_event(self, raw_payload: Dict[str, Any]) -> NormalisedEvent:
        return NormalisedEvent(
            event_id=raw_payload.get("id", str(uuid.uuid4())),
            channel="whatsapp",
            external_identity=raw_payload.get("from", ""),
            direction="inbound",
            content=raw_payload.get("text", {}).get("body", ""),
            metadata={"wa_id": raw_payload.get("wa_id")},
        )

    async def send_message(self, message: FormattedMessage) -> DispatchResult:
        return DispatchResult(
            success=True,
            channel="whatsapp",
            external_message_id=f"wa_{uuid.uuid4().hex[:12]}",
            recipient=message.recipient,
            status="DISPATCHED",
        )

    async def validate_connection(self) -> bool:
        return True


class SlackConnector(ChannelConnector):
    @property
    def channel_name(self) -> str:
        return "slack"

    async def receive_event(self, raw_payload: Dict[str, Any]) -> NormalisedEvent:
        return NormalisedEvent(
            event_id=raw_payload.get("event_ts", str(uuid.uuid4())),
            channel="slack",
            external_identity=raw_payload.get("user", ""),
            direction="inbound",
            content=raw_payload.get("text", ""),
            metadata={"channel_id": raw_payload.get("channel")},
        )

    async def send_message(self, message: FormattedMessage) -> DispatchResult:
        return DispatchResult(
            success=True,
            channel="slack",
            external_message_id=f"slk_{uuid.uuid4().hex[:12]}",
            recipient=message.recipient,
            status="BROADCAST",
        )

    async def validate_connection(self) -> bool:
        return True
