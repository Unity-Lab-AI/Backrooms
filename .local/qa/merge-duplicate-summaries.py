# -*- coding: utf-8 -*-
"""Fold two <summary> blocks that describe the SAME member into one, losing no sentence.

Where both halves of a stacked pair are about the member below them, the repair is a merge rather
than a move: the junction `/// </summary>` + `/// <summary>` becomes a single `///` separator, so
one block carries both bodies in order and **not a word is dropped**.

Anchored on the first line of the second block, which is unique, so a merge cannot land on the
wrong pair.
"""
import io
import sys

NL = chr(10)

MERGES = [
    ("src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs",
     "Carve the coordinate and return the cells along its corridor walls"),
    ("src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs",
     "Carve the routes between rooms, **as rooms**, and report the cells along their walls"),
    ("src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs",
     "Solid rock everywhere a room or corridor is not"),
]


def main():
    failures = 0
    for path, second_opening in MERGES:
        lines = io.open(path, encoding="utf-8-sig").read().split(NL)
        hits = [i for i, l in enumerate(lines)
                if second_opening in l and l.strip().startswith("///")]
        if len(hits) != 1:
            print("REFUSED  %-60s matched %d" % (second_opening[:58], len(hits)))
            failures += 1
            continue
        at = hits[0]
        # The `/// <summary>` immediately above it, and the `/// </summary>` immediately above that.
        if lines[at - 1].strip() != "/// <summary>" or lines[at - 2].strip() != "/// </summary>":
            print("REFUSED  %-60s not a stacked junction" % second_opening[:58])
            failures += 1
            continue
        indent = lines[at - 1][:len(lines[at - 1]) - len(lines[at - 1].lstrip())]
        out = lines[:at - 2] + [indent + "///"] + lines[at:]
        io.open(path, "w", encoding="utf-8-sig", newline=NL).write(NL.join(out))
        print("merged  %s" % second_opening[:66])
    print("")
    print("%d merged, %d refused" % (len(MERGES) - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
