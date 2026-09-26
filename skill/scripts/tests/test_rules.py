"""per-rule dirty/clean checks.

    make test        # from the repo root

fails if a rule has no example, if its dirty example stops firing it, or
if its clean example fires anything at all. clean text should be clean
text, not merely text that dodges one rule. mutation breaks each pattern
rule's regex in turn and checks its own dirty example notices, so a test
that passes without exercising its rule gets caught.
"""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.realpath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HERE)

from deslop import contrast as C  # noqa: E402
from deslop import rules as R  # noqa: E402
from deslop.detect import Detector  # noqa: E402
from rule_examples import DERIVED, EXAMPLES, FILE_EXAMPLES, doc_examples, pr_examples  # noqa: E402
from deslop import pr as PR  # noqa: E402

TESTDATA = os.path.join(SCRIPTS, "testdata")


def registry() -> set[str]:
    """every fixed rule id the detector can emit, read from the rule table
    and from detect.py's own add() calls, so a new rule can't dodge the
    check by not being listed anywhere."""
    ids = {p[0] for p in R.PATTERNS} | {"quantifier-tail"}
    src = open(os.path.join(SCRIPTS, "deslop", "detect.py"), encoding="utf-8").read()
    ids |= set(re.findall(r'self\.add\("([a-z0-9-]+)"', src))
    ids |= {"contrast:" + name for name, _ in C.COMPILED}
    return ids


def all_examples() -> dict:
    ex = dict(EXAMPLES)
    ex.update(doc_examples())
    for rule, (dirty, clean) in FILE_EXAMPLES.items():
        read = lambda f: open(os.path.join(TESTDATA, f), encoding="utf-8").read()  # noqa: E731
        ex[rule] = (read(dirty), read(clean))
    return ex


def fired(text: str) -> set[str]:
    return {f.rule for f in Detector(text).run().findings}


class PrRuleExamples(unittest.TestCase):
    """the --pr rules, run in PR mode."""

    def test_every_pr_rule_has_an_example(self):
        src = open(os.path.join(SCRIPTS, "deslop", "pr.py"), encoding="utf-8").read()
        emitted = set(re.findall(r'det\.add\("([a-z0-9-]+)"', src))
        self.assertEqual(emitted, set(PR.RULES), "pr.RULES and pr.py's add() calls disagree")
        self.assertEqual(sorted(set(PR.RULES) - set(pr_examples())), [], "--pr rules with no example")

    def test_dirty_fires(self):
        for rule, (dirty, _) in pr_examples().items():
            with self.subTest(rule=rule):
                self.assertIn(rule, {f.rule for f in Detector(dirty, pr=True).run().findings})

    def test_clean_quiet(self):
        for rule, (_, clean) in pr_examples().items():
            with self.subTest(rule=rule):
                self.assertEqual(sorted({f.rule for f in Detector(clean, pr=True).run().findings}), [])

    def test_off_without_the_flag(self):
        for rule, (dirty, _) in pr_examples().items():
            with self.subTest(rule=rule):
                self.assertNotIn(rule, fired(dirty))


class RuleExamples(unittest.TestCase):
    def test_every_rule_has_an_example(self):
        have = {k.split(":caption")[0] for k in all_examples()}
        missing = sorted(registry() - have - DERIVED)
        self.assertEqual(missing, [], "rules with no dirty/clean example in tests/rule_examples.py")

    def test_every_rule_has_a_fix_scope(self):
        # fix_scope defaults to "sentence"; a rule scored per paragraph or
        # document that forgets to register gets a wrong routing hint. the
        # check: anything emitted without a span is not sentence-scoped.
        for rule, (dirty, _) in all_examples().items():
            rule = rule.split(":caption")[0]
            for f in Detector(dirty).run().findings:
                if f.rule == rule and f.end <= f.start:
                    self.assertNotEqual(f.scope, "sentence", f"{rule} has no span but is sentence-scoped")

    def test_dirty_fires(self):
        for rule, (dirty, _) in all_examples().items():
            rule = rule.split(":caption")[0]
            with self.subTest(rule=rule):
                self.assertIn(rule, fired(dirty), f"dirty example doesn't trip {rule}")

    def test_clean_quiet(self):
        for rule, (_, clean) in all_examples().items():
            rule = rule.split(":caption")[0]
            with self.subTest(rule=rule):
                self.assertEqual(sorted(fired(clean)), [], f"clean example for {rule} fires something")

    def test_mutation(self):
        # Detector compiles R.PATTERNS at construction, so swapping the
        # table in place is enough. "(?!)" never matches.
        ex = all_examples()
        original = list(R.PATTERNS)
        try:
            for p in original:
                rid = p[0]
                if rid not in ex:
                    continue
                R.PATTERNS[:] = [(q[0], *q[1:5], "(?!)", *q[6:]) if q[0] == rid else q for q in original]
                with self.subTest(rule=rid):
                    self.assertNotIn(rid, fired(ex[rid][0]), f"{rid} still fires with its regex broken")
        finally:
            R.PATTERNS[:] = original


if __name__ == "__main__":
    unittest.main()
