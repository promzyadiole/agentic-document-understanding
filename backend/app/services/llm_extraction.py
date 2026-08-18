from __future__ import annotations

"""
LLM-based structured extraction.

This replaces the brittle regex engine with grounded, schema-constrained
extraction using LangChain's ``with_structured_output``. For every field the
model is asked to return not just a value but the *verbatim evidence snippet*
from the document that supports it. That evidence is then located in the source
text to build ``SourceSpan`` objects, which powers source-span highlighting in
the UI and keeps every extracted value auditable.

The output is mapped back into the exact same typed schemas the rest of the
pipeline already understands (``InvoiceData``, ``PurchaseOrderData`` ...), so
validation, KPI logging and the API contract are unchanged.
"""

from typing import Any, Optional

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.models.enums import ConfidenceLevel, DocumentType, ProcessingStatus
from app.models.schemas import (
    DeliveryNoteData,
    ExtractedField,
    ExtractionResult,
    FinancialReportData,
    InvoiceData,
    PurchaseOrderData,
    SiteReportData,
    SourceSpan,
)
from app.services.extraction import (
    _estimate_page_number,
    _normalize_amount,
    _normalize_company_name,
    _normalize_currency,
)

settings = get_settings()


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )


# ---------------------------------------------------------------------------
# LLM-facing schemas
# ---------------------------------------------------------------------------
# These are intentionally flat and string-based so the model can populate them
# reliably. Each field carries the value, a verbatim evidence snippet, and a
# self-reported confidence. They are mapped to the pipeline schemas afterwards.


class LLMField(BaseModel):
    value: Optional[str] = Field(
        default=None,
        description="The extracted value exactly as it should be reported, or null if the document does not contain it. Never guess.",
    )
    evidence: Optional[str] = Field(
        default=None,
        description="A short verbatim snippet copied from the document text that proves this value. Null if not found.",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How confident you are in this value, from 0.0 to 1.0.",
    )


class LLMLineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    amount: Optional[float] = None


class LLMInvoice(BaseModel):
    invoice_number: LLMField = Field(default_factory=LLMField)
    po_number: LLMField = Field(default_factory=LLMField)
    supplier_name: LLMField = Field(default_factory=LLMField)
    invoice_date: LLMField = Field(default_factory=LLMField)
    due_date: LLMField = Field(default_factory=LLMField)
    currency: LLMField = Field(default_factory=LLMField)
    subtotal: LLMField = Field(default_factory=LLMField)
    tax_amount: LLMField = Field(default_factory=LLMField)
    total_amount: LLMField = Field(default_factory=LLMField)
    line_items: list[LLMLineItem] = Field(default_factory=list)


class LLMPurchaseOrder(BaseModel):
    po_number: LLMField = Field(default_factory=LLMField)
    supplier_name: LLMField = Field(default_factory=LLMField)
    buyer_name: LLMField = Field(default_factory=LLMField)
    issue_date: LLMField = Field(default_factory=LLMField)
    currency: LLMField = Field(default_factory=LLMField)
    total_amount: LLMField = Field(default_factory=LLMField)
    line_items: list[LLMLineItem] = Field(default_factory=list)


class LLMDeliveryNote(BaseModel):
    delivery_note_number: LLMField = Field(default_factory=LLMField)
    po_number: LLMField = Field(default_factory=LLMField)
    supplier_name: LLMField = Field(default_factory=LLMField)
    delivery_date: LLMField = Field(default_factory=LLMField)
    received_items: list[LLMLineItem] = Field(default_factory=list)


class LLMFinancialReport(BaseModel):
    company_name: LLMField = Field(default_factory=LLMField)
    reporting_period: LLMField = Field(default_factory=LLMField)
    revenue: LLMField = Field(default_factory=LLMField)
    operating_income: LLMField = Field(default_factory=LLMField)
    net_income: LLMField = Field(default_factory=LLMField)
    total_assets: LLMField = Field(default_factory=LLMField)
    total_liabilities: LLMField = Field(default_factory=LLMField)
    cash_flow_operating: LLMField = Field(default_factory=LLMField)
    key_sections: list[str] = Field(default_factory=list)


class LLMSiteReport(BaseModel):
    project_name: LLMField = Field(default_factory=LLMField)
    site_location: LLMField = Field(default_factory=LLMField)
    report_date: LLMField = Field(default_factory=LLMField)
    contractor_name: LLMField = Field(default_factory=LLMField)
    summary: LLMField = Field(default_factory=LLMField)
    issues: list[str] = Field(default_factory=list)


_SCHEMA_BY_TYPE: dict[DocumentType, type[BaseModel]] = {
    DocumentType.INVOICE: LLMInvoice,
    DocumentType.PURCHASE_ORDER: LLMPurchaseOrder,
    DocumentType.DELIVERY_NOTE: LLMDeliveryNote,
    DocumentType.FINANCIAL_REPORT: LLMFinancialReport,
    DocumentType.SITE_REPORT: LLMSiteReport,
}

# Which fields should be normalized as monetary amounts / currency / company.
_AMOUNT_FIELDS = {
    "total_amount",
    "subtotal",
    "tax_amount",
    "revenue",
    "operating_income",
    "net_income",
    "total_assets",
    "total_liabilities",
    "cash_flow_operating",
}


def _confidence_level(score: float) -> ConfidenceLevel:
    if score >= 0.85:
        return ConfidenceLevel.HIGH
    if score >= 0.65:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def _normalizer_for(field_name: str):
    if field_name in _AMOUNT_FIELDS:
        return _normalize_amount
    if field_name == "currency":
        return _normalize_currency
    if field_name == "company_name":
        return _normalize_company_name
    return None


def _source_spans_for(evidence: Optional[str], text: str) -> list[SourceSpan]:
    if not evidence:
        return []
    idx = text.lower().find(evidence.strip().lower())
    page = _estimate_page_number(text, idx) if idx >= 0 else 1
    return [SourceSpan(page=page, text_excerpt=evidence.strip()[:300], bbox=None)]


def _to_extracted_field(name: str, llm_field: LLMField, text: str) -> Optional[ExtractedField]:
    if llm_field is None or llm_field.value is None or str(llm_field.value).strip() == "":
        return None

    raw_value = str(llm_field.value).strip()
    normalizer = _normalizer_for(name)
    normalized = normalizer(raw_value) if normalizer else raw_value
    confidence = float(llm_field.confidence or 0.0)

    return ExtractedField(
        name=name,
        value=raw_value,
        normalized_value=normalized,
        confidence_score=confidence,
        confidence_level=_confidence_level(confidence),
        source_spans=_source_spans_for(llm_field.evidence, text),
    )


def _line_items(items: list[LLMLineItem]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items[:25]:
        result.append(
            {
                "description": item.description,
                "quantity": item.quantity,
                "amount": item.amount,
            }
        )
    return result


def _map_to_structured(document_type: DocumentType, data: BaseModel, text: str):
    """Map a flat LLM extraction object into the pipeline's typed schema."""

    def field(name: str):
        return _to_extracted_field(name, getattr(data, name, None), text)

    if document_type == DocumentType.INVOICE:
        return InvoiceData(
            invoice_number=field("invoice_number"),
            po_number=field("po_number"),
            supplier_name=field("supplier_name"),
            invoice_date=field("invoice_date"),
            due_date=field("due_date"),
            currency=field("currency"),
            subtotal=field("subtotal"),
            tax_amount=field("tax_amount"),
            total_amount=field("total_amount"),
            line_items=_line_items(data.line_items),
        )
    if document_type == DocumentType.PURCHASE_ORDER:
        return PurchaseOrderData(
            po_number=field("po_number"),
            supplier_name=field("supplier_name"),
            buyer_name=field("buyer_name"),
            issue_date=field("issue_date"),
            currency=field("currency"),
            total_amount=field("total_amount"),
            line_items=_line_items(data.line_items),
        )
    if document_type == DocumentType.DELIVERY_NOTE:
        return DeliveryNoteData(
            delivery_note_number=field("delivery_note_number"),
            po_number=field("po_number"),
            supplier_name=field("supplier_name"),
            delivery_date=field("delivery_date"),
            received_items=_line_items(data.received_items),
        )
    if document_type == DocumentType.FINANCIAL_REPORT:
        return FinancialReportData(
            company_name=field("company_name"),
            reporting_period=field("reporting_period"),
            revenue=field("revenue"),
            operating_income=field("operating_income"),
            net_income=field("net_income"),
            total_assets=field("total_assets"),
            total_liabilities=field("total_liabilities"),
            cash_flow_operating=field("cash_flow_operating"),
            key_sections=list(data.key_sections or []),
        )
    if document_type == DocumentType.SITE_REPORT:
        return SiteReportData(
            project_name=field("project_name"),
            site_location=field("site_location"),
            report_date=field("report_date"),
            contractor_name=field("contractor_name"),
            summary=field("summary"),
            issues=list(data.issues or []),
        )
    return {"raw_preview": text[:2000]}


def _flatten_fields(structured: Any) -> dict[str, ExtractedField]:
    if structured is None or isinstance(structured, dict):
        return {}
    fields: dict[str, ExtractedField] = {}
    for key in structured.model_dump().keys():
        attr = getattr(structured, key, None)
        if isinstance(attr, ExtractedField):
            fields[key] = attr
    return fields


_SYSTEM_PROMPT = (
    "You are a meticulous document-extraction engine for construction and finance documents. "
    "Extract ONLY information that is explicitly present in the provided text. "
    "Never invent, infer, or hallucinate values. If a field is not present, return null for its value. "
    "For every field you fill, copy a short verbatim evidence snippet from the document that supports it, "
    "and give an honest confidence score."
)


def llm_extract_document_data(
    document_id: str,
    text: str,
    document_type: DocumentType,
    classification_confidence: float | None = None,
    *,
    feedback: str | None = None,
) -> ExtractionResult:
    """
    Extract structured data with an LLM constrained to a typed schema.

    ``feedback`` lets the self-correcting agent loop pass validation errors back
    into a re-extraction attempt (Tier 1B).
    """
    schema = _SCHEMA_BY_TYPE.get(document_type)
    if schema is None:
        structured = {"raw_preview": text[:2000]}
        return ExtractionResult(
            document_id=document_id,
            document_type=document_type,
            fields={},
            structured_data=structured,
            processing_status=ProcessingStatus.EXTRACTED,
            classification_confidence=classification_confidence,
            extraction_notes=["Unknown document type; no structured extraction performed."],
        )

    llm = _get_llm().with_structured_output(schema)

    correction_note = ""
    if feedback:
        correction_note = (
            "\n\nA previous extraction attempt had these validation problems. "
            "Pay special attention to fixing them:\n" + feedback
        )

    user_prompt = (
        f"Document type: {document_type.value}.\n"
        f"Extract the structured fields defined by the schema from the document below.{correction_note}\n\n"
        f"----- DOCUMENT START -----\n{text[:12000]}\n----- DOCUMENT END -----"
    )

    data = llm.invoke(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )

    structured = _map_to_structured(document_type, data, text)
    fields = _flatten_fields(structured)

    notes = ["Structured extraction performed by LLM (schema-constrained)."]
    if feedback:
        notes.append("Re-extraction guided by validation feedback.")

    return ExtractionResult(
        document_id=document_id,
        document_type=document_type,
        fields=fields,
        structured_data=structured,
        processing_status=ProcessingStatus.EXTRACTED,
        classification_confidence=classification_confidence,
        extraction_notes=notes,
    )
