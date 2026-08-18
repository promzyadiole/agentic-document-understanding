import { Brain, Repeat } from "lucide-react";
import { Card, SectionTitle, StatusBadge, Badge, EmptyState } from "@/components/ui";

function docTypeLabel(t?: string) {
  return (t || "unknown").replace(/_/g, " ");
}

export default function LatestAgentRun({ document }: { document: any }) {
  const trace = document?.agent_trace;

  return (
    <Card className="p-6">
      <SectionTitle title="Latest agent run" hint="The most recent agent-controlled document run." />
      {!document ? (
        <EmptyState icon={<Brain size={22} />} title="No runs yet" hint="Process a document to see the agent's decisions." />
      ) : (
        <div className="space-y-4">
          <div>
            <p className="truncate text-sm font-semibold text-text">{document.filename}</p>
            <p className="mt-0.5 truncate text-xs text-text-faint">{document.document_id}</p>
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            <Badge tone="brand">{docTypeLabel(document.document_type)}</Badge>
            <StatusBadge status={document.validation_status} />
            <Badge tone="neutral">
              <Repeat size={11} /> {trace?.loop_count ?? "-"} loops
            </Badge>
          </div>

          <div className="rounded-xl border border-border bg-surface-2 p-4">
            <p className="label-caps">Final decision</p>
            <p className="mt-1 text-sm font-medium text-text">{trace?.agent_action || "—"}</p>
            {trace?.agent_reasoning ? (
              <p className="mt-2 text-xs italic leading-relaxed text-text-muted">
                “{trace.agent_reasoning}”
              </p>
            ) : null}
          </div>
        </div>
      )}
    </Card>
  );
}
