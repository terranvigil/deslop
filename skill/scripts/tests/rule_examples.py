"""one dirty example that trips each rule and one clean example that
doesn't: every rule ships with both. test_rules.py checks the
dirty one fires that rule and the clean one fires nothing at all.

families (word:, phrase:, contrast:, overused:, llm-adverb:) have their
own entries below. every contrast frame is listed by name, since each is
a separate regex; the word and phrase lists are checked by a sample,
since they're plain literals.

examples that need a whole document (rates, budgets, 300-word floors)
are built by the functions at the bottom.
"""

# a neutral filler sentence for padding documents out without tripping
# anything; varied lengths so the rhythm rules stay quiet.
FILL = [
    "Saturday stalls get assigned by lottery on Thursday night.",
    "Nobody likes it.",
    "I sat in on the draw twice this spring, once for the flower sellers and once for a cheese stand that kept losing its corner spot, so the complaints were about the rules themselves.",
    "Those rules date from before the website.",
    "If vendors ask again at the spring meeting, we'll probably move the draw to Wednesday.",
]


def filler(words: int) -> str:
    out, n, i = [], 0, 0
    while n < words:
        s = FILL[i % len(FILL)]
        out.append(s)
        n += len(s.split())
        i += 1
        if i % 5 == 0:
            out.append("\n\n")
    return " ".join(out)


EXAMPLES = {
    # --- pattern rules, rules.PATTERNS ---------------------------------------
    "em-dash": ("Pickup moves to the side door — the front steps are being redone.", "Pickup moves to the side door while the front steps are redone."),
    "en-dash": ("Checkout opens at noon – two hours late.", "The lottery covers stalls 12-40."),
    "spaced-hyphen": ("Swim lessons are full - try the Thursday class.", "Swim lessons are full, so try the Thursday class."),
    "double-hyphen": ("The printer jammed--again.", "Pass --verbose to see each row."),
    "arrow": ("Book a slot → get a confirmation text.", "Booking a slot sends a confirmation text."),
    "arrow-other": ("Missed appointments ↓ since reminders started.", "Missed appointments went down once reminders started."),
    "emoji": ("New menu is live 🍞", "New menu is live."),
    "emoji-symbol": ("Careful with the old export ⚠", "Careful with the old export."),
    "transition-tic": ("In practice, most families pick the early slot.", "Most families pick the early slot."),
    "curly-quote": ("The sign says ‘back in five minutes’ all afternoon.", "The sign says 'back in five minutes' all afternoon."),
    "bold-label": ("- **Note:** the gym closes early on Fridays.", "- The gym closes early on Fridays."),
    "bold-inline": ("Please bring **exact** change.", "Please bring exact change."),
    "data-parens": ("Most orders ship the same day (about 85% last month).", "About 85% of orders shipped the same day last month."),
    "negative-parallelism": ("The app not only books courts but also rents rackets.", "The app books courts and rents rackets."),
    "to-front": ("A kiosk is going in to front the returns desk.", "A kiosk now handles the returns desk queue."),
    "scaffold-isnt": ("Parking isn't the problem, it's the signage.", "The signage is the problem."),
    "scaffold-semicolon": ("Late fees go to the branch; they don't fund new books.", "Late fees go to the branch budget."),
    "trailing-not": ("Grades are posted by class, not for each student.", "Grades are posted by class."),
    "rather-than": ("Rather than email everyone, the office posts one notice.", "The office posts one notice."),
    "as-opposed-to": ("Weekend tickets cost more as opposed to weekday ones.", "Weekend tickets cost more than weekday ones."),
    "appositive-heading": ("## Bike docks, a field guide", "## Finding a free dock"),
    "not-so-much": ("The fair is not so much a market as a party.", "The fair is mostly a party."),
    "no-longer-but": ("Registration is no longer on paper but online.", "Registration is online now."),
    "reflexive-comparison": ("The form feels like a quiz instead of a signup.", "The form asks eleven questions."),
    "self-restatement": ("Returns close at five. Put another way, use the drop box after that.", "Use the drop box after five."),
    "aphoristic-echo": ("Every tray gets weighed twice. That was new.", "Weighing every tray twice started this month."),
    "formulaic-transition": ("Furthermore, the pool closes at eight.", "The pool also closes at eight."),
    "tilde": ("The walk takes ~15 minutes.", "The walk takes about 15 minutes."),
    "cliche-header": ("## Conclusion", "## Where the waitlist stands"),
    "how-we-header": ("## The road to a shorter queue", "## Queue length since March"),
    "fact-dense-paragraph": ("Since v4.12.1 the `reminder_send` job (BK-2291) double-sends to about 140 of 2,300 members on the `nightly-eu` cron, and BK-2240 touched `send_window_min`.",
                             "Some members get the same class reminder twice. It started with the last release and only affects the nightly European run."),
    "ticket-url": ("Fixed in https://tracker.example.com/browse/BK-2291 last week.", "Fixed in [BK-2291](https://tracker.example.com/browse/BK-2291) last week."),
    "date-in-prose": ("Sign-ups opened 2026-02-09 and filled in a day.", "Sign-ups filled within a day of opening."),
    "schedule-date": ("The new routes start Q3 2027.", "The new routes start after the council vote."),
    "status-tag": ("[WIP] Menu import for the spring catalog", "Menu import for the spring catalog is still underway."),
    "status-parens": ("Refunds for cancelled classes (backlog) go out monthly.", "Refunds for cancelled classes go out monthly."),
    "count-appositive": ("Two kitchens, three shifts, one walk-in fridge.", "Two kitchens share one walk-in fridge across three shifts."),
    "possessive-carry": ("The loyalty card carried no expiry date.", "The loyalty card had no expiry date."),
    "in-todays": ("In today's busy households, meal plans save time.", "Meal plans save time."),
    "labeled-intro": ("The short version: the gym is closed Monday.", "The gym is closed Monday."),
    "moves-the-line": ("Free delivery is moving the order line.", "Free delivery added about forty orders a week."),
    "sharp-edge": ("Bulk refunds are the sharpest edge in the admin panel.", "Bulk refunds can issue the same refund twice."),
    "hedged-precision": ("The survey drew roughly 1,237 replies.", "The survey drew 1,237 replies."),
    "over-precise-pct": ("Attendance rose to 91.25 percent.", "Attendance rose to 91 percent."),
    "pseudo-cleft": ("A second oven is what makes Saturdays possible.", "A second oven gets us through Saturdays."),
    "self-posed-question": ("The catch? Refunds take a week.", "Refunds take a week."),
    "false-suspense": ("Here's why the queue jumps at noon.", "The queue jumps at noon when school lets out."),
    "fake-candid": ("To be honest with you, nobody reads the FAQ.", "Nobody reads the FAQ."),
    "reminder-close": ("Remember, spots are first come, first served.", "Spots are first come, first served."),
    "hand-holding": ("Think of it as a library card for tools.", "It works like a library card for tools."),
    "scene-setting": ("Picture this: a Saturday market with no queue at the cash stall.", "The cash stall had no queue on Saturday."),
    "invented-persona": ("Imagine Tom, a parent juggling three pickups.", "Parents often juggle three pickups."),
    "quietly": ("The tool library is quietly building a waitlist.", "The tool library has a waitlist now."),
    "unquantified-intensifier": ("Queue times dropped dramatically after the change.", "Queue times dropped from twenty minutes to five."),
    "trailing-participial": ("The council approved the budget, signaling support for the pool.", "The council approved the pool budget."),
    "formulaic-transition-2": ("Consequently, the draw moved to Wednesday.", "The draw moved to Wednesday."),
    "model-residue": ("Opening hours are listed below.:contentReference[oaicite:2]{index=2}", "Opening hours are listed below."),
    "hitched-comma": ("The van broke down, something that happens every winter.", "The van broke down again this winter."),
    "comma-and-clause": ("Classes start at nine, but most kids arrive early.", "Most kids arrive before classes start at nine."),
    "hitched-with": ("The market opened, with one stall still setting up.", "The market opened while one stall was still setting up."),
    "bare-and-clause": ("Parents book online and they get a text the day before.", "Parents who book online get a text the day before."),
    "throat-clearing": ("I just wanted to let everyone know the pool is closed Monday.", "The pool is closed Monday."),
    "vague-quantity": ("Most of the complaints were resolved in many of the cases.", "Staff resolved most of the complaints within a week."),
    # --- detector checks, detect.py -------------------------------------------
    "quantifier-tail": ("The branches reopened Monday, each with shorter hours.", "Each branch reopened Monday with shorter hours."),
    "italic-subtitle": ("# Spring fair\n\n_What went right and what did not_\n\nStalls sold out.", "# Spring fair\n\nStalls sold out by _ten_ in the morning."),
    "hedge-stack": ("Perhaps the new timetable might arguably suit most teachers.", "The new timetable suits most teachers, I think."),
    "number-dense-sentence": ("The shelter took in 14 dogs, 9 cats, 3 rabbits and 2 ferrets.", "The shelter took in more dogs than cats this month."),
    "number-dense-paragraph": ("Membership was 1402 in 2023 and 1876 in 2024.", "Membership grew by about a third over two years."),
    "monotone-rhythm": ("The pool opens for lap swim at six each morning. Families get the shallow end from ten until noon. The swim team books every lane after school ends. Evening classes fill the deep end on weekday nights.",
                        "Lap swim starts at six. Families get the shallow end from ten until noon, then the swim team takes every lane once school lets out and keeps it until the evening classes arrive. After that it's quiet."),
    "fresh-subjects": ("A volunteer opens the shed at eight. The first borrower usually shows up by quarter past. An inventory sheet hangs by the door. The drill set goes out most weekends.",
                       "A volunteer opens the shed at eight. Borrowers start arriving soon after. Most weekends the drill set goes out first."),
    "table-restated": ("| branch | loans |\n| --- | --- |\n| east | 4,210 |\n\nThe east branch lent 4,210 books.", "| branch | loans |\n| --- | --- |\n| east | 4,210 |\n\nThe east branch lent the most books."),
    "thematic-breaks": ("Bread.\n\n---\n\nCake.\n\n---\n\nPie.\n\n---\n\nTarts.", "Bread.\n\n---\n\nCake."),
    "rule-of-three": ("Bring a towel, goggles, and a lock. Lanes are slow, medium, and fast. Staff check bags, coats, and umbrellas.", "Bring a towel and goggles. Lanes are marked by speed."),
    "semicolon-chain": ("Refunds take a week; exchanges are same day. Gift cards never expire; store credit does.", "Refunds take a week. Exchanges happen the same day."),
    "name-drift": ("Staff edit pickupWindow in the admin page. The locker app reads PickupWindow at startup.", "Staff edit pickupWindow in the admin page. The locker app reads it at startup."),
    "appositive-heading:caption": ("**Lockers, by neighborhood**", "**Lockers by neighborhood**"),
    "symmetric-bullets": ("- **When:** Saturday mornings.\n- **Where:** the church hall.\n- **Cost:** free for members.", "- Saturday mornings\n- in the church hall, which has parking out back\n- free for members"),
    # --- families -------------------------------------------------------------
    "word:leverage": ("We leverage the waitlist to fill cancellations.", "The clinic fills cancellations from its waitlist."),
    "word:robust": ("The kiosk needs a robust paper feed.", "The kiosk needs a paper feed that doesn't jam."),
    "phrase:it's important to note": ("Families, it's important to note, must bring ID.", "Families must bring ID."),
    "phrase:serves as": ("The front desk serves as lost and found.", "Lost and found is at the front desk."),
    "phrase:the path forward": ("For the pool, the path forward is a bond vote.", "The pool needs a bond vote."),
    "overused:simply": ("You simply scan the card, simply pick a slot, and simply pay.", "Scan the card, pick a slot, and pay."),
    "overused:canonical": ("The canonical timetable hangs in the office; the canonical copy is the printed one.", "The printed timetable in the office is the canonical one."),
    "llm-adverb:notably": ("The fair was notably busy, notably at the pie stand.", "The fair was busy, mostly at the pie stand."),
    # contrast frames from slop-score (contrast.py); the clean side of each
    # is the plain positive claim
    "contrast:not-but": ("Parents were not upset about the fee, but about the time.", "Parents were upset about the time."),
    "contrast:not-dash": ("The pantry doesn't only hand out food — it runs a clothing swap too.", "The pantry also runs a clothing swap."),
    "contrast:pron-be-not-sep-be": ("That is not a typo. That is the new fee.", "The new fee is correct."),
    "contrast:np-be-not-sep-they-be": ("Late buses were not the problem. They were a symptom.", "Late buses were a symptom."),
    "contrast:no-longer-sep": ("Cash is no longer accepted at the pool. It was too slow.", "The pool takes cards only."),
    "contrast:not-just-sep": ("They're not just volunteers. They're the whole staff.", "The volunteers are the whole staff."),
    "contrast:not-period-sameverb": ("The club didn't cancel practice. It canceled the match instead.", "The club canceled the match and kept practice."),
    "contrast:simple-be-not-it-be": ("The gym isn't closed on Sunday. It's open until two.", "The gym is open until two on Sunday."),
    "contrast:embedded-not-just-sep": ("For most parents it's not just a bake sale. It's the year's biggest fundraiser.", "For most parents the bake sale is the year's biggest fundraiser."),
    "contrast:dialogue-not-just": ('"It\'s not just a raffle." The organizer added a sign. "It\'s the roof fund."', '"It\'s the roof fund," the organizer said.'),
}


def doc_examples():
    """rules that need a whole document."""
    plain = filler(320)
    authorless = " ".join(s.replace("I sat", "A clerk sat").replace("we'll", "the board will") for s in [plain])
    no_hedge = plain.replace("probably ", "").replace("If vendors ask", "When vendors ask")
    flat = " ".join(f"Bus {n} leaves the north depot on the hour." for n in range(1, 17))
    varied = filler(200)
    dashes = "Refunds go back to the card - cash refunds need a manager; nobody likes that. " + filler(60)
    colon = ("Stall rules are posted by day: bread on monday, pastry on tuesday. Fees: cash only. "
             "Parking: behind the hall. Dogs: on a lead. Music: acoustic only. " + filler(40))
    contrast = " ".join(["Tickets sell at the door, not online.", "Kids ride free instead of half price.",
                         "We chose paper maps rather than an app.", "The fee covers cleanup as opposed to security."])
    part = "The stalls filled by nine, leaving the late vendors on the grass. The draw ran twice, doubling the complaints. " + filler(300)
    return {
        "authorless": (authorless, plain),
        "no-hedges": (no_hedge, plain),
        "flat-rhythm": (flat, varied),
        "dash-budget": (dashes, filler(60)),
        "colon-splice": (colon, filler(80)),
        "contrast-habit": (contrast, "Tickets sell at the door. " + filler(40)),
        "participial-rate": (part, filler(300)),
    }


# rules whose example lives in a fixture file instead (path relative to
# skill/scripts/testdata)
FILE_EXAMPLES = {
    "even-section-weight": ("even-sections-dirty.md", "even-sections-clean.md"),
}

# emitted only as a side effect of participial-rate firing; covered there
DERIVED = {"participial-instance"}


# --pr rules (deslop/pr.py): examples run with Detector(text, pr=True). the
# clean one must fire nothing at all in that mode.
PR_CLEAN = (
    "## Summary\n\n"
    "Saturday stalls now come from the vendor list the office keeps, so the lottery page shows who holds each corner.\n\n"
    "## Testing\n\n"
    "I ran the draw on last month's list and every vendor got the stall the office expected.\n"
)


def pr_examples() -> dict:
    long_pr = "## Summary\n\n" + filler(330) + "\n"
    return {
        "pr-length": (long_pr, PR_CLEAN),
        "pr-history": ("## Summary\n\nInitially the draw ran by hand.\n", PR_CLEAN),
        "pr-number-dense": ("## Summary\n\nStalls 12, 14, 19 and 22 moved; 40 of 44 vendors kept a corner.\n", PR_CLEAN),
        "pr-results-table": ("## Testing\n\n| Week | Stalls |\n|---|---|\n| First | Full |\n", PR_CLEAN),
        "pr-untracked-open-item": ("## Still open\n\n- Moving the draw to Wednesday.\n", PR_CLEAN),
    }
