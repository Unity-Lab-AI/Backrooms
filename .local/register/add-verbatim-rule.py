import io

p = 'tools/check-doc-conformance.py'
s = io.open(p, encoding='utf-8').read()

# --- the rule ------------------------------------------------------------
helper = '''

# An owner direction as the ledgers quote one: a blockquote holding an italicised quotation.
OWNER_QUOTE = re.compile(r'^>\\s*\\*"(.+?)"\\*\\s*$', re.M | re.S)

# Quotations short enough to be a fragment of a longer one, or a stock phrase, are skipped:
# matching them proves nothing either way.
MIN_QUOTE_CHARS = 25


def owner_quotes(text):
    """Every verbatim owner direction a document quotes."""
    found = []
    for match in OWNER_QUOTE.finditer(text):
        quote = " ".join(match.group(1).split())
        if len(quote) >= MIN_QUOTE_CHARS:
            found.append(quote)
    return found


def check_directions_reached_the_queue(problems):
    """LAW #0, made checkable.

    Owner direction, 2026-09-29, verbatim: *"it seems like sometimes i dont see you record
    the verbatiums and then build them into tasks of the todo prperly"*.

    The owner was right. An audit found **three of seventeen** directions that had been acted
    on and archived in `FINALIZED.md` without ever being written into `TODO.md` as tasks. Each
    was implemented correctly, so nothing was lost -- but the queue was not the record of what
    had been asked for, which is the one job it has.

    A direction quoted in the permanent archive is by definition something that shipped. If it
    never appeared in the working queue, it skipped the queue entirely. That is now a failure.
    """
    archive = os.path.join(REPO, "docs", "FINALIZED.md")
    queue = os.path.join(REPO, "docs", "TODO.md")
    if not (os.path.isfile(archive) and os.path.isfile(queue)):
        return
    archived = owner_quotes(io.open(archive, encoding="utf-8-sig").read())
    queue_text = " ".join(io.open(queue, encoding="utf-8-sig").read().split())
    for quote in archived:
        if quote not in queue_text:
            problems.append("docs/FINALIZED.md quotes an owner direction that never reached "
                            "docs/TODO.md: %r" % (quote[:90] + ("..." if len(quote) > 90 else "")))
'''

anchor = '\ndef main():'
assert anchor in s
s = s.replace(anchor, helper + anchor, 1)

# --- call it -------------------------------------------------------------
old = '''    print("doc-conformance")
    print("  living documents checked : %d" % len(docs))'''
new = '''    check_directions_reached_the_queue(problems)

    print("doc-conformance")
    print("  living documents checked : %d" % len(docs))'''
assert old in s
s = s.replace(old, new, 1)

# --- say so in the header ------------------------------------------------
old = '''5. **`DEFERRED.md` is not described as a live queue.** It is closed, and the standing rule
   is that nothing is ever deferred.'''
new = '''5. **`DEFERRED.md` is not described as a live queue.** It is closed, and the standing rule
   is that nothing is ever deferred.
6. **Every owner direction quoted in `FINALIZED.md` also appears in `TODO.md`.** LAW #0 says
   the owner's exact words go into the queue. An audit on 2026-09-29 found three of seventeen
   directions that had been acted on and archived without ever being written into the queue as
   tasks. Each was implemented correctly, so nothing was lost -- but the queue was not the
   record of what had been asked for, which is the one job it has. A direction in the
   permanent archive is by definition something that shipped; if it never appeared in the
   queue, it skipped the queue.'''
assert old in s
s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('verbatim-reached-the-queue rule added')
