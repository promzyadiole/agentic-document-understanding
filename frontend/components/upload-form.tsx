"use client";

import { useState } from "react";
import { uploadDocument } from "@/lib/api";

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h4 className="text-base font-semibold text-gray-900">{title}</h4>
      <div className="mt-3">{children}</div>
    </div>
  );
}

function StatusBadge({
  label,
  tone = "gray",
}: {
  label: string;
  tone?: "green" | "yellow" | "red" | "blue" | "gray";
}) {
  const styles = {
    green: "bg-green-100 text-green-800",
    yellow: "bg-yellow-100 text-yellow-800",
    red: "bg-red-100 text-red-800",
    blue: "bg-blue-100 text-blue-800",
    gray: "bg-gray-100 text-gray-700",
  };

  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${styles[tone]}`}>
      {label}
    </span>
  );
}

function toneForValidation(status?: string) {
  if (status === "pass") return "green";
  if (status === "warning") return "yellow";
  if (status === "fail") return "red";
  return "gray";
}

function toneForDocType(type?: string) {
  if (type === "financial_report") return "blue";
  if (type === "invoice" || type === "purchase_order" || type === "delivery_note") return "green";
  if (type === "unknown") return "gray";
  return "blue";
}

function toneForConfidence(level?: string) {
  if (level === "high") return "green";
  if (level === "medium") return "yellow";
  return "red";
}

function ExtractedFieldsCard({ extraction }: { extraction: any }) {
  const fields = extraction?.fields || {};
  const entries = Object.entries(fields);

  return (
    <SectionCard title="Extracted Fields">
      {entries.length === 0 ? (
        <p className="text-sm text-gray-600">No structured fields were extracted.</p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {entries.map(([key, value]: [string, any]) => (
            <div key={key} className="rounded-2xl bg-gray-50 p-4">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-medium text-gray-900">{key}</p>
                <StatusBadge
                  label={value?.confidence_level || "unknown"}
                  tone={toneForConfidence(value?.confidence_level)}
                />
              </div>

              <p className="mt-2 break-words text-sm text-gray-700">
                <span className="font-medium">Value:</span>{" "}
                {value?.value !== null && value?.value !== undefined && String(value?.value).trim() !== ""
                  ? String(value.value)
                  : "-"}
              </p>

              <p className="mt-1 text-sm text-gray-600">
                <span className="font-medium">Normalized:</span>{" "}
                {value?.normalized_value !== null && value?.normalized_value !== undefined
                  ? String(value.normalized_value)
                  : "-"}
              </p>

              <p className="mt-1 text-sm text-gray-600">
                <span className="font-medium">Confidence:</span> {value?.confidence_score ?? "-"}
              </p>
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  );
}

function ValidationIssuesCard({ validation }: { validation: any }) {
  const issues = validation?.issues || [];

  return (
    <SectionCard title="Validation Issues">
      {issues.length === 0 ? (
        <p className="text-sm text-gray-600">No validation issues found.</p>
      ) : (
        <div className="space-y-3">
          {issues.map((issue: any, idx: number) => (
            <div key={idx} className="rounded-2xl bg-gray-50 p-4">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-medium text-gray-900">{issue.field_name}</p>
                <StatusBadge label={issue.status} tone={toneForValidation(issue.status)} />
              </div>
              <p className="mt-2 text-sm text-gray-700">{issue.message}</p>
              {(issue.expected_value !== null && issue.expected_value !== undefined) ||
              (issue.actual_value !== null && issue.actual_value !== undefined) ? (
                <div className="mt-2 text-xs text-gray-600">
                  <p>Expected: {String(issue.expected_value ?? "-")}</p>
                  <p>Actual: {String(issue.actual_value ?? "-")}</p>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  );
}

function AgentTraceCard({ trace }: { trace: any }) {
  const steps = trace?.steps_taken || [];
  const history = trace?.history || [];

  return (
    <SectionCard title="Agent Trace">
      <div className="space-y-4 text-sm text-gray-700">
        <p>
          <span className="font-medium">Final action:</span> {trace?.agent_action || "-"}
        </p>
        <p>
          <span className="font-medium">Loop count:</span> {trace?.loop_count ?? "-"}
        </p>
        <p>
          <span className="font-medium">Final reasoning:</span> {trace?.agent_reasoning || "-"}
        </p>

        <div className="pt-2">
          <p className="font-medium text-gray-900">Step history</p>
          {steps.length === 0 ? (
            <p className="mt-2 text-sm text-gray-600">No steps recorded.</p>
          ) : (
            <div className="mt-3 flex flex-wrap gap-2">
              {steps.map((step: string, idx: number) => (
                <span
                  key={`${step}-${idx}`}
                  className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700"
                >
                  {idx + 1}. {step}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="pt-2">
          <p className="font-medium text-gray-900">Reasoning timeline</p>
          {history.length === 0 ? (
            <p className="mt-2 text-sm text-gray-600">No reasoning history available.</p>
          ) : (
            <div className="mt-3 space-y-3">
              {history.map((item: any, idx: number) => (
                <div key={idx} className="rounded-2xl bg-gray-50 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-black px-3 py-1 text-xs text-white">
                      Loop {item.loop_count ?? idx + 1}
                    </span>
                    <span className="rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-800">
                      {item.action || "unknown"}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-gray-700">
                    {item.reasoning || "-"}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </SectionCard>
  );
}

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [projectId, setProjectId] = useState("default");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function handleUpload() {
    if (!file) return;

    setLoading(true);
    setResult(null);
    setError("");

    try {
      const data = await uploadDocument(file, projectId);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  const parsed = result?.parsed_document;
  const classification = result?.classification;
  const extraction = result?.extraction;
  const validation = result?.validation;
  const agentTrace = result?.agent_trace;

  return (
    <div className="space-y-6">
      <div className="space-y-5 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Upload document</h3>
          <p className="mt-1 text-sm text-gray-600">
            Run parsing, classification, extraction, validation, indexing, KPI logging, and agent reasoning.
          </p>
        </div>

        <input
          type="text"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          placeholder="Project namespace"
          className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-black"
        />

        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-black"
        />

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="rounded-xl bg-black px-5 py-3 text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Processing..." : "Upload & Process"}
        </button>

        {error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        ) : null}
      </div>

      {result ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <SectionCard title="Document Metadata">
            <div className="space-y-2 text-sm text-gray-700">
              <p><span className="font-medium">Filename:</span> {parsed?.metadata?.filename}</p>
              <p><span className="font-medium">Document ID:</span> {parsed?.metadata?.document_id}</p>
              <p><span className="font-medium">File size:</span> {parsed?.metadata?.file_size}</p>
              <p><span className="font-medium">Pages:</span> {parsed?.metadata?.page_count}</p>
              <p><span className="font-medium">Method:</span> {parsed?.extraction_method}</p>
              <p><span className="font-medium">Language:</span> {parsed?.detected_language || "-"}</p>
            </div>
          </SectionCard>

          <SectionCard title="Classification">
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-center gap-3">
                <span className="font-medium">Type:</span>
                <StatusBadge
                  label={classification?.document_type || "unknown"}
                  tone={toneForDocType(classification?.document_type)}
                />
              </div>
              <p><span className="font-medium">Confidence:</span> {classification?.confidence_score ?? "-"}</p>
              <p><span className="font-medium">Reasoning:</span> {classification?.reasoning || "-"}</p>
            </div>
          </SectionCard>

          <SectionCard title="Validation">
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-center gap-3">
                <span className="font-medium">Status:</span>
                <StatusBadge
                  label={validation?.overall_status || "-"}
                  tone={toneForValidation(validation?.overall_status)}
                />
              </div>
              <p><span className="font-medium">Score:</span> {validation?.score ?? "-"}</p>
              <p><span className="font-medium">Issue count:</span> {validation?.issues?.length ?? 0}</p>
            </div>
          </SectionCard>

          <AgentTraceCard trace={agentTrace} />

          <SectionCard title="Extraction Notes">
            <div className="space-y-2 text-sm text-gray-700">
              {Array.isArray(extraction?.extraction_notes) && extraction.extraction_notes.length > 0 ? (
                extraction.extraction_notes.map((note: string, idx: number) => (
                  <div key={idx} className="rounded-xl bg-gray-50 p-3">
                    {note}
                  </div>
                ))
              ) : (
                <p>No notes available.</p>
              )}
            </div>
          </SectionCard>

          <div className="lg:col-span-2">
            <ExtractedFieldsCard extraction={extraction} />
          </div>

          <div className="lg:col-span-2">
            <ValidationIssuesCard validation={validation} />
          </div>

          <div className="lg:col-span-2">
            <SectionCard title="Raw Processed Response">
              <pre className="max-h-[500px] overflow-auto rounded-2xl bg-gray-950 p-4 text-xs text-green-300">
                {JSON.stringify(result, null, 2)}
              </pre>
            </SectionCard>
          </div>
        </div>
      ) : null}
    </div>
  );
}