"""the detector: runs the rule table and the document-level checks over a Doc.

findings carry char offsets into the original file, the line, the matched
text, the rule id, layer, severity and fix hint. text output reproduces the
bash script's "line N: <tell> -> <fix>" lines in file order.
"""

import json
import math
import re
import sys
from dataclasses import dataclass, asdict

import os

from . import rules as R
from . import contrast as C
from . import metrics as M
from . import project as P
from .text import Doc, Block, sentences, sentence_lengths


@dataclass
class Finding:
    rule: str
    layer: str
    severity: int
    label: str
    fix: str
    line: int
    start: int
    end: int
    text: str
    scope: str = "sentence"

    def as_text(self) -> str:
        return f"line {self.line}: {self.label} -> {self.fix}"


class Detector:
    def __init__(self, src: str, config: dict | None = None):
        self.doc = Doc(src)
        self.config = config or {}
        self.findings: list[Finding] = []
        self._compiled = [(rid, layer, sev, label, fix, re.compile(pat, flags), scope)
                          for rid, layer, sev, label, fix, pat, flags, scope in R.PATTERNS]
        words = {w: R.word_fix(w) for w in R.WORDS}
        phrases = dict(R.PHRASES)
        # config layers, merged in order: curated (rules.py), fingerprint
        # (measured), personal (pet peeves). later layers win.
        for name in ("fingerprint.json", "personal.json"):
            path = os.path.join(os.path.dirname(__file__), "data", name)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as fh:
                    extra = json.load(fh)
                words.update({k.lower(): v for k, v in extra.get("words", {}).items()})
                phrases.update({k.lower(): v for k, v in extra.get("phrases", {}).items()})
        def word_pattern(w: str) -> re.Pattern:
            exclude = R.WORD_EXCLUDE_AFTER.get(w.lower())
            tail = r"(?!\s+" + exclude + r")" if exclude else ""
            return re.compile(r"\b" + re.escape(w) + r"\b" + tail, re.I)

        self._words = [(w, fix, word_pattern(w)) for w, fix in words.items()]
        self._phrases = [(p, fix, re.compile(re.escape(p), re.I)) for p, fix in phrases.items()]

    # ----------------------------------------------------------------- helpers
    def add(self, rule, layer, sev, label, fix, start, end, text=""):
        self.findings.append(Finding(rule, layer, sev, label, fix, self.doc.line_of(start), start, end, text, R.fix_scope(rule)))

    def scan(self, blocks: list[Block], pat: re.Pattern, rule, layer, sev, label, fix, exclude: re.Pattern | None = None):
        for b in blocks:
            for m in pat.finditer(b.text):
                if exclude and exclude.match(b.text, m.start()):
                    continue
                self.add(rule, layer, sev, label, fix, b.start + m.start(), b.start + m.end(), m.group(0))

    # -------------------------------------------------------------- pattern rules
    def run_patterns(self):
        d = self.doc
        headings = [b for b in d.blocks if b.kind == "heading"]
        for w, fix, pat in self._words:
            self.scan(d.blocks, pat, "word:" + w, "lexical", 1, f"banned word '{w}'", fix)
        for p, fix, pat in self._phrases:
            self.scan(d.blocks, pat, "phrase:" + p, "lexical", 1, f"banned phrase '{p}'", fix)
        for rid, layer, sev, label, fix, pat, scope in self._compiled:
            blocks = headings if scope == "heading" else (d.prose_blocks if scope == "prose" else d.blocks)
            self.scan(blocks, pat, rid, layer, sev, label, fix)
        ours = [(f.start, f.end) for f in self.findings if f.rule in C.OUR_CONTRAST_RULES]
        for name, pat in C.COMPILED:
            for b in d.blocks:
                for m in pat.finditer(b.text):
                    s0, e0 = b.start + m.start(), b.start + m.end()
                    if any(s0 < e and s < e0 for s, e in ours):
                        continue
                    ours.append((s0, e0))
                    self.add("contrast:" + name, "structural", 2, f"contrast frame ({name})", "state the positive claim; drop the negated half", s0, e0, m.group(0)[:80])
        self.scan(d.blocks, R.QUANT_TAIL, "quantifier-tail", "structural", 2, "quantifier appositive tail",
                  "give it a verb or its own clause, not a tacked-on ', both/each/all X'", exclude=R.QUANT_TAIL_EXCLUDE)
        # italic subtitle: first non-blank line after an H1 that is wrapped in * or _
        cleaned_lines = d.cleaned.split("\n")
        prev = ""
        for i, line in enumerate(cleaned_lines):
            if re.match(r"^[*_][^*_].*[*_]\s*$", line) and re.match(r"^# ", prev):
                off = sum(len(l) + 1 for l in cleaned_lines[:i])
                self.add("italic-subtitle", "structural", 2, "italic subtitle under title", "fold it into the opening paragraph", off, off + len(line), line)
            if line.strip():
                prev = line

        # appositive caption: a bold-only line or image alt text with the
        # same noun-comma-noun shape as an appositive heading, e.g. a
        # figure captioned "**One queue, four policies**".
        APPOS_SHAPE = r"[^,.:!?]{2,44}, [^,.:!?]{2,44}"
        BOLD_LINE = re.compile(r"^(\*\*" + APPOS_SHAPE + r"\*\*)$")
        ALT_TEXT = re.compile(r"(!\[" + APPOS_SHAPE + r"\])")
        for i, line in enumerate(cleaned_lines):
            m = BOLD_LINE.match(line.strip()) or ALT_TEXT.search(line)
            if m:
                off = sum(len(l) + 1 for l in cleaned_lines[:i]) + line.find(m.group(1))
                self.add("appositive-heading", "structural", 2, "appositive caption or alt text", "name the subject plainly; if the second half matters, give it a verb", off, off + len(m.group(1)), m.group(1))

    # ------------------------------------------------------- document-level rules
    def run_document(self):
        d = self.doc
        cleaned, prose = d.cleaned, d.prose
        words_all = d.words()
        words_prose = len(prose.split())

        def first(pat: re.Pattern, text=cleaned):
            m = pat.search(text)
            return (m.start(), m.end(), m.group(0)) if m else (0, 0, "")

        def over_blocks(pat: re.Pattern):
            """count over unwrapped prose blocks; return (n, first_start, first_end, text)."""
            n, hit = 0, None
            for b in d.prose_blocks:
                for m in pat.finditer(b.text):
                    n += 1
                    if hit is None:
                        hit = (b.start + m.start(), b.start + m.end(), m.group(0))
            return (n,) + (hit or (0, 0, ""))

        def count_word(w, text=cleaned):
            return len(re.findall(r"\b" + re.escape(w) + r"\b", text, re.I))

        for w in R.OVERUSED_QUALIFIERS:
            n = count_word(w)
            if n >= 3:
                s, e, t = first(re.compile(r"\b" + w + r"\b", re.I))
                self.add("overused:" + w, "lexical", 3, f"overused qualifier '{w}' ({n} times)", "keep one; vary or cut the rest", s, e, t)
        for w in R.LLM_ADVERBS:
            n = count_word(w)
            if n >= 2:
                s, e, t = first(re.compile(r"\b" + w + r"\b", re.I))
                self.add("llm-adverb:" + w, "lexical", 3, f"LLM-marker adverb '{w}' ({n} times)", "cut it; the sentence carries its own emphasis", s, e, t)
        for w in R.OVERUSED_WORDS:
            n = count_word(w)
            if n >= 2:
                s, e, t = first(re.compile(r"\b" + w + r"\b", re.I))
                self.add("overused:" + w, "lexical", 3, f"overused word '{w}' ({n} times)", "keep it where it's the established term; name the concrete thing elsewhere", s, e, t)

        # colon-splice cadence: 5+ and denser than 1 per 240 words. the script
        # said 1 per 20 non-blank lines, which depends on wrap width; 240 words
        # is that threshold at a typical 12-word line.
        n, s, e, t = over_blocks(re.compile(r"[a-z]: [a-z]"))
        if n >= 5 and n * 240 > words_prose:
            self.add("colon-splice", "structural", 3, f"colon-splice cadence ({n} instances)", "restructure most into plain sentences; keep the few that earn it", s, e, t)
        n, s, e, t = over_blocks(re.compile(r"[a-z]; [a-z]"))
        if n >= 2:
            self.add("semicolon-chain", "structural", 3, f"semicolon-chain cadence ({n} instances)", "split them into sentences; at most one semicolon per document", s, e, t)

        # monotone rhythm: 4 consecutive sentences of 8+ words with spread <= 3, per paragraph
        for b in d.prose_blocks:
            if b.kind != "paragraph":
                continue
            lens = sentence_lengths(b.text)
            for i in range(len(lens) - 3):
                win = lens[i:i + 4]
                if min(win) >= 8 and max(win) - min(win) <= 3:
                    self.add("monotone-rhythm", "structural", 3, "monotone sentence rhythm (4 similar-length sentences)", "vary the lengths: fold two together, or cut one short", b.start, b.end, "")
                    break

        # fresh bare subjects: 4+ consecutive sentences each opening "The
        # X"/"A X"/"An X", none threaded back by a pronoun or connective
        for b in d.prose_blocks:
            if b.kind != "paragraph":
                continue
            run = 0
            for s in sentences(b.text):
                s = s.strip()
                first = s.split()[0].lower().strip(".,;:") if s.split() else ""
                if first in R.FRESH_SUBJECT_BREAK:
                    run = 0
                    continue
                run = run + 1 if R.FRESH_SUBJECT.match(s) else 0
                if run >= 4:
                    self.add("fresh-subjects", "grammatical", 2, "run of fresh bare subjects (4+ sentences, none threaded to the last)", "thread it (subordinate, connect, lead with the point) or make it a real list", b.start, b.end, "")
                    break

        # authorless voice and hedge floor, 300+ words
        if words_all > 300:
            fp = sum(count_word(w) for w in R.FIRST_PERSON)
            if fp == 0:
                self.add("authorless", "discourse", 3, f"authorless voice (no I/we/our in {words_all} words)", "the author exists: decisions read 'we chose X because', not 'X was chosen'", 0, 0, "")
            h = sum(count_word(w) for w in R.HEDGES)
            if h == 0:
                self.add("no-hedges", "discourse", 3, "no hedges in the whole document", "say what you are unsure of: probably, usually, I suspect, roughly", 0, 0, "")

        # numbers: per sentence and per paragraph, on prose paragraphs only
        for b in d.prose_blocks:
            if b.kind != "paragraph":
                continue
            worst = 0
            for s in sentences(b.text):
                s2 = R.ISO_DATE.sub("", s); s2 = R.VERSION.sub("", s2); s2 = R.IDENT_LETTER_FIRST.sub("", s2); s2 = R.IDENT_DIGIT_FIRST.sub("", s2)
                n = len(R.FIGURE.findall(s2)) + len(R.NUMERAL_WORDS.findall(s2))
                worst = max(worst, n)
            if worst > 3:
                self.add("number-dense-sentence", "discourse", 2, f"number-dense sentence ({worst} figures)", "keep the one figure the claim needs; move the rest to a table", b.start, b.end, "")
            t = R.IDENT_LETTER_FIRST.sub("", b.text); t = R.IDENT_DIGIT_FIRST.sub("", t)
            digits = len(re.findall(r"[0-9]", t))
            if digits > 12:
                self.add("number-dense-paragraph", "discourse", 2, f"number-dense paragraph ({digits} digits)", "state the takeaway in prose; put the values in a table", b.start, b.end, "")

        # hedge stack: 3+ hedges in one sentence
        for b in d.prose_blocks:
            if b.kind == "heading":
                continue
            for s in sentences(b.text):
                n = len(R.HEDGE_STACK.findall(s))
                if n >= 3:
                    i = b.text.find(s)
                    i = 0 if i < 0 else i
                    self.add("hedge-stack", "discourse", 2, f"hedge stack ({n} hedges in one sentence)", "keep the one hedge the uncertainty needs, or commit", b.start + i, b.start + i + len(s), s[:60])

        # table values restated in prose
        table_text = "\n".join(l for l in cleaned.split("\n") if l.strip().startswith("|") or l.count("|") >= 2)
        if table_text.strip():
            noid = R.IDENT_LETTER_FIRST.sub("", prose); noid = R.IDENT_DIGIT_FIRST.sub("", noid)
            for num in sorted(set(re.findall(r"[0-9]+[,.][0-9]+|[0-9]{3,}", table_text))):
                i = noid.find(num)
                if i >= 0:
                    self.add("table-restated", "discourse", 2, f"table value restated in prose ('{num}')", "name the takeaway in prose; let the table hold the value", i, i + len(num), num)

        # thematic breaks
        hrs = [b for b in d.blocks if b.kind == "hr"]
        if len(hrs) >= 3:
            self.add("thematic-breaks", "structural", 3, f"thematic breaks as section glue ({len(hrs)} rules)", "headings separate sections; delete the rules", hrs[0].start, hrs[0].end, "---")

        # flat rhythm across the document: 15+ sentences, sd < 5 or cv < 0.45
        lens = [len(s.split()) for s in re.split(r"[.!?]", prose) if len(s.split()) > 3]
        if len(lens) >= 15:
            m = sum(lens) / len(lens); sd = math.sqrt(sum(x * x for x in lens) / len(lens) - m * m)
            self.metrics.update(sentence_mean=round(m, 1), sentence_sd=round(sd, 1), sentence_cv=round(sd / m, 2) if m else 0)
            if sd / m < 0.45 or sd < 5:
                self.add("flat-rhythm", "structural", 3, f"flat sentence rhythm across the document (sd {sd:.1f} words, cv {sd / m:.2f}; human prose runs sd near 8)", "vary the lengths: fold sentences together, let one run long, cut one short", 0, 0, "")

        # rule of three: 3+ triples
        n, s, e, t = over_blocks(R.TRIPLE)
        if n >= 3:
            self.add("rule-of-three", "structural", 3, f"rule of three ({n} triples)", "keep one; make the others two items or four", s, e, t)

        # contrast as a habit: 4+ and denser than 1 per 400 words
        n, s, e, t = over_blocks(R.CONTRAST)
        if n >= 4 and n * 400 > words_prose:
            self.add("contrast-habit", "structural", 3, f"contrast as a habit ({n} in {words_prose} words)", "state the fact; keep a foil only where the other option was real", s, e, t)

        # dash and semicolon budget: 1 per 1000 words, minimum 1
        allowed = max(1, words_prose // 1000)
        breaks = len(re.findall("—|–|[a-zA-Z,)] +- +[a-zA-Z(]|;", prose))
        self.metrics.update(interrupters=breaks, interrupters_allowed=allowed)
        if breaks > allowed:
            self.add("dash-budget", "structural", 3, f"dash/semicolon budget ({breaks} in {words_prose} words, allowed {allowed})", "most are a comma or a full stop; keep the one that earns it", 0, 0, "")

        # one name per thing: the same camelCase/PascalCase identifier
        # spelled two ways in the document (UserId vs UserID). code spans
        # are already blanked, so this only sees prose/heading references,
        # not real code.
        first_spelling: dict[str, str] = {}
        flagged: set[str] = set()
        for m in R.NAME_VARIANT.finditer(cleaned):
            term = m.group(0)
            key = term.lower()
            if key not in first_spelling:
                first_spelling[key] = term
            elif first_spelling[key] != term and key not in flagged:
                flagged.add(key)
                self.add("name-drift", "lexical", 2, f"one thing, two spellings ('{first_spelling[key]}' and '{term}')",
                         "pick one spelling and use it everywhere", m.start(), m.end(), term)

    # ------------------------------------------------------------- metric rules
    def run_metrics(self):
        d = self.doc
        m = M.compute(d.prose_blocks, d.prose)
        spans = m.pop("_participial_spans")
        bullet_lists = m.pop("_bullet_lists")
        self.metrics.update(m)
        for g in bullet_lists:
            if g["same_bold_label"]:
                self.add("symmetric-bullets", "structural", 2,
                         f"symmetric bullet list ({g['n']} items, all opening with a bold label)",
                         "let the items differ in length and shape; fold the label into the sentence or drop it",
                         g["start"], g["end"], "")
        sec_t = R.THRESHOLDS["section_weight_cv"]
        sec_cv = m["section_weight_cv"]
        if sec_t and sec_cv is not None and sec_cv < sec_t:
            self.add("even-section-weight", "structural", 3,
                     f"even section weight ({m['section_count']} sections, word-count cv {sec_cv:.2f}; human docs run above {sec_t:.1f})",
                     "let the hard part take more room; sections don't need to match", 0, 0, "")
        t = R.THRESHOLDS["participial_post_comma_per_1k"]
        rate = m["participial_post_comma_per_1k"]
        if t and rate > t and d.words() >= 300:
            self.add("participial-rate", "grammatical", 3,
                     f"participial clause rate ({rate:.1f} per 1k words after a comma; human prose runs under {t:.0f})",
                     "end sentences at the fact; say the consequence in its own sentence", 0, 0, "")
            # the instances the named trailing-participial rule didn't already flag
            named = [(f.start, f.end) for f in self.findings if f.rule == "trailing-participial"]
            for s0, e0, w in spans:
                if d.cleaned[max(0, s0 - 2):s0] == ", " and not any(s < e0 and s0 < e for s, e in named):
                    self.add("participial-instance", "grammatical", 1, f"participial clause after a comma ('{w}')",
                             "end the sentence at the fact", s0, e0, w)

    def clusters(self) -> list[dict]:
        """paragraphs with several findings: the signal."""
        out = []
        need = R.THRESHOLDS["cluster_min_findings"]
        for b in self.doc.blocks:
            if b.kind not in ("paragraph", "item"):
                continue
            hits = [f for f in self.findings if b.start <= f.start < b.end and f.rule not in ("authorless", "no-hedges", "flat-rhythm", "dash-budget", "participial-rate")]
            if len(hits) >= need:
                out.append({"line": b.line, "findings": len(hits), "rules": sorted({f.rule.split(":")[0] for f in hits})})
        return out

    # ------------------------------------------------------------------- driver
    def run(self):
        self.metrics = {"words": self.doc.words(), "words_prose": len(self.doc.prose.split())}
        self.run_patterns()
        self.run_document()
        self.run_metrics()
        if self.config:
            self.findings = [f for f in self.findings if not P.suppressed(f.rule, self.config)]
        self.findings.sort(key=lambda f: (f.line, f.start, f.rule))
        w = max(1, self.metrics["words"])
        by_layer = {}
        for f in self.findings:
            by_layer[f.layer] = by_layer.get(f.layer, 0) + 1
        self.metrics.update(
            findings=len(self.findings),
            findings_per_1k=round(len(self.findings) * 1000 / w, 2),
            by_layer=by_layer,
            score=round(sum(f.severity for f in self.findings) * 1000 / w, 2),
            clusters=self.clusters(),
        )
        return self

    def as_json(self) -> str:
        return json.dumps({"metrics": self.metrics, "findings": [asdict(f) for f in self.findings]}, indent=2)

    def as_text(self) -> str:
        if not self.findings:
            return "clean: no mechanical tells found\n"
        out = "".join(f.as_text() + "\n" for f in self.findings)
        cl = self.metrics.get("clusters") or []
        if cl:
            out += "clusters: " + ", ".join(f"line {c['line']} ({c['findings']} findings)" for c in cl) + "\n"
        return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    # check_tells.sh cds into scripts/ and passes the caller's cwd here
    cwd = os.environ.get("DESLOP_CWD") or os.getcwd()
    if "--changed" in argv:
        strict = "--strict" in argv
        rest = [a for a in argv if a not in ("--changed", "--json", "--strict")]
        if len(rest) > 1 or any(a.startswith("--") for a in rest):
            print("usage: check_tells.sh [--json] [--strict] --changed [base]", file=sys.stderr)
            return 255
        return P.run_changed(cwd, rest[0] if rest else None, "--json" in argv, strict)
    argv = [a if a.startswith("--") else os.path.join(cwd, a) for a in argv]
    if "--diff" in argv:
        from .diff import main as diff_main
        return diff_main(argv)
    as_json = "--json" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print("usage: python3 -m deslop [--json] <file>", file=sys.stderr)
        return 255
    try:
        src = open(args[0], encoding="utf-8", errors="replace").read()
    except OSError:
        print("usage: python3 -m deslop [--json] <file>", file=sys.stderr)
        return 255
    det = Detector(src, P.load_config(P.find_config(args[0]))).run()
    sys.stdout.write(det.as_json() + "\n" if as_json else det.as_text())
    return min(255, len(det.findings))
