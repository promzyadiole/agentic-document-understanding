function Badge({
  label,
  tone = "gray",
}: {
  label: string;
  tone?: "green" | "yellow" | "red" | "blue" | "gray";
}) {
  const styles = {
    green: "bg-green-100 text-green-800",
    yellow: "bg-yellow-100 text-yellow-800",
    red: "bg-red-100 text-red-800",
    blue: "bg-blue-100 text-blue-800",
    gray: "bg-gray-100 text-gray-700",
  };

  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${styles[tone]}`}>
      {label}
    </span>
  );
}

function toneForValidation(status?: string) {
  if (status === "pass") return "green";
  if (status === "warning") return "yellow";
  if (status === "fail") return "red";
  return "gray";
}

function toneForDocType(type?: string) {
  if (type === "financial_report") return "blue";
  if (type === "invoice" || type === "purchase_order" || type === "delivery_note") return "green";
  if (type === "unknown") return "gray";
  return "blue";
}

export default function LatestAgentRun({ document }: { document: any }) {
  const trace = document?.agent_trace;

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900">Latest Agent Run</h3>

      {!document ? (
        <p className="mt-3 text-sm text-gray-600">No processed document available yet.</p>
      ) : (
        <div className="mt-4 space-y-4 text-sm text-gray-700">
          <div>
            <p className="font-medium text-gray-900">{document.filename}</p>
            <p className="mt-1 text-gray-600">Document ID: {document.document_id}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Badge label={document.document_type || "unknown"} tone={toneForDocType(document.document_type)} />
            <Badge label={document.validation_status || "no validation"} tone={toneForValidation(document.validation_status)} />
            <Badge label={`loops: ${trace?.loop_count ?? "-"}`} tone="gray" />
          </div>

          <div className="space-y-2">
            <p>
              <span className="font-medium">Final action:</span> {trace?.agent_action || "-"}
            </p>
            <p>
              <span className="font-medium">Final reasoning:</span> {trace?.agent_reasoning || "-"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}