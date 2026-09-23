# Checker baseline

Output of `skill/scripts/check_tells.sh` on every eval fixture and testdata
file. Each `.txt` file ends with the exit code, which is the finding count
(capped at 255). `clean.txt` must stay at 0.

Regenerate with `scripts/baseline.sh` from the repo root. Verify with
`scripts/baseline.sh --check`, which diffs each output and exits 1 on drift.
A drift is either a bug or a rule change you meant; re-record only in the
second case, in the same commit as the rule.

`human-baseline.json` holds the detector's false-positive rate per 1k words
on a corpus of human-written technical prose, which `scripts/gate.sh`
compares against. The corpus isn't in the repo, so that gate skips without
it. Regenerate with `scripts/gate.sh --write-human-baseline` after a
deliberate detector change.
