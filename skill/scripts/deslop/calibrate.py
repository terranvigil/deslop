"""print metric distributions over a set of files, to set thresholds.

usage: python3 -m deslop.calibrate <label> <files...> [-- <label> <files...>]
reports, per label, the median and 90th and 95th percentiles of each metric
over files with at least 300 words. single-threaded, one pass per file.
"""

import sys

from .text import Doc
from . import metrics as M

KEYS = ["mattr", "paragraph_cv", "participial_initial_per_1k", "participial_post_comma_per_1k",
        "participial_per_1k", "nominalizations_per_1k", "bullet_min_cv", "section_weight_cv",
        "clipped_opener_share"]


def pct(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    i = min(len(xs) - 1, int(round((len(xs) - 1) * p)))
    return xs[i]


def main(argv):
    groups, cur = [], None
    for a in argv:
        if a == "--":
            cur = None
        elif cur is None:
            cur = (a, [])
            groups.append(cur)
        else:
            cur[1].append(a)
    print(f"{'group':18s} {'files':>5s} " + " ".join(f"{k[:22]:>24s}" for k in KEYS))
    for label, files in groups:
        rows = []
        for f in files:
            src = open(f, encoding="utf-8", errors="replace").read()
            d = Doc(src)
            if d.words() < 300:
                continue
            rows.append(M.compute(d.prose_blocks, d.prose))
        line = f"{label:18s} {len(rows):5d} "
        for k in KEYS:
            vals = [r[k] for r in rows]
            line += f" {str(pct(vals, .5)):>7s}/{str(pct(vals, .9)):>7s}/{str(pct(vals, .95)):>7s}"
        print(line)
    print("columns: median / p90 / p95")


if __name__ == "__main__":
    main(sys.argv[1:])
