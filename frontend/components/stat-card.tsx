import { LucideIcon } from "lucide-react";

export default function StatCard({
  title,
  value,
  description,
  icon: Icon,
  accent = false,
}: {
  title: string;
  value: string;
  description: string;
  icon: LucideIcon;
  accent?: boolean;
}) {
  return (
    <div className="card card-hover p-5">
      <div className="flex items-start justify-between">
        <p className="label-caps">{title}</p>
        <span
          className={`flex h-9 w-9 items-center justify-center rounded-xl ${
            accent ? "bg-brand text-white" : "bg-brand-soft text-brand"
          }`}
        >
          <Icon size={17} />
        </span>
      </div>
      <p className="mt-3 text-3xl font-bold tracking-tight text-text">{value}</p>
      <p className="mt-1.5 text-xs leading-relaxed text-text-muted">{description}</p>
    </div>
  );
}
