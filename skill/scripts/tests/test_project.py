""".deslop.json and check_tells.sh --changed. the --changed tests build a
throwaway git repo and run the real wrapper, so they cover path handling and exit codes too."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, SCRIPTS)
from deslop import project as P  # noqa: E402
from deslop.detect import Detector  # noqa: E402

CHECKER = os.path.join(SCRIPTS, "check_tells.sh")
TESTDATA = os.path.join(SCRIPTS, "testdata")
ORIGINAL = "Library holds expire after seven days unless the patron renews them.\n"
PADDED = "Library holds expire after seven days in most of the cases unless the patron renews them.\n"
DIRTY = os.path.join(TESTDATA, "dirty.md")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def run(*args, cwd):
    return subprocess.run([CHECKER, *args], cwd=cwd, capture_output=True, text=True)


class Config(unittest.TestCase):
    def test_allow_and_disable(self):
        path = os.path.join(TESTDATA, "config", "doc.md")
        cfg = P.load_config(P.find_config(path))
        rules = {f.rule for f in Detector(read(path), cfg).run().findings}
        self.assertEqual(rules, {"word:seamlessly"})  # gates allowed, comma-and-clause disabled
        self.assertIn("word:gates", {f.rule for f in Detector(read(path)).run().findings})

    def test_cli_reads_config_from_relative_path(self):
        r = run("--json", "config/doc.md", cwd=TESTDATA)
        self.assertEqual({f["rule"] for f in json.loads(r.stdout)["findings"]}, {"word:seamlessly"})

    def test_family_and_exact_ids(self):
        cfg = {"allow": ["Gates"], "disable": ["contrast", "em-dash"]}
        self.assertTrue(P.suppressed("word:gates", cfg))
        self.assertTrue(P.suppressed("overused:gates", cfg))
        self.assertTrue(P.suppressed("contrast:not-but", cfg))
        self.assertTrue(P.suppressed("em-dash", cfg))
        self.assertFalse(P.suppressed("en-dash", cfg))
        self.assertFalse(P.suppressed("word:leverage", cfg))


class Changed(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q", "-b", "main")
        self.write("warmup.md", ORIGINAL)
        shutil.copy(DIRTY, os.path.join(self.repo, "untouched.md"))
        shutil.copy(DIRTY, os.path.join(self.repo, "renamed.md"))
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        self.git("checkout", "-qb", "feature")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def git(self, *a):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *a],
                       cwd=self.repo, check=True, capture_output=True)

    def write(self, rel, text):
        os.makedirs(os.path.dirname(os.path.join(self.repo, rel)) or self.repo, exist_ok=True)
        with open(os.path.join(self.repo, rel), "w") as fh:
            fh.write(text)

    def changed(self, *args, cwd=None):
        r = run("--json", *args, "--changed", cwd=cwd or self.repo)
        return r, sorted((f["file"], f["rule"]) for f in json.loads(r.stdout)["new_findings"])

    def test_reports_only_what_changed_files_added(self):
        self.write("warmup.md", PADDED)
        self.git("mv", "renamed.md", "moved.md")
        self.write("notes.txt", "we leverage the holds shelf\n")
        r, found = self.changed()
        self.assertEqual(found, [("warmup.md", "vague-quantity")])
        self.assertEqual(r.returncode, 0)

    def test_untracked_ignore_and_strict(self):
        shutil.copy(DIRTY, os.path.join(self.repo, "new.md"))
        os.makedirs(os.path.join(self.repo, "vendor"))
        shutil.copy(DIRTY, os.path.join(self.repo, "vendor", "copy.md"))
        self.write(".deslop.json", json.dumps({"ignore": ["vendor/"]}))
        _, found = self.changed()
        self.assertEqual({f for f, _ in found}, {"new.md"})
        self.assertEqual(run("--strict", "--changed", cwd=self.repo).returncode, 1)

    def test_base_and_subdirectory(self):
        self.write("docs/a.md", PADDED)
        self.git("add", "-A")
        self.git("commit", "-qm", "docs")
        _, since_main = self.changed(cwd=os.path.join(self.repo, "docs"))
        _, since_head = self.changed("HEAD")
        self.assertEqual(since_main, [("docs/a.md", "vague-quantity")])
        self.assertEqual(since_head, [])

    def test_non_ascii_path(self):
        self.write("résumé.md", PADDED)
        _, found = self.changed()
        self.assertEqual(found, [("résumé.md", "vague-quantity")])

    def test_nested_config_applies(self):
        self.write("docs/.deslop.json", json.dumps({"disable": ["vague-quantity"]}))
        self.write("docs/a.md", PADDED)
        self.write("b.md", PADDED)
        _, found = self.changed()
        self.assertEqual(found, [("b.md", "vague-quantity")])

    def test_bad_base(self):
        self.assertEqual(run("--changed", "no-such-branch", cwd=self.repo).returncode, 255)


if __name__ == "__main__":
    unittest.main()
