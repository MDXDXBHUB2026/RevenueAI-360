"""
RevenueAI 360 - Enterprise Domain Models
Defines all persistent relational entities for CRM, Omnichannel Interactions,
Multi-Agent Execution Traces, RAG Knowledge Base, and Human-in-the-Loop Governance.
Compatible with PostgreSQL (pgvector) and SQLite (for unit/offline test suites).
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    Float,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ==========================================
# 1. CRM Core Entities
# ==========================================

class CustomerAccount(Base):
    __tablename__ = "customer_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    tier = Column(String(50), default="Standard")  # Enterprise, Mid-Market, Standard
    status = Column(String(50), default="prospect")  # prospect, customer, churned
    sentiment_score = Column(Float, default=0.0)  # -1.0 to 1.0
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    persons = relationship("Person", back_populates="account", cascade="all, delete-orphan")
    channel_identities = relationship("ChannelIdentity", back_populates="account", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="account", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="account", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="account", cascade="all, delete-orphan")
    support_cases = relationship("SupportCase", back_populates="account", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="account", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="account", cascade="all, delete-orphan")


class Person(Base):
    __tablename__ = "persons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    role = Column(String(100), nullable=True)  # e.g., Decision Maker, Technical Lead, Champion
    title = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    account = relationship("CustomerAccount", back_populates="persons")
    channel_identities = relationship("ChannelIdentity", back_populates="person")
    leads = relationship("Lead", back_populates="person")


class ChannelIdentity(Base):
    """
    Maps inbound channel identifiers (email address, WhatsApp phone number,
    Slack user ID, LinkedIn profile) to a specific Person and CustomerAccount.
    """
    __tablename__ = "channel_identities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey("persons.id"), nullable=True, index=True)
    channel = Column(String(50), nullable=False, index=True)  # email, whatsapp, webchat, slack, social
    external_id = Column(String(255), nullable=False, index=True)  # e.g. user@domain.com, +123456789
    verified = Column(Boolean, default=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    account = relationship("CustomerAccount", back_populates="channel_identities")
    person = relationship("Person", back_populates="channel_identities")

    __table_args__ = (
        Index("idx_channel_external", "channel", "external_id", unique=True),
    )


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey("persons.id"), nullable=True, index=True)
    source = Column(String(100), default="inbound_enquiry")
    qualification_status = Column(String(50), default="NEW")  # NEW, QUALIFIED, DISCOVERY_REQUIRED, NURTURE
    intent_summary = Column(Text, nullable=True)
    unknowns = Column(JSON, default=list)  # Missing discovery gaps
    discovery_questions = Column(JSON, default=list)  # Recommended questions
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    account = relationship("CustomerAccount", back_populates="leads")
    person = relationship("Person", back_populates="leads")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    stage = Column(String(50), default="Discovery")  # Discovery, Solutioning, Proposal, Closed Won, Closed Lost
    estimated_value = Column(Float, default=0.0)
    ai_solution_concept = Column(JSON, default=dict)  # Stores generated AI Solution Demo Architecture
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    account = relationship("CustomerAccount", back_populates="opportunities")


class Interaction(Base):
    """
    Unified omnichannel timeline record.
    Aggregates emails, chats, WhatsApp notes, complaint logs into one timeline.
    """
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey("persons.id"), nullable=True, index=True)
    channel = Column(String(50), nullable=False)  # email, whatsapp, webchat, slack, social, system
    direction = Column(String(20), default="inbound")  # inbound, outbound, internal
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    sentiment = Column(String(50), default="neutral")  # positive, neutral, negative, urgent
    timestamp = Column(DateTime, default=utc_now, index=True)
    metadata_json = Column(JSON, default=dict)

    account = relationship("CustomerAccount", back_populates="interactions")
    messages = relationship("Message", back_populates="interaction", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    channel = Column(String(50), nullable=False)
    external_thread_id = Column(String(255), nullable=True, index=True)
    status = Column(String(50), default="active")  # active, closed
    created_at = Column(DateTime, default=utc_now)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=True, index=True)
    interaction_id = Column(String(36), ForeignKey("interactions.id"), nullable=True, index=True)
    sender_type = Column(String(50), nullable=False)  # customer, agent, sales_rep, system
    sender_name = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=utc_now)
    channel_payload = Column(JSON, default=dict)

    conversation = relationship("Conversation", back_populates="messages")
    interaction = relationship("Interaction", back_populates="messages")


class SupportCase(Base):
    __tablename__ = "support_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    case_number = Column(String(50), unique=True, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    resolution_notes = Column(Text, nullable=True)
    sla_due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    account = relationship("CustomerAccount", back_populates="support_cases")
    complaints = relationship("Complaint", back_populates="support_case")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    support_case_id = Column(String(36), ForeignKey("support_cases.id"), nullable=True, index=True)
    severity = Column(String(50), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    complaint_text = Column(Text, nullable=False)
    root_cause = Column(String(255), nullable=True)
    repeat_count = Column(Integer, default=1)
    sla_breached = Column(Boolean, default=False)
    escalation_status = Column(String(50), default="PENDING")  # NONE, PENDING, ESCALATED, RESOLVED
    escalation_target = Column(String(100), nullable=True)  # Engineering, Management, Customer Success
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    account = relationship("CustomerAccount", back_populates="complaints")
    support_case = relationship("SupportCase", back_populates="complaints")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=False, index=True)
    assigned_to = Column(String(100), default="Sales Rep")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED
    created_at = Column(DateTime, default=utc_now)

    account = relationship("CustomerAccount", back_populates="tasks")


# ==========================================
# 2. Knowledge & Vector RAG Entities
# ==========================================

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    doc_type = Column(String(50), default="policy")  # policy, product_catalogue, case_study, architecture
    file_path = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    chunk_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    # Stored as JSON array or vector; for pgvector native support we handle dynamically in DB setup
    embedding_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    document = relationship("KnowledgeDocument", back_populates="chunks")


# ==========================================
# 3. Multi-Agent Execution & Observability
# ==========================================

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trace_id = Column(String(100), nullable=False, index=True)
    account_id = Column(String(36), ForeignKey("customer_accounts.id"), nullable=True, index=True)
    trigger_channel = Column(String(50), nullable=False)
    intent = Column(String(50), nullable=True)  # lead, sales, support, complaint
    status = Column(String(50), default="RUNNING")  # RUNNING, COMPLETED, WAITING_APPROVAL, FAILED
    current_stage = Column(String(100), default="init")
    execution_plan = Column(JSON, default=list)
    state_snapshot = Column(JSON, default=dict)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, index=True)
    completed_at = Column(DateTime, nullable=True)

    agent_runs = relationship("AgentRun", back_populates="workflow", cascade="all, delete-orphan")
    pending_actions = relationship("PendingAction", back_populates="workflow", cascade="all, delete-orphan")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="COMPLETED")  # COMPLETED, REVISING, FAILED, SKIPPED
    model_provider = Column(String(50), default="mock")
    model_name = Column(String(100), default="mock-agent")
    execution_rationale = Column(Text, nullable=True)
    input_payload = Column(JSON, default=dict)
    structured_output = Column(JSON, default=dict)
    evidence_items = Column(JSON, default=list)
    citations = Column(JSON, default=list)
    retry_count = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    workflow = relationship("WorkflowRun", back_populates="agent_runs")
    tool_calls = relationship("ToolCall", back_populates="agent_run", cascade="all, delete-orphan")


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_run_id = Column(String(36), ForeignKey("agent_runs.id"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False, index=True)
    input_payload = Column(JSON, default=dict)
    output_payload = Column(JSON, default=dict)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED, TIMEOUT
    execution_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    agent_run = relationship("AgentRun", back_populates="tool_calls")


# ==========================================
# 4. Human-In-The-Loop & Governance Entities
# ==========================================

class PendingAction(Base):
    __tablename__ = "pending_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False)  # send_email, create_opportunity, escalate_ticket
    requested_by_agent = Column(String(100), nullable=False)
    risk_level = Column(String(50), default="MEDIUM")  # LOW (Tier 1), MEDIUM (Tier 2), HIGH (Tier 3)
    approval_required = Column(Boolean, default=True)
    payload = Column(JSON, default=dict)
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED, EDITED
    reviewer = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    execution_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    workflow = relationship("WorkflowRun", back_populates="pending_actions")
    approvals = relationship("Approval", back_populates="pending_action", cascade="all, delete-orphan")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    pending_action_id = Column(String(36), ForeignKey("pending_actions.id"), nullable=False, index=True)
    decision = Column(String(50), nullable=False)  # APPROVED, REJECTED, EDITED
    reviewer = Column(String(100), nullable=False)
    review_comments = Column(Text, nullable=True)
    edited_payload = Column(JSON, nullable=True)
    decided_at = Column(DateTime, default=utc_now)

    pending_action = relationship("PendingAction", back_populates="approvals")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, APPROVE, REJECT, DISPATCH
    actor = Column(String(100), nullable=False)  # AI_AGENT, HUMAN_USER, SYSTEM
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=utc_now, index=True)
