"""ChromaDB wrapper for the AeroForge RAG knowledge base."""

from __future__ import annotations

import logging
from typing import Any, Optional

from .chunker import Chunk
from .config import RAGConfig

logger = logging.getLogger(__name__)


class RAGDatabase:
    """Persistent vector database backed by ChromaDB."""

    def __init__(self, config: RAGConfig | None = None) -> None:
        self._config = config or RAGConfig()
        self._client: Any = None
        self._collection: Any = None

    def initialize(self) -> None:
        """Create or open the ChromaDB persistent client and collection."""
        import chromadb

        self._config.db_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._config.db_path))
        self._collection = self._client.get_or_create_collection(
            name=self._config.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "RAG database initialized: %s (%d documents)",
            self._config.collection_name,
            self._collection.count(),
        )

    def add_documents(self, chunks: list[Chunk]) -> int:
        """Add chunked documents to the collection. Returns count added."""
        if not chunks:
            return 0
        self._ensure_initialized()

        ids = [f"doc_{i}_{hash(c.text) & 0xFFFFFFFF:08x}" for i, c in enumerate(chunks)]
        documents = [c.text for c in chunks]
        metadatas = [c.metadata if c.metadata else {"_source": "unknown"} for c in chunks]

        batch_size = 100
        added = 0
        for start in range(0, len(chunks), batch_size):
            end = start + batch_size
            self._collection.add(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )
            added += min(batch_size, len(chunks) - start)

        logger.info("Added %d documents to collection %s", added, self._config.collection_name)
        return added

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic search. Returns list of {text, metadata, distance}."""
        self._ensure_initialized()

        kwargs: dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": min(n_results, self._collection.count() or 1),
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata

        results = self._collection.query(**kwargs)

        output: list[dict[str, Any]] = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            for doc, meta, dist in zip(docs, metas, dists):
                output.append({"text": doc, "metadata": meta, "distance": dist})

        return output

    def get_collection_stats(self) -> dict[str, Any]:
        """Return count and collection name."""
        self._ensure_initialized()
        count = self._collection.count()
        return {
            "collection": self._config.collection_name,
            "document_count": count,
            "db_path": str(self._config.db_path),
        }

    def collection_exists(self) -> bool:
        """Check if the DB has been populated."""
        try:
            self._ensure_initialized()
            return self._collection.count() > 0
        except Exception:
            return False

    def clear(self) -> None:
        """Delete all documents (for repopulation)."""
        self._ensure_initialized()
        if self._client is not None:
            self._client.delete_collection(self._config.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self._config.collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    def close(self) -> None:
        """Release the ChromaDB client resources."""
        self._collection = None
        self._client = None

    def _ensure_initialized(self) -> None:
        if self._collection is None:
            self.initialize()
