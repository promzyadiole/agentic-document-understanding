"use client";

import { useState } from "react";
import { askQuestion } from "@/lib/api";

export default function QueryForm() {
  const [projectId, setProjectId] = useState("default");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function handleAsk() {
    if (!question.trim()) return;

    setLoading(true);
    setResult(null);
    setError("");

    try {
      const data = await askQuestion({
        question,
        project_id: projectId,
        top_k: 5,
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Query failed");
    } finally {
      setLoading(false);
    }
  }

  const answer = result?.result?.answer;
  const sources = result?.result?.sources || [];

  return (
    <div className="space-y-6">
      <div className="space-y-5 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Ask your documents</h3>
          <p className="mt-1 text-sm text-gray-600">
            Query the indexed corpus with grounded retrieval and source excerpts.
          </p>
        </div>

        <input
          type="text"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          placeholder="Project namespace"
          className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-black"
        />

        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What does the report say about revenue, liabilities, or operating income?"
          className="min-h-[160px] w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-black"
        />

        <button
          onClick={handleAsk}
          disabled={!question.trim() || loading}
          className="rounded-xl bg-black px-5 py-3 text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Querying..." : "Ask"}
        </button>

        {error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        ) : null}
      </div>

      {answer ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h4 className="text-lg font-semibold text-gray-900">Answer</h4>
          <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-gray-700">
            {answer}
          </p>
        </div>
      ) : null}

      {sources.length > 0 ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h4 className="text-lg font-semibold text-gray-900">Sources</h4>
          <div className="mt-4 space-y-4">
            {sources.map((source: any, idx: number) => (
              <div key={idx} className="rounded-2xl bg-gray-50 p-4">
                <div className="text-sm text-gray-800">
                  <span className="font-medium">Document:</span> {source.document_id}
                  {source.page ? <> · <span className="font-medium">Page:</span> {source.page}</> : null}
                </div>
                <p className="mt-2 text-sm leading-6 text-gray-600">{source.excerpt}</p>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {result ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h4 className="text-lg font-semibold text-gray-900">Raw Response</h4>
          <pre className="mt-4 max-h-[400px] overflow-auto rounded-2xl bg-gray-950 p-4 text-xs text-green-300">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      ) : null}
    </div>
  );
}