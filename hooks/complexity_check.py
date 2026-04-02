"""PreToolUse hook for Write operations on DESIGN_CONSENSUS.md files.

Scans the content being written for language that suggests
unjustified simplification. WARNS (does not block) if found.

The project philosophy is: "Why make it simple when it can be complex?"
The aerodynamicist decides the optimal shape — but must JUSTIFY any
simplification with quantified data (mass, strength, printability).

Triggers on: Write tool when file path contains DESIGN_CONSENSUS

Exit codes:
    0 = PASS
    1 = WARN (simplification language found without justification)

Manual test:
    echo '{"tool_input":{"file_path":"DESIGN_CONSENSUS.md","content":"for simplicity we chose trapezoidal"}}' | python hooks/complexity_check.py
"""

import json
import re
import sys


# Patterns that suggest unjustified simplification
SIMPLIFICATION_PATTERNS = [
    r"for\s+simplicity",
    r"to\s+keep\s+(?:it\s+|things\s+)?simple",
    r"simplified?\s+(?:planform|shape|geometry|design)",
    r"only\s+[\d.]+%\s+(?:improvement|gain|benefit|reduction)",
    r"negligible\s+(?:improvement|gain|benefit|difference)",
    r"not\s+worth\s+(?:the\s+)?(?:complexity|effort)",
    r"for\s+ease\s+of",
    r"to\s+avoid\s+complexity",
]

# Patterns that indicate the simplification IS justified with data
JUSTIFICATION_PATTERNS = [
    r"mass\s+penalty\s+of\s+[\d.]+\s*g",
    r"weight\s+increase\s+of\s+[\d.]+",
    r"exceeds?\s+(?:mass\s+)?budget",
    r"structural(?:ly)?\s+(?:insufficient|inadequate|too\s+thin)",
    r"does?\s+not\s+fit\s+(?:print\s+)?bed",
    r"printability\s+(?:concern|issue|problem)",
    r"flutter\s+risk",
    r"buckling",
]


def main() -> int:
    """Main entry point."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    file_path = data.get("tool_input", {}).get("file_path", "")
    content = data.get("tool_input", {}).get("content", "")

    # Only check DESIGN_CONSENSUS files
    if "DESIGN_CONSENSUS" not in file_path:
        return 0

    content_lower = content.lower()

    # Find simplification language
    found_simplifications = []
    for pattern in SIMPLIFICATION_PATTERNS:
        matches = re.findall(pattern, content_lower)
        if matches:
            found_simplifications.extend(matches)

    if not found_simplifications:
        # Check for comparison table (at least 3 options)
        has_comparison = (
            "comparison" in content_lower
            or content_lower.count("|") > 20  # Table with rows
        )
        if not has_comparison:
            print(
                "[complexity-hook] WARNING: DESIGN_CONSENSUS lacks a comparison table. "
                "Aero proposals must compare at least 3 design options.",
                file=sys.stderr,
            )
            return 1
        return 0

    # Check if justifications exist
    found_justifications = []
    for pattern in JUSTIFICATION_PATTERNS:
        matches = re.findall(pattern, content_lower)
        if matches:
            found_justifications.extend(matches)

    if found_simplifications and not found_justifications:
        print(
            f"[complexity-hook] WARNING: Simplification language detected without "
            f"quantified justification:",
            file=sys.stderr,
        )
        for s in found_simplifications[:5]:
            print(f"  - '{s}'", file=sys.stderr)
        print(
            "[complexity-hook] The project philosophy is: 'Why make it simple when "
            "it can be complex?' Every simplification must be justified with "
            "specific numbers (mass penalty, structural limit, bed fit, etc.).",
            file=sys.stderr,
        )
        return 1

    # Simplification found but justified
    if found_simplifications and found_justifications:
        print(
            f"[complexity-hook] Note: Simplification language found but appears justified "
            f"({len(found_justifications)} justification(s) detected).",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
