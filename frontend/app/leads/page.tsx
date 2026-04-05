"use client";

import { useState } from "react";
import Topbar from "@/components/topbar";
import LeadCard from "@/components/lead-card";
import { draftEmail, searchLeads } from "@/lib/api";

export default function LeadsPage() {
  const [query, setQuery] = useState(
    "top construction companies with complex multi-project operations and digital transformation challenges"
  );
  const [locationHint, setLocationHint] = useState("Germany");
  const [leads, setLeads] = useState<any[]>([]);
  const [draftResult, setDraftResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    setLoading(true);
    setDraftResult(null);
    setError("");

    try {
      const data = await searchLeads({
        query,
        max_results: 10,
        location_hint: locationHint,
      });
      setLeads(data.leads || []);
    } catch (err: any) {
      setError(err.message || "Lead search failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleDraft(lead: any) {
    setError("");
    try {
      const data = await draftEmail({
        company_name: lead.company_name,
        company_summary: lead.summary,
        website: lead.website,
        location: lead.location,
        recipient_email: "",
      });
      setDraftResult(data);
    } catch (err: any) {
      setError(err.message || "Draft creation failed");
    }
  }

  const draft = draftResult?.draft;

  return (
    <div className="space-y-6">
      <Topbar
        title="Leads & Outreach"
        subtitle="Discover candidate construction companies and generate human-approved draft emails."
      />

      <div className="space-y-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-black"
          placeholder="Lead research query"
        />
        <input
          value={locationHint}
          onChange={(e) => setLocationHint(e.target.value)}
          className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-black"
          placeholder="Location hint"
        />
        <button
          onClick={handleSearch}
          className="rounded-xl bg-black px-5 py-3 text-white transition hover:opacity-90"
        >
          {loading ? "Searching..." : "Search leads"}
        </button>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        {leads.map((lead, idx) => (
          <LeadCard key={idx} lead={lead} onDraft={handleDraft} />
        ))}
      </div>

      {draft ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900">Draft email</h3>
          <div className="mt-4 rounded-2xl bg-gray-50 p-5">
            <p className="text-sm text-gray-500">Company</p>
            <p className="mt-1 font-medium text-gray-900">{draft.company_name}</p>

            <p className="mt-4 text-sm text-gray-500">Subject</p>
            <p className="mt-1 font-medium text-gray-900">{draft.subject}</p>

            <p className="mt-4 text-sm text-gray-500">Body</p>
            <div className="mt-2 whitespace-pre-wrap text-sm leading-7 text-gray-700">
              {draft.body}
            </div>

            <div className="mt-4 flex gap-3 text-sm">
              <span className="rounded-full bg-yellow-100 px-3 py-1 text-yellow-800">
                Approval required: {String(draft.approval_required)}
              </span>
              <span className="rounded-full bg-gray-100 px-3 py-1 text-gray-700">
                Approved: {String(draft.approved)}
              </span>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}