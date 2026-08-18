import Topbar from "@/components/topbar";
import QueryForm from "@/components/query-form";

export default function AskPage() {
  return (
    <div>
      <Topbar
        eyebrow="Retrieval"
        title="Ask Documents"
        subtitle="Grounded retrieval over your indexed corpus — answers are built only from retrieved chunks and cite their sources."
      />
      <QueryForm />
    </div>
  );
}