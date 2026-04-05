from __future__ import annotations

from typing import Any

from app.models.enums import DocumentType, ValidationStatus
from app.models.schemas import (
    DeliveryNoteData,
    ExtractionResult,
    InvoiceData,
    PurchaseOrderData,
    ValidationIssue,
    ValidationResult,
)


def validate_extraction_result(result: ExtractionResult) -> ValidationResult:
    """
    Validate a single extracted document result.
    """
    issues: list[ValidationIssue] = []

    if result.document_type == DocumentType.PURCHASE_ORDER:
        issues.extend(_validate_purchase_order(result.structured_data))
    elif result.document_type == DocumentType.DELIVERY_NOTE:
        issues.extend(_validate_delivery_note(result.structured_data))
    elif result.document_type == DocumentType.INVOICE:
        issues.extend(_validate_invoice(result.structured_data))
    elif result.document_type == DocumentType.FINANCIAL_REPORT:
        issues.extend(_validate_financial_report(result.structured_data))
    elif result.document_type == DocumentType.SITE_REPORT:
        issues.extend(_validate_site_report(result.structured_data))

    overall_status = _aggregate_status(issues)
    score = _compute_validation_score(issues)

    return ValidationResult(
        document_id=result.document_id,
        overall_status=overall_status,
        issues=issues,
        score=score,
    )


def validate_document_pair(
    primary: ExtractionResult,
    secondary: ExtractionResult,
) -> ValidationResult:
    """
    Cross-document validation, e.g. PO vs Invoice, PO vs Delivery Note.
    """
    issues: list[ValidationIssue] = []

    p_data = primary.structured_data
    s_data = secondary.structured_data

    # PO number consistency
    primary_po = _get_normalized_field_value(p_data, "po_number")
    secondary_po = _get_normalized_field_value(s_data, "po_number")

    if primary_po and secondary_po:
        if primary_po != secondary_po:
            issues.append(
                ValidationIssue(
                    field_name="po_number",
                    message="PO number mismatch across documents.",
                    status=ValidationStatus.FAIL,
                    expected_value=primary_po,
                    actual_value=secondary_po,
                )
            )
    elif primary_po or secondary_po:
        issues.append(
            ValidationIssue(
                field_name="po_number",
                message="PO number missing in one of the documents.",
                status=ValidationStatus.WARNING,
                expected_value=primary_po,
                actual_value=secondary_po,
            )
        )

    # Supplier consistency
    primary_supplier = _get_normalized_field_value(p_data, "supplier_name")
    secondary_supplier = _get_normalized_field_value(s_data, "supplier_name")

    if primary_supplier and secondary_supplier:
        if primary_supplier != secondary_supplier:
            issues.append(
                ValidationIssue(
                    field_name="supplier_name",
                    message="Supplier name mismatch across documents.",
                    status=ValidationStatus.FAIL,
                    expected_value=primary_supplier,
                    actual_value=secondary_supplier,
                )
            )
    elif primary_supplier or secondary_supplier:
        issues.append(
            ValidationIssue(
                field_name="supplier_name",
                message="Supplier name missing in one of the documents.",
                status=ValidationStatus.WARNING,
                expected_value=primary_supplier,
                actual_value=secondary_supplier,
            )
        )

    # Total amount consistency when available
    primary_total = _get_numeric_normalized_field_value(p_data, "total_amount")
    secondary_total = _get_numeric_normalized_field_value(s_data, "total_amount")

    if primary_total is not None and secondary_total is not None:
        if abs(primary_total - secondary_total) > 0.01:
            issues.append(
                ValidationIssue(
                    field_name="total_amount",
                    message="Total amount mismatch across documents.",
                    status=ValidationStatus.WARNING,
                    expected_value=primary_total,
                    actual_value=secondary_total,
                )
            )

    overall_status = _aggregate_status(issues)
    score = _compute_validation_score(issues)

    return ValidationResult(
        document_id=f"{primary.document_id}__vs__{secondary.document_id}",
        overall_status=overall_status,
        issues=issues,
        score=score,
    )


def _validate_purchase_order(data: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(data, PurchaseOrderData):
        return [
            ValidationIssue(
                field_name="structured_data",
                message="Invalid structured data for purchase order validation.",
                status=ValidationStatus.FAIL,
            )
        ]

    issues.extend(_check_required_fields(data, ["po_number", "supplier_name", "issue_date", "total_amount"]))

    total_amount = _get_numeric_normalized_field_value(data, "total_amount")
    if total_amount is not None and total_amount <= 0:
        issues.append(
            ValidationIssue(
                field_name="total_amount",
                message="Total amount must be greater than zero.",
                status=ValidationStatus.FAIL,
                actual_value=total_amount,
            )
        )

    return issues


def _validate_delivery_note(data: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(data, DeliveryNoteData):
        return [
            ValidationIssue(
                field_name="structured_data",
                message="Invalid structured data for delivery note validation.",
                status=ValidationStatus.FAIL,
            )
        ]

    issues.extend(_check_required_fields(data, ["delivery_note_number", "supplier_name"]))

    if not data.received_items:
        issues.append(
            ValidationIssue(
                field_name="received_items",
                message="No received items were extracted from the delivery note.",
                status=ValidationStatus.WARNING,
            )
        )

    return issues


def _validate_invoice(data: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(data, InvoiceData):
        return [
            ValidationIssue(
                field_name="structured_data",
                message="Invalid structured data for invoice validation.",
                status=ValidationStatus.FAIL,
            )
        ]

    issues.extend(_check_required_fields(data, ["invoice_number", "supplier_name", "invoice_date", "total_amount"]))

    subtotal = _get_numeric_normalized_field_value(data, "subtotal")
    tax_amount = _get_numeric_normalized_field_value(data, "tax_amount")
    total_amount = _get_numeric_normalized_field_value(data, "total_amount")

    if total_amount is not None and total_amount <= 0:
        issues.append(
            ValidationIssue(
                field_name="total_amount",
                message="Invoice total amount must be greater than zero.",
                status=ValidationStatus.FAIL,
                actual_value=total_amount,
            )
        )

    if subtotal is not None and tax_amount is not None and total_amount is not None:
        expected_total = round(subtotal + tax_amount, 2)
        if abs(expected_total - total_amount) > 0.01:
            issues.append(
                ValidationIssue(
                    field_name="total_amount",
                    message="Invoice total does not match subtotal + tax.",
                    status=ValidationStatus.WARNING,
                    expected_value=expected_total,
                    actual_value=total_amount,
                )
            )

    return issues


def _validate_financial_report(data: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    required_soft = ["company_name", "reporting_period"]
    issues.extend(_check_required_fields(data, required_soft, missing_status=ValidationStatus.WARNING))

    key_numeric_fields = [
        "revenue",
        "operating_income",
        "net_income",
        "total_assets",
        "total_liabilities",
    ]

    missing_numeric_count = 0
    for field_name in key_numeric_fields:
        value = _get_numeric_normalized_field_value(data, field_name)
        if value is None:
            missing_numeric_count += 1

    if missing_numeric_count >= 4:
        issues.append(
            ValidationIssue(
                field_name="financial_metrics",
                message="Most key financial metrics were not extracted.",
                status=ValidationStatus.WARNING,
            )
        )

    return issues


def _validate_site_report(data: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    required_soft = ["project_name", "report_date"]
    issues.extend(_check_required_fields(data, required_soft, missing_status=ValidationStatus.WARNING))

    return issues


def _check_required_fields(
    data: Any,
    field_names: list[str],
    *,
    missing_status: ValidationStatus = ValidationStatus.FAIL,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for field_name in field_names:
        field_obj = getattr(data, field_name, None)
        value = getattr(field_obj, "value", None) if field_obj is not None else None

        if value is None or str(value).strip() == "":
            issues.append(
                ValidationIssue(
                    field_name=field_name,
                    message=f"Required field '{field_name}' is missing.",
                    status=missing_status,
                )
            )

    return issues


def _get_normalized_field_value(data: Any, field_name: str) -> str | None:
    field_obj = getattr(data, field_name, None)
    if field_obj is None:
        return None

    normalized = getattr(field_obj, "normalized_value", None)
    raw_value = getattr(field_obj, "value", None)

    if normalized is not None:
        return str(normalized).strip().lower()

    if raw_value is not None:
        return str(raw_value).strip().lower()

    return None


def _get_numeric_normalized_field_value(data: Any, field_name: str) -> float | None:
    field_obj = getattr(data, field_name, None)
    if field_obj is None:
        return None

    normalized = getattr(field_obj, "normalized_value", None)
    raw_value = getattr(field_obj, "value", None)

    if isinstance(normalized, (int, float)):
        return float(normalized)

    if isinstance(raw_value, (int, float)):
        return float(raw_value)

    return None


def _aggregate_status(issues: list[ValidationIssue]) -> ValidationStatus:
    if any(issue.status == ValidationStatus.FAIL for issue in issues):
        return ValidationStatus.FAIL
    if any(issue.status == ValidationStatus.WARNING for issue in issues):
        return ValidationStatus.WARNING
    return ValidationStatus.PASS


def _compute_validation_score(issues: list[ValidationIssue]) -> float:
    """
    Simple scoring rule:
    - FAIL reduces more than WARNING
    - empty issues => perfect score
    """
    score = 1.0

    for issue in issues:
        if issue.status == ValidationStatus.FAIL:
            score -= 0.25
        elif issue.status == ValidationStatus.WARNING:
            score -= 0.10

    return max(0.0, round(score, 2))