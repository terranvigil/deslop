# deslop

A Claude Code skill `humanize-writing`, alias `deslop` that detects AI
prose and rewrites them. It has three parts:

1. A detector: deterministic Python that flags spans by rule and by layer
   (lexical, structural, grammatical, discourse) and scores the document.
   Its rules draw on Wikipedia's "Signs of AI writing", the grammatical
   features in Reinhart et al. (PNAS 2025), and Sam Paech's slop-score
   contrast regexes.
2. A fixer: the skill's workflow. Claude rewrites only the flagged spans
   and checks that every number, date, URL and quote survived. It stops
   after three passes.
3. Evals: checks that dirty fixtures improve while clean fixtures and pre-LLM
   human writing stay clean.
4. Optionally logs findings, can be used to improve training.

## Install

You need Claude Code and Python 3.10 or newer. There are no Python
packages to install.

```bash
git clone https://github.com/terranvigil/deslop.git
cd deslop
ln -s "$PWD/skill" ~/.claude/skills/humanize-writing
mkdir -p ~/.claude/commands
ln -s "$PWD/commands/deslop.md" ~/.claude/commands/deslop.md   # optional /deslop alias
```

Check that the detector runs:

```bash
~/.claude/skills/humanize-writing/scripts/check_tells.sh skill/scripts/testdata/dirty.md
```

It should print one finding per line. If it picks up the wrong Python, set
`DESLOP_PYTHON` to a 3.10+ interpreter.

## Use

In any Claude Code session, ask for it in plain words ("humanize
design.md", "make this PR description sound less like AI") or call it
directly:

```
/humanize-writing docs/design.md
/deslop README.md
```

Claude runs the detector, rewrites the flagged passages, and checks the
result against the original for new tells and dropped facts. It revises
the file in place and reports what changed in a line or two. The same
rules apply when Claude drafts a new document for you.

To run the detector on its own, like a linter:

```bash
CT=~/.claude/skills/humanize-writing/scripts/check_tells.sh
$CT README.md                 # every finding in one file
$CT --json README.md          # spans, rule ids, severity, fix scope, score
$CT --diff old.md new.md      # only what new.md added, plus dropped facts
$CT --changed                 # new findings in Markdown changed since main
```

The exit code is the number of findings. `--strict` makes `--changed` exit
1 on a severity-3 finding. `skill/reference/other-projects.md` has the
rest, including a pre-commit hook and a GitHub Actions template.

## Configure

- **Your voice.** Copy `skill/voice.md` to `skill/voice.local.md` and fill
  it in from things you wrote by hand. The fixer matches it when it writes
  as you. `voice.local.md` is gitignored.
- **Project jargon.** A `.deslop.json` at a repo's root allows terms the
  detector would otherwise flag and turns off rules that don't fit the
  project:

  ```json
  {
    "allow":   ["surface", "surfaces"],
    "disable": ["authorless"],
    "ignore":  ["CHANGELOG.md", "vendor/"]
  }
  ```

  A `.deslop.json` in a subdirectory overrides it for the files below.
  `skill/reference/other-projects.md` lists every key.
- **Pet peeves.** `skill/scripts/deslop/data/personal.json` maps words and
  phrases you never want to see to a fix hint. The detector flags them
  like its own.
- **Rewrite log.** Set `DESLOP_LOG_TRIPLES=1` and the fixer appends each
  accepted rewrite (original span, new text, score change) to
  `logs/triples.jsonl` in this repo. It's off by default. The log is
  gitignored.

## Develop

`skill/` is the installed directory, so edits there are live. The rule
catalog is `skill/reference/tells.md`. The detector's rules are in
`skill/scripts/deslop/rules.py`. `docs/IMPROVING.md` covers adding and
tuning rules.

```bash
make test                   # per-rule dirty/clean examples
scripts/baseline.sh --check # detector output on the fixtures hasn't drifted
scripts/gate.sh             # every eval gate, pass or fail
```

The human-writing gate needs a corpus of pre-LLM prose in
`voice/human-baseline/`, which isn't shipped. Without it, that gate skips.

## Credits

Sam Paech (slop-score, slop-forensics, auto-antislop, the Antislop paper),
WikiProject AI Cleanup, Chakrabarty, Laban and Wu (LAMP, WQRM), Reinhart
et al., Russell, Karpinska and Iyyer, Shaib et al., and the community
humanizer skills that came before this one.

## License

MIT (see `LICENSE`). `skill/scripts/deslop/contrast.py` ports code from
slop-score, which is also MIT. Its notice is in `THIRD_PARTY_LICENSES.md`.
