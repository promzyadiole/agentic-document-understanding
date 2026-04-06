from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_documents import router as documents_router
from app.api.routes_graph import router as graph_router
from app.api.routes_health import router as health_router
from app.api.routes_kpi import router as kpi_router
from app.api.routes_leads import router as leads_router
from app.api.routes_query import router as query_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Agentic document understanding for procurement and construction intelligence.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://agentic-document-understanding-two.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(kpi_router, prefix="/kpis", tags=["kpis"])
app.include_router(leads_router, prefix="/leads", tags=["leads"])
app.include_router(graph_router, prefix="/graph", tags=["graph"])


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running",
        "environment": settings.app_env,
    }