from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import (
    ConfidenceLevel,
    DocumentType,
    ExtractionMethod,
    KPIType,
    LeadStatus,
    ProcessingStatus,
    ValidationStatus,
)


class SourceSpan(BaseModel):
    page: int = Field(..., ge=1)
    text_excerpt: str = ""
    bbox: list[float] | None = None


class ExtractedField(BaseModel):
    name: str
    value: Any = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel = ConfidenceLevel.LOW
    source_spans: list[SourceSpan] = Field(default_factory=list)
    normalized_value: Any | None = None


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    content_type: str | None = None
    file_size: int | None = None
    page_count: int | None = None
    project_id: str | None = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ParsedDocument(BaseModel):
    metadata: DocumentMetadata
    raw_text: str = ""
    cleaned_text: str = ""
    extraction_method: ExtractionMethod = ExtractionMethod.NATIVE_PDF
    detected_language: str | None = None


class ClassificationResult(BaseModel):
    document_type: DocumentType = DocumentType.UNKNOWN
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str = ""


class PurchaseOrderData(BaseModel):
    po_number: ExtractedField | None = None
    supplier_name: ExtractedField | None = None
    buyer_name: ExtractedField | None = None
    issue_date: ExtractedField | None = None
    currency: ExtractedField | None = None
    total_amount: ExtractedField | None = None
    line_items: list[dict[str, Any]] = Field(default_factory=list)


class DeliveryNoteData(BaseModel):
    delivery_note_number: ExtractedField | None = None
    po_number: ExtractedField | None = None
    supplier_name: ExtractedField | None = None
    delivery_date: ExtractedField | None = None
    received_items: list[dict[str, Any]] = Field(default_factory=list)


class InvoiceData(BaseModel):
    invoice_number: ExtractedField | None = None
    po_number: ExtractedField | None = None
    supplier_name: ExtractedField | None = None
    invoice_date: ExtractedField | None = None
    due_date: ExtractedField | None = None
    currency: ExtractedField | None = None
    subtotal: ExtractedField | None = None
    tax_amount: ExtractedField | None = None
    total_amount: ExtractedField | None = None
    line_items: list[dict[str, Any]] = Field(default_factory=list)


class FinancialReportData(BaseModel):
    company_name: ExtractedField | None = None
    reporting_period: ExtractedField | None = None
    revenue: ExtractedField | None = None
    operating_income: ExtractedField | None = None
    net_income: ExtractedField | None = None
    total_assets: ExtractedField | None = None
    total_liabilities: ExtractedField | None = None
    cash_flow_operating: ExtractedField | None = None
    key_sections: list[str] = Field(default_factory=list)


class SiteReportData(BaseModel):
    project_name: ExtractedField | None = None
    site_location: ExtractedField | None = None
    report_date: ExtractedField | None = None
    contractor_name: ExtractedField | None = None
    summary: ExtractedField | None = None
    issues: list[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    document_id: str
    document_type: DocumentType
    fields: dict[str, ExtractedField] = Field(default_factory=dict)
    structured_data: (
        PurchaseOrderData
        | DeliveryNoteData
        | InvoiceData
        | FinancialReportData
        | SiteReportData
        | dict[str, Any]
        | None
    ) = None
    processing_status: ProcessingStatus = ProcessingStatus.EXTRACTED
    classification_confidence: float | None = None
    extraction_notes: list[str] = Field(default_factory=list)
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationIssue(BaseModel):
    field_name: str
    message: str
    status: ValidationStatus
    expected_value: Any | None = None
    actual_value: Any | None = None


class ValidationResult(BaseModel):
    document_id: str
    overall_status: ValidationStatus = ValidationStatus.PASS
    issues: list[ValidationIssue] = Field(default_factory=list)
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class RAGChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    page: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    question: str
    project_id: str | None = None
    document_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class QuerySource(BaseModel):
    document_id: str
    filename: str | None = None
    page: int | None = None
    excerpt: str


class QueryResponseData(BaseModel):
    answer: str
    sources: list[QuerySource] = Field(default_factory=list)
    grounded: bool = True


class KPIRecord(BaseModel):
    kpi_name: KPIType
    value: float
    document_id: str | None = None
    project_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LeadCompany(BaseModel):
    company_name: str
    website: str | None = None
    location: str | None = None
    summary: str = ""
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    status: LeadStatus = LeadStatus.DISCOVERED


class EmailDraft(BaseModel):
    company_name: str
    recipient_email: str | None = None
    subject: str
    body: str
    approval_required: bool = True
    approved: bool = False

class LeadSearchRequest(BaseModel):
    query: str = "top construction companies with complex multi-project operations and digital workflow needs"
    max_results: int = Field(default=10, ge=1, le=20)
    location_hint: str | None = None


class EmailDraftRequest(BaseModel):
    company_name: str
    company_summary: str
    website: str | None = None
    location: str | None = None
    recipient_email: str | None = None