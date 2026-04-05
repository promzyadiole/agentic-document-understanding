"use client";

import { useEffect, useState } from "react";
import Topbar from "@/components/topbar";
import AgentTracePanel from "@/components/agent-trace-panel";
import { exportGraph, getLatestDocument } from "@/lib/api";

export default function GraphPage() {
  const [graphData, setGraphData] = useState<any>(null);
  const [latestDocument, setLatestDocument] = useState<any>(null);
  const [trace, setTrace] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const graph = await exportGraph();
        setGraphData(graph);
      } catch (err: any) {
        setError(err.message || "Failed to export graph");
      }

      try {
        const latest = await getLatestDocument();
        const doc = latest?.document;
        setLatestDocument(doc);
        setTrace(doc?.agent_trace || null);
      } catch {
        // keep page usable even if latest document lookup fails
      }
    }

    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <Topbar
        title="Workflow Graph"
        subtitle="Exported LangGraph agent loop showing reasoning, tool routing, validation, and stopping behavior."
      />

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1.35fr_0.9fr]">
        <div className="space-y-6">
          {graphData?.image_url ? (
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900">Rendered Workflow</h3>
              <p className="mt-2 text-sm text-gray-600">
                This graph shows the LangGraph execution flow for intake, reasoning,
                tool selection, extraction, validation, indexing, and KPI logging.
              </p>

              <div className="mt-5 overflow-auto rounded-2xl border border-gray-200 bg-gray-50 p-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={graphData.image_url}
                  alt="Workflow graph"
                  className="mx-auto w-full max-w-5xl rounded-xl border border-gray-200 bg-white"
                />
              </div>
            </div>
          ) : null}

          {graphData ? (
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900">Graph Export Metadata</h3>
              <pre className="mt-4 overflow-auto rounded-2xl bg-gray-950 p-4 text-xs text-green-300">
                {JSON.stringify(graphData, null, 2)}
              </pre>
            </div>
          ) : null}
        </div>

        <div className="space-y-6">
          {latestDocument ? (
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900">Latest Processed Document</h3>
              <div className="mt-4 space-y-2 text-sm text-gray-700">
                <p><span className="font-medium">Filename:</span> {latestDocument.filename}</p>
                <p><span className="font-medium">Document ID:</span> {latestDocument.document_id}</p>
                <p><span className="font-medium">Type:</span> {latestDocument.document_type}</p>
                <p><span className="font-medium">Validation:</span> {latestDocument.validation_status || "-"}</p>
                <p><span className="font-medium">Pages:</span> {latestDocument.page_count ?? "-"}</p>
              </div>
            </div>
          ) : null}

          <AgentTracePanel trace={trace} />
        </div>
      </div>
    </div>
  );
}