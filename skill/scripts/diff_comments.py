#!/usr/bin/env python3
"""diff_comments.py - collect the code comments a branch adds, as Markdown.

usage: diff_comments.py [base] > comments.md
       check_tells.sh comments.md

Reads `git diff -U0 <base>...HEAD` (default origin/HEAD, then main) in the
current directory and prints each run of added comment lines under a
heading naming the file and line, so the detector can read comments the
way it reads prose. Recognises //, /* */ and leading * for C-family files
and # for Python, shell, PowerShell, CMake and YAML. String literals and
code are ignored; a comment trailing code on the same line is kept.
"""
import os
import re
import subprocess
import sys

SLASH = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".cs", ".js", ".jsx", ".ts", ".tsx",
         ".java", ".go", ".rs", ".swift", ".kt", ".hlsl", ".hlsli", ".fx", ".glsl", ".m", ".mm"}
HASH = {".py", ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".cmake", ".yml", ".yaml", ".toml", ".rb", ".pl"}
HASH_NAMES = {"CMakeLists.txt", "Makefile", "Dockerfile"}


def comment_text(path: str, line: str) -> str | None:
    """the comment on an added line, or None."""
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    s = line.strip()
    if ext in SLASH:
        if s.startswith(("/*", "*")) and not s.startswith("*/"):
            return s.lstrip("/*").rstrip("*/").strip() or None
        m = re.search(r"(?<![:\"'])//+(.*)$", line)
        if m and line[:m.start()].count('"') % 2 == 0:
            return m.group(1).strip() or None
        return None
    if ext in HASH or name in HASH_NAMES:
        if s.startswith("#!"):
            return None
        m = re.search(r"(?:^|\s)#+(?!\[)(.*)$", line)
        if m and line[:m.start()].count('"') % 2 == 0 and line[:m.start()].count("'") % 2 == 0:
            return m.group(1).strip() or None
    return None


def collect(diff: str) -> list[tuple[str, int, list[str]]]:
    """runs of consecutive added comment lines: (path, first line, texts)."""
    runs, path, lineno, cur = [], None, 0, None
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path = raw[6:] if raw.startswith("+++ b/") else None
            cur = None
            continue
        m = re.match(r"@@ -\S+ \+(\d+)(?:,\d+)? @@", raw)
        if m:
            lineno, cur = int(m.group(1)), None
            continue
        if path is None or not raw.startswith("+"):
            cur = None
            continue
        text = comment_text(path, raw[1:])
        # only whole-line comments join a run; one trailing code stands alone
        whole = raw[1:].lstrip().startswith(("//", "/*", "*", "#"))
        if text is None:
            cur = None
        elif whole and cur is not None and cur[1] + len(cur[2]) == lineno:
            cur[2].append(text)
        else:
            cur = (path, lineno, [text])
            runs.append(cur)
            if not whole:
                cur = None
        lineno += 1
    return runs


def main(argv: list[str]) -> int:
    base = argv[0] if argv else None
    if base is None:
        for cand in ("origin/HEAD", "origin/main", "origin/master", "main", "master"):
            if subprocess.run(["git", "rev-parse", "--verify", "-q", cand], capture_output=True).returncode == 0:
                base = cand
                break
    if base is None:
        print("diff_comments.py: no base branch found; pass one", file=sys.stderr)
        return 2
    diff = subprocess.run(["git", "diff", "-U0", f"{base}...HEAD"], capture_output=True, text=True)
    if diff.returncode != 0:
        print(diff.stderr.strip(), file=sys.stderr)
        return 2
    for path, line, texts in collect(diff.stdout):
        print(f"## {path} line {line}\n\n{' '.join(texts)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
