"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Briefcase,
  TrendingUp,
  Sparkles,
  ArrowRight,
  Building2,
  DollarSign,
  Calendar,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function OpportunitiesPage() {
  const [opps, setOpps] = useState<any[]>([
    {
      id: "opp-nexa-copilot",
      company: "Nexa Logistics (Fictional Demo)",
      title: "AI Customer Service Copilot Enterprise Pilot",
      stage: "Solutioning",
      value: 185000,
      closeDate: "Q2 2026",
      aiPattern: "Multi-Agent Dispatch Copilot with TMS Webhook Sync",
    },
    {
      id: "opp-02",
      company: "Apex Global Cargo (Fictional)",
      title: "Consignee Exception Alert Automation",
      stage: "Discovery",
      value: 120000,
      closeDate: "Q3 2026",
      aiPattern: "Automated WhatsApp Notification Gateway",
    },
  ]);

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Commercial Opportunities & Deals"
        subtitle="Tracking customer deal pipelines and AI solution demo architectures"
      />

      <main className="flex-1 p-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {opps.map((opp) => (
            <div
              key={opp.id}
              className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    {opp.company}
                  </span>
                  <h3 className="text-sm font-bold text-white mt-0.5">{opp.title}</h3>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded font-bold uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  {opp.stage}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Value</span>
                  <p className="text-sm font-bold text-emerald-400 font-mono mt-0.5">
                    ${opp.value.toLocaleString()}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Target Close</span>
                  <p className="text-xs font-semibold text-slate-300 mt-0.5">{opp.closeDate}</p>
                </div>
              </div>

              <div className="text-xs text-slate-400">
                <strong>Solution Pattern: </strong> {opp.aiPattern}
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex justify-end">
                <Link
                  href="/demo-builder"
                  className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1"
                >
                  Inspect Architecture Blueprint <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
