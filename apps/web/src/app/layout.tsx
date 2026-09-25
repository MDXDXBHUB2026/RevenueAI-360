import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "RevenueAI 360 | AI-Native Multi-Agent Customer Lifecycle Intelligence",
  description: "Enterprise Omnichannel CRM & Multi-Agent Lifecycle Intelligence Platform powered by LangGraph, pgvector, and Human-in-the-Loop Governance.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 flex antialiased">
        <Sidebar />
        <div className="flex-1 ml-64 flex flex-col min-h-screen overflow-x-hidden">
          {children}
        </div>
      </body>
    </html>
  );
}
