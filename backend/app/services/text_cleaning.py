from __future__ import annotations

import re


def clean_ocr_text(text: str) -> str:
    """
    Normalize OCR/native extracted text so downstream extraction is more stable.
    """
    if not text:
        return ""

    cleaned = text

    # Normalize line endings
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    # Remove repeated spaces/tabs
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Remove excessive blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Fix common OCR spacing around punctuation
    cleaned = re.sub(r"\s+([,.:;])", r"\1", cleaned)

    # Normalize broken currency spacing like "€ 1 234" -> "€ 1234"
    cleaned = re.sub(r"([€$£])\s+", r"\1", cleaned)

    # Trim each line
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())

    # Final strip
    cleaned = cleaned.strip()

    return cleaned


def normalize_for_matching(text: str) -> str:
    """
    Lightweight normalization for fuzzy comparisons and document rules.
    """
    if not text:
        return ""

    normalized = text.lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[^a-z0-9\s\-_/.:]", "", normalized)
    return normalized.strip()