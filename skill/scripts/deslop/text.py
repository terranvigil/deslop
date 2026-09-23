"""preprocessing: blank code and link targets, blank tables, split into blocks.

every transform keeps the string the same length, so an offset into the
cleaned text is an offset into the original file. line numbers come from
counting newlines in the original up to that offset.
"""

import re
from dataclasses import dataclass

FENCE = re.compile(r"^(```|~~~)")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
TABLE_LEAD = re.compile(r"^\s*\|")
TABLE_SEP = re.compile(r"^\s*[-:|\s]+$")
HEADING = re.compile(r"^#{1,6} ")
LIST_ITEM = re.compile(r"^\s*([-*]|[0-9]+\.)\s")
HR = re.compile(r"^-{3,}\s*$")


def _blank(s: str) -> str:
    return re.sub(r"[^\n]", " ", s)


def clean(src: str) -> str:
    """blank fenced code blocks, inline code spans and link targets."""
    out = []
    infence = False
    for line in src.split("\n"):
        if FENCE.match(line):
            infence = not infence
            out.append(_blank(line))
            continue
        if infence:
            out.append(_blank(line))
            continue
        line = LINK_TARGET.sub(lambda m: "]" + " " * (len(m.group(0)) - 1), line)
        line = INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)
        out.append(line)
    return "\n".join(out)


def is_table_row(line: str) -> bool:
    if TABLE_LEAD.match(line):
        return True
    if TABLE_SEP.match(line) and re.search(r"[-|]", line):
        return True
    return line.count("|") >= 2


def blank_tables(cleaned: str) -> str:
    """the prose stream: table rows blanked so cadence and number checks skip them."""
    return "\n".join(_blank(l) if is_table_row(l) else l for l in cleaned.split("\n"))


@dataclass
class Block:
    kind: str  # paragraph | heading | item | hr | table
    start: int  # char offset into the file
    end: int
    text: str  # unwrapped: newlines replaced by spaces, same length as the source span

    @property
    def line(self) -> int:  # 1-based line of the block's first char; set by the caller
        return self._line

    @line.setter
    def line(self, v: int):
        self._line = v


def blocks(text: str) -> list[Block]:
    """split into paragraphs, headings, list items, rules and table rows.

    a paragraph is a run of non-blank lines that aren't headings, list markers,
    rules or table rows. a list item is its marker line plus following indented
    continuation lines. offsets are into `text`.
    """
    out: list[Block] = []
    pos = 0
    lines = text.split("\n")
    offsets = []
    for l in lines:
        offsets.append(pos)
        pos += len(l) + 1
    i = 0
    n = len(lines)

    def emit(kind, a, b):
        start, end = offsets[a], offsets[b - 1] + len(lines[b - 1])
        out.append(Block(kind, start, end, text[start:end].replace("\n", " ")))

    while i < n:
        l = lines[i]
        if not l.strip():
            i += 1
            continue
        if HR.match(l):
            emit("hr", i, i + 1); i += 1; continue
        if HEADING.match(l):
            emit("heading", i, i + 1); i += 1; continue
        if is_table_row(l):
            emit("table", i, i + 1); i += 1; continue
        if LIST_ITEM.match(l):
            j = i + 1
            while j < n and lines[j].strip() and lines[j][:1].isspace() and not LIST_ITEM.match(lines[j]) and not is_table_row(lines[j]):
                j += 1
            emit("item", i, j); i = j; continue
        j = i + 1
        while j < n and lines[j].strip() and not HEADING.match(lines[j]) and not LIST_ITEM.match(lines[j]) and not is_table_row(lines[j]) and not HR.match(lines[j]):
            j += 1
        emit("paragraph", i, j); i = j
    line_starts = offsets
    for b in out:
        b.line = _line_of(line_starts, b.start)
    return out


def _line_of(line_starts: list[int], offset: int) -> int:
    lo, hi = 0, len(line_starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if line_starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


class Doc:
    def __init__(self, src: str):
        self.src = src
        self.cleaned = clean(src)
        self.prose = blank_tables(self.cleaned)
        self.blocks = blocks(self.cleaned)
        self.prose_blocks = [b for b in blocks(self.prose) if b.kind != "table"]
        self._line_starts = [0] + [m.end() for m in re.finditer(r"\n", src)]
        self.lines = src.split("\n")

    def line_of(self, offset: int) -> int:
        return _line_of(self._line_starts, offset)

    def words(self, text: str | None = None) -> int:
        return len((self.cleaned if text is None else text).split())


SENT_SPLIT = re.compile(r"[.!?]+ +")

# a bare period-plus-space split reads a bibliography entry ("[5] J. Smith,
# A. Jones, B. Lee...") as several fake short "sentences". Protect the two shapes that cause it: a single
# capital-letter initial ("J.", "A.") and a short list of common dotted
# abbreviations, before splitting. Python's re requires fixed-width
# lookbehind, so abbreviations with an internal period ("e.g.") can't be
# excluded that way; substitute a placeholder for the period instead and
# restore it after splitting. Trade-off, accepted: a real sentence that
# ends in a bare capital letter ("See Section A. The next part covers B.")
# merges with the next one. Rarer than the bug this fixes.
_ABBREV = ["e.g.", "i.e.", "cf.", "vs.", "etc.", "et al.", "Fig.", "Figs.",
           "Eq.", "Eqs.", "No.", "pp.", "Prof.", "Dr.", "Mr.", "Mrs.",
           "Jr.", "Sr.", "Inc.", "Corp.", "Ltd.", "approx.", "Vol.",
           "Ch.", "Sec.", "Ref.", "Refs.", "St.", "Ave.", "Proc.",
           "Trans.", "Conf.", "Rev.", "Jan.", "Feb.", "Mar.", "Apr.",
           "Jun.", "Jul.", "Aug.", "Sep.", "Sept.", "Oct.", "Nov.", "Dec."]
_ABBREV_RE = re.compile(r"\b(?:" + "|".join(re.escape(a) for a in _ABBREV) + r")", re.I)
_INITIAL_RE = re.compile(r"\b[A-Z]\.(?=\s)")


def _protect_abbrevs(text: str) -> str:
    text = _ABBREV_RE.sub(lambda m: m.group(0)[:-1] + "\x00", text)
    return _INITIAL_RE.sub(lambda m: m.group(0)[:-1] + "\x00", text)


def sentences(text: str) -> list[str]:
    """the script's sentence split: on terminal punctuation followed by
    spaces, with abbreviations and initials protected first."""
    protected = _protect_abbrevs(text)
    return [s.replace("\x00", ".") for s in SENT_SPLIT.split(protected) if s.strip()]


def sentence_lengths(text: str) -> list[int]:
    return [len(s.split()) for s in sentences(text)]
