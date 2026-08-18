"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DollarSign, Check, RefreshCw, TrendingUp, Clock, FileText, MailCheck } from "lucide-react";
import Topbar from "@/components/topbar";
import { Card, ErrorBanner, StatusBadge, EmptyState, SectionTitle } from "@/components/ui";
import { listPayments, getRevenueSummary, confirmPayment } from "@/lib/api";

function money(cents: number, currency = "usd") {
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: currency.toUpperCase(), maximumFractionDigits: 0 }).format((cents || 0) / 100);
  } catch {
    return `$${((cents || 0) / 100).toFixed(0)}`;
  }
}

function SummaryCard({ icon: Icon, label, value, accent }: any) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <p className="label-caps">{label}</p>
        <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${accent ? "bg-ok text-white" : "bg-brand-soft text-brand"}`}>
          <Icon size={17} />
        </span>
      </div>
      <p className="mt-3 text-3xl font-bold tracking-tight text-text">{value}</p>
    </Card>
  );
}

export default function RevenuePage() {
  const [summary, setSummary] = useState<any>(null);
  const [payments, setPayments] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState<string | null>(null);
  const [flash, setFlash] = useState<string | null>(null);

  function load() {
    setLoading(true);
    Promise.all([getRevenueSummary().catch(() => null), listPayments().catch(() => ({ payments: [] }))])
      .then(([s, p]) => {
        setSummary(s);
        setPayments((p?.payments || []).slice().reverse());
      })
      .catch((e) => setError(e.message || "Failed to load revenue"))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  async function confirm(id: string) {
    setConfirming(id);
    setError("");
    setFlash(null);
    try {
      const d = await confirmPayment(id);
      setFlash(d.message || "Payment confirmed.");
      load();
    } catch (e: any) {
      setError(e.message || "Confirm failed");
    } finally {
      setConfirming(null);
    }
  }

  return (
    <div>
      <Topbar
        eyebrow="Finance"
        title="Revenue"
        subtitle="Registered payments become income once you confirm them. Confirming a payment runs the proposal PDF through the document workflow and drafts a thank-you email for your approval."
        actions={
          <button onClick={load} className="btn btn-ghost">
            <RefreshCw size={15} /> Refresh
          </button>
        }
      />

      <ErrorBanner message={error} />
      {flash ? (
        <div className="mb-6 flex items-center gap-2 rounded-xl border border-ok-soft bg-ok-soft px-4 py-3 text-sm text-ok">
          <Check size={16} /> {flash}
          <Link href="/outreach" className="ml-auto inline-flex items-center gap-1 font-medium underline">
            <MailCheck size={14} /> Review thank-you email
          </Link>
        </div>
      ) : null}

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <SummaryCard icon={TrendingUp} label="Total revenue" value={money(summary?.total_revenue_cents || 0)} accent />
        <SummaryCard icon={Check} label="Confirmed" value={String(summary?.confirmed_count ?? 0)} />
        <SummaryCard icon={Clock} label="Pending" value={String(summary?.pending_count ?? 0)} />
      </div>

      <Card className="overflow-hidden">
        <div className="p-6 pb-0">
          <SectionTitle title="Payments" hint="Newest first." />
        </div>
        {loading ? (
          <div className="p-6">
            <Card className="shimmer h-24" />
          </div>
        ) : payments.length === 0 ? (
          <div className="p-6">
            <EmptyState icon={<DollarSign size={22} />} title="No payments yet" hint="Register a payment from a proposal to see it here." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-y border-border bg-surface-2 text-text-faint">
                  <th className="px-6 py-3 font-medium">Company</th>
                  <th className="px-6 py-3 font-medium">Amount</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Document</th>
                  <th className="px-6 py-3 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id} className="border-b border-border">
                    <td className="px-6 py-3 font-medium text-text">{p.company_name || "—"}</td>
                    <td className="px-6 py-3 font-semibold text-text">{money(p.amount_cents, p.currency)}</td>
                    <td className="px-6 py-3">
                      <StatusBadge status={p.status === "confirmed" ? "pass" : "warning"} />
                    </td>
                    <td className="max-w-[160px] truncate px-6 py-3 text-text-muted">
                      {p.document_id ? (
                        <span className="inline-flex items-center gap-1 text-xs">
                          <FileText size={12} className="text-ok" /> processed
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-6 py-3 text-right">
                      {p.status === "pending" ? (
                        <button onClick={() => confirm(p.id)} disabled={confirming === p.id} className="btn btn-primary !py-1.5 !text-xs">
                          <Check size={13} /> {confirming === p.id ? "Confirming…" : "Accept & confirm"}
                        </button>
                      ) : (
                        <span className="text-xs text-text-faint">confirmed</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
