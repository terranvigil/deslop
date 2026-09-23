# Eval procedure and expectations

Run this after any change to SKILL.md, reference/tells.md, or the detector
behind scripts/check_tells.sh.

## Procedure

For each fixture in `fixtures/`, in a FRESH session or subagent (so the
skill is read cold, with no conversation context):

1. Prompt: "Read ~/.claude/skills/humanize-writing/SKILL.md and follow it
   to revise <fixture path> into <fixture dir>/out-<name>.md. The revised
   file must preserve every factual claim."
2. Run: `~/.claude/skills/humanize-writing/scripts/check_tells.sh
   ~/.claude/skills/humanize-writing/evals/fixtures/out-<name>.md` - must
   exit 0, except for findings the reviser kept on purpose and named in
   its report, which workflow step 4 allows. The slack fixture's one emoji
   is the standing example. The script flags every emoji. The register
   allows one, so keeping it is the right call.
3. Check the must/must-not lists below by reading the output.
4. Delete the out-*.md files afterward; they are not committed.

The untouched fixtures' finding counts are recorded in `baseline/`. After
editing the detector, run `scripts/baseline.sh --check` from the repo root.
Expect the same counts or a change you meant to make, then re-record with
`scripts/baseline.sh` and commit the new counts with the rule change.

## All fixtures: must

- Every factual claim survives: numbers, names, direction of change
  (3,150 to 2,770 km a week, 12%, 40 stations, 1,100 students, 48
  seconds against 2 minutes 10 seconds, 95s to 38s).
- No invented specifics: nothing concrete appears in the output that isn't
  in the fixture.
- Register preserved: the design doc stays technical, the Slack post stays
  celebratory and informal, the PR description stays factual.
- Sentence lengths visibly vary.
- No more than two "X, Y, and Z" triples per document. Plenty of ordinary
  human writing has two, so the bar sits at three.

## All fixtures: must not

- Staccato slogan rewrite (rows of five-word sentences).
- Numbers dropped or rounded away where they were load-bearing; rounding in
  prose is fine, losing the figure is not.
- Meaning drift or dropped claims.
- New headers, bold, or bullets added where the fixture had prose.

## Per fixture

- design-doc.md: the "Despite these challenges" frame under "Final Thoughts" is
  gone and any real open problems are stated plainly. The italic subtitle
  is folded into the opening. The mileage figures appear outside
  parentheses.
  No paragraph holds more than about a dozen digits or any sentence more
  than three figures. Every mileage and pilot figure from the fixture
  still appears somewhere.
- slack-post.md: thanks and enthusiasm survive. The post still reads like
  a launch rather than a status line. At most one emoji, kept on purpose
  over the script's objection. The bold-label bullets become prose or a
  lumpy list. No sycophancy filler.
- pr-description.md: headers are specific or absent; the generation times
  survive; the closing paragraph makes one concrete claim or is cut.
