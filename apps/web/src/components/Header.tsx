"use client";

import { useState } from "react";
import { Sparkles, RefreshCw, Radio, CheckCircle, Bell } from "lucide-react";
import { api } from "@/lib/api";

export function Header({ title, subtitle }: { title?: string; subtitle?: string }) {
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleResetDemo = async () => {
    try {
      setResetting(true);
      await api.resetDemoData();
      setMessage("Demo data restored for Nexa Logistics.");
      setTimeout(() => {
        setMessage(null);
        window.location.reload();
      }, 1000);
    } catch (e: any) {
      setMessage(`Reset error: ${e.message}`);
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setResetting(false);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/70 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-30">
      <div>
        <h2 className="text-base font-semibold text-white tracking-tight">
          {title || "Overview"}
        </h2>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Status notification */}
        {message && (
          <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5 animate-fadeIn">
            <CheckCircle className="h-3.5 w-3.5" />
            {message}
          </span>
        )}

        {/* Live LangGraph Engine indicator */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-slate-800 bg-slate-900/80 text-xs text-slate-300">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-mono text-[11px] text-slate-300">LangGraph Active</span>
        </div>

        {/* Reset Demo button */}
        <button
          onClick={handleResetDemo}
          disabled={resetting}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-700 bg-slate-900 hover:bg-slate-800 text-xs text-slate-300 font-medium transition-colors"
          title="Reset Nexa Logistics state to default demonstration dataset"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${resetting ? "animate-spin text-blue-400" : ""}`} />
          Reset Demo State
        </button>
      </div>
    </header>
  );
}
