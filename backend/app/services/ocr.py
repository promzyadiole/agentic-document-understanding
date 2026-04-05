from __future__ import annotations

from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from app.models.enums import ExtractionMethod
from app.models.schemas import DocumentMetadata, ParsedDocument


def ocr_image(image_path: str | Path, project_id: str | None = None) -> ParsedDocument:
    """
    OCR a standalone image file.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    image = Image.open(path)
    raw_text = pytesseract.image_to_string(image).strip()

    metadata = DocumentMetadata(
        document_id=path.stem,
        filename=path.name,
        content_type=f"image/{path.suffix.lower().replace('.', '')}",
        file_size=path.stat().st_size,
        page_count=1,
        project_id=project_id,
    )

    return ParsedDocument(
        metadata=metadata,
        raw_text=raw_text,
        cleaned_text=raw_text,
        extraction_method=ExtractionMethod.OCR,
        detected_language="en",
    )


def ocr_pdf(file_path: str | Path, project_id: str | None = None) -> ParsedDocument:
    """
    OCR each page of a scanned PDF by rasterizing pages and sending them to Tesseract.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pdf = fitz.open(path)
    page_texts: list[str] = []

    for page in pdf:
        pix = page.get_pixmap(dpi=200)
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(image).strip()
        page_texts.append(text)

    raw_text = "\n\n".join(page_texts).strip()

    metadata = DocumentMetadata(
        document_id=path.stem,
        filename=path.name,
        content_type="application/pdf",
        file_size=path.stat().st_size,
        page_count=len(pdf),
        project_id=project_id,
    )

    pdf.close()

    return ParsedDocument(
        metadata=metadata,
        raw_text=raw_text,
        cleaned_text=raw_text,
        extraction_method=ExtractionMethod.OCR,
        detected_language="en",
    )