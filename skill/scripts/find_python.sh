# find_python.sh - sourced, not run. sets PY to a python 3.10+ interpreter.
#
# the detector uses 3.10 syntax (X | None). macOS ships /usr/bin/python3 as
# 3.9, and a Claude Code shell can find it before Homebrew's even when
# ~/.zprofile runs brew shellenv. so don't trust whatever python3 is first
# on PATH: take $DESLOP_PYTHON if set, else the first candidate that's new
# enough. on failure, print why and return 1; the caller decides the exit.
PY=""
for c in ${DESLOP_PYTHON:+"$DESLOP_PYTHON"} python3 python3.14 python3.13 python3.12 python3.11 python3.10 \
         /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if command -v "$c" >/dev/null 2>&1 &&
     "$c" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
    PY="$c"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "deslop: needs python 3.10 or newer; found none (python3 is $(python3 --version 2>&1))." >&2
  echo "  install one (brew install python) or set DESLOP_PYTHON=/path/to/python3" >&2
  return 1 2>/dev/null || exit 1
fi
