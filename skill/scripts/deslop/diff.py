"""what a revision added: findings in the revised text that weren't in the
original, plus the fact lock.

a finding counts as the same one in both versions when its rule and its
matched text agree ("word:robust" on "robust" stays the same finding even
if the sentence around it was rewritten). findings with no matched text,
which are block- or document-level ("monotone-rhythm", "flat-rhythm"),
match on the rule alone. if the revision has more of a key than the
original did, the extra ones are added; fewer means resolved.
"""
import collections
import json
import os
import sys

from .detect import Detector

# fact_lock.py lives one directory up, next to check_tells.sh
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import fact_lock  # noqa: E402


def _key(f):
    return (f.rule, " ".join(f.text.lower().split()))


def compare(original: str, revised: str, config: dict | None = None) -> dict:
    before = Detector(original, config).run()
    after = Detector(revised, config).run()
    nb = collections.Counter(_key(f) for f in before.findings)
    seen = collections.Counter()
    added = []
    for f in after.findings:
        k = _key(f)
        seen[k] += 1
        if seen[k] > nb[k]:
            added.append(f)
    na = collections.Counter(_key(f) for f in after.findings)
    resolved = sum(max(0, n - na[k]) for k, n in nb.items())
    facts = fact_lock.check(original, revised)
    dropped = [(k.replace("missing_", "")[:-1], v) for k in ("missing_numbers", "missing_dates", "missing_urls", "missing_quotes") for v in facts[k]]
    return {
        "added": added,
        "resolved": resolved,
        "score_before": before.metrics["score"],
        "score_after": after.metrics["score"],
        "dropped_facts": dropped,
        "words_before": facts["words_before"],
        "words_after": facts["words_after"],
    }


def report(r: dict, as_json: bool = False) -> str:
    growth = (r["words_after"] - r["words_before"]) / r["words_before"] if r["words_before"] else 0.0
    if as_json:
        out = dict(r, added=[vars(f) for f in r["added"]], growth=round(growth, 3))
        return json.dumps(out, indent=2) + "\n"
    lines = []
    for f in r["added"]:
        lines.append(f"added line {f.line}: {f.label} -> {f.fix}")
    for kind, v in r["dropped_facts"]:
        lines.append(f"dropped {kind}: {v!r}")
    if growth > 0.15:
        lines.append(f"grew {growth:+.0%}: a fix should compress, not pad")
    lines.append(f"{len(r['added'])} added, {r['resolved']} resolved, score {r['score_before']} -> {r['score_after']}, "
                 f"{len(r['dropped_facts'])} facts dropped")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if len(paths) != 2:
        print("usage: python3 -m deslop --diff [--json] <original> <revised>", file=sys.stderr)
        return 255
    try:
        a, b = (open(p, encoding="utf-8", errors="replace").read() for p in paths)
    except OSError as e:
        print(f"deslop --diff: {e}", file=sys.stderr)
        return 255
    from .project import find_config, load_config
    r = compare(a, b, load_config(find_config(paths[1])))
    sys.stdout.write(report(r, as_json))
    return min(255, len(r["added"]) + len(r["dropped_facts"]))
