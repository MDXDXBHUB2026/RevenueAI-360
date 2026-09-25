"""
RevenueAI 360 - Shared Workflow State & Pydantic Data Contracts
Implements the shared LangGraph state and typed contracts between cooperating agents.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class NormalisedEvent(BaseModel):
    event_id: str
    channel: Literal["email", "whatsapp", "webchat", "webform", "slack", "social"]
    external_identity: str  # e.g., "marcus.vance@nexalogistics.com"
    direction: Literal["inbound", "outbound", "internal"] = "inbound"
    timestamp: datetime = Field(default_factory=utc_now)
    subject: Optional[str] = None
    content: str
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResolvedIdentity(BaseModel):
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    account_status: Optional[str] = "prospect"  # prospect, customer, churned
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    person_role: Optional[str] = None
    is_known: bool = False
    confidence: float = 1.0
    channel_identity_id: Optional[str] = None


class EvidenceItem(BaseModel):
    source: str
    source_type: Literal["public_web", "crm_history", "knowledge_base", "channel_message"]
    fact: str
    verified: bool = True
    provenance_url: Optional[str] = None


class CitationItem(BaseModel):
    document_title: str
    chunk_id: Optional[str] = None
    excerpt: str
    relevance_score: float = 1.0


class AccountResearchResult(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: str
    business_model: str
    operational_profile: str
    technology_signals: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    strategic_initiatives: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class QualificationResult(BaseModel):
    status: Literal["QUALIFIED", "DISCOVERY_REQUIRED", "NURTURE", "NOT_ENOUGH_INFORMATION"]
    business_problem: str
    intent_level: Literal["HIGH", "MEDIUM", "LOW"]
    known_stakeholder: Optional[str] = None
    decision_authority_confirmed: bool = False
    timeline_confirmed: bool = False
    budget_confirmed: bool = False
    technical_fit: str
    unknowns: List[str] = Field(default_factory=list)
    discovery_questions: List[str] = Field(default_factory=list)
    recommended_next_action: str


class SalesStrategyResult(BaseModel):
    sales_objective: str
    tailored_value_proposition: str
    recommended_commercial_motion: str
    proposed_meeting_agenda: List[str] = Field(default_factory=list)
    draft_outreach_message: str
    supporting_citations: List[CitationItem] = Field(default_factory=list)


class ServiceResolutionResult(BaseModel):
    ticket_category: str
    issue_diagnosis: str
    recommended_solution: str
    citations: List[CitationItem] = Field(default_factory=list)
    requires_human_intervention: bool = False


class ComplaintResolutionResult(BaseModel):
    complaint_summary: str
    sentiment_severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    repeat_occurrence_detected: bool = False
    previous_ticket_references: List[str] = Field(default_factory=list)
    sla_breached: bool = False
    root_cause_analysis: str
    escalation_required: bool = False
    recommended_resolution_path: str


class EscalationResult(BaseModel):
    escalation_target: Literal["Engineering", "Management", "Customer Success", "Technical Support", "Sales"]
    priority: Literal["MEDIUM", "HIGH", "URGENT"]
    internal_briefing: str
    customer_acknowledgement: str
    assigned_lead: Optional[str] = None


class GuardrailViolation(BaseModel):
    rule_name: str
    category: Literal["pii", "prompt_injection", "unsubstantiated_claim", "unauthorized_commitment", "offensive_content"]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    description: str
    suggested_fix: Optional[str] = None


class GuardrailResult(BaseModel):
    verdict: Literal["PASS", "REVISE", "BLOCK"]
    agent_inspected: str
    violations: List[GuardrailViolation] = Field(default_factory=list)
    reasoning: str


class EvaluationMetric(BaseModel):
    metric_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: str


class EvaluationResult(BaseModel):
    verdict: Literal["PASS", "FAIL"]
    agent_evaluated: str
    metrics: List[EvaluationMetric] = Field(default_factory=list)
    feedback: Optional[str] = None


class NextBestActionResult(BaseModel):
    action_type: str
    recommended_timing: str
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    explainable_reason: str
    suppress_promotions: bool = False


class FormattedMessage(BaseModel):
    channel: Literal["email", "whatsapp", "webchat", "webform", "slack", "social"]
    recipient: str
    subject: Optional[str] = None
    body: str
    tone: str
    purpose: str
    facts_used: List[str] = Field(default_factory=list)
    approval_tier: Literal["tier1_auto", "tier2_approval", "tier3_human_only"]


class PendingActionItem(BaseModel):
    id: Optional[str] = None
    action_type: str
    requested_by_agent: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    approval_required: bool = True
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["PENDING", "APPROVED", "REJECTED", "EDITED"] = "PENDING"


class ToolResultRecord(BaseModel):
    tool_name: str
    agent_name: str
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    output_payload: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["SUCCESS", "FAILED", "BLOCKED"]
    duration_ms: int = 0


class Customer360Context(BaseModel):
    account: Dict[str, Any] = Field(default_factory=dict)
    contacts: List[Dict[str, Any]] = Field(default_factory=list)
    lifecycle_stage: str = "prospect"
    lead_summary: Optional[Dict[str, Any]] = None
    active_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    recent_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    channel_history: List[Dict[str, Any]] = Field(default_factory=list)
    open_support_cases: List[Dict[str, Any]] = Field(default_factory=list)
    complaints: List[Dict[str, Any]] = Field(default_factory=list)
    sentiment_trend: str = "neutral"
    knowledge_references: List[Dict[str, Any]] = Field(default_factory=list)
    pending_actions: List[Dict[str, Any]] = Field(default_factory=list)
    next_best_action: Optional[Dict[str, Any]] = None


# ==========================================
# Master LangGraph Shared Workflow State
# ==========================================

class SharedWorkflowState(BaseModel):
    workflow_id: str
    trace_id: str
    event: NormalisedEvent
    customer_identity: Optional[ResolvedIdentity] = None
    customer360: Optional[Customer360Context] = None
    intent: Optional[Literal["lead", "sales", "support", "complaint"]] = None
    objective: Optional[str] = None
    execution_plan: List[str] = Field(default_factory=list)
    current_stage: str = "init"
    
    # Specialist agent structured outputs
    research_output: Optional[AccountResearchResult] = None
    qualification_output: Optional[QualificationResult] = None
    sales_output: Optional[SalesStrategyResult] = None
    service_output: Optional[ServiceResolutionResult] = None
    complaint_output: Optional[ComplaintResolutionResult] = None
    escalation_output: Optional[EscalationResult] = None
    
    # Evidence & Citations
    evidence: List[EvidenceItem] = Field(default_factory=list)
    citations: List[CitationItem] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    
    # Tool Execution Results
    tool_results: List[ToolResultRecord] = Field(default_factory=list)
    
    # Quality & Governance
    guardrail_results: List[GuardrailResult] = Field(default_factory=list)
    evaluations: List[EvaluationResult] = Field(default_factory=list)
    pending_actions: List[PendingActionItem] = Field(default_factory=list)
    
    # Outbound response & state termination
    next_best_action: Optional[NextBestActionResult] = None
    final_response: Optional[FormattedMessage] = None
    status: Literal["RUNNING", "COMPLETED", "WAITING_APPROVAL", "FAILED"] = "RUNNING"
    errors: List[str] = Field(default_factory=list)
    iteration_count: int = 0
    max_iterations: int = 3
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
