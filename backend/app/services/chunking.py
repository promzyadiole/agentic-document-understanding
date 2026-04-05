from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.models.schemas import RAGChunk


def chunk_text(
    document_id: str,
    text: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> list[RAGChunk]:
    """
    Simple paragraph-aware chunker with overlap.
    """
    settings = get_settings()
    chunk_size = settings.max_chunk_size
    chunk_overlap = settings.chunk_overlap

    text = (text or "").strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[RAGChunk] = []

    current = ""
    chunk_index = 0

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(
                RAGChunk(
                    chunk_id=f"{document_id}_chunk_{chunk_index}",
                    document_id=document_id,
                    text=current,
                    page=None,
                    metadata=metadata or {},
                )
            )
            chunk_index += 1

            overlap_text = current[-chunk_overlap:] if chunk_overlap > 0 else ""
            current = f"{overlap_text}\n\n{para}".strip()
        else:
            # very long paragraph fallback
            start = 0
            while start < len(para):
                end = min(start + chunk_size, len(para))
                piece = para[start:end]
                chunks.append(
                    RAGChunk(
                        chunk_id=f"{document_id}_chunk_{chunk_index}",
                        document_id=document_id,
                        text=piece,
                        page=None,
                        metadata=metadata or {},
                    )
                )
                chunk_index += 1
                start = max(end - chunk_overlap, end)

            current = ""

    if current:
        chunks.append(
            RAGChunk(
                chunk_id=f"{document_id}_chunk_{chunk_index}",
                document_id=document_id,
                text=current,
                page=None,
                metadata=metadata or {},
            )
        )

    return chunks