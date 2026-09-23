"""check_tells.sh --diff: a padded revision shows what it added, a plain
one shows nothing."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from deslop.diff import compare  # noqa: E402

ORIGINAL = "The parcel-locker firmware update is a game-changing release for couriers. Failed door openings went from 312 a week to 40.\n"
PADDED = "The parcel-locker firmware update helps couriers in a number of ways, so door openings may fail somewhat less. Failed openings are down to 40 a week.\n"
PLAIN = "The parcel-locker firmware update helps couriers. Failed door openings went from 312 a week to 40.\n"


class Diff(unittest.TestCase):
    def test_padded_revision_reports_what_it_added(self):
        r = compare(ORIGINAL, PADDED)
        self.assertIn("vague-quantity", {f.rule for f in r["added"]})
        self.assertIn(("number", "312"), r["dropped_facts"])

    def test_plain_revision_adds_nothing(self):
        r = compare(ORIGINAL, PLAIN)
        self.assertEqual(r["added"], [])
        self.assertEqual(r["dropped_facts"], [])
        self.assertGreater(r["resolved"], 0)

    def test_unchanged_text_adds_nothing(self):
        r = compare(ORIGINAL, ORIGINAL)
        self.assertEqual((r["added"], r["resolved"]), ([], 0))


if __name__ == "__main__":
    unittest.main()
