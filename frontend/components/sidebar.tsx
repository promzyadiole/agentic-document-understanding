"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  Upload,
  MessageSquareText,
  BarChart3,
  Building2,
  Workflow,
  Menu,
  X,
  Boxes,
  MailCheck,
  FileSignature,
  DollarSign,
  Inbox,
} from "lucide-react";
import ThemeToggle from "@/components/theme-toggle";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, desc: "Overview" },
  { href: "/upload", label: "Upload", icon: Upload, desc: "Process a document" },
  { href: "/ask", label: "Ask Docs", icon: MessageSquareText, desc: "Grounded Q&A" },
  { href: "/kpis", label: "KPIs", icon: BarChart3, desc: "Quality metrics" },
  { href: "/inbox", label: "Inbox", icon: Inbox, desc: "Classified inbound" },
  { href: "/leads", label: "Leads", icon: Building2, desc: "Discover & outreach" },
  { href: "/outreach", label: "Approvals", icon: MailCheck, desc: "Approve emails" },
  { href: "/proposals", label: "Proposals", icon: FileSignature, desc: "Generate & send" },
  { href: "/revenue", label: "Revenue", icon: DollarSign, desc: "Payments & income" },
  { href: "/graph", label: "Graph", icon: Workflow, desc: "Agent workflow" },
];

function NavList({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  return (
    <nav className="space-y-1">
      {navItems.map((item) => {
        const active = pathname === item.href;
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
              active
                ? "bg-brand-soft text-brand-strong"
                : "text-text-muted hover:bg-surface-2 hover:text-text"
            }`}
          >
            <span
              className={`flex h-8 w-8 items-center justify-center rounded-lg transition ${
                active ? "bg-brand text-white" : "bg-surface-2 text-text-muted group-hover:text-text"
              }`}
            >
              <Icon size={16} />
            </span>
            <span className="flex flex-col leading-tight">
              <span>{item.label}</span>
              <span className="text-[0.68rem] font-normal text-text-faint">{item.desc}</span>
            </span>
          </Link>
        );
      })}
    </nav>
  );
}

function Brand() {
  return (
    <Link href="/" className="flex items-center gap-3">
      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-strong text-white shadow-lg">
        <Boxes size={20} />
      </span>
      <div className="leading-tight">
        <p className="text-sm font-bold text-text">ConstructionFlow</p>
        <p className="text-[0.7rem] text-text-faint">by Proziem Digital Global</p>
      </div>
    </Link>
  );
}

export default function Sidebar() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Mobile top bar */}
      <div className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-surface/80 px-4 py-3 backdrop-blur lg:hidden">
        <Brand />
        <button className="btn btn-ghost !px-3" onClick={() => setOpen(true)} aria-label="Open menu">
          <Menu size={18} />
        </button>
      </div>

      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-72 border-r border-border bg-surface p-5">
            <div className="mb-6 flex items-center justify-between">
              <Brand />
              <button className="btn btn-ghost !px-3" onClick={() => setOpen(false)} aria-label="Close menu">
                <X size={18} />
              </button>
            </div>
            <NavList onNavigate={() => setOpen(false)} />
            <div className="mt-6">
              <ThemeToggle />
            </div>
          </aside>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen w-72 shrink-0 flex-col border-r border-border bg-surface/70 p-5 backdrop-blur lg:flex">
        <div className="mb-8">
          <Brand />
        </div>
        <NavList />
        <div className="mt-auto space-y-4 pt-6">
          <div className="card p-4">
            <p className="label-caps">Powered by</p>
            <p className="mt-1.5 text-xs leading-relaxed text-text-muted">
              LangGraph · LangChain · FastAPI · Pinecone · Next.js
            </p>
          </div>
          <ThemeToggle />
        </div>
      </aside>
    </>
  );
}
