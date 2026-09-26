"""the rule table, ported from check_tells.sh with labels and fix hints unchanged.

each block rule: id, layer, severity, label, fix, pattern, flags, scope.
scope 'block' runs on every unwrapped block of the cleaned text (tables
included, as the script did). scope 'prose' runs on the prose stream (tables
blanked). scope 'heading' runs on heading lines only. document-level rules
live in detect.py because they need counts, not matches.

layers: lexical, structural, grammatical, discourse.
severity: 1 single lexical hit, 2 structural or grammatical construction,
3 document-level habit. the score is the severity-weighted count per 1000
words; the weights are provisional.
"""

import re

I = re.IGNORECASE

# sentence start: beginning of block, or after a sentence terminator and a
# space. the script only knew ". "; ! and ? are added on purpose.
SS = r"(?:^|(?<=[.!?] ))"

# --- banned words -----------------------------------------------------------
# "drive" and "ecosystem" are left off on purpose: pre-LLM technical prose
# uses both constantly ("drive adoption", "device ecosystem"), so they don't
# separate human from generated text.
WORDS = """delve delves delving delved tapestry vibrant realm beacon pivotal
nuanced comprehensive leverage leverages leveraging leveraged harness
harnesses harnessing facilitate facilitates facilitating holistic robust
seamless seamlessly cutting-edge multifaceted poised commendable noteworthy
groundbreaking transformative burgeoning boasts bolster bolstered crucial
foster fosters fostering garner garnered interplay intricate intricacies
meticulous meticulously showcase showcases showcasing testament underscore
underscores underscoring utilize utilizes utilizing elucidate encapsulates
unveil unveils unveiled enduring landscape posture eliminable load-bearing
land lands landed landing
myriad plethora paramount spearhead spearheads spearheading spearheaded
robustness keystone surface surfaces surfacing surfaced ambient
pins pinned pinning bind binds fronts fronted fronting fight fights
fighting cuts backs mint mints minted minting shape shapes shaping toll diurnal honest honestly carries lever levers gates gating gated
embark embarks embarking paradigm journey journeys unlock unlocks
unlocking unlocked empower empowers empowering empowered streamline
streamlines streamlining streamlined cultivate cultivates cultivating rich
navigate navigates navigating
firstly secondly necessitate necessitates necessitating revolutionize
revolutionizes amidst palpable camaraderie solace cacophony nestled renowned
enhance enhances enhancing enhanced emphasizing highlighting resonate
resonates individuals insights valuable ever-evolving""".split()

_WORD_FIX = [
    (r"leverage", "use"),
    (r"utilize", "use"),
    (r"facilitat", "help"),
    (r"comprehensive$", "full, complete"),
    (r"robust$", "solid, reliable"),
    (r"(crucial|pivotal)$", "important, central"),
    (r"boasts$", "has"),
    (r"showcase", "show"),
    (r"underscore", "show, make clear"),
    (r"(landscape|posture|harness)", "fine if literal; banned in the abstract sense"),
    (r"eliminable$", "avoidable, removable"),
    (r"load-bearing$", "fine if literal (structures); as a metaphor say essential, or what depends on it"),
    (r"(land|lands|landed|landing)$", "fine only for things that physically land (aircraft, a plane, a probe); when work lands (a change, a migration, a PR, a fix) that is the tell: say shipped, is live, is in place, went out"),
    (r"keystone$", "say what it enables instead"),
    (r"surface", "fine if physical; for APIs say endpoints/routes, for verbs say appear, show up"),
    (r"ambient$", "fine if literal (light, sound, temperature); for auth name the credential or its absence"),
    (r"(pins|pinned|pinning)$", "fine for versions and dependencies; for constraints say accepts only, fixed to"),
    (r"(bind|binds)$", "fine for sockets and mounts; otherwise say ties, links, includes"),
    (r"front", "for topology say expose, serve through, or put behind"),
    (r"fight", "fine for people; for tech say is a bad match for, works against"),
    (r"cuts$", "fine if literal (scissors, releases); for reductions say lowers, shrinks, saves"),
    (r"backs$", "fine if literal (reversing, backs up); otherwise say is used to support, supports"),
    (r"(mint|mints|minted|minting)$", "fine if literal (currency, condition); for tokens and URLs say created, generated, constructed, issued"),
    (r"(shape|shapes|shaping)$", "fine as a noun or in compounds (request-shaped); as a verb say sets, decides, changes"),
    (r"toll$", "fine for literal road/death tolls; for expense say cost, charge, fee"),
    (r"diurnal$", "say daily, or day-night for the day-vs-night swing"),
    (r"(honest|honestly)$", "honesty is assumed in tech docs; state the limit or cost plainly"),
    (r"carries$", "fine for physical transport; say has, holds, includes, or is used for"),
    (r"(lever|levers)$", "fine for physical levers; name the actual setting or action, or drop it"),
    (r"(gates|gating|gated)$", "as a verb say blocks, must pass before; for criteria say check, requirement"),
    (r"embark", "start"),
    (r"paradigm$", "model, approach"),
    (r"journey", "fine for literal travel; otherwise say the actual process"),
    (r"unlock", "fine for locks; otherwise enable, allow"),
    (r"empower", "let, enable"),
    (r"streamline", "simplify, speed up"),
    (r"cultivate", "fine for crops; otherwise build, develop"),
    (r"rich$", "fine for money and rich text; otherwise full, detailed"),
    (r"(navigate|navigates|navigating)$", "fine for maps and ships; for situations say deal with, work through"),
    (r"(firstly|secondly)$", "first, then; or drop the enumeration"),
    (r"necessitate", "requires, needs"),
    (r"revolutionize", "cut the marketing; say what changes"),
    (r"amidst$", "among, during"),
    (r"(palpable|camaraderie|solace|cacophony|nestled|renowned)$", "rewrite without it"),
    (r"enhance", "improve, or name the change"),
    (r"(emphasizing|highlighting)$", "usually a trailing participial clause; end the sentence at the fact"),
    (r"resonate", "say who agreed and with what"),
    (r"individuals$", "people"),
    (r"insights$", "say what was learned"),
    (r"valuable$", "say what it is worth and to whom"),
    (r"ever-evolving$", "cut it"),
]


def word_fix(w: str) -> str:
    for pat, fix in _WORD_FIX:
        if re.match(pat, w):
            return fix
    return "rewrite without it"


# literal collocations the fix hints above already call out as fine (rich
# text, landing page) but the bare \bword\b match never excluded. a word
# key here suppresses the match when immediately followed by the given
# pattern.
WORD_EXCLUDE_AFTER = {
    "rich": r"text\b",
    "land": r"pages?\b",
    "landing": r"pages?\b",
}


# --- banned phrases ---------------------------------------------------------
PHRASES = [
    ("it's important to note", "cut it; say the thing"),
    ("it is important to note", "cut it; say the thing"),
    ("it's worth noting", "cut it; say the thing"),
    ("it is worth noting", "cut it; say the thing"),
    ("at its core", "cut it"),
    ("this underscores", "this shows"),
    ("a testament to", "cut, or say plainly why it matters"),
    ("i'd be happy to", "cut it"),
    ("great question", "cut it"),
    ("stands as", "is"),
    ("serves as", "is"),
    ("functions as", "is"),
    # copula avoidance (tells.md 7). "features" and "offers" are left off:
    # in human prose they're almost always ordinary noun/verb usage
    # ("language features"), not copula avoidance.
    ("acts as", "is"),
    ("represents a", "is a"),
    ("plays a vital role", "say what it does"),
    ("plays a crucial role", "say what it does"),
    ("plays a pivotal role", "say what it does"),
    ("plays a key role", "say what it does"),
    ("rich history", "cut, or be specific"),
    ("in the heart of", "in"),
    ("diverse array", "name the items or cut"),
    ("valuable insights", "say what was learned"),
    ("key takeaway", "say the point"),
    ("in conclusion", "cut; end on the last point"),
    ("in summary", "cut; end on the last point"),
    # absent from human technical prose; common in model output
    ("the path forward", "say what you'll do next"),
    ("it should be noted", "cut it; say the thing"),
    ("deep dive", "name what you actually examined"),
    ("the bottom line", "say the point"),
    ("defended against", "'protected against', or name the check"),
    ("defends against", "'protects against', or name the check"),
    ("blast radius", "say what actually breaks and how far"),
    ("leans on", "depends on, uses"),
    ("lean on", "depend on, use"),
    ("leaning on", "depending on, using"),
    ("let's dive", "cut the signpost"),
    ("moving forward", "cut, or 'from now on'"),
    ("best-in-class", "cut the marketing"),
    ("game-changing", "cut the marketing"),
    ("generally speaking", "cut the filler hedge"),
    ("to some extent", "cut the filler hedge"),
    ("from a broader perspective", "cut the filler hedge"),
    ("drawn from", "based on, comes from"),
    ("no basis", "say can't decide, or has no way to"),
    ("ties together", "combines, joins"),
    ("same story", "say the shared fact plainly, or works the same way"),
    ("thumb on the scale", "say which way the evidence moved and why"),
    ("on paper", "say what actually differs; drop the paper-vs-practice contrast"),
    ("sit on", "say is/are, runs, or state the actual relation"),
    ("sits on", "say is/are, runs, or state the actual relation"),
    ("sit in", "say is/are, lives in only if literal; state the actual relation"),
    ("sits in", "say is/are, or state the actual relation"),
    ("full register", "the full list"),
    ("tie together", "combine, join"),
    ("tying together", "combining, joining"),
    ("more than just", "state it directly"),
    ("at least as good as", "false precision; say better and when, or say equivalent"),
    ("whether you're", "drop the audience-spanning frame"),
    ("strictly better", "say better, or name the actual condition"),
    ("shed light on", "show, explain, measure"),
    ("pave the way", "say what it enables"),
    ("bridge the gap", "say what is missing and what fills it"),
    ("deeply rooted", "say where it comes from"),
    ("indelible mark", "cut it"),
    ("despite these challenges", "cut the frame; state the open problems"),
    ("no discussion would be complete", "cut it"),
    ("actionable insights", "say what to do"),
    ("align with", "match, follow, agree with"),
    ("aims to", "say what it does, or who intends what"),
    ("in essence", "cut it"),
    ("when it comes to", "cut it; name the subject"),
    ("one of the most", "name the rank or drop the superlative"),
    # vague attribution (tells.md 4): sourcing a claim to nobody.
    ("industry reports suggest", "name the report, or cut the claim"),
    ("experts agree", "name who, or cut the claim"),
    ("studies show", "cite the study, or cut the claim"),
    ("it is widely", "say who holds the view, or cut the hedge"),
    ("many believe", "say who, or cut the claim"),
    ("research indicates", "cite the research, or cut the claim"),
    ("according to some", "name the source, or cut it"),
    # canned notability (tells.md 6): where it was mentioned instead of what
    # it does.
    ("featured in", "say what it does instead of where it was mentioned"),
    ("profiled by", "say what it does instead of where it was mentioned"),
    ("recognized as", "say what it does instead of the label"),
    ("has been cited by", "say what it does instead of where it was mentioned"),
    # chatbot residue / sycophancy / cutoff / placeholders (tells.md 28,
    # 30-32).
    ("i hope this helps", "cut it"),
    ("would you like me to", "cut it; state what you did or will do"),
    ("certainly!", "cut it"),
    ("you're absolutely right", "cut it"),
    ("as of my last update", "cut it; say what's currently true"),
    ("[your name]", "fill in the real value or delete the placeholder"),
    ("[insert", "fill in the real value or delete the placeholder"),
    # both-sidesing (checklist "commits to something"). absent from human
    # technical prose.
    ("both approaches have", "say which one you picked and why"),
    ("there are trade-offs", "name the actual trade-off, or commit"),
    ("it depends", "say what it depends on, or commit"),
    ("on the one hand", "cut the frame; state the position"),
    ("each has its merits", "say which one you picked and why"),
    ("ultimately, the choice", "make the choice; say what you chose"),
]
# "the fact that", "not only" and "state-of-the-art" are left off: all three
# are ordinary formal English that human technical prose uses often, not an
# LLM tell.

# --- pattern rules ----------------------------------------------------------
# (id, layer, severity, label, fix, pattern, flags, scope)
EMOJI = r"[\U0001F000-\U0001FFFF]"

PATTERNS = [
    # punctuation and formatting
    ("em-dash", "structural", 1, "em dash", "hyphen, comma, or two sentences", "—", 0, "block"),
    ("en-dash", "structural", 1, "en dash used as punctuation", "hyphen, comma, or two sentences", "–", 0, "block"),
    ("spaced-hyphen", "structural", 1, "spaced hyphen used as a dash", "comma, colon, or two sentences", r"[a-zA-Z,)] +- +[a-zA-Z(]", 0, "block"),
    # double-hyphen: symmetric spacing only, so a bare CLI flag in prose
    # ("run it with --json") isn't read as a dash.
    ("double-hyphen", "structural", 1, "double hyphen used as a dash", "comma, colon, or two sentences", r"[a-zA-Z,)](?: -- |--)[a-zA-Z(]", 0, "block"),
    ("arrow", "structural", 1, "arrow in prose", "write the chain as a sentence, or put it in a code block", "→", 0, "block"),
    ("arrow-other", "structural", 1, "arrow in prose", "write it as words: becomes, leads to, up, down", "[⇒⟶↑↓↔]", 0, "block"),
    ("emoji", "structural", 1, "emoji", "delete it (Slack register: at most one, deliberately)", EMOJI, 0, "block"),
    ("emoji-symbol", "structural", 1, "emoji symbol", "delete it (Slack register: at most one, deliberately)", "[✅❌⚠]", 0, "block"),
    ("transition-tic", "structural", 2, "transition tic", "cut it; start with the point", SS + r"(Concretely|Specifically|In essence|In practice|Fundamentally|Essentially)[:,]", 0, "block"),
    ("curly-quote", "structural", 1, "curly quote", "straight quotes", "[“”‘’]", 0, "block"),
    ("bold-label", "structural", 2, "bold label", "make it prose or a real heading", r"\*\*[^*]+:\*\*", 0, "block"),
    ("bold-inline", "structural", 2, "bold inside a sentence", "let the sentence carry it", r"[a-zA-Z,;] +\*\*[^*]+\*\*", 0, "block"),
    ("data-parens", "structural", 2, "data in parentheses", "weave it in, or give it its own sentence", r"\([^)]*[0-9][^)]*\)", 0, "block"),
    ("negative-parallelism", "structural", 2, "negative parallelism", "state it directly", r"not (just|only|merely) [^.]{0,80}but", I, "block"),
    ("to-front", "lexical", 1, "phrase 'to front'", "expose, serve through, or put behind", r"\bto front\b", I, "block"),
    # contrast scaffolds and foils. see tells.md 8, 8c
    ("scaffold-isnt", "structural", 2, "contrast scaffold ('isn't X, it's Y')", "state the positive claim; drop the negated half", r"\b(is|are|was|were)n.t (just |only )?(a |an |the )?[^,.;:]{1,45}[,;] (it.s|it is|they.re|they are|that.s|that is|this is)", I, "block"),
    ("scaffold-semicolon", "structural", 2, "contrast scaffold ('X; it doesn't Y')", "state the positive claim; drop the negated half", r"; (it|they|this|that) (do|does|is|are|was|were|won|can|did|could)n.t", I, "block"),
    ("trailing-not", "structural", 2, "trailing 'X, not Y' contrast", "state the positive claim once; cut the negated foil", r", not (a |an |the |how |what |when |whether |because |just |every |for )", I, "block"),
    ("rather-than", "structural", 2, "manufactured foil ('X rather than Y')", "keep only if Y was genuinely on the table; otherwise state X alone", r"\brather than\b", I, "block"),
    ("as-opposed-to", "structural", 2, "manufactured foil ('as opposed to Y')", "state the positive claim; cut the foil", r"\bas opposed to\b", I, "block"),
    ("appositive-heading", "structural", 2, "appositive heading", "name the subject plainly; if the second half matters, give it a verb", r"^#{1,6} [^,.:!?]{2,44}, [^,.:!?]{2,44}$", 0, "heading"),
    ("not-so-much", "structural", 2, "manufactured foil ('not so much X as Y')", "say what it is", r"\bnot so much [^.;]{1,60} as\b", I, "block"),
    ("no-longer-but", "structural", 2, "manufactured foil ('no longer X but Y')", "say what it is now", r"\bno longer [^.;]{1,50} but\b", I, "block"),
    ("reflexive-comparison", "structural", 2, "manufactured foil (reflexive comparison)", "describe the thing itself", r"\b(reads|feels|looks|sounds|comes across|behaves) (as|like) [^.;]{1,50} (instead of|not as)\b", I, "block"),
    ("self-restatement", "discourse", 2, "self-restatement marker", "say it once, in the better version", r"\b(in other words|put another way|to put it another way|that is to say|which is to say|or rather,)\b", I, "block"),
    ("aphoristic-echo", "structural", 2, "aphoristic echo sentence", "cut it, or merge the point into the previous sentence", r"\. That (takes|is|was|does|means) [a-z']+\.", 0, "block"),
    ("formulaic-transition", "structural", 2, "formulaic transition", "cut it, or use a plain link", SS + r"(Additionally|Moreover|Furthermore),", 0, "block"),
    ("tilde", "lexical", 1, "tilde approximation", "'about' or the plain number", r"~[0-9]", 0, "block"),
    ("cliche-header", "structural", 2, "cliche header", "specific title or no header", r"^#{1,6} +(overview|key takeaways?|next steps|what changed|conclusion|final thoughts|(challenges and )?future outlook|key statistics|introduction)\s*$", I, "heading"),
    ("how-we-header", "structural", 2, "how-we header", "name the actual content; specific title or no header", r"^#{1,6} +(how (we|i)|the (road|journey) to)\b", I, "heading"),
    ("date-in-prose", "structural", 1, "date in prose", "drop the date; state the fact or link the ticket", r"\b(19|20)[0-9]{2}-[0-1][0-9]-[0-3][0-9]\b", 0, "block"),
    # a ticket reads as its id, with the url in the link target: [TIK-1234](url)
    ("ticket-url", "structural", 2, "ticket link shown as a url", "show only the ticket id and put the url in the link: [TIK-1234](url)", r"https?://[^\s)\]]*(/browse/[A-Z][A-Z0-9]+-[0-9]+|/issues?/[A-Za-z0-9-]+|/pull/[0-9]+|selectedIssue=[A-Z][A-Z0-9]+-[0-9]+)", 0, "block"),
    ("schedule-date", "structural", 1, "schedule date in prose", "express it as a gate or milestone, not a calendar date", r"\b20[0-9]{2}[ -](Q[1-4]|H[12])\b|\b(Q[1-4]|H[12]) 20[0-9]{2}\b", 0, "block"),
    ("status-tag", "structural", 1, "status tag in prose", "drop it; status goes stale, link the ticket instead", r"\[(RELEASED|DONE|BACKLOG|IN PROGRESS|DECLINED|CLOSED|RESOLVED|TODO|WIP)\]", 0, "block"),
    ("status-parens", "structural", 1, "status label in parens", "drop it; status goes stale, link the ticket instead", r"\((released|in progress|backlog|declined)\)", I, "block"),
    ("count-appositive", "structural", 2, "count-appositive enumeration", "verbless count list; give it a subject and a verb", r"(one|two|three|four) [a-z][a-z -]*, (one|two|three|four) [a-z]", I, "block"),
    ("possessive-carry", "lexical", 1, "possessive 'carry'", "use has/holds/stores/records, or rephrase", r"\b(carries|carry|carrying|carried) (a|an|the|no|its|their|this|that|full|empty) ", I, "block"),
    ("in-todays", "structural", 2, "in today's opener", "cut the opener; start with the point", SS + r"In today's", 0, "block"),
    ("labeled-intro", "structural", 2, "labeled-intro sentence ('The x: ...')", "fold the label into the sentence", SS + r"The [a-z][a-z -]{1,30}: ", 0, "block"),
    ("moves-the-line", "lexical", 1, "moves-the-line metaphor", "say what actually changes and by how much", r"mov(e|es|ing) the [a-z-]+ (line|needle)", 0, "block"),
    ("sharp-edge", "lexical", 1, "'sharp edge' metaphor", "name the actual problem", r"\bsharp(est)? edge\b", I, "block"),
    ("hedged-precision", "discourse", 2, "hedged number with false precision", "round to two significant figures, or drop the hedge", r"(about|approximately|roughly|around|nearly|estimated) +([0-9],[0-9][0-9][1-9]|[0-9]{4,}|[0-9]+\.[0-9]{2,})", I, "block"),
    ("over-precise-pct", "discourse", 2, "over-precise percentage", "round it; decimals on a percentage need a denominator over 100", r"[0-9]\.[0-9]{2,} ?(%|percent)", 0, "block"),
    # rhetorical moves
    ("pseudo-cleft", "structural", 2, "pseudo-cleft reveal ('is what X')", "just say what it does", r"\bis what (closes|makes|does|drives|lets|keeps|gives)\b", I, "block"),
    ("self-posed-question", "structural", 2, "self-posed question", "state the answer as a sentence", r"\bthe (result|answer|catch|problem|takeaway|verdict|upshot|payoff|reason)\? ", I, "block"),
    ("false-suspense", "structural", 2, "false-suspense transition", "cut the tease; say the thing", r"here.s (the (thing|kicker|catch|part|rub)|where it gets|why)", I, "block"),
    ("fake-candid", "structural", 2, "fake-candid opener", "cut it; performed candor is its own tell", r"let.s be (real|honest)|to be (honest|real) with you", I, "block"),
    ("reminder-close", "structural", 2, "reminder close", "cut it; the document already said this", SS + r"Remember, ", 0, "block"),
    ("hand-holding", "structural", 2, "pedagogical hand-holding", "explain the mechanism instead of announcing that you will", r"\b(let.s (break|dive|unpack|explore|walk through|take a (look|closer)))|\bthink of (it|this) as\b", I, "block"),
    ("scene-setting", "structural", 2, "scene-setting opener", "cut the opener; start with the point", SS + r"(In an era|Imagine a world|Picture this|In a world)", 0, "block"),
    ("invented-persona", "structural", 2, "invented persona", "use a real case from the source material, or cut the example", SS + r"(Imagine|Consider|Meet) [A-Z][a-z]+, an? ", 0, "block"),
    ("quietly", "lexical", 1, "'quietly' insight claim", "say who did what, with evidence", r"\bquietly (becoming|reshaping|transforming|building|running|winning|doing)", I, "block"),
    ("unquantified-intensifier", "discourse", 2, "unquantified intensifier", "give the number, or drop the adverb", r"\b(significantly|dramatically|substantially|greatly|considerably) (improv|reduc|increas|enhanc|boost|speed|slow|lower)", I, "block"),
    # same tell, adverb after the verb instead of before ("dropped
    # significantly"), which the pattern above misses.
    ("unquantified-intensifier", "discourse", 2, "unquantified intensifier", "give the number, or drop the adverb", r"\b(improv\w*|reduc\w*|increas\w*|enhanc\w*|boost\w*|speed\w*|sped|slow\w*|lower\w*|dropp?\w*|ris(?:e|es|ing|en)|rose|grew|grow\w*|fell|fall\w*|climb\w*|surg\w*|jump\w*|plummet\w*|spik\w*|shrink\w*|shrank|shrunk) (significantly|dramatically|substantially|greatly|considerably)\b", I, "block"),
    ("trailing-participial", "grammatical", 2, "trailing participial clause", "end the sentence at the fact; say the consequence in its own sentence", r", (ensuring|highlighting|underscoring|emphasizing|showcasing|reflecting|demonstrating|signaling|signalling|marking|paving|cementing|solidifying|positioning|reinforcing|illustrating|making it (clear|possible|easier)) ", I, "block"),
    ("formulaic-transition-2", "structural", 2, "formulaic transition", "cut it, or use a plain link", SS + r"(Ultimately|Consequently|Overall|Importantly|Crucially|Remarkably|Interestingly|Notably),", 0, "block"),
    ("model-residue", "lexical", 3, "model residue string", "delete it; this is a citation artifact, not content", r"contentReference|oaicite|turn[0-9]+(search|news|view)[0-9]+|attributableIndex|\[cite: ?[0-9]+\]|grok_render|utm_source=chatgpt", 0, "block"),
    # clause coordination. see tells.md 8e, 8h
    ("hitched-comma", "grammatical", 2, "second fact hitched on by a comma", "split it: the clause after the comma becomes its own sentence", r", (the same [a-z]+ (that|the|it|we|as)|much like|one that|something that|which (means|makes|puts|keeps|leaves|explains|is why|is what|is how)) ", I, "block"),
    ("comma-and-clause", "grammatical", 2, 'second clause joined by ", and"', "two facts in one sentence: split at the comma, or subordinate one with because/so/which", r", (and|but) (the|a|an|it|its|that|this|these|those|they|we|our|he|she|there|no|nobody|nothing|none|every|each|only|one|both|most|some|all|what|where|how|why|ours) ", I, "block"),
    ("hitched-with", "grammatical", 2, 'second fact hitched on with ", with"', 'split it: the clause after ", with" becomes its own sentence', r", with (a|an|the|its|their|our|one|two|three|four|five|six|no|no-one|nothing|each|every|both|all|most|some) [a-z]+ (as|at|on|in|under|over|behind|beside|below|above|from|to|that|which|still|now|just|only|also|being|reading|running|sitting|coming|holding|doing|carrying) ", I, "block"),
    # padding: what a rewrite does when it drops a banned word without
    # saying the thing. single hedging downtoners stay legal; these are
    # throat-clearing and filler, both rare in human technical prose.
    ("throat-clearing", "structural", 2, "throat-clearing preamble", "cut it; say the thing", r"\b(it )?(should|must|might|may|could) (probably |perhaps )?be (noted|mentioned|pointed out) that\b|\b(might|may|could) be worth (mentioning|noting|considering|pointing out)\b|\bit is worth considering\b|\bI (just )?wanted to (take a moment|let (you|everyone|you all|the team|folks) know)\b|\btak(e|ing) a moment to\b", I, "block"),
    ("vague-quantity", "discourse", 1, "vague quantity filler", "name them, give the count, or cut the phrase", r"\bin a number of (ways|places|cases|areas|respects)\b|\bin (most|many|some) of the cases\b", I, "block"),
    ("bare-and-clause", "grammatical", 2, 'second clause joined by a bare "and"', "two facts in one sentence: split at the and, or make one the reason for the other", r" and (you|we|they|it|he|she|there|that|this) (need|needs|have|has|is|are|was|were|will|would|can|could|do|does|did|get|gets|got|read|reads|run|runs|print|prints|pay|pays|take|takes|make|makes|say|says|see|sees|start|starts|stop|stops|come|comes|go|goes|keep|keeps|know|knows|want|wants|use|uses|move|moves|cost|costs|win|wins|lose|loses|hold|holds|stay|stays|end|ends|carry|carries|report|reports|score|scores|finish|finishes|show|shows|mean|means|look|looks|work|works|give|gives|fall|falls|sit|sits|land|lands|open|opens|close|closes|matter|matters|change|changes|explain|explains) ", I, "block"),
]

# quantifier appositive tail is a match with an exclusion, handled specially
QUANT_TAIL = re.compile(r", (both|each|all|neither|either) [a-z]", I)
QUANT_TAIL_EXCLUDE = re.compile(r", (both|each|all|neither|either) of (you|us|them|it|which|whom|these|those|the)\b", I)

# one name per thing: a camelCase/PascalCase identifier (an internal
# lowercase-to-uppercase transition) spelled two ways in the same document.
# case-only variants of ordinary words don't qualify (needs the internal-cap
# shape), which keeps this off heading-vs-body capitalization noise
# ("Read-Only" vs "Read-only").
NAME_VARIANT = re.compile(r"\b[A-Za-z]*[a-z][A-Z][a-zA-Z0-9]*\b")

# sentence-initial fresh bare subjects (recipe step 10): a run of sentences
# each opening "The X ..." / "A X ..." / "An X ...", none threaded back to
# the previous sentence by a pronoun or connective. rare in human prose,
# frequent in model output. fires at 4+ in a row, same cluster-sized bar as
# monotone-rhythm.
FRESH_SUBJECT = re.compile(r"^(the|a|an)\s+[a-z]", I)
FRESH_SUBJECT_BREAK = frozenset(
    "i we it they this that these those he she and but so because since "
    "although though while if unless until when however therefore thus "
    "also then meanwhile instead still yet moreover additionally "
    "furthermore consequently next first second third finally otherwise "
    "nonetheless nevertheless hence accordingly there here".split()
)

# document-level thresholds, copied from the script
OVERUSED_QUALIFIERS = ("deliberately", "plainly", "simply", "relatively")  # 3+
LLM_ADVERBS = ("notably", "particularly", "additionally")  # 2+
# workhorse metaphor density (tells.md 27b): a term drafted to carry every
# instance of a concept. "gate" and "vector" from the catalog's own examples
# are left off: both collide with ordinary engineering usage (release
# gates, feature vectors).
OVERUSED_WORDS = ("canonical", "rides", "wedge", "substrate")  # 2+
HEDGES = ("may", "might", "could", "probably", "likely", "roughly", "seems", "suggests", "generally", "ideally", "usually", "often", "I think", "I suspect")
# hedge-stack: 3+ of these in one sentence is manufactured doubt, not an
# honest hedge. 2 is common in careful human prose ("this could
# probably be cached"); 3+ is rare. number hedges (about, roughly,
# around) are left out: hedged-precision owns those.
HEDGE_STACK = re.compile(r"\b(probably|perhaps|possibly|potentially|arguably|somewhat|fairly|reasonably|relatively|hopefully|maybe|seemingly|presumably|conceivably|slightly|a bit|more or less|to some extent|in some ways|might|may|could|seems?|appears?|likely|generally)\b", I)
FIRST_PERSON = ("I", "we", "our", "us", "I'd", "I'm", "we'll", "we're", "we've")
CONTRAST = re.compile(r"(, not [a-z]|[^a-z]not [a-z ]{1,30}, but |[^a-z]rather than |[^a-z]instead of |[^a-z]as opposed to |[^a-z]not so much )", I)
TRIPLE = re.compile(r"[^\W\d_]+, [^\W\d_]+,? and [^\W\d_]+")

NUMERAL_WORDS = re.compile(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|trillion|half|twice|double|triple)\b", I)
IDENT_LETTER_FIRST = re.compile(r"[A-Za-z]\.?[0-9]+([.-][0-9]+)*")
IDENT_DIGIT_FIRST = re.compile(r"[0-9]+:[0-9]+:[0-9]+|[0-9]+-?(bit|byte|fps|Hz|hz|kHz|khz|p|i|K)")
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
FIGURE = re.compile(r"[0-9]+([,.][0-9]+)*")

# specifics a ticket or status writeup piles into its story: code spans,
# urls, ticket keys, versions, identifiers, figures. link targets don't
# count, since a reader never sees them. a paragraph needs three kinds
# mixed together to fire, which keeps plain number-heavy prose out
# (number-dense-* cover that).
SPECIFICS = [
    re.compile(r"`[^`\n]+`"),
    re.compile(r"https?://\S+"),
    re.compile(r"\b[A-Z][A-Z0-9]{1,9}-[0-9]+\b"),
    re.compile(r"\bv?[0-9]+\.[0-9]+(\.[0-9]+)+\b|\bv[0-9]+(\.[0-9]+)?\b"),
    re.compile(r"\b[a-z]+_[a-z0-9_]+\b|\b[a-z]+[A-Z][A-Za-z0-9]*\b"),
    FIGURE,
]
LINK_TARGET_RAW = re.compile(r"\]\([^)]*\)")
# human technical prose stays under this outside pasted logs and markup
FACT_DENSE_MIN = 8
FACT_DENSE_PER_100W = 25


# --- thresholds from calibrate.py ------------------------------------------
# post-comma participial clauses per 1,000 words: set above the human
# technical prose p95 and below typical model output. nominalizations,
# MATTR and paragraph uniformity did not separate human from generated on
# technical prose and are reported as metrics only.
# what a fix has to touch. a sentence
# rewrite can clear "sentence" findings; "paragraph" needs the whole
# paragraph or list restructured; "document" is a count or rate across the
# whole file, so no single edit clears it. anything not listed is
# "sentence". families (overused:, llm-adverb:) match on the prefix.
FIX_SCOPE = {
    "paragraph": {"monotone-rhythm", "fresh-subjects", "number-dense-sentence", "number-dense-paragraph",
                  "fact-dense-paragraph",
                  "symmetric-bullets", "italic-subtitle", "pr-results-table", "pr-untracked-open-item"},
    "document": {"colon-splice", "semicolon-chain", "authorless", "no-hedges", "flat-rhythm", "dash-budget",
                 "participial-rate", "even-section-weight", "thematic-breaks", "rule-of-three",
                 "contrast-habit", "name-drift", "overused", "llm-adverb", "pr-length", "pr-number-dense"},
}


def fix_scope(rule: str) -> str:
    for scope, ids in FIX_SCOPE.items():
        if rule in ids or rule.split(":")[0] in ids:
            return scope
    return "sentence"


THRESHOLDS = {
    "participial_post_comma_per_1k": 4.0,
    "nominalizations_per_1k": None,
    "mattr": None,
    "paragraph_cv": None,
    "cluster_min_findings": 3,
    # even section weight: human docs with H2 sections vary a lot more
    # than this (p10 around 0.55); 0.3 leaves margin below the most even
    # human document while still catching generated same-length sections.
    "section_weight_cv": 0.3,
}
