"""diff_comments.py pulls added comments, and only comments, out of a diff."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from diff_comments import collect, comment_text  # noqa: E402

DIFF = """\
diff --git a/src/draw.cpp b/src/draw.cpp
+++ b/src/draw.cpp
@@ -10,0 +11,4 @@
+// Stalls go to the vendor list the office keeps.
+// The lottery page reads it back.
+int stalls = 44; // one per corner
+auto url = "https://example.com/a//b";
diff --git a/tools/run.py b/tools/run.py
+++ b/tools/run.py
@@ -1,0 +2,2 @@
+# Wednesday draws start next month.
+x = "#not a comment"
"""


class DiffComments(unittest.TestCase):
    def test_runs(self):
        runs = collect(DIFF)
        self.assertEqual(runs[0], ("src/draw.cpp", 11, ["Stalls go to the vendor list the office keeps.",
                                                        "The lottery page reads it back."]))
        self.assertEqual(runs[1], ("src/draw.cpp", 13, ["one per corner"]))
        self.assertEqual(runs[2], ("tools/run.py", 2, ["Wednesday draws start next month."]))
        self.assertEqual(len(runs), 3)

    def test_code_is_not_a_comment(self):
        self.assertIsNone(comment_text("a.cpp", 'auto u = "http://x//y";'))
        self.assertIsNone(comment_text("a.py", 'x = "#tag"'))
        self.assertIsNone(comment_text("a.sh", "#!/usr/bin/env bash"))
        self.assertEqual(comment_text("a.h", " * Doc comment line."), "Doc comment line.")


if __name__ == "__main__":
    unittest.main()
