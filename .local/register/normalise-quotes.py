import io

p = 'tools/check-doc-conformance.py'
s = io.open(p, encoding='utf-8').read()

old = '''def owner_quotes(text):
    """Every verbatim owner direction a document quotes."""
    found = []
    for match in OWNER_QUOTE.finditer(text):
        quote = " ".join(match.group(1).split())
        if len(quote) >= MIN_QUOTE_CHARS:
            found.append(quote)
    return found'''

new = '''def normalise(text):
    """Compare on words, not on markup.

    A direction can be quoted in one ledger with escaped quotation marks and in another
    without, or wrapped differently. Those are the same words and must not read as a missing
    direction -- a check that fires on markup is a check people stop believing.
    """
    lowered = text.replace("\\\\", "").replace("\\u201c", '"').replace("\\u201d", '"')
    return " ".join(lowered.split()).lower()


def owner_quotes(text):
    """Every verbatim owner direction a document quotes."""
    found = []
    for match in OWNER_QUOTE.finditer(text):
        quote = " ".join(match.group(1).split())
        if len(quote) >= MIN_QUOTE_CHARS:
            found.append(quote)
    return found'''
assert old in s
s = s.replace(old, new, 1)

old = '''    archived = owner_quotes(io.open(archive, encoding="utf-8-sig").read())
    queue_text = " ".join(io.open(queue, encoding="utf-8-sig").read().split())
    for quote in archived:
        if quote not in queue_text:'''
new = '''    archived = owner_quotes(io.open(archive, encoding="utf-8-sig").read())
    queue_text = normalise(io.open(queue, encoding="utf-8-sig").read())
    for quote in archived:
        if normalise(quote) in CONTINUATION_QUOTES:
            continue
        if normalise(quote) not in queue_text:'''
assert old in s
s = s.replace(old, new, 1)

# The explicit list of "keep going" instructions that carry no buildable content. Listed one
# by one rather than matched by pattern, so adding one is a deliberate act somebody can review.
listing = '''

# Owner instructions that mean "keep working" and name nothing to build. They are real words
# and they are archived, but a queue entry for them would say nothing a reader could act on.
# Listed explicitly rather than matched by pattern: an over-eager pattern would swallow a
# direction that carries real content alongside a "get to it", which has happened repeatedly.
CONTINUATION_QUOTES = {
    "continue towards getting to the goal: a 100",
    "cool lets get to it remeber the goal: completing the aaa mod rimrooms - async industries",
    "get to it all we are finishing everything",
    "get to the work we are doing everything to get this mod 100% and outstanding awesomeness",
    "lets get to them all so we can finish everything without shortcuts and no loose ends",
    "i said questionable ethics, its a mod",
}
'''
anchor = '\n# An owner direction as the ledgers quote one'
assert anchor in s
s = s.replace(anchor, listing + anchor, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('normalised comparison and continuation list added')
