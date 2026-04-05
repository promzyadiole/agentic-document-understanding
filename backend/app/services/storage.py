from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


def save_upload_file(upload_file: UploadFile) -> Path:
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4().hex}_{upload_file.filename}"
    file_path = upload_dir / safe_name

    with file_path.open("wb") as f:
        f.write(upload_file.file.read())

    return file_path