"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Settings,
  RefreshCw,
  Play,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  ExternalLink,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function SettingsAndDemoModePage() {
  const [resetting, setResetting] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const demoSteps = [
    { step: 1, title: "Inbound Prospect Enquiry", link: "/inbox", desc: "Simulate lead inquiry regarding freight status copilot." },
    { step: 2, title: "Automated Account Research", link: "/leads", desc: "Inspect Nexa Logistics corporate profile and 4,500 carrier contracts." },
    { step: 3, title: "Explainable Lead Qualification", link: "/leads", desc: "Review DISCOVERY REQUIRED rubric and 2 high-yield questions." },
    { step: 4, title: "Watch Multi-Agent Orchestration", link: "/control-room", desc: "Observe real-time LangGraph routing, evidence, and duration." },
    { step: 5, title: "Human-In-The-Loop Authorization", link: "/approvals", desc: "Review, edit, and authorize Tier 2 personalized outreach." },
    { step: 6, title: "Cross-Channel WhatsApp Recognition", link: "/inbox", desc: "Marcus replies via WhatsApp; system resolves same identity." },
    { step: 7, title: "Customer Conversion", link: "/customers/acc-nexa-logistics-demo", desc: "Convert prospect to customer state with 1-click." },
    { step: 8, title: "Operational Support Query", link: "/support", desc: "Submit freight ETA inquiry; watch Customer Service Agent resolve via RAG." },
    { step: 9, title: "Repeat Complaint & SLA Breach", link: "/support", desc: "Inject repeated complaint; witness automatic escalation to Engineering." },
    { step: 10, title: "Customer 360 Timeline & Next-Best-Action", link: "/customers/acc-nexa-logistics-demo", desc: "Verify complaint prioritization and promotional suppression." },
    { step: 11, title: "Customer AI Demo Architecture", link: "/demo-builder", desc: "Generate multi-agent solution architecture and production roadmap." },
    { step: 12, title: "Quality Gates & Telemetry Audit", link: "/evaluations", desc: "Review zero-leakage guardrails and citation coverage." },
  ];

  const handleReset = async () => {
    try {
      setResetting(true);
      await api.resetDemoData();
      setFeedback("Nexa Logistics demonstration dataset reset to pristine baseline state.");
    } catch (e: any) {
      setFeedback(`Error: ${e.message}`);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Settings & Portfolio Walkthrough Guide"
        subtitle="Step-by-step 5-7 minute demonstration guide and system configuration"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Reset State Control */}
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Reset Demonstration Data</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Restores Nexa Logistics, contacts, opportunities, and RAG knowledge documents to baseline demo state.
            </p>
          </div>
          <button
            onClick={handleReset}
            disabled={resetting}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${resetting ? "animate-spin" : ""}`} />
            {resetting ? "Resetting..." : "Reset Demo Baseline"}
          </button>
        </div>

        {feedback && (
          <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300">
            {feedback}
          </div>
        )}

        {/* 12-Step Walkthrough Flow */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Interactive 5–7 Minute Portfolio Demonstration Script</h3>
              <p className="text-xs text-slate-400">Step-by-step tour demonstrating all 12 specialized agents and engineering capabilities</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
            {demoSteps.map((item) => (
              <div
                key={item.step}
                className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 space-y-2 flex flex-col justify-between hover:border-slate-700 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-blue-400 font-mono">
                      STEP {item.step < 10 ? `0${item.step}` : item.step}
                    </span>
                    <span className="h-2 w-2 rounded-full bg-blue-500" />
                  </div>
                  <h4 className="text-xs font-bold text-white">{item.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed font-sans">{item.desc}</p>
                </div>

                <div className="pt-2 border-t border-slate-800/80">
                  <Link
                    href={item.link}
                    className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1"
                  >
                    Open Step Workspace <ExternalLink className="h-3 w-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
