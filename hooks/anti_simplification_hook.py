"""PreToolUse hook that BLOCKS forbidden simplification language in ALL written files.

FORBIDDEN WORDS (exit 2 = hard block):
- simple, simpler, simplest
- practical, impractical
- rational, irrational
- simplified, simplification (unless justified)
- "for ease of", "for convenience"
- "good enough", "close enough"
- approximation, approximate (unless in math context)

ALLOWED (only with quantified justification in same content):
- If the content also contains mass/strength/printability penalty data, the block is lifted.

The project philosophy is: "Why make it simple when it can be complex — for the same price?"
The aerodynamicist decides the optimal shape. Every 0.1% of performance matters.
Simplification is ONLY acceptable when the optimal solution has a quantified penalty
(weight, printability, structural) that makes it impractical — and even then,
the user must approve.

Triggers on: Write tool, Edit tool — checks ALL written content.
"""

import json
import re
import sys


# Words that trigger a HARD BLOCK
FORBIDDEN_PATTERNS = [
    # Direct simplification words
    r"\bsimpler\b",
    r"\bsimplest\b",
    r"\bsimple\b(?!\s*[-_])",  # simple but not simplex
    r"\bpractical\b",
    r"\bimpractical\b",
    r"\brational\b",
    r"\birrational\b",
    r"\bsimplified\b",
    r"\bsimplification\b",
    r"\bapproximate\b(?!ly\s+equal)",  # approximate but not "approximately equal"
    r"\bapproximation\b",
    # Phrases
    r"for\s+ease\s+of",
    r"for\s+convenience",
    r"good\s+enough",
    r"close\s+enough",
    r"near\s+enough",
    r"good\s+approx",
    r"close\s+approx",
    r"reasonable\s+approx",
    r"minor\s+penalty",
    r"negligible\s+(?:improvement|gain|benefit|difference|effect)",
    r"not\s+worth",
    r"overly\s+complex",
    r"unnecessarily\s+complex",
    r"too\s+complex",
    r"keep\s+it\s+simple",
    r"keep\s+things\s+simple",
    r"straightforward\s+(?:approach|design|solution)",
    r"basic\s+(?:approach|design|solution|shape|geometry)",
    r"plain\s+(?:wing|tip|shape)",
    r"flat\s+(?:tip|wing\s*tip)(?!\s*.*(?:rib|panel|section|surface|area|plate))",
    r"standard\s+(?:practice|approach|solution)",
    r"conventional\s+(?:approach|design|solution|shape)",
    r"conservative\s+(?:approach|design|choice)",
    r"minimal\s+(?:complexity|effort)",
    r"least\s+effort",
    r"least\s+complex",
    r"less\s+complex",
    r"reduced\s+complexity",
    r"avoid\s+complexity",
    r"minimize\s+complexity",
    r"limits?\s+complexity",
    r"doesn't\s+justify",
    r"does\s+not\s+justify",
    r"can't\s+justify",
    r"hard\s+to\s+(?:justify|source|manufacture|print)",
    r"not\s+practical",
]

# Phrases that indicate the simplification IS justified with quantified data
JUSTIFICATION_PATTERNS = [
    r"mass\s+penalty\s+of\s+[\d.]+",
    r"weight\s+(?:penalty|increase|cost)\s+of\s+[\d.]+",
    r"[\d.]+\s*g\s+(?:heavier|weight\s+penalty|mass\s+penalty)",
    r"exceeds?\s+(?:mass\s+)?budget",
    r"structural(?:ly)?\s+(?:insufficient|inadequate|limit)",
    r"does\s+not\s+fit\s+(?:print\s+)?bed",
    r"printability\s+(?:limit|concern|issue|constraint)",
    r"flutter\s+risk",
    r"buckling\s+(?:risk|limit|margin)",
    r"safety\s+factor\s+[\d.]+",
    r"[\d.]+%\s+(?:heavier|mass\s+increase|weight\s+penalty)",
    r"cannot\s+be\s+printed",
    r"print\s+failure",
    r"layer\s+adhesion",
    r"overhang\s+(?:angle|limit)",
]


def main() -> int:
    """Main entry point. Returns 2 for BLOCK, 0 for pass."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only check Write and Edit tools
    if tool_name not in ("Write", "Edit"):
        return 0

    # Get content to check
    content = tool_input.get("content", "")
    if not content:
        return 0

    # Also check the old_string in Edit operations (what's being replaced)
    # But mainly check the NEW content being written
    file_path = tool_input.get("file_path", "")

    content_lower = content.lower()

    # Find forbidden words
    found_forbidden = []
    for pattern in FORBIDDEN_PATTERNS:
        try:
            matches = re.findall(pattern, content_lower)
            if matches:
                found_forbidden.extend(matches)
        except re.error:
            continue

    if not found_forbidden:
        return 0

    # Check if justifications exist in the content
    found_justifications = []
    for pattern in JUSTIFICATION_PATTERNS:
        try:
            matches = re.findall(pattern, content_lower)
            if matches:
                found_justifications.extend(matches)
        except re.error:
            continue

    # If justifications found, allow with note
    if found_justifications:
        print(
            "[anti-simplification-hook] NOTE: Forbidden words detected but appear "
            f"justified ({len(found_justifications)} justification(s) found):",
            file=sys.stderr,
        )
        for f in found_forbidden[:5]:
            print(f"  - '{f}'", file=sys.stderr)
        return 0

    # HARD BLOCK — forbidden words without justification
    print(
        "[anti-simplification-hook] BLOCKED: Forbidden simplification language detected:",
        file=sys.stderr,
    )
    for f in found_forbidden[:10]:
        print(f"  - '{f}'", file=sys.stderr)
    print(
        "\nThe project philosophy is: 'Why make it simple when it can be complex — "
        "for the same price?'",
        file=sys.stderr,
    )
    print(
        "Every 0.1% of performance matters. Simplification is ONLY acceptable when "
        "the optimal solution has a quantified penalty (weight, printability, structural) "
        "— and the user must approve.",
        file=sys.stderr,
    )
    print(
        "\nTo proceed, either:",
        file=sys.stderr,
    )
    print(
        "  1. Use the optimal (more complex) solution instead, OR",
        file=sys.stderr,
    )
    print(
        "  2. Add quantified justification in the content (e.g., 'mass penalty of 12g'), OR",
        file=sys.stderr,
    )
    print(
        "  3. Get explicit user approval for this simplification.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
