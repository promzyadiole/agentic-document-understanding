🏗️ ConstructionFlow AI
Agentic Document Understanding for Construction Intelligence




🚀 Overview

ConstructionFlow AI is an agentic AI system designed to process, understand, and extract insights from complex construction and procurement documents.

It combines:

🧠 LLM-powered reasoning (LangGraph agent loop)
📄 OCR + document parsing
🔎 RAG (Retrieval-Augmented Generation)
📊 KPI tracking & evaluation
🎯 Lead generation & outreach automation

The system is built to simulate real-world enterprise workflows, where AI agents iteratively reason, select tools, validate outputs, and improve results.

🧠 Key Concept: Agentic Workflow

Unlike traditional pipelines, this system uses a loop-based reasoning agent:

Analyze document
Decide next action
Call tools (OCR, extraction, validation, indexing)
Evaluate results
Repeat until complete

👉 This mimics how a human analyst works.

🏗️ System Architecture
🔁 Agent Loop (LangGraph)

The workflow follows this structure:

document_intake
clean_text
classify_document
agent_reasoning_loop
tool_execution
extract_fields
validate_document
index_document
log_kpis

The agent dynamically decides:

which tool to call
when to retry
when to stop
🧩 Tech Stack
Backend
⚡ FastAPI
🧠 LangChain + LangGraph
🔍 Pinecone (vector DB)
🧾 PDFPlumber + PyMuPDF
🔤 Tesseract OCR (via pytesseract)
📊 Pandas / NumPy
🔗 LangSmith (tracing)
Frontend
⚛️ Next.js (App Router)
🎨 TailwindCSS
📊 Recharts
🧩 Component-driven UI
Infrastructure
▲ Vercel (Frontend + Backend Serverless)
🐍 Python 3.12
📦 uv (dependency management)
📂 Project Structure
agentic-document-understanding/
│
├── backend/
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── services/       # OCR, extraction, validation
│   │   ├── workflows/      # LangGraph agent
│   │   ├── models/         # schemas & enums
│   │   └── core/           # config
│   │
│   └── api/main.py         # Vercel entrypoint
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
├── agentic-doc.png         # Architecture diagram
└── README.md
⚙️ Features
📄 Document Processing
Upload PDFs or images
OCR extraction (if needed)
Structured parsing
Metadata generation
🧠 Agent Reasoning
Multi-step decision loop
Tool selection via LLM
Iterative refinement
Explainable trace output
🔎 RAG System
Document indexing in Pinecone
Semantic search
Grounded Q&A
📊 KPI Tracking
Field coverage
Extraction accuracy
Schema validity
Agent loop count
🧲 Lead Generation
AI-powered company discovery
Context-aware email drafting
Human-in-the-loop (HITL)
🖥️ UI Pages
Dashboard → system overview + KPIs
Upload → document ingestion
Ask Docs → RAG querying
KPIs → metrics analysis
Leads → outreach generation
Graph → agent workflow visualization
🔌 API Endpoints
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
🧪 Local Setup
1. Clone repo
git clone https://github.com/promzyadiole/agentic-document-understanding.git
cd agentic-document-understanding
2. Backend setup
cd backend
uv venv
source .venv/bin/activate
uv sync
uvicorn app.main:app --reload
3. Frontend setup
cd frontend
npm install
npm run dev
🔑 Environment Variables

Create .env in backend:

OPENAI_API_KEY=your_key
PINECONE_API_KEY=your_key
INDEX_NAME=agentic-docs
TAVILY_API_KEY=your_key
LANGSMITH_API_KEY=your_key

OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
🚀 Deployment
Frontend (Vercel)
Root directory: frontend
Backend (Vercel)
Root directory: backend
Entry point: api/main.py
Python version: 3.12
📈 KPI Formula Examples
Field Coverage
filled_fields / total_fields
Extraction Accuracy
correct_fields / extracted_fields
Schema Validity
valid_fields / total_fields
Agent Efficiency
1 / loop_count
🔍 Explainability

Each document stores:

agent decisions
tool calls
loop iterations
validation outcomes

👉 Visible in the Graph + Trace UI

🎯 Use Cases
Construction contract analysis
Procurement document automation
Financial report parsing
Vendor intelligence & outreach
Knowledge extraction pipelines
🧠 Why This Project Matters

This project demonstrates:

Agentic AI system design
Real-world LLM orchestration
End-to-end AI product engineering
Explainability & evaluation
Production-ready architecture
👤 Author

Promise Adiole

⭐ Future Improvements
Multi-agent collaboration
Streaming reasoning traces
Better OCR fallback strategies
Fine-tuned extraction models
Distributed processing
📜 License

MIT License