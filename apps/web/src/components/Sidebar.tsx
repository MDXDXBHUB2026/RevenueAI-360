"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Inbox,
  Target,
  Users,
  Briefcase,
  Headphones,
  Cpu,
  CheckCircle2,
  Sparkles,
  BookOpen,
  BarChart3,
  Settings,
  ShieldAlert,
} from "lucide-react";

const navigation = [
  { name: "Executive Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Omnichannel Inbox", href: "/inbox", icon: Inbox },
  { name: "Lead Intelligence", href: "/leads", icon: Target },
  { name: "Customers & 360", href: "/customers", icon: Users },
  { name: "Opportunities", href: "/opportunities", icon: Briefcase },
  { name: "Support & Grievances", href: "/support", icon: Headphones },
  { name: "AI Control Room", href: "/control-room", icon: Cpu, badge: "Live" },
  { name: "Approval Centre", href: "/approvals", icon: CheckCircle2, badge: "HITL" },
  { name: "Customer AI Demo Builder", href: "/demo-builder", icon: Sparkles },
  { name: "Knowledge Base (RAG)", href: "/knowledge", icon: BookOpen },
  { name: "Evaluation & Quality", href: "/evaluations", icon: BarChart3 },
  { name: "Demo Mode & Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col h-screen fixed left-0 top-0 z-40">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="h-9 w-9 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold text-lg shadow-sm">
          360
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight text-white flex items-center gap-1.5">
            RevenueAI <span className="text-blue-500 font-bold">360</span>
          </h1>
          <p className="text-[10px] text-slate-400 tracking-wider font-medium uppercase">
            Customer Lifecycle AI
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
          Platform Workspace
        </div>
        {navigation.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center justify-between px-3 py-2 text-xs font-medium rounded-md transition-all ${
                isActive
                  ? "bg-blue-600/15 text-blue-400 border border-blue-500/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`h-4 w-4 ${isActive ? "text-blue-400" : "text-slate-400"}`} />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>

      {/* Demo Entity Footnote */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/30">
        <div className="p-2.5 rounded-lg border border-slate-800 bg-slate-950/60 flex items-start gap-2">
          <ShieldAlert className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-[11px] font-semibold text-slate-200">Nexa Logistics Active</p>
            <p className="text-[10px] text-slate-400">Primary Demo Entity (Fictional)</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
