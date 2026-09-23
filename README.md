# deslop

Detect and fix the writing habits that make AI prose easy to spot. It's a `humanize-writing` Claude Code skill with three parts:

1. The detector is deterministic code that flags spans by rule and by layer
   (lexical, structural, grammatical, discourse) and reports a score. It draws
   on Wikipedia's "Signs of AI writing", the grammatical features from
   Reinhart et al. (PNAS 2025), and Sam Paech's slop-score contrast regexes.
2. The fixer is a skill that rewrites only flagged spans, keeps facts locked,
   follows the writer's voice sample, and stops after a few passes.
3. In the evals, dirty fixtures have to get better while clean fixtures and
   pre-LLM human writing stay clean and every fact survives. The evals decide
   whether a change helped.

The goal is prose a skilled reader doesn't wince at.

## Layout

```
skill/                the skill itself, symlinked into ~/.claude/skills/
  SKILL.md            the fixer workflow
  scripts/            detector (deslop/), fact lock, check_tells.sh entry point
  evals/              fixtures, baselines and eval expectations
  reference/          the tell catalog and use in other repos
commands/deslop.md    /deslop, an alias for the skill
docs/IMPROVING.md     adding and tuning rules, the fixer, running the gates
scripts/gate.sh       one command, pass/fail per eval gate
scripts/baseline.sh   regenerate or check the fixture baseline
CLAUDE.md             repo rules, loaded by Claude Code
```

## Setup

Develop in `skill/`, since that's the directory that gets installed. Symlink
it in:

```bash
ln -s "$PWD/skill" ~/.claude/skills/humanize-writing
mkdir -p ~/.claude/commands && ln -s "$PWD/commands/deslop.md" ~/.claude/commands/deslop.md
```

The second link adds `/deslop` as an alias for `/humanize-writing`.

Then verify:

```bash
scripts/gate.sh
```

## Using it in other repos

Nothing to install per repo. Ask Claude to humanize a doc, or run the
detector directly:

```bash
~/.claude/skills/humanize-writing/scripts/check_tells.sh --changed   # new findings since main
```

`skill/reference/other-projects.md` covers `--changed`, the per-repo
`.deslop.json`, an advisory pre-commit hook and a GitHub Actions template.

## Credits

Sam Paech (slop-score, slop-forensics, auto-antislop, the Antislop paper),
WikiProject AI Cleanup, Chakrabarty, Laban and Wu (LAMP, WQRM), Reinhart et al.,
Russell, Karpinska and Iyyer, Shaib et al., and the community humanizer
skills that came before this one.

## License

MIT (see `LICENSE`). `skill/scripts/deslop/contrast.py` ports code from
slop-score, which is also MIT. Its notice is in `THIRD_PARTY_LICENSES.md`.
