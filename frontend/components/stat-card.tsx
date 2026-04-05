import { LucideIcon } from "lucide-react";

export default function StatCard({
  title,
  value,
  description,
  icon: Icon,
}: {
  title: string;
  value: string;
  description: string;
  icon: LucideIcon;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
        </div>
        <div className="rounded-2xl bg-gray-100 p-3">
          <Icon size={20} className="text-gray-700" />
        </div>
      </div>
      <p className="mt-3 text-sm text-gray-600">{description}</p>
    </div>
  );
}