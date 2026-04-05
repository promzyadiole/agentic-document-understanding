from __future__ import annotations

from app.models.schemas import ExtractionResult, ValidationResult


def compute_system_quality_score(
    extraction: ExtractionResult | None,
    validation: ValidationResult | None,
) -> float:
    """
    Lightweight composite score for interview/demo use.

    Formula:
    0.45 * extraction confidence proxy
    0.35 * validation score
    0.20 * field completeness
    """
    if extraction is None:
        return 0.0

    extraction_conf = extraction.classification_confidence or 0.0
    validation_score = validation.score if validation is not None else 0.0

    total_fields = len(extraction.fields)
    filled_fields = sum(
        1 for field in extraction.fields.values()
        if field.value is not None and str(field.value).strip() != ""
    )
    completeness = (filled_fields / total_fields) if total_fields > 0 else 0.0

    score = (
        0.45 * extraction_conf
        + 0.35 * validation_score
        + 0.20 * completeness
    )

    return round(score, 4)