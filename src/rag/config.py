"""Configuration for the AeroForge RAG vector database."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DB_PATH = PROJECT_ROOT / ".aeroforge" / "rag_db"
DEFAULT_RAG_DOCS = PROJECT_ROOT / "docs" / "rag"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64
DEFAULT_MAX_WEB_RESULTS = 20


@dataclass
class RAGConfig:
    """All tunables for the RAG pipeline."""

    db_path: Path = field(default_factory=lambda: DEFAULT_DB_PATH)
    rag_docs_path: Path = field(default_factory=lambda: DEFAULT_RAG_DOCS)
    collection_name: str = "aeroforge_default"
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    embedding_provider: str = "sentence-transformers"
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    max_web_results: int = DEFAULT_MAX_WEB_RESULTS
    search_queries_per_domain: int = 5

    @staticmethod
    def collection_for_project(
        project_code: str,
        aircraft_type: str,
    ) -> str:
        """Derive a collection name from project metadata."""
        safe_code = project_code.lower().replace(" ", "_")
        safe_type = aircraft_type.lower().replace(" ", "_")
        return f"{safe_code}_{safe_type}"
