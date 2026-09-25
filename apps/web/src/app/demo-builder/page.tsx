"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Sparkles,
  Cpu,
  Wrench,
  Database,
  Network,
  ShieldCheck,
  Calendar,
  AlertCircle,
  Send,
  Layers,
  CheckCircle2,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

import { Suspense } from "react";

function AIDemoBuilderContent() {
  const searchParams = useSearchParams();
  const queryAccount = searchParams.get("account") || "acc-nexa-logistics-demo";

  const [problem, setProblem] = useState(
    "12,000 weekly freight tracking inquiries and lack of automated exception routing during transit disruptions causing severe dispatcher fatigue."
  );
  const [notes, setNotes] = useState(
    "Legacy SAP ERP and high volume of repetitive 'Where is my truck' messages across email and WhatsApp."
  );
  const [generating, setGenerating] = useState(false);
  const [solutionSpec, setSolutionSpec] = useState<any>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setGenerating(true);
      const res = await api.createAIDemo(queryAccount, {
        customer_problem: problem,
        discovery_notes: notes,
      });
      setSolutionSpec(res);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Customer AI Demo Builder"
        subtitle="Rapid Solution Engineering: Turn customer operational bottlenecks into bespoke multi-agent solution architecture proposals"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Solution Input Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-400" />
              Customer Problem & Discovery Notes Input
            </h3>
            <span className="text-[10px] uppercase font-bold text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              Solution Design Mode
            </span>
          </div>

          <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Core Customer Operational Bottleneck
              </label>
              <textarea
                rows={3}
                value={problem}
                onChange={(e) => setProblem(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none font-sans"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Technical Discovery & Integration Constraints
              </label>
              <textarea
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none font-sans"
              />
            </div>

            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                disabled={generating}
                className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <Sparkles className={`h-4 w-4 ${generating ? "animate-spin" : ""}`} />
                {generating ? "Synthesizing Architecture..." : "Generate AI Solution Concept"}
              </button>
            </div>
          </form>
        </div>

        {/* Output Architecture Dossier */}
        {solutionSpec && (
          <div className="space-y-6 animate-fadeIn">
            {/* Disclaimer Alert */}
            <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-300/90 leading-relaxed">
                {solutionSpec.disclaimer}
              </p>
            </div>

            {/* Architecture Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-500">Recommended Pattern</span>
                <p className="text-xs font-bold text-white">{solutionSpec.recommended_ai_pattern}</p>
              </div>
              <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-500">Target Outcome</span>
                <p className="text-xs font-medium text-slate-300">{solutionSpec.desired_outcome}</p>
              </div>
              <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-500">Governance Policy</span>
                <p className="text-xs font-medium text-slate-300">{solutionSpec.human_oversight_policy}</p>
              </div>
            </div>

            {/* Proposed Multi-Agent Roster & Tools */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Proposed Agents */}
              <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
                <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-blue-400" />
                  Proposed Cooperating Agents
                </h4>
                <div className="space-y-3">
                  {solutionSpec.proposed_agents.map((ag: any, idx: number) => (
                    <div key={idx} className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white">{ag.name}</span>
                        <span className="text-[10px] font-mono text-blue-400">Agent Spec</span>
                      </div>
                      <p className="text-xs text-slate-300">{ag.role}</p>
                      <p className="text-[11px] text-slate-500 pt-1">
                        <strong>Decision Boundary:</strong> {ag.decision_boundary}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Proposed Tools */}
              <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
                <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Wrench className="h-4 w-4 text-emerald-400" />
                  Proposed Tool Registry
                </h4>
                <div className="space-y-3">
                  {solutionSpec.proposed_tools.map((t: any, idx: number) => (
                    <div key={idx} className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono font-bold text-white">{t.name}</span>
                        <span className="text-[10px] uppercase font-bold text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded">
                          {t.permission_tier}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono">
                        Target System: {t.system_target}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Prototype-to-Production Roadmap */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <Calendar className="h-4 w-4 text-purple-400" />
                Prototype-to-Production Phased Roadmap
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {solutionSpec.prototype_to_production_roadmap.map((stage: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-[10px] uppercase font-bold text-purple-400">{stage.phase}</span>
                    <p className="text-xs text-slate-200 leading-relaxed">{stage.milestone}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default function AIDemoBuilderPage() {
  return (
    <Suspense
      fallback={
        <div className="flex-1 flex items-center justify-center p-12 text-slate-400 text-xs">
          Loading AI Demo Builder...
        </div>
      }
    >
      <AIDemoBuilderContent />
    </Suspense>
  );
}
