# -*- coding: utf-8 -*-
"""Teach the queue tools to report on a console that cannot encode a document's own characters.

**AN INSTRUMENT THAT CRASHES WHILE REPORTING CANNOT REPORT.** `archive-finished-todo.py` prints the
title of every section and group it moves, and a heading in `docs/TODO.md` carries whatever the
document carries -- in this case an interdiction sign, which cp1252 cannot encode. The run died at
`print` **after** the reassembly identity had already held, so the operator saw a half-written report
and no way to tell whether the move had happened. It had not, which was luck rather than design.

`check-doc-conformance.py` already learned this exact lesson and fixed it with a replacing print. The
fix is copied rather than reinvented, and it is applied to every queue tool that prints text taken out
of a document instead of only the one that happened to break today.
"""
import io
import re
import sys

NL = chr(10)

TARGETS = (
    "tools/archive-finished-todo.py",
    "tools/verify-archive-move.py",
    "tools/archive-empty-sections.py",
    "tools/check-queue-integrity.py",
    "tools/check-queue-pointers.py",
)

HELPER = '''

def say(line=""):
    """Print a line that may hold characters the console cannot encode.

    **AN INSTRUMENT THAT CRASHES WHILE REPORTING CANNOT REPORT.** These tools print section titles
    and row text straight out of the queue, so they can be handed any character the document holds.
    One heading carrying an interdiction sign killed `archive-finished-todo` at `print`, after the
    reassembly identity had already held -- leaving a half-written report and no statement of whether
    the move had happened.

    Replaced rather than dropped, so the reader still sees where the character was. Same answer
    `check-doc-conformance.say` already carries, for the same reason.
    """
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))

'''


def main():
    patched = 0
    for target in TARGETS:
        text = io.open(target, encoding="utf-8-sig").read()
        if "def say(line=\"\"):" in text:
            print("already patched: %s" % target)
            continue

        # Rewrite call sites only. `print(` at a statement position, never inside a string: every
        # match is anchored to line start plus indentation, which a quoted occurrence never is.
        body, count = re.subn(r"(?m)^(\s*)print\(", r"\1say(", text)
        if count == 0:
            print("no print call sites in %s; refusing to touch it" % target)
            continue

        # The helper goes above the first module-level def or class, so it is defined before use.
        marker = re.search(r"(?m)^(?:def |class )", body)
        if marker is None:
            print("no module-level definition in %s to sit above; refusing" % target)
            return 1
        at = marker.start()
        body = body[:at].rstrip(NL) + NL + HELPER + NL + body[at:]

        import ast
        ast.parse(body)
        io.open(target, "w", encoding="utf-8", newline=NL).write(body)
        print("patched %-40s %d call site(s)" % (target, count))
        patched += 1

    print("")
    print("%d tool(s) patched" % patched)
    return 0


if __name__ == "__main__":
    sys.exit(main())
