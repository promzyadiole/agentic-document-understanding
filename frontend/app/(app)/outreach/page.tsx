"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MailCheck, Check, X, FileSignature, RefreshCw, Building2, ArrowRight, Heart, Send } from "lucide-react";
import Topbar from "@/components/topbar";
import { Card, ErrorBanner, Badge, StatusBadge, EmptyState } from "@/components/ui";
import { listOutreach, approveOutreach, rejectOutreach } from "@/lib/api";

const SENDER = "promzy007adiole100@gmail.com";

function OutreachRow({ item, onChanged }: { item: any; onChanged: () => void }) {
  const [recipient, setRecipient] = useState(item.recipient_email || "");
  const [subject, setSubject] = useState(item.subject);
  const [body, setBody] = useState(item.body);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const editable = item.status === "drafted";
  const isThankYou = item.kind === "thank_you";

  async function approve() {
    setBusy(true);
    setError("");
    try {
      await approveOutreach(item.id, { recipient_email: recipient, subject, body });
      onChanged();
    } catch (e: any) {
      setError(e.message || "Approve failed");
    } finally {
      setBusy(false);
    }
  }

  async function reject() {
    setBusy(true);
    setError("");
    try {
      await rejectOutreach(item.id);
      onChanged();
    } catch (e: any) {
      setError(e.message || "Reject failed");
    } finally {
      setBusy(false);
    }
  }

  const proposalHref = `/proposals/new?outreach=${item.id}&company=${encodeURIComponent(
    item.company_name
  )}&website=${encodeURIComponent(item.website || "")}`;

  return (
    <Card className="p-6">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-soft text-brand">
            <Building2 size={18} />
          </span>
          <div>
            <div className="flex items-center gap-2">
              <p className="text-sm font-semibold text-text">{item.company_name}</p>
              {isThankYou ? (
                <Badge tone="accent"><Heart size={11} /> Thank-you</Badge>
              ) : (
                <Badge tone="brand">Outreach</Badge>
              )}
            </div>
            <p className="text-xs text-text-muted">From: {SENDER}</p>
          </div>
        </div>
        <StatusBadge status={item.status === "drafted" ? "warning" : item.status === "approved" ? "pass" : "fail"} />
      </div>

      <div className="space-y-3">
        <div>
          <label className="label-caps">To (recipient email)</label>
          <input
            type="email"
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            disabled={!editable}
            placeholder="add the customer's email…"
            className="input mt-1.5 disabled:opacity-70"
          />
        </div>
        <div>
          <label className="label-caps">Subject</label>
          <input
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            disabled={!editable}
            className="input mt-1.5 disabled:opacity-70"
          />
        </div>
        <div>
          <label className="label-caps">Body {editable ? "(edit before approving)" : ""}</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            disabled={!editable}
            className="input mt-1.5 min-h-[150px] resize-y disabled:opacity-70"
          />
        </div>
      </div>

      <ErrorBanner message={error} />

      <div className="mt-4 flex flex-wrap gap-2">
        {editable ? (
          <>
            <button onClick={approve} disabled={busy} className="btn btn-primary">
              <Check size={15} /> {busy ? "Approving…" : "Approve email"}
            </button>
            <button onClick={reject} disabled={busy} className="btn btn-ghost">
              <X size={15} /> Reject
            </button>
          </>
        ) : item.status === "approved" ? (
          isThankYou ? (
            <span className="inline-flex items-center gap-2 rounded-lg bg-ok-soft px-3 py-2 text-sm font-medium text-ok">
              <Send size={14} /> Approved — ready to send
            </span>
          ) : item.proposal_id ? (
            <Link href={`/proposals/${item.proposal_id}`} className="btn btn-primary">
              <FileSignature size={15} /> View proposal <ArrowRight size={14} />
            </Link>
          ) : (
            <Link href={proposalHref} className="btn btn-primary">
              <FileSignature size={15} /> Generate proposal <ArrowRight size={14} />
            </Link>
          )
        ) : (
          <Badge tone="neutral">Rejected</Badge>
        )}
      </div>
    </Card>
  );
}

export default function OutreachPage() {
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    listOutreach()
      .then((d) => setItems(d.outreach || []))
      .catch((e) => setError(e.message || "Failed to load outreach"))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  const pending = items.filter((i) => i.status === "drafted");
  const rest = items.filter((i) => i.status !== "drafted");

  return (
    <div>
      <Topbar
        eyebrow="Human-in-the-loop"
        title="Outreach Approvals"
        subtitle="Nothing is sent automatically. Review and edit each email, approve it, then generate an aligned proposal for the company."
        actions={
          <button onClick={load} className="btn btn-ghost">
            <RefreshCw size={15} /> Refresh
          </button>
        }
      />

      <ErrorBanner message={error} />

      {loading ? (
        <div className="space-y-4">
          {[...Array(2)].map((_, i) => (
            <Card key={i} className="shimmer h-56" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={<MailCheck size={22} />}
          title="No outreach yet"
          hint="Go to Leads, find a company, and draft an outreach email — it will appear here for approval."
        />
      ) : (
        <div className="space-y-6">
          {pending.length > 0 ? (
            <div className="space-y-4">
              <p className="label-caps">Pending approval ({pending.length})</p>
              {pending.map((item) => (
                <OutreachRow key={item.id} item={item} onChanged={load} />
              ))}
            </div>
          ) : null}
          {rest.length > 0 ? (
            <div className="space-y-4">
              <p className="label-caps">Processed</p>
              {rest.map((item) => (
                <OutreachRow key={item.id} item={item} onChanged={load} />
              ))}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
