"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { FileSignature, Sparkles, Globe } from "lucide-react";
import Topbar from "@/components/topbar";
import { Card, ErrorBanner, SectionTitle } from "@/components/ui";
import { generateProposal } from "@/lib/api";

function NewProposalInner() {
  const router = useRouter();
  const params = useSearchParams();

  const [company, setCompany] = useState(params.get("company") || "");
  const [website, setWebsite] = useState(params.get("website") || "");
  const outreachId = params.get("outreach") || undefined;

  const [price, setPrice] = useState("15000");
  const [brief, setBrief] = useState(
    "Automate their document-heavy and knowledge-intensive workflows with agentic document understanding, retrieval, and automation."
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!company.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await generateProposal({
        company_name: company.trim(),
        website: website.trim() || undefined,
        price_cents: Math.round((parseFloat(price) || 0) * 100),
        currency: "usd",
        brief: brief.trim(),
        outreach_id: outreachId,
      });
      const id = data?.proposal?.id;
      if (id) router.push(`/proposals/${id}`);
      else setError("Proposal generated but no id was returned.");
    } catch (err: any) {
      setError(err.message || "Proposal generation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Topbar
        eyebrow="Proposals"
        title="Generate a proposal"
        subtitle="Claude Opus reads the company's website and writes a proposal aligned to their needs and Proziem's credibility."
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <Card className="p-6">
          <SectionTitle title="Engagement details" hint="Prefilled from the approved lead — adjust anything before generating." />
          <div className="space-y-4">
            <div>
              <label className="label-caps">Company name</label>
              <input value={company} onChange={(e) => setCompany(e.target.value)} className="input mt-1.5" placeholder="Acme Construction" />
            </div>
            <div>
              <label className="label-caps">Company website</label>
              <input value={website} onChange={(e) => setWebsite(e.target.value)} className="input mt-1.5" placeholder="https://example.com" />
              <p className="mt-1 flex items-center gap-1 text-xs text-text-faint">
                <Globe size={11} /> Used to ground and align the proposal.
              </p>
            </div>
            <div>
              <label className="label-caps">Price (USD)</label>
              <input value={price} onChange={(e) => setPrice(e.target.value)} type="number" className="input mt-1.5" placeholder="15000" />
            </div>
            <div>
              <label className="label-caps">Brief</label>
              <textarea value={brief} onChange={(e) => setBrief(e.target.value)} className="input mt-1.5 min-h-[120px] resize-y" />
            </div>
            <button onClick={handleGenerate} disabled={!company.trim() || loading} className="btn btn-primary w-full">
              <Sparkles size={16} /> {loading ? "Generating with Claude…" : "Generate proposal"}
            </button>
            <ErrorBanner message={error} />
          </div>
        </Card>

        <Card className="flex h-full min-h-[300px] flex-col items-center justify-center p-8 text-center">
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-soft text-brand">
            <FileSignature size={26} />
          </span>
          <p className="text-sm font-medium text-text">Your proposal will open here</p>
          <p className="mt-1 max-w-xs text-sm text-text-muted">
            A full page — hero, deliverables, process, pricing, and terms — that you can share with the company.
          </p>
        </Card>
      </div>
    </div>
  );
}

export default function NewProposalPage() {
  return (
    <Suspense fallback={<div className="p-6 text-sm text-text-muted">Loading…</div>}>
      <NewProposalInner />
    </Suspense>
  );
}
