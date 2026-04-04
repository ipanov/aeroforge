"""Tests for RAG agent context builder.

Covers:
- Query generation from workflow context
- Result formatting
- Preamble generation
- Empty/missing RAG handling
"""

from __future__ import annotations

from src.rag.agent_context import (
    _build_queries,
    _format_results,
    build_agent_context,
    get_agent_preamble,
)


class TestQueryBuilding:

    def test_aero_proposal_queries_include_airfoil(self) -> None:
        queries = _build_queries("wing", "AERO_PROPOSAL", "sailplane")
        assert any("airfoil" in q for q in queries)

    def test_structural_review_queries_include_wall(self) -> None:
        queries = _build_queries("fuselage", "STRUCTURAL_REVIEW", "drone")
        assert any("wall" in q.lower() or "structural" in q.lower() for q in queries)

    def test_research_queries_include_reference(self) -> None:
        queries = _build_queries("empennage", "RESEARCH", "sailplane")
        assert any("reference" in q for q in queries)

    def test_unknown_step_falls_back_to_research(self) -> None:
        queries = _build_queries("wing", "UNKNOWN_STEP", "sailplane")
        assert len(queries) > 0

    def test_queries_substitute_component_and_type(self) -> None:
        queries = _build_queries("wing", "AERO_PROPOSAL", "interceptor")
        for q in queries:
            assert "wing" in q or "interceptor" in q


class TestResultFormatting:

    def test_empty_results(self) -> None:
        assert _format_results([]) == ""

    def test_formats_results(self) -> None:
        results = [
            {
                "document": "The AG24 airfoil is optimal at Re=80k",
                "metadata": {"source": "f5j_catalog.md"},
                "distance": 0.2,
            }
        ]
        formatted = _format_results(results)
        assert "AG24" in formatted
        assert "Reference" in formatted
        assert "f5j_catalog" in formatted

    def test_skips_low_relevance(self) -> None:
        results = [
            {
                "document": "Irrelevant content",
                "metadata": {"source": "random.md"},
                "distance": 0.9,  # Very low relevance
            }
        ]
        formatted = _format_results(results)
        assert formatted == ""

    def test_truncates_long_chunks(self) -> None:
        results = [
            {
                "document": "x" * 1000,
                "metadata": {"source": "long.md"},
                "distance": 0.1,
            }
        ]
        formatted = _format_results(results)
        assert "..." in formatted

    def test_deduplicates_sources(self) -> None:
        results = [
            {"document": "First", "metadata": {"source": "same.md"}, "distance": 0.1},
            {"document": "Second", "metadata": {"source": "same.md"}, "distance": 0.2},
        ]
        formatted = _format_results(results)
        # Should only appear once
        assert formatted.count("same.md") == 1

    def test_includes_innovation_note(self) -> None:
        results = [
            {"document": "Data", "metadata": {"source": "test.md"}, "distance": 0.1},
        ]
        formatted = _format_results(results)
        assert "innovate" in formatted.lower() or "Do not copy" in formatted


class TestBuildAgentContext:

    def test_returns_empty_when_rag_not_populated(self) -> None:
        # With no RAG database, should return empty string
        result = build_agent_context(
            "wing", "AERO_PROPOSAL", "NONEXISTENT_PROJECT",
        )
        assert result == ""


class TestGetAgentPreamble:

    def test_returns_empty_when_no_context(self) -> None:
        preamble = get_agent_preamble(
            "wing", "AERO_PROPOSAL", "NONEXISTENT",
        )
        assert preamble == ""
