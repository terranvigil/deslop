---
name: humanize-writing
description: Use when writing or revising any prose document (docs, design docs, emails, Slack posts, READMEs, reports, PR descriptions, proposals), or when asked to humanize, deslop, de-AI, fix the tone or style of text, or make it sound less like AI wrote it.
---

# Humanize Writing

Write prose that reads authored, not generated. This governs prose only.
Leave code, config, log output, and quoted material alone.

Two modes:

- **Generating**: follow the recipe from the first draft.
- **Revising**: find the tells, rewrite in place. Preserve the author's
  meaning, facts, and intentional voice. Never invent content or change claims.
  Inflation with no fact under it isn't a claim: a closing paragraph that
  only asserts significance can go, and so can an unsourced "industry
  reports suggest". What survives is every fact, name, number, and direction
  of change.
  The stance rule below still applies, but a stance you add has to come from
  a commitment the document already makes: if it endorses an approach,
  say so in the author's own person. Don't attribute an opinion the text
  doesn't hold. When the document needs a position it never takes, ask
  rather than supply one.

When writing as the user, read `voice.local.md` first (or `voice.md` if
there's no local copy) and match it. If it's still the unfilled template,
use the recipe alone and offer to calibrate once. When revising,
consult `reference/tells.md` for the full catalog with examples. To check
only the prose a branch changed, allow a repo's jargon (`.deslop.json`), or
set up a hook, see `reference/other-projects.md`.

## Voice recipe

1. **Plain verbs.** "X is Y". Use, help, show, improve, make.
   - Before: "The waitlist acts as a buffer between signups and open class seats."
   - After: "The waitlist holds signups until a class seat opens."
2. **Concrete subjects doing things.** Undo nominalizations. Passive is
   fine when it keeps the paragraph's topic in subject position.
   - Before: "Utilization of the new rota results in a reduction of overtime hours."
   - After: "The new rota means fewer overtime hours."
3. **Vary sentence length on purpose.** Follow a long sentence with a short
   one. Uniform medium-length sentences read generated; detectors call the
   variation burstiness, and the script flags monotone runs.
4. **Contractions** where the register allows: don't, it's, can't.
5. **Take a stance.** First person, honest hedges ("I suspect", "probably"),
   a real opinion where the document calls for one. Generated text is
   confident, impersonal, and praises by adjective; authored text argues.
   This applies to specifications and design docs too: the author exists,
   so decisions read "we chose X because", never "X was chosen".
   - Before: "Both approaches have trade-offs that should be considered."
   - After: "I'd pick the nightly batch. A late invoice is cheaper than a double charge."
6. **Specifics you have, questions for ones you don't.** Concrete details
   come from the source material. Never invent a number, feature, or
   example; if the point needs one, ask.
7. **Standard punctuation.** Hyphens, commas, periods.
8. **End where the fact ends.** No trailing "-ing" significance clause.
   - Before: "Unclaimed parcels go back to the depot after 5 days, contributing to substantial gains in locker availability."
   - After: "Unclaimed parcels go back to the depot after 5 days. That frees 14% of the lockers on a typical Monday."
9. **No throat-clearing, no recap.** Start with the point. Stop when it's made.
10. **Thread sentences with the known-new contract.** Open a sentence from
   something the previous one established, then add the new thing. A run of
   "X1 does Y1. X2 does Y2." rows, each opening a fresh subject, is a list
   wearing paragraph clothes: either thread it (subordinate, connect, lead
   with the point the facts support) or make it a real list.

## Numbers

Generated technical prose inlines figures far more often than authored prose
does. The discipline is selection, not deletion.

- Three or fewer values go in prose. Four to twenty go in a table. More than
  twenty want a chart. A before/after across three or more metrics is a
  table. These are placement rules for documents that can hold a table; in
  Slack, a PR description, or an email, the prose caps below are the whole
  rule.
- At most three figures in a sentence, and only when they form one
  comparison. Two unrelated measurements don't share a sentence. Twelve
  digits per prose paragraph, dates included; digits inside names (A4, B12,
  p99, IPv6) don't count. Lists and tables are exempt; the caps are on
  running prose. Spelled-out numerals count: "a fifth of them" and "twice a
  week" load a reader the same way 0.2 and 2 do.
- **Never derive in prose.** State the result and stop. A sentence that walks
  the arithmetic ("2,016 free lunches a day: 36 schools, 280 pupils each, a
  fifth of them on the free plan") spends a reader's whole
  working memory, about four chunks, before it reaches its point. If the
  derivation matters, give it a table, a figure, or a footnote the reader can
  choose. Readers stop tracking after the third figure in a paragraph, so put
  the load-bearing one first.
- Round to two significant figures in prose **only when the exact value
  survives somewhere else**: a table, an appendix, a linked source. With
  nowhere to put the precise figure, keep it in the sentence. Rounding a
  number out of the document entirely is data loss, not style.
- A derived number gets no more significant figures than its least precise
  input. "About 3,482" is a contradiction: pick the hedge or the precision.
- The table holds the values; the prose names the takeaway. Don't walk the
  cells.
- Keep the exact number inline when it's load-bearing (the SLO, the limit
  that was hit, the headline result), when someone will act on or reproduce
  it (config, thresholds, versions, timestamps, money, the inputs behind an
  estimate), or when the margin is the point. The detector's `table-restated`
  finding fires on this every time, with no load-bearing exception built in
  — that's the tool being mechanical, not this rule being wrong. Keep the
  figure inline per this rule and keep the `table-restated` finding open;
  don't chase it to zero by deleting the one number a reader needs without
  opening the table.
- One headline number per claim of change, where a before/after pair counts
  as one: "median checkout went from 90 seconds to 35" is a single figure in this sense,
  and its delta belongs in the next sentence. Stripping specificity is the
  worse failure.
- A claim of change with no number at all is usually a defect, but not when
  you're revising and the source never had one. Leave it unquantified and
  say so, or ask. Never supply the figure yourself.

## Register

Humanized means authored, not casual. A design doc stays technical, a Slack
post stays loose and keeps its exclamation point and its one emoji, a PR
description stays factual and short, an email stays direct. A launch post
that loses all its warmth is as badly revised as one full of "thrilled". Don't bolt on folksy filler to
sound human. Match the document's job first, the voice profile second.

## Workflow

1. Fix the structure before any sentence-level work. Read the headings
   alone: if they'd fit any other document of this genre, the skeleton is
   generated no matter how the sentences read. Cut the throat-clearing
   intro and the recap outro, merge symmetric sections, and let the hard
   part take more room than the easy parts. Sentence polish on a section
   you should have cut is wasted.
2. Draft or revise from the underlying meaning, following the recipe.
3. Save the prose to a file (a scratch file if it's headed for chat or
   Slack) and run it directly (it's an executable shell script, not a
   Python file — don't prefix it with `python3`):
   `~/.claude/skills/humanize-writing/scripts/check_tells.sh --json <file>`
4. If it reports findings, fix in this order, for up to 3 passes total,
   re-running the script after each pass:
   1. **Clusters first.** `metrics.clusters` names paragraphs with 3 or
      more findings — that's the real signal (see Guardrails). Rewrite
      the whole paragraph from its point, not word by word. The `line`
      a cluster reports is the paragraph's first line, not the span it
      covers: a "paragraph" is a run of non-blank source lines, which can
      visually be many lines long if the source has no blank lines
      between short sentences. Read the whole run, not just that line.
   2. **Remaining findings by severity**, highest first. Each finding's
      `scope` says what the fix has to touch. `sentence`: rewrite the
      sentence the span sits in. `paragraph`: restructure the paragraph
      or list (move figures to a table, vary the rhythm, drop the bold
      labels); a sentence rewrite won't clear it. `document`: a count or
      rate across the file; no single edit clears it, so fix what you
      can in passing and name it in the report. For sentence findings,
      rewrite the sentence, not the word: swapped synonyms keep the
      generated cadence the finding is actually about. Use the finding's
      `layer` for the shape of the fix, not the specific word it named:
      - `lexical`: name the concrete thing the word was standing in for.
        Don't fill the gap with padding ("in a number of ways", "should
        hopefully"); that's a new finding, not a fix (tells 28f).
      - `structural`: state the claim directly; cut the scaffold, the
        transition tic, or the manufactured contrast around it.
      - `grammatical`: end the sentence at the fact; say the consequence,
        if there is one, in its own sentence.
      - `discourse`: commit to the claim or cut the sentence; if it's
        vague because the source is vague, say so or ask, never invent
        a specific to fill the gap.
   3. Stop after 3 passes or once nothing but scattered severity-1
      findings remain, whichever comes first — hitting the pass cap with
      real findings still open (including severity 2 or 3) is a normal,
      sufficient reason to stop, not a sign you did it wrong. A nonzero
      score is fine; the goal is prose a skilled reader doesn't wince at,
      not a 0.
   Findings kept on purpose (literal uses, quoted material, the user's
   own voice per the voice profile, a sanctioned `table-restated` per the Numbers
   section above) are fine — name them in the report line instead of
   arguing with the script.
5. Check what the revision added: run
   `~/.claude/skills/humanize-writing/scripts/check_tells.sh --diff <original> <revised>`
   against the pre-edit and post-edit versions. It lists only findings
   your edits introduced (padding in place of a banned word, a sentence
   split that created a new ", and" clause), any number, date, URL, or
   quoted string that was in the original and is gone, and growth over
   15%. Fix every added finding and every dropped fact before you report
   done. For a dropped fact, either put it back, or if it was already
   invented (not from the source), that's the bug, not the check.
   `fact_lock.py` still runs the fact half on its own.
6. Log what you accepted, only if the environment has
   `DESLOP_LOG_TRIPLES=1` (check with `echo $DESLOP_LOG_TRIPLES`; skip this
   step otherwise). For each rewrite you kept (not ones you reverted or
   the user rejected), run:
   `~/.claude/skills/humanize-writing/scripts/log_triple.py --rule <id> --layer <layer> --original "<span>" --rewrite "<new text>" --score-before <N> --score-after <N>`
   using the finding's `rule` and `layer` from the JSON and the
   document's `metrics.score` before and after your edits. On a dense
   document, log one representative triple per distinct rule id instead
   of one per instance. The log goes to `logs/triples.jsonl` in the
   skill's repo (gitignored) and is local training data for a rewrite
   judge.
7. Walk the self-audit checklist.
8. Report what changed in one or two lines. Show the document, not a
   lecture about it.

## Self-audit checklist

Walk each item. Don't paste the list into your response unless the user
asks for it; the report stays one or two lines.

- [ ] Sentence lengths vary; no run of same-shape sentences, and consecutive sentences don't all open with fresh bare subjects
- [ ] Bullets only where content has parts; items lumpy, not symmetric
- [ ] The document commits to something; no balanced both-sidesing
- [ ] No padded intro or recap outro
- [ ] No template sections ("Challenges and Future Outlook" and kin)
- [ ] Each thing keeps one name throughout
- [ ] No more than two "X, Y, and Z" triples in the document
- [ ] Attribution is specific or absent
- [ ] No significance inflation
- [ ] Headers are specific, or there's no header
- [ ] No appositive labels: every heading, figure title and caption names its subject with words that could be spoken aloud, never two noun phrases joined by a comma ("One timetable, three campuses")
- [ ] Nothing is defined by what it isn't ("it's X, not Y", "isn't X, it's Y", negated headings), and no manufactured foil in the affirmative forms either ("X rather than Y", "as opposed to Y"): a foil stays only when Y was a real option, a rejected decision, or a live misconception. When the source's own claim is a contrast, keep it once and state it plainly
- [ ] No sentence paraphrases itself, and no stubby echo sentence ("That takes preferences.") restates the claim before it
- [ ] No sentence carries a second fact hitched on by a comma (an appositive, "which means", "much like"); each fact gets its own sentence, with the long/short variation kept
- [ ] At most one semicolon in the document
- [ ] Figures obey the number rules: three per sentence, a dozen digits per paragraph, rounded in prose, not restated from a table
- [ ] Every claim of change carries exactly one number, and the load-bearing figures are still exact
- [ ] No trailing participial clause (", ensuring X", ", highlighting Y")
- [ ] Sections are lumpy: the hard part got the most room
- [ ] Something is left open, if the source has one; never manufacture an open question
- [ ] Nothing claims more certainty than the source has; if there's real uncertainty it's hedged, but don't manufacture doubt
- [ ] No overcorrection: no staccato stack, no fake-candid opener, no synonym swaps

## Guardrails

- Never carry the banned-word or banned-phrase list into your own
  rewriting reasoning as a thing to avoid in general; work from the
  specific findings this run of the script produced. Priming a rewrite
  with a list of words not to use has limited effect and can backfire.
  Fix what's actually on the page instead of generating defensively.
- Clusters count, single instances don't. One stiff verb isn't proof of
  anything; don't gut legitimate prose. Look for three or four tells
  converging before you rewrite a passage; detectors flag careful human
  prose all the time for the same reason.
- The overcorrection catalog is in `reference/tells.md` under
  Overcorrection. Read it if a revision pass is running long: word salad,
  broetry, and performed candor are worse than the tells they replaced.
- Revising someone else's text: check for a non-AI explanation before
  rewriting.
- Count the changes the script didn't flag and the checklist doesn't name.
  More than about 8 of those per 500 words means you're overcorrecting, and
  back off. Fixing every mechanical finding in a dense document isn't
  overcorrection even when it touches every sentence.
- Don't compress prose into clipped slogans. Staccato is the
  overcorrected tell.
- When unsplicing semicolon or colon chains, re-link the clauses (because,
  so, which) or reshape the paragraph. A row of disconnected declaratives
  is the same tell with different punctuation.
- Replacements come from the source or from asking, never from invention.
- Break any of these rules sooner than write something barbarous.

## Improving this skill

This skill is meant to grow. When the user corrects the same thing twice,
that's a rule. Route it:

- **Mechanically scannable** (a word, phrase, punctuation mark, or
  formatting pattern a regex can catch): add it to
  `scripts/check_tells.sh`, not to this file.
- **Judgment call** (structure, tone, rhythm): add a short entry with a
  before/after pair to `reference/tells.md`, or a line to the checklist
  here if it's universal.

Don't leave a rule you keep overriding; fix or delete it. After changing
this file, the script, or the catalog, run the eval in
`evals/EXPECTATIONS.md`. Tell the user in one line what changed. Ask before
loosening or removing a rule; small additive tweaks don't need permission.
