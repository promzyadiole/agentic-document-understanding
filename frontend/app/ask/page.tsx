import Topbar from "@/components/topbar";
import QueryForm from "@/components/query-form";

export default function AskPage() {
  return (
    <div className="space-y-6">
      <Topbar
        title="Ask Documents"
        subtitle="Run grounded retrieval over indexed financial and construction document corpora."
      />
      <QueryForm />
    </div>
  );
}