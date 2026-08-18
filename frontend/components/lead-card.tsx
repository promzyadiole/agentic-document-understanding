"use client";

import { Building2, ExternalLink, Mail, MapPin, AtSign } from "lucide-react";
import { Badge } from "@/components/ui";

export default function LeadCard({
  lead,
  onDraft,
  drafting = false,
}: {
  lead: any;
  onDraft: (lead: any) => void;
  drafting?: boolean;
}) {
  const score = Number(lead.relevance_score || 0);
  const tone = score >= 0.75 ? "ok" : score >= 0.5 ? "warn" : "neutral";

  return (
    <div className="card card-hover flex flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">
            <Building2 size={18} />
          </span>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-text">{lead.company_name}</h3>
            {lead.location ? (
              <p className="mt-0.5 flex items-center gap-1 text-xs text-text-muted">
                <MapPin size={11} /> {lead.location}
              </p>
            ) : null}
          </div>
        </div>
        <Badge tone={tone as any}>{Math.round(score * 100)}% fit</Badge>
      </div>

      <p className="mt-4 line-clamp-4 text-sm leading-relaxed text-text-muted">{lead.summary}</p>

      <div className="mt-3 space-y-1">
        {lead.website ? (
          <a
            href={lead.website.startsWith("http") ? lead.website : `https://${lead.website}`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 truncate text-xs font-medium text-brand hover:text-brand-strong"
          >
            <ExternalLink size={12} className="shrink-0" /> <span className="truncate">{lead.website}</span>
          </a>
        ) : null}
        {lead.email ? (
          <p className="flex items-center gap-1 text-xs text-text-muted">
            <AtSign size={12} className="shrink-0 text-ok" /> {lead.email}
          </p>
        ) : (
          <p className="flex items-center gap-1 text-xs text-text-faint">
            <AtSign size={12} className="shrink-0" /> no public email found
          </p>
        )}
      </div>

      {Array.isArray(lead.evidence) && lead.evidence.length > 0 ? (
        <ul className="mt-4 space-y-1.5">
          {lead.evidence.slice(0, 3).map((item: string, idx: number) => (
            <li key={idx} className="flex gap-2 text-xs text-text-muted">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-brand" />
              {item}
            </li>
          ))}
        </ul>
      ) : null}

      <button
        onClick={() => onDraft(lead)}
        disabled={drafting}
        className="btn btn-ghost mt-5 w-full"
      >
        <Mail size={15} /> {drafting ? "Drafting…" : "Draft outreach for approval"}
      </button>
    </div>
  );
}
