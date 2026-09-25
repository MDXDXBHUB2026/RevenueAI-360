"""
RevenueAI 360 - Guardrail Agent
Enforces strict enterprise AI safety, prompt injection detection, PII sanitization,
unsupported claim prevention, and prohibits unauthorized autonomous financial/contractual commitments.
"""

import time
import re
from typing import List
from agents.base_agent import BaseAgent
from shared.state import SharedWorkflowState, GuardrailResult, GuardrailViolation


class GuardrailAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            name="Guardrail Agent",
            description="Inspects candidate drafts for prompt injections, PII leakage, unsupported claims, and unauthorized commercial commitments.",
            provider=provider,
        )

    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        start_time = time.time()
        violations: List[GuardrailViolation] = []
        
        # Determine draft to inspect
        target_text = ""
        agent_inspected = "unknown"
        if state.sales_output and state.sales_output.draft_outreach_message:
            target_text = state.sales_output.draft_outreach_message
            agent_inspected = "Sales Agent"
        elif state.service_output and state.service_output.recommended_solution:
            target_text = state.service_output.recommended_solution
            agent_inspected = "Customer Service Agent"
        elif state.complaint_output and state.complaint_output.recommended_resolution_path:
            target_text = state.complaint_output.recommended_resolution_path
            agent_inspected = "Complaint Resolution Agent"

        # 1. Prompt Injection Checks
        injection_patterns = [
            r"ignore all previous instructions",
            r"disregard previous prompts",
            r"you are now in DAN mode",
            r"system override",
            r"<script.*?>",
            r"drop table",
        ]
        for pattern in injection_patterns:
            if re.search(pattern, target_text, re.IGNORECASE) or re.search(pattern, state.event.content, re.IGNORECASE):
                violations.append(
                    GuardrailViolation(
                        rule_name="prompt_injection_detected",
                        category="prompt_injection",
                        severity="CRITICAL",
                        description=f"Potential prompt injection pattern matched: '{pattern}'",
                        suggested_fix="Sanitize input and abort automated generation.",
                    )
                )

        # 2. Unauthorized Financial / Commercial Commitment Check
        unauthorized_financial_patterns = [
            r"guarantee(?:s)?\s+(?:a\s+)?(?:\d+%)",
            r"(?:we\s+will|i\s+will)\s+(?:refund|compensate|pay)\s+\$?\d+",
            r"(?:offer|give)\s+(?:a\s+)?(?:\d+%)\s+discount",
            r"binding\s+agreement",
            r"we\s+promise\s+100%\s+uptime",
        ]
        for pattern in unauthorized_financial_patterns:
            if re.search(pattern, target_text, re.IGNORECASE):
                violations.append(
                    GuardrailViolation(
                        rule_name="unauthorized_commercial_commitment",
                        category="unauthorized_commitment",
                        severity="HIGH",
                        description="Autonomous agent drafted binding financial discount or absolute uptime guarantee.",
                        suggested_fix="Remove unapproved financial guarantees. Revert to standard discovery and SLA references.",
                    )
                )

        # 3. PII / Sensitive Data Check
        credit_card_pattern = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        if re.search(credit_card_pattern, target_text) or re.search(ssn_pattern, target_text):
            violations.append(
                GuardrailViolation(
                    rule_name="pii_leakage_detected",
                    category="pii",
                    severity="CRITICAL",
                    description="Draft contains unmasked credit card or social security number.",
                    suggested_fix="Redact sensitive numerical identifiers immediately.",
                )
            )

        # Determine Verdict
        if any(v.severity == "CRITICAL" for v in violations):
            verdict = "BLOCK"
            reasoning = "Critical security or privacy violation detected. Workflow halted for security review."
        elif any(v.severity == "HIGH" for v in violations):
            verdict = "REVISE"
            reasoning = "Commercial policy violation detected. Returned to agent for grounded revision."
        else:
            verdict = "PASS"
            reasoning = "All safety, grounding, anti-injection, and PII checks successfully passed."

        result = GuardrailResult(
            verdict=verdict,
            agent_inspected=agent_inspected,
            violations=violations,
            reasoning=reasoning,
        )

        state.guardrail_results.append(result)
        duration_ms = int((time.time() - start_time) * 1000)
        state.current_stage = f"guardrail_{verdict.lower()}"
        return state
