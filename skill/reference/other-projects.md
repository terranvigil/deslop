# Using the detector in other repos

The skill is installed globally, so any repo can already ask Claude to
humanize a doc. This page covers running the detector by itself, the way
you'd run a linter: on the prose a branch or commit changed, with a
per-repo config for project jargon.

All commands assume the skill is at `~/.claude/skills/humanize-writing`
and that some Python 3.10 or newer is installed. The script finds one on
its own. Set `DESLOP_PYTHON` if it picks the wrong one.

## Commands

```bash
CT=~/.claude/skills/humanize-writing/scripts/check_tells.sh
$CT README.md                  # every finding in one file
$CT --json README.md           # spans, rule ids, severity, fix scope, metrics
$CT --diff old.md new.md       # what new.md added, plus dropped facts
$CT --changed                  # new findings in Markdown changed since main
$CT --changed HEAD             # ... since the last commit
$CT --strict --changed main    # exit 1 if any new finding is severity 3
~/.claude/skills/humanize-writing/scripts/fact_lock.py old.md new.md  # dropped numbers, dates, URLs, quotes only
```

`--changed` diffs against the merge-base of the base and `HEAD`, reads
each file from the working tree, and includes untracked files. A file
that didn't change prints nothing. So does a file whose edit added no
new tells, even if it has old ones. It exits 0 unless `--strict` is set.

"New" uses the same comparison as `--diff`: a finding matches the old
version when its rule and matched text agree, so rewording the sentence
around an old "robust" doesn't re-report it. Findings with no matched text
(paragraph rhythm, no hedges, flat rhythm) count as new only when the rule
fires more times than it did before.

## .deslop.json

Put it at the repo root. For each file it checks, the detector looks in
the file's directory and each parent up to the git root, and uses the
first `.deslop.json` it finds. So `docs/.deslop.json` can allow extra
jargon for the docs. `ignore` and `include` are read from the root file
only.

```json
{
  "allow":   ["gates", "gating"],
  "disable": ["authorless"],
  "ignore":  ["CHANGELOG.md", "vendor/", "docs/archive/*"],
  "include": ["*.md", "*.markdown"]
}
```

- `allow`: words and phrases that are real terms in this project. It
  silences `word:`, `phrase:`, `overused:` and `llm-adverb:` findings for
  exactly those terms. List each inflection you use.
- `disable`: rule ids (`comma-and-clause`) or whole families (`contrast`).
  `--json` output shows every finding's rule id.
- `ignore`, `include`: which files `--changed` looks at. Globs match the
  repo-relative path, and `*` crosses directories. An entry ending in `/`
  is a directory prefix. A file named on the command line is always
  checked.

Unknown keys print a warning, which catches typos.

## Pre-commit hook

Advisory: it prints new findings and never blocks the commit. Save as
`.git/hooks/pre-commit` and `chmod +x` it:

```sh
#!/bin/sh
ct="$HOME/.claude/skills/humanize-writing/scripts/check_tells.sh"
[ -x "$ct" ] || exit 0
exec "$ct" --changed HEAD
```

Add `--strict` before `--changed` to block on severity 3. The hook reads
the working tree, not the index, so it also sees unstaged edits.

## GitHub Actions

`deslop-check.yml` next to this file is a workflow template. Copy it to
`.github/workflows/`. It checks out `terranvigil/deslop` next to your
code and runs the detector on the changed files. For a private fork, add
`token: ${{ secrets.YOUR_TOKEN }}` to that checkout step. The workflow is
advisory. To make it fail the build, edit the last line to add `--strict`.
