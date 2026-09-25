# RevenueAI 360: Demonstration Video Scripts

This document outlines two high-impact demonstration scripts designed for technical hiring managers, enterprise clients, and architecture review boards.

---

# Script 1: 90-Second Portfolio & LinkedIn Walkthrough

**Target Audience**: VP of AI Engineering, CTO, Head of Solutions Architecture  
**Goal**: Rapidly prove genuine multi-agent orchestration, continuous customer context, and strict governance without superficial chatbot wrappers.

### [0:00 - 0:15] The Hook: The Core Problem
- **Visual**: Open `Executive Dashboard` (`http://localhost:3000`). Clean, dark enterprise UI showing active workflows, high-priority grievances, and pending approvals.
- **Narrative**:
  > *"Most AI CRM applications are either shallow chatbot wrappers or linear prompt chains that lose context across channels. Today, I'm showcasing **RevenueAI 360**, an AI-native customer lifecycle platform where cooperating specialized agents maintain one continuous context across Email, WhatsApp, and WebChat, governed by a strict rule: **Agents Decide, Tools Execute**."*

### [0:15 - 0:40] The First Inbound Lead & Real-Time Orchestration
- **Visual**: Switch to `Omnichannel Inbox` (`/inbox`). Show an inbound email from Marcus Vance (VP Logistics at Nexa Logistics). Click **Simulate Inbound**.
- **Visual**: Jump to `AI Control Room` (`/control-room`). Show the live LangGraph execution trace activating: `Identity & Context` -> `Customer Journey Manager` -> `Research` -> `Qualification` -> `Knowledge RAG` -> `Sales` -> `Guardrail` -> `Evaluator`.
- **Narrative**:
  > *"When an inquiry arrives, our Identity Agent maps the account, and the Customer Journey Manager dynamically synthesizes an execution plan. Notice our Research Agent pulling company signals while our Qualification Agent evaluates B2B criteria with zero arbitrary percentage scores. It identifies missing timeline details and tags the status as 'DISCOVERY REQUIRED'."*

### [0:40 - 1:05] Grounded Intelligence & Human-in-the-Loop Governance
- **Visual**: Navigate to `Approval Centre` (`/approvals`). Inspect the synthesized response. Show the citations from the Enterprise Knowledge Base and the clean Guardrail pass. Click **Approve & Execute**.
- **Narrative**:
  > *"Notice how the Sales Agent grounds its discovery questions in our enterprise capability catalog. We enforce a 3-tier governance policy: read actions are automated, but customer-facing communications require explicit Human-in-the-Loop approval before our deterministic tools can dispatch an email."*

### [1:05 - 1:25] Cross-Channel Grievance & Next-Best-Action Suppression
- **Visual**: Back to `/inbox`, switch channel to **WhatsApp**. Nexa Logistics reports a repeat shipment webhook drop.
- **Visual**: Show the workflow route through `Complaint Resolution Agent` and `Escalation Agent`. Jump to `Customer 360` (`/customers/acc-nexa-logistics-demo`). Show the unified omnichannel timeline and the **Next-Best-Action engine** recommending: *"Resolve active complaint first; suppress promotional outreach."*
- **Narrative**:
  > *"When the customer switches to WhatsApp to report a repeat outage, the system preserves unified identity. The complaint agent identifies a breached SLA, triggers an internal engineering escalation, and our Next-Best-Action engine immediately suppresses sales campaigns until the grievance is resolved."*

### [1:25 - 1:30] Outro & Codebase
- **Visual**: Show GitHub repo with passing Pytest suite and Docker Compose setup.
- **Narrative**:
  > *"Built with Next.js 15, FastAPI, LangGraph, and PostgreSQL pgvector. Fully open-source and ready to deploy."*

---

# Script 2: 5-Minute Technical Solutions Architecture Deep-Dive

**Target Audience**: Principal AI Engineers, Enterprise Architects, Technical Leadership  
**Goal**: Detailed, verifiable walk-through demonstrating system architecture, data models, state machines, guardrail loops, and custom AI demo generation.

### Segment 1: System Architecture & Data Model [0:00 - 0:45]
- **Walkthrough**:
  - Present the architecture diagram in `docs/architecture.md`.
  - Explain the separation of concerns:
    - **FastAPI backend** running LangGraph state machines and SQLAlchemy models.
    - **Pydantic V2 shared state**: Type-safe transitions between agents.
    - **PostgreSQL + pgvector**: Unified relational store for Customer 360 + vector embeddings for RAG.
    - **Tool Registry**: Audited layer with permission tiers (`Auto`, `Approval Required`, `Human Only`).

### Segment 2: Inbound Ingestion & Multi-Agent Routing [0:45 - 1:45]
- **Walkthrough**:
  - Open `/inbox`. Demonstrate sending an inbound lead payload.
  - Open `/control-room`.
  - Inspect the selected agent cards:
    - `IdentityAgent`: Shows matched account `acc-nexa-logistics-demo` and contact `per-marcus-vance`.
    - `ResearchAgent`: Shows extracted signals (12,000 shipments/week, SAP TMS).
    - `QualificationAgent`: Explains why `DISCOVERY_REQUIRED` was selected based on explicit evidence, not a random percentage.
    - `KnowledgeAgent`: Shows retrieved vector chunks from `ai-copilot-capabilities.md`.
    - `SalesAgent`: Formulates targeted discovery questions.

### Segment 3: Guardrail Intervention & Self-Correction Loop [1:45 - 2:45]
- **Walkthrough**:
  - Explain the self-correction mechanism in LangGraph.
  - Show test scenario 5: When an agent produces an unsubstantiated commercial guarantee, `GuardrailAgent` intercepts with a `REVISE` finding.
  - Show how the manager routes the payload back to the agent for revision, re-evaluates the output, and clears it only after verified citations are attached.

### Segment 4: Omnichannel Grievance & Next-Best-Action [2:45 - 3:45]
- **Walkthrough**:
  - Demonstrate an inbound WhatsApp message reporting a repeat operational failure.
  - Observe `ComplaintResolutionAgent` calculating historical ticket frequency and SLA status.
  - Show `EscalationAgent` generating a structured incident report for Engineering.
  - Open `/customers/acc-nexa-logistics-demo` to inspect the unified Customer 360 screen.
  - Point out the cross-channel timeline: Email -> WhatsApp -> Internal Escalation.
  - Explain the **Next-Best-Action** algorithm: Commercial expansion is blocked until customer satisfaction is verified.

### Segment 5: Customer AI Demo Builder [3:45 - 4:30]
- **Walkthrough**:
  - Navigate to `/demo-builder`.
  - Select Nexa Logistics. The operational bottleneck is pre-populated: *"12,000 weekly freight tracking inquiries and dispatcher fatigue."*
  - Click **Generate AI Solution Concept**.
  - Review the synthesized technical architecture proposal:
    - Proposed cooperating agents (Carrier API Copilot, Dispatch Exception Agent).
    - Required enterprise tools (TMS webhook polling, ERP inventory lookup).
    - Phased prototype-to-production roadmap (Phase 1: Read-only lookup -> Phase 2: Autonomous routing -> Phase 3: Proactive carrier rebooking).

### Segment 6: Testing, CI/CD & Production Readiness [4:30 - 5:00]
- **Walkthrough**:
  - In terminal, execute `pytest -v`.
  - Show 100% passing tests across unit, integration, and scenario tests.
  - Highlight the GitHub Actions CI workflow and Docker Compose setup.
  - Conclude on how RevenueAI 360 serves as a battle-tested blueprint for enterprise AI adoption.
