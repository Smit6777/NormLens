"""
Centralized application configuration.

All configuration is environment-based (12-factor style). Nothing here is
hardcoded that a deployer might need to change, and no secrets or API
keys live in source code -- see .env.example for the full list of
recognized variables.

Requires: pydantic-settings (see requirements.txt). Not importable until
`pip install -r requirements.txt` has been run in the target environment.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = Field(default="BIS Standard Recommendation & Compliance Auditor")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # --- Data layer (the five knowledge-layer JSON files) ---
    data_dir: Path = Field(default=Path("./data"))
    bis_metadata_file: str = Field(default="bis_metadata.json")
    bis_compliance_file: str = Field(default="bis_compliance.json")
    qco_mapping_file: str = Field(default="qco_mapping.json")
    normative_graph_file: str = Field(default="normative_graph.json")
    sources_file: str = Field(default="sources.json")

    # --- Embeddings / vector search (wired up from Phase 2 onward) ---
    embedding_model_name: str = Field(default="all-mpnet-base-v2")
    vector_index_dir: Path = Field(default=Path("./data/index"))
    top_k_candidates: int = Field(default=10, ge=1, le=100)
    min_match_score: float = Field(default=0.3, ge=0.0, le=1.0)

    # --- Upload handling ---
    max_upload_size_mb: int = Field(default=10, ge=1)
    allowed_upload_extensions: str = Field(default=".pdf,.txt")

    # --- Security & Auth ---
    api_key: str = Field(default="test-api-key")
    admin_api_key: str = Field(default="admin-api-key")
    rate_limit: str = Field(default="100/hour")

    # --- Advanced Features ---
    enable_llm_extractor: bool = Field(default=False)
    enable_hindi: bool = Field(default=False)
    enable_cache: bool = Field(default=True)

    # --- API ---
    api_v1_prefix: str = Field(default="/api/v1")

    @property
    def rate_limit_int(self) -> int:
        try:
            return int(self.rate_limit.split("/")[0])
        except (ValueError, IndexError):
            return 100

    @property
    def allowed_upload_extensions_list(self) -> list[str]:
        return [
            ext.strip().lower()
            for ext in self.allowed_upload_extensions.split(",")
            if ext.strip()
        ]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def bis_metadata_path(self) -> Path:
        return self.data_dir / self.bis_metadata_file

    @property
    def bis_compliance_path(self) -> Path:
        return self.data_dir / self.bis_compliance_file

    @property
    def qco_mapping_path(self) -> Path:
        return self.data_dir / self.qco_mapping_file

    @property
    def normative_graph_path(self) -> Path:
        return self.data_dir / self.normative_graph_file

    @property
    def sources_path(self) -> Path:
        return self.data_dir / self.sources_file


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached Settings instance.

    Use as a FastAPI dependency (`Depends(get_settings)`) rather than
    importing a module-level singleton, so tests can override it cleanly.
    """
    return Settings()
