"use client";

import { useEffect, useState } from "react";
import { Inbox, RefreshCw, Mail, FileText, Zap } from "lucide-react";
import Topbar from "@/components/topbar";
import { Card, ErrorBanner, Badge, EmptyState } from "@/components/ui";
import { listInbound } from "@/lib/api";

const CATEGORY_TONE: Record<string, any> = {
  new_business: "ok",
  proposal_reply: "brand",
  payment: "accent",
  support: "warn",
  partnership: "brand",
  recruitment: "neutral",
  spam: "danger",
  other: "neutral",
};

function label(s?: string) {
  return (s || "other").replace(/_/g, " ");
}

export default function InboxPage() {
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    listInbound()
      .then((d) => setItems((d.inbound || []).slice().reverse()))
      .catch((e) => setError(e.message || "Failed to load inbox"))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  return (
    <div>
      <Topbar
        eyebrow="Triage"
        title="Inbox"
        subtitle="Inbound messages from your Contact page, auto-classified for fast tracking and action — and each one runs through the document workflow."
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
            <Card key={i} className="shimmer h-32" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={<Inbox size={22} />}
          title="No inbound messages yet"
          hint="Messages from the Contact Us form on your landing page appear here, classified and ready to action."
        />
      ) : (
        <div className="space-y-4">
          {items.map((m) => {
            const cls = m.classification || {};
            return (
              <Card key={m.id} className="p-6">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-soft text-brand">
                      <Mail size={18} />
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-text">
                        {m.name} {m.company ? <span className="text-text-muted">· {m.company}</span> : null}
                      </p>
                      <p className="text-xs text-text-faint">{m.email}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5">
                    <Badge tone={CATEGORY_TONE[cls.category] || "neutral"}>{label(cls.category)}</Badge>
                    <Badge tone={cls.priority === "high" ? "danger" : cls.priority === "low" ? "neutral" : "warn"}>
                      {cls.priority || "medium"} priority
                    </Badge>
                  </div>
                </div>

                {cls.summary ? <p className="mt-4 text-sm text-text">{cls.summary}</p> : null}
                <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-text-muted">{m.message}</p>

                <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-border pt-3">
                  {cls.suggested_action ? (
                    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-brand">
                      <Zap size={13} /> {cls.suggested_action}
                    </span>
                  ) : null}
                  {m.document_id ? (
                    <span className="inline-flex items-center gap-1 text-xs text-text-muted">
                      <FileText size={12} className="text-ok" /> processed through workflow
                    </span>
                  ) : null}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
