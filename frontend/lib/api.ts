const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function handleResponse(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    // Prefer FastAPI's { "detail": "..." } message over the raw JSON body.
    let message = text || "Request failed";
    try {
      const parsed = JSON.parse(text);
      if (parsed?.detail) {
        message = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
      }
    } catch {
      /* not JSON — keep raw text */
    }
    throw new Error(message);
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

// --- Firm profile (Proziem) ---
export async function getAgencyProfile() {
  const res = await fetch(`${API_BASE}/proposals/agency/profile`, { cache: "no-store" });
  return handleResponse(res);
}

// --- Outreach approval flow ---
export async function listOutreach() {
  const res = await fetch(`${API_BASE}/outreach`, { cache: "no-store" });
  return handleResponse(res);
}

export async function createOutreach(payload: {
  company_name: string;
  company_summary?: string;
  website?: string;
  location?: string;
  recipient_email?: string;
}) {
  const res = await fetch(`${API_BASE}/outreach`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function approveOutreach(id: string, payload: { recipient_email?: string; subject?: string; body?: string }) {
  const res = await fetch(`${API_BASE}/outreach/${id}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function rejectOutreach(id: string) {
  const res = await fetch(`${API_BASE}/outreach/${id}/reject`, { method: "POST" });
  return handleResponse(res);
}

// --- Proposals ---
export async function listProposals() {
  const res = await fetch(`${API_BASE}/proposals`, { cache: "no-store" });
  return handleResponse(res);
}

export async function generateProposal(payload: {
  company_name: string;
  website?: string;
  price_cents?: number;
  currency?: string;
  brief?: string;
  outreach_id?: string;
}) {
  const res = await fetch(`${API_BASE}/proposals/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function getProposal(id: string) {
  const res = await fetch(`${API_BASE}/proposals/${id}`, { cache: "no-store" });
  return handleResponse(res);
}

export async function getProposalByToken(token: string) {
  const res = await fetch(`${API_BASE}/proposals/token/${token}`, { cache: "no-store" });
  return handleResponse(res);
}

// --- Revenue & payments ---
export async function registerPayment(payload: {
  proposal_id?: string;
  company_name?: string;
  amount_cents: number;
  currency?: string;
}) {
  const res = await fetch(`${API_BASE}/revenue/payments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function listPayments() {
  const res = await fetch(`${API_BASE}/revenue/payments`, { cache: "no-store" });
  return handleResponse(res);
}

/** Confirm a payment; the returned proposal PDF is run through the document workflow. */
export async function confirmPayment(id: string) {
  const res = await fetch(`${API_BASE}/revenue/payments/${id}/confirm`, { method: "POST" });
  return handleResponse(res);
}

export async function getRevenueSummary() {
  const res = await fetch(`${API_BASE}/revenue/summary`, { cache: "no-store" });
  return handleResponse(res);
}

// --- Contact (inbound from the landing page) ---
export async function submitContact(payload: {
  name: string;
  email: string;
  company?: string;
  message: string;
}) {
  const res = await fetch(`${API_BASE}/contact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function listInbound() {
  const res = await fetch(`${API_BASE}/contact/inbound`, { cache: "no-store" });
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

export type StreamEvent = {
  type: "start" | "node" | "done" | "error";
  node?: string;
  label?: string;
  agent_action?: string | null;
  agent_reasoning?: string | null;
  steps_taken?: string[];
  loop_count?: number | null;
  filename?: string;
  result?: any;
  detail?: string;
};

/**
 * Upload a document and receive live Server-Sent Events as the LangGraph
 * agent reasons through the workflow. `onEvent` fires for every event.
 */
export async function uploadDocumentStream(
  file: File,
  onEvent: (event: StreamEvent) => void,
  projectId?: string
): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);

  const url = projectId
    ? `${API_BASE}/documents/upload/stream?project_id=${encodeURIComponent(projectId)}`
    : `${API_BASE}/documents/upload/stream`;

  const res = await fetch(url, { method: "POST", body: formData });
  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    throw new Error(text || "Streaming upload failed");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const frames = buffer.split("\n\n");
    buffer = frames.pop() || "";
    for (const frame of frames) {
      const line = frame.trim();
      if (!line.startsWith("data:")) continue;
      const json = line.slice(5).trim();
      if (!json) continue;
      try {
        onEvent(JSON.parse(json) as StreamEvent);
      } catch {
        /* ignore malformed frame */
      }
    }
  }
}