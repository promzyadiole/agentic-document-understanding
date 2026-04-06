🏗️ ConstructionFlow AI
Agentic Document Intelligence for Construction & Procurement




🧭 TL;DR

ConstructionFlow AI is a production-grade agentic document intelligence system that:

reasons over documents using LLM-driven loops
retrieves knowledge through RAG with Pinecone
extracts structured data from unstructured PDFs
evaluates itself with KPI metrics
generates real-world business outputs such as lead discovery and outreach drafts

This is not a fixed pipeline.
It is an AI system that can reason, act, validate, and improve.

🚀 Why This Project Exists

Real-world business documents such as:

contracts
invoices
procurement reports
financial statements

are often:

unstructured
inconsistent
noisy
context-dependent

Traditional automation systems struggle because they:

follow rigid pipelines
cannot adapt to ambiguity
cannot self-correct when confidence is low
💡 Core idea

This project solves that by introducing:

Agentic reasoning loops over document workflows

Instead of:

parse → extract → done

it uses:

analyze → decide → act → evaluate → retry → finalize
🧠 Core Innovation: Agentic Loop
🔁 The Brain of the System

The system is built around a LangGraph-powered reasoning loop:

START
  ↓
document_intake
  ↓
clean_text
  ↓
classify_document
  ↓
AGENT LOOP:
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
What makes it truly agentic?

The agent can:

dynamically select tools
decide when extraction is sufficient
retry when confidence is low
validate its own outputs
stop based on reasoning instead of fixed rules
🧩 System Capabilities
📄 Document Intelligence
OCR for scanned PDFs and images
semantic parsing
metadata enrichment
🔎 Retrieval-Augmented Generation
vector indexing with Pinecone
semantic retrieval
grounded answers over uploaded documents
📊 KPI Self-Evaluation
field coverage
schema validity
extraction accuracy
loop efficiency
🧲 Lead Generation
company discovery using LLM + search
context-aware email drafting
human-in-the-loop approval
🧠 Explainability
full agent trace
tool usage visibility
reasoning history
🏗️ Architecture Breakdown
Backend (AI Engine)
FastAPI — API layer
LangGraph — agent orchestration
LangChain — tool abstraction
Pinecone — vector database
Tesseract / pytesseract — OCR
Pydantic — schema validation
Frontend (Control Panel)
Next.js (App Router)
TailwindCSS
Recharts
Infrastructure
Vercel for frontend deployment
Python 3.12
uv for dependency management
📂 Project Structure
agentic-document-understanding/
│
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── services/     # OCR, extraction, validation, RAG
│   │   ├── workflows/    # LangGraph agent logic
│   │   ├── models/       # schemas and enums
│   │   └── core/         # configuration
│   │
│   └── api/main.py       # Vercel backend entrypoint
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
🧠 How the Agent Thinks

Each run produces a reasoning trace similar to this:

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

This enables:

debugging AI decisions
measuring reasoning quality
improving system behavior over time
📊 KPI System
Why KPIs matter

Most AI demos stop at “it works.”
This system also asks: how well does it work?

Metrics tracked
Metric	Meaning
Field Coverage	Percentage of expected fields successfully extracted
Extraction Accuracy	Correctness of extracted outputs
Schema Validity	Structural correctness of results
Loop Count	Agent reasoning efficiency
Example formulas
field_coverage = filled_fields / total_fields
accuracy = correct_fields / extracted_fields
🔌 API Overview
Documents
POST /documents/upload
GET /documents/history
GET /documents/latest
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
Dashboard	Overall system status and KPIs
Upload	Document ingestion and processing
Ask Docs	RAG-based grounded question answering
KPIs	Evaluation metrics and trends
Leads	Lead generation and outreach drafting
Graph	Agent workflow and reasoning visualization
⚙️ Local Setup
Clone the repository
git clone https://github.com/promzyadiole/agentic-document-understanding.git
cd agentic-document-understanding
Backend setup
cd backend
uv venv
source .venv/bin/activate
uv sync
uvicorn app.main:app --reload
Frontend setup
cd frontend
npm install
npm run dev
🔑 Environment Variables

Create a .env file for the backend with values such as:

OPENAI_API_KEY=
PINECONE_API_KEY=
INDEX_NAME=

TAVILY_API_KEY=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
LANGSMITH_TRACING=true

OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
🚀 Deployment Strategy
Frontend
Platform: Vercel
Root directory: frontend
Backend
Platform: Vercel serverless
Root directory: backend
Entry point: api/main.py
Python version: 3.12
⚠️ Known Limitations
Tesseract may require custom deployment support depending on hosting runtime
File system persistence is limited in serverless environments
Large document processing can be slower in serverless deployments
Pinecone index must be configured in advance
🔮 Future Work
multi-agent collaboration
streaming reasoning traces
better OCR fallback strategies
adaptive tool selection policies
stronger batch processing support
production-grade persistent storage for uploads and traces
🎯 What This Project Demonstrates

This project showcases:

agentic AI system design
LLM orchestration with LangGraph
document understanding with OCR + extraction
RAG integration with Pinecone
explainability and evaluation
full-stack AI product engineering
👤 Author

Promise Adiole

⭐ Final Note

This project is not just about calling an LLM.

It is about building a system that can reason through document workflows, choose actions, validate outputs, and expose its own decision process.
