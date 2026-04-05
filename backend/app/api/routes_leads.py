from fastapi import APIRouter, HTTPException

from app.models.responses import EmailDraftResponse, LeadListResponse
from app.models.schemas import EmailDraftRequest, LeadSearchRequest
from app.services.email_drafting import draft_outreach_email
from app.services.lead_research import search_construction_leads

router = APIRouter()


@router.post("/search", response_model=LeadListResponse)
def search_leads(request: LeadSearchRequest):
    try:
        leads = search_construction_leads(
            query=request.query,
            max_results=request.max_results,
            location_hint=request.location_hint,
        )
        return LeadListResponse(
            leads=leads,
            message="Lead search completed successfully.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/draft-email", response_model=EmailDraftResponse)
def create_email_draft(request: EmailDraftRequest):
    try:
        draft = draft_outreach_email(
            company_name=request.company_name,
            company_summary=request.company_summary,
            website=request.website,
            location=request.location,
            recipient_email=request.recipient_email,
        )
        return EmailDraftResponse(
            message="Draft email created successfully. Human approval is required before sending.",
            draft=draft,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("")
def get_leads_info():
    return {
        "message": "Use /leads/search to discover leads and /leads/draft-email to generate approval-safe drafts."
    }