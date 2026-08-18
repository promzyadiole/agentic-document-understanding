from __future__ import annotations

import json
from pathlib import Path

from app.core.config import get_settings
from app.models.schemas import InboundMessage


def _store_path() -> Path:
    settings = get_settings()
    processed_dir = Path(settings.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / "inbound_messages.json"


def _load_raw() -> list[dict]:
    path = _store_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(records: list[dict]) -> None:
    with _store_path().open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)


def list_inbound() -> list[InboundMessage]:
    return [InboundMessage.model_validate(item) for item in _load_raw()]


def create_inbound(message: InboundMessage) -> InboundMessage:
    records = _load_raw()
    records.append(message.model_dump(mode="json"))
    _save_raw(records)
    return message
