"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Upload,
  MessageSquareText,
  BarChart3,
  Building2,
  Workflow,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/ask", label: "Ask Docs", icon: MessageSquareText },
  { href: "/kpis", label: "KPIs", icon: BarChart3 },
  { href: "/leads", label: "Leads", icon: Building2 },
  { href: "/graph", label: "Graph", icon: Workflow },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-72 shrink-0 border-r border-gray-200 bg-white lg:block">
      <div className="p-6">
        <div className="rounded-2xl bg-black p-5 text-white">
          <h1 className="text-2xl font-bold">ConstructionFlow AI</h1>
          <p className="mt-2 text-sm text-gray-300">
            Agentic document understanding for construction intelligence.
          </p>
        </div>
      </div>

      <nav className="space-y-1 px-4 pb-6">
        {navItems.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                active
                  ? "bg-gray-900 text-white shadow-sm"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}