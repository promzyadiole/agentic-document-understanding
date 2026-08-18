"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileSignature, Plus, Building2 } from "lucide-react";
import Topbar from "@/components/topbar";
import { Card, ErrorBanner, EmptyState, Badge } from "@/components/ui";
import { listProposals } from "@/lib/api";

function money(cents: number, currency: string) {
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: (currency || "usd").toUpperCase(), maximumFractionDigits: 0 }).format((cents || 0) / 100);
  } catch {
    return `$${((cents || 0) / 100).toFixed(0)}`;
  }
}

export default function ProposalsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProposals()
      .then((d) => setItems((d.proposals || []).slice().reverse()))
      .catch((e) => setError(e.message || "Failed to load proposals"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <Topbar
        eyebrow="Proposals"
        title="Proposals"
        subtitle="Aligned proposals generated for your leads. Open one to share it or mark it paid."
        actions={
          <Link href="/proposals/new" className="btn btn-primary">
            <Plus size={15} /> New proposal
          </Link>
        }
      />

      <ErrorBanner message={error} />

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {[...Array(2)].map((_, i) => (
            <Card key={i} className="shimmer h-32" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={<FileSignature size={22} />}
          title="No proposals yet"
          hint="Approve an outreach email, then generate a proposal for the company."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((p) => (
            <Link key={p.id} href={`/proposals/${p.id}`} className="card card-hover p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-soft text-brand">
                    <Building2 size={18} />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-text">{p.company_name}</p>
                    <p className="mt-0.5 line-clamp-1 text-xs text-text-muted">{p.content?.hero?.headline}</p>
                  </div>
                </div>
                <Badge tone={p.status === "paid" ? "ok" : "brand"}>{p.status}</Badge>
              </div>
              <p className="mt-3 text-lg font-bold text-text">{money(p.price_cents, p.currency)}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
