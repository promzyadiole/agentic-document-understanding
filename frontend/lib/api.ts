const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function handleResponse(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Request failed");
  }
  return res.json();
}

export async function getKpis() {
  const res = await fetch(`${API_BASE}/kpis`, { cache: "no-store" });
  return handleResponse(res);
}

export async function getDocumentHistory() {
  const res = await fetch(`${API_BASE}/documents/history`, { cache: "no-store" });
  return handleResponse(res);
}

export async function getLatestDocument() {
  const res = await fetch(`${API_BASE}/documents/latest`, { cache: "no-store" });
  return handleResponse(res);
}

export async function askQuestion(payload: {
  question: string;
  project_id?: string;
  document_ids?: string[];
  top_k?: number;
}) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function searchLeads(payload: {
  query: string;
  max_results?: number;
  location_hint?: string;
}) {
  const res = await fetch(`${API_BASE}/leads/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function draftEmail(payload: {
  company_name: string;
  company_summary: string;
  website?: string;
  location?: string;
  recipient_email?: string;
}) {
  const res = await fetch(`${API_BASE}/leads/draft-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function exportGraph() {
  const res = await fetch(`${API_BASE}/graph/export`, { cache: "no-store" });
  return handleResponse(res);
}

export async function uploadDocument(file: File, projectId?: string) {
  const formData = new FormData();
  formData.append("file", file);

  const url = projectId
    ? `${API_BASE}/documents/upload?project_id=${encodeURIComponent(projectId)}`
    : `${API_BASE}/documents/upload`;

  const res = await fetch(url, {
    method: "POST",
    body: formData,
  });

  return handleResponse(res);
}