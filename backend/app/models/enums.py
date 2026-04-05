from enum import Enum


class DocumentType(str, Enum):
    PURCHASE_ORDER = "purchase_order"
    DELIVERY_NOTE = "delivery_note"
    INVOICE = "invoice"
    FINANCIAL_REPORT = "financial_report"
    SITE_REPORT = "site_report"
    UNKNOWN = "unknown"


class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSED = "parsed"
    CLASSIFIED = "classified"
    EXTRACTED = "extracted"
    INDEXED = "indexed"
    VALIDATED = "validated"
    FAILED = "failed"


class ExtractionMethod(str, Enum):
    NATIVE_PDF = "native_pdf"
    OCR = "ocr"
    HYBRID = "hybrid"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class LeadStatus(str, Enum):
    DISCOVERED = "discovered"
    SCORED = "scored"
    DRAFTED = "drafted"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"


class KPIType(str, Enum):
    EXTRACTION_ACCURACY = "extraction_accuracy"
    FIELD_COVERAGE = "field_coverage"
    SCHEMA_VALIDITY = "schema_validity"
    RETRIEVAL_RELEVANCE = "retrieval_relevance"
    GROUNDED_ANSWER_RATE = "grounded_answer_rate"
    LATENCY = "latency"
    HUMAN_CORRECTION_RATE = "human_correction_rate"
    APPROVAL_RATE = "approval_rate"