"use client";

import { useEffect, useState } from "react";
import {
  BookOpen,
  Plus,
  Search,
  CheckCircle2,
  FileText,
  UploadCloud,
  Sparkles,
  Layers,
} from "lucide-react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function KnowledgeBasePage() {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newDocType, setNewDocType] = useState("policy");
  const [ingesting, setIngesting] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const loadDocs = async () => {
    try {
      setLoading(true);
      const data = await api.getKnowledgeDocs();
      setDocs(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newContent) return;
    try {
      setIngesting(true);
      const res = await api.ingestKnowledgeDoc({
        title: newTitle,
        content: newContent,
        doc_type: newDocType,
      });
      setFeedback(`Document '${res.title}' indexed into ${res.chunk_count} vector chunks.`);
      setNewTitle("");
      setNewContent("");
      await loadDocs();
    } catch (e: any) {
      setFeedback(`Error: ${e.message}`);
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Enterprise Knowledge Base & RAG Index"
        subtitle="Semantic vector retrieval layer over corporate policies, product specifications, and SLA guidelines using pgvector"
      />

      <main className="flex-1 p-8 space-y-6">
        {feedback && (
          <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300">
            {feedback}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Indexed Enterprise Documents */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between pb-1">
              <h3 className="text-sm font-semibold text-white">Indexed Documents ({docs.length})</h3>
              <span className="text-[10px] font-mono text-emerald-400 font-semibold uppercase">
                Vector Index: Active (1536-dim)
              </span>
            </div>

            <div className="space-y-3">
              {docs.map((doc) => (
                <div
                  key={doc.id}
                  className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 space-y-2 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white flex items-center gap-2">
                      <FileText className="h-4 w-4 text-blue-400" />
                      {doc.title}
                    </span>
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                      {doc.doc_type}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-1 border-t border-slate-800/80">
                    <span>{doc.chunk_count} Semantic Chunks</span>
                    <span>Status: Active Grounding</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Ingest & Index New Document */}
          <div className="lg:col-span-5 rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <UploadCloud className="h-4 w-4 text-blue-400" />
              Ingest & Index Document
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload raw Markdown, policy rules, or product capabilities. The system chunks the text,
              generates embeddings, and registers it into the RAG vector store for agent citation.
            </p>

            <form onSubmit={handleIngest} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Document Title</label>
                <input
                  type="text"
                  placeholder="e.g. 2026 Fleet Exception Rerouting Policy"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Document Type</label>
                <select
                  value={newDocType}
                  onChange={(e) => setNewDocType(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none"
                >
                  <option value="policy">Policy & SLA</option>
                  <option value="product_catalogue">Product Catalogue</option>
                  <option value="case_study">Case Study & ROI</option>
                  <option value="architecture">Technical Architecture</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Content Text (Markdown/TXT)</label>
                <textarea
                  rows={6}
                  placeholder="Paste raw corporate text or policy directives here..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={ingesting || !newTitle || !newContent}
                className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Plus className="h-4 w-4" />
                {ingesting ? "Embedding Chunks..." : "Chunk, Embed & Index"}
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
