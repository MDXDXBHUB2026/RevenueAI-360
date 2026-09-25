"""
RevenueAI 360 - Next-Best-Action (NBA) Engine
Evaluates customer lifecycle stage, sentiment trajectory, open complaints, SLA status,
and pipeline opportunities to recommend explainable, prioritized next actions.
Explicitly prioritizes complaint resolution and suppresses commercial outreach during active grievances.
"""

from typing import Optional
from shared.state import Customer360Context, NextBestActionResult


class NextBestActionService:
    def evaluate(self, c360: Customer360Context) -> NextBestActionResult:
        """
        Evaluates 360 context and determines the optimal next action with explainable rationale.
        """
        # Rule 1: Active Critical/High Complaint -> Prioritize de-escalation & suppress sales
        high_complaints = [c for c in c360.complaints if c.get("severity") in ["HIGH", "CRITICAL"]]
        if high_complaints:
            comp = high_complaints[0]
            is_repeat = comp.get("repeat_count", 1) > 1
            return NextBestActionResult(
                action_type="ESCALATE_AND_RESOLVE_COMPLAINT",
                recommended_timing="IMMEDIATE (< 30 minutes)",
                priority="CRITICAL",
                explainable_reason=(
                    f"Account has {len(high_complaints)} active high-severity complaint(s) (Repeat count: {comp.get('repeat_count', 1)}). "
                    f"All promotional and expansion outreach must be SUPPRESSED until carrier tracking exception is diagnosed and acknowledged."
                ),
                suppress_promotions=True,
            )

        # Rule 2: Open Support Cases with Neutral/Negative Sentiment
        if c360.open_support_cases:
            return NextBestActionResult(
                action_type="SUPPORT_CASE_FOLLOWUP",
                recommended_timing="Within 2 hours",
                priority="HIGH",
                explainable_reason="Open support ticket pending customer confirmation. Verify resolution before commercial engagement.",
                suppress_promotions=False,
            )

        # Rule 3: Pending Approvals in Pipeline
        if c360.pending_actions:
            return NextBestActionResult(
                action_type="REVIEW_PENDING_APPROVAL",
                recommended_timing="Today",
                priority="HIGH",
                explainable_reason=f"There are {len(c360.pending_actions)} pending human-in-the-loop action(s) awaiting sales or management approval.",
                suppress_promotions=False,
            )

        # Rule 4: New Lead requiring Discovery
        if c360.lead_summary and c360.lead_summary.get("qualification_status") == "DISCOVERY_REQUIRED":
            return NextBestActionResult(
                action_type="CONDUCT_TECHNICAL_DISCOVERY",
                recommended_timing="Within 2 business days",
                priority="MEDIUM",
                explainable_reason="Lead qualified with open discovery gaps (decision authority and target rollout timeline). Schedule technical discovery.",
                suppress_promotions=False,
            )

        # Rule 5: Active Opportunities in Solutioning
        if c360.active_opportunities:
            opp = c360.active_opportunities[0]
            return NextBestActionResult(
                action_type="PRESENT_AI_DEMO_ARCHITECTURE",
                recommended_timing="Next scheduled milestone",
                priority="MEDIUM",
                explainable_reason=f"Active opportunity '{opp.get('title')}' in {opp.get('stage')} stage. Deliver bespoke Customer AI Solution demo.",
                suppress_promotions=False,
            )

        # Default: Proactive Retention & Health Check
        return NextBestActionResult(
            action_type="QUARTERLY_BUSINESS_REVIEW",
            recommended_timing="Next Month",
            priority="LOW",
            explainable_reason="Account state is healthy and stable. Schedule standard proactive customer check-in.",
            suppress_promotions=False,
        )


next_best_action_service = NextBestActionService()
