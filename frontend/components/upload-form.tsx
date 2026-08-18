"use client";

import { useCallback, useRef, useState } from "react";
import { UploadCloud, FileText, RefreshCw, Cpu } from "lucide-react";
import { uploadDocumentStream, type StreamEvent } from "@/lib/api";
import { Card, ErrorBanner } from "@/components/ui";
import LiveTrace from "@/components/live-trace";
import ExtractionResult from "@/components/extraction-result";

const ACCEPT = ".pdf,.png,.jpg,.jpeg,.tiff,.bmp";

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [projectId, setProjectId] = useState("default");
  const [running, setRunning] = useState(false);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) setFile(f);
  }, []);

  async function handleUpload() {
    if (!file) return;
    setRunning(true);
    setResult(null);
    setError("");
    setEvents([]);

    try {
      await uploadDocumentStream(
        file,
        (event) => {
          if (event.type === "error") {
            setError(event.detail || "Processing failed");
            return;
          }
          if (event.type === "done") {
            setResult(event.result);
            return;
          }
          setEvents((prev) => [...prev, event]);
        },
        projectId
      );
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setRunning(false);
    }
  }

  const showTrace = running || events.length > 0 || result;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
      {/* Left: uploader + live trace */}
      <div className="space-y-6">
        <Card className="p-6">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition ${
              dragOver
                ? "border-brand bg-brand-soft"
                : "border-border-strong bg-surface-2 hover:border-brand hover:bg-brand-soft/40"
            }`}
          >
            <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-soft text-brand">
              {file ? <FileText size={22} /> : <UploadCloud size={22} />}
            </span>
            {file ? (
              <>
                <p className="text-sm font-semibold text-text">{file.name}</p>
                <p className="mt-1 text-xs text-text-muted">
                  {(file.size / 1024).toFixed(0)} KB · click to replace
                </p>
              </>
            ) : (
              <>
                <p className="text-sm font-semibold text-text">
                  Drop a document, or click to browse
                </p>
                <p className="mt-1 text-xs text-text-muted">
                  PDF or image (invoice, PO, delivery note, financial or site report)
                </p>
              </>
            )}
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPT}
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden"
            />
          </div>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <div className="flex-1">
              <label className="label-caps">Project namespace</label>
              <input
                type="text"
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                placeholder="default"
                className="input mt-1.5"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={handleUpload}
                disabled={!file || running}
                className="btn btn-primary h-[46px] w-full sm:w-auto"
              >
                {running ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" /> Processing…
                  </>
                ) : (
                  <>
                    <Cpu size={16} /> Run Agent Pipeline
                  </>
                )}
              </button>
            </div>
          </div>

          <ErrorBanner message={error} />
        </Card>

        {showTrace ? (
          <Card className="p-6">
            <LiveTrace events={events} running={running} />
          </Card>
        ) : (
          <Card className="p-6">
            <p className="label-caps mb-2">What happens when you run</p>
            <ol className="space-y-2 text-sm text-text-muted">
              {[
                "OCR / native parsing of the document",
                "A LangGraph agent decides each next step",
                "Schema-constrained LLM extraction with evidence",
                "Validation — and self-correction if it fails",
                "Vector indexing + KPI logging",
              ].map((t, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-brand">{i + 1}.</span> {t}
                </li>
              ))}
            </ol>
          </Card>
        )}
      </div>

      {/* Right: results */}
      <div className="space-y-6">
        {result ? (
          <div className="animate-fade-up">
            <ExtractionResult
              classification={result.classification}
              extraction={result.extraction}
              validation={result.validation}
            />
          </div>
        ) : (
          <Card className="flex h-full min-h-[300px] flex-col items-center justify-center p-8 text-center">
            <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-2 text-text-faint">
              <FileText size={26} />
            </span>
            <p className="text-sm font-medium text-text">Extraction results appear here</p>
            <p className="mt-1 max-w-xs text-sm text-text-muted">
              Grounded fields, evidence snippets, line items, and validation — as soon as the
              agent finishes.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
