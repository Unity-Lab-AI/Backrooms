import io

p = 'tools/check-doc-conformance.py'
s = io.open(p, encoding='utf-8').read()

# --- branch rule: an explicit list of names that WERE real branches -------
old = '''VERSION_CLAIM = re.compile(r"(?:current\\s+(?:development\\s+)?version|development\\s+build)\\D{0,12}"
                           r"(\\d+\\.\\d+\\.\\d+-dev)", re.I)
BRANCH_CLAIM = re.compile(r"feature/[A-Za-z0-9._-]+")'''
new = '''VERSION_CLAIM = re.compile(r"(?:current\\s+(?:development\\s+)?version|development\\s+build)\\D{0,12}"
                           r"(\\d+\\.\\d+\\.\\d+-dev)", re.I)

# Branch names that were genuinely the working branch once and are not now. Matching any
# "feature/..." string instead was tried first and was wrong: it flagged file paths like
# `feature/feature-review.md` and prose like "feature/adapter work". A checker that cries
# wolf is a checker people learn to scroll past, which is worse than not having it.
STALE_BRANCHES = ("feature/preproduction-handoff",)

# Vocabulary that marks a retired def as being DESCRIBED rather than promised. Naming one
# while explaining that it was retired is exactly what a ledger and a roadmap should do.
RETIREMENT_WORDS = re.compile(
    r"\\b(retir|remov|delet|legacy|historical|no longer|former|obsolete|superseded|archiv|was\\s+the)",
    re.I)

# Text that would tell a reader DEFERRED.md is somewhere to put open work.
DEFERRED_CLOSED_WORDS = re.compile(r"(closed|never add|nothing is deferred|zero open)", re.I)'''
assert old in s
s = s.replace(old, new, 1)

# --- apply the refined rules ---------------------------------------------
old = '''        for name in set(BRANCH_CLAIM.findall(text)):
            if branch and name != branch:
                problems.append("%s names working branch %r; the branch is %r" % (rel, name, branch))

        for definition in RETIRED_DEFS:
            if definition in text:
                problems.append("%s names retired def %s as if it still ships" % (rel, definition))'''
new = '''        for name in STALE_BRANCHES:
            if name in text and branch and name != branch:
                problems.append("%s names working branch %r; the branch is %r" % (rel, name, branch))

        # A retired def may be named while explaining that it is retired. It may not be named
        # on a line that reads as a promise, so the line itself has to carry the explanation.
        for number, line in enumerate(text.split("\\n"), start=1):
            for definition in RETIRED_DEFS:
                if definition in line and not RETIREMENT_WORDS.search(line):
                    problems.append("%s:%d names retired def %s with nothing saying it is gone"
                                    % (rel, number, definition))'''
assert old in s
s = s.replace(old, new, 1)

old = '''        if DEFERRED_AS_LIVE.search(text):
            problems.append("%s describes DEFERRED.md as a live queue; it is closed and nothing "
                            "is ever deferred" % rel)'''
new = '''        # Mentioning the file is fine; mentioning it without anywhere saying it is closed is
        # what leaves a reader thinking there is still somewhere to put work.
        if "DEFERRED.md" in text and not DEFERRED_CLOSED_WORDS.search(text):
            problems.append("%s mentions DEFERRED.md without saying anywhere that it is closed"
                            % rel)'''
assert old in s
s = s.replace(old, new, 1)

# The old unused pattern goes with it.
old = '''DEFERRED_AS_LIVE = re.compile(
    r"(add(ing)?\\s+(a\\s+)?(new\\s+)?rows?\\s+to\\s+`?DEFERRED|defer\\s+it\\s+to\\s+`?DEFERRED"
    r"|record(ed)?\\s+in\\s+`?DEFERRED\\.md`?\\s+(as|with)\\s+an?\\s+open)", re.I)

'''
assert old in s
s = s.replace(old, '', 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('doc checker tightened')
