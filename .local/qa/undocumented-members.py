# -*- coding: utf-8 -*-
"""List every method/field declaration in a file and whether a doc comment sits directly above it.

An orphaned <summary> has a member it belongs to. The reliable way to find it is to ask which
members in the same file have no doc comment of their own -- a stacked pair almost always means
one block was separated from its member when something was inserted between them.
"""
import io
import re
import sys

NL = chr(10)
DECL = re.compile(
    r"^\s{4,8}(?:\[[^\]]*\]\s*)?"
    r"(?:public|private|internal|protected)\s[^;{}()]*?(\w+)\s*(?:\(|=|;|\{|=>)")


def main(path):
    lines = io.open(path, encoding="utf-8-sig").read().split(NL)
    for index, line in enumerate(lines):
        match = DECL.match(line)
        if not match:
            continue
        above = index - 1
        while above >= 0 and lines[above].strip() == "":
            above -= 1
        documented = above >= 0 and lines[above].strip() == "/// </summary>"
        print("%-5s %5d  %s" % ("DOC" if documented else "----", index + 1, line.strip()[:92]))


if __name__ == "__main__":
    main(sys.argv[1])
