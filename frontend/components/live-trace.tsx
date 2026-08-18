"use client";

import {
  Brain,
  FileSearch,
  Sparkles,
  Tags,
  Database,
  ListChecks,
  ShieldCheck,
  Gauge,
  Flag,
  Loader2,
} from "lucide-react";
import type { StreamEvent } from "@/lib/api";

const NODE_ICON: Record<string, any> = {
  document_intake: FileSearch,
  agent_reason: Brain,
  clean_text: Sparkles,
  classify_document: Tags,
  index_document: Database,
  extract_fields: ListChecks,
  validate_document: ShieldCheck,
  log_kpis: Gauge,
};

export default function LiveTrace({
  events,
  running,
}: {
  events: StreamEvent[];
  running: boolean;
}) {
  const nodeEvents = events.filter((e) => e.type === "node");

  return (
    <div className="relative">
      <div className="mb-4 flex items-center gap-2">
        <span
          className={`flex h-6 w-6 items-center justify-center rounded-full ${
            running ? "bg-brand-soft text-brand" : "bg-ok-soft text-ok"
          }`}
        >
          {running ? (
            <Loader2 size={13} className="animate-spin" />
          ) : (
            <Flag size={13} />
          )}
        </span>
        <p className="text-sm font-semibold text-text">
          {running ? "Agent reasoning live…" : "Agent run complete"}
        </p>
      </div>

      <ol className="relative space-y-0 border-l border-border pl-6">
        {nodeEvents.map((e, i) => {
          const Icon = NODE_ICON[e.node || ""] || Brain;
          const isAgent = e.node === "agent_reason";
          const isLast = i === nodeEvents.length - 1;
          const active = running && isLast;
          return (
            <li key={i} className="relative animate-fade-up pb-5 last:pb-0">
              <span
                className={`absolute -left-[2.15rem] flex h-7 w-7 items-center justify-center rounded-full border ${
                  active
                    ? "border-brand bg-brand text-white"
                    : isAgent
                    ? "border-brand-soft bg-brand-soft text-brand"
                    : "border-border bg-surface text-text-muted"
                }`}
              >
                <Icon size={13} className={active ? "animate-pulse-dot" : ""} />
              </span>
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                <p className="text-sm font-medium text-text">{e.label || e.node}</p>
                {e.loop_count != null ? (
                  <span className="chip bg-surface-2 text-text-faint">loop {e.loop_count}</span>
                ) : null}
                {isAgent && e.agent_action ? (
                  <span className="chip bg-accent-soft text-accent">→ {e.agent_action}</span>
                ) : null}
              </div>
              {isAgent && e.agent_reasoning ? (
                <p className="mt-1 text-xs italic leading-relaxed text-text-muted">
                  “{e.agent_reasoning}”
                </p>
              ) : null}
            </li>
          );
        })}
        {!nodeEvents.length ? (
          <li className="text-sm text-text-muted">Waiting for the first reasoning step…</li>
        ) : null}
      </ol>
    </div>
  );
}
