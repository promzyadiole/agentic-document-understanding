"use client";

import { useState } from "react";
import { Search, Sparkles, FileText, Quote } from "lucide-react";
import { askQuestion } from "@/lib/api";
import { Card, ErrorBanner, Badge, SectionTitle, EmptyState } from "@/components/ui";

const SUGGESTIONS = [
  "What was the total revenue and net income?",
  "List the total assets and liabilities.",
  "What is the invoice total and due date?",
  "Summarize the key financial sections.",
];

/** Render inline [Source N] citations as small chips. */
function AnswerText({ text }: { text: string }) {
  const parts = text.split(/(\[Source \d+\])/g);
  return (
    <p className="whitespace-pre-wrap text-sm leading-7 text-text">
      {parts.map((part, i) =>
        /^\[Source \d+\]$/.test(part) ? (
          <span key={i} className="mx-0.5 inline-flex align-baseline">
            <Badge tone="brand">{part.replace(/[[\]]/g, "")}</Badge>
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </p>
  );
}

export default function QueryForm() {
  const [projectId, setProjectId] = useState("default");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function handleAsk(q?: string) {
    const query = (q ?? question).trim();
    if (!query) return;
    if (q) setQuestion(q);

    setLoading(true);
    setResult(null);
    setError("");
    try {
      const data = await askQuestion({ question: query, project_id: projectId, top_k: 5 });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Query failed");
    } finally {
      setLoading(false);
    }
  }

  const answer = result?.result?.answer;
  const sources = result?.result?.sources || [];
  const grounded = result?.result?.grounded;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
      <div className="space-y-4">
        <Card className="p-6">
          <SectionTitle title="Ask your documents" hint="Grounded retrieval over the indexed corpus — answers cite their sources." />
          <div className="space-y-3">
            <div>
              <label className="label-caps">Project namespace</label>
              <input
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                placeholder="default"
                className="input mt-1.5"
              />
            </div>
            <div>
              <label className="label-caps">Question</label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleAsk();
                }}
                placeholder="What does the report say about revenue, liabilities, or operating income?"
                className="input mt-1.5 min-h-[130px] resize-y"
              />
            </div>
            <button onClick={() => handleAsk()} disabled={!question.trim() || loading} className="btn btn-primary w-full">
              <Search size={16} /> {loading ? "Searching…" : "Ask"}
            </button>
          </div>
          <ErrorBanner message={error} />
        </Card>

        <Card className="p-5">
          <p className="label-caps mb-2.5">Try asking</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => handleAsk(s)}
                disabled={loading}
                className="rounded-lg border border-border bg-surface-2 px-3 py-1.5 text-left text-xs text-text-muted transition hover:border-brand hover:text-text"
              >
                {s}
              </button>
            ))}
          </div>
        </Card>
      </div>

      <div className="space-y-4">
        {answer ? (
          <Card className="animate-fade-up p-6">
            <div className="mb-3 flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand text-white">
                <Sparkles size={14} />
              </span>
              <p className="text-sm font-semibold text-text">Answer</p>
              {grounded === false ? <Badge tone="warn">ungrounded</Badge> : <Badge tone="ok">grounded</Badge>}
            </div>
            <AnswerText text={answer} />
          </Card>
        ) : (
          <Card className="flex h-full min-h-[280px] flex-col items-center justify-center p-8 text-center">
            <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-2 text-text-faint">
              <Sparkles size={26} />
            </span>
            <p className="text-sm font-medium text-text">Grounded answers appear here</p>
            <p className="mt-1 max-w-xs text-sm text-text-muted">
              Ask a question and the system retrieves relevant chunks, then answers with inline citations.
            </p>
          </Card>
        )}

        {sources.length > 0 ? (
          <Card className="animate-fade-up p-6">
            <SectionTitle title={`Sources (${sources.length})`} hint="Chunks retrieved to ground the answer." />
            <div className="space-y-3">
              {sources.map((source: any, idx: number) => (
                <div key={idx} className="rounded-xl border border-border bg-surface-2 p-3.5">
                  <div className="flex items-center gap-2">
                    <Badge tone="brand">Source {idx + 1}</Badge>
                    <span className="flex items-center gap-1 text-xs text-text-muted">
                      <FileText size={12} /> {source.filename || source.document_id}
                      {source.page ? ` · p.${source.page}` : ""}
                    </span>
                  </div>
                  <p className="mt-2 flex gap-1.5 text-xs leading-relaxed text-text-muted">
                    <Quote size={12} className="mt-0.5 shrink-0 text-text-faint" />
                    {source.excerpt}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
