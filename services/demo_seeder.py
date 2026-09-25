"""
RevenueAI 360 - Demonstration Data Seeder
Seeds fictional enterprise data for 'Nexa Logistics' and realistic cross-channel history.
Explicitly labels all entities and people as FICTIONAL.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from domain.models import (
    CustomerAccount,
    Person,
    ChannelIdentity,
    Lead,
    Opportunity,
    Interaction,
    Message,
    SupportCase,
    Complaint,
    Task,
)
from domain.database import SessionLocal
from services.rag.knowledge_service import knowledge_service


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def seed_demo_data(db_session: Session = None):
    db = db_session or SessionLocal()
    try:
        # 1. Seed RAG knowledge documents
        await knowledge_service.seed_demo_knowledge(db_session=db)

        # 2. Check if Nexa Logistics exists
        existing_acc = db.query(CustomerAccount).filter(CustomerAccount.domain == "nexalogistics.com").first()
        if existing_acc:
            return existing_acc

        now = utc_now()

        # Create Primary Demonstration Account
        account = CustomerAccount(
            id="acc-nexa-logistics-demo",
            name="Nexa Logistics (Fictional Demo)",
            domain="nexalogistics.com",
            industry="Freight & Supply Chain Logistics",
            tier="Enterprise",
            status="prospect",  # Moves to customer during demo
            sentiment_score=0.45,
            created_at=now - timedelta(days=14),
        )
        db.add(account)
        db.commit()
        db.refresh(account)

        # Primary Contact: Marcus Vance
        contact = Person(
            id="person-marcus-vance",
            account_id=account.id,
            full_name="Marcus Vance",
            email="marcus.vance@nexalogistics.com",
            phone="+1-555-019-2834",
            role="VP of Supply Chain Operations",
            title="Vice President, Supply Chain Operations",
            created_at=now - timedelta(days=14),
        )
        db.add(contact)

        # Secondary Contact: Elena Rostova (Lead Dispatcher)
        contact2 = Person(
            id="person-elena-rostova",
            account_id=account.id,
            full_name="Elena Rostova",
            email="elena.rostova@nexalogistics.com",
            phone="+1-555-019-8821",
            role="Director of Freight Operations",
            title="Director of Operations",
            created_at=now - timedelta(days=10),
        )
        db.add(contact2)
        db.commit()

        # Multi-Channel Identity Mappings
        # Email identity
        db.add(ChannelIdentity(
            account_id=account.id,
            person_id=contact.id,
            channel="email",
            external_id="marcus.vance@nexalogistics.com",
            verified=True,
        ))
        # WhatsApp identity (same person, different channel)
        db.add(ChannelIdentity(
            account_id=account.id,
            person_id=contact.id,
            channel="whatsapp",
            external_id="+15550192834",
            verified=True,
        ))
        # WebChat identity
        db.add(ChannelIdentity(
            account_id=account.id,
            person_id=contact2.id,
            channel="webchat",
            external_id="elena.rostova@nexalogistics.com",
            verified=True,
        ))

        # Initial Lead Record
        lead = Lead(
            id="lead-nexa-001",
            account_id=account.id,
            person_id=contact.id,
            source="inbound_webform",
            qualification_status="DISCOVERY_REQUIRED",
            intent_summary="Inquiring about automated AI agents to handle 12,000 weekly freight status inquiries and exceptions.",
            unknowns=[
                "Executive budget sign-off authority and committee schedule.",
                "Target production rollout date for freight tracking workflows.",
            ],
            discovery_questions=[
                "Who will be the executive sponsor for the AI automation budget?",
                "What is Nexa's target timeline for rolling out the first automated communication channels?",
            ],
            created_at=now - timedelta(days=7),
        )
        db.add(lead)

        # Opportunity
        opp = Opportunity(
            id="opp-nexa-copilot",
            account_id=account.id,
            title="AI Customer Service Copilot Enterprise Pilot",
            stage="Solutioning",
            estimated_value=185000.0,
            ai_solution_concept={
                "architecture": "Multi-agent dispatch copilot with TMS webhook sync",
                "target_rollout": "Q2 2026",
            },
            created_at=now - timedelta(days=5),
        )
        db.add(opp)

        # Chronological Interaction History (Step-by-step portfolio timeline)
        interactions_data = [
            {
                "channel": "email",
                "direction": "inbound",
                "subject": "Inquiry regarding AI Customer Service Automation",
                "content": "Hi Team, We manage 12,000 freight shipments weekly at Nexa Logistics. Our dispatchers spend 40% of their day answering 'where is my truck' emails. We are exploring AI copilot automation. Can we discuss?",
                "sentiment": "neutral",
                "days_ago": 7,
            },
            {
                "channel": "email",
                "direction": "outbound",
                "subject": "Re: Inquiry regarding AI Customer Service Automation",
                "content": "Hi Marcus, Thank you for reaching out. We would love to schedule a technical discovery session to review our TMS-connected dispatch copilot architecture.",
                "sentiment": "positive",
                "days_ago": 6,
            },
            {
                "channel": "whatsapp",
                "direction": "inbound",
                "subject": "WhatsApp follow-up from Marcus Vance",
                "content": "Following up on my email earlier - also wanted to confirm if your copilot can send automated WhatsApp exception alerts to our retail consignees?",
                "sentiment": "positive",
                "days_ago": 4,
            },
            {
                "channel": "slack",
                "direction": "internal",
                "subject": "Discovery Prep Notes: Nexa Logistics",
                "content": "Account research complete. Verified legacy SAP ERP and 4 regional dispatch centers. Strong alignment with Copilot v2 roadmap.",
                "sentiment": "positive",
                "days_ago": 3,
            },
        ]

        for item in interactions_data:
            inter = Interaction(
                account_id=account.id,
                person_id=contact.id,
                channel=item["channel"],
                direction=item["direction"],
                subject=item["subject"],
                content=item["content"],
                sentiment=item["sentiment"],
                timestamp=now - timedelta(days=item["days_ago"]),
            )
            db.add(inter)

        # Pre-seed a prior support ticket to establish chronic issue history
        past_case = SupportCase(
            id="case-nexa-prior-01",
            account_id=account.id,
            case_number="CAS-48192",
            subject="Carrier GPS Telemetry Delay on Midwest Corridor",
            description="Consignees not receiving automated status updates between Chicago and Detroit dispatch hubs.",
            status="OPEN",
            priority="HIGH",
            created_at=now - timedelta(days=2),
        )
        db.add(past_case)

        # Pre-seed Tasks
        db.add(Task(
            account_id=account.id,
            assigned_to="Senior AI Solutions Engineer",
            title="Prepare Nexa Logistics AI Architecture Concept & Demo",
            due_date=now + timedelta(days=2),
            status="IN_PROGRESS",
        ))

        db.commit()
        return account
    finally:
        if not db_session:
            db.close()
