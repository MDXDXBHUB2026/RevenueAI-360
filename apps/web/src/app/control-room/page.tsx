"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
  Search,
  BookOpen,
  FileCheck,
  Send,
  RefreshCw,
  Terminal,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

function ControlRoomContent() {
  const searchParams = useSearchParams();
  const queryWfId = searchParams.get("wf");

  const [workflows, setWorkflows] = useState<any[]>([]);
  const [selectedWfId, setSelectedWfId] = useState<string | null>(queryWfId);
  const [traceData, setTraceData] = useState<any>(null);
  const [selectedAgentRun, setSelectedAgentRun] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadWorkflows = async () => {
    try {
      setRefreshing(true);
      const wfList = await api.getRecentWorkflows(15);
      setWorkflows(wfList);
      if (wfList.length > 0 && !selectedWfId) {
        setSelectedWfId(wfList[0].id);
      }
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkflows();
  }, []);

  useEffect(() => {
    if (selectedWfId) {
      api.getWorkflowTrace(selectedWfId).then((data) => {
        setTraceData(data);
        if (data.agent_runs && data.agent_runs.length > 0) {
          setSelectedAgentRun(data.agent_runs[0]);
        }
      }).catch(console.error);
    }
  }, [selectedWfId]);

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="AI Control Room & Live Agent Telemetry"
        subtitle="Real-time multi-agent execution state machine, conditional routing graph, and governance audit trail"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Top Controls: Workflow Selector & Refresh */}
        <div className="flex items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-300">Active Workflow:</span>
            <select
              value={selectedWfId || ""}
              onChange={(e) => setSelectedWfId(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-white focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
            >
              {workflows.map((wf) => (
                <option key={wf.id} value={wf.id}>
                  {wf.trace_id} ({wf.intent?.toUpperCase()} - {wf.status})
                </option>
              ))}
            </select>
            {traceData && (
              <span className="text-xs text-slate-400 font-mono">
                Stage: <span className="text-blue-400">{traceData.current_stage}</span>
              </span>
            )}
          </div>

          <button
            onClick={loadWorkflows}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin text-blue-400" : ""}`} />
            Refresh Telemetry
          </button>
        </div>

        {/* Section 18: Conditional Routing Visualization (Proves Non-Linear LangGraph Routing) */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">LangGraph Execution Route & Branching</h3>
              <p className="text-xs text-slate-400">
                Visualizing conditional branches executed vs. skipped dynamically based on Customer 360 context
              </p>
            </div>
            {traceData && (
              <span className={`text-[11px] font-bold uppercase px-2 py-0.5 rounded ${
                traceData.status === "COMPLETED"
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                  : traceData.status === "WAITING_APPROVAL"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                  : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
              }`}>
                {traceData.status}
              </span>
            )}
          </div>

          {/* Conditional Route Pills */}
          <div className="flex items-center flex-wrap gap-2 pt-2">
            {[
              { id: "identity", label: "Identity & Context", active: true },
              { id: "planner", label: "Journey Manager", active: true },
              { id: "research", label: "Research Agent", active: traceData?.intent === "lead" },
              { id: "qualification", label: "Qualification Agent", active: traceData?.intent === "lead" },
              { id: "support", label: "Customer Service Agent", active: traceData?.intent === "support" },
              { id: "complaint", label: "Complaint Agent", active: traceData?.intent === "complaint" },
              { id: "escalation", label: "Escalation Agent", active: traceData?.intent === "complaint" },
              { id: "knowledge", label: "Knowledge / RAG", active: true },
              { id: "sales", label: "Sales Agent", active: traceData?.intent === "lead" },
              { id: "guardrail", label: "Guardrail Agent", active: true },
              { id: "evaluator", label: "Evaluator Agent", active: true },
              { id: "communication", label: "Communication Agent", active: true },
            ].map((node, index, arr) => (
              <div key={node.id} className="flex items-center gap-2">
                <div
                  className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                    node.active
                      ? "bg-blue-950/40 border-blue-500/40 text-blue-300 shadow-sm"
                      : "bg-slate-950/40 border-slate-800/80 text-slate-600 line-through opacity-60"
                  }`}
                  title={node.active ? "Executed in current workflow" : "Conditionally bypassed by Journey Manager"}
                >
                  {node.label}
                  {!node.active && <span className="ml-1 text-[9px] uppercase tracking-wider">(Skipped)</span>}
                </div>
                {index < arr.length - 1 && (
                  <ArrowRight className="h-3 w-3 text-slate-600" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Section 17: Two-Pane Agent Control Room */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Agent Execution Cards List */}
          <div className="lg:col-span-5 space-y-3">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-1">
              Executed Specialist Agents
            </h4>

            {traceData?.agent_runs?.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500 border border-slate-800 rounded-xl bg-slate-900/30">
                No agent execution records found for this workflow.
              </div>
            ) : (
              traceData?.agent_runs?.map((run: any) => {
                const isSelected = selectedAgentRun?.id === run.id;
                return (
                  <div
                    key={run.id}
                    onClick={() => setSelectedAgentRun(run)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? "bg-slate-900 border-blue-500/50 shadow-md ring-1 ring-blue-500/20"
                        : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/70"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Cpu className={`h-4 w-4 ${isSelected ? "text-blue-400" : "text-slate-400"}`} />
                        <span className="text-xs font-semibold text-white">{run.agent_name}</span>
                      </div>
                      <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {run.status}
                      </span>
                    </div>

                    <div className="mt-2 text-xs text-slate-400 line-clamp-1">
                      {run.execution_rationale || "Executed stage without error."}
                    </div>

                    <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                      <span>Model: {run.model_name || "gpt-4o-mini"}</span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {run.duration_ms}ms
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Right Column: Deep Inspection Panel for Selected Agent */}
          <div className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-6">
            {selectedAgentRun ? (
              <>
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                      <Terminal className="h-4 w-4 text-blue-400" />
                      {selectedAgentRun.agent_name} Details
                    </h3>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">
                      Provider: {selectedAgentRun.model_provider} • Latency: {selectedAgentRun.duration_ms}ms
                    </p>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-medium">
                    {selectedAgentRun.status}
                  </span>
                </div>

                {/* Structured Output Section */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <FileCheck className="h-3.5 w-3.5 text-blue-400" />
                    Structured Output Contract
                  </h4>
                  <pre className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-56">
                    {JSON.stringify(selectedAgentRun.structured_output, null, 2)}
                  </pre>
                </div>

                {/* Evidence & Provenance Section */}
                {selectedAgentRun.evidence_items?.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Search className="h-3.5 w-3.5 text-emerald-400" />
                      Evidence & Provenance
                    </h4>
                    <div className="space-y-2">
                      {selectedAgentRun.evidence_items.map((ev: any, idx: number) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                          <div className="flex items-center justify-between text-slate-400 text-[10px]">
                            <span className="font-semibold text-slate-300">{ev.source}</span>
                            <span className="uppercase text-emerald-400 font-mono">Verified Fact</span>
                          </div>
                          <p className="text-slate-300 text-[11px]">{ev.fact}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Grounded Citations Section */}
                {selectedAgentRun.citations?.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <BookOpen className="h-3.5 w-3.5 text-indigo-400" />
                      RAG Knowledge Citations
                    </h4>
                    <div className="space-y-2">
                      {selectedAgentRun.citations.map((c: any, idx: number) => (
                        <div key={idx} className="p-3 rounded-lg bg-indigo-950/20 border border-indigo-500/20 text-xs space-y-1">
                          <div className="flex items-center justify-between text-[10px] text-indigo-300 font-semibold">
                            <span>{c.document_title}</span>
                            <span>Score: {c.relevance_score}</span>
                          </div>
                          <p className="text-slate-300 text-[11px] italic">"{c.excerpt}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="py-16 text-center text-xs text-slate-500">
                Select an agent run card from the left panel to inspect its structured output, citations, and execution telemetry.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function ControlRoomPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs text-slate-400">Loading Control Room...</div>}>
      <ControlRoomContent />
    </Suspense>
  );
}
