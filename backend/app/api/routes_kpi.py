from fastapi import APIRouter

from app.models.responses import KPIListResponse
from app.services.kpi import load_kpi_records, summarize_kpis

router = APIRouter()


@router.get("", response_model=KPIListResponse)
def get_kpis():
    records = load_kpi_records()
    summary = summarize_kpis(records)
    return KPIListResponse(entries=records, summary=summary)