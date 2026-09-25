"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Search, ArrowRight, UserCheck, ShieldAlert, Sparkles } from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function CustomersListPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.getCustomers(filterStatus || undefined, searchQuery || undefined);
      setCustomers(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterStatus]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Enterprise Accounts & Customers"
        subtitle="Manage complete 360 dossiers across prospects, active accounts, and customer lifecycles"
      />

      <main className="flex-1 p-8 space-y-6">
        {/* Search & Filters */}
        <div className="flex items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <form onSubmit={handleSearch} className="flex-1 max-w-md relative">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search companies by name or domain..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </form>

          <div className="flex items-center gap-3">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none"
            >
              <option value="">All Lifecycle Stages</option>
              <option value="prospect">Prospects</option>
              <option value="customer">Active Customers</option>
            </select>
          </div>
        </div>

        {/* Customer Account Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {customers.map((account) => (
            <div
              key={account.id}
              className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 space-y-4 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
                      <Building2 className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">{account.name}</h3>
                      <p className="text-xs text-slate-400">{account.domain || "Internal account"}</p>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                    account.status === "customer"
                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                      : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                  }`}>
                    {account.status}
                  </span>
                </div>

                <div className="pt-2 grid grid-cols-3 gap-2 border-t border-slate-800/80 text-center">
                  <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
                    <p className="text-[10px] text-slate-500 uppercase font-semibold">Contacts</p>
                    <p className="text-xs font-bold text-white mt-0.5">{account.contacts_count}</p>
                  </div>
                  <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
                    <p className="text-[10px] text-slate-500 uppercase font-semibold">Deals</p>
                    <p className="text-xs font-bold text-emerald-400 mt-0.5">{account.opportunities_count}</p>
                  </div>
                  <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
                    <p className="text-[10px] text-slate-500 uppercase font-semibold">Cases</p>
                    <p className="text-xs font-bold text-amber-400 mt-0.5">{account.open_cases_count}</p>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                <span className="text-[11px] text-slate-500 font-mono">
                  Tier: <span className="text-slate-300">{account.tier}</span>
                </span>
                <Link
                  href={`/customers/${account.id}`}
                  className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
                >
                  View Customer 360 <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
