"""Document chunking for the AeroForge RAG pipeline.

Splits markdown, HTML, and plain text into overlapping chunks that
preserve semantic coherence by respecting heading boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """One chunk of text with provenance metadata."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentChunker:
    """Heading-aware document chunker."""

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 64,
    ) -> None:
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk_markdown(self, text: str, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        """Split markdown on heading boundaries, then subdivide large sections."""
        base_meta = metadata or {}
        sections = self._split_markdown_sections(text)
        chunks: list[Chunk] = []

        for heading, body in sections:
            section_meta = {**base_meta, "section": heading}
            section_text = f"{heading}\n{body}".strip() if heading else body.strip()
            if not section_text:
                continue

            if len(section_text) <= self._chunk_size:
                chunks.append(Chunk(
                    text=section_text,
                    metadata={**section_meta, "chunk_index": len(chunks)},
                ))
            else:
                for sub in self._split_with_overlap(section_text):
                    chunks.append(Chunk(
                        text=sub,
                        metadata={**section_meta, "chunk_index": len(chunks)},
                    ))
        return chunks

    def chunk_plain(self, text: str, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        """Split plain text by paragraphs, then subdivide."""
        base_meta = metadata or {}
        chunks: list[Chunk] = []
        for sub in self._split_with_overlap(text):
            chunks.append(Chunk(
                text=sub,
                metadata={**base_meta, "chunk_index": len(chunks)},
            ))
        return chunks

    def chunk_html(self, html: str, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        """Strip HTML tags and chunk as plain text."""
        clean = re.sub(r"<[^>]+>", " ", html)
        clean = re.sub(r"\s+", " ", clean).strip()
        return self.chunk_plain(clean, metadata)

    # ── Internal ─────────────────────────────────────────────────

    @staticmethod
    def _split_markdown_sections(text: str) -> list[tuple[str, str]]:
        """Split markdown into (heading, body) pairs."""
        pattern = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)
        parts = pattern.split(text)

        sections: list[tuple[str, str]] = []
        if parts[0].strip():
            sections.append(("", parts[0]))

        i = 1
        while i < len(parts):
            heading = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((heading, body))
            i += 2

        return sections

    def _split_with_overlap(self, text: str) -> list[str]:
        """Split text into chunks with overlap, preferring paragraph breaks."""
        if len(text) <= self._chunk_size:
            return [text]

        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current = ""

        for para in paragraphs:
            candidate = f"{current}\n\n{para}".strip() if current else para.strip()
            if len(candidate) <= self._chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(para) <= self._chunk_size:
                    current = para.strip()
                else:
                    # Force-split oversized paragraphs
                    words = para.split()
                    current = ""
                    for word in words:
                        test = f"{current} {word}".strip()
                        if len(test) <= self._chunk_size:
                            current = test
                        else:
                            if current:
                                chunks.append(current)
                            current = word

        if current:
            chunks.append(current)

        # Add overlap by prepending tail of previous chunk
        if self._overlap > 0 and len(chunks) > 1:
            overlapped = [chunks[0]]
            for i in range(1, len(chunks)):
                tail = chunks[i - 1][-self._overlap:]
                overlapped.append(f"{tail} {chunks[i]}")
            chunks = overlapped

        return chunks
