from functools import lru_cache
from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


def _anchor(path_value: str) -> str:
    """
    Resolve a storage path to an absolute location anchored at the backend
    root, so it is independent of the process working directory.

    Historically a ``backend/app/data/...`` value combined with running the app
    from the ``backend/`` directory produced a nested ``backend/backend/...``
    tree. We strip a leading ``backend/`` and anchor at BASE_DIR to prevent that.
    """
    p = Path(path_value)
    if p.is_absolute():
        return str(p)
    parts = p.parts
    if parts and parts[0] == "backend":
        p = Path(*parts[1:]) if len(parts) > 1 else Path(".")
    return str((BASE_DIR / p).resolve())


class Settings(BaseSettings):
    app_name: str = "ConstructionFlow AI"
    app_env: str = "development"

    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-large"

    langsmith_api_key: str | None = None
    langsmith_project: str = "AGENTIC DOCUMENT UNDERSTANDING"
    langsmith_tracing: bool = True

    tavily_api_key: str | None = None

    pinecone_api_key: str
    index_name: str = "agentic-document-understanding"

    upload_dir: str = "app/data/uploads"
    processed_dir: str = "app/data/processed"
    graph_output_dir: str = "app/data/graph"

    # Public URL of this backend (used to build absolute asset URLs, e.g. the
    # exported workflow graph). Set to the Render URL in production.
    public_base_url: str = "http://127.0.0.1:8000"
    # Comma-separated list of allowed frontend origins for CORS. Set to the
    # Netlify URL(s) in production.
    frontend_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    max_chunk_size: int = 1200
    chunk_overlap: int = 150
    top_k_retrieval: int = 5

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def _anchor_storage_dirs(self) -> "Settings":
        self.upload_dir = _anchor(self.upload_dir)
        self.processed_dir = _anchor(self.processed_dir)
        self.graph_output_dir = _anchor(self.graph_output_dir)
        return self

    @property
    def cors_origins(self) -> list[str]:
        """Allowed CORS origins, normalized (no trailing slashes, no blanks)."""
        return [
            origin.strip().rstrip("/")
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()