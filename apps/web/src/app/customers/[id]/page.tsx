"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  Building2,
  Mail,
  Phone,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Send,
  MessageSquare,
  Clock,
  UserCheck,
  TrendingUp,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function Customer360DetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const accountId = resolvedParams.id;

  const [c360, setC360] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [converting, setConverting] = useState(false);
  const [activeTab, setActiveTab] = useState<"timeline" | "cases" | "complaints" | "actions">("timeline");

  const loadData = async () => {
    try {
      const data = await api.getCustomer360(accountId);
      setC360(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [accountId]);

  const handleConvert = async () => {
    try {
      setConverting(true);
      await api.convertToCustomer(accountId);
      await loadData();
    } finally {
      setConverting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <Header title="Customer 360" />
        <div className="flex-1 flex items-center justify-center text-xs text-slate-500">
          Loading Customer 360 dossier...
        </div>
      </div>
    );
  }

  if (!c360) {
    return (
      <div className="flex-1 flex flex-col">
        <Header title="Customer 360" />
        <div className="p-8 text-center text-xs text-slate-500">
          Customer account not found. Return to <Link href="/customers" className="text-blue-400 underline">Customers list</Link>.
        </div>
      </div>
    );
  }

  const { account, contacts, recent_interactions, open_support_cases, complaints, next_best_action, active_opportunities, lead_summary } = c360;

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title={`Customer 360: ${account.name}`}
        subtitle={`Continuous cross-channel relationship dossier • Domain: ${account.domain || "N/A"}`}
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Top Account Header Card */}
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-md">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold text-xl">
              <Building2 className="h-7 w-7" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <h2 className="text-lg font-bold text-white">{account.name}</h2>
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                  account.status === "customer"
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                    : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                }`}>
                  {account.status}
                </span>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {account.tier} Tier
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Industry: <span className="text-slate-200">{account.industry || "Logistics"}</span> • Sentiment Index:{" "}
                <span className={account.sentiment_score >= 0 ? "text-emerald-400" : "text-rose-400"}>
                  {account.sentiment_score > 0 ? `+${account.sentiment_score}` : account.sentiment_score}
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {account.status === "prospect" && (
              <button
                onClick={handleConvert}
                disabled={converting}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition-colors"
              >
                {converting ? "Updating..." : "Convert to Active Customer"}
              </button>
            )}
            <Link
              href={`/demo-builder?account=${accountId}`}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md flex items-center gap-1.5 transition-colors"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Build AI Solution Demo
            </Link>
          </div>
        </div>

        {/* Section 10: Next-Best-Action Engine Directive */}
        {next_best_action && (
          <div className={`p-5 rounded-xl border flex items-start justify-between gap-4 shadow-sm ${
            next_best_action.priority === "CRITICAL"
              ? "bg-rose-950/20 border-rose-500/40"
              : "bg-blue-950/20 border-blue-500/40"
          }`}>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                  next_best_action.priority === "CRITICAL"
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                    : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                }`}>
                  Next Best Action • {next_best_action.priority}
                </span>
                <span className="text-xs font-mono font-semibold text-white">
                  {next_best_action.action_type}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
                {next_best_action.explainable_reason}
              </p>
            </div>
            {next_best_action.suppress_promotions && (
              <span className="px-2.5 py-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-bold uppercase tracking-wider shrink-0">
                Promotions Suppressed
              </span>
            )}
          </div>
        )}

        {/* Two-Column Dossier Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Stakeholders & Channel Identities */}
          <div className="lg:col-span-4 space-y-6">
            {/* Verified Stakeholders */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Key Account Stakeholders
              </h3>
              <div className="space-y-3">
                {contacts.length === 0 ? (
                  <p className="text-xs text-slate-500">No contacts linked yet.</p>
                ) : (
                  contacts.map((contact: any) => (
                    <div key={contact.id} className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-white">{contact.name}</span>
                        <span className="text-[10px] text-blue-400 font-medium">{contact.role || "Stakeholder"}</span>
                      </div>
                      <p className="text-[11px] text-slate-400">{contact.title || "Operations Lead"}</p>
                      <div className="pt-1 flex flex-col gap-1 text-[11px] text-slate-500 font-mono">
                        {contact.email && <span className="flex items-center gap-1.5"><Mail className="h-3 w-3" /> {contact.email}</span>}
                        {contact.phone && <span className="flex items-center gap-1.5"><Phone className="h-3 w-3" /> {contact.phone}</span>}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Opportunities */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Active Opportunities
              </h3>
              <div className="space-y-2.5">
                {active_opportunities.length === 0 ? (
                  <p className="text-xs text-slate-500">No active commercial deals.</p>
                ) : (
                  active_opportunities.map((opp: any) => (
                    <div key={opp.id} className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-white">{opp.title}</span>
                        <span className="text-[11px] font-mono text-emerald-400 font-bold">
                          ${opp.estimated_value.toLocaleString()}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">Stage: <span className="text-blue-400 font-medium">{opp.stage}</span></p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right Column: Unified Chronological Cross-Channel Timeline */}
          <div className="lg:col-span-8 rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-white">Unified Omnichannel Timeline</h3>
                <p className="text-xs text-slate-400">Continuous context preserved across Email, WhatsApp, WebChat, and Slack</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 font-mono">
                  {recent_interactions.length} Interactions Recorded
                </span>
              </div>
            </div>

            {/* Timeline Stream */}
            <div className="space-y-4">
              {recent_interactions.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-500">
                  No interactions recorded yet. Ingest messages via Omnichannel Inbox to populate timeline.
                </div>
              ) : (
                recent_interactions.map((item: any, idx: number) => {
                  const isComplaint = item.sentiment === "urgent" || item.sentiment === "negative";
                  return (
                    <div key={item.id || idx} className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 space-y-2 hover:border-slate-700 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                            item.channel === "whatsapp"
                              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                              : item.channel === "email"
                              ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                              : item.channel === "slack"
                              ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                              : "bg-slate-800 text-slate-300 border border-slate-700"
                          }`}>
                            {item.channel}
                          </span>
                          <span className="text-xs font-semibold text-white">
                            {item.subject || "Direct Message"}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {item.timestamp ? new Date(item.timestamp).toLocaleDateString() : "Recent"}
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed font-sans">
                        {item.content}
                      </p>

                      <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500 font-mono">
                        <span className="uppercase text-[10px]">Direction: {item.direction}</span>
                        <span className={`text-[10px] font-bold uppercase ${isComplaint ? "text-rose-400" : "text-slate-400"}`}>
                          Sentiment: {item.sentiment}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
