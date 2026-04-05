export default function LeadCard({
  lead,
  onDraft,
}: {
  lead: any;
  onDraft: (lead: any) => void;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{lead.company_name}</h3>
          <p className="mt-1 text-sm text-gray-500">{lead.location || "Unknown location"}</p>
        </div>
        <div className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-700">
          {lead.relevance_score}
        </div>
      </div>

      <p className="mt-4 text-sm leading-6 text-gray-600">{lead.summary}</p>

      {lead.website ? (
        <p className="mt-3 text-sm text-gray-500">{lead.website}</p>
      ) : null}

      {Array.isArray(lead.evidence) && lead.evidence.length > 0 ? (
        <div className="mt-4 space-y-2">
          <p className="text-sm font-medium text-gray-800">Evidence</p>
          <ul className="list-disc space-y-1 pl-5 text-sm text-gray-600">
            {lead.evidence.slice(0, 3).map((item: string, idx: number) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <button
        onClick={() => onDraft(lead)}
        className="mt-5 rounded-xl bg-black px-4 py-2 text-sm text-white transition hover:opacity-90"
      >
        Draft email
      </button>
    </div>
  );
}