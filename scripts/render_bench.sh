#!/usr/bin/env bash
# Render 950 evidence; failures preserve the live site. Never fetch the 910 branch.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "${ASCEND950_SYNC_CI:-0}" = "1" ]; then
  python3 scripts/sync_ascend950_ci.py
fi
python3 scripts/gen_ascend950_pages.py
