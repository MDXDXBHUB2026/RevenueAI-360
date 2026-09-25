"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Headphones,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Send,
  Building2,
  FileText,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function SupportWorkspacePage() {
  const [submittingComplaint, setSubmittingComplaint] = useState(false);
  const [submittingSupport, setSubmittingSupport] = useState(false);
  const [complaintText, setComplaintText] = useState(
    "I have reported this tracking latency multiple times now and we are missing carrier delivery deadlines! Why has this not been resolved?"
  );
  const [supportText, setSupportText] = useState(
    "Can you provide updated ETA for shipment container MSCU-948192 from Chicago to Detroit?"
  );
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleInjectComplaint = async () => {
    try {
      setSubmittingComplaint(true);
      const res = await api.submitComplaint("acc-nexa-logistics-demo", {
        complaint_text: complaintText,
        channel: "email",
      });
      setFeedback(`Repeat complaint processed & escalated to Engineering. Workflow ID: ${res.workflow_id?.slice(0, 8)}`);
    } catch (e: any) {
      setFeedback(`Error: ${e.message}`);
    } finally {
      setSubmittingComplaint(false);
    }
  };

  const handleInjectSupport = async () => {
    try {
      setSubmittingSupport(true);
      const res = await api.submitSupport("acc-nexa-logistics-demo", {
        subject: "Freight Tracking Status",
        description: supportText,
        channel: "webchat",
      });
      setFeedback(`Support inquiry resolved via RAG. Workflow ID: ${res.workflow_id?.slice(0, 8)}`);
    } catch (e: any) {
      setFeedback(`Error: ${e.message}`);
    } finally {
      setSubmittingSupport(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Support & Grievances Workspace"
        subtitle="Operational issue triage, repeat complaint detection, SLA breach evaluation, and automated engineering escalation"
      />

      <main className="flex-1 p-8 space-y-6">
        {feedback && (
          <div className="p-4 rounded-xl bg-blue-950/40 border border-blue-500/40 text-xs text-blue-200 flex items-center justify-between">
            <span>{feedback}</span>
            <Link href="/control-room" className="underline font-semibold flex items-center gap-1">
              View in Control Room <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Panel 1: Repeat Complaint & Escalation Simulator (Demo Steps 9 & 10) */}
          <div className="rounded-xl border border-rose-500/30 bg-slate-900/40 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] uppercase font-bold text-rose-400 tracking-wider">
                  Portfolio Demo Step 9 & 10
                </span>
                <h3 className="text-sm font-semibold text-white flex items-center gap-2 mt-0.5">
                  <AlertTriangle className="h-4 w-4 text-rose-400" />
                  Repeat Complaint & Escalation Workflow
                </h3>
              </div>
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                SLA Breach
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Inject a chronic customer grievance stating the issue has been reported multiple times. Observe
              how the Complaint Resolution Agent reconstructs ticket history, evaluates urgency, bypasses routine triage,
              and immediately triggers an internal incident briefing to Engineering.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-slate-400">Customer Complaint Payload</label>
              <textarea
                rows={4}
                value={complaintText}
                onChange={(e) => setComplaintText(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none font-sans"
              />
            </div>

            <button
              onClick={handleInjectComplaint}
              disabled={submittingComplaint}
              className="w-full py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Send className="h-3.5 w-3.5" />
              {submittingComplaint ? "Escalating Incident..." : "Trigger Repeat Complaint Workflow"}
            </button>
          </div>

          {/* Panel 2: Operational Support Query & RAG Resolution */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] uppercase font-bold text-blue-400 tracking-wider">
                  Operational Inquiry (Step 8)
                </span>
                <h3 className="text-sm font-semibold text-white flex items-center gap-2 mt-0.5">
                  <Headphones className="h-4 w-4 text-blue-400" />
                  Routine Customer Support Workflow
                </h3>
              </div>
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                RAG Grounded
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Submit a standard inquiry regarding container status or transit milestones. The Customer Service
              Agent consults enterprise knowledge, validates carrier telemetry, and delivers grounded guidance.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-slate-400">Inbound Support Question</label>
              <textarea
                rows={4}
                value={supportText}
                onChange={(e) => setSupportText(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none font-sans"
              />
            </div>

            <button
              onClick={handleInjectSupport}
              disabled={submittingSupport}
              className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Send className="h-3.5 w-3.5" />
              {submittingSupport ? "Resolving with Copilot..." : "Trigger Support Resolution"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
