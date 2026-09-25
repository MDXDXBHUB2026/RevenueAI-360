"""
RevenueAI 360 - Customer 360 Context Service
Aggregates unified omnichannel context across Accounts, Contacts, Leads,
Opportunities, Cross-Channel Interactions, Open Support Cases, Complaints,
and Pending Governance Actions into a single structured dossier.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from domain.models import (
    CustomerAccount,
    Person,
    Lead,
    Opportunity,
    Interaction,
    ChannelIdentity,
    SupportCase,
    Complaint,
    PendingAction,
)
from domain.database import SessionLocal
from shared.state import Customer360Context


class Customer360Service:
    def get_context(
        self,
        account_id: str,
        db_session: Optional[Session] = None,
    ) -> Optional[Customer360Context]:
        """Loads and structures complete 360-degree context for an account."""
        db = db_session or SessionLocal()
        try:
            account = db.query(CustomerAccount).filter(CustomerAccount.id == account_id).first()
            if not account:
                return None

            # 1. Contacts
            contacts = [
                {
                    "id": p.id,
                    "name": p.full_name,
                    "email": p.email,
                    "phone": p.phone,
                    "role": p.role,
                    "title": p.title,
                }
                for p in account.persons
            ]

            # 2. Leads
            latest_lead = (
                db.query(Lead)
                .filter(Lead.account_id == account_id)
                .order_by(Lead.created_at.desc())
                .first()
            )
            lead_summary = None
            if latest_lead:
                lead_summary = {
                    "id": latest_lead.id,
                    "qualification_status": latest_lead.qualification_status,
                    "source": latest_lead.source,
                    "intent": latest_lead.intent_summary,
                    "unknowns": latest_lead.unknowns or [],
                    "discovery_questions": latest_lead.discovery_questions or [],
                }

            # 3. Opportunities
            opps = [
                {
                    "id": o.id,
                    "title": o.title,
                    "stage": o.stage,
                    "estimated_value": o.estimated_value,
                    "ai_solution_concept": o.ai_solution_concept or {},
                }
                for o in account.opportunities
            ]

            # 4. Interactions Timeline (Chronological cross-channel)
            interactions = (
                db.query(Interaction)
                .filter(Interaction.account_id == account_id)
                .order_by(Interaction.timestamp.desc())
                .limit(20)
                .all()
            )
            timeline = [
                {
                    "id": i.id,
                    "channel": i.channel,
                    "direction": i.direction,
                    "subject": i.subject,
                    "content": i.content,
                    "sentiment": i.sentiment,
                    "timestamp": i.timestamp.isoformat() if i.timestamp else None,
                }
                for i in interactions
            ]

            # 5. Channel Identities
            channel_hist = [
                {
                    "channel": ci.channel,
                    "external_id": ci.external_id,
                    "verified": ci.verified,
                }
                for ci in account.channel_identities
            ]

            # 6. Support Cases
            cases = [
                {
                    "id": sc.id,
                    "case_number": sc.case_number,
                    "subject": sc.subject,
                    "status": sc.status,
                    "priority": sc.priority,
                    "created_at": sc.created_at.isoformat() if sc.created_at else None,
                }
                for sc in account.support_cases
            ]

            # 7. Complaints
            complaint_records = [
                {
                    "id": c.id,
                    "severity": c.severity,
                    "complaint_text": c.complaint_text,
                    "repeat_count": c.repeat_count,
                    "sla_breached": c.sla_breached,
                    "escalation_status": c.escalation_status,
                    "escalation_target": c.escalation_target,
                }
                for c in account.complaints
            ]

            # 8. Pending Actions
            pending_actions = (
                db.query(PendingAction)
                .filter(PendingAction.status == "PENDING")
                .all()
            )
            # Filter pending actions belonging to this account's workflows
            filtered_pending = [
                {
                    "id": pa.id,
                    "action_type": pa.action_type,
                    "requested_by_agent": pa.requested_by_agent,
                    "risk_level": pa.risk_level,
                    "payload": pa.payload,
                }
                for pa in pending_actions
                if pa.workflow and pa.workflow.account_id == account_id
            ]

            # Sentiment trend calculation
            trend = "neutral"
            if any(c.get("severity") in ["HIGH", "CRITICAL"] for c in complaint_records):
                trend = "critical_negative"
            elif any(i.get("sentiment") == "negative" for i in timeline[:3]):
                trend = "negative"
            elif any(i.get("sentiment") == "positive" for i in timeline[:3]):
                trend = "positive"

            return Customer360Context(
                account={
                    "id": account.id,
                    "name": account.name,
                    "domain": account.domain,
                    "industry": account.industry,
                    "tier": account.tier,
                    "status": account.status,
                    "sentiment_score": account.sentiment_score,
                },
                contacts=contacts,
                lifecycle_stage=account.status,
                lead_summary=lead_summary,
                active_opportunities=opps,
                recent_interactions=timeline,
                channel_history=channel_hist,
                open_support_cases=[c for c in cases if c["status"] != "RESOLVED"],
                complaints=complaint_records,
                sentiment_trend=trend,
                pending_actions=filtered_pending,
            )
        finally:
            if not db_session:
                db.close()


customer360_service = Customer360Service()
