"""document metrics: rhythm (paragraph uniformity, MATTR) and grammatical rates
(participial clauses, nominalizations) per 1,000 words.

thresholds are not here; they come from calibrate.py over the human baseline
and live in rules.THRESHOLDS. the rates are the plan's layer 3, after
Reinhart et al. 2025: instruction-tuned models use present participial
clauses at 2 to 5x the human rate and nominalizations at 1.5 to 2x.
"""

import math
import re

from .text import Block, sentences

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*")

# words ending in -ing that are not participles, or that open a sentence for
# other reasons. kept short on purpose; calibration sets the bar.
ING_STOP = {"during", "thing", "things", "nothing", "something", "everything", "anything", "morning",
            "evening", "string", "strings", "spring", "king", "ring", "wing", "sing", "bring", "sibling",
            "ceiling", "building", "buildings", "meeting", "meetings", "setting", "settings", "encoding",
            "encodings", "streaming", "recording", "recordings", "timing", "sampling", "caching", "logging",
            "packaging", "rendering", "warning", "warnings", "following", "including", "according", "regarding",
            "using", "being", "having", "doing", "existing", "remaining", "underlying", "ongoing", "missing"}

NOM_SUFFIX = re.compile(r"(?:tion|sion|ment|ness|ity|ance|ence|ancy|ency)s?$", re.I)
NOM_STOP = {"moment", "comment", "comments", "document", "documents", "segment", "segments", "element", "elements",
            "equipment", "argument", "arguments", "environment", "environments", "city", "community", "entity",
            "entities", "identity", "quantity", "quality", "security", "priority", "minority", "majority",
            "university", "opportunity", "station", "nation", "section", "sections", "position", "positions",
            "function", "functions", "option", "options", "question", "questions", "version", "versions",
            "session", "sessions", "instance", "instances", "distance", "balance", "sequence", "sequences",
            "reference", "references", "difference", "differences", "experience", "science", "audience",
            "business", "witness", "fitness", "condition", "conditions", "portion", "region", "regions",
            "fraction", "motion", "notion", "mention", "attention", "content", "percent", "component",
            "components", "agent", "agents", "client", "clients", "event", "events", "latency", "currency",
            "frequency", "efficiency", "emergency", "agency", "dependency", "dependencies", "capacity",
            "velocity", "density", "opacity", "property", "properties", "party", "duty", "beauty", "county",
            "faculty", "penalty", "safety", "variety", "society", "anxiety", "entirety", "quantities"}


def tokens(text: str) -> list[str]:
    return [t.lower() for t in TOKEN.findall(text)]


def mattr(toks: list[str], window: int = 500) -> float | None:
    """moving-average type-token ratio. window shrinks to the text if shorter."""
    n = len(toks)
    if n < 50:
        return None
    w = min(window, n)
    counts: dict[str, int] = {}
    for t in toks[:w]:
        counts[t] = counts.get(t, 0) + 1
    total = len(counts)
    for i in range(w, n):
        out, inn = toks[i - w], toks[i]
        counts[out] -= 1
        if counts[out] == 0:
            del counts[out]
        counts[inn] = counts.get(inn, 0) + 1
        total += len(counts)
    return round(total / (n - w + 1) / w, 4)


def _cv(lens: list[int]) -> float | None:
    if not lens:
        return None
    m = sum(lens) / len(lens)
    if not m:
        return None
    sd = math.sqrt(sum((x - m) ** 2 for x in lens) / len(lens))
    return round(sd / m, 3)


def paragraph_uniformity(blocks: list[Block]) -> tuple[int, float | None]:
    """count of prose paragraphs and the coefficient of variation of their lengths."""
    lens = [len(b.text.split()) for b in blocks if b.kind == "paragraph" and len(b.text.split()) >= 5]
    if len(lens) < 4:
        return len(lens), None
    return len(lens), _cv(lens)


ITEM_MARKER = re.compile(r"^\s*(?:[-*]|[0-9]+\.)\s+")
ITEM_BOLD_LABEL = re.compile(r"^\*\*[^*]+\*\*")


def bullet_lists(blocks: list[Block]) -> list[dict]:
    """group runs of 3+ consecutive 'item' blocks: each
    entry is the run's span, item count, word-count CV, and whether every
    item opens with a bold label (a second, independent "same shape" signal
    the CV alone can miss, e.g. **Latency:** / **Cost:** / **Risk:** with
    deliberately varied body length).
    """
    out = []
    i, n = 0, len(blocks)
    while i < n:
        if blocks[i].kind != "item":
            i += 1
            continue
        j = i
        while j < n and blocks[j].kind == "item":
            j += 1
        group = blocks[i:j]
        if len(group) >= 3:
            stripped = [ITEM_MARKER.sub("", b.text) for b in group]
            lens = [len(s.split()) for s in stripped]
            out.append({
                "start": group[0].start,
                "end": group[-1].end,
                "n": len(group),
                "cv": _cv(lens),
                "same_bold_label": all(ITEM_BOLD_LABEL.match(s) for s in stripped),
            })
        i = j
    return out


SECTION_HEADING = re.compile(r"^(#{1,2})(?!#)")


def section_weights(blocks: list[Block]) -> list[int]:
    """word count per H2 section. Content before the first
    H2, and any H1, doesn't belong to a section; an H1 also closes out
    whatever H2 section came before it.
    """
    sections, cur = [], None
    for b in blocks:
        if b.kind == "heading":
            m = SECTION_HEADING.match(b.text)
            if m:
                if cur is not None:
                    sections.append(cur)
                cur = 0 if len(m.group(1)) == 2 else None
                continue
        if cur is not None:
            cur += len(b.text.split())
    if cur is not None:
        sections.append(cur)
    return [s for s in sections if s > 0]


def clipped_openers(blocks: list[Block]) -> tuple[int, int]:
    """(paragraph count, count whose first sentence is 7 words or fewer).
    a share, not a per-instance hit: one short opener is normal rhythm,
    most of them being short is the tell.

    Paragraphs under 5 words are dropped from both counts: a PDF-extracted
    paper can turn page numbers, running heads and isolated keywords into
    one-line "paragraphs", which swamps the real signal. Same floor
    `paragraph_uniformity` already uses.
    """
    paras = [b for b in blocks if b.kind == "paragraph" and len(b.text.split()) >= 5]
    clipped = 0
    for b in paras:
        s = sentences(b.text)
        if s and len(s[0].split()) <= 7:
            clipped += 1
    return len(paras), clipped


def _is_participle(word: str) -> bool:
    w = word.lower().strip("*_\"'")
    return len(w) > 4 and w.endswith("ing") and w not in ING_STOP


def participial_clauses(blocks: list[Block]) -> tuple[int, int, list[tuple[int, int, str]]]:
    """(sentence-initial count, post-comma count, spans) over prose paragraphs and items."""
    initial, post, spans = 0, 0, []
    for b in blocks:
        if b.kind not in ("paragraph", "item"):
            continue
        for m in re.finditer(r"(?:^|(?<=[.!?] ))([A-Z][a-z]+ing)\b(?= [a-z])", b.text):
            if _is_participle(m.group(1)):
                initial += 1
                spans.append((b.start + m.start(1), b.start + m.end(1), m.group(1)))
        for m in re.finditer(r", ([a-z]+ing)\b(?= [a-z])", b.text):
            if _is_participle(m.group(1)):
                post += 1
                spans.append((b.start + m.start(1), b.start + m.end(1), m.group(1)))
    return initial, post, spans


def nominalizations(toks: list[str]) -> int:
    return sum(1 for t in toks if len(t) >= 7 and NOM_SUFFIX.search(t) and t not in NOM_STOP)


def compute(blocks: list[Block], prose_text: str) -> dict:
    toks = tokens(prose_text)
    n = max(1, len(toks))
    per_k = 1000 / n
    initial, post, spans = participial_clauses(blocks)
    nparas, cv = paragraph_uniformity(blocks)
    nom = nominalizations(toks)
    blists = bullet_lists(blocks)
    qualifying_cvs = [g["cv"] for g in blists if g["cv"] is not None]
    sections = section_weights(blocks)
    section_cv = _cv(sections) if len(sections) >= 3 else None
    nparas_all, nclipped = clipped_openers(blocks)
    return {
        "tokens": len(toks),
        "mattr": mattr(toks),
        "paragraphs": nparas,
        "paragraph_cv": cv,
        "participial_initial_per_1k": round(initial * per_k, 2),
        "participial_post_comma_per_1k": round(post * per_k, 2),
        "participial_per_1k": round((initial + post) * per_k, 2),
        "nominalizations_per_1k": round(nom * per_k, 2),
        "bullet_lists_n": len(blists),
        "bullet_min_cv": min(qualifying_cvs) if qualifying_cvs else None,
        "section_count": len(sections),
        "section_weight_cv": section_cv,
        "clipped_opener_paragraphs": nparas_all,
        "clipped_opener_share": round(nclipped / nparas_all, 3) if nparas_all >= 5 else None,
        "_participial_spans": spans,
        "_bullet_lists": blists,
    }
