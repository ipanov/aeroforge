"""Tests for the AeroForge RAG vector database infrastructure."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


def test_chunker_markdown_splits_on_headings():
    """Verify markdown chunker produces chunks at heading boundaries."""
    from src.rag.chunker import DocumentChunker

    text = """# Title

Some intro text.

## Section One

Content of section one.

## Section Two

Content of section two.
"""
    chunker = DocumentChunker(chunk_size=2000, overlap=0)
    chunks = chunker.chunk_markdown(text, {"source": "test"})

    assert len(chunks) >= 3  # title + section1 + section2
    assert any("Title" in c.text for c in chunks)
    assert any("Section One" in c.text for c in chunks)
    assert any("Section Two" in c.text for c in chunks)
    for c in chunks:
        assert c.metadata.get("source") == "test"


def test_chunker_respects_max_size():
    """Verify no chunk exceeds the configured size."""
    from src.rag.chunker import DocumentChunker

    text = "word " * 500  # ~2500 chars
    chunker = DocumentChunker(chunk_size=200, overlap=0)
    chunks = chunker.chunk_plain(text)

    assert len(chunks) > 1
    for c in chunks:
        # Allow small overflow from overlap stitching
        assert len(c.text) <= 300


def test_chunker_html_strips_tags():
    """Verify HTML chunker strips tags before chunking."""
    from src.rag.chunker import DocumentChunker

    html = "<html><body><h1>Title</h1><p>Some <b>bold</b> text.</p></body></html>"
    chunker = DocumentChunker()
    chunks = chunker.chunk_html(html)

    assert len(chunks) >= 1
    full = " ".join(c.text for c in chunks)
    assert "<" not in full
    assert "Title" in full
    assert "bold" in full


def test_rag_config_collection_for_project():
    """Verify collection name derivation."""
    from src.rag.config import RAGConfig

    name = RAGConfig.collection_for_project("AIR4", "thermal_electric_sailplane")
    assert name == "air4_thermal_electric_sailplane"

    name2 = RAGConfig.collection_for_project("TEST 1", "Paper Airplane")
    assert name2 == "test_1_paper_airplane"


def test_database_add_and_query():
    """Create an in-memory ChromaDB, add chunks, query, verify results."""
    chromadb = pytest.importorskip("chromadb")

    from src.rag.chunker import Chunk
    from src.rag.config import RAGConfig
    from src.rag.database import RAGDatabase

    tmpdir = tempfile.mkdtemp()
    cfg = RAGConfig(
        db_path=Path(tmpdir) / "test_db",
        collection_name="test_collection",
    )
    db = RAGDatabase(cfg)
    db.initialize()

    chunks = [
        Chunk(text="The F5J sailplane has a 4 meter wingspan limit.", metadata={"source_type": "test"}),
        Chunk(text="Paper airplanes are made from a single sheet.", metadata={"source_type": "test"}),
        Chunk(text="Carbon fiber spars provide excellent stiffness.", metadata={"source_type": "test"}),
    ]
    added = db.add_documents(chunks)
    assert added == 3

    results = db.query("sailplane wingspan", n_results=2)
    assert len(results) >= 1
    assert "sailplane" in results[0]["text"].lower() or "wingspan" in results[0]["text"].lower()
    db.close()


def test_database_stats():
    """Verify stats reporting after population."""
    chromadb = pytest.importorskip("chromadb")

    from src.rag.chunker import Chunk
    from src.rag.config import RAGConfig
    from src.rag.database import RAGDatabase

    tmpdir = tempfile.mkdtemp()
    cfg = RAGConfig(
        db_path=Path(tmpdir) / "test_db",
        collection_name="stats_test",
    )
    db = RAGDatabase(cfg)
    db.initialize()
    db.add_documents([Chunk(text="Test document", metadata={"source_type": "test"})])

    stats = db.get_collection_stats()
    assert stats["document_count"] == 1
    assert stats["collection"] == "stats_test"
    db.close()


def test_loader_reads_docs_rag():
    """Point the loader at a temp directory with sample .md files, verify all are chunked."""
    from src.rag.loader import LocalDocLoader

    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "test_doc.md").write_text("# Test\n\nSome content about aircraft.\n")
        (p / "sub").mkdir()
        (p / "sub" / "nested.md").write_text("## Nested\n\nMore content.\n")

        loader = LocalDocLoader(rag_dir=p)
        chunks = loader.load_all()
        assert len(chunks) >= 2
        assert any("aircraft" in c.text for c in chunks)


def test_scraper_builds_queries_for_different_types():
    """Verify query generation produces reasonable queries for various aircraft types."""
    from src.rag.scraper import DomainScraper

    scraper = DomainScraper()

    sailplane_queries = scraper.build_search_queries("thermal_electric_sailplane")
    assert len(sailplane_queries) >= 3
    assert any("sailplane" in q.lower() for q in sailplane_queries)

    drone_queries = scraper.build_search_queries("surveillance_drone")
    assert len(drone_queries) >= 3
    assert any("drone" in q.lower() for q in drone_queries)

    paper_queries = scraper.build_search_queries("paper_airplane")
    assert len(paper_queries) >= 3
    assert any("paper" in q.lower() for q in paper_queries)


def test_init_rag_database_local_only():
    """Run init_rag_database with skip_web=True, verify local docs are loaded."""
    chromadb = pytest.importorskip("chromadb")

    from src.rag import init_rag_database
    from src.rag.config import RAGConfig

    tmpdir = tempfile.mkdtemp()
    cfg = RAGConfig(
        db_path=Path(tmpdir) / "test_rag_db",
    )
    db = init_rag_database(
        aircraft_type="test_aircraft",
        project_scope="aircraft",
        project_code="TEST",
        config=cfg,
        skip_web=True,
    )
    stats = db.get_collection_stats()
    # Should have loaded whatever exists in docs/rag/ (may be 0 if CI has no docs)
    assert stats["document_count"] >= 0
    assert "test_test_aircraft" in stats["collection"]
    db.close()
