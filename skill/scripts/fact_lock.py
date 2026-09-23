#!/usr/bin/env python3
"""fact-lock check: a revision may cut, reorder, or rephrase anything, but
the facts survive. Coarse and document-wide on purpose: a number, date,
URL, or quote is allowed to move to a different sentence (even a table or
a footnote) as long as it's still in the document somewhere. Missing entirely is the violation this catches.

    scripts/fact_lock.py <original> <revised>

Exit code: number of distinct dropped facts (numbers + dates + URLs +
quotes), capped at 255. 0 means the revision kept every fact. Negation
count is reported, not gated: rephrasing shifts negation markers around
too often for a raw count to be a reliable signal on its own.
"""
import re
import sys

FIGURE = re.compile(r"\b[0-9]+(?:[,.][0-9]+)*")
ISO_DATE = re.compile(r"\b[0-9]{4}-[0-9]{2}-[0-9]{2}\b")
URL = re.compile(r"\bhttps?://[^\s)\]\"'>]+")
MD_LINK_TARGET = re.compile(r"\]\(([^)]+)\)")
QUOTED = re.compile(r"[\"“]([^\"”\n]{3,200})[\"”]")
NEGATION = re.compile(r"\b(not|never|no|none|nobody|nothing|neither|nor|without|isn.t|aren.t|wasn.t|weren.t|doesn.t|don.t|didn.t|won.t|wouldn.t|can.t|cannot|couldn.t|shouldn.t)\b", re.I)


def _strip_trailing_punct(url: str) -> str:
    return url.rstrip(".,;:!?)]'\"")


def extract(text: str) -> dict:
    numbers = set(m.group(0) for m in FIGURE.finditer(text))
    dates = set(m.group(0) for m in ISO_DATE.finditer(text))
    urls = {_strip_trailing_punct(m.group(0)) for m in URL.finditer(text)}
    urls |= {_strip_trailing_punct(m.group(1)) for m in MD_LINK_TARGET.finditer(text)}
    quotes = set(m.group(1).strip() for m in QUOTED.finditer(text))
    negations = len(NEGATION.findall(text))
    return {"numbers": numbers, "dates": dates, "urls": urls, "quotes": quotes, "negations": negations}


def check(original: str, revised: str) -> dict:
    a, b = extract(original), extract(revised)
    return {
        "missing_numbers": sorted(a["numbers"] - b["numbers"]),
        "missing_dates": sorted(a["dates"] - b["dates"]),
        "missing_urls": sorted(a["urls"] - b["urls"]),
        "missing_quotes": sorted(a["quotes"] - b["quotes"]),
        "negations_before": a["negations"],
        "negations_after": b["negations"],
        "words_before": len(original.split()),
        "words_after": len(revised.split()),
    }


def report(r: dict) -> int:
    dropped = 0
    for key, label in (("missing_numbers", "number"), ("missing_dates", "date"),
                        ("missing_urls", "URL"), ("missing_quotes", "quote")):
        for v in r[key]:
            print(f"DROPPED {label}: {v!r}")
            dropped += 1
    growth = (r["words_after"] - r["words_before"]) / r["words_before"] if r["words_before"] else 0
    print(f"words: {r['words_before']} -> {r['words_after']} ({growth:+.0%})")
    if growth > 0.15:
        print(f"LENGTH: grew more than 15% ({growth:+.0%}) — a fixer should compress slop, not pad it")
    print(f"negations: {r['negations_before']} -> {r['negations_after']} (reported, not gated)")
    if dropped == 0:
        print("fact lock: PASS")
    else:
        print(f"fact lock: FAIL ({dropped} dropped)")
    return min(255, dropped)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: fact_lock.py <original> <revised>", file=sys.stderr)
        return 2
    original = open(argv[0], encoding="utf-8", errors="replace").read()
    revised = open(argv[1], encoding="utf-8", errors="replace").read()
    return report(check(original, revised))


if __name__ == "__main__":
    raise SystemExit(main())
