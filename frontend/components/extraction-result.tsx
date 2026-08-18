"use client";

import { useState } from "react";
import { Quote, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { Badge, ConfidenceBadge, StatusBadge, Card, SectionTitle } from "@/components/ui";

type Field = {
  name: string;
  value: any;
  normalized_value?: any;
  confidence_score?: number;
  source_spans?: { page: number; text_excerpt: string }[];
};

function prettyName(name: string) {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function FieldRow({ field }: { field: Field }) {
  const [open, setOpen] = useState(false);
  const evidence = field.source_spans?.[0]?.text_excerpt;
  const page = field.source_spans?.[0]?.page;

  return (
    <div className="rounded-xl border border-border bg-surface-2 p-3.5 transition hover:border-border-strong">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="label-caps">{prettyName(field.name)}</p>
          <p className="mt-1 break-words text-sm font-semibold text-text">
            {field.value != null && String(field.value) !== "" ? String(field.value) : "—"}
          </p>
          {field.normalized_value != null &&
          String(field.normalized_value) !== String(field.value) ? (
            <p className="mt-0.5 text-xs text-text-faint">
              normalized: {String(field.normalized_value)}
            </p>
          ) : null}
        </div>
        <ConfidenceBadge score={field.confidence_score} />
      </div>

      {evidence ? (
        <div className="mt-2.5">
          <button
            onClick={() => setOpen((o) => !o)}
            className="inline-flex items-center gap-1.5 text-xs font-medium text-brand transition hover:text-brand-strong"
          >
            <Quote size={12} />
            {open ? "Hide" : "Show"} evidence{page ? ` · p.${page}` : ""}
          </button>
          {open ? (
            <p className="mt-2 rounded-lg border-l-2 border-brand bg-brand-soft px-3 py-2 text-xs italic leading-relaxed text-text">
              “{evidence}”
            </p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function ValidationIssues({ validation }: { validation: any }) {
  const issues = validation?.issues || [];
  if (!issues.length) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-ok-soft bg-ok-soft px-4 py-3 text-sm text-ok">
        <CheckCircle2 size={16} /> No validation issues — all required fields present and consistent.
      </div>
    );
  }
  return (
    <div className="space-y-2">
      {issues.map((issue: any, i: number) => {
        const s = (issue.status || "").toLowerCase();
        const Icon = s === "fail" ? XCircle : AlertTriangle;
        const tone = s === "fail" ? "text-danger" : "text-warn";
        return (
          <div key={i} className="flex items-start gap-2.5 rounded-xl border border-border bg-surface-2 px-3.5 py-2.5 text-sm">
            <Icon size={15} className={`mt-0.5 shrink-0 ${tone}`} />
            <div>
              <span className="font-medium text-text">{prettyName(issue.field_name)}</span>
              <span className="text-text-muted"> — {issue.message}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function ExtractionResult({
  classification,
  extraction,
  validation,
}: {
  classification?: any;
  extraction?: any;
  validation?: any;
}) {
  const fields: Field[] = extraction?.fields ? Object.values(extraction.fields) : [];
  const structured = extraction?.structured_data || {};
  const lineItems: any[] = structured.line_items || structured.received_items || [];

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        {classification?.document_type ? (
          <Badge tone="brand">{prettyName(classification.document_type)}</Badge>
        ) : null}
        {classification?.confidence_score != null ? (
          <span className="text-xs text-text-muted">
            classified with <ConfidenceBadge score={classification.confidence_score} /> confidence
          </span>
        ) : null}
        {validation?.overall_status ? <StatusBadge status={validation.overall_status} /> : null}
      </div>

      {fields.length ? (
        <Card className="p-5">
          <SectionTitle title="Extracted fields" hint="Each value is grounded in a verbatim evidence snippet from the source." />
          <div className="grid gap-3 sm:grid-cols-2">
            {fields.map((f) => (
              <FieldRow key={f.name} field={f} />
            ))}
          </div>
        </Card>
      ) : null}

      {lineItems.length ? (
        <Card className="p-5">
          <SectionTitle title="Line items" hint={`${lineItems.length} row(s) detected`} />
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-text-faint">
                  <th className="pb-2 font-medium">Description</th>
                  <th className="pb-2 text-right font-medium">Qty</th>
                  <th className="pb-2 text-right font-medium">Amount</th>
                </tr>
              </thead>
              <tbody>
                {lineItems.map((item, i) => (
                  <tr key={i} className="border-t border-border">
                    <td className="py-2 pr-4 text-text">{item.description || "—"}</td>
                    <td className="py-2 text-right text-text-muted">{item.quantity ?? "—"}</td>
                    <td className="py-2 text-right font-medium text-text">{item.amount ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}

      {validation ? (
        <Card className="p-5">
          <SectionTitle
            title="Validation"
            hint="Schema, required-field, and arithmetic checks with a self-correction loop."
          />
          <ValidationIssues validation={validation} />
        </Card>
      ) : null}
    </div>
  );
}
