export default function KpiTable({ entries }: { entries: any[] }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <div className="border-b border-gray-200 px-6 py-4">
        <h3 className="text-lg font-semibold text-gray-900">KPI Entries</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="px-6 py-3 font-medium">KPI</th>
              <th className="px-6 py-3 font-medium">Value</th>
              <th className="px-6 py-3 font-medium">Document</th>
              <th className="px-6 py-3 font-medium">Project</th>
              <th className="px-6 py-3 font-medium">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, idx) => (
              <tr key={idx} className="border-t border-gray-100">
                <td className="px-6 py-4">{entry.kpi_name}</td>
                <td className="px-6 py-4">{entry.value}</td>
                <td className="px-6 py-4">{entry.document_id || "-"}</td>
                <td className="px-6 py-4">{entry.project_id || "-"}</td>
                <td className="px-6 py-4">{entry.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}