"""AeroForge RAG Vector Database.

Provides a ChromaDB-backed knowledge base that is populated after the
initialization wizard completes. Agents query it during the RESEARCH
workflow step for domain-specific context.

Usage:
    from src.rag import init_rag_database, query_rag

    # After init wizard — populate the knowledge base
    db = init_rag_database("thermal_electric_sailplane", "aircraft", "AIR4")

    # During RESEARCH step — query for context
    results = query_rag("F5J competition rules wingspan limits")
"""

from __future__ import annotations

import logging
from typing import Any

from .config import RAGConfig
from .database import RAGDatabase

logger = logging.getLogger(__name__)


def init_rag_database(
    aircraft_type: str,
    project_scope: str,
    project_code: str,
    config: RAGConfig | None = None,
    skip_web: bool = False,
) -> RAGDatabase:
    """One-shot RAG population after init wizard.

    1. Create/clear the DB
    2. Load local docs/rag/ files
    3. Web search and scrape domain knowledge (unless skip_web=True)
    4. Return the populated database
    """
    from .chunker import DocumentChunker
    from .loader import LocalDocLoader
    from .scraper import DomainScraper

    cfg = config or RAGConfig()
    cfg.collection_name = RAGConfig.collection_for_project(project_code, aircraft_type)

    chunker = DocumentChunker(chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)

    db = RAGDatabase(cfg)
    db.initialize()
    db.clear()  # Fresh population

    # Step 1: Load local reference docs
    loader = LocalDocLoader(rag_dir=cfg.rag_docs_path, chunker=chunker)
    local_chunks = loader.load_all()
    if local_chunks:
        db.add_documents(local_chunks)
        logger.info("Loaded %d local doc chunks", len(local_chunks))

    # Step 2: Web search and scrape (optional)
    if not skip_web:
        scraper = DomainScraper(config=cfg, chunker=chunker)
        queries = scraper.build_search_queries(aircraft_type, project_scope)
        logger.info("Running %d web search queries for %s", len(queries), aircraft_type)
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


def query_rag(
    query: str,
    n_results: int = 5,
    config: RAGConfig | None = None,
) -> list[dict[str, Any]]:
    """Query the existing RAG database."""
    cfg = config or RAGConfig()
    db = RAGDatabase(cfg)
    if not db.collection_exists():
        logger.warning("RAG database not populated yet. Run init_rag_database first.")
        return []
    return db.query(query, n_results=n_results)


__all__ = [
    "RAGConfig",
    "RAGDatabase",
    "init_rag_database",
    "query_rag",
]
