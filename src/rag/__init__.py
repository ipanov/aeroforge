"""AeroForge RAG Vector Database.

A ChromaDB-backed knowledge base populated by the LLM during the RESEARCH
workflow phase. The LLM uses its built-in WebSearch tool to find URLs,
then passes them here for fetching, chunking, and storage.

Usage:
    from src.rag import add_urls_to_rag, add_to_rag, query_rag

    # LLM finds URLs via WebSearch, then feeds them in
    add_urls_to_rag(["https://example.com/paper-plane-study"], project_code="PP1")

    # Add a single URL
    add_to_rag("https://example.com/f5j-design-guide", project_code="AIR4")

    # Query during design decisions
    results = query_rag("paper airplane glide ratio", project_code="PP1")
"""

from __future__ import annotations

import logging
from typing import Any

from .config import RAGConfig
from .database import RAGDatabase

logger = logging.getLogger(__name__)


def add_urls_to_rag(
    urls: list[str],
    project_code: str = "default",
    config: RAGConfig | None = None,
) -> int:
    """Add multiple URLs to the RAG database. Returns total chunks added.

    Primary entry point: the LLM finds URLs via WebSearch and passes them here.
    """
    from .chunker import DocumentChunker
    from .scraper import DomainScraper

    cfg = config or RAGConfig()
    cfg.collection_name = f"{project_code.lower().replace(' ', '_')}_research"

    chunker = DocumentChunker(chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)
    scraper = DomainScraper(config=cfg, chunker=chunker)

    chunks = scraper.scrape_urls(urls)
    if not chunks:
        logger.warning("No chunks extracted from %d URLs", len(urls))
        return 0

    db = RAGDatabase(cfg)
    db.initialize()
    count = db.add_documents(chunks)
    logger.info("Added %d chunks from %d URLs to RAG", count, len(urls))
    return count


def add_to_rag(
    url: str,
    project_code: str = "default",
    config: RAGConfig | None = None,
) -> int:
    """Add a single URL to the existing RAG database. Returns chunks added."""
    return add_urls_to_rag([url], project_code=project_code, config=config)


def query_rag(
    query: str,
    n_results: int = 5,
    project_code: str = "default",
    config: RAGConfig | None = None,
) -> list[dict[str, Any]]:
    """Query the RAG database. Returns empty list if not populated."""
    cfg = config or RAGConfig()
    cfg.collection_name = f"{project_code.lower().replace(' ', '_')}_research"

    db = RAGDatabase(cfg)
    if not db.collection_exists():
        return []
    return db.query(query, n_results=n_results)


def get_rag_stats(
    project_code: str = "default",
    config: RAGConfig | None = None,
) -> dict[str, Any]:
    """Return RAG database stats for a project."""
    cfg = config or RAGConfig()
    cfg.collection_name = f"{project_code.lower().replace(' ', '_')}_research"

    db = RAGDatabase(cfg)
    if not db.collection_exists():
        return {"collection": cfg.collection_name, "document_count": 0}
    return db.get_collection_stats()


def populate_rag(
    project_code: str,
    mission_prompt: str = "",
    config: RAGConfig | None = None,
    include_local_docs: bool = True,
    web_queries: list[str] | None = None,
) -> RAGDatabase:
    """Initialize RAG database and load local docs.

    Web search is NOT done here — the LLM uses WebSearch and calls
    add_urls_to_rag() with discovered URLs.
    """
    from .chunker import DocumentChunker
    from .loader import LocalDocLoader

    cfg = config or RAGConfig()
    cfg.collection_name = f"{project_code.lower().replace(' ', '_')}_research"

    chunker = DocumentChunker(chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)

    db = RAGDatabase(cfg)
    db.initialize()

    if include_local_docs:
        loader = LocalDocLoader(rag_dir=cfg.rag_docs_path, chunker=chunker)
        local_chunks = loader.load_all()
        if local_chunks:
            db.add_documents(local_chunks)
            logger.info("Loaded %d local doc chunks", len(local_chunks))

    stats = db.get_collection_stats()
    logger.info(
        "RAG database ready: %s — %d documents",
        stats["collection"],
        stats["document_count"],
    )
    return db


# Backward compat
def init_rag_database(
    aircraft_type: str,
    project_scope: str,
    project_code: str,
    config: RAGConfig | None = None,
    skip_web: bool = False,
) -> RAGDatabase:
    """Backward-compatible wrapper."""
    return populate_rag(
        project_code=project_code,
        mission_prompt=aircraft_type.replace("_", " "),
        config=config,
    )


__all__ = [
    "RAGConfig",
    "RAGDatabase",
    "add_urls_to_rag",
    "add_to_rag",
    "query_rag",
    "get_rag_stats",
    "populate_rag",
    "init_rag_database",
]
