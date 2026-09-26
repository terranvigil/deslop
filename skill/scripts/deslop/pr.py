"""checks for pull request descriptions, run with --pr.

a PR description is read by a reviewer deciding what to look at: it says
where the change stands, not how it got there, and it fits on a screen.
these rules only run in --pr mode, since history words and figures are
fine in a design doc or a postmortem.
"""
import re

# a description past this many words stops being read in full
WORD_BUDGET = 300
# numbers per 100 words; a description that reads like a results table
NUMBER_DENSITY = 5.0

HISTORY = re.compile(
    r"\b(?:first attempt|initially|originally|it turned out|turned out to|we (?:then|later|found that)|"
    r"after (?:the )?(?:first |second |last )?review(?: round)?|review round|bisect(?:ed|ing)?|"
    r"previous (?:attempt|approach|version|iteration)|earlier (?:attempt|approach|version)|"
    r"(?:first|second|third) (?:pass|round|iteration)|went back to)\b",
    re.I,
)
# sections that list work still to do, as opposed to limitations of the change
OPEN_HEADING = re.compile(r"\b(?:open(?: items| questions)?|still open|to ?do|follow[- ]?ups?|next steps|known (?:gaps|issues)|remaining)\b", re.I)
TICKET = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b|#\d+\b|https?://\S+")
NUMBER = re.compile(r"(?<![\w.])\d[\d,.]*%?")

RULES = ("pr-length", "pr-history", "pr-number-dense", "pr-results-table", "pr-untracked-open-item")


def run(det) -> None:
    d = det.doc
    words = d.words()
    if words > WORD_BUDGET:
        det.add("pr-length", "discourse", 2,
                f"PR description is {words} words; a reviewer reads about {WORD_BUDGET}",
                "say where the change stands: what it does, how it was tested, what a reviewer must know; "
                "cut the path that led here", 0, 0, "")
    for b in d.prose_blocks:
        for m in HISTORY.finditer(b.text):
            det.add("pr-history", "discourse", 2, f"development history in a PR ('{m.group(0)}')",
                    "state the current behaviour; the history lives in the commits", b.start + m.start(),
                    b.start + m.end(), m.group(0))
    numbers = len(NUMBER.findall(TICKET.sub(" ", d.cleaned)))
    if words and numbers * 100 / words > NUMBER_DENSITY:
        det.add("pr-number-dense", "discourse", 2,
                f"PR description carries {numbers} numbers in {words} words",
                "keep the one or two figures a reviewer acts on (tests passing, the headline result); "
                "link the rest", 0, 0, "")
    for b in d.blocks:
        if b.kind == "table":
            det.add("pr-results-table", "structural", 1, "results table in a PR description",
                    "give the headline result in a sentence and link the full numbers", b.start, b.end, "")
            break
    in_open = False
    for b in d.blocks:
        if b.kind == "heading":
            in_open = bool(OPEN_HEADING.search(b.text))
            continue
        if in_open and b.kind == "item" and not TICKET.search(b.text):
            det.add("pr-untracked-open-item", "discourse", 2, "open item with no ticket",
                    "resolve it in this PR, drop it if it's a process step, or file it and link the id",
                    b.start, b.end, b.text[:60])
