from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.models.schemas import OutreachDraft, OutreachStatus


def _store_path() -> Path:
    settings = get_settings()
    processed_dir = Path(settings.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / "outreach_drafts.json"


def _load_raw() -> list[dict]:
    path = _store_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(records: list[dict]) -> None:
    with _store_path().open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)


def list_outreach() -> list[OutreachDraft]:
    return [OutreachDraft.model_validate(item) for item in _load_raw()]


def get_outreach(outreach_id: str) -> OutreachDraft | None:
    for item in _load_raw():
        if item.get("id") == outreach_id:
            return OutreachDraft.model_validate(item)
    return None


def create_outreach(draft: OutreachDraft) -> OutreachDraft:
    if not draft.id:
        draft.id = uuid4().hex
    records = _load_raw()
    records.append(draft.model_dump(mode="json"))
    _save_raw(records)
    return draft


def update_outreach(outreach_id: str, **changes) -> OutreachDraft | None:
    records = _load_raw()
    updated: OutreachDraft | None = None
    for item in records:
        if item.get("id") == outreach_id:
            item.update({k: v for k, v in changes.items() if v is not None})
            item["updated_at"] = datetime.utcnow().isoformat()
            updated = OutreachDraft.model_validate(item)
            break
    if updated is not None:
        _save_raw(records)
    return updated


def set_status(outreach_id: str, status: OutreachStatus) -> OutreachDraft | None:
    return update_outreach(outreach_id, status=status.value)
