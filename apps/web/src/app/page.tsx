"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  ShieldAlert,
  ArrowUpRight,
  Clock,
  Sparkles,
  Inbox,
  UserCheck,
  Send,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [recentWorkflows, setRecentWorkflows] = useState<any[]>([]);
  const [pendingActions, setPendingActions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [inboundTriggering, setInboundTriggering] = useState(false);
  const [inboundFeedback, setInboundFeedback] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, wf, pa] = await Promise.all([
          api.getDashboardMetrics().catch(() => null),
          api.getRecentWorkflows(6).catch(() => []),
          api.getPendingActions().catch(() => []),
        ]);
        setMetrics(m);
        setRecentWorkflows(wf);
        setPendingActions(pa);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const triggerDemoLead = async () => {
    try {
      setInboundTriggering(true);
      const res = await api.ingestInboundEvent({
        channel: "email",
        external_identity: "marcus.vance@nexalogistics.com",
        subject: "Inquiry: AI Freight Exception & Dispatch Copilot",
        content: "Nexa Logistics handles 12,000 weekly freight loads. We are evaluating an autonomous copilot to answer shipper inquiries and integrate with our SAP/TMS. Please coordinate discovery.",
      });
      setInboundFeedback(`Workflow triggered: ${res.workflow_id.slice(0, 8)}... (${res.current_stage})`);
      setTimeout(() => {
        window.location.href = `/control-room?wf=${res.workflow_id}`;
      }, 1200);
    } catch (e: any) {
      setInboundFeedback(`Error: ${e.message}`);
    } finally {
      setInboundTriggering(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Executive Intelligence Dashboard"
        subtitle="Real-time multi-agent customer lifecycle telemetry across all digital touchpoints"
      />

      <main className="flex-1 p-8 space-y-8">
        {/* Top Banner: Portfolio Demo Trigger */}
        <div className="rounded-xl border border-blue-500/30 bg-gradient-to-r from-blue-950/40 via-slate-900 to-indigo-950/30 p-6 flex items-center justify-between shadow-lg">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30 uppercase tracking-wider">
                Primary Demo Scenario
              </span>
              <h3 className="text-base font-semibold text-white">Nexa Logistics Customer Journey</h3>
            </div>
            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              Experience the complete autonomous pipeline: inbound email lead ingestion, account enrichment,
              explainable discovery qualification, RAG capability retrieval, guardrail safety checks, and HITL approval.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={triggerDemoLead}
              disabled={inboundTriggering}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-all disabled:opacity-50"
            >
              <Send className={`h-3.5 w-3.5 ${inboundTriggering ? "animate-pulse" : ""}`} />
              {inboundTriggering ? "Launching Agents..." : "Simulate Inbound Lead"}
            </button>
            <Link
              href="/control-room"
              className="px-4 py-2.5 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-semibold transition-all"
            >
              Open Control Room
            </Link>
          </div>
        </div>

        {inboundFeedback && (
          <div className="p-3 rounded-lg bg-blue-950/60 border border-blue-500/40 text-xs text-blue-200 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-blue-400" />
            {inboundFeedback}
          </div>
        )}

        {/* Core Metric Cards (Genuine, un-fabricated data) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 space-y-3">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">New Leads</span>
              <UserCheck className="h-4 w-4 text-blue-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{metrics?.new_leads ?? "--"}</span>
              <span className="text-[11px] text-amber-400 font-medium">
                {metrics?.leads_requiring_discovery ?? 0} require discovery
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Evaluated by Qualification Agent</p>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 space-y-3">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Active Opportunities</span>
              <TrendingUp className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{metrics?.active_opportunities ?? "--"}</span>
              <span className="text-[11px] text-emerald-400 font-medium">In Solutioning</span>
            </div>
            <p className="text-[11px] text-slate-500">Supported by AI Demo Builder</p>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 space-y-3">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Complaints & Grievances</span>
              <AlertTriangle className="h-4 w-4 text-rose-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{metrics?.open_complaints ?? "--"}</span>
              <span className="text-[11px] text-rose-400 font-medium">
                {metrics?.high_priority_complaints ?? 0} High/Critical
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Auto-escalated to Engineering</p>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 space-y-3">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium">Pending Approvals</span>
              <CheckCircle2 className="h-4 w-4 text-amber-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{metrics?.pending_approvals ?? "--"}</span>
              <span className="text-[11px] text-amber-400 font-medium">Tier 2 HITL Queue</span>
            </div>
            <p className="text-[11px] text-slate-500">Awaiting human sales rep review</p>
          </div>
        </div>

        {/* Split Grid: Recent Workflows & Pending Approvals */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Multi-Agent Workflows */}
          <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-white">Live Multi-Agent Workflow Runs</h3>
                <p className="text-xs text-slate-400">Inspecting real-time LangGraph state transitions and decisions</p>
              </div>
              <Link
                href="/control-room"
                className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
              >
                View all in Control Room <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>

            <div className="divide-y divide-slate-800/80">
              {recentWorkflows.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-500">
                  No active workflows recorded. Simulate an inbound event above to observe real-time orchestration.
                </div>
              ) : (
                recentWorkflows.map((wf) => (
                  <div key={wf.id} className="py-3.5 flex items-center justify-between hover:bg-slate-900/60 px-2 rounded-lg transition-colors">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                          wf.intent === "complaint"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                            : wf.intent === "support"
                            ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                            : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        }`}>
                          {wf.intent || "LEAD"}
                        </span>
                        <span className="text-xs font-mono text-slate-300 font-medium">
                          {wf.trace_id || wf.id.slice(0, 8)}
                        </span>
                        <span className="text-[11px] text-slate-500">Channel: {wf.channel}</span>
                      </div>
                      <p className="text-xs text-slate-400">
                        Current Stage: <span className="text-slate-200 font-mono">{wf.current_stage}</span>
                      </p>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className={`text-xs px-2.5 py-1 rounded font-medium ${
                        wf.status === "COMPLETED"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                          : wf.status === "WAITING_APPROVAL"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                          : "bg-blue-500/10 text-blue-400 border border-blue-500/30"
                      }`}>
                        {wf.status}
                      </span>
                      <Link
                        href={`/control-room?wf=${wf.id}`}
                        className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                        title="Inspect trace"
                      >
                        <ArrowUpRight className="h-3.5 w-3.5" />
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Pending HITL Governance Queue */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-white">Pending Approval Queue</h3>
                <p className="text-xs text-slate-400">Human-In-The-Loop Tier 2 Gates</p>
              </div>
              <Link
                href="/approvals"
                className="text-xs text-blue-400 hover:text-blue-300 font-medium"
              >
                Review All
              </Link>
            </div>

            <div className="space-y-3">
              {pendingActions.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-500">
                  No actions currently pending approval. All Tier 1 executions succeeded autonomously.
                </div>
              ) : (
                pendingActions.slice(0, 4).map((action) => (
                  <div
                    key={action.id}
                    className="p-3.5 rounded-lg border border-slate-800 bg-slate-950/70 space-y-2 hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-mono font-semibold text-slate-300">
                        {action.action_type}
                      </span>
                      <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        {action.risk_level} Risk
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-2">
                      {action.payload?.body || action.payload?.message || "Outreach message awaiting review."}
                    </p>
                    <div className="flex items-center justify-between pt-1">
                      <span className="text-[10px] text-slate-500">
                        Agent: {action.requested_by_agent}
                      </span>
                      <Link
                        href="/approvals"
                        className="text-xs text-blue-400 hover:underline font-medium"
                      >
                        Inspect & Authorize →
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
