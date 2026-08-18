import Topbar from "@/components/topbar";
import UploadForm from "@/components/upload-form";

export default function UploadPage() {
  return (
    <div>
      <Topbar
        eyebrow="Ingest"
        title="Upload & Process"
        subtitle="Drop a document and watch the LangGraph agent reason through parsing, extraction, validation, and indexing — live."
      />
      <UploadForm />
    </div>
  );
}