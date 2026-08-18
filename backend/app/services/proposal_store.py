from __future__ import annotations

import json
from pathlib import Path

from app.core.config import get_settings
from app.models.schemas import Proposal


def _store_path() -> Path:
    settings = get_settings()
    processed_dir = Path(settings.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / "proposals.json"


def _load_raw() -> list[dict]:
    path = _store_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(records: list[dict]) -> None:
    with _store_path().open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)


def list_proposals() -> list[Proposal]:
    return [Proposal.model_validate(item) for item in _load_raw()]


def get_proposal(proposal_id: str) -> Proposal | None:
    for item in _load_raw():
        if item.get("id") == proposal_id:
            return Proposal.model_validate(item)
    return None


def get_proposal_by_token(token: str) -> Proposal | None:
    for item in _load_raw():
        if item.get("share_token") == token:
            return Proposal.model_validate(item)
    return None


def save_proposal(proposal: Proposal) -> Proposal:
    records = _load_raw()
    records.append(proposal.model_dump(mode="json"))
    _save_raw(records)
    return proposal


def set_proposal_status(proposal_id: str, status: str) -> Proposal | None:
    records = _load_raw()
    updated: Proposal | None = None
    for item in records:
        if item.get("id") == proposal_id:
            item["status"] = status
            updated = Proposal.model_validate(item)
            break
    if updated is not None:
        _save_raw(records)
    return updated
