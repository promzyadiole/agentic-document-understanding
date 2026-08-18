from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.models.enums import DocumentType
from app.models.responses import (
    DocumentProcessingResponse,
    ExtractionResponse,
    ValidationResponse,
)
from app.services.document_registry import append_document_record, load_document_registry
from app.services.extraction import extract_document_data
from app.services.storage import save_upload_file
from app.services.text_cleaning import clean_ocr_text
from app.services.validation import validate_extraction_result
from app.workflows.graph import document_workflow

router = APIRouter()


def _agent_trace(result: dict) -> dict:
    return {
        "agent_action": result.get("agent_action"),
        "agent_reasoning": result.get("agent_reasoning"),
        "steps_taken": result.get("steps_taken", []),
        "loop_count": result.get("loop_count"),
        "history": result.get("agent_history", []),
    }


def _persist_document_record(result: dict) -> None:
    parsed = result["parsed_document"]
    classification = result.get("classification")
    validation = result.get("validation")
    append_document_record(
        {
            "document_id": parsed.metadata.document_id,
            "filename": parsed.metadata.filename,
            "content_type": parsed.metadata.content_type,
            "page_count": parsed.metadata.page_count,
            "project_id": parsed.metadata.project_id,
            "document_type": classification.document_type.value if classification else "unknown",
            "classification_confidence": classification.confidence_score if classification else 0.0,
            "validation_status": validation.overall_status.value if validation else None,
            "extraction": result["extraction"].model_dump(mode="json") if result.get("extraction") else None,
            "agent_trace": _agent_trace(result),
        }
    )


def _build_processing_response(result: dict) -> DocumentProcessingResponse:
    return DocumentProcessingResponse(
        message="Document uploaded and processed successfully through LangGraph workflow.",
        parsed_document=result.get("parsed_document"),
        classification=result.get("classification"),
        extraction=result.get("extraction"),
        validation=result.get("validation"),
        agent_trace=_agent_trace(result),
    )


@router.get("")
def list_documents():
    return {"documents": [], "message": "Documents endpoint ready"}


@router.post("/upload", response_model=DocumentProcessingResponse)
def upload_and_process_document(file: UploadFile = File(...), project_id: str | None = None):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    saved_path = save_upload_file(file)

    try:
        state = {
            "file_path": str(saved_path),
            "filename": Path(saved_path).name,
            "project_id": project_id,
        }

        result = document_workflow.invoke(state)
        _persist_document_record(result)
        return _build_processing_response(result)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Human-readable labels for each workflow node, surfaced in the live trace UI.
_NODE_LABELS = {
    "document_intake": "Reading & parsing document",
    "agent_reason": "Agent deciding next action",
    "clean_text": "Cleaning extracted text",
    "classify_document": "Classifying document type",
    "index_document": "Indexing into vector store",
    "extract_fields": "Extracting structured fields",
    "validate_document": "Validating extraction",
    "log_kpis": "Logging quality KPIs",
}


@router.post("/upload/stream")
def upload_and_stream_document(file: UploadFile = File(...), project_id: str | None = None):
    """
    Same pipeline as /upload, but streams the agent's reasoning live via
    Server-Sent Events so the UI can show the LangGraph loop thinking in
    real time. Emits one `node` event per workflow step and a final `done`
    event carrying the complete result.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    saved_path = save_upload_file(file)

    def event_stream():
        state = {
            "file_path": str(saved_path),
            "filename": Path(saved_path).name,
            "project_id": project_id,
        }

        def sse(payload: dict) -> str:
            return f"data: {json.dumps(payload)}\n\n"

        yield sse({"type": "start", "filename": Path(saved_path).name})

        final_state: dict = {}
        try:
            # Our nodes return the full merged state, so each streamed update is
            # a complete snapshot we can both surface and accumulate.
            for chunk in document_workflow.stream(state, stream_mode="updates"):
                for node_name, node_state in chunk.items():
                    if not isinstance(node_state, dict):
                        continue
                    final_state = node_state
                    yield sse(
                        {
                            "type": "node",
                            "node": node_name,
                            "label": _NODE_LABELS.get(node_name, node_name),
                            "agent_action": node_state.get("agent_action"),
                            "agent_reasoning": node_state.get("agent_reasoning"),
                            "steps_taken": node_state.get("steps_taken", []),
                            "loop_count": node_state.get("loop_count"),
                        }
                    )

            if final_state.get("parsed_document") is not None:
                _persist_document_record(final_state)
                response = _build_processing_response(final_state)
                yield sse({"type": "done", "result": response.model_dump(mode="json")})
            else:
                yield sse({"type": "error", "detail": "Workflow produced no parsed document."})
        except Exception as exc:  # noqa: BLE001 - surface any failure to the client
            yield sse({"type": "error", "detail": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/extract", response_model=ExtractionResponse)
def extract_from_text(document_id: str, document_type: DocumentType, text: str):
    try:
        result = extract_document_data(
            document_id=document_id,
            text=clean_ocr_text(text),
            document_type=document_type,
        )
        return ExtractionResponse(
            message="Extraction completed successfully.",
            result=result,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/validate", response_model=ValidationResponse)
def validate_document_extraction(document_id: str, document_type: DocumentType, text: str):
    try:
        extraction = extract_document_data(
            document_id=document_id,
            text=clean_ocr_text(text),
            document_type=document_type,
        )
        validation = validate_extraction_result(extraction)

        return ValidationResponse(
            message="Validation completed successfully.",
            result=validation,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/history")
def get_document_history():
    return {
        "documents": load_document_registry(),
    }

@router.get("/latest")
def get_latest_document():
    documents = load_document_registry()
    if not documents:
        return {"document": None}
    return {"document": documents[-1]}