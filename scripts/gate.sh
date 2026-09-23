#!/usr/bin/env bash
# scripts/gate.sh [--write-human-baseline]
# thin wrapper, see scripts/gate.py for what each gate checks.
cd "$(dirname "$0")/.." || exit 1
. skill/scripts/find_python.sh || exit 1
exec "$PY" scripts/gate.py "$@"
