"""Web search query generation and content scraping for the RAG pipeline.

Generates domain-specific search queries based on the aircraft class,
fetches web content, and chunks it for ingestion into the vector database.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from .chunker import Chunk, DocumentChunker
from .config import RAGConfig

logger = logging.getLogger(__name__)

# Domain keyword templates keyed on common aircraft class tokens.
_DOMAIN_TEMPLATES: dict[str, list[str]] = {
    "sailplane": [
        "{type} competition rules FAI",
        "{type} design specifications dimensions wingspan",
        "{type} construction techniques 3D printed",
        "{type} airfoil selection low Reynolds",
        "similar {type} models comparison specifications",
    ],
    "glider": [
        "{type} competition regulations",
        "{type} design dimensions weight",
        "{type} construction materials structure",
        "{type} airfoil performance low Re",
        "{type} design references plans",
    ],
    "drone": [
        "{type} regulations FAA Part 107",
        "{type} frame design specifications",
        "{type} motor propeller efficiency",
        "{type} flight controller setup",
        "{type} endurance range optimization",
    ],
    "interceptor": [
        "{type} design high speed aerodynamics",
        "{type} structural requirements maneuver loads",
        "{type} propulsion thrust to weight",
        "{type} control surface sizing authority",
        "{type} materials composite carbon fiber",
    ],
    "paper_airplane": [
        "paper airplane aerodynamics science",
        "paper airplane competition rules distance",
        "best paper airplane designs world record",
        "paper airplane fold techniques optimization",
        "aerodynamics of paper planes research",
    ],
    "paraglider": [
        "paraglider wing design certification EN 926",
        "paraglider aerodynamics lift drag",
        "paraglider materials ripstop nylon dyneema",
        "paraglider line layout design",
        "paraglider safety regulations certification",
    ],
    "_default": [
        "{type} aerodynamic design principles",
        "{type} structural design requirements",
        "{type} materials and construction",
        "{type} performance optimization",
        "{type} regulations and standards",
    ],
}


class DomainScraper:
    """Generate search queries and scrape web content for a given aircraft class."""

    def __init__(
        self,
        config: RAGConfig | None = None,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self._config = config or RAGConfig()
        self._chunker = chunker or DocumentChunker()

    def build_search_queries(
        self,
        aircraft_type: str,
        project_scope: str = "aircraft",
    ) -> list[str]:
        """Generate domain-specific search queries based on aircraft class."""
        type_lower = aircraft_type.lower().replace("_", " ")
        tokens = type_lower.split()

        # Find the best matching template set
        templates = _DOMAIN_TEMPLATES.get("_default", [])
        for key in _DOMAIN_TEMPLATES:
            if key == "_default":
                continue
            if key in type_lower or key in tokens:
                templates = _DOMAIN_TEMPLATES[key]
                break

        queries = [t.format(type=aircraft_type.replace("_", " ")) for t in templates]

        # Add scope-specific queries
        if project_scope == "aircraft":
            queries.append(f"{type_lower} full aircraft design overview")
        elif project_scope == "assembly":
            queries.append(f"{type_lower} assembly integration")
        elif project_scope == "component":
            queries.append(f"{type_lower} component design details")

        return queries[: self._config.search_queries_per_domain + 1]

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
            logger.debug("Failed to scrape %s: %s", url, exc)
            return []

    def scrape_search_results(
        self,
        queries: list[str],
        max_results_per_query: int = 3,
    ) -> list[Chunk]:
        """Run web searches and scrape top results.

        This is a best-effort method. If no search backend is available,
        it returns an empty list without error.
        """
        all_chunks: list[Chunk] = []
        seen_urls: set[str] = set()

        for query in queries:
            urls = self._web_search(query, max_results_per_query)
            for url in urls:
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                chunks = self.scrape_url(url)
                all_chunks.extend(chunks)
                if len(all_chunks) >= self._config.max_web_results * 5:
                    return all_chunks

        logger.info(
            "Scraped %d chunks from %d unique URLs",
            len(all_chunks),
            len(seen_urls),
        )
        return all_chunks

    @staticmethod
    def _web_search(query: str, max_results: int = 3) -> list[str]:
        """Best-effort web search. Returns URLs or empty list."""
        try:
            import httpx

            # Use a simple search API if available
            response = httpx.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "AeroForge-RAG/1.0"},
                timeout=10,
                follow_redirects=True,
            )
            # Extract URLs from DuckDuckGo HTML results
            urls = re.findall(r'href="(https?://[^"]+)"', response.text)
            # Filter out DuckDuckGo internal links
            filtered = [
                u for u in urls
                if "duckduckgo.com" not in u and "duck.co" not in u
            ]
            return filtered[:max_results]
        except Exception:
            return []
