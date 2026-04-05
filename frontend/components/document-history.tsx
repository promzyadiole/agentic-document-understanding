export default function DocumentHistory({ documents }: { documents: any[] }) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900">Recent Documents</h3>

      <div className="mt-4 space-y-3">
        {(documents || []).length === 0 ? (
          <p className="text-sm text-gray-600">No processed documents yet.</p>
        ) : (
          documents
            .slice()
            .reverse()
            .slice(0, 6)
            .map((doc, idx) => (
              <div key={idx} className="rounded-2xl bg-gray-50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium text-gray-900">{doc.filename}</p>
                  <span className="rounded-full bg-white px-3 py-1 text-xs text-gray-700">
                    {doc.document_type || "unknown"}
                  </span>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  <p>Document ID: {doc.document_id}</p>
                  <p>Pages: {doc.page_count ?? "-"}</p>
                  <p>Validation: {doc.validation_status || "-"}</p>
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
}