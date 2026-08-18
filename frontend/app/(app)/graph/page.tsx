"use client";

import { useEffect, useState } from "react";
import { FileText, GitBranch } from "lucide-react";
import Topbar from "@/components/topbar";
import AgentTracePanel from "@/components/agent-trace-panel";
import WorkflowDiagram from "@/components/workflow-diagram";
import { Card, SectionTitle, Badge, StatusBadge, ErrorBanner } from "@/components/ui";
import { getLatestDocument } from "@/lib/api";

export default function GraphPage() {
  const [latestDocument, setLatestDocument] = useState<any>(null);
  const [trace, setTrace] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getLatestDocument()
      .then((latest) => {
        const doc = latest?.document;
        setLatestDocument(doc);
        setTrace(doc?.agent_trace || null);
      })
      .catch((err) => setError(err.message || "Failed to load latest run"));
  }, []);

  const steps: string[] = trace?.steps_taken || [];

  return (
    <div>
      <Topbar
        eyebrow="Explainability"
        title="Workflow Graph"
        subtitle="The live LangGraph topology. The agent_reason hub routes to each tool and loops back until it decides to finish."
      />

      <ErrorBanner message={error} />

      <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <div className="space-y-6">
          <Card className="p-6">
            <SectionTitle
              title="Agent workflow"
              hint="Interactive — hover any node. Highlighted nodes were visited by the latest run."
              right={<Badge tone="brand"><GitBranch size={12} /> LangGraph</Badge>}
            />
            <WorkflowDiagram steps={steps} />
          </Card>

          {latestDocument ? (
            <Card className="p-6">
              <SectionTitle title="Latest processed document" />
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="flex items-start gap-3 rounded-xl border border-border bg-surface-2 p-4">
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-soft text-brand">
                    <FileText size={16} />
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-text">{latestDocument.filename}</p>
                    <p className="truncate text-xs text-text-faint">{latestDocument.document_id}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2 rounded-xl border border-border bg-surface-2 p-4">
                  <Badge tone="brand">{(latestDocument.document_type || "unknown").replace(/_/g, " ")}</Badge>
                  <StatusBadge status={latestDocument.validation_status} />
                  <Badge tone="neutral">{latestDocument.page_count ?? "—"} pages</Badge>
                </div>
              </div>
            </Card>
          ) : null}
        </div>

        <AgentTracePanel trace={trace} />
      </div>
    </div>
  );
}
