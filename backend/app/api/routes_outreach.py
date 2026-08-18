from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ApproveOutreachRequest,
    CreateOutreachRequest,
    OutreachDraft,
    OutreachStatus,
)
from app.core.agency_profile import SENDER_EMAIL
from app.services import gmail_send, outreach_store
from app.services.email_drafting import draft_outreach_email

router = APIRouter()


@router.get("")
def list_outreach():
    return {"outreach": [d.model_dump(mode="json") for d in outreach_store.list_outreach()]}


@router.post("")
def create_outreach(request: CreateOutreachRequest):
    """Draft an outreach email for a company and persist it as pending human approval."""
    try:
        draft = draft_outreach_email(
            company_name=request.company_name,
            company_summary=request.company_summary,
            website=request.website,
            location=request.location,
            recipient_email=request.recipient_email,
        )
        record = OutreachDraft(
            id=uuid4().hex,
            company_name=request.company_name,
            recipient_email=request.recipient_email,
            website=request.website,
            location=request.location,
            summary=request.company_summary,
            subject=draft.subject,
            body=draft.body,
            status=OutreachStatus.DRAFTED,
        )
        outreach_store.create_outreach(record)
        return {"message": "Outreach drafted; human approval required before sending.", "outreach": record.model_dump(mode="json")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{outreach_id}")
def get_outreach(outreach_id: str):
    record = outreach_store.get_outreach(outreach_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Outreach draft not found.")
    return {"outreach": record.model_dump(mode="json")}


@router.post("/{outreach_id}/approve")
def approve_outreach(outreach_id: str, request: ApproveOutreachRequest):
    """Human approves the email (optionally editing the subject/body first)."""
    record = outreach_store.get_outreach(outreach_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Outreach draft not found.")

    updated = outreach_store.update_outreach(
        outreach_id,
        recipient_email=request.recipient_email,
        subject=request.subject,
        body=request.body,
        status=OutreachStatus.APPROVED.value,
    )

    # Real send: if a recipient is set and Gmail sending is configured, send it
    # from the org Gmail and mark it SENT. Otherwise it stays APPROVED.
    sent = False
    send_note = ""
    if updated.recipient_email and gmail_send.is_configured():
        try:
            gmail_send.send_email(
                sender=SENDER_EMAIL,
                to=updated.recipient_email,
                subject=updated.subject,
                body=updated.body,
            )
            updated = outreach_store.set_status(outreach_id, OutreachStatus.SENT)
            sent = True
        except Exception as exc:  # keep approval even if send fails
            send_note = f" (approved, but sending failed: {exc})"
    elif updated.recipient_email and not gmail_send.is_configured():
        send_note = " Gmail sending isn't authorized yet — run backend/scripts/gmail_authorize.py to enable real send."

    base = "Outreach sent from your Gmail." if sent else "Outreach approved."
    if updated.kind != "thank_you":
        base += " You can now generate a proposal for this company."
    return {"message": base + send_note, "sent": sent, "outreach": updated.model_dump(mode="json")}


@router.post("/{outreach_id}/reject")
def reject_outreach(outreach_id: str):
    updated = outreach_store.set_status(outreach_id, OutreachStatus.REJECTED)
    if updated is None:
        raise HTTPException(status_code=404, detail="Outreach draft not found.")
    return {"message": "Outreach rejected.", "outreach": updated.model_dump(mode="json")}
