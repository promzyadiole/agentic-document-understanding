from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.agency_profile import public_profile
from app.core.config import get_settings
from app.models.schemas import GenerateProposalRequest
from app.services import outreach_store, proposal_store
from app.services.proposal_generation import generate_proposal

router = APIRouter()


@router.get("/agency/profile")
def get_agency_profile():
    """Public firm profile used by the services landing page."""
    return public_profile()


@router.get("")
def list_proposals():
    return {"proposals": [p.model_dump(mode="json") for p in proposal_store.list_proposals()]}


@router.post("/generate")
def create_proposal(request: GenerateProposalRequest):
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="Proposal generation is not configured (missing OPENAI_API_KEY).",
        )
    try:
        proposal = generate_proposal(
            company_name=request.company_name,
            website=request.website,
            price_cents=request.price_cents,
            currency=request.currency,
            brief=request.brief,
            outreach_id=request.outreach_id,
        )
        # Link the proposal back to its originating approved outreach, if any.
        if request.outreach_id:
            outreach_store.update_outreach(request.outreach_id, proposal_id=proposal.id)
        return {"message": "Proposal generated.", "proposal": proposal.model_dump(mode="json")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{proposal_id}")
def get_proposal(proposal_id: str):
    proposal = proposal_store.get_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return {"proposal": proposal.model_dump(mode="json")}


@router.get("/token/{token}")
def get_proposal_by_token(token: str):
    proposal = proposal_store.get_proposal_by_token(token)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return {"proposal": proposal.model_dump(mode="json")}
