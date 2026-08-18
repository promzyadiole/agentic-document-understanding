from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.models.schemas import ContactRequest, InboundMessage
from app.services import inbound_store
from app.services.document_pipeline import run_and_register
from app.services.email_classifier import classify_message
from app.services.pdf_render import render_inquiry_pdf

router = APIRouter()


@router.get("/inbound")
def list_inbound():
    return {"inbound": [m.model_dump(mode="json") for m in inbound_store.list_inbound()]}


@router.post("")
def submit_contact(request: ContactRequest):
    """
    Public contact-form submission from the landing page. The inquiry is
    classified for fast triage, then rendered to a PDF and run through the same
    document-understanding workflow as an uploaded document.
    """
    try:
        classification = classify_message(
            name=request.name,
            email=request.email,
            message=request.message,
            company=request.company,
        )

        document_id = None
        try:
            pdf_path = render_inquiry_pdf(request.name, request.email, request.company, request.message)
            _, document_id = run_and_register(pdf_path, project_id="inbound", source="contact_form")
        except Exception:
            document_id = None

        record = InboundMessage(
            id=uuid4().hex,
            name=request.name,
            email=request.email,
            company=request.company,
            message=request.message,
            classification=classification,
            document_id=document_id,
        )
        inbound_store.create_inbound(record)
        return {
            "message": "Thanks — your message was received and routed to our team.",
            "inbound": record.model_dump(mode="json"),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
