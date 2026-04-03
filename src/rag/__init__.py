"""AeroForge RAG Vector Database.

A ChromaDB-backed knowledge base that agents can populate and query
during the RESEARCH workflow step. This is an OPTIONAL intelligence
tool — agents decide whether and when to use it.

Role hierarchy (agents should prefer in this order):
    1. LLM built-in knowledge — instant, broad coverage
    2. RAG database — fast (~10ms), pre-fetched competitive intelligence
    3. docs/rag/ curated files — direct Read, project-specific benchmarks
    4. WebSearch — real-time, for current or specific data
    5. WebFetch — for known URLs

The RAG is a pre-fetched cache of competitive intelligence that agents
can query fast during iterative design decisions. It is NOT a mandatory
step and NOT a replacement for web search.

Usage:
    from src.rag import populate_rag, query_rag, add_to_rag

    # Agent decides to populate during RESEARCH step
    db = populate_rag(project_code="AIR4", mission_prompt="F5J thermal sailplane")

    # Agent queries during design decisions
    results = query_rag("F5J planform taper ratio competition")

    # Agent adds a specific URL it found useful
    add_to_rag("https://example.com/f5j-design-guide")
"""

from __future__ import annotations

import logging
from typing import Any

from .config import RAGConfig
from .database import RAGDatabase

logger = logging.getLogger(__name__)


def populate_rag(
    project_code: str,
    mission_prompt: str = "",
    config: RAGConfig | None = None,
    include_local_docs: bool = True,
    web_queries: list[str] | None = None,
) -> RAGDatabase:
    """Populate the RAG database. Called by agents during RESEARCH, not by init.

    Args:
        project_code: Project identifier for the collection name.
        mission_prompt: The user's original design brief (used for baseline queries).
        config: Optional config override.
        include_local_docs: Whether to load docs/rag/ files.
        web_queries: Explicit search queries (agent-generated, not hardcoded).
            If None and mission_prompt is provided, generates minimal baseline queries.
    """
    from .chunker import DocumentChunker
    from .loader import LocalDocLoader
    from .scraper import DomainScraper

    cfg = config or RAGConfig()
    cfg.collection_name = f"{project_code.lower().replace(' ', '_')}_research"

    chunker = DocumentChunker(chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)

    db = RAGDatabase(cfg)
    db.initialize()

    # Load local reference docs if they exist
    if include_local_docs:
        loader = LocalDocLoader(rag_dir=cfg.rag_docs_path, chunker=chunker)
        local_chunks = loader.load_all()
        if local_chunks:
            db.add_documents(local_chunks)
            logger.info("Loaded %d local doc chunks", len(local_chunks))

    # Web scrape with agent-provided or baseline queries
    scraper = DomainScraper(config=cfg, chunker=chunker)
    queries = web_queries or (
        scraper.build_baseline_queries(mission_prompt) if mission_prompt else []
    )
    if queries:
        logger.info("Running %d web search queries", len(queries))
        web_chunks = scraper.scrape_search_results(queries)
        if web_chunks:
            db.add_documents(web_chunks)
            logger.info("Loaded %d web-scraped chunks", len(web_chunks))

    stats = db.get_collection_stats()
    logger.info(
        "RAG database ready: %s — %d documents",
        stats["collection"],
        stats["document_count"],
    )
    return db


def add_to_rag(
    url: str,
    project_code: str = "default",
    config: RAGConfig | None = None,
) -> int:
    """Add a single URL to the existing RAG database. Returns chunks added."""
    from .chunker import DocumentChunker
    from .scraper import DomainScraper

    cfg = config or RAGConfig()
    cfg.collection_name = f"{project_code.lower().replace(' ', '_')}_research"

    chunker = DocumentChunker(chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)
    scraper = DomainScraper(config=cfg, chunker=chunker)

    chunks = scraper.scrape_url(url)
    if not chunks:
        return 0

    db = RAGDatabase(cfg)
    db.initialize()
    return db.add_documents(chunks)


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


# Keep backward compat alias
def init_rag_database(
    aircraft_type: str,
    project_scope: str,
    project_code: str,
    config: RAGConfig | None = None,
    skip_web: bool = False,
) -> RAGDatabase:
    """Backward-compatible wrapper. Prefer populate_rag() for new code."""
    return populate_rag(
        project_code=project_code,
        mission_prompt=aircraft_type.replace("_", " "),
        config=config,
        web_queries=[] if skip_web else None,
    )


__all__ = [
    "RAGConfig",
    "RAGDatabase",
    "populate_rag",
    "add_to_rag",
    "query_rag",
    "init_rag_database",
]
