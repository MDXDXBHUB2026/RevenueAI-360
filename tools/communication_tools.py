"""
RevenueAI 360 - Communication Tools
Outbound message dispatch tools for Email, WhatsApp, WebChat, and internal Slack notifications.
Enforces Tier 2 Human-in-the-loop approval policy for external customer-facing dispatches.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from tools.registry import tool_registry, ToolDefinition


class SendEmailInput(BaseModel):
    recipient_email: str
    subject: str
    body: str
    reply_to: Optional[str] = None


class SendEmailOutput(BaseModel):
    delivered: bool
    channel: str = "email"
    message_id: str
    recipient: str
    status: str


def handle_send_email(
    recipient_email: str,
    subject: str,
    body: str,
    reply_to: Optional[str] = None,
) -> SendEmailOutput:
    import uuid
    msg_id = f"eml_{uuid.uuid4().hex[:12]}"
    # In production/sandbox, connects to SMTP/SendGrid or Demo Gateway
    return SendEmailOutput(
        delivered=True,
        channel="email",
        message_id=msg_id,
        recipient=recipient_email,
        status="DISPATCHED",
    )


tool_registry.register(
    ToolDefinition(
        name="send_email",
        description="Sends customer-facing email communication. Requires Tier 2 HITL approval.",
        input_schema=SendEmailInput,
        output_schema=SendEmailOutput,
        side_effect=True,
        approval_required=True,  # Tier 2 approval required
        permission_level="elevated",
    ),
    handle_send_email,
)


class SendWhatsAppInput(BaseModel):
    phone_number: str
    message: str


class SendWhatsAppOutput(BaseModel):
    delivered: bool
    channel: str = "whatsapp"
    message_id: str
    recipient: str
    status: str


def handle_send_whatsapp(phone_number: str, message: str) -> SendWhatsAppOutput:
    import uuid
    msg_id = f"wa_{uuid.uuid4().hex[:12]}"
    return SendWhatsAppOutput(
        delivered=True,
        channel="whatsapp",
        message_id=msg_id,
        recipient=phone_number,
        status="DISPATCHED",
    )


tool_registry.register(
    ToolDefinition(
        name="send_whatsapp",
        description="Dispatches a message to the customer's verified WhatsApp handle. Requires Tier 2 approval.",
        input_schema=SendWhatsAppInput,
        output_schema=SendWhatsAppOutput,
        side_effect=True,
        approval_required=True,
        permission_level="elevated",
    ),
    handle_send_whatsapp,
)


class PostInternalNotificationInput(BaseModel):
    target_channel: str = "#customer-escalations"
    title: str
    message: str
    priority: str = "HIGH"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PostInternalNotificationOutput(BaseModel):
    delivered: bool
    channel: str = "internal_slack"
    broadcast_id: str
    status: str


def handle_post_internal_notification(
    target_channel: str,
    title: str,
    message: str,
    priority: str = "HIGH",
    metadata: Dict[str, Any] = {},
) -> PostInternalNotificationOutput:
    import uuid
    b_id = f"slk_{uuid.uuid4().hex[:12]}"
    return PostInternalNotificationOutput(
        delivered=True,
        channel="internal_slack",
        broadcast_id=b_id,
        status="NOTIFIED",
    )


tool_registry.register(
    ToolDefinition(
        name="post_internal_notification",
        description="Posts urgent escalation briefing to internal Slack or Teams channels.",
        input_schema=PostInternalNotificationInput,
        output_schema=PostInternalNotificationOutput,
        side_effect=True,
        approval_required=False,  # Internal alerting is Tier 1 (auto allowed)
        permission_level="standard",
    ),
    handle_post_internal_notification,
)
