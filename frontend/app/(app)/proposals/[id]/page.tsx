"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Link2, Check, DollarSign, ExternalLink, ArrowLeft } from "lucide-react";
import Topbar from "@/components/topbar";
import ProposalView from "@/components/proposal-view";
import { Card, ErrorBanner, SectionTitle } from "@/components/ui";
import { getProposal, registerPayment } from "@/lib/api";

export default function ProposalDetailPage() {
  const params = useParams();
  const id = String(params.id);

  const [proposal, setProposal] = useState<any>(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [amount, setAmount] = useState("");
  const [paying, setPaying] = useState(false);
  const [paid, setPaid] = useState(false);

  function load() {
    getProposal(id)
      .then((d) => {
        setProposal(d.proposal);
        setAmount(String(((d.proposal?.price_cents || 0) / 100).toFixed(0)));
        if (d.proposal?.status === "paid") setPaid(true);
      })
      .catch((e) => setError(e.message || "Failed to load proposal"));
  }
  useEffect(load, [id]);

  const shareUrl =
    typeof window !== "undefined" && proposal ? `${window.location.origin}/p/${proposal.share_token}` : "";

  function copyLink() {
    if (!shareUrl) return;
    navigator.clipboard?.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  async function handleRegisterPayment() {
    setPaying(true);
    setError("");
    try {
      await registerPayment({
        proposal_id: id,
        amount_cents: Math.round((parseFloat(amount) || 0) * 100),
        currency: proposal?.currency || "usd",
      });
      setPaid(true);
    } catch (e: any) {
      setError(e.message || "Could not register payment");
    } finally {
      setPaying(false);
    }
  }

  return (
    <div>
      <Topbar
        eyebrow="Proposal"
        title={proposal?.company_name || "Proposal"}
        subtitle={proposal?.content?.hero?.headline}
        actions={
          <Link href="/proposals" className="btn btn-ghost">
            <ArrowLeft size={15} /> All proposals
          </Link>
        }
      />

      <ErrorBanner message={error} />

      {proposal ? (
        <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
          <ProposalView proposal={proposal} />

          <div className="space-y-4">
            <Card className="p-5">
              <SectionTitle title="Share with the client" hint="A public, read-only proposal page." />
              <div className="flex items-center gap-2">
                <input readOnly value={shareUrl} className="input text-xs" />
                <button onClick={copyLink} className="btn btn-ghost !px-3" title="Copy link">
                  {copied ? <Check size={15} className="text-ok" /> : <Link2 size={15} />}
                </button>
              </div>
              {shareUrl ? (
                <a href={shareUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-brand hover:text-brand-strong">
                  <ExternalLink size={12} /> Open public page
                </a>
              ) : null}
            </Card>

            <Card className="p-5">
              <SectionTitle title="Payment" hint="Register a payment once the client agrees & pays." />
              {paid ? (
                <div className="flex items-center gap-2 rounded-xl border border-ok-soft bg-ok-soft px-4 py-3 text-sm text-ok">
                  <Check size={16} /> Payment registered — pending confirmation in Revenue.
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <label className="label-caps">Amount (USD)</label>
                    <div className="mt-1.5 flex items-center gap-2">
                      <DollarSign size={15} className="text-text-faint" />
                      <input value={amount} onChange={(e) => setAmount(e.target.value)} type="number" className="input" />
                    </div>
                  </div>
                  <button onClick={handleRegisterPayment} disabled={paying} className="btn btn-primary w-full">
                    <DollarSign size={15} /> {paying ? "Registering…" : "Register payment"}
                  </button>
                </div>
              )}
              {paid ? (
                <Link href="/revenue" className="btn btn-ghost mt-3 w-full">
                  Go to Revenue
                </Link>
              ) : null}
            </Card>
          </div>
        </div>
      ) : !error ? (
        <Card className="shimmer h-96" />
      ) : null}
    </div>
  );
}
