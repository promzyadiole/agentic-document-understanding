from __future__ import annotations

import re
from typing import Any

from app.models.enums import ConfidenceLevel, DocumentType, ProcessingStatus
from app.models.schemas import (
    ExtractedField,
    ExtractionResult,
    FinancialReportData,
    InvoiceData,
    PurchaseOrderData,
    DeliveryNoteData,
    SiteReportData,
    SourceSpan,
)


def extract_document_data(
    document_id: str,
    text: str,
    document_type: DocumentType,
    classification_confidence: float | None = None,
) -> ExtractionResult:
    """
    Main extraction entrypoint.
    Dispatches extraction based on classified document type.
    """
    if document_type == DocumentType.PURCHASE_ORDER:
        structured = extract_purchase_order_data(text)
    elif document_type == DocumentType.DELIVERY_NOTE:
        structured = extract_delivery_note_data(text)
    elif document_type == DocumentType.INVOICE:
        structured = extract_invoice_data(text)
    elif document_type == DocumentType.FINANCIAL_REPORT:
        structured = extract_financial_report_data(text)
    elif document_type == DocumentType.SITE_REPORT:
        structured = extract_site_report_data(text)
    else:
        structured = {"raw_preview": text[:2000]}

    fields = _flatten_structured_fields(structured)

    return ExtractionResult(
        document_id=document_id,
        document_type=document_type,
        fields=fields,
        structured_data=structured,
        processing_status=ProcessingStatus.EXTRACTED,
        classification_confidence=classification_confidence,
        extraction_notes=[],
    )


def extract_purchase_order_data(text: str) -> PurchaseOrderData:
    po_number = _extract_field(
        text,
        "po_number",
        [
            r"purchase\s+order\s+(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9\-/]+)",
            r"\bpo\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9\-/]+)",
        ],
    )
    supplier_name = _extract_field(
        text,
        "supplier_name",
        [
            r"(?:supplier|vendor)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    buyer_name = _extract_field(
        text,
        "buyer_name",
        [
            r"(?:buyer|purchaser|ordered\s+by)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    issue_date = _extract_field(
        text,
        "issue_date",
        [
            r"(?:issue\s+date|order\s+date|date)\s*[:\-]?\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
        ],
        normalizer=_normalize_date_string,
    )
    currency = _extract_field(
        text,
        "currency",
        [
            r"\b(currency)\s*[:\-]?\s*([A-Z]{3})",
            r"([€$£])",
        ],
        group_index=2,
        normalizer=_normalize_currency,
    )
    total_amount = _extract_field(
        text,
        "total_amount",
        [
            r"(?:total\s+amount|order\s+total|grand\s+total|total)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]*)",
        ],
        normalizer=_normalize_amount,
    )

    line_items = _extract_line_items(text)

    return PurchaseOrderData(
        po_number=po_number,
        supplier_name=supplier_name,
        buyer_name=buyer_name,
        issue_date=issue_date,
        currency=currency,
        total_amount=total_amount,
        line_items=line_items,
    )


def extract_delivery_note_data(text: str) -> DeliveryNoteData:
    delivery_note_number = _extract_field(
        text,
        "delivery_note_number",
        [
            r"(?:delivery\s+note\s+(?:number|no\.?|#)|delivery\s+(?:number|no\.?|#))\s*[:\-]?\s*([A-Z0-9\-/]+)",
        ],
    )
    po_number = _extract_field(
        text,
        "po_number",
        [
            r"\bpo\s*(?:number|no\.?|#)?\s*[:\-]?\s*([A-Z0-9\-/]+)",
            r"purchase\s+order\s*(?:number|no\.?|#)?\s*[:\-]?\s*([A-Z0-9\-/]+)",
        ],
    )
    supplier_name = _extract_field(
        text,
        "supplier_name",
        [
            r"(?:supplier|vendor)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    delivery_date = _extract_field(
        text,
        "delivery_date",
        [
            r"(?:delivery\s+date|delivered\s+on|date)\s*[:\-]?\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
        ],
        normalizer=_normalize_date_string,
    )

    received_items = _extract_line_items(text)

    return DeliveryNoteData(
        delivery_note_number=delivery_note_number,
        po_number=po_number,
        supplier_name=supplier_name,
        delivery_date=delivery_date,
        received_items=received_items,
    )


def extract_invoice_data(text: str) -> InvoiceData:
    invoice_number = _extract_field(
        text,
        "invoice_number",
        [
            r"invoice\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9\-/]+)",
        ],
    )
    po_number = _extract_field(
        text,
        "po_number",
        [
            r"\bpo\s*(?:number|no\.?|#)?\s*[:\-]?\s*([A-Z0-9\-/]+)",
            r"purchase\s+order\s*(?:number|no\.?|#)?\s*[:\-]?\s*([A-Z0-9\-/]+)",
        ],
    )
    supplier_name = _extract_field(
        text,
        "supplier_name",
        [
            r"(?:supplier|vendor|from)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    invoice_date = _extract_field(
        text,
        "invoice_date",
        [
            r"(?:invoice\s+date|date)\s*[:\-]?\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
        ],
        normalizer=_normalize_date_string,
    )
    due_date = _extract_field(
        text,
        "due_date",
        [
            r"(?:due\s+date|payment\s+due)\s*[:\-]?\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
        ],
        normalizer=_normalize_date_string,
    )
    currency = _extract_field(
        text,
        "currency",
        [
            r"\b(currency)\s*[:\-]?\s*([A-Z]{3})",
            r"([€$£])",
        ],
        group_index=2,
        normalizer=_normalize_currency,
    )
    subtotal = _extract_field(
        text,
        "subtotal",
        [
            r"(?:subtotal|net\s+amount)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]*)",
        ],
        normalizer=_normalize_amount,
    )
    tax_amount = _extract_field(
        text,
        "tax_amount",
        [
            r"(?:tax|vat|tax\s+amount|vat\s+amount)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]*)",
        ],
        normalizer=_normalize_amount,
    )
    total_amount = _extract_field(
        text,
        "total_amount",
        [
            r"(?:total\s+amount|amount\s+due|grand\s+total|total)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]*)",
        ],
        normalizer=_normalize_amount,
    )

    line_items = _extract_line_items(text)

    return InvoiceData(
        invoice_number=invoice_number,
        po_number=po_number,
        supplier_name=supplier_name,
        invoice_date=invoice_date,
        due_date=due_date,
        currency=currency,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        line_items=line_items,
    )


def extract_financial_report_data(text: str) -> FinancialReportData:
    company_name = _extract_field(
        text,
        "company_name",
        [
            r"^([A-Z][A-Z0-9&,\.\-\s]{2,})\n",
            r"(?:company|group)\s*[:\-]?\s*([^\n]+)",
        ],
        flags=re.MULTILINE,
        normalizer=_normalize_company_name,
    )
    reporting_period = _extract_field(
        text,
        "reporting_period",
        [
            r"(?:for\s+the\s+year\s+ended|year\s+ended|at)\s+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
            r"(?:reporting\s+period)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    revenue = _extract_field(
        text,
        "revenue",
        [
            r"(?:revenue|sales)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]{3,})",
        ],
        normalizer=_normalize_amount,
    )
    operating_income = _extract_field(
        text,
        "operating_income",
        [
            r"(?:operating\s+income|operating\s+profit|ebit)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]{3,})",
        ],
        normalizer=_normalize_amount,
    )
    net_income = _extract_field(
        text,
        "net_income",
        [
            r"(?:net\s+income|net\s+profit|profit\s+for\s+the\s+year)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]{3,})",
        ],
        normalizer=_normalize_amount,
    )
    total_assets = _extract_field(
        text,
        "total_assets",
        [
            r"(?:total\s+assets)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]{3,})",
        ],
        normalizer=_normalize_amount,
    )
    total_liabilities = _extract_field(
        text,
        "total_liabilities",
        [
            r"(?:total\s+liabilities)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]{3,})",
        ],
        normalizer=_normalize_amount,
    )
    cash_flow_operating = _extract_field(
        text,
        "cash_flow_operating",
        [
            r"(?:cash\s+flow\s+from\s+operations|net\s+cash\s+from\s+operating\s+activities)\s*[:\-]?\s*([€$£]?\s?[0-9][0-9,\.\s]{3,})",
        ],
        normalizer=_normalize_amount,
    )

    key_sections = _extract_financial_sections(text)

    return FinancialReportData(
        company_name=company_name,
        reporting_period=reporting_period,
        revenue=revenue,
        operating_income=operating_income,
        net_income=net_income,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        cash_flow_operating=cash_flow_operating,
        key_sections=key_sections,
    )


def extract_site_report_data(text: str) -> SiteReportData:
    project_name = _extract_field(
        text,
        "project_name",
        [
            r"(?:project\s+name|project)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    site_location = _extract_field(
        text,
        "site_location",
        [
            r"(?:site\s+location|location)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    report_date = _extract_field(
        text,
        "report_date",
        [
            r"(?:report\s+date|date)\s*[:\-]?\s*([0-9]{1,2}[\/\-.][0-9]{1,2}[\/\-.][0-9]{2,4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
        ],
        normalizer=_normalize_date_string,
    )
    contractor_name = _extract_field(
        text,
        "contractor_name",
        [
            r"(?:contractor|main\s+contractor)\s*[:\-]?\s*([^\n]+)",
        ],
    )
    summary = _extract_field(
        text,
        "summary",
        [
            r"(?:summary|overview)\s*[:\-]?\s*([^\n]+)",
        ],
    )

    issues = _extract_bulleted_issues(text)

    return SiteReportData(
        project_name=project_name,
        site_location=site_location,
        report_date=report_date,
        contractor_name=contractor_name,
        summary=summary,
        issues=issues,
    )


def _extract_field(
    text: str,
    field_name: str,
    patterns: list[str],
    *,
    group_index: int = 1,
    flags: int = re.IGNORECASE,
    normalizer=None,
) -> ExtractedField | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if not match:
            continue

        if group_index > match.lastindex if match.lastindex is not None else True:
            value = match.group(1).strip()
        else:
            try:
                value = match.group(group_index).strip()
            except IndexError:
                value = match.group(1).strip()

        normalized_value = normalizer(value) if normalizer else value
        confidence_score = _estimate_confidence(value)
        confidence_level = _confidence_level(confidence_score)

        return ExtractedField(
            name=field_name,
            value=value,
            normalized_value=normalized_value,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            source_spans=[_build_source_span(text, match)],
        )

    return None


def _extract_line_items(text: str) -> list[dict[str, Any]]:
    """
    Baseline heuristic line-item extractor.
    Looks for table-like rows with quantity and amount signals.
    """
    line_items: list[dict[str, Any]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        if len(line) < 8:
            continue

        if re.search(r"\b(qty|quantity)\b", line, re.IGNORECASE):
            continue

        match = re.search(
            r"(?P<description>[A-Za-z0-9 \-_/(),\.]{4,}?)\s+(?P<qty>\d+(?:\.\d+)?)\s+(?P<amount>[€$£]?\s?[0-9][0-9,\.]*)$",
            line,
        )
        if match:
            line_items.append(
                {
                    "description": match.group("description").strip(),
                    "quantity": _safe_float(match.group("qty")),
                    "amount": _normalize_amount(match.group("amount")),
                }
            )

    return line_items[:25]


def _extract_financial_sections(text: str) -> list[str]:
    known_sections = [
        "consolidated financial statements",
        "balance sheet",
        "income statement",
        "statement of income",
        "cash flow statement",
        "notes to the financial statements",
        "management report",
        "risk factors",
        "auditor's report",
    ]

    content = text.lower()
    found = [section for section in known_sections if section in content]
    return found


def _extract_bulleted_issues(text: str) -> list[str]:
    issues: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^[-•*]\s+", stripped):
            issues.append(re.sub(r"^[-•*]\s+", "", stripped))
    return issues[:20]


def _flatten_structured_fields(structured: Any) -> dict[str, ExtractedField]:
    if structured is None or isinstance(structured, dict):
        return {}

    fields: dict[str, ExtractedField] = {}
    data = structured.model_dump()

    for key, value in data.items():
        original_attr = getattr(structured, key, None)
        if isinstance(original_attr, ExtractedField):
            fields[key] = original_attr

    return fields


def _build_source_span(text: str, match: re.Match[str]) -> SourceSpan:
    matched_text = match.group(0).strip()
    page = _estimate_page_number(text, match.start())
    return SourceSpan(
        page=page,
        text_excerpt=matched_text[:300],
        bbox=None,
    )


def _estimate_page_number(text: str, char_index: int) -> int:
    """
    Simple heuristic page estimate based on form-feed or page markers.
    If none exist, return page 1.
    """
    if "\f" in text:
        return text[:char_index].count("\f") + 1
    return 1


def _estimate_confidence(value: str) -> float:
    if not value:
        return 0.2

    value = value.strip()
    if len(value) >= 20:
        return 0.92
    if len(value) >= 8:
        return 0.85
    if len(value) >= 4:
        return 0.75
    return 0.6


def _confidence_level(score: float) -> ConfidenceLevel:
    if score >= 0.85:
        return ConfidenceLevel.HIGH
    if score >= 0.65:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def _normalize_amount(value: str | None) -> float | None:
    if not value:
        return None

    cleaned = value.strip()
    cleaned = cleaned.replace(" ", "")
    cleaned = cleaned.replace(",", "")

    cleaned = re.sub(r"[^\d\.\-]", "", cleaned)

    try:
        return float(cleaned)
    except ValueError:
        return None


def _normalize_currency(value: str | None) -> str | None:
    if not value:
        return None

    mapping = {
        "€": "EUR",
        "$": "USD",
        "£": "GBP",
    }
    value = value.strip().upper()
    return mapping.get(value, value)


def _normalize_date_string(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip()


def _normalize_company_name(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s{2,}", " ", value.strip().title())


def _safe_float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None