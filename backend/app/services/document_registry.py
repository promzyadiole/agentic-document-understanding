from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.config import get_settings


def _registry_path() -> Path:
    settings = get_settings()
    processed_dir = Path(settings.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / "document_registry.json"


def load_document_registry() -> list[dict[str, Any]]:
    path = _registry_path()
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_document_registry(records: list[dict[str, Any]]) -> None:
    path = _registry_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def append_document_record(record: dict[str, Any]) -> None:
    records = load_document_registry()
    records.append(record)
    save_document_registry(records)