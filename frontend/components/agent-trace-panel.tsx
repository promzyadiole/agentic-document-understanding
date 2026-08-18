import { Brain } from "lucide-react";
import { Card, SectionTitle, Badge, EmptyState } from "@/components/ui";

export default function AgentTracePanel({ trace }: { trace: any }) {
  const history = trace?.history || [];

  return (
    <Card className="p-6">
      <SectionTitle title="Agent reasoning trace" hint="Every decision the controller made, in order." />
      {history.length === 0 ? (
        <EmptyState icon={<Brain size={22} />} title="No trace available" hint="Process a document to record a reasoning trace." />
      ) : (
        <ol className="relative space-y-0 border-l border-border pl-6">
          {history.map((item: any, idx: number) => {
            const isAgent = true;
            return (
              <li key={idx} className="relative pb-5 last:pb-0">
                <span className="absolute -left-[2.15rem] flex h-7 w-7 items-center justify-center rounded-full border border-brand-soft bg-brand-soft text-brand">
                  <Brain size={13} />
                </span>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone="neutral">loop {item.loop_count ?? idx + 1}</Badge>
                  <Badge tone="accent">→ {item.action || "unknown"}</Badge>
                </div>
                {isAgent && item.reasoning ? (
                  <p className="mt-1.5 text-xs italic leading-relaxed text-text-muted">“{item.reasoning}”</p>
                ) : null}
              </li>
            );
          })}
        </ol>
      )}
    </Card>
  );
}
