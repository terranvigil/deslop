# deslop

The `humanize-writing` Claude Code skill: a deterministic detector for AI
writing tells, a span-targeted fixer, and an eval suite both have to pass.
`README.md` has the layout and setup; `docs/IMPROVING.md` covers adding
rules and running the gates.

## Rules for this repo

- Don't break the existing fixtures. `skill/scripts/check_tells.sh` must keep
  working as an entry point.
- Every new rule ships with one dirty example that trips it and one clean
  example that fires nothing (`make test`).
- Never gate on an LLM's opinion of writing quality alone.
- Never put a ban list into a rewrite prompt.
- Never invent facts to make prose more specific. Flag vagueness instead.
- Check licenses before vendoring: slop-score's code is MIT but its wordfreq
  data is CC-BY-SA.
- Docs and comments describe the project as it is. Keep development history
  out of tracked files.
- Develop in `skill/`; that's the directory that gets installed.

## Goal

Prose a skilled reader doesn't wince at. Not detector evasion.
