# Catalog of AI tells

Read this when revising a document, or when a script finding needs context.
Each entry: the tell, then a before/after pair. Mechanical tells (banned
words, phrases, punctuation, formatting) live in `scripts/check_tells.sh`,
not here; the before-examples below may contain them as demonstration text.

Every entry carries one of four layer tags in brackets: `[lexical]` for word and phrase choice, `[structural]` for
rhetorical shape, formatting and document layout, `[grammatical]` for clause
construction (participial clauses, nominalizations, coordination), and
`[discourse]` for vagueness, redundancy, missing commitment and register.
The tag is the primary layer; some entries touch two.

## Content

1. **Significance inflation.** [discourse] Puffing arbitrary facts up as historic.
   - Before: "The new booking calendar marks a pivotal moment for the clinic's front desk."
   - After: "The new booking calendar replaces the paper appointment book at the front desk."
2. **Trailing "-ing" significance clause.** [grammatical] A participial clause bolted onto a fact to assert meaning.
   - Before: "Recipe pages now load photos last, making it easier for readers on slow connections."
   - After: "Recipe pages now load photos last, so on a slow connection the ingredient list shows up first."
3. **Promotional tone.** [lexical] Travel-guide adjectives on technical subjects.
   - Before: "Crumbline offers a rich set of powerful ordering features."
   - After: "Crumbline takes cake orders by pickup time, size, and allergy note."
4. **Vague attribution.** [discourse] Sourcing a claim to nobody.
   - Before: "Industry reports suggest bike docks fail most often in the first hard frost."
   - After: name the actual source, or drop the claim.
5. **"Challenges and Future Outlook" formula.** [structural] Praise, then "despite these challenges", then vague optimism. Delete the frame; state open problems plainly.
6. **Canned notability.** [discourse] Listing where something was "featured" or "profiled" instead of saying what it does.

## Language

7. **Copula avoidance.** [lexical] "serves as / stands as / functions as / represents / boasts / features / offers" where is/has works.
   - Before: "At the Saturday market, one tablet on the counter functions as both till and order board."
   - After: "At the Saturday market, the counter tablet is the till and the order board."
7b. **Work that "lands".** [lexical] A change, a migration, a PR, or a fix that "lands"
or "landed". Reserve the verb for things that physically land: an aircraft,
a probe. When work arrives, say shipped, went out, is live, is in place.
This holds in Slack too, where "the migration landed" feels natural: it's
the register the tell hides in, not an exception to it.
   - Before: "Crumbline's allergen filter landed on Tuesday after two rounds of review."
   - After: "Crumbline's allergen filter went live on Tuesday after two rounds of review."

7a. **Possessive "carry".** [lexical] A system, field, doc, or config "carries" an attribute where has/holds/stores/records is the plain verb. "Pantry carries the allergenCodes field", "the export carries the full menu", "each order carries empty notes". Literal transport ("the van does not carry chilled goods", "the page number is carried in the query string") is fine.
   - Before: "Every hold record carries a pickup-by date, and the branch desk prints it on the slip."
   - After: "Every hold record has a pickup-by date, which the branch desk prints on the slip."
8. **Negative parallelism.** [structural] "Not just X, but Y"; "not X, but Y"; reflexive "X rather than Y".
   - Before: "This release is not only fixing the double bookings but also giving each dentist a calendar of their own."
   - After: "Each dentist now gets a calendar of their own, which ends the double bookings."
8a. **Appositive label.** [structural] Two noun phrases joined by a comma, with no verb between them, used as a title, heading, figure caption or section label: "One depot, six routes"; "A real refund, one step at a time"; "Two kitchens, one menu, one printer"; "Checklists, not hunches". The tail form is the same move ("..., both shipping now", "..., each with its own X", "..., all at Y"), and a verb earlier in the sentence does not redeem a tacked-on appositive.
   - Before: "One depot, six routes"
   - After: "Delivery routes from the north depot"
   - **Why it happens, so you can catch it in yourself.** The appositive dodges the verb. Naming a thing plainly means committing to what it *is*, which is a falsifiable claim; a comma-joined pair implies a relationship without ever stating one, so it gets the rhetorical shape of a claim at none of the cost. Two other pressures push the same way: this shape is idiomatic in editorial headlines and talk titles, which are dense in the training data and read as "designed", and once a comma follows a short noun phrase the highest-probability continuation is another noun phrase of the same shape, doubly so with a number in it. That is why the count form ("Three X, one Y") is the most common variant.
   - The fix is almost always to name the subject and stop. If the second half carries real information, give it a verb and make it a sentence. Count-led and trailing forms are scanned by check_tells, along with headings that join two phrases with a comma; the verbless caption still needs a human eye.

8b. **Contrast scaffold, negated form.** [structural] "Isn't X, it's Y"; "X; it doesn't Y"; a trailing ", not Y" tacked onto a claim that was already complete. The negated half restates what something isn't before naming what it is, which drags the reader through a claim nobody needed to make.
   - Before: "For most parents the closure text isn't a courtesy, it's the only notice they get."
   - After: "For most parents the closure text is the only notice they get."
   - Cut the negated half and let the positive claim stand alone. If the negated half names a real misconception the reader is likely holding, keep it once, stated plainly, without the "it's Y" scaffold around it. The three surface forms are scanned by check_tells (`scaffold-isnt`, `scaffold-semicolon`, `trailing-not`); a negated heading needs a human eye.

8c. **Manufactured foil.** [structural] The claim arrives strapped to an alternative nobody raised: "X rather than Y", "as opposed to Y", "not so much X as Y", "it reads as X instead of Y". The negated forms in 8b are the same move; this is the affirmative one, and it slips past a reader who is watching for "not X, but Y". Generated prose reaches for a foil because a contrast gives a sentence shape for free, and the foil is usually a straw one the writer invented on the spot.
   - Before: "Members of the farm co-op pick up a weekly box, as opposed to ordering item by item."
   - After: "Members of the farm co-op pick up a weekly box."
   - The test is whether Y was ever on the table. A foil earns its place when it names a real option someone weighed ("we emailed the reminders instead of buying an SMS plan"), a decision the document already rejected, or a misconception the reader is likely holding. Otherwise cut it and let the positive claim stand. Cutting is usually the whole fix; the sentence rarely needs rewriting around the hole.

8e. **Second fact hitched on by a comma.** [grammatical] A sentence states one thing and
   then rides a second fact on a comma: an appositive ("...printed on the
   hold slip, the same slip the desk hands out"), a "which means" clause,
   a "much like" comparison. Each is a fact of its own and wants its own
   sentence; chained, they read generated even when every clause is true.
   - Before: "Couriers open a locker by scanning its code with their phone, which means a flat battery stops the whole drop."
   - After: "Couriers open a locker by scanning its code with their phone. A flat battery stops the whole drop."
   - Keep the long/short variation the recipe asks for; the default when a sentence carries two facts is to split, not to chop every sentence.
8h. **Second clause joined by ", and", or by a bare "and".** [grammatical] Two facts in one sentence, joined by
a comma and a conjunction. It's the written form of the "X, Y" habit. Split them, or make one the reason for
the other.
   - Before: "Returns go through the front desk, and the drop box is emptied only on Mondays."
   - After: "Returns go through the front desk. The drop box is emptied only on Mondays."
   - Before: "Each allotment plot has its own water meter and we read them on the last Sunday of the month."
   - After: "Each allotment plot has its own water meter. We read them on the last Sunday of the month."

8g. **Sing-song verb triple.** [structural] Three parallel verb phrases in one sentence,
   often with a rhythm to them: "weigh the next parcels, price the route,
   and reload before the van leaves". The reader hears the cadence before
   the content.
   - Before: "The forecast lets the bakery size each morning's bake, add staff ahead of a holiday rush, and hold back flour for the orders the weekend will depend on."
   - After: "The forecast says what's coming: how many loaves each day needs, which mornings will be busy, and which orders the weekend depends on. So the bakery can plan the bake, add a baker before a holiday, and keep flour back where it counts."
   - The fix is to say what the thing knows and what it does with it as plain statements. A list of three is fine when the list itself is the content (three modes, three files); it is the tell when it is three verbs performing thoroughness.

8f. **Contrast as a habit.** [structural] Rules 8 and 8c one at a time; this is the page-wide
   version. A document where ", not X", "rather than", "instead of" recur
   every few paragraphs reads generated no matter how each instance is
   justified. check_tells fires
   a summary above 1 per 400 words. The fix is the same as 8c: state the fact,
   keep the one or two foils where the other option was real.

8d. **Self-restatement.** [discourse] One sentence makes a claim and then paraphrases itself, joined by a dash, colon or comma. It reads like emphasis and works like padding, because the second half adds no fact the first half lacked.
   - Before: "The sign-up form asks for two fields, so a parent has almost nothing to type."
   - After: "The sign-up form asks for two fields."
   - Marked forms ("in other words", "put another way", "which is to say") are scanned by check_tells. The unmarked form is the common one and needs a human eye: read the second clause and ask what fact it adds. If the answer is none, keep whichever half is more concrete and delete the other. This is 8b's aphoristic echo compressed into a single sentence.

14c. **Self-posed question with an instant answer.** [structural] "The upshot? Fewer refunds."
    Manufactured drama, mid-paragraph. State the answer as a sentence.
    - Before: "We moved the appointment reminder to the evening before. The catch? Half the patients mute their phones after nine."
    - After: "We moved the appointment reminder to the evening before, though half the patients mute their phones after nine."
14d. **False-suspense transition.** [structural] "Here's the thing", "Here's where it gets
    interesting", "But here's why that matters". Promises a revelation and
    delivers the next ordinary fact.
    - Before: "And here's where it gets interesting: nobody had ever renewed a permit online."
    - After: "Nobody had ever renewed a permit online."
14e. **Pedagogical hand-holding.** [structural] "Let's break this down", "Think of it as a
    very patient school secretary", "Now that we've covered X, let's turn to Y".
    Announcing an explanation instead of giving one.
    - Before: "Let's walk through how the timetable solver works. Think of it as a very patient school secretary."
    - After: "The timetable solver places the hardest lessons first, labs and double periods, then fills the free slots around them."
14f. **Scene-setting opener and the invented persona.** [structural] "In an era of", "Imagine
    a world where", "Meet Dev, a courier who spends his mornings hunting for
    free lockers". Stock people and stock eras standing in for the real case.
    - Before: "Meet Dev, a courier who spends his mornings hunting for free lockers."
    - After: "In September, couriers on the east route spent 25 minutes a morning finding free lockers."
14g. **Unquantified intensifier.** [discourse] "significantly improves", "dramatically
    reduces" with no number anywhere near it. Either give the number or drop
    the adverb; the adverb without evidence is the tell.
    - Before: "Keeping the pantry list in memory dramatically reduced page load times."
    - After: "Keeping the pantry list in memory brought the recipe page from 2.1s to 0.4s."
14h. **Fake-candid opener.** [structural] "Honestly?", "Let's be real", "To be honest with
    you". Performed candor. Humanizing prompts generate these, which is why
    they now read as generated rather than as voice.

23c. **Derivation in prose.** [discourse] Showing the arithmetic that produced a figure: "About 99 kilos of flour a morning: 600 loaves, 150 grams each, plus a tenth for trim and waste." Every step is correct and the reader has stopped reading. Working memory holds about four chunks ([Cowan 2001](https://philpapers.org/rec/COWTMN)), and a derivation spends all four before the sentence reaches its point.
   - Before: as above.
   - After: "The morning bake uses about 99 kilos of flour."
   - The result is the claim; the derivation is a footnote, a table, or a figure the reader can choose to look at. Spelled-out numerals cost the same as digits, so "a tenth" counts against the sentence cap the same way 0.1 would. Where the derivation is genuinely the point, give it its own display block rather than a clause.

## Structure and formatting

15. **Bold-label bullets.** [structural] "**Speed:** it's fast." Make it prose or a real heading. In reference and definition docs, a key naming a stable field (Scope, Purpose, Dependencies, Speed) is legitimate structure and stays. An editorial verb dressed as a key ("**Refactored:**", "**Enhanced:**", "**Optimized:**") is the tell, because it's a sentence wearing a label. The script flags both; keep the reference keys and say so in the report.
16. **Bold in running prose.** [structural] "refunds this term come to **$3,150**". Let the sentence carry it. Bold is for headings and table totals.
17. **Inline-header lists.** [structural] Every bullet shaped "Header: explanation". Lumpy prose beats symmetric bullets.
18. **Heading case drift.** [structural] Pick one heading convention and keep it everywhere. If the first heading is in sentence case, the rest should be too; mixed casing across a doc is the tell.
19. **Cliche headers.** [structural] "Overview", "Key takeaways", "What changed", "Next steps". Specific title or no header.
19a. **"How we X" headers.** [structural] "How we get there", "How we prove it", "How it works", "Getting started", "The road to GA". Cutesy narration standing in for a real section name. Name the content instead.
    - Before: "## How we prove it"
    - After: "## Testing and validation"
20. **Italic subtitle under the title.** [structural] "*Spring term - draft for staff review*". Fold it into the opening paragraph.
21. **Repeated table column headers.** [structural] Re-explaining sourcing in every table ("Oven hours (March actual)"). Establish sourcing once in prose; plain headers after.
22. **Backticks on non-code.** [structural] Table names, Slack channels, config keys styled as code. Backticks are for code, paths, and commands.
23. **Parenthetical data dumps.** [structural] "(3 vans, 11 routes, 90-minute delivery windows)". Weave it in or give it its own sentence.
23a. **Parenthetical asides in bulk.** [structural] Beyond data dumps: if an aside is worth saying, make it part of the sentence; if not, delete it. More than a couple of parentheticals per page is a tell.
23b. **Number-stuffed prose.** [discourse] Beyond parentheses: figures sprayed through
    a paragraph until it reads like a bill of materials. Editorial practice
    gives usable caps. Three or fewer values belong in prose; four to twenty
    belong in a table; more than twenty want a chart. At most three figures
    in a sentence, and only when they form one comparison. About twelve
    digits per prose paragraph, counting dates. Enumerated measurements in a
    list or table are exempt; the cap is on running prose.
    - Before: "Over 14 market days this spring the stall sold 1,840 loaves, took back 212, gave 96 to the food bank and threw out 37, against 1,410 sold in 12 days last spring."
    - After: "Spring sales were up about a third on last year. Returns, donations and waste are in the table."
23c. **False precision, and hedged precision.** [discourse] "About 3,418" is a
    contradiction: it's either about 3,400 or it is 3,418. A derived number
    gets no more significant figures than its least precise input, so an
    estimate built from estimates rounds to two. Decimals on a percentage
    need a denominator over 100; under about 50, give the fraction ("5 of
    12") instead of a percentage at all.
    - Before: "Each ride drains about 3.47% of a battery, so the fleet needs an estimated 1,283 swaps a week."
    - After: "A ride uses about 3.5% of a battery, which puts the fleet at roughly 1,300 swaps a week. The working is in the appendix."
23d. **Restating table values in prose.** [discourse] The table holds the values, the
    prose names the takeaway. If the prose walks every cell, delete the
    table or delete the prose.
    - Before: "Holds wait 4.2 days at Eastgate and 11.6 days at Millbrook, and the other five branches fall between 5.1 and 7.3 days."
    - After: "Millbrook's holds wait nearly three times as long as Eastgate's. The table has every branch."
23e. **When the inline number is right.** [discourse] The counter-rule, and the bigger
    risk: stripping specificity makes writing worse. Keep the exact figure
    in prose when it's the load-bearing value of the document (the SLO, the
    limit that was hit, the headline result), when someone will act on or
    reproduce it (config values, thresholds, versions, timestamps, money on
    an invoice), when the margin is the point ("312 of the 320 lockers"),
    or when precision itself is the message. Every claim of change gets
    exactly one number: zero is as much a defect as five.

24. **Tilde approximations.** [lexical] "~30%" in prose. "About" or the plain number, and sparingly.
24a. **Dates and statuses baked into sentences.** [structural] Parenthetical dates and status tags sprinkled through prose read like a changelog bot and go stale the moment the ticket moves. Especially common in ticket descriptions and status writeups. State the fact; link the ticket for its live status; keep a date only when the date itself is the point.
    - Before: "The lane-closure form was rebuilt under PERMIT-77 [DONE] and the fee refund work (in progress) should wrap up by 2026-11-30."
    - After: "PERMIT-77 rebuilt the lane-closure form. The fee refund work is tracked in PERMIT-81."
25. **Small "Key Statistics" tables** [structural] that should be a sentence.
26. **"X is what does Y" reveal.** [structural] "The evening prep shift is what closes that gap." Just say what it does.
27. **Symmetric bullet lists.** [structural] Every item the same length and shape. Real lists are lumpy.

27a. **Setup-payoff sentence pair.** [structural] A short framing sentence whose only job is to introduce the next sentence: "The ordering matters. Lab periods are placed first..."; "Two things matter here. First..."; "The reasoning is simple. X because Y." The frame adds no fact; it stalls the reader for a beat of anticipation. Fold the framing word into the content sentence, or cut it. Once per document is a rhetorical choice; a habit of it is generated cadence.
   - Before: "The fix was small. Returned books with a hold on them now go straight to the holds shelf instead of the sorting cart."
   - After: "Returned books with a hold on them now go straight to the holds shelf instead of the sorting cart."


27b. **Workhorse metaphor overuse.** [lexical] One term drafted to carry every instance of a concept: every checkpoint is a "gate", every API a "surface", every dependency "rides" something. Each use is fine alone; the density is the tell. Keep the term where it's established vocabulary (GA gate), and name the concrete thing elsewhere (exit condition, prerequisite, check).
   - Before: "Three gates recur. The tasting gate is... The allergen-label gate is..."
   - After: "Three checks recur. The tasting panel is... Allergen labels match the recipe card for N batches in a row..."


27d. **Clipped-declaration paragraph openers.** [structural] Every paragraph opens with a short assertive declaration, then the elaboration: "Late orders get a phone call. When a cake..." / "Holidays are handled. A closed day..." One is fine; a section of them reads generated. Open with a full sentence that says the actual thing.
   - Before: "Late orders get a phone call. When a cake order comes in less than 48 hours before pickup, someone rings the customer to confirm."
   - After: "Someone rings the customer to confirm any cake order placed less than 48 hours before pickup."

27c. **Authorless spec voice.** [discourse] Specifications and design docs written with no author present: every choice appears as passive fact ("X was chosen", "the design has Y") and "I"/"we" never occur. Real specs have authors who decided things: "we chose SQLite", "I rejected a shared spreadsheet because", "we'll check this during the pilot week". Use first person for decisions, opinions, and commitments; keep plain declaratives for how the system behaves.
   - Before: "The timetable is generated nightly. Manual overrides are not supported in the first release."
   - After: "We generate the timetable nightly. I left manual overrides out of the first release because no teacher in the pilot asked for them."


27e. **Parallel label openers with a contrast label.** [structural] A run of paragraphs or bullets that all open `Label: list, of, items`, where one label is a stiff contrast pair like "Estimated rather than measured", "Known vs unknown", "Measured, not projected". The symmetry is the tell, and the contrast label is the worst of them because no one says it aloud. Thread the items into prose that says where each number came from, or keep one label and drop the rest.
   - Before: "Known: 14 routes, 38 couriers. Unknown: holiday volume, locker faults. Assumed, not timed: the 6-minute handoff."
   - After: "We know the network runs 14 routes with 38 couriers. Nobody has timed the 6-minute handoff yet, and holiday volume and locker faults are open questions."


27f. **Even section weight.** [structural] Every section the same size, every topic
covered to the same depth. A person writes long about the part that was
hard and skips what didn't need saying, so you can find the real problem by
looking at which section got the most room. Uniform coverage is the shape of
an outline that was filled in rather than a document that was written.

27g. **Template skeleton.** [structural] Two documents on unrelated topics with the same
section sequence. Models reuse discourse structure across topics; people
don't. Read your headings alone: if they'd fit any other document of the
same genre, the skeleton is generated even when every sentence has been
rewritten. This is the tell that survives word-level editing, which is why
structure gets fixed before sentences.

27h. **Everything resolves.** [discourse] The document opens with a thesis, supports it,
and closes with everything settled. Real technical documents leave threads
open: an unanswered question, a decision deferred, a number nobody has
measured yet. Say what's still unknown and stop there.

27i. **Parallel heading shapes.** [structural] Headings that are all the same grammatical
form, often "X and Y" pairs. Human headings are lumpy: a noun phrase, then
a question, then a two-word label.

27j. **Thematic breaks as section glue.** [structural] A `---` rule between every section.
A chat-rendering habit exported into documents. Headings already separate
sections.

27k. **Missing human artifacts.** [discourse] Things models don't produce and people do:
a TODO left in place, an internal name used without introduction, a
reference to shared context ("since the incident last month"), a dependency
quirk noted in passing, an estimate that is round because nobody measured
it. Don't manufacture these, but don't sand them out of a draft either.

## Overcorrection

The failure mode on the other side. These read worse than the AI tells they
replaced, and they are what humanizing tools and "write how you talk"
prompts actually produce.

28a. **The staccato stack.** [structural] "The menu changed. Orders fell. Panic
followed." Sermon rhythm, not thought. Human rhythm bounces between a
fragment, a long subordinated sentence, and a flat declarative; it isn't
uniformly short. The repair for monotone medium sentences is variation, not
shortness.
   - Before: "The menu changed. Orders fell. Panic followed."
   - After: "When the menu changed, weekday orders dropped by a third. The panic was predictable."

28b. **Broetry.** [structural] One sentence per line, blank line between, building to a
lesson. Reads as generated now regardless of who wrote it.

28c. **Thesaurus salad.** [lexical] Synonym-swapping to move the statistical
signature: technical phrasing comes out subtly wrong and the meaning drifts.
This is what commercial humanizers do, and it degrades technical writing
worst. Rewrite the sentence from its point; never swap words in place.

28d. **Forced casualness on a formal skeleton.** [discourse] Contractions and slang
sprinkled over template structure. A document that is formal in shape and
chummy in diction reads worse than either one alone.

28e. **Deliberate typos and lowercase.** [lexical] Fools weak detectors, fools no
reader, and in technical writing just reads as careless.

28f. **Padding in place of the banned word.** [discourse] The buzzword comes out and
filler goes in: "leverage" becomes "makes use of ... in order to help", "robust"
becomes "should hopefully provide a reasonably stable base", and a claim gets
wrapped in "It should probably be noted that" or "in a number of places". The
sentence is longer, says less, and no longer trips the word list. A single
honest hedge is fine (the recipe asks for them); throat-clearing, vague
quantities, and three hedges in one sentence are not. The checker flags those
as `throat-clearing`, `vague-quantity` and `hedge-stack`.
   - Before: "The co-op's delivery sheet has been meticulously streamlined."
   - Padded: "It should probably be noted that the delivery sheet has been made somewhat simpler in a number of ways, which may help drivers."
   - After: "The delivery sheet is now one page, sorted by route." (Or, if the source doesn't say what changed: "The delivery sheet is shorter.")

## Meta

28. **Chatbot residue.** [lexical] "I hope this helps", "Would you like me to", "Certainly!".
29. **Restating the prompt** [discourse] before answering it.
30. **Sycophancy.** [lexical] "Great question!", "You're absolutely right".
31. **Knowledge-cutoff phrasing.** [lexical] "As of my last update", "details are not widely documented".
32. **Placeholder leakage.** [lexical] "[Your Name]", unfilled template slots.

## On the shelf life of this catalog

Lexical tells decay from both ends. The 2023-24 vocabulary (delve, tapestry,
realm, beacon) collapsed after the backlash: models suppress those words now
and people picked some of them up, so their absence proves nothing and their
presence increasingly means an old model rather than a model at all. The
mid-2024-25 wave (align with, enhance, highlighting, showcasing, emphasizing)
is the current one. Keeping stale words banned is harmless because they cost
nothing in a document that wasn't going to use them, but don't expect the word
list to carry the load.

The structural tells hold up better: trailing participial clauses, negative
parallelism, copula avoidance, even section weight, flat sentence rhythm, no
hedging, no author. Reinhart et al. (2025) measured GPT-4o at 5.3x the human
rate for participial clauses and 2.1x for nominalizations, the two largest
gaps found; those survive lexical editing, which is why they matter more than
the word list.

One caution the sources agree on: no single instance convicts. Every item here
has a legitimate use, and detectors flagged Paul Graham's 2013 essay at 90% AI
because polished low-surprise prose looks generated. Look for three or four
tells converging before rewriting anything.
