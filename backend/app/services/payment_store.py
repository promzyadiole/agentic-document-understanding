from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.core.config import get_settings
from app.models.schemas import Payment, PaymentStatus


def _store_path() -> Path:
    settings = get_settings()
    processed_dir = Path(settings.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / "payments.json"


def _load_raw() -> list[dict]:
    path = _store_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(records: list[dict]) -> None:
    with _store_path().open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)


def list_payments() -> list[Payment]:
    return [Payment.model_validate(item) for item in _load_raw()]


def get_payment(payment_id: str) -> Payment | None:
    for item in _load_raw():
        if item.get("id") == payment_id:
            return Payment.model_validate(item)
    return None


def create_payment(payment: Payment) -> Payment:
    records = _load_raw()
    records.append(payment.model_dump(mode="json"))
    _save_raw(records)
    return payment


def update_payment(payment_id: str, **changes) -> Payment | None:
    records = _load_raw()
    updated: Payment | None = None
    for item in records:
        if item.get("id") == payment_id:
            item.update({k: (v.value if hasattr(v, "value") else v) for k, v in changes.items() if v is not None})
            updated = Payment.model_validate(item)
            break
    if updated is not None:
        _save_raw(records)
    return updated


def confirmed_revenue_cents() -> int:
    return sum(
        int(item.get("amount_cents", 0))
        for item in _load_raw()
        if item.get("status") == PaymentStatus.CONFIRMED.value
    )
