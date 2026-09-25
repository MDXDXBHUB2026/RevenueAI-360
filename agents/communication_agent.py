"""
RevenueAI 360 - Communication Agent
Transforms validated business outputs into channel-native syntax (Email, WhatsApp,
WebChat, Slack, Social) while preserving exact semantic commitments and facts.
Determines required Human-In-The-Loop automation tier.
"""

import time
from agents.base_agent import BaseAgent
from shared.state import SharedWorkflowState, FormattedMessage, PendingActionItem


class CommunicationAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            name="Communication Agent",
            description="Formats approved agent content for channel delivery and enforces HITL Tier policies.",
            provider=provider,
        )

    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        start_time = time.time()
        
        target_channel = state.event.channel
        recipient = state.event.external_identity
        facts = [ev.fact for ev in state.evidence[:3]]
        
        # Determine draft body from agent outputs
        raw_body = ""
        subject = None
        purpose = "Customer Engagement"

        if state.sales_output and state.sales_output.draft_outreach_message:
            raw_body = state.sales_output.draft_outreach_message
            subject = f"RevenueAI & {state.customer_identity.account_name if state.customer_identity else 'Enterprise'}: AI Customer Service Discovery"
            purpose = "Sales Prospecting & Technical Discovery"
        elif state.complaint_output and state.complaint_output.recommended_resolution_path:
            raw_body = state.complaint_output.recommended_resolution_path
            subject = "URGENT: Re: Service Interruption Escalation & Resolution Plan"
            purpose = "Complaint Resolution & SLA Acknowledgement"
        elif state.service_output and state.service_output.recommended_solution:
            raw_body = state.service_output.recommended_solution
            subject = "Support Case Resolution Guidance"
            purpose = "Technical Service Guidance"

        # Apply channel-native styling without altering facts
        if target_channel == "whatsapp":
            # Concise, markdown bolding, conversational
            body = (
                f"*RevenueAI Solutions*\n\n"
                f"Hello {state.customer_identity.person_name if state.customer_identity else 'there'},\n\n"
                f"{raw_body.strip()}\n\n"
                f"_Reply directly to this message or tap our link to confirm._"
            )
            tone = "Concise & Professional Mobile"
        elif target_channel == "slack":
            body = f":bell: *Internal Escalation Alert*\n>{raw_body}"
            tone = "Internal Urgent Actionable"
        else:  # email
            body = raw_body
            tone = "Executive B2B Professional"

        # Automation Tier Policy Check (Section 13)
        # Tier 1 - Auto: internal summaries, notifications
        # Tier 2 - Approval Required: prospect outreach, customer follow-up, complaint acknowledgement
        # Tier 3 - Human Only: binding contract execution, pricing exceptions, financial compensation
        tier = "tier2_approval"
        tier3_triggers = [
            "binding contract",
            "execute contract",
            "sign contract",
            "contractual agreement",
            "financial refund",
            "issue refund",
            "credit note",
            "pricing exception",
            "financial compensation",
            "legal liability",
        ]
        if any(trigger in body.lower() for trigger in tier3_triggers):
            tier = "tier3_human_only"

        formatted = FormattedMessage(
            channel=target_channel,
            recipient=recipient,
            subject=subject,
            body=body,
            tone=tone,
            purpose=purpose,
            facts_used=facts,
            approval_tier=tier,
        )

        state.final_response = formatted

        # If Tier 2 or Tier 3, create a PendingActionItem for Human Approval
        if tier in ["tier2_approval", "tier3_human_only"]:
            action_item = PendingActionItem(
                action_type=f"send_{target_channel}",
                requested_by_agent="Communication Agent",
                risk_level="MEDIUM" if tier == "tier2_approval" else "HIGH",
                approval_required=True,
                payload={
                    "recipient": recipient,
                    "subject": subject,
                    "body": body,
                    "channel": target_channel,
                },
                status="PENDING",
            )
            state.pending_actions.append(action_item)
            state.status = "WAITING_APPROVAL"
        else:
            state.status = "COMPLETED"

        duration_ms = int((time.time() - start_time) * 1000)
        state.current_stage = "communication_formatted"
        return state
