# RevenueAI 360: Agent Specification Catalog

The platform employs **12 specialized cooperating agents** orchestrated via LangGraph. Each agent possesses bounded authority, typed Pydantic V2 state contracts, and distinct responsibilities.

---

### 1. Customer Journey Manager (`agents/manager.py`)
- **Role**: Workflow Director and Dynamic Graph Orchestrator.
- **Responsibilities**:
  - Evaluates Customer 360 state and inbound event intent.
  - Dynamically synthesizes the execution plan.
  - Controls conditional routing, loop limits, and failure fallback branches.
  - Enforces priority policies (e.g., active complaints take precedence over promotional sales).
- **Execution Engine**: LangGraph `StateGraph` with conditional edge routing.

---

### 2. Identity & Context Agent (`agents/identity_agent.py`)
- **Role**: Customer Resolution and Lifecycle Context Anchor.
- **Responsibilities**:
  - Reviews normalized channel events (email, phone, channel handle).
  - Matches or creates records across `persons`, `customer_accounts`, and `channel_identities`.
  - Reconstructs active lifecycle stage and history.
  - Emits typed `IdentityOutput`.

---

### 3. Research Agent (`agents/research_agent.py`)
- **Role**: Automated Account Intelligence and Business Profiling.
- **Responsibilities**:
  - Gathers verified corporate profiles, shipment volumes, software stack, and strategic initiatives.
  - Emits factual findings with explicit provenance tracking (`provenance: "research_dossier"`).
  - Never fabricates facts in the absence of verified tool output.

---

### 4. Qualification Agent (`agents/qualification_agent.py`)
- **Role**: Objective B2B Lead Qualification.
- **Responsibilities**:
  - Assesses budget, authority, need, and timeline against documented enterprise rubrics.
  - Categorizes into explainable classifications: `QUALIFIED`, `DISCOVERY REQUIRED`, `NURTURE`, `UNQUALIFIED`.
  - Identifies critical discovery gaps and unknowns.
  - **No arbitrary pseudo-numeric scores**: Every status is grounded in explicit evidence.

---

### 5. Sales Agent (`agents/sales_agent.py`)
- **Role**: Commercial Engagement & Discovery Strategy.
- **Responsibilities**:
  - Formulates tailored discovery questionnaires targeting operational bottlenecks.
  - Recommends next commercial milestones (e.g., technical solution demo, architecture workshop).
  - Drafts personalized outbound engagement aligned with account intelligence.

---

### 6. Customer Service Agent (`agents/customer_service_agent.py`)
- **Role**: Technical Troubleshooting & Operational Support.
- **Responsibilities**:
  - Resolves tier-1 and tier-2 operational requests.
  - Retrieves grounded documentation from the Enterprise Knowledge Base.
  - Synthesizes clear, step-by-step resolution instructions with verified chunk citations.

---

### 7. Complaint Resolution Agent (`agents/complaint_agent.py`)
- **Role**: Grievance De-escalation & SLA Root Cause Analysis.
- **Responsibilities**:
  - Detects repeat grievance signals, SLA breaches, and sentiment degradation.
  - Correlates historical support tickets and past dispatch attempts.
  - Synthesizes empathetic de-escalation acknowledgments without making unauthorized financial commitments.

---

### 8. Escalation Agent (`agents/escalation_agent.py`)
- **Role**: Departmental Routing & Incident Escalation.
- **Responsibilities**:
  - Evaluates operational severity and maps required escalation target (Engineering, Customer Success, Logistics Operations, Executive Management).
  - Formulates internal notification payloads with comprehensive background context.
  - Creates high-priority internal action items.

---

### 9. Knowledge Agent (`agents/knowledge_agent.py`)
- **Role**: Enterprise Retrieval-Augmented Generation (RAG) Retrieval.
- **Responsibilities**:
  - Executes semantic cosine similarity search across indexed corporate knowledge chunks.
  - Enforces citation retention (`doc_id`, `chunk_id`, `title`).
  - Verifies that retrieved context is treated as untrusted data.

---

### 10. Communication Agent (`agents/communication_agent.py`)
- **Role**: Omnichannel Tone & Format Adaptation.
- **Responsibilities**:
  - Adapts business response intent into channel-appropriate styling (Email, WhatsApp, WebChat, Slack).
  - Preserves exact factual commitments and citations across all communication styles.
  - Generates message previews for Human-in-the-Loop review.

---

### 11. Guardrail Agent (`agents/guardrail_agent.py`)
- **Role**: Safety, Privacy, and Hallucination Gatekeeper.
- **Responsibilities**:
  - Scans for PII leakage (unmasked credentials, credit card numbers).
  - Detects prompt injection attempts in incoming channel content.
  - Verifies that commercial claims (pricing, SLAs, guarantees) are backed by citations.
  - Emits structured decisions: `PASS`, `REVISE`, or `BLOCK`.

---

### 12. Evaluator Agent (`agents/evaluator_agent.py`)
- **Role**: Objective Quality Assurance & Grounding Validation.
- **Responsibilities**:
  - Validates schema compliance and required-field completeness.
  - Checks citation coverage for technical or policy assertions.
  - Evaluates prompt relevance and grounding fidelity.
  - Authorizes or rejects workflow progression to the dispatch phase.
