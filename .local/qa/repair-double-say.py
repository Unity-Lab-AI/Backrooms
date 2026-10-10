# -*- coding: utf-8 -*-
"""Undo my own patch on the two tools that already had a safe print.

**THE PATCH ASSUMED A PROBLEM THAT TWO OF THE FIVE FILES HAD ALREADY SOLVED.**
`check-queue-pointers.py` and `archive-empty-sections.py` each carried their own `say(line)` whose
body is `print(line)` -- at a line start, with indentation, which is exactly the shape the rewrite
matched. So the rewrite turned each helper into a call to itself and both tools died with
`RecursionError` the first time they printed anything.

Caught by running all five immediately after patching rather than trusting a clean `ast.parse`, which
is the whole reason to run them: **a file that parses is not a file that works.**

The repair is a revert, not a second layer: my inserted helper comes out and the original `print(line)`
goes back, so both files end byte-identical to how they were found.
"""
import io
import sys

NL = chr(10)

TARGETS = ("tools/check-queue-pointers.py", "tools/archive-empty-sections.py")

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
    for target in TARGETS:
        text = io.open(target, encoding="utf-8-sig").read()
        if HELPER not in text:
            print("REFUSED: %s does not hold the inserted helper verbatim" % target)
            return 1
        text = text.replace(HELPER + NL, "", 1)

        # The original helper's own body, restored. Counted, because exactly one self-call was
        # created and a file with two would mean the rewrite had matched something else as well.
        if text.count("        say(line)" + NL) != 1:
            print("REFUSED: %s holds %d self-call(s), expected exactly 1"
                  % (target, text.count("        say(line)" + NL)))
            return 1
        text = text.replace("        say(line)" + NL, "        print(line)" + NL, 1)

        if text.count("def say(") != 1:
            print("REFUSED: %s would end with %d say definition(s)"
                  % (target, text.count("def say(")))
            return 1

        import ast
        ast.parse(text)
        io.open(target, "w", encoding="utf-8", newline=NL).write(text)
        print("reverted %s" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
