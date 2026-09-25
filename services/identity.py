"""
RevenueAI 360 - Customer Identity Resolution Service
Safely determines whether an inbound event belongs to an existing Person,
Account, or a new prospect without unsafe probabilistic guessing.
Persists explicit channel identity mappings across Email, WhatsApp, WebChat, and Slack.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from domain.models import CustomerAccount, Person, ChannelIdentity, Lead
from domain.database import SessionLocal
from shared.state import NormalisedEvent, ResolvedIdentity


class IdentityResolutionService:
    def resolve_event(
        self,
        event: NormalisedEvent,
        db_session: Optional[Session] = None,
    ) -> ResolvedIdentity:
        """
        Resolves identity from channel and external_identity.
        1. Checks exact match on `channel_identities` (e.g., email or phone).
        2. If not found, checks `persons` email or phone.
        3. If not found, checks if domain matches an existing `customer_accounts`.
        4. If not found, provisions new prospect account, person, and channel identity mapping.
        """
        db = db_session or SessionLocal()
        try:
            # 1. Look up existing channel mapping
            mapping = (
                db.query(ChannelIdentity)
                .filter(
                    ChannelIdentity.channel == event.channel,
                    ChannelIdentity.external_id == event.external_identity,
                )
                .first()
            )

            if mapping:
                account = mapping.account
                person = mapping.person
                return ResolvedIdentity(
                    account_id=account.id if account else None,
                    account_name=account.name if account else "Unknown Account",
                    account_status=account.status if account else "prospect",
                    person_id=person.id if person else None,
                    person_name=person.full_name if person else None,
                    person_role=person.role if person else None,
                    is_known=True,
                    confidence=1.0,
                    channel_identity_id=mapping.id,
                )

            # 2. Check if external_identity is an email and matches Person record
            person = None
            if "@" in event.external_identity:
                person = db.query(Person).filter(Person.email == event.external_identity).first()

            if person:
                account = person.account
                # Auto-link this new channel identity for future recognition
                new_mapping = ChannelIdentity(
                    account_id=account.id,
                    person_id=person.id,
                    channel=event.channel,
                    external_id=event.external_identity,
                    verified=True,
                )
                db.add(new_mapping)
                db.commit()
                db.refresh(new_mapping)

                return ResolvedIdentity(
                    account_id=account.id,
                    account_name=account.name,
                    account_status=account.status,
                    person_id=person.id,
                    person_name=person.full_name,
                    person_role=person.role,
                    is_known=True,
                    confidence=1.0,
                    channel_identity_id=new_mapping.id,
                )

            # 3. Check domain match (e.g. user@nexalogistics.com)
            domain = None
            if "@" in event.external_identity:
                domain = event.external_identity.split("@")[-1].lower()

            account = None
            if domain and domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
                account = db.query(CustomerAccount).filter(CustomerAccount.domain == domain).first()

            # If account does not exist, provision new prospect account
            if not account:
                acc_name = event.metadata.get("company_name")
                if not acc_name:
                    if domain:
                        acc_name = domain.split(".")[0].capitalize() + " Corp"
                    else:
                        acc_name = "New Inbound Prospect"

                account = CustomerAccount(
                    name=acc_name,
                    domain=domain,
                    industry=event.metadata.get("industry", "Logistics & Supply Chain"),
                    tier="Enterprise" if "enterprise" in event.content.lower() else "Standard",
                    status="prospect",
                )
                db.add(account)
                db.commit()
                db.refresh(account)

            # Create new Person if not present
            p_name = event.metadata.get("contact_name")
            if not p_name:
                p_name = event.external_identity.split("@")[0].replace(".", " ").title() if "@" in event.external_identity else "Unknown Contact"

            person = Person(
                account_id=account.id,
                full_name=p_name,
                email=event.external_identity if "@" in event.external_identity else None,
                phone=event.external_identity if ("+" in event.external_identity or event.external_identity.isdigit()) else None,
                role=event.metadata.get("role", "Prospect Stakeholder"),
                title=event.metadata.get("title", "Operations Lead"),
            )
            db.add(person)
            db.commit()
            db.refresh(person)

            # Persist explicit channel mapping
            mapping = ChannelIdentity(
                account_id=account.id,
                person_id=person.id,
                channel=event.channel,
                external_id=event.external_identity,
                verified=True,
            )
            db.add(mapping)
            db.commit()
            db.refresh(mapping)

            return ResolvedIdentity(
                account_id=account.id,
                account_name=account.name,
                account_status=account.status,
                person_id=person.id,
                person_name=person.full_name,
                person_role=person.role,
                is_known=False,  # newly created prospect
                confidence=1.0,
                channel_identity_id=mapping.id,
            )
        finally:
            if not db_session:
                db.close()


identity_service = IdentityResolutionService()
