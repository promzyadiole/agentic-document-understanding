import { Card, SectionTitle, EmptyState } from "@/components/ui";
import { Table } from "lucide-react";

function label(name: string) {
  return (name || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function fmtTime(ts?: string) {
  if (!ts) return "—";
  const d = new Date(ts);
  return isNaN(d.getTime()) ? ts : d.toLocaleString();
}

export default function KpiTable({ entries }: { entries: any[] }) {
  const rows = (entries || []).slice().reverse();

  return (
    <Card className="overflow-hidden">
      <div className="p-6 pb-0">
        <SectionTitle title="KPI entries" hint={`${rows.length} record(s), newest first.`} />
      </div>
      {rows.length === 0 ? (
        <div className="p-6">
          <EmptyState icon={<Table size={22} />} title="No KPI records" />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-y border-border bg-surface-2 text-text-faint">
                <th className="px-6 py-3 font-medium">KPI</th>
                <th className="px-6 py-3 font-medium">Value</th>
                <th className="px-6 py-3 font-medium">Document</th>
                <th className="px-6 py-3 font-medium">Project</th>
                <th className="px-6 py-3 font-medium">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((entry, idx) => (
                <tr key={idx} className="border-b border-border transition hover:bg-surface-2">
                  <td className="px-6 py-3 font-medium text-text">{label(entry.kpi_name)}</td>
                  <td className="px-6 py-3">
                    <span className="font-mono text-text">{entry.value}</span>
                  </td>
                  <td className="max-w-[180px] truncate px-6 py-3 text-text-muted">{entry.document_id || "—"}</td>
                  <td className="px-6 py-3 text-text-muted">{entry.project_id || "—"}</td>
                  <td className="px-6 py-3 text-text-faint">{fmtTime(entry.timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
