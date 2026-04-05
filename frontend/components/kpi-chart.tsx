"use client";

import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export default function KpiChart({ entries }: { entries: any[] }) {
  const grouped: Record<string, number[]> = {};

  for (const entry of entries || []) {
    if (!grouped[entry.kpi_name]) grouped[entry.kpi_name] = [];
    grouped[entry.kpi_name].push(Number(entry.value));
  }

  const data = Object.entries(grouped).map(([name, values]) => ({
    name,
    value:
      values.length > 0
        ? Number((values.reduce((a, b) => a + b, 0) / values.length).toFixed(4))
        : 0,
  }));

  if (data.length === 0) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900">KPI Trend View</h3>
        <p className="mt-3 text-sm text-gray-600">No KPI data available yet.</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900">KPI Trend View</h3>
      <div className="mt-4 overflow-x-auto">
        <LineChart
          width={700}
          height={320}
          data={data}
          margin={{ top: 10, right: 20, left: 0, bottom: 50 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-15} textAnchor="end" height={70} interval={0} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" strokeWidth={2} />
        </LineChart>
      </div>
    </div>
  );
}