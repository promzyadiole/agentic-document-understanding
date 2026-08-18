import { CheckCircle2, Boxes } from "lucide-react";

const STEP_TITLES = ["Discovery call", "Proposal", "Project", "Ongoing support"];

function formatPrice(cents: number, currency: string) {
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: (currency || "usd").toUpperCase(), maximumFractionDigits: 0 }).format(
      (cents || 0) / 100
    );
  } catch {
    return `${((cents || 0) / 100).toFixed(0)} ${currency?.toUpperCase() || "USD"}`;
  }
}

export default function ProposalView({ proposal }: { proposal: any }) {
  const c = proposal?.content || {};
  const hero = c.hero || {};
  const deliverables = c.deliverables || [];
  const process = c.process || [];

  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-surface">
      {/* Hero */}
      <div className="relative border-b border-border bg-gradient-to-br from-brand-soft to-transparent px-6 py-12 sm:px-10 sm:py-16">
        <div className="flex items-center gap-2 text-brand-strong">
          <Boxes size={18} />
          <span className="text-sm font-bold">Proziem Digital Global</span>
        </div>
        {hero.eyebrow ? <p className="label-caps mt-6 text-brand">{hero.eyebrow}</p> : null}
        <h1 className="mt-2 max-w-3xl text-3xl font-bold leading-tight tracking-tight text-text sm:text-5xl">
          {hero.headline}
        </h1>
        {hero.subheadline ? (
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted sm:text-lg">{hero.subheadline}</p>
        ) : null}
      </div>

      <div className="space-y-12 px-6 py-10 sm:px-10">
        {/* Deliverables */}
        {deliverables.length ? (
          <section>
            <p className="label-caps text-brand">What you get</p>
            <h2 className="mt-1 text-xl font-bold text-text">Deliverables</h2>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {deliverables.map((d: any, i: number) => (
                <div key={i} className="rounded-xl border border-border bg-surface-2 p-5">
                  <div className="flex items-start gap-2.5">
                    <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-brand" />
                    <div>
                      <h3 className="text-sm font-semibold text-text">{d.title}</h3>
                      <p className="mt-1 text-sm leading-relaxed text-text-muted">{d.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* Process */}
        {process.length ? (
          <section>
            <p className="label-caps text-brand">How we work</p>
            <h2 className="mt-1 text-xl font-bold text-text">Process</h2>
            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {process.map((s: any, i: number) => (
                <div key={i} className="rounded-xl border border-border bg-surface-2 p-5">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-sm font-bold text-white">
                    {i + 1}
                  </span>
                  <h3 className="mt-3 text-sm font-semibold text-text">{STEP_TITLES[i] || `Step ${i + 1}`}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-text-muted">{s.description}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* Pricing */}
        <section className="rounded-2xl border border-border bg-surface-2 p-6 sm:p-8">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="label-caps text-brand">Investment</p>
              <p className="mt-2 text-4xl font-bold text-text">
                {formatPrice(proposal.price_cents, proposal.currency)}
              </p>
            </div>
          </div>
          {c.pricing_framing ? (
            <p className="mt-4 max-w-3xl text-sm leading-relaxed text-text-muted">{c.pricing_framing}</p>
          ) : null}
        </section>

        {/* Terms */}
        {c.scope_summary ? (
          <section>
            <p className="label-caps text-brand">Scope &amp; terms</p>
            <h2 className="mt-1 text-xl font-bold text-text">The engagement</h2>
            <p className="mt-4 max-w-3xl text-sm leading-relaxed text-text-muted">{c.scope_summary}</p>
            <p className="mt-4 max-w-3xl text-xs leading-relaxed text-text-faint">
              Payment is due upon signing unless otherwise agreed in writing. Work begins once payment is received.
              Either party may cancel with written notice; work completed to date will be invoiced accordingly.
            </p>
          </section>
        ) : null}
      </div>

      <div className="border-t border-border px-6 py-6 text-center text-xs text-text-faint sm:px-10">
        Prepared by Proziem Digital Global · promzy007adiole@yahoo.com
      </div>
    </div>
  );
}
