"use client";

import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, SectionTitle, EmptyState } from "@/components/ui";
import { BarChart3 } from "lucide-react";

function label(name: string) {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function KpiChart({ entries }: { entries: any[] }) {
  const grouped: Record<string, number[]> = {};
  for (const entry of entries || []) {
    if (!grouped[entry.kpi_name]) grouped[entry.kpi_name] = [];
    grouped[entry.kpi_name].push(Number(entry.value));
  }

  const data = Object.entries(grouped).map(([name, values]) => ({
    name: label(name),
    value: values.length ? Number((values.reduce((a, b) => a + b, 0) / values.length).toFixed(3)) : 0,
  }));

  return (
    <Card className="p-6">
      <SectionTitle title="KPI averages" hint="Mean value per metric across all processed documents." />
      {data.length === 0 ? (
        <EmptyState icon={<BarChart3 size={22} />} title="No KPI data yet" hint="Process a document to populate metrics." />
      ) : (
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis
                dataKey="name"
                angle={-18}
                textAnchor="end"
                height={64}
                interval={0}
                tick={{ fill: "var(--text-faint)", fontSize: 11 }}
                stroke="var(--border-strong)"
              />
              <YAxis
                domain={[0, 1]}
                tick={{ fill: "var(--text-faint)", fontSize: 11 }}
                stroke="var(--border-strong)"
              />
              <Tooltip
                cursor={{ fill: "var(--brand-soft)" }}
                contentStyle={{
                  background: "var(--surface)",
                  border: "1px solid var(--border-strong)",
                  borderRadius: 12,
                  color: "var(--text)",
                  fontSize: 12,
                }}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {data.map((d, i) => (
                  <Cell
                    key={i}
                    fill={d.value >= 0.85 ? "var(--ok)" : d.value >= 0.6 ? "var(--brand)" : "var(--accent)"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
