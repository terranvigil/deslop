# Improving deslop

How to change the detector and the fixer without making either worse.

There are two parts to improve. The detector (`skill/scripts/deslop/`)
gets better through rules and thresholds. Each one is measured against
human text. The fixer is the Workflow section of `skill/SKILL.md`. We
change it only when cold runs on the fixtures show the edit helped. For
either one, change one thing at a time and run the tests and the gate
afterward. If the evals don't show a change helped, it probably didn't.

```bash
make test                     # per-rule dirty/clean examples and the --diff tests
scripts/baseline.sh --check   # fixture finding counts still match skill/evals/baseline/
scripts/gate.sh               # every eval gate
```

## Before you start

- Python 3.10 or newer. The scripts find one on their own. Set
  `DESLOP_PYTHON` if they pick the wrong one.
- Some checks need a corpus of human-written prose that isn't in the repo,
  because it's other people's writing. `scripts/gate.sh` reads it from
  `voice/human-baseline/blog/` and `paper/` (gitignored), one plain-text
  document per `.txt` file, and gate 1 skips without it. Any
  sizable body of technical prose written before 2022 works for measuring
  a rule by hand.
- Three rules come up constantly: every rule ships with a dirty and a
  clean example, never gate on an LLM's opinion of writing alone, and
  never put a ban list into a rewrite prompt.

## What the gate checks

1. The false-positive rate on the human corpus doesn't regress past the
   rate recorded in `skill/evals/baseline/human-baseline.json`.
   Typography and number rules are left out, since published web pages use
   curly quotes and this corpus is number-heavy on purpose.
2. `scripts/baseline.sh --check` passes.
3. The dirty fixtures still score above a loose floor, and `clean.md`
   scores exactly 0. This catches a rule table gutted by accident.
4. `fact_lock.py` and the even-section-weight rule still tell apart a
   synthetic good/bad pair.
5. `make test` passes.

## Adding a rule

1. **Measure it on human text.** Count matches in the human corpus. A few
   lines of Python with `re.finditer` is enough. Unwrap paragraphs first,
   the way the detector does, or a phrase split across a line break will
   hide.
2. **Check the AI side.** The rule needs support in AI-styled text that
   wasn't written to test it: `skill/scripts/testdata/dirty.md`, the
   fixtures in `skill/evals/fixtures/`, or real fixer output. Zero human
   hits alone isn't enough.
3. **Decide.** Ship it if it stays rare in human text and shows up in AI
   text. For scale, "in order to" is common in human prose and isn't a
   rule. A rejected rule is a result too, so say why in the PR.
4. **Add it.** A regex rule goes in `PATTERNS` in `rules.py`. A word or
   phrase goes in `WORDS` or `PHRASES`. A rule that needs counts across the
   document goes in `detect.py`. Give it a `FIX_SCOPE` entry: `sentence`
   if a one-sentence rewrite can clear it, `paragraph` or `document` if it
   can't. The tests fail if it has none.
5. **Add its examples** to `skill/scripts/tests/rule_examples.py`: one
   dirty sentence that fires it and one clean sentence that fires nothing.
6. **Re-record and gate.** If `scripts/baseline.sh --check` shows a
   fixture's count moved, check that the change is the one you meant, then
   run `scripts/baseline.sh` to re-record it. Run
   `scripts/gate.sh --write-human-baseline` so the recorded human rate
   matches, then `scripts/gate.sh`. Commit the baseline changes with the
   rule so the diff shows what moved.

A judgment call that a regex can't catch goes in `skill/reference/tells.md`
as an entry with a before/after pair, not in the detector.

## Loosening or removing a rule

Same loop in reverse. Look at the rule's human hits and decide whether
they're false positives or normal writing the rule shouldn't flag. Words
like "drive" and "ecosystem" are ordinary pre-LLM tech jargon, so they
aren't on the list (`rules.py` has the comment). False positives the tests
turn up count too.

## Thresholds

Metric thresholds (participial rate, section weight) live in
`rules.THRESHOLDS`. Set them from distributions, not by feel:

```bash
cd skill/scripts
python3 -m deslop.calibrate human <human files...> -- dirty testdata/dirty.md
```

It prints the median, p90 and p95 of each metric per label, over files of
300 words or more. Put the threshold between the human p95 and the dirty
side, and write the numbers in the comment next to it, as the existing
entries do.

## Word lists

`skill/scripts/deslop/data/` layers extra words and phrases over
`rules.py`. `personal.json` holds one writer's pet peeves. A
`fingerprint.json` in the same format, if present, is merged too; it's
meant for a list measured from current model output.

## Improving the fixer

Change the Workflow text the way you'd change code:

1. Make one change.
2. Have a fresh agent run the workflow cold on
   `skill/scripts/testdata/dirty.md` and on each eval fixture, per
   `skill/evals/EXPECTATIONS.md`.
3. Compare with `check_tells.sh --diff <original> <revised>`. It shows
   the findings the revision added, the facts it dropped and how much it
   grew. A change that lowers the score by padding or dropping facts is a
   regression.
4. Read the output yourself. The score is a floor. The goal is prose a
   skilled reader doesn't wince at.

Two things never go into `SKILL.md`: the rule lists, and examples taken
from the logs. Both teach the fixer to dodge the detector instead of
writing better.
