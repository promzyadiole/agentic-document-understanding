from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI

from app.core.config import get_settings
from app.models.enums import DocumentType
from app.services.chunking import chunk_text
from app.services.classifier import classify_document
from app.services.extraction import extract_document_data
from app.services.kpi import log_extraction_kpis
from app.services.kpi_eval import compute_system_quality_score
from app.services.ocr import ocr_image, ocr_pdf
from app.services.pdf_parser import extract_text_from_pdf, is_likely_scanned_pdf
from app.services.rag import upsert_chunks
from app.services.text_cleaning import clean_ocr_text
from app.services.validation import validate_extraction_result
from app.workflows.state import DocumentWorkflowState

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


def document_intake_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    file_path = state["file_path"]
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        if is_likely_scanned_pdf(file_path):
            parsed = ocr_pdf(file_path, project_id=state.get("project_id"))
        else:
            parsed = extract_text_from_pdf(file_path, project_id=state.get("project_id"))
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        parsed = ocr_image(file_path, project_id=state.get("project_id"))
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return {
        **state,
        "parsed_document": parsed,
        "filename": parsed.metadata.filename,
        "namespace": parsed.metadata.project_id or "default",
        "steps_taken": ["document_intake"],
        "loop_count": 0,
        "max_loops": state.get("max_loops", 8),
    }


def agent_reason_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    parsed = state.get("parsed_document")
    classification = state.get("classification")
    extraction = state.get("extraction")
    validation = state.get("validation")
    steps_taken = state.get("steps_taken", [])
    loop_count = state.get("loop_count", 0)
    max_loops = state.get("max_loops", 8)
    agent_history = state.get("agent_history", [])

    if loop_count >= max_loops:
        action = "finish"
        reasoning = "Maximum loop count reached; stopping workflow."
        updated_history = agent_history + [
            {
                "action": action,
                "reasoning": reasoning,
                "loop_count": loop_count + 1,
            }
        ]
        return {
            **state,
            "agent_action": action,
            "agent_reasoning": reasoning,
            "agent_history": updated_history,
            "loop_count": loop_count + 1,
        }

    prompt = f"""
You are the controller of an agentic document-understanding workflow.

Available actions:
- clean_text
- classify_document
- index_document
- extract_fields
- validate_document
- log_kpis
- finish

Your job is to choose the NEXT best action based on current state.

Rules:
1. If cleaned_text is empty or missing but raw_text exists, prefer clean_text.
2. If document classification is missing, prefer classify_document.
3. If indexing has not happened yet, prefer index_document.
4. If classification exists and is not unknown, but extraction is missing, prefer extract_fields.
5. If extraction exists but validation is missing, prefer validate_document.
6. If validation exists and KPIs have not yet been logged, prefer log_kpis.
7. If validation score is good enough or work is complete, choose finish.
8. If classification is unknown and already attempted, you may still choose index_document then finish.
9. Avoid repeating the same action too many times.

Return ONLY valid JSON:
{{
  "action": "one_of_the_actions_above",
  "reasoning": "short reason"
}}

Current state summary:
- has_raw_text: {bool(parsed and parsed.raw_text)}
- has_cleaned_text: {bool(parsed and parsed.cleaned_text)}
- classification: {classification.document_type.value if classification else None}
- classification_confidence: {classification.confidence_score if classification else None}
- has_extraction: {extraction is not None}
- has_validation: {validation is not None}
- validation_score: {validation.score if validation else None}
- indexed_chunk_count: {state.get("indexed_chunk_count")}
- steps_taken: {steps_taken}
- loop_count: {loop_count}
""".strip()

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a workflow controller. Return strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        data = json.loads(content)

        action = data.get("action", "finish")
        reasoning = data.get("reasoning", "No reasoning provided.")
    except Exception:
        action, reasoning = _fallback_agent_decision(state)

    updated_history = agent_history + [
        {
            "action": action,
            "reasoning": reasoning,
            "loop_count": loop_count + 1,
        }
    ]

    return {
        **state,
        "agent_action": action,
        "agent_reasoning": reasoning,
        "agent_history": updated_history,
        "loop_count": loop_count + 1,
    }


def _fallback_agent_decision(state: DocumentWorkflowState) -> tuple[str, str]:
    parsed = state.get("parsed_document")
    classification = state.get("classification")
    extraction = state.get("extraction")
    validation = state.get("validation")
    steps_taken = state.get("steps_taken", [])

    if parsed and parsed.raw_text and not parsed.cleaned_text:
        return "clean_text", "Fallback: cleaned text missing."
    if classification is None:
        return "classify_document", "Fallback: classification missing."
    if "index_document" not in steps_taken:
        return "index_document", "Fallback: indexing not yet performed."
    if classification and classification.document_type != DocumentType.UNKNOWN and extraction is None:
        return "extract_fields", "Fallback: extraction missing for known document type."
    if extraction is not None and validation is None:
        return "validate_document", "Fallback: validation missing."
    if validation is not None and "log_kpis" not in steps_taken:
        return "log_kpis", "Fallback: KPI logging missing."
    return "finish", "Fallback: workflow appears complete."


def clean_text_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    parsed = state["parsed_document"]
    parsed.cleaned_text = clean_ocr_text(parsed.raw_text)

    steps_taken = state.get("steps_taken", []) + ["clean_text"]
    return {
        **state,
        "parsed_document": parsed,
        "steps_taken": steps_taken,
    }


def classify_document_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    parsed = state["parsed_document"]
    classification = classify_document(parsed.cleaned_text)

    steps_taken = state.get("steps_taken", []) + ["classify_document"]
    return {
        **state,
        "classification": classification,
        "steps_taken": steps_taken,
    }


def index_document_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    parsed = state["parsed_document"]
    classification = state.get("classification")

    doc_type = classification.document_type.value if classification else "unknown"

    chunks = chunk_text(
        document_id=parsed.metadata.document_id,
        text=parsed.cleaned_text,
        metadata={
            "filename": parsed.metadata.filename,
            "content_type": parsed.metadata.content_type,
            "document_type": doc_type,
            "project_id": parsed.metadata.project_id,
        },
    )

    indexed_count = upsert_chunks(
        chunks,
        namespace=state.get("namespace", "default"),
    )

    steps_taken = state.get("steps_taken", []) + ["index_document"]
    return {
        **state,
        "indexed_chunk_count": indexed_count,
        "steps_taken": steps_taken,
    }


def extract_fields_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    parsed = state["parsed_document"]
    classification = state.get("classification")

    if classification is None or classification.document_type == DocumentType.UNKNOWN:
        steps_taken = state.get("steps_taken", []) + ["extract_fields_skipped"]
        return {
            **state,
            "extraction": None,
            "steps_taken": steps_taken,
        }

    extraction = extract_document_data(
        document_id=parsed.metadata.document_id,
        text=parsed.cleaned_text,
        document_type=classification.document_type,
        classification_confidence=classification.confidence_score,
    )

    steps_taken = state.get("steps_taken", []) + ["extract_fields"]
    return {
        **state,
        "extraction": extraction,
        "steps_taken": steps_taken,
    }


def validate_document_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    extraction = state.get("extraction")

    if extraction is None:
        steps_taken = state.get("steps_taken", []) + ["validate_document_skipped"]
        return {
            **state,
            "validation": None,
            "steps_taken": steps_taken,
        }

    validation = validate_extraction_result(extraction)
    extraction.extraction_notes.append(
        f"Validation status: {validation.overall_status.value}; validation score: {validation.score}"
    )

    steps_taken = state.get("steps_taken", []) + ["validate_document"]
    return {
        **state,
        "extraction": extraction,
        "validation": validation,
        "steps_taken": steps_taken,
    }


def log_kpis_node(state: DocumentWorkflowState) -> DocumentWorkflowState:
    extraction = state.get("extraction")
    validation = state.get("validation")

    if extraction is None:
        steps_taken = state.get("steps_taken", []) + ["log_kpis_skipped"]
        return {
            **state,
            "steps_taken": steps_taken,
        }

    log_extraction_kpis(
        extraction=extraction,
        validation=validation,
        project_id=state.get("project_id"),
    )

    quality_score = compute_system_quality_score(extraction, validation)
    extraction.extraction_notes.append(f"System quality score: {quality_score}")
    extraction.extraction_notes.append(
        f"Indexed {state.get('indexed_chunk_count', 0)} chunks into namespace '{state.get('namespace', 'default')}'"
    )

    steps_taken = state.get("steps_taken", []) + ["log_kpis"]
    return {
        **state,
        "extraction": extraction,
        "steps_taken": steps_taken,
    }