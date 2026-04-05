from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


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

    max_chunk_size: int = 1200
    chunk_overlap: int = 150
    top_k_retrieval: int = 5

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()