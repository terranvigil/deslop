#!/usr/bin/env python3
"""Append one (flagged span, accepted rewrite, score delta) triple to
logs/triples.jsonl. This is the training set if a rewriter model is ever
worth building; logging it now costs nothing and can't be reconstructed
later.

    scripts/log_triple.py --rule <id> --layer <layer> \\
        --original "<flagged sentence>" --rewrite "<rewritten sentence>" \\
        [--score-before N] [--score-after N]

score-before/after are the whole document's detector score (--json
metrics.score) right before and after this one edit, if you have them;
omit them for a quick log. Does nothing unless DESLOP_LOG_TRIPLES=1.
"""
import argparse
import datetime
import json
import os
import sys

# repo root, three levels up from skill/scripts/log_triple.py. realpath, not
# abspath: when invoked through the ~/.claude/skills/humanize-writing symlink,
# abspath would stay inside the symlinked path and land one level too shallow.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
LOG_PATH = os.path.join(ROOT, "logs", "triples.jsonl")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rule", required=True, help="the finding's rule id, e.g. trailing-participial")
    p.add_argument("--layer", required=True, choices=["lexical", "structural", "grammatical", "discourse"])
    p.add_argument("--original", required=True, help="the flagged span, verbatim")
    p.add_argument("--rewrite", required=True, help="the accepted rewrite, verbatim")
    p.add_argument("--score-before", type=float, default=None)
    p.add_argument("--score-after", type=float, default=None)
    args = p.parse_args(argv)

    # the log holds the user's own text, so it only writes when they opted in
    if os.environ.get("DESLOP_LOG_TRIPLES") != "1":
        print("not logged: set DESLOP_LOG_TRIPLES=1 to enable", file=sys.stderr)
        return 0

    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "rule": args.rule,
        "layer": args.layer,
        "original": args.original,
        "rewrite": args.rewrite,
        "score_before": args.score_before,
        "score_after": args.score_after,
        "delta": (args.score_before - args.score_after) if args.score_before is not None and args.score_after is not None else None,
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(f"logged to {os.path.relpath(LOG_PATH, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
