from fastapi import APIRouter
from app.models.responses import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
def health_check():
    return HealthResponse()