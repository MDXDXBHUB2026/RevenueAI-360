"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Inbox,
  Mail,
  MessageSquare,
  MessageCircle,
  Share2,
  Send,
  Sparkles,
  AlertTriangle,
  ArrowRight,
  Filter,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function OmnichannelInboxPage() {
  const [filterChannel, setFilterChannel] = useState<string>("all");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inboundMessage, setInboundMessage] = useState("");
  const [inboundChannel, setInboundChannel] = useState("email");
  const [inboundSender, setInboundSender] = useState("marcus.vance@nexalogistics.com");
  const [inboundSubject, setInboundSubject] = useState("AI Customer Service Automation Inquiry");
  const [statusFeedback, setStatusFeedback] = useState<string | null>(null);

  // Sample normalized inbox feed
  const [feedItems, setFeedItems] = useState<any[]>([
    {
      id: "inb-01",
      channel: "email",
      sender: "marcus.vance@nexalogistics.com",
      company: "Nexa Logistics (Fictional Demo)",
      subject: "AI Customer Service Automation inquiry for Nexa Logistics",
      content: "We handle 12,000 shipments weekly. Repetitive carrier tracking inquiries are overwhelming our dispatch desks. Looking for an AI copilot solution.",
      timestamp: "10 mins ago",
      type: "lead",
      priority: "HIGH",
    },
    {
      id: "inb-02",
      channel: "whatsapp",
      sender: "+15550192834 (Marcus Vance)",
      company: "Nexa Logistics (Fictional Demo)",
      subject: "WhatsApp Inquiry",
      content: "Can the AI copilot send proactive exception alerts to consignees when carrier transit delays occur?",
      timestamp: "1 hour ago",
      type: "lead",
      priority: "MEDIUM",
    },
    {
      id: "inb-03",
      channel: "webchat",
      sender: "elena.rostova@nexalogistics.com",
      company: "Nexa Logistics (Fictional Demo)",
      subject: "Freight Tracking Status",
      content: "Can you provide updated ETA for shipment container MSCU-948192 from Chicago to Detroit?",
      timestamp: "3 hours ago",
      type: "support",
      priority: "MEDIUM",
    },
    {
      id: "inb-04",
      channel: "email",
      sender: "marcus.vance@nexalogistics.com",
      company: "Nexa Logistics (Fictional Demo)",
      subject: "URGENT: Issue reported multiple times without resolution",
      content: "I have complained about the GPS telemetry outage multiple times now and we have had zero updates! Our clients are furious. Why is this still not fixed?",
      timestamp: "Yesterday",
      type: "complaint",
      priority: "CRITICAL",
    },
  ]);

  const handleSimulateInbound = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inboundMessage) return;

    try {
      setIsSubmitting(true);
      const res = await api.ingestInboundEvent({
        channel: inboundChannel,
        external_identity: inboundSender,
        subject: inboundSubject,
        content: inboundMessage,
      });

      setStatusFeedback(`Event normalized & processed. Workflow ID: ${res.workflow_id.slice(0, 8)}`);

      // Add to local feed
      const newItem = {
        id: res.workflow_id,
        channel: inboundChannel,
        sender: inboundSender,
        company: "Nexa Logistics",
        subject: inboundSubject,
        content: inboundMessage,
        timestamp: "Just now",
        type: res.intent || "lead",
        priority: res.intent === "complaint" ? "CRITICAL" : "HIGH",
      };
      setFeedItems([newItem, ...feedItems]);
      setInboundMessage("");
    } catch (err: any) {
      setStatusFeedback(`Error: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredItems = feedItems.filter((item) => {
    if (filterChannel === "all") return true;
    return item.channel === filterChannel;
  });

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Omnichannel Ingestion Inbox"
        subtitle="Common gateway normalizing events across Email, WhatsApp, WebChat, and Slack into Customer 360"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Quick Simulator Bar */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-400" />
              Simulate Inbound Channel Message
            </h3>
            {statusFeedback && (
              <span className="text-xs text-emerald-400 font-mono">{statusFeedback}</span>
            )}
          </div>

          <form onSubmit={handleSimulateInbound} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Channel Gateway</label>
              <select
                value={inboundChannel}
                onChange={(e) => setInboundChannel(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none"
              >
                <option value="email">Email Gateway (SMTP/IMAP)</option>
                <option value="whatsapp">WhatsApp Business API</option>
                <option value="webchat">WebChat WebSocket</option>
                <option value="slack">Slack Internal Webhook</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">External Identity</label>
              <input
                type="text"
                value={inboundSender}
                onChange={(e) => setInboundSender(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none"
              />
            </div>

            <div className="md:col-span-2">
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Subject Header</label>
              <input
                type="text"
                value={inboundSubject}
                onChange={(e) => setInboundSubject(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none"
              />
            </div>

            <div className="md:col-span-3">
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Message Content Payload</label>
              <input
                type="text"
                value={inboundMessage}
                onChange={(e) => setInboundMessage(e.target.value)}
                placeholder="Enter customer message payload to normalize and trigger AI agents..."
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none"
              />
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={isSubmitting || !inboundMessage}
                className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                <Send className="h-3.5 w-3.5" />
                {isSubmitting ? "Ingesting..." : "Ingest & Orchestrate"}
              </button>
            </div>
          </form>
        </div>

        {/* Channel Filter Pills */}
        <div className="flex items-center gap-2">
          {["all", "email", "whatsapp", "webchat", "slack"].map((ch) => (
            <button
              key={ch}
              onClick={() => setFilterChannel(ch)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-medium uppercase tracking-wider transition-colors ${
                filterChannel === ch
                  ? "bg-blue-600 text-white border-blue-500 shadow-sm"
                  : "bg-slate-900 border-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {ch}
            </button>
          ))}
        </div>

        {/* Inbound Normalized Events Feed */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">Unified Inbound Stream</h3>

          <div className="space-y-3">
            {filteredItems.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-xl border border-slate-800 bg-slate-950/80 hover:border-slate-700 transition-colors space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                      item.channel === "whatsapp"
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : item.channel === "email"
                        ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                        : "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                    }`}>
                      {item.channel}
                    </span>
                    <span className="text-xs font-semibold text-white">{item.sender}</span>
                    <span className="text-xs text-slate-500">({item.company})</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                      item.priority === "CRITICAL"
                        ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                        : "bg-slate-800 text-slate-400"
                    }`}>
                      {item.priority}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">{item.timestamp}</span>
                  </div>
                </div>

                <div className="text-xs font-medium text-slate-200">{item.subject}</div>
                <p className="text-xs text-slate-400 font-sans leading-relaxed">{item.content}</p>

                <div className="pt-2 flex items-center justify-between border-t border-slate-800/80">
                  <span className="text-[11px] text-slate-500">
                    Intent Classified: <span className="uppercase text-blue-400 font-semibold">{item.type}</span>
                  </span>
                  <Link
                    href="/control-room"
                    className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
                  >
                    View Agent Trace <ArrowRight className="h-3 w-3" />
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
