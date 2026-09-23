"""surface not-x-but-y patterns, ported from slop-score's regexes-stage1.js.

MIT, copyright 2025 Sam Paech. these carry guards ours lack: a reporter
frame ("she knew that it wasn't ...") and a following subordinator ("but
when ...") are not contrasts. slop-score's stage 2 needs a POS tagger and
is not ported; a tagger is worth adding only if these prove too noisy.

matches that overlap one of our own scaffold findings are dropped in
detect.py so a contrast is counted once.
"""

import re

MAXG = 160
PRON = r"(?:it|they|this|that)"
BE = r"(?:is|are|was|were)"
BE_NEG = r"(?:is\s+not|are\s+not|was\s+not|were\s+not|isn't|aren't|wasn't|weren't|ain't)"
SS = r"(?:^|(?<=[.?!]\s))"
Q = "[\"“”']"

STAGE1 = [
    # 1) "not X, but Y"
    ("not-but", r"\b(?:(?:" + BE_NEG + r")|not(?!\s+(?:that|only)\b))\s+"
     r"(?:(?!\bbut\b|[.?!]).){1,100}?"
     r"[,;:]\s*but\s+"
     r"(?!when\b|while\b|which\b|who\b|whom\b|whose\b|where\b|if\b|that\b|as\b|because\b|although\b|though\b|till\b|until\b|unless\b|"
     r"here\b|there\b|then\b|my\b|we\b|I\b|you\b|it\s+seems\b|it\s+appears\b|it\s+felt\b|it\s+looks?\b|anything\b)"),
    # 2) dash form "not/n't ... - pron BE/verb"
    ("not-dash", r"\b(?:\w+n't|not)\s+(?:just|only|merely)?\s+"
     r"(?:(?![.?!]).){1," + str(MAXG) + r"}?"
     r"(?:-|\s-\s|[—–])\s*"
     + PRON + r"\s+(?:(?:'re|are|'s|is|were|was)\b|(?!'re|are|'s|is|were|was)[*_~]*[a-z]\w*)"),
    # 3) "It/They BE not ... . It/They BE ..."
    ("pron-be-not-sep-be", SS + r"\s*" + Q + r"?"
     r"(?:(?:" + PRON + r"\s+" + BE + r"\s+not)|(?:" + PRON + r"\s+" + BE + r"n't)|(?:it's|they're|that's)\s+not)\b"
     r"[^.?!]{0," + str(MAXG) + r"}[.;:?!]\s*" + Q + r"?"
     + PRON + r"\s+(?:" + BE + r"|(?:'s|'re))\b(?!\s+not\b)"),
    # 4) NP-led "... wasn't ... . It/They BE ..." with reporter-frame guards
    ("np-be-not-sep-they-be", SS + r"\s*"
     r"(?![^.?!]{0,80}\b(?:knew|know|thought|think|said|says|told|heard|learned)\b[^.?!]{0,40}?\bthat\b)"
     r"(?!\s*not\s+without\b)"
     r"(?![^.?!]{0,50}\bnot\s+put\b)"
     r"[^.?!]{0," + str(MAXG) + r"}?\b(?:" + BE_NEG + r")\b[^.?!]{0," + str(MAXG) + r"}[.;:?!]\s*"
     + Q + r"?" + PRON + r"\b(?:'re|\s+(?:are|were|is|was))\b(?!\s+not\b)"),
    # 5) "no longer ... ; it/they was ..."
    ("no-longer-sep", SS + r"\s*[^.?!]{0," + str(MAXG) + r"}\bno\s+longer\b[^.;:?!]{0," + str(MAXG) + r"}"
     r"[.;:?!]\s*(?:it|they|this|that)\s+(?:is|are|was|were)\b(?!\s+not\b)"),
    # 6) "not just ... . It/They ..."
    ("not-just-sep", SS + r"\s*" + Q + r"?"
     + PRON + r"\b(?:'s|'re|\s+(?:is|are|was|were))?\s+not\s+just\b[^.?!]{0," + str(MAXG) + r"}[.?!]\s*" + Q + r"?"
     + PRON + r"\b(?:'s|'re|\s+(?:is|are|was|were))\b(?!\s+not\b)"),
    # 7) cross-sentence same verb: "didn't V. It V..."
    ("not-period-sameverb", SS + r"[^.?!]*?\b(?:do|does|did)n't\b\s+"
     r"(?:(?:\w+\s+){0,2})([a-z]{3,})\b[^.?!]*[.?!]\s*"
     + PRON + r"\s+\1(?:ed|es|s|ing)?\b"),
    # 8) simple BE: "... isn't ... . It's ..." with reporter-frame guard
    ("simple-be-not-it-be", SS + r"\s*" + Q + r"?"
     r"(?!he\b|she\b|i\b|you\b|we\b)"
     r"(?![^.?!]{0,80}\b(?:knew|know|thought|think|said|says|told|heard|learned)\b[^.?!]{0,40}?\bthat\b)"
     r"[^.?!]{0," + str(MAXG) + r"}?\b" + BE_NEG + r"\b[^.?!]{0," + str(MAXG) + r"}[.;:?!]\s*"
     + Q + r"?it(?:'s|\s+(?:is|are|was|were))\b"),
    # 9) embedded "not just ... ; It/They ..."
    ("embedded-not-just-sep", SS
     + r"[^.?!]{0,80}?\b(?:(?:it|they)\s+(?:is|are)|(?:it's|they're))\s+not\s+just\b"
     r"[^.?!]{0," + str(MAXG) + r"}[.?!]\s*"
     r"(?:(?:it|they)\s+(?:is|are)|(?:it's|they're))\b"),
    # 10) dialogue-aware "You're not just X," <said Y>. "You're Z."
    ("dialogue-not-just", Q + r"?" + PRON + r"(?:'re|'s|\s+(?:are|is|was|were))\s+not\s+just\b[^\"“”']{0," + str(MAXG) + r"}" + Q + r"?\s*"
     r"(?:[^.?!]{0,80}\b(?:said|asked|whispered|muttered|replied|added|shouted|cried)\b[^.?!]{0,80}[.?!]\s*)?"
     + Q + r"?" + PRON + r"(?:'re|'s|\s+(?:are|is|was|were))\s+[*_~]?[a-z]\w*"),
]

COMPILED = [(name, re.compile(pat, re.I)) for name, pat in STAGE1]

# our own scaffold rules that describe the same construction
OUR_CONTRAST_RULES = {"scaffold-isnt", "scaffold-semicolon", "trailing-not", "negative-parallelism",
                      "not-so-much", "no-longer-but", "reflexive-comparison"}
