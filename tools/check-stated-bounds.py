# -*- coding: utf-8 -*-
"""Refuse a numeric cap that can refuse CONTENT and does not say why it exists.

Why this exists
---------------
**Owner, verbatim:** *"so dont limit yourself"*. Where a bound exists it has to be a bound the
geometry imposes **and is stated**, not one chosen for convenience.

The worked example is `MaximumUndirectedEdgesPerRoom`. It was **2**, *"because a slot has four
neighbours"* -- a true reason at the time. Then bent corridors made eight neighbours reachable and
**the constant became the thing refusing them**: the planner could build a richer level and a
number nobody had revisited said no. A cap with its reasoning written down is a cap the next person
can tell has gone stale. A bare `= 2` is indistinguishable from a guess.

Scoped, deliberately, to where a bound can refuse content
---------------------------------------------------------
`Generation/`, `Portals/` and `Gate/` only. A cap in those directories decides what a level may
contain, how far a route may reach, or what may cross -- so a convenient one costs the player
something.

**`ConnectedWork/` is out of scope and that is not laziness.** Its roughly thirty `Maximum*`
constants are per-tick scan windows: bounded rotating windows rather than prefixes, by invariant 5,
and their reason is one shared policy rather than thirty separate judgements. Demanding a comment
on each would add thirty paragraphs saying the same thing, and **a checker that cries wolf is one
people scroll past** -- which is the failure this project has recorded about its own rules twice.

Measured at 0.12.98-dev: 44 caps in scope, 8 of them bare. All eight were given reasons read out
of their own use, and this is what stops the ninth.

Exit status is the result. Run from the repository root.
"""
import io
import os
import re
import sys

NL = chr(10)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
SCOPE = ("Generation", "Portals", "Gate")

# A const of a numeric type whose NAME says it is a bound. Named rather than every numeric const,
# because a tuning value is not a cap and this rule is about caps.
CAP = re.compile(
    r"^\s*(?:internal|public|private|protected)\s+(?:static\s+)?(?:readonly\s+)?const\s+"
    r"(?:int|float|long|double)\s+"
    r"(\w*(?:Max|Min|Maximum|Minimum|Cap|Limit|Budget|Ceiling|Rarity)\w*)\s*=")


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def main():
    total = 0
    bare = []
    for area in SCOPE:
        base = os.path.join(SRC, area)
        if not os.path.isdir(base):
            say("FAILED: %s is not a source area any more; this rule's scope has moved" % area)
            return 1
        for root, _, names in os.walk(base):
            parts = root.split(os.sep)
            if "obj" in parts or "bin" in parts:
                continue
            for name in sorted(names):
                if not name.endswith(".cs"):
                    continue
                path = os.path.join(root, name)
                rel = os.path.relpath(path, REPO).replace(os.sep, "/")
                lines = io.open(path, encoding="utf-8-sig").read().split(NL)
                for index, line in enumerate(lines):
                    match = CAP.match(line)
                    if not match:
                        continue
                    total += 1
                    above = index - 1
                    while above >= 0 and lines[above].strip() == "":
                        above -= 1
                    stated = above >= 0 and (
                        lines[above].strip().endswith("</summary>")
                        or lines[above].strip().startswith("//"))
                    if not stated:
                        bare.append((rel, index + 1, match.group(1)))

    say("stated-bounds")
    say("  scope                : %s" % ", ".join(SCOPE))
    say("  numeric caps in scope: %d" % total)
    say("  with a stated reason : %d" % (total - len(bare)))
    say("  out of scope         : ConnectedWork/ per-tick scan windows -- one shared policy")
    say("                         (invariant 5), not thirty separate judgements")
    say("")
    if total == 0:
        say("FAIL: no caps found in scope at all. An absence rule over an empty set passes by "
            "construction, so this is a failure rather than a clean run.")
        return 1
    if bare:
        say("FAIL: %d cap(s) can refuse content and do not say why" % len(bare))
        for rel, line, name in bare:
            say("  - %s:%d  %s" % (rel, line, name))
        say("")
        say("      Write the reason the bound exists, from what it actually bounds. A cap whose "
            "reasoning is written down is one the next person can tell has gone stale; a bare "
            "number is indistinguishable from a guess.")
        return 1
    say("PASS: every cap that can refuse content states why it exists")
    return 0


if __name__ == "__main__":
    sys.exit(main())
