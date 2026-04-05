import Topbar from "@/components/topbar";
import UploadForm from "@/components/upload-form";

export default function UploadPage() {
  return (
    <div className="space-y-6">
      <Topbar
        title="Upload & Process"
        subtitle="Upload PDFs or images and run the LangGraph-powered document workflow."
      />
      <UploadForm />
    </div>
  );
}