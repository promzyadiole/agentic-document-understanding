from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from app.models.enums import ExtractionMethod
from app.models.schemas import DocumentMetadata, ParsedDocument


def extract_text_from_pdf(file_path: str | Path, project_id: str | None = None) -> ParsedDocument:
    """
    Extract text from a PDF using native PDF parsing.

    Returns a ParsedDocument object containing:
    - metadata
    - raw_text
    - cleaned_text (initially same as raw_text)
    - extraction method
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    doc = fitz.open(path)
    page_texts: list[str] = []

    for page in doc:
        text = page.get_text("text")
        if text:
            page_texts.append(text)

    raw_text = "\n\n".join(page_texts).strip()

    metadata = DocumentMetadata(
        document_id=path.stem,
        filename=path.name,
        content_type="application/pdf",
        file_size=path.stat().st_size,
        page_count=len(doc),
        project_id=project_id,
    )

    doc.close()

    return ParsedDocument(
        metadata=metadata,
        raw_text=raw_text,
        cleaned_text=raw_text,
        extraction_method=ExtractionMethod.NATIVE_PDF,
        detected_language="en",
    )


def extract_text_by_page(file_path: str | Path) -> list[dict]:
    """
    Extract page-level text for future provenance and chunking.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    doc = fitz.open(path)
    pages: list[dict] = []

    for idx, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        pages.append(
            {
                "page": idx,
                "text": text.strip(),
                "char_count": len(text.strip()),
            }
        )

    doc.close()
    return pages


def is_likely_scanned_pdf(file_path: str | Path, min_text_threshold: int = 50) -> bool:
    """
    Heuristic to detect scanned PDFs.
    If average extracted text is extremely low, assume OCR is needed.
    """
    pages = extract_text_by_page(file_path)
    if not pages:
        return True

    avg_chars = sum(page["char_count"] for page in pages) / len(pages)
    return avg_chars < min_text_threshold