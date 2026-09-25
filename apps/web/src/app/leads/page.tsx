"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Target,
  Sparkles,
  Search,
  CheckCircle2,
  HelpCircle,
  ArrowRight,
  ShieldCheck,
  Send,
  Building2,
  Mail,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function LeadIntelligencePage() {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Fictional demonstration lead
  const leadData = {
    id: "lead-nexa-001",
    company: "Nexa Logistics (Fictional Demo)",
    contact: "Marcus Vance",
    role: "VP of Supply Chain Operations",
    email: "marcus.vance@nexalogistics.com",
    channel: "Inbound Webform",
    status: "DISCOVERY_REQUIRED",
    intent: "Inquiring about automated AI customer service copilot to resolve 12,000 weekly freight status calls.",
  };

  const runLeadAnalysis = async () => {
    try {
      setAnalyzing(true);
      const res = await api.triggerLeadAnalysis(leadData.id);
      setAnalysisResult(res);
      setFeedback("Lead intelligence and account research refreshed successfully.");
    } catch (e: any) {
      setFeedback(`Error: ${e.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Lead Intelligence & Account Research Workspace"
        subtitle="Automated background intelligence, explainable qualification rubric, and discovery question formulation"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Top Action Bar */}
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 flex items-center justify-between shadow-md">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <Target className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">{leadData.company}</h2>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {leadData.status}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Contact: <span className="text-slate-200">{leadData.contact}</span> ({leadData.role}) • Source: {leadData.channel}
              </p>
            </div>
          </div>

          <button
            onClick={runLeadAnalysis}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50"
          >
            <Sparkles className={`h-4 w-4 ${analyzing ? "animate-spin text-blue-300" : ""}`} />
            {analyzing ? "Synthesizing Intelligence..." : "Run AI Lead Analysis"}
          </button>
        </div>

        {feedback && (
          <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300">
            {feedback}
          </div>
        )}

        {/* Intelligence Dossier Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Account Research & Signals */}
          <div className="lg:col-span-6 space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Search className="h-4 w-4 text-blue-400" />
                Automated Account Research (Research Agent)
              </h3>

              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-500">Operational Footprint</span>
                  <p className="text-slate-300 leading-relaxed">
                    Manages over 4,500 active carrier contracts across North America and Europe, handling 12,000+ freight shipments weekly.
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-500">Technology Signals</span>
                  <ul className="list-disc list-inside text-slate-300 space-y-1 font-mono text-[11px]">
                    <li>Legacy Transport Management System (TMS) with REST webhooks</li>
                    <li>Enterprise Resource Planning (SAP ECC / S4HANA)</li>
                    <li>High volume email/WhatsApp freight inquiries from consignees</li>
                  </ul>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-500">Strategic Corporate Initiatives</span>
                  <p className="text-slate-300 leading-relaxed">
                    Publicly committed to deploying AI customer-facing agents to cut response latency under 3 minutes (Digital Strategy 2026).
                  </p>
                </div>
              </div>
            </div>

            {/* Evidence & Provenance Retention */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-3">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Research Provenance
              </h3>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded bg-slate-950/70 border border-slate-800 text-slate-300">
                  <span className="text-emerald-400 font-bold font-mono text-[10px] uppercase">Verified Source: </span>
                  Public Annual Logistics Technology Review 2026
                </div>
                <div className="p-2.5 rounded bg-slate-950/70 border border-slate-800 text-slate-300">
                  <span className="text-emerald-400 font-bold font-mono text-[10px] uppercase">Verified Source: </span>
                  Nexa Logistics Company Profile & Dispatch Centers
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Qualification Rubric & Discovery Questions */}
          <div className="lg:col-span-6 space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  Explainable Qualification (Qualification Agent)
                </h3>
                <span className="text-xs px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
                  DISCOVERY REQUIRED
                </span>
              </div>

              <div className="space-y-3">
                <div className="p-3.5 rounded-lg bg-amber-950/20 border border-amber-500/30 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-amber-400">Identified Discovery Unknowns</span>
                  <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                    <li>Key budget sign-off authority and executive steering committee involvement.</li>
                    <li>Target production rollout milestone and pilot launch window.</li>
                  </ul>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2">
                  <span className="text-[10px] uppercase font-bold text-blue-400">High-Yield Discovery Questions</span>
                  <div className="space-y-1.5 text-xs text-slate-300">
                    <p className="p-2 rounded bg-slate-900/70 border border-slate-800">
                      1. "Who will be the primary executive sponsor and sign-off authority for the AI deployment budget?"
                    </p>
                    <p className="p-2 rounded bg-slate-900/70 border border-slate-800">
                      2. "What is Nexa's target timeline for rolling out the first automated customer communication workflows?"
                    </p>
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-emerald-400">Recommended Commercial Action</span>
                  <p className="text-xs text-slate-300">
                    Schedule a 25-minute technical discovery session with Marcus Vance focusing on legacy TMS webhook integration.
                  </p>
                </div>
              </div>
            </div>

            {/* Sales Engagement Draft with Approval Link */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Mail className="h-4 w-4 text-blue-400" />
                  Personalized Outreach Draft (Sales Agent)
                </h3>
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  Grounded in RAG
                </span>
              </div>

              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-sans leading-relaxed whitespace-pre-wrap">
{`Hi Marcus,

Thank you for reaching out regarding customer service automation for Nexa Logistics.

Given Nexa's scale in freight brokerage and carrier contracts, repetitive shipment inquiries often create significant operational bottlenecks for dispatch teams.

Our AI Customer Service Copilot connects directly with transport management systems to deliver instant, accurate GPS transit updates and delay notifications across email and WhatsApp.

Would you be open to a 25-minute technical discovery conversation next Tuesday or Thursday to review a tailored workflow architecture for Nexa Logistics?`}
              </div>

              <div className="pt-2 flex items-center justify-between">
                <span className="text-[11px] text-amber-400 font-medium">Status: Awaiting Review in Approval Centre</span>
                <Link
                  href="/approvals"
                  className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors flex items-center gap-1"
                >
                  Review & Authorize <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
