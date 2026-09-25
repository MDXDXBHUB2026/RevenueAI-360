"""
RevenueAI 360 - Evaluator Agent
Measures concrete quality metrics: citation coverage, schema validity, field completeness,
and policy compliance without random numbers. Evaluates state before dispatch.
"""

import time
from typing import List
from agents.base_agent import BaseAgent
from shared.state import SharedWorkflowState, EvaluationResult, EvaluationMetric


class EvaluatorAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            name="Evaluator Agent",
            description="Performs deterministic evaluation of schema completeness, citation grounding, and policy adherence.",
            provider=provider,
        )

    async def run(self, state: SharedWorkflowState) -> SharedWorkflowState:
        start_time = time.time()
        metrics: List[EvaluationMetric] = []
        
        # 1. Metric: Schema Validity
        schema_valid = True
        schema_details = "State contains valid typed Pydantic models."
        if not state.event or not state.customer_identity:
            schema_valid = False
            schema_details = "Missing essential event or identity objects."
        metrics.append(EvaluationMetric(metric_name="schema_validity", passed=schema_valid, score=1.0 if schema_valid else 0.0, details=schema_details))

        # 2. Metric: Guardrail Compliance
        last_guardrail = state.guardrail_results[-1] if state.guardrail_results else None
        guardrail_passed = last_guardrail is not None and last_guardrail.verdict == "PASS"
        gr_details = f"Last guardrail verdict: {last_guardrail.verdict if last_guardrail else 'NONE'}"
        metrics.append(EvaluationMetric(metric_name="guardrail_compliance", passed=guardrail_passed, score=1.0 if guardrail_passed else 0.0, details=gr_details))

        # 3. Metric: Citation Grounding Coverage
        has_citations = len(state.citations) > 0
        citation_score = 1.0 if has_citations else (0.5 if state.intent == "lead" else 0.0)
        metrics.append(EvaluationMetric(
            metric_name="citation_grounding",
            passed=has_citations,
            score=citation_score,
            details=f"Attached citations count: {len(state.citations)}",
        ))

        # 4. Metric: Required Field Completeness
        completeness_passed = True
        completeness_details = "All expected agent outputs populated for intent."
        if state.intent == "lead" and (not state.qualification_output or not state.sales_output):
            completeness_passed = False
            completeness_details = "Lead workflow missing qualification or sales strategy."
        elif state.intent == "complaint" and not state.complaint_output:
            completeness_passed = False
            completeness_details = "Complaint workflow missing complaint analysis."
        metrics.append(EvaluationMetric(
            metric_name="field_completeness",
            passed=completeness_passed,
            score=1.0 if completeness_passed else 0.0,
            details=completeness_details,
        ))

        # Final verdict
        overall_pass = all(m.passed for m in metrics if m.metric_name in ["schema_validity", "guardrail_compliance", "field_completeness"])
        verdict = "PASS" if overall_pass else "FAIL"

        result = EvaluationResult(
            verdict=verdict,
            agent_evaluated="Multi-Agent Pipeline",
            metrics=metrics,
            feedback="All deterministic evaluation gates verified." if overall_pass else "Failed quality gates; revision required.",
        )

        state.evaluations.append(result)
        duration_ms = int((time.time() - start_time) * 1000)
        state.current_stage = f"evaluated_{verdict.lower()}"
        return state
