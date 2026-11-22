"""Review-only fixtures exercise problems a pattern matcher should not guess.

The metadata fixture deliberately produces no findings.  A cold fixer still
has to rewrite it by applying the semantic sweep in SKILL.md; the manual
acceptance criteria live in evals/EXPECTATIONS.md.  If a future rule flags
this text, change this test deliberately and give that rule a measured
dirty/clean pair rather than silently turning a judgment case into a broad
syntax ban.
"""
import os
import sys
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, SCRIPTS)

from deslop.detect import Detector  # noqa: E402


FIXTURE = os.path.join(SCRIPTS, "..", "evals", "fixtures", "metadata-prose.md")


class ReviewOnlyFixture(unittest.TestCase):
    def test_metadata_prose_is_scanner_clean(self):
        with open(FIXTURE, encoding="utf-8") as fh:
            findings = Detector(fh.read()).run().findings
        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
