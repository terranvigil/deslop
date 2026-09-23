"""using the detector from other repos: per-repo config, and checking only
the prose a branch or commit changed. what counts as "new" is diff.py's
comparison, the same one --diff uses.

.deslop.json, found by walking up from the checked file to the git root:

  {
    "allow":   ["gates", "gating"],      # jargon: silences word:, phrase:,
                                         # overused: and llm-adverb: findings
    "disable": ["authorless"],           # rule ids, or a family ("contrast")
    "ignore":  ["CHANGELOG.md", "vendor/", "docs/archive/*"],
    "include": ["*.md", "*.markdown"]    # which files --changed looks at
  }

ignore and include are fnmatch globs on the repo-relative path ("*" also
crosses "/"); an entry ending in "/" is a directory prefix. only --changed
applies them, and only from the root .deslop.json: a file named on the
command line is always checked. allow and disable come from each file's
nearest config in every mode.
"""

import fnmatch
import json
import os
import subprocess
import sys


CONFIG = ".deslop.json"
KEYS = {"allow", "disable", "ignore", "include"}
TERM_FAMILIES = ("word", "phrase", "overused", "llm-adverb")
DEFAULT_INCLUDE = ["*.md", "*.markdown"]


# ------------------------------------------------------------------- config
def find_config(start: str) -> str | None:
    """nearest .deslop.json from `start` (a file or directory) up to the git root."""
    d = os.path.abspath(start if os.path.isdir(start) else os.path.dirname(start))
    while True:
        path = os.path.join(d, CONFIG)
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(d)
        if os.path.exists(os.path.join(d, ".git")) or parent == d:
            return None
        d = parent


def load_config(path: str | None) -> dict:
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"deslop: ignoring {path}: {e}", file=sys.stderr)
        return {}
    if not isinstance(cfg, dict):
        print(f"deslop: ignoring {path}: expected a JSON object", file=sys.stderr)
        return {}
    for k in sorted(set(cfg) - KEYS):
        print(f"deslop: {path}: unknown key '{k}' (known: {', '.join(sorted(KEYS))})", file=sys.stderr)
    return cfg


def suppressed(rule: str, cfg: dict) -> bool:
    family, _, term = rule.partition(":")
    if rule in cfg.get("disable", ()) or family in cfg.get("disable", ()):
        return True
    return family in TERM_FAMILIES and term.lower() in {a.lower() for a in cfg.get("allow", ())}


def _match(rel: str, globs) -> bool:
    return any(rel.startswith(g) if g.endswith("/") else fnmatch.fnmatch(rel, g) for g in globs)


# ------------------------------------------------------------------ changed
def _git(cwd: str, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} failed")
    return r.stdout


def changed_files(cwd: str, base: str | None) -> tuple[str, str, list[tuple[str, str | None]]]:
    """(repo root, merge-base, [(path, path at base or None)]) for every file
    that differs between the merge-base and the working tree, untracked
    files included. paths are repo-relative."""
    root = _git(cwd, "rev-parse", "--show-toplevel").strip()
    if base is None:
        for b in ("main", "master"):
            if subprocess.run(["git", "rev-parse", "--verify", "-q", b], cwd=root, capture_output=True).returncode == 0:
                base = b
                break
        else:
            raise RuntimeError("no main or master branch; pass a base: --changed <base>")
    mb = _git(root, "merge-base", base, "HEAD").strip()
    # -z: NUL-separated and unquoted, or git C-quotes non-ASCII paths
    # ("r\303\251sum\303\251.md") and they never match a glob or open
    files = []
    fields = _git(root, "diff", "-z", "--name-status", "-M", "--diff-filter=ACMR", mb).split("\0")
    i = 0
    while i < len(fields) and fields[i]:
        status = fields[i]
        if status.startswith("R"):
            files.append((fields[i + 2], fields[i + 1]))
            i += 3
        else:
            files.append((fields[i + 1], None if status == "A" else fields[i + 1]))
            i += 2
    for path in _git(root, "ls-files", "-z", "--others", "--exclude-standard").split("\0"):
        if path:
            files.append((path, None))
    return root, mb, files


def run_changed(cwd: str, base: str | None, as_json: bool, strict: bool) -> int:
    from .diff import compare
    try:
        root, mb, files = changed_files(cwd, base)
    except (RuntimeError, OSError) as e:
        print(f"deslop --changed: {e}", file=sys.stderr)
        return 255
    # which files: the root config's include/ignore. how each is checked:
    # its nearest config, the same one single-file mode and --diff use
    cfg = load_config(os.path.join(root, CONFIG) if os.path.isfile(os.path.join(root, CONFIG)) else None)
    include = cfg.get("include", DEFAULT_INCLUDE)
    nearest: dict[str, dict] = {}
    report, checked = [], 0
    for rel, old in files:
        if not _match(rel, include) or _match(rel, cfg.get("ignore", ())):
            continue
        try:
            after_src = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        before_src = ""
        if old is not None:
            try:
                before_src = _git(root, "show", f"{mb}:{old}")
            except RuntimeError:
                before_src = ""
        checked += 1
        path = find_config(os.path.join(root, rel))
        if path not in nearest:
            nearest[path] = load_config(path)
        for f in compare(before_src, after_src, nearest[path])["added"]:
            report.append((rel, f))

    blocking = [f for _, f in report if f.severity >= 3]
    if as_json:
        from dataclasses import asdict
        print(json.dumps({"base": mb, "files_checked": checked,
                          "new_findings": [{"file": rel, **asdict(f)} for rel, f in report]}, indent=2))
    elif report:
        for rel, f in report:
            print(f"{rel}:{f.line}: {f.label} -> {f.fix}")
        print(f"deslop: {len(report)} new finding(s) in {len({r for r, _ in report})} of {checked} changed "
              f"prose file(s) since {mb[:10]}" + ("" if strict else " (advisory)"))
    return 1 if strict and blocking else 0
