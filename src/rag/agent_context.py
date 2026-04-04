"""RAG context builder for agent integration.

Agents call ``build_agent_context()`` to get a pre-formatted block of
relevant reference data from the RAG knowledge base before making design
decisions.  This is the bridge between the RAG database and the agent
prompt — it builds smart queries from the current workflow context and
returns a formatted string agents can cite in their proposals.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Query templates per workflow step — agents get context relevant to
# what they are about to decide.
_STEP_QUERY_TEMPLATES: dict[str, list[str]] = {
    "RESEARCH": [
        "{aircraft_type} {component} reference design",
        "{aircraft_type} {component} competition examples",
        "best practices {component} design",
    ],
    "AERO_PROPOSAL": [
        "{component} airfoil selection {aircraft_type}",
        "{component} planform taper ratio aspect ratio",
        "{aircraft_type} aerodynamic optimization {component}",
        "reference designs {component} dimensions",
    ],
    "STRUCTURAL_REVIEW": [
        "{component} structural analysis {aircraft_type}",
        "{component} wall thickness infill mass estimate",
        "3D printed {component} structural requirements",
        "{component} spar sizing carbon tube",
    ],
    "AERO_RESPONSE": [
        "{component} aerodynamic compromise structural constraints",
        "{component} optimized planform reference",
    ],
    "VALIDATION": [
        "{aircraft_type} validation criteria performance targets",
        "{component} CFD FEA results reference",
    ],
}


def _build_queries(
    component_name: str,
    step: str,
    aircraft_type: str,
) -> list[str]:
    """Generate contextual RAG queries for the given workflow state."""
    templates = _STEP_QUERY_TEMPLATES.get(step, _STEP_QUERY_TEMPLATES["RESEARCH"])
    return [
        t.format(component=component_name, aircraft_type=aircraft_type)
        for t in templates
    ]


def _format_results(results: list[dict[str, Any]], max_results: int = 8) -> str:
    """Format RAG query results into a readable context block."""
    if not results:
        return ""

    lines = ["## Reference Data from Knowledge Base\n"]
    seen_sources: set[str] = set()

    for i, r in enumerate(results[:max_results]):
        source = r.get("metadata", {}).get("source", "unknown")
        text = r.get("document", r.get("text", ""))
        distance = r.get("distance", 1.0)

        # Skip duplicates and low-relevance results
        if source in seen_sources or distance > 0.7:
            continue
        seen_sources.add(source)

        # Truncate long chunks
        if len(text) > 500:
            text = text[:500] + "..."

        lines.append(f"### Reference {i+1} (relevance: {1-distance:.0%})")
        lines.append(f"Source: {source}")
        lines.append(text)
        lines.append("")

    if len(lines) <= 1:
        return ""

    lines.append(
        "**Note:** Use these references for comparison and validation. "
        "Do not copy designs — innovate based on the data.\n"
    )
    return "\n".join(lines)


def build_agent_context(
    component_name: str,
    step: str,
    project_code: str,
    aircraft_type: str = "",
    max_results: int = 8,
) -> str:
    """Build a RAG-enriched context string for agent consumption.

    This is the primary API for injecting knowledge base data into
    agent prompts. It generates step-appropriate queries, fetches
    results from the RAG database, and formats them into a reference
    block the agent can cite.

    Args:
        component_name: The sub-assembly being designed (e.g., "wing").
        step: Current workflow step (e.g., "AERO_PROPOSAL").
        project_code: Project identifier for RAG collection.
        aircraft_type: Aircraft type for query context.
        max_results: Maximum number of reference entries to include.

    Returns:
        Formatted string with reference data, or empty string if no
        relevant data found.
    """
    try:
        from src.rag import query_rag
    except ImportError:
        logger.debug("RAG module not available — skipping context injection")
        return ""

    queries = _build_queries(component_name, step, aircraft_type)
    all_results: list[dict[str, Any]] = []

    for q in queries:
        try:
            results = query_rag(q, n_results=3, project_code=project_code)
            all_results.extend(results)
        except Exception as exc:
            logger.debug("RAG query failed for '%s': %s", q, exc)

    if not all_results:
        return ""

    # Sort by relevance (lower distance = more relevant)
    all_results.sort(key=lambda r: r.get("distance", 1.0))

    return _format_results(all_results, max_results=max_results)


def get_agent_preamble(
    component_name: str,
    step: str,
    project_code: str,
    aircraft_type: str = "",
) -> str:
    """Build a complete preamble for agent invocation.

    Includes RAG context and a reminder to use it. Returns empty string
    if no relevant context found.
    """
    context = build_agent_context(
        component_name, step, project_code, aircraft_type,
    )
    if not context:
        return ""

    return (
        "--- KNOWLEDGE BASE CONTEXT (auto-injected) ---\n\n"
        f"{context}\n"
        "--- END KNOWLEDGE BASE CONTEXT ---\n\n"
        "Use the reference data above to inform your analysis. "
        "Compare your proposals against reference designs. "
        "If the data is insufficient, use WebSearch for additional information.\n\n"
    )
