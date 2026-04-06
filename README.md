# 🏗️ ConstructionFlow AI  
### Agentic Document Intelligence for Construction & Procurement

<p align="center">
  <img src="./agentic-doc.png" width="85%" />
</p>

<p align="center">
  <b>LLM-powered agent system for reasoning over real-world documents</b><br/>
  Built with FastAPI • LangGraph • LangChain • Pinecone • Next.js
</p>

---

## 🧠 What This Project Is

ConstructionFlow AI is a **production-grade agentic system** that goes beyond simple extraction.

It introduces a **reasoning loop** where the system:

- 🧠 Understands documents  
- 🔎 Retrieves context (RAG)  
- ⚙️ Takes actions via tools  
- 📊 Evaluates its own outputs  
- 🔁 Improves through iteration  

> This is not a pipeline.  
> This is a system that **reasons, acts, validates, and improves**.

---

## ⚡ Key Features

- 🧠 **Agentic Reasoning Loop** (LangGraph-powered)
- 🔎 **Retrieval-Augmented Generation (RAG)** with Pinecone
- 📄 **OCR + Structured Extraction**
- 📊 **Self-Evaluation via KPIs**
- 🎯 **Lead Generation & Outreach Automation**
- 🧠 **Explainability (full agent trace + logs)**

---

## 🔁 Agentic Workflow

```text
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
    - retry if needed
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
```

---

## 🧠 Core Idea

**Traditional Systems**
- parse → extract → done ❌

**ConstructionFlow AI**
- analyze → decide → act → evaluate → retry → finalize ✅

---

## ⚙️ Capabilities

### 📄 Document Intelligence
- OCR (scanned PDFs/images)
- semantic parsing
- structured data extraction

### 🔎 Retrieval-Augmented Generation
- Pinecone vector indexing
- semantic search
- grounded answers

### 📊 KPI Evaluation
- field coverage
- schema validity
- extraction accuracy
- loop efficiency

### 🧲 Lead Generation
- company discovery
- LLM-assisted outreach drafting
- human-in-the-loop approval

### 🧠 Explainability
- full agent trace
- decision transparency
- tool usage logs

---

## 🏗️ Architecture Overview

```text
                ┌────────────────────┐
                │   Frontend (Next)  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   FastAPI Backend  │
                └─────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 ┌────────────┐   ┌──────────────┐   ┌──────────────┐
 │  LangGraph │   │  LangChain   │   │  OCR Engine  │
 │ Agent Loop │   │    Tools     │   │ (Tesseract)  │
 └────────────┘   └──────────────┘   └──────────────┘
        │
        ▼
 ┌────────────────────┐
 │ Pinecone Vector DB │
 └────────────────────┘
```

---

## 📂 Project Structure

```text
agentic-document-understanding/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── workflows/
│   │   ├── models/
│   │   └── core/
│   └── api/main.py
│
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/api.ts
│
└── agentic-doc.png
```

---

## 🧠 Agent Trace Example

```json
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
```

---

## 📊 KPI System

- **Field Coverage** → % of required fields extracted  
- **Extraction Accuracy** → correctness vs ground truth  
- **Schema Validity** → structural correctness  
- **Loop Count** → reasoning efficiency  

---

## 🔌 API

### Documents
- POST `/documents/upload`
- GET `/documents/history`

### Query
- POST `/query`

### KPIs
- GET `/kpis`

### Leads
- POST `/leads/search`
- POST `/leads/draft-email`

### Graph
- GET `/graph/export`

---

## 🖥️ UI

- Dashboard → system overview  
- Upload → document ingestion  
- Ask Docs → RAG queries  
- KPIs → performance metrics  
- Leads → outreach generation  
- Graph → agent visualization  

---

## ⚙️ Local Setup

### Clone Repository
```bash
git clone https://github.com/promzyadiole/agentic-document-understanding.git
cd agentic-document-understanding
```

### Backend
```bash
cd backend
uv venv
source .venv/bin/activate
uv sync
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Environment Variables

Create `.env` in backend:

```
OPENAI_API_KEY=
PINECONE_API_KEY=
INDEX_NAME=
TAVILY_API_KEY=
LANGSMITH_API_KEY=
```

---

## 🚀 Deployment

Frontend:
- Vercel → `frontend/`

Backend:
- Vercel Serverless → `backend/`
- Python 3.12
- Entry: `api/main.py`

---

## ⚠️ Limitations

- OCR depends on Tesseract environment  
- Serverless filesystem is ephemeral  
- Large documents may introduce latency  

---

## 🔮 Future Work

- multi-agent orchestration  
- streaming reasoning traces  
- improved OCR fallback  
- persistent storage layer  

---

## 👤 Author

**Promise Adiole**

---

## ⭐ Final Thought

> This project is not about calling an LLM.
>
> It is about building a system that can:
>
> - **Reason**
> - **Act**
> - **Validate**
> - **Improve**
>
> in real-world document workflows.
