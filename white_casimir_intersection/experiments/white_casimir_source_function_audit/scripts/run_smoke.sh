#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export MPLCONFIGDIR="${TMPDIR:-/tmp}/white_casimir_mplconfig"
export XDG_CACHE_HOME="${TMPDIR:-/tmp}/white_casimir_xdg_cache"
mkdir -p "$MPLCONFIGDIR" "$XDG_CACHE_HOME/fontconfig"
PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python -m white_casimir_audit.report --base-dir "$ROOT"
