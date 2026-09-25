"""
RevenueAI 360 - CRM Tools
Deterministic database access tools for Customer Accounts, Leads, Opportunities,
Support Cases, Complaints, and unified Interactions.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from domain.models import (
    CustomerAccount,
    Person,
    Lead,
    Opportunity,
    SupportCase,
    Complaint,
    Interaction,
    Message,
    Task,
)
from domain.database import SessionLocal
from tools.registry import tool_registry, ToolDefinition, RetryPolicy


# ==========================================
# 1. Get Customer Tool
# ==========================================

class GetCustomerInput(BaseModel):
    account_id: Optional[str] = None
    domain: Optional[str] = None
    account_name: Optional[str] = None


class GetCustomerOutput(BaseModel):
    found: bool
    account: Optional[Dict[str, Any]] = None
    message: str


def handle_get_customer(
    account_id: Optional[str] = None,
    domain: Optional[str] = None,
    account_name: Optional[str] = None,
    db_session: Optional[Session] = None,
) -> GetCustomerOutput:
    db = db_session or SessionLocal()
    try:
        q = db.query(CustomerAccount)
        if account_id:
            account = q.filter(CustomerAccount.id == account_id).first()
        elif domain:
            account = q.filter(CustomerAccount.domain.ilike(f"%{domain}%")).first()
        elif account_name:
            account = q.filter(CustomerAccount.name.ilike(f"%{account_name}%")).first()
        else:
            return GetCustomerOutput(found=False, message="No search criteria specified.")

        if not account:
            return GetCustomerOutput(found=False, message="Account not found.")

        return GetCustomerOutput(
            found=True,
            account={
                "id": account.id,
                "name": account.name,
                "domain": account.domain,
                "industry": account.industry,
                "tier": account.tier,
                "status": account.status,
                "sentiment_score": account.sentiment_score,
            },
            message="Account retrieved successfully.",
        )
    finally:
        if not db_session:
            db.close()


tool_registry.register(
    ToolDefinition(
        name="get_customer",
        description="Retrieve account details by ID, domain name, or company name.",
        input_schema=GetCustomerInput,
        output_schema=GetCustomerOutput,
        side_effect=False,
        approval_required=False,
        permission_level="read_only",
    ),
    handle_get_customer,
)


# ==========================================
# 2. Create Lead Tool
# ==========================================

class CreateLeadInput(BaseModel):
    account_id: str
    person_id: Optional[str] = None
    source: str = "inbound_enquiry"
    qualification_status: str = "NEW"
    intent_summary: str
    unknowns: List[str] = Field(default_factory=list)
    discovery_questions: List[str] = Field(default_factory=list)


class CreateLeadOutput(BaseModel):
    success: bool
    lead_id: str
    message: str


def handle_create_lead(
    account_id: str,
    person_id: Optional[str] = None,
    source: str = "inbound_enquiry",
    qualification_status: str = "NEW",
    intent_summary: str = "",
    unknowns: List[str] = [],
    discovery_questions: List[str] = [],
    db_session: Optional[Session] = None,
) -> CreateLeadOutput:
    db = db_session or SessionLocal()
    try:
        new_lead = Lead(
            account_id=account_id,
            person_id=person_id,
            source=source,
            qualification_status=qualification_status,
            intent_summary=intent_summary,
            unknowns=unknowns,
            discovery_questions=discovery_questions,
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        return CreateLeadOutput(success=True, lead_id=new_lead.id, message="Lead record created.")
    finally:
        if not db_session:
            db.close()


tool_registry.register(
    ToolDefinition(
        name="create_lead",
        description="Creates a qualified or discovery-required lead in the CRM.",
        input_schema=CreateLeadInput,
        output_schema=CreateLeadOutput,
        side_effect=True,
        approval_required=False,
        permission_level="standard",
    ),
    handle_create_lead,
)


# ==========================================
# 3. Create Opportunity Tool
# ==========================================

class CreateOpportunityInput(BaseModel):
    account_id: str
    title: str
    stage: str = "Discovery"
    estimated_value: float = 0.0
    ai_solution_concept: Dict[str, Any] = Field(default_factory=dict)


class CreateOpportunityOutput(BaseModel):
    success: bool
    opportunity_id: str
    message: str


def handle_create_opportunity(
    account_id: str,
    title: str,
    stage: str = "Discovery",
    estimated_value: float = 0.0,
    ai_solution_concept: Dict[str, Any] = {},
    db_session: Optional[Session] = None,
) -> CreateOpportunityOutput:
    db = db_session or SessionLocal()
    try:
        opp = Opportunity(
            account_id=account_id,
            title=title,
            stage=stage,
            estimated_value=estimated_value,
            ai_solution_concept=ai_solution_concept,
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)
        return CreateOpportunityOutput(success=True, opportunity_id=opp.id, message="Opportunity created.")
    finally:
        if not db_session:
            db.close()


tool_registry.register(
    ToolDefinition(
        name="create_opportunity",
        description="Creates a new commercial sales opportunity with solution architecture.",
        input_schema=CreateOpportunityInput,
        output_schema=CreateOpportunityOutput,
        side_effect=True,
        approval_required=False,  # Can be created autonomously after discovery
        permission_level="standard",
    ),
    handle_create_opportunity,
)


# ==========================================
# 4. Create Support Case Tool
# ==========================================

class CreateSupportCaseInput(BaseModel):
    account_id: str
    subject: str
    description: str
    priority: str = "MEDIUM"


class CreateSupportCaseOutput(BaseModel):
    success: bool
    case_id: str
    case_number: str
    message: str


def handle_create_support_case(
    account_id: str,
    subject: str,
    description: str,
    priority: str = "MEDIUM",
    db_session: Optional[Session] = None,
) -> CreateSupportCaseOutput:
    db = db_session or SessionLocal()
    try:
        import random
        case_num = f"CAS-{random.randint(10000, 99999)}"
        case = SupportCase(
            account_id=account_id,
            case_number=case_num,
            subject=subject,
            description=description,
            priority=priority,
            status="OPEN",
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return CreateSupportCaseOutput(success=True, case_id=case.id, case_number=case_num, message="Support case created.")
    finally:
        if not db_session:
            db.close()


tool_registry.register(
    ToolDefinition(
        name="create_support_case",
        description="Creates an inbound customer support case ticket.",
        input_schema=CreateSupportCaseInput,
        output_schema=CreateSupportCaseOutput,
        side_effect=True,
        approval_required=False,
        permission_level="standard",
    ),
    handle_create_support_case,
)


# ==========================================
# 5. Create Complaint Tool
# ==========================================

class CreateComplaintInput(BaseModel):
    account_id: str
    support_case_id: Optional[str] = None
    severity: str = "HIGH"
    complaint_text: str
    repeat_count: int = 1
    sla_breached: bool = False
    escalation_target: Optional[str] = None


class CreateComplaintOutput(BaseModel):
    success: bool
    complaint_id: str
    message: str


def handle_create_complaint(
    account_id: str,
    support_case_id: Optional[str] = None,
    severity: str = "HIGH",
    complaint_text: str = "",
    repeat_count: int = 1,
    sla_breached: bool = False,
    escalation_target: Optional[str] = None,
    db_session: Optional[Session] = None,
) -> CreateComplaintOutput:
    db = db_session or SessionLocal()
    try:
        complaint = Complaint(
            account_id=account_id,
            support_case_id=support_case_id,
            severity=severity,
            complaint_text=complaint_text,
            repeat_count=repeat_count,
            sla_breached=sla_breached,
            escalation_target=escalation_target,
            escalation_status="ESCALATED" if escalation_target else "PENDING",
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return CreateComplaintOutput(success=True, complaint_id=complaint.id, message="Complaint logged and registered.")
    finally:
        if not db_session:
            db.close()


tool_registry.register(
    ToolDefinition(
        name="create_complaint",
        description="Registers a customer complaint and escalation status.",
        input_schema=CreateComplaintInput,
        output_schema=CreateComplaintOutput,
        side_effect=True,
        approval_required=False,
        permission_level="standard",
    ),
    handle_create_complaint,
)
