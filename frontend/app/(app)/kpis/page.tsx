"use client";

import { useEffect, useState } from "react";
import Topbar from "@/components/topbar";
import KpiTable from "@/components/kpi-table";
import KpiChart from "@/components/kpi-chart";
import { Card, ErrorBanner } from "@/components/ui";
import { getKpis } from "@/lib/api";

function SummaryCard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <Card className="p-5">
      <p className="label-caps">{label}</p>
      <p className="mt-2 text-2xl font-bold tracking-tight text-text">{value}</p>
      {hint ? <p className="mt-1 text-xs text-text-muted">{hint}</p> : null}
    </Card>
  );
}

export default function KpisPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getKpis()
      .then(setData)
      .catch((err) => setError(err.message || "Failed to load KPIs"));
  }, []);

  const summary = data?.summary || {};
  const averages = summary?.averages || {};
  const pct = (v: any) => (v == null ? "—" : `${Math.round(Number(v) * 100)}%`);

  return (
    <div>
      <Topbar
        eyebrow="Quality"
        title="KPIs"
        subtitle="Extraction coverage, validation quality, and runtime metrics logged on every document run."
      />

      <ErrorBanner message={error} />

      {data ? (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <SummaryCard label="Total KPI Records" value={summary.total_records ?? 0} hint="Across all runs" />
            <SummaryCard label="Field Coverage" value={pct(averages.field_coverage)} hint="Fields extracted" />
            <SummaryCard label="Extraction Accuracy" value={pct(averages.extraction_accuracy)} hint="Classifier-confidence proxy" />
            <SummaryCard label="Schema Validity" value={pct(averages.schema_validity)} hint="Validation pass rate" />
          </div>

          <KpiChart entries={data.entries || []} />
          <KpiTable entries={data.entries || []} />
        </div>
      ) : !error ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="shimmer h-24 p-5" />
          ))}
        </div>
      ) : null}
    </div>
  );
}
