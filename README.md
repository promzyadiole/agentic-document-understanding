🏗️ ConstructionFlow AI
Agentic Document Intelligence for Construction & Procurement




🧭 TL;DR

ConstructionFlow AI is a production-grade agentic system that:

🧠 reasons over documents using LLM-driven loops
🔎 retrieves knowledge via RAG (Pinecone)
📄 extracts structured data from unstructured PDFs
📊 evaluates itself via KPI metrics
🎯 generates real-world business outputs (leads & emails)

👉 This is not a pipeline — it is an AI agent system that thinks, acts, and improves.

🚀 Why This Project Exists

Real-world documents (contracts, invoices, procurement reports) are:

unstructured
inconsistent
noisy
context-dependent

Traditional systems fail because they:

follow rigid pipelines
cannot adapt
cannot self-correct
💡 This system solves that by introducing:

Agentic reasoning loops over document workflows

Instead of:

parse → extract → done ❌

We do:

analyze → decide → act → evaluate → retry → finalize ✅
🧠 Core Innovation: Agentic Loop
🔁 The Brain of the System (LangGraph)

The system is built around a reasoning loop:

START
  ↓
document_intake
  ↓
clean_text
  ↓
classify_document
  ↓
🧠 AGENT LOOP:
    - analyze state
    - decide next action
    - call tool
    - evaluate result
    - repeat if needed
  ↓
extract_fields
  ↓
validate_document
  ↓
index_document
  ↓
log_kpis
  ↓
END
🧠 What makes it "Agentic"?

The agent:

dynamically selects tools
decides when extraction is sufficient
retries on low confidence
validates its own outputs
stops based on reasoning (not fixed rules)
🧩 System Capabilities
📄 Document Intelligence
OCR (scanned PDFs/images)
semantic parsing
metadata enrichment
🔎 Retrieval-Augmented Generation (RAG)
vector indexing (Pinecone)
semantic search
grounded answers
📊 KPI Self-Evaluation
field coverage
schema validity
extraction accuracy
agent loop efficiency
🧲 Lead Generation
company discovery (LLM + search)
context-aware email drafting
human-in-the-loop (HITL)
🧠 Explainability
full agent trace
tool usage logs
reasoning visibility
🏗️ Architecture Breakdown
Backend (AI Engine)
FastAPI → API layer
LangGraph → agent orchestration
LangChain → tool abstraction
Pinecone → vector DB
Tesseract → OCR
Pydantic → schema validation
Frontend (Control Panel)
Next.js (App Router)
TailwindCSS UI
Recharts (KPI visualization)
Infrastructure
Vercel (Frontend + Serverless backend)
Python 3.12
uv (fast dependency resolution)
📂 Project Structure
agentic-document-understanding/
│
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── services/     # OCR, extraction, validation
│   │   ├── workflows/    # LangGraph agent logic
│   │   ├── models/       # schemas
│   │   └── core/         # config
│   │
│   └── api/main.py       # Vercel entrypoint
│
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── upload/
│   │   ├── ask/
│   │   ├── kpis/
│   │   ├── leads/
│   │   └── graph/
│   │
│   ├── components/
│   └── lib/api.ts
│
└── agentic-doc.png
🧠 How the Agent Thinks (Critical Section)

Each run produces a trace like this:

{
  "loop": 1,
  "decision": "Extract financial fields",
  "tool": "extract_financial_data",
  "confidence": 0.72
}
{
  "loop": 2,
  "decision": "Validate extraction",
  "result": "schema mismatch",
  "action": "retry extraction"
}
{
  "loop": 3,
  "decision": "Finalize",
  "confidence": 0.94
}

👉 This enables:

debugging AI decisions
measuring reasoning quality
improving system behavior
📊 KPI System
Why KPIs matter

Most AI systems don’t measure themselves.

This one does.

Metrics
Metric	Meaning
Field Coverage	% of extracted fields
Extraction Accuracy	correctness of outputs
Schema Validity	structural correctness
Loop Count	reasoning efficiency
Example
field_coverage = filled_fields / total_fields
accuracy = correct_fields / extracted_fields
🔌 API Overview
Documents
POST /documents/upload
GET /documents/history
Query
POST /query
KPIs
GET /kpis
Leads
POST /leads/search
POST /leads/draft-email
Graph
GET /graph/export
🖥️ UI Overview
Page	Purpose
Dashboard	system overview
Upload	document ingestion
Ask Docs	RAG querying
KPIs	evaluation metrics
Leads	outreach generation
Graph	agent visualization
⚙️ Local Setup
git clone https://github.com/promzyadiole/agentic-document-understanding.git
cd agentic-document-understanding
Backend
cd backend
uv venv
source .venv/bin/activate
uv sync
uvicorn app.main:app --reload
Frontend
cd frontend
npm install
npm run dev
🔑 Environment Variables
OPENAI_API_KEY=
PINECONE_API_KEY=
INDEX_NAME=

TAVILY_API_KEY=
LANGSMITH_API_KEY=

OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
🚀 Deployment Strategy
Frontend
Vercel
Root: frontend
Backend
Vercel serverless
Root: backend
Entry: api/main.py
Python: 3.12
⚠️ Known Limitations
Tesseract may require custom deployment
File system is ephemeral on Vercel
Large document processing can be slow
Pinecone index must be pre-configured
🔮 Future Work

Real-world LLM orchestration

RAG + tool usage integration

Explainability & evaluation

Full-stack AI product engineering

👤 Author

Promise Adiole

⭐ Final Note

This project is not about calling an LLM.

It is about building a system that thinks.
