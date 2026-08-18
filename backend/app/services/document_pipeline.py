from __future__ import annotations

"""
Shared entry point for running a file through the LangGraph document workflow
and recording it in the registry. Used by the normal upload path, and by the
payment-confirmation and inbound-contact flows so a returned proposal PDF or an
inbound inquiry completes the exact same document-understanding pipeline.
"""

from pathlib import Path
from typing import Any

from app.services.document_registry import append_document_record
from app.workflows.graph import document_workflow


def _record_from_result(result: dict, *, source: str) -> dict:
    parsed = result["parsed_document"]
    classification = result.get("classification")
    validation = result.get("validation")
    return {
        "document_id": parsed.metadata.document_id,
        "filename": parsed.metadata.filename,
        "content_type": parsed.metadata.content_type,
        "page_count": parsed.metadata.page_count,
        "project_id": parsed.metadata.project_id,
        "source": source,
        "document_type": classification.document_type.value if classification else "unknown",
        "classification_confidence": classification.confidence_score if classification else 0.0,
        "validation_status": validation.overall_status.value if validation else None,
        "extraction": result["extraction"].model_dump(mode="json") if result.get("extraction") else None,
        "agent_trace": {
            "agent_action": result.get("agent_action"),
            "agent_reasoning": result.get("agent_reasoning"),
            "steps_taken": result.get("steps_taken", []),
            "loop_count": result.get("loop_count"),
            "history": result.get("agent_history", []),
        },
    }


def run_and_register(file_path: str, *, project_id: str | None = None, source: str = "upload") -> tuple[dict[str, Any], str]:
    """
    Invoke the document workflow on a file, persist the run to the registry, and
    return (full_result, document_id).
    """
    state = {
        "file_path": str(file_path),
        "filename": Path(file_path).name,
        "project_id": project_id,
    }
    result = document_workflow.invoke(state)
    append_document_record(_record_from_result(result, source=source))
    return result, result["parsed_document"].metadata.document_id
