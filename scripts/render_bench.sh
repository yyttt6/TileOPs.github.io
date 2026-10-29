#!/usr/bin/env bash
# Only an official remote snapshot can populate the upstream-format pages.
set -euo pipefail
cd "$(dirname "$0")/.."
args=()
if [ -n "${ASCEND950_OFFICIAL_SNAPSHOT:-}" ]; then
  args=(--snapshot "$ASCEND950_OFFICIAL_SNAPSHOT")
fi
python3 scripts/render_official_ascend950.py "${args[@]}"
# Explicit user-published cache progress is a separate baseline-only view.
python3 scripts/render_baseline_cache.py
