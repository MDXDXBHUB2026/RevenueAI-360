"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Send,
  Eye,
  Edit3,
  ShieldCheck,
  RefreshCw,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function ApprovalCentrePage() {
  const [pendingActions, setPendingActions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAction, setSelectedAction] = useState<any>(null);
  const [editBody, setEditBody] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.getPendingActions();
      setPendingActions(data);
      if (data.length > 0 && !selectedAction) {
        setSelectedAction(data[0]);
        setEditBody(data[0].payload?.body || "");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApprove = async (actionId: string) => {
    try {
      setProcessing(true);
      const res = await api.approveAction(actionId, {
        decision: "APPROVED",
        reviewer: "Senior AI Solutions Reviewer",
        comments: "Verified personalized discovery questions and commercial grounding.",
        edited_payload: selectedAction ? { ...selectedAction.payload, body: editBody } : undefined,
      });
      setFeedback(`Action authorized & dispatched via deterministic tool: ${res.tool_execution?.tool_name}`);
      await loadData();
    } catch (e: any) {
      setFeedback(`Error: ${e.message}`);
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async (actionId: string) => {
    try {
      setProcessing(true);
      await api.rejectAction(actionId, {
        decision: "REJECTED",
        reviewer: "Senior AI Solutions Reviewer",
        comments: "Rejected by human reviewer for manual rewrite.",
      });
      setFeedback("Action rejected and returned to pipeline.");
      await loadData();
    } catch (e: any) {
      setFeedback(`Error: ${e.message}`);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Human-In-The-Loop Approval Centre"
        subtitle="Tier 2 & Tier 3 Governance Queue: Inspect, edit, and authorize external customer dispatches"
      />

      <main className="flex-1 p-8 space-y-6">
        {feedback && (
          <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300 flex items-center justify-between">
            <span>{feedback}</span>
            <button onClick={() => setFeedback(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Pending Actions Queue */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center justify-between pb-1">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Pending Actions ({pendingActions.length})
              </h3>
              <button
                onClick={loadData}
                className="text-xs text-blue-400 hover:underline flex items-center gap-1 font-medium"
              >
                <RefreshCw className="h-3 w-3" /> Refresh
              </button>
            </div>

            {pendingActions.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500 border border-slate-800 rounded-xl bg-slate-900/30">
                All pending actions have been reviewed and executed.
              </div>
            ) : (
              pendingActions.map((action) => {
                const isSelected = selectedAction?.id === action.id;
                return (
                  <div
                    key={action.id}
                    onClick={() => {
                      setSelectedAction(action);
                      setEditBody(action.payload?.body || "");
                    }}
                    className={`p-4 rounded-xl border cursor-pointer transition-all space-y-2 ${
                      isSelected
                        ? "bg-slate-900 border-blue-500/60 shadow-md ring-1 ring-blue-500/20"
                        : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/70"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-white">
                        {action.action_type}
                      </span>
                      <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                        action.risk_level === "HIGH"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      }`}>
                        {action.risk_level} Risk
                      </span>
                    </div>

                    <p className="text-xs text-slate-400 line-clamp-2 font-sans">
                      {action.payload?.body || "Outreach dispatch draft."}
                    </p>

                    <div className="pt-1 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                      <span>Requested by: {action.requested_by_agent}</span>
                      <span>Channel: {action.payload?.channel || "email"}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Right Column: Deep Inspection, Inline Edit, and Authorization */}
          <div className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-6">
            {selectedAction ? (
              <>
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-white">
                      Action Review: <span className="font-mono text-blue-400">{selectedAction.action_type}</span>
                    </h3>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">
                      Recipient: {selectedAction.payload?.recipient || "N/A"}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleReject(selectedAction.id)}
                      disabled={processing}
                      className="px-3.5 py-1.5 rounded-lg border border-rose-600/40 bg-rose-950/20 hover:bg-rose-900/40 text-rose-300 text-xs font-semibold transition-colors flex items-center gap-1.5"
                    >
                      <XCircle className="h-3.5 w-3.5" />
                      Reject
                    </button>
                    <button
                      onClick={() => handleApprove(selectedAction.id)}
                      disabled={processing}
                      className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition-colors flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      {processing ? "Authorizing..." : "Approve & Execute Tool"}
                    </button>
                  </div>
                </div>

                {/* Editable Payload Area */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Edit3 className="h-3.5 w-3.5 text-blue-400" />
                      Editable Message Body
                    </label>
                    <span className="text-[11px] text-slate-500 font-mono">
                      (Human edits will overwrite agent draft before dispatch)
                    </span>
                  </div>

                  <textarea
                    rows={12}
                    value={editBody}
                    onChange={(e) => setEditBody(e.target.value)}
                    className="w-full p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 font-sans leading-relaxed focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>

                {/* Audit & Governance Rules Note */}
                <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-400 flex items-start gap-2.5">
                  <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                  <p className="leading-relaxed text-[11px]">
                    <strong className="text-slate-200">Governance Policy Notice: </strong>
                    Approval executes the underlying registered communication tool with verified credentials.
                    The final dispatched content and reviewer ID will be logged into the permanent immutable audit trail.
                  </p>
                </div>
              </>
            ) : (
              <div className="py-20 text-center text-xs text-slate-500">
                Select an item from the pending actions list on the left to review, edit, and approve.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
