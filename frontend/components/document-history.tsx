import { FileText } from "lucide-react";
import { Card, SectionTitle, StatusBadge, Badge, EmptyState } from "@/components/ui";

function docTypeLabel(t?: string) {
  return (t || "unknown").replace(/_/g, " ");
}

export default function DocumentHistory({ documents }: { documents: any[] }) {
  const docs = (documents || []).slice().reverse().slice(0, 8);

  return (
    <Card className="p-6">
      <SectionTitle title="Recent documents" hint="Most recent runs recorded in the processing registry." />
      {docs.length === 0 ? (
        <EmptyState icon={<FileText size={22} />} title="No processed documents yet" hint="Upload a document to get started." />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {docs.map((doc, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 rounded-xl border border-border bg-surface-2 p-3.5 transition hover:border-border-strong"
            >
              <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
                <FileText size={16} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-text">{doc.filename}</p>
                <p className="mt-0.5 truncate text-xs text-text-faint">{doc.document_id}</p>
                <div className="mt-2 flex flex-wrap items-center gap-1.5">
                  <Badge tone="brand">{docTypeLabel(doc.document_type)}</Badge>
                  <StatusBadge status={doc.validation_status} />
                  {doc.page_count != null ? (
                    <span className="text-xs text-text-muted">{doc.page_count}p</span>
                  ) : null}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
