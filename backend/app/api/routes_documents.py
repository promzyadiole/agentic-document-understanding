from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

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

        append_document_record(
            {
                "document_id": result["parsed_document"].metadata.document_id,
                "filename": result["parsed_document"].metadata.filename,
                "content_type": result["parsed_document"].metadata.content_type,
                "page_count": result["parsed_document"].metadata.page_count,
                "project_id": result["parsed_document"].metadata.project_id,
                "document_type": (
                    result["classification"].document_type.value
                    if result.get("classification") is not None
                    else "unknown"
                ),
                "classification_confidence": (
                    result["classification"].confidence_score
                    if result.get("classification") is not None
                    else 0.0
                ),
                "validation_status": (
                    result["validation"].overall_status.value
                    if result.get("validation") is not None
                    else None
                ),
                "agent_trace": {
                    "agent_action": result.get("agent_action"),
                    "agent_reasoning": result.get("agent_reasoning"),
                    "steps_taken": result.get("steps_taken", []),
                    "loop_count": result.get("loop_count"),
                    "history": result.get("agent_history", []),
                },
            }
        )

        return DocumentProcessingResponse(
            message="Document uploaded and processed successfully through LangGraph workflow.",
            parsed_document=result.get("parsed_document"),
            classification=result.get("classification"),
            extraction=result.get("extraction"),
            validation=result.get("validation"),
            agent_trace={
                "agent_action": result.get("agent_action"),
                "agent_reasoning": result.get("agent_reasoning"),
                "steps_taken": result.get("steps_taken", []),
                "loop_count": result.get("loop_count"),
                "history": result.get("agent_history", []),
            },
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


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