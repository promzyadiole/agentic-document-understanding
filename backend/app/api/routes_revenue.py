from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    OutreachDraft,
    OutreachStatus,
    Payment,
    PaymentStatus,
    RegisterPaymentRequest,
)
from app.services import outreach_store, payment_store, proposal_store
from app.services.document_pipeline import run_and_register
from app.services.email_drafting import draft_thank_you_email
from app.services.pdf_render import render_proposal_pdf

router = APIRouter()


def _money(cents: int, currency: str) -> str:
    return f"{cents / 100:,.0f} {currency.upper()}"


@router.get("/summary")
def revenue_summary():
    payments = payment_store.list_payments()
    confirmed = [p for p in payments if p.status == PaymentStatus.CONFIRMED]
    pending = [p for p in payments if p.status == PaymentStatus.PENDING]
    return {
        "total_revenue_cents": payment_store.confirmed_revenue_cents(),
        "confirmed_count": len(confirmed),
        "pending_count": len(pending),
        "total_count": len(payments),
    }


@router.get("/payments")
def list_payments():
    return {"payments": [p.model_dump(mode="json") for p in payment_store.list_payments()]}


@router.post("/payments")
def register_payment(request: RegisterPaymentRequest):
    company_name = request.company_name or ""
    if request.proposal_id and not company_name:
        proposal = proposal_store.get_proposal(request.proposal_id)
        if proposal:
            company_name = proposal.company_name

    payment = Payment(
        id=uuid4().hex,
        proposal_id=request.proposal_id,
        company_name=company_name,
        amount_cents=request.amount_cents,
        currency=request.currency,
        status=PaymentStatus.PENDING,
    )
    payment_store.create_payment(payment)
    return {"message": "Payment registered; awaiting confirmation.", "payment": payment.model_dump(mode="json")}


@router.post("/payments/{payment_id}/confirm")
def confirm_payment(payment_id: str):
    """
    Confirm a payment. On confirmation:
      1. Revenue increments (status -> confirmed).
      2. The proposal is rendered to a PDF and run through the document workflow
         — completing the same pipeline as an uploaded document.
      3. A thank-you email is drafted into Approvals for human confirmation
         before sending.
    """
    payment = payment_store.get_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found.")
    if payment.status == PaymentStatus.CONFIRMED:
        return {"message": "Payment already confirmed.", "payment": payment.model_dump(mode="json")}

    document_id: str | None = None
    proposal = proposal_store.get_proposal(payment.proposal_id) if payment.proposal_id else None

    # 2. Run the returned proposal PDF through the document workflow.
    if proposal is not None:
        try:
            pdf_path = render_proposal_pdf(proposal)
            _, document_id = run_and_register(
                pdf_path, project_id=f"paid-{proposal.company_name[:20]}", source="paid_proposal"
            )
            proposal_store.set_proposal_status(proposal.id, "paid")
        except Exception as exc:  # keep the confirmation resilient
            document_id = None
            _pdf_error = str(exc)

    updated = payment_store.update_payment(
        payment_id,
        status=PaymentStatus.CONFIRMED.value,
        document_id=document_id,
        confirmed_at=datetime.utcnow().isoformat(),
    )

    # 3. Draft a thank-you email for human confirmation before sending.
    thank_you_id: str | None = None
    try:
        draft = draft_thank_you_email(
            company_name=payment.company_name or "our client",
            amount_label=_money(payment.amount_cents, payment.currency),
        )
        record = OutreachDraft(
            id=uuid4().hex,
            company_name=payment.company_name or "Client",
            subject=draft.subject,
            body=draft.body,
            kind="thank_you",
            status=OutreachStatus.DRAFTED,
            proposal_id=payment.proposal_id,
        )
        outreach_store.create_outreach(record)
        thank_you_id = record.id
    except Exception:
        thank_you_id = None

    return {
        "message": "Payment confirmed. Revenue updated, proposal PDF processed, and a thank-you email drafted for your approval.",
        "payment": updated.model_dump(mode="json") if updated else None,
        "document_id": document_id,
        "thank_you_outreach_id": thank_you_id,
    }
