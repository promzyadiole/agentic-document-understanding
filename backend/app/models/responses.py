from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.schemas import (
    ClassificationResult,
    EmailDraft,
    ExtractionResult,
    KPIRecord,
    LeadCompany,
    ParsedDocument,
    QueryResponseData,
    ValidationResult,
)


class HealthResponse(BaseModel):
    status: str = "ok"


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str


class DocumentParseResponse(BaseModel):
    message: str
    parsed_document: ParsedDocument


class AgentTraceItemResponse(BaseModel):
    action: str | None = None
    reasoning: str | None = None
    loop_count: int | None = None


class AgentTraceResponse(BaseModel):
    agent_action: str | None = None
    agent_reasoning: str | None = None
    steps_taken: list[str] = Field(default_factory=list)
    loop_count: int | None = None
    history: list[AgentTraceItemResponse] = Field(default_factory=list)


class DocumentProcessingResponse(BaseModel):
    message: str
    parsed_document: ParsedDocument
    classification: ClassificationResult | None = None
    extraction: ExtractionResult | None = None
    validation: ValidationResult | None = None
    agent_trace: AgentTraceResponse | None = None


class ExtractionResponse(BaseModel):
    message: str
    result: ExtractionResult


class ValidationResponse(BaseModel):
    message: str
    result: ValidationResult


class QueryResponseModel(BaseModel):
    message: str = "Query answered successfully"
    result: QueryResponseData


class KPIListResponse(BaseModel):
    entries: list[KPIRecord] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)


class LeadListResponse(BaseModel):
    leads: list[LeadCompany] = Field(default_factory=list)
    message: str = "Lead discovery results"


class EmailDraftResponse(BaseModel):
    message: str
    draft: EmailDraft