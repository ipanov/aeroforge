"""Load local docs/rag/ files into the RAG database."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .chunker import Chunk, DocumentChunker
from .config import RAGConfig

logger = logging.getLogger(__name__)


class LocalDocLoader:
    """Walk the local RAG docs directory and chunk all markdown files."""

    def __init__(
        self,
        rag_dir: Path | None = None,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self._rag_dir = rag_dir or RAGConfig().rag_docs_path
        self._chunker = chunker or DocumentChunker()

    def load_all(self) -> list[Chunk]:
        """Recursively load and chunk all .md files under the RAG docs dir."""
        if not self._rag_dir.exists():
            logger.warning("RAG docs directory does not exist: %s", self._rag_dir)
            return []

        chunks: list[Chunk] = []
        for md_file in sorted(self._rag_dir.rglob("*.md")):
            chunks.extend(self.load_file(md_file))

        logger.info(
            "Loaded %d chunks from %s",
            len(chunks),
            self._rag_dir,
        )
        return chunks

    def load_file(self, path: Path) -> list[Chunk]:
        """Chunk a single markdown file."""
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            logger.warning("Failed to read %s: %s", path, exc)
            return []

        metadata: dict[str, Any] = {
            "source_type": "local_doc",
            "source_file": str(path.relative_to(path.parents[2]) if len(path.parents) > 2 else path.name),
        }
        return self._chunker.chunk_markdown(text, metadata)
