# -*- coding: utf-8 -*-
"""Refuse a member that carries two <summary> blocks, because half of it is invisible.

Why this exists
---------------
**The published wiki told every reader the free ways through the Backrooms stop at depth 3. They
stop at 6.** Nobody copied that from another page: `NaturalFrontierService.MaximumNaturalDepth`
carried **two consecutive `<summary>` blocks**, the first still arguing for three in full and the
second recording the raise to six, and whoever wrote the page read the first one and wrote it down
correctly.

So this is not a tidiness rule. **A stale doc comment is the upstream of a published lie**, and two
summaries on one member is the shape that hides one: C# keeps one and discards the other, so half
of every pair is invisible to the tooling and fully visible to the next person who reads the file.

A sweep found **23 of them**. Three sampled, three live faults -- one documented an entirely
different field than the one it sat above. Every one was repaired by reuniting the orphan with the
member it described, merging true duplicates, or dropping a block whose every word provably
survived on the correct member.

What it refuses, and why it cannot cry wolf
-------------------------------------------
Exactly one shape: a `/// </summary>` followed, across blank lines only, by a `/// <summary>`.
There is no legitimate reason for that -- a member has one summary, and anything else a member
needs is `<param>`, `<returns>` or `<remarks>`. So the rule has no judgement to get wrong and no
threshold to tune, which is the property a rule needs if people are to keep trusting it.

A class summary followed by a member summary does **not** match, because the class declaration
sits between them.
"""
import io
import os
import sys

NL = chr(10)
SEP = chr(92)
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC = os.path.join(REPO, "src")


def say(line):
    """Print without dying on a console that cannot encode a character in the source."""
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def sources():
    for root, _, names in os.walk(SRC):
        parts = root.split(os.sep)
        if "obj" in parts or "bin" in parts:
            continue
        for name in sorted(names):
            if name.endswith(".cs"):
                yield os.path.join(root, name)


def stacked(path):
    """Every line number where one member's doc comment opens `<summary>` more than once.

    **Counted per contiguous doc block rather than by matching a closing tag against an opening
    one**, because the first version of this rule did the latter and a plant walked straight
    through it: `/// <summary>one-line</summary>` twice over is the same fault and never produces a
    line that is exactly `/// </summary>`. Both forms are in this codebase.

    A doc block is the run of `///` lines directly above a member, blank lines allowed inside it.
    Two openings in one run is the fault, whatever shape they take.
    """
    lines = io.open(path, encoding="utf-8-sig").read().split(NL)
    found = []
    index = 0
    while index < len(lines):
        if not lines[index].strip().startswith("///"):
            index += 1
            continue
        start = index
        openings = 0
        while index < len(lines):
            stripped = lines[index].strip()
            if stripped.startswith("///"):
                openings += stripped.count("<summary>")
                index += 1
                continue
            if stripped == "" and index + 1 < len(lines) \
                    and lines[index + 1].strip().startswith("///"):
                index += 1
                continue
            break
        if openings > 1:
            found.append((start + 1, openings))
    return found, len(lines)


def main():
    problems = []
    files = 0
    scanned = 0
    summaries = 0
    for path in sources():
        files += 1
        hits, count = stacked(path)
        scanned += count
        text = io.open(path, encoding="utf-8-sig").read()
        summaries += text.count("/// <summary>")
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for line, openings in hits:
            problems.append("%s:%d opens <summary> %d times for one member. C# keeps one and "
                            "discards the rest, so the others are invisible to tooling and fully "
                            "visible to the next person who reads the file -- which is how the "
                            "wiki came to publish a superseded depth cap."
                            % (rel, line, openings))

    say("doc-comments")
    say("  source files scanned     : %d" % files)
    say("  lines scanned            : %d" % scanned)
    say("  summary blocks           : %d" % summaries)
    say("  rule                     : a member has ONE <summary>; use <param>, <returns> or")
    say("                             <remarks> for anything else. No threshold, no judgement.")
    say("")
    if problems:
        say("FAIL: %d member(s) carry a doubled summary" % len(problems))
        for problem in problems:
            say("  - %s" % problem)
        say("")
        say("      Reunite the orphan with the member it describes, merge a true duplicate, or")
        say("      drop a block only once its every word provably survives elsewhere.")
        return 1
    say("PASS: every documented member carries exactly one summary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
