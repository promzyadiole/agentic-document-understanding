"use client";

import { useEffect, useState } from "react";
import Topbar from "@/components/topbar";
import StatCard from "@/components/stat-card";
import KpiChart from "@/components/kpi-chart";
import DocumentHistory from "@/components/document-history";
import LatestAgentRun from "@/components/latest-agent-run";
import { ErrorBanner } from "@/components/ui";
import { BarChart3, DollarSign, FileText, Workflow, Upload, MessageSquareText, ArrowRight, Building2 } from "lucide-react";
import Link from "next/link";
import { getDocumentHistory, getKpis, getLatestDocument, getRevenueSummary } from "@/lib/api";

const QUICK_LINKS = [
  { href: "/upload", label: "Upload & Process", desc: "Run the agent pipeline on a document", icon: Upload },
  { href: "/ask", label: "Ask Documents", desc: "Grounded Q&A with citations", icon: MessageSquareText },
  { href: "/kpis", label: "KPIs", desc: "Extraction & validation quality", icon: BarChart3 },
  { href: "/leads", label: "Leads & Outreach", desc: "Discover companies, draft emails", icon: Building2 },
];

export default function DashboardPage() {
  const [kpiData, setKpiData] = useState<any>(null);
  const [historyData, setHistoryData] = useState<any>(null);
  const [latestDocumentData, setLatestDocumentData] = useState<any>(null);
  const [revenue, setRevenue] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const [kpis, history, latest, rev] = await Promise.all([
          getKpis().catch(() => null),
          getDocumentHistory().catch(() => null),
          getLatestDocument().catch(() => null),
          getRevenueSummary().catch(() => null),
        ]);
        setKpiData(kpis);
        setHistoryData(history);
        setLatestDocumentData(latest);
        setRevenue(rev);
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard data");
      }
    }
    loadData();
  }, []);

  const money = (cents: any) => {
    try {
      return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format((Number(cents) || 0) / 100);
    } catch {
      return "$0";
    }
  };

  const averages = kpiData?.summary?.averages || {};
  const documents = historyData?.documents || [];
  const latestDocument = latestDocumentData?.document || null;
  const latestTrace = latestDocument?.agent_trace || null;

  const pct = (v: any) => (v == null ? "—" : `${Math.round(Number(v) * 100)}%`);

  return (
    <div>
      <Topbar
        eyebrow="Overview"
        title="Dashboard"
        subtitle="Document intelligence, agent workflows, quality metrics, and lead generation at a glance."
      />

      <ErrorBanner message={error} />

      <div className="mt-2 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Revenue" value={money(revenue?.total_revenue_cents)} description={`${revenue?.confirmed_count ?? 0} confirmed · ${revenue?.pending_count ?? 0} pending`} icon={DollarSign} accent />
        <StatCard title="Processed Documents" value={String(documents.length || 0)} description="Recorded in the processing registry." icon={FileText} />
        <StatCard title="Field Coverage" value={pct(averages.field_coverage)} description="Avg. share of fields extracted." icon={Workflow} />
        <StatCard title="Schema Validity" value={pct(averages.schema_validity)} description="Avg. validation quality." icon={BarChart3} />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {QUICK_LINKS.map((l) => {
          const Icon = l.icon;
          return (
            <Link key={l.href} href={l.href} className="card card-hover group flex items-center gap-3 p-4">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-soft text-brand">
                <Icon size={18} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-text">{l.label}</p>
                <p className="truncate text-xs text-text-muted">{l.desc}</p>
              </div>
              <ArrowRight size={16} className="text-text-faint transition group-hover:translate-x-0.5 group-hover:text-brand" />
            </Link>
          );
        })}
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        <KpiChart entries={kpiData?.entries || []} />
        <LatestAgentRun document={latestDocument} />
      </div>

      <div className="mt-6">
        <DocumentHistory documents={documents} />
      </div>
    </div>
  );
}
