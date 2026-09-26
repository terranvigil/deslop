#!/usr/bin/env bash
# check_tells.sh - scan a prose file for mechanical AI tells.
#
# usage: check_tells.sh [--json] [--pr] <file>
#        check_tells.sh --diff [--json] <original> <revised>
#        check_tells.sh [--json] [--strict] --changed [base]
# output: one line per finding: "line N: <tell> -> <fix>", or JSON with --json.
#         --pr adds the PR-description checks (deslop/pr.py): a word budget,
#         development history, number density, results tables, open items
#         without a ticket.
#         --diff prints only the findings the revision added, plus dropped
#         facts (fact_lock.py's check) and the score before and after.
#         --changed reports the findings added to each Markdown file changed
#         since the merge-base with base (default main), untracked files
#         included. a .deslop.json in the repo configures both; see
#         deslop/project.py and reference/other-projects.md.
# exit:   number of findings (capped at 255); 0 = clean; usage error or no
#         python 3.10+ = 255 (see find_python.sh).
#         --diff: added findings + dropped facts; 0 = the revision made
#         nothing worse. --changed: 0, advisory, unless --strict and a new
#         severity-3 finding, then 1.
#
# thin wrapper around the python detector in scripts/deslop/. the rule lists
# live there (rules.py) on purpose: keeping them out of prompt context avoids
# overcompensation and leakage.
# after editing rules, run scripts/baseline.sh --check from the repo root.
export DESLOP_CWD="$PWD"
cd "$(dirname "$0")" || exit 255
. ./find_python.sh || exit 255
exec "$PY" -m deslop "$@"
