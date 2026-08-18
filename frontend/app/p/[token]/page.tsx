"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Boxes } from "lucide-react";
import ProposalView from "@/components/proposal-view";
import ThemeToggle from "@/components/theme-toggle";
import { getProposalByToken } from "@/lib/api";

export default function PublicProposalPage() {
  const params = useParams();
  const token = String(params.token);
  const [proposal, setProposal] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getProposalByToken(token)
      .then((d) => setProposal(d.proposal))
      .catch((e) => setError(e.message || "Proposal not found"));
  }, [token]);

  return (
    <div className="app-canvas min-h-screen">
      <header className="border-b border-border bg-surface/70 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand to-brand-strong text-white">
              <Boxes size={16} />
            </span>
            <span className="text-sm font-bold text-text">Proziem Digital Global</span>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
        {error ? (
          <div className="rounded-xl border border-danger-soft bg-danger-soft px-4 py-8 text-center text-sm text-danger">
            {error}
          </div>
        ) : proposal ? (
          <>
            <p className="mb-4 text-center text-sm text-text-muted">
              Prepared for <span className="font-semibold text-text">{proposal.company_name}</span>
            </p>
            <ProposalView proposal={proposal} />
          </>
        ) : (
          <div className="h-96 animate-pulse rounded-2xl bg-surface-2" />
        )}
      </main>
    </div>
  );
}
