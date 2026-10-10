# -*- coding: utf-8 -*-
"""Repair the word-boundary regexes a bash heredoc turned into backspace bytes.

**USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.** That lesson is recorded in `NOW.md` and I
broke it one rule after writing a rule about absence. The `\\b` in two regexes arrived in the file as
a literal **0x08 backspace**, so `re.search` looked for a control character and the rule failed on
correct code -- a false RED this time, which is the lucky direction.
"""
import io
import sys

PATH = "tools/check-quest-paperwork.py"
BACKSPACE = chr(8)


def main():
    text = io.open(PATH, encoding="utf-8-sig").read()
    if BACKSPACE not in text:
        print("no backspace bytes; nothing to repair")
        return 1
    count = text.count(BACKSPACE)
    # The only place a backspace can have come from is the mangled `\b`, so each one becomes the
    # two characters it was meant to be.
    text = text.replace(BACKSPACE, chr(92) + "b")
    io.open(PATH, "w", encoding="utf-8", newline=chr(10)).write(text)
    print("repaired %d backspace byte(s) into word boundaries" % count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
