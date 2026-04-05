import Topbar from "@/components/topbar";
import StatCard from "@/components/stat-card";
import KpiChart from "@/components/kpi-chart";
import DocumentHistory from "@/components/document-history";
import LatestAgentRun from "@/components/latest-agent-run";
import { BarChart3, Building2, FileText, Workflow } from "lucide-react";
import Link from "next/link";
import { getDocumentHistory, getKpis, getLatestDocument } from "@/lib/api";

export default async function DashboardPage() {
  let kpiData: any = null;
  let historyData: any = null;
  let latestDocumentData: any = null;

  try {
    kpiData = await getKpis();
  } catch {}

  try {
    historyData = await getDocumentHistory();
  } catch {}

  try {
    latestDocumentData = await getLatestDocument();
  } catch {}

  const summary = kpiData?.summary || {};
  const averages = summary?.averages || {};
  const documents = historyData?.documents || [];
  const latestDocument = latestDocumentData?.document || null;
  const latestTrace = latestDocument?.agent_trace || null;

  return (
    <div className="space-y-6">
      <Topbar
        title="Dashboard"
        subtitle="Overview of document intelligence, KPI tracking, agent workflows, and lead generation."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Processed Documents"
          value={String(documents.length || 0)}
          description="Documents recorded in the processing registry."
          icon={FileText}
        />
        <StatCard
          title="Field Coverage"
          value={String(averages.field_coverage ?? "-")}
          description="Average extraction field coverage across processed documents."
          icon={Workflow}
        />
        <StatCard
          title="Schema Validity"
          value={String(averages.schema_validity ?? "-")}
          description="Average validation quality across document outputs."
          icon={BarChart3}
        />
        <StatCard
          title="Latest Agent Loops"
          value={String(latestTrace?.loop_count ?? "-")}
          description="Loop count used by the most recent agent-controlled run."
          icon={Building2}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Link href="/upload" className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
          <h3 className="text-lg font-semibold">Upload & Process</h3>
          <p className="mt-2 text-sm text-gray-600">
            Process procurement, financial, and construction-related documents end to end.
          </p>
        </Link>

        <Link href="/ask" className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
          <h3 className="text-lg font-semibold">Ask Documents</h3>
          <p className="mt-2 text-sm text-gray-600">
            Ask grounded questions over indexed PDFs and document corpora.
          </p>
        </Link>

        <Link href="/kpis" className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
          <h3 className="text-lg font-semibold">KPIs</h3>
          <p className="mt-2 text-sm text-gray-600">
            Inspect extraction coverage, validation quality, and runtime metrics.
          </p>
        </Link>

        <Link href="/leads" className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
          <h3 className="text-lg font-semibold">Leads & Outreach</h3>
          <p className="mt-2 text-sm text-gray-600">
            Discover candidate construction companies and draft controlled outreach emails.
          </p>
        </Link>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <KpiChart entries={kpiData?.entries || []} />
        <LatestAgentRun document={latestDocument} />
      </div>

      <DocumentHistory documents={documents} />
    </div>
  );
}