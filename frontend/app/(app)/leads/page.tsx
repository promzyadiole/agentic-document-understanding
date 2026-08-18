"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, Building2, MailCheck, ArrowRight } from "lucide-react";
import Topbar from "@/components/topbar";
import LeadCard from "@/components/lead-card";
import { Card, ErrorBanner, SectionTitle, EmptyState } from "@/components/ui";
import { createOutreach, searchLeads } from "@/lib/api";

export default function LeadsPage() {
  const [query, setQuery] = useState(
    "top construction companies with complex multi-project operations and digital transformation challenges"
  );
  const [locationHint, setLocationHint] = useState("Germany");
  const [leads, setLeads] = useState<any[]>([]);
  const [created, setCreated] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [draftingFor, setDraftingFor] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    setLoading(true);
    setCreated(null);
    setError("");
    try {
      const data = await searchLeads({ query, max_results: 10, location_hint: locationHint });
      setLeads(data.leads || []);
      setSearched(true);
    } catch (err: any) {
      setError(err.message || "Lead search failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleDraft(lead: any) {
    setError("");
    setCreated(null);
    setDraftingFor(lead.company_name);
    try {
      await createOutreach({
        company_name: lead.company_name,
        company_summary: lead.summary,
        website: lead.website,
        location: lead.location,
        recipient_email: lead.email || "",
      });
      setCreated(lead.company_name);
      if (typeof window !== "undefined") {
        setTimeout(() => document.getElementById("created-panel")?.scrollIntoView({ behavior: "smooth" }), 60);
      }
    } catch (err: any) {
      setError(err.message || "Draft creation failed");
    } finally {
      setDraftingFor(null);
    }
  }

  return (
    <div>
      <Topbar
        eyebrow="Growth"
        title="Leads & Outreach"
        subtitle="Discover companies with Tavily + LLM scoring (grounded, with contact emails), then draft outreach that waits for your approval."
      />

      <Card className="p-6">
        <SectionTitle title="Find leads" hint="Describe your ideal customer; results are scored for fit and enriched with a contact email where available." />
        <div className="grid gap-3 sm:grid-cols-[1fr_200px]">
          <div>
            <label className="label-caps">Research query</label>
            <input value={query} onChange={(e) => setQuery(e.target.value)} className="input mt-1.5" placeholder="Lead research query" />
          </div>
          <div>
            <label className="label-caps">Location hint</label>
            <input value={locationHint} onChange={(e) => setLocationHint(e.target.value)} className="input mt-1.5" placeholder="e.g. Germany" />
          </div>
        </div>
        <button onClick={handleSearch} disabled={loading} className="btn btn-primary mt-4">
          <Search size={16} /> {loading ? "Searching…" : "Search leads"}
        </button>
        <ErrorBanner message={error} />
      </Card>

      {created ? (
        <div id="created-panel" className="mt-6">
          <Card className="animate-fade-up flex flex-col items-start gap-3 border-ok-soft p-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ok-soft text-ok">
                <MailCheck size={18} />
              </span>
              <div>
                <p className="text-sm font-semibold text-text">Outreach drafted for {created}</p>
                <p className="text-xs text-text-muted">It&apos;s waiting for your approval before anything is sent.</p>
              </div>
            </div>
            <Link href="/outreach" className="btn btn-primary shrink-0">
              Review in Approvals <ArrowRight size={15} />
            </Link>
          </Card>
        </div>
      ) : null}

      <div className="mt-6">
        {leads.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {leads.map((lead, idx) => (
              <LeadCard key={idx} lead={lead} onDraft={handleDraft} drafting={draftingFor === lead.company_name} />
            ))}
          </div>
        ) : searched && !loading ? (
          <EmptyState icon={<Building2 size={22} />} title="No leads found" hint="Try a broader query or a different location." />
        ) : loading ? (
          <div className="grid gap-4 md:grid-cols-2">
            {[...Array(4)].map((_, i) => (
              <Card key={i} className="shimmer h-48" />
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
