#!/usr/bin/env bash
# Pre-push hook: run tests and lint before allowing push.
# Install: cp hooks/pre-push.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
#
# This hook ensures no failing code reaches the remote. It mirrors the CI
# pipeline so that CI failures are caught locally first.

set -euo pipefail

echo "=== Pre-push: running tests ==="

cd "$(git rev-parse --show-toplevel)"

# Run the same test suite as CI (excluding hardware/project-specific tests)
PYTHONPATH=. python -m pytest tests/ \
    --ignore=tests/test_rpc_helper.py \
    -m "not hardware" \
    -q --tb=short

echo "=== Pre-push: running lint ==="

python -m ruff check src/orchestrator/ src/providers/ tests/ \
    --select E,F,W --ignore E501,F401,E402

echo "=== Pre-push: all checks passed ==="
