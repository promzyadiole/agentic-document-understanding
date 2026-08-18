import type { ReactNode } from "react";

type Tone = "brand" | "ok" | "warn" | "danger" | "neutral" | "accent";

const toneClasses: Record<Tone, string> = {
  brand: "bg-brand-soft text-brand-strong",
  ok: "bg-ok-soft text-ok",
  warn: "bg-warn-soft text-warn",
  danger: "bg-danger-soft text-danger",
  accent: "bg-accent-soft text-accent",
  neutral: "bg-surface-2 text-text-muted",
};

export function Badge({
  children,
  tone = "neutral",
  className = "",
}: {
  children: ReactNode;
  tone?: Tone;
  className?: string;
}) {
  return <span className={`chip ${toneClasses[tone]} ${className}`}>{children}</span>;
}

export function StatusBadge({ status }: { status?: string | null }) {
  const s = (status || "").toLowerCase();
  const tone: Tone = s === "pass" ? "ok" : s === "warning" ? "warn" : s === "fail" ? "danger" : "neutral";
  const label = status ? status.toUpperCase() : "—";
  return <Badge tone={tone}>{label}</Badge>;
}

export function ConfidenceBadge({ score }: { score?: number | null }) {
  if (score == null) return <Badge tone="neutral">n/a</Badge>;
  const tone: Tone = score >= 0.85 ? "ok" : score >= 0.65 ? "warn" : "danger";
  return <Badge tone={tone}>{Math.round(score * 100)}%</Badge>;
}

export function Card({
  children,
  className = "",
  hover = false,
}: {
  children?: ReactNode;
  className?: string;
  hover?: boolean;
}) {
  return <div className={`card ${hover ? "card-hover" : ""} ${className}`}>{children}</div>;
}

export function SectionTitle({
  title,
  hint,
  right,
}: {
  title: string;
  hint?: string;
  right?: ReactNode;
}) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4">
      <div>
        <h3 className="text-base font-semibold text-text">{title}</h3>
        {hint ? <p className="mt-0.5 text-sm text-text-muted">{hint}</p> : null}
      </div>
      {right}
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  hint,
}: {
  icon?: ReactNode;
  title: string;
  hint?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border-strong bg-surface-2 px-6 py-12 text-center">
      {icon ? <div className="mb-3 text-text-faint">{icon}</div> : null}
      <p className="text-sm font-medium text-text">{title}</p>
      {hint ? <p className="mt-1 max-w-sm text-sm text-text-muted">{hint}</p> : null}
    </div>
  );
}

export function ErrorBanner({ message }: { message?: string }) {
  if (!message) return null;
  return (
    <div className="rounded-xl border border-danger-soft bg-danger-soft px-4 py-3 text-sm text-danger">
      {message}
    </div>
  );
}
