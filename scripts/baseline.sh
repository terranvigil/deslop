#!/usr/bin/env bash
# run skill/scripts/check_tells.sh over every fixture and testdata file and
# write the output to skill/evals/baseline/. with --check, compare against
# what's committed instead of overwriting, and exit 1 on any drift.
#
#   scripts/baseline.sh          # regenerate
#   scripts/baseline.sh --check  # verify the checker still matches the baseline
set -u
cd "$(dirname "$0")/.."

CHECKER=skill/scripts/check_tells.sh
OUT=skill/evals/baseline
INPUTS="skill/evals/fixtures/design-doc.md
skill/evals/fixtures/pr-description.md
skill/evals/fixtures/slack-post.md
skill/scripts/testdata/dirty.md
skill/scripts/testdata/clean.md"

mode="${1:-write}"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
drift=0

for f in $INPUTS; do
  name="$(basename "$f" .md)"
  bash "$CHECKER" "$f" > "$tmpdir/$name.txt" 2>&1
  code=$?
  printf 'exit %d\n' "$code" >> "$tmpdir/$name.txt"
  if [ "$mode" = "--check" ]; then
    if diff -u "$OUT/$name.txt" "$tmpdir/$name.txt"; then
      printf '%-18s ok (exit %d)\n' "$name" "$code"
    else
      printf '%-18s DRIFT\n' "$name"
      drift=1
    fi
  else
    cp "$tmpdir/$name.txt" "$OUT/$name.txt"
    printf '%-18s exit %d\n' "$name" "$code"
  fi
done

exit "$drift"
