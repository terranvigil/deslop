#!/usr/bin/env python3
"""eval gate command.

    scripts/gate.sh                        # run every gate, print pass/fail
    scripts/gate.sh --write-human-baseline  # regenerate the recorded human
                                             # corpus rates; run this only
                                             # after a deliberate detector
                                             # change, then commit the diff

Gate 1 needs voice/human-baseline/, a local corpus of pre-LLM human prose
that isn't checked in. If it isn't present the gate is skipped, not failed,
so this still runs on a checkout that doesn't have it.

Gate 3's floors are a starting point, not calibrated.
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skill", "scripts"))

from deslop.detect import Detector  # noqa: E402

HUMAN_DIR = os.path.join(ROOT, "voice", "human-baseline")
HUMAN_BASELINE_PATH = os.path.join(ROOT, "skill", "evals", "baseline", "human-baseline.json")

# excluded from the human false-positive gate only: a published web page uses
# curly quotes and dashes by convention, and this corpus is number-heavy
# technical writing.
TYPOGRAPHY_RULES = {"em-dash", "en-dash", "curly-quote"}
NUMBER_RULES = {
    "hedged-precision", "over-precise-pct", "number-dense-sentence",
    "number-dense-paragraph", "table-restated", "tilde",
}
EXCLUDE = TYPOGRAPHY_RULES | NUMBER_RULES

# set just above the measured human rate. most of what fires on human
# prose is the banned word list catching pre-LLM tech jargon (comprehensive,
# robust, leverage). skill/evals/baseline/human-baseline.json has the
# current rates. this ceiling is informational only; the hard gate is
# regression against the recorded rate.
CEILING_PER_1K = {"blog": 9.0, "paper": 10.0}

# gate 3: fixtures must stay above this floor, about 80% of an earlier
# recorded count. loose on purpose: this catches a rule table
# gutted by accident, not day-to-day drift, which scripts/baseline.sh --check
# already catches exactly.
FIXTURE_FLOORS = {
    "skill/scripts/testdata/dirty.md": 86,
    "skill/evals/fixtures/design-doc.md": 27,
    "skill/evals/fixtures/pr-description.md": 16,
    "skill/evals/fixtures/slack-post.md": 17,
}
CLEAN_FIXTURE = "skill/scripts/testdata/clean.md"


def scan(path: str):
    text = open(path, encoding="utf-8", errors="replace").read()
    det = Detector(text).run()
    return det.metrics["words"], det.findings


def human_baseline_rates():
    # plain-text pre-LLM technical writing, one document per .txt file,
    # already stripped of page chrome
    groups = {name: sorted(glob.glob(os.path.join(HUMAN_DIR, name, "*.txt"))) for name in ("blog", "paper")}
    out = {}
    for name, files in groups.items():
        words = findings = 0
        for f in files:
            w, fs = scan(f)
            words += w
            findings += len([x for x in fs if x.rule not in EXCLUDE])
        out[name] = {
            "files": len(files),
            "words": words,
            "findings": findings,
            "rate_per_1k": round(findings * 1000 / words, 2) if words else 0.0,
        }
    return out


def write_human_baseline():
    rates = human_baseline_rates()
    os.makedirs(os.path.dirname(HUMAN_BASELINE_PATH), exist_ok=True)
    with open(HUMAN_BASELINE_PATH, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "note": "false-positive rate on voice/human-baseline/, typography "
                "and number rules excluded. Regenerate "
                "with `scripts/gate.sh --write-human-baseline` only after a "
                "deliberate detector change, and commit the diff.",
                "ceiling_per_1k": CEILING_PER_1K,
                "rates": rates,
            },
            fh,
            indent=2,
        )
        fh.write("\n")
    print(f"wrote {os.path.relpath(HUMAN_BASELINE_PATH, ROOT)}")
    for name, r in rates.items():
        print(f"  {name:6s} {r['rate_per_1k']:5.2f}/1k  ({r['findings']} findings, {r['words']} words, {r['files']} files)")


# ------------------------------------------------------------------- gates
def gate_1_human_baseline():
    print("gate 1: human baseline false-positive ceiling")
    if not os.path.isdir(HUMAN_DIR):
        print("  SKIP: voice/human-baseline/ not present (local corpus, not checked in)")
        return True
    if not os.path.exists(HUMAN_BASELINE_PATH):
        print(f"  FAIL: no recorded baseline at {os.path.relpath(HUMAN_BASELINE_PATH, ROOT)}")
        print("        run `scripts/gate.sh --write-human-baseline` once, then commit it")
        return False
    recorded = json.load(open(HUMAN_BASELINE_PATH, encoding="utf-8"))["rates"]
    current = human_baseline_rates()
    ok = True
    for name, cur in current.items():
        rec = recorded.get(name, {}).get("rate_per_1k")
        ceiling = CEILING_PER_1K.get(name)
        flag = ""
        if rec is not None and cur["rate_per_1k"] > rec + 0.05:
            ok = False
            flag = f"  REGRESSION (recorded {rec}/1k)"
        elif ceiling and cur["rate_per_1k"] > ceiling:
            flag = f"  above suggested ceiling {ceiling}/1k, not yet a hard gate"
        print(f"  {name:6s} {cur['rate_per_1k']:5.2f}/1k  ({cur['findings']} findings, {cur['words']} words){flag}")
    return ok


def gate_2_baseline_check():
    print("gate 2: scripts/baseline.sh --check")
    p = subprocess.run(["bash", os.path.join(ROOT, "scripts", "baseline.sh"), "--check"],
                        cwd=ROOT, capture_output=True, text=True)
    for line in p.stdout.splitlines():
        print("  " + line)
    if p.returncode != 0:
        for line in p.stderr.splitlines():
            print("  " + line)
    return p.returncode == 0


def gate_3_fixture_floor():
    print("gate 3: dirty fixtures above floor, clean.md at 0")
    ok = True
    for rel, floor in FIXTURE_FLOORS.items():
        _, findings = scan(os.path.join(ROOT, rel))
        n = len(findings)
        status = "ok" if n >= floor else "FAIL"
        if n < floor:
            ok = False
        print(f"  {rel:45s} {n:4d} findings (floor {floor})  {status}")
    _, findings = scan(os.path.join(ROOT, CLEAN_FIXTURE))
    n = len(findings)
    status = "ok" if n == 0 else "FAIL"
    if n != 0:
        ok = False
    print(f"  {CLEAN_FIXTURE:45s} {n:4d} findings (must be 0)  {status}")
    return ok


def gate_4_fact_lock_and_length():
    print("gate 4: fact-lock and calibration-pair smoke tests")
    print("  the fixer itself is LLM-driven, not something this deterministic")
    print("  gate can run; this checks the deterministic tooling stays correct")
    import fact_lock  # noqa: E402 (scripts/ dir, same as this file)
    source = os.path.join(ROOT, "skill", "scripts", "testdata", "fact-lock-source.md")
    good = os.path.join(ROOT, "skill", "scripts", "testdata", "fact-lock-good.md")
    bad = os.path.join(ROOT, "skill", "scripts", "testdata", "fact-lock-bad.md")
    ok = True
    for label, revised, want_pass in (("good", good, True), ("bad", bad, False)):
        r = fact_lock.check(open(source, encoding="utf-8").read(), open(revised, encoding="utf-8").read())
        dropped = sum(len(r[k]) for k in ("missing_numbers", "missing_dates", "missing_urls", "missing_quotes"))
        passed = dropped == 0
        status = "ok" if passed == want_pass else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"  fact-lock {label:5s} fixture: {dropped} dropped, expected {'pass' if want_pass else 'fail'}  {status}")

    for label, path, want_fire in (
        ("dirty", os.path.join(ROOT, "skill", "scripts", "testdata", "even-sections-dirty.md"), True),
        ("clean", os.path.join(ROOT, "skill", "scripts", "testdata", "even-sections-clean.md"), False),
    ):
        _, findings = scan(path)
        fired = any(f.rule == "even-section-weight" for f in findings)
        status = "ok" if fired == want_fire else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"  even-section-weight {label:5s} fixture: fired={fired}, expected {want_fire}  {status}")
    return ok


def gate_5_rule_examples():
    """every rule's dirty example fires it, its clean example doesn't
    (the tests are also `make test`)."""
    print("gate 5: per-rule dirty/clean examples and --diff (make test)")
    import subprocess
    tests = os.path.join(ROOT, "skill", "scripts", "tests")
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", tests], capture_output=True, text=True)
    tail = (r.stderr or r.stdout).strip().splitlines()
    if r.returncode == 0:
        print(f"  {tail[-3] if len(tail) >= 3 else ''} ok")
        return True
    for line in tail:
        if line.startswith(("AssertionError", "FAIL:")):
            print("  " + line)
    print("  FAIL (run `make test` for details)")
    return False


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--write-human-baseline"]:
        write_human_baseline()
        return 0
    if argv:
        print("usage: gate.sh [--write-human-baseline]", file=sys.stderr)
        return 2

    results = [
        gate_1_human_baseline(),
        gate_2_baseline_check(),
        gate_3_fixture_floor(),
        gate_4_fact_lock_and_length(),
        gate_5_rule_examples(),
    ]
    print()
    print("PASS" if all(results) else "FAIL")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
