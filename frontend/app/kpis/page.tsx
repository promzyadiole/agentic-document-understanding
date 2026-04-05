"use client";

import { useEffect, useState } from "react";
import Topbar from "@/components/topbar";
import KpiTable from "@/components/kpi-table";
import { getKpis } from "@/lib/api";

function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}

export default function KpisPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const res = await getKpis();
        setData(res);
      } catch (err: any) {
        setError(err.message || "Failed to load KPIs");
      }
    }

    loadData();
  }, []);

  const summary = data?.summary || {};
  const averages = summary?.averages || {};

  return (
    <div className="space-y-6">
      <Topbar
        title="KPIs"
        subtitle="Runtime metrics for extraction quality, validation, and system performance."
      />

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      ) : null}

      {data ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <SummaryCard label="Total KPI Records" value={summary.total_records ?? 0} />
            <SummaryCard label="Field Coverage" value={averages.field_coverage ?? "-"} />
            <SummaryCard label="Extraction Accuracy" value={averages.extraction_accuracy ?? "-"} />
            <SummaryCard label="Schema Validity" value={averages.schema_validity ?? "-"} />
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900">Summary JSON</h3>
            <pre className="mt-4 overflow-auto rounded-2xl bg-gray-950 p-4 text-xs text-green-300">
              {JSON.stringify(summary, null, 2)}
            </pre>
          </div>

          <KpiTable entries={data.entries || []} />
        </>
      ) : null}
    </div>
  );
}