"""URL fetching and content chunking for the RAG pipeline.

The LLM performs web searches using its built-in WebSearch tool, then
passes discovered URLs here for fetching and chunking into the RAG database.
This module does NOT search — it only fetches and chunks.
"""

from __future__ import annotations

import logging

from .chunker import Chunk, DocumentChunker
from .config import RAGConfig

logger = logging.getLogger(__name__)


class DomainScraper:
    """Fetch web content and chunk it for the RAG database.

    The LLM is responsible for finding URLs via its built-in WebSearch tool.
    This class only fetches the content and chunks it.
    """

    def __init__(
        self,
        config: RAGConfig | None = None,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self._config = config or RAGConfig()
        self._chunker = chunker or DocumentChunker()

    def build_baseline_queries(self, mission_prompt: str) -> list[str]:
        """Generate baseline search queries from the mission prompt.

        These are for the LLM to execute via WebSearch, not for this class.
        """
        prompt_clean = mission_prompt.strip()[:200]
        queries = [
            f"{prompt_clean} design specifications",
            f"{prompt_clean} similar existing designs",
            f"{prompt_clean} regulations rules standards",
            f"{prompt_clean} construction techniques materials",
            f"{prompt_clean} aerodynamic performance data",
        ]
        return queries[: self._config.search_queries_per_domain]

    def scrape_url(self, url: str) -> list[Chunk]:
        """Fetch and chunk a single URL. Returns empty list on failure."""
        try:
            import httpx

            response = httpx.get(url, timeout=15, follow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")

            if "html" in content_type:
                chunks = self._chunker.chunk_html(
                    response.text,
                    {"source_type": "web", "source_url": url},
                )
            else:
                chunks = self._chunker.chunk_plain(
                    response.text,
                    {"source_type": "web", "source_url": url},
                )
            return chunks
        except Exception as exc:
            logger.warning("Failed to scrape %s: %s", url, exc)
            return []

    def scrape_urls(self, urls: list[str]) -> list[Chunk]:
        """Fetch and chunk multiple URLs. Deduplicates."""
        all_chunks: list[Chunk] = []
        seen: set[str] = set()

        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            chunks = self.scrape_url(url)
            all_chunks.extend(chunks)
            if len(all_chunks) >= self._config.max_web_results * 5:
                logger.info("Chunk limit reached at %d chunks", len(all_chunks))
                break

        logger.info(
            "Scraped %d chunks from %d unique URLs",
            len(all_chunks),
            len(seen),
        )
        return all_chunks
