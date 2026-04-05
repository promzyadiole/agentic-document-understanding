from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from app.core.config import get_settings
from app.models.enums import KPIType, ValidationStatus
from app.models.schemas import ExtractionResult, KPIRecord, ValidationResult


def _kpi_store_path() -> Path:
    settings = get_settings()
    processed_dir = Path(settings.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / "kpi_records.json"


def load_kpi_records() -> list[KPIRecord]:
    path = _kpi_store_path()
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    return [KPIRecord.model_validate(item) for item in raw]


def save_kpi_records(records: list[KPIRecord]) -> None:
    path = _kpi_store_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump([record.model_dump(mode="json") for record in records], f, indent=2)


def append_kpi_record(record: KPIRecord) -> None:
    records = load_kpi_records()
    records.append(record)
    save_kpi_records(records)


def log_extraction_kpis(
    extraction: ExtractionResult,
    validation: ValidationResult | None = None,
    project_id: str | None = None,
) -> list[KPIRecord]:
    records: list[KPIRecord] = []

    total_fields = len(extraction.fields)
    filled_fields = sum(
        1
        for field in extraction.fields.values()
        if field.value is not None and str(field.value).strip() != ""
    )
    low_conf_fields = sum(
        1 for field in extraction.fields.values() if field.confidence_score < 0.65
    )

    field_coverage = (filled_fields / total_fields) if total_fields > 0 else 0.0
    low_confidence_rate = (low_conf_fields / total_fields) if total_fields > 0 else 0.0

    # We use classifier confidence as an early proxy for extraction accuracy.
    extraction_accuracy_proxy = extraction.classification_confidence or 0.0

    records.append(
        KPIRecord(
            kpi_name=KPIType.FIELD_COVERAGE,
            value=round(field_coverage, 4),
            document_id=extraction.document_id,
            project_id=project_id,
            metadata={
                "total_fields": total_fields,
                "filled_fields": filled_fields,
            },
        )
    )

    records.append(
        KPIRecord(
            kpi_name=KPIType.EXTRACTION_ACCURACY,
            value=round(extraction_accuracy_proxy, 4),
            document_id=extraction.document_id,
            project_id=project_id,
            metadata={
                "proxy": "classification_confidence",
                "document_type": extraction.document_type.value,
            },
        )
    )

    records.append(
        KPIRecord(
            kpi_name=KPIType.HUMAN_CORRECTION_RATE,
            value=round(low_confidence_rate, 4),
            document_id=extraction.document_id,
            project_id=project_id,
            metadata={
                "definition": "low_confidence_field_rate",
                "low_confidence_fields": low_conf_fields,
                "total_fields": total_fields,
            },
        )
    )

    if validation is not None:
        schema_validity = 1.0 if validation.overall_status == ValidationStatus.PASS else 0.0
        if validation.overall_status == ValidationStatus.WARNING:
            schema_validity = 0.5

        records.append(
            KPIRecord(
                kpi_name=KPIType.SCHEMA_VALIDITY,
                value=round(schema_validity, 4),
                document_id=extraction.document_id,
                project_id=project_id,
                metadata={
                    "validation_status": validation.overall_status.value,
                    "validation_score": validation.score,
                    "issue_count": len(validation.issues),
                },
            )
        )

    for record in records:
        append_kpi_record(record)

    return records


def summarize_kpis(records: list[KPIRecord]) -> dict[str, Any]:
    if not records:
        return {
            "total_records": 0,
            "averages": {},
        }

    grouped: dict[str, list[float]] = {}
    for record in records:
        grouped.setdefault(record.kpi_name.value, []).append(record.value)

    averages = {
        kpi_name: round(sum(values) / len(values), 4)
        for kpi_name, values in grouped.items()
        if values
    }

    return {
        "total_records": len(records),
        "averages": averages,
    }