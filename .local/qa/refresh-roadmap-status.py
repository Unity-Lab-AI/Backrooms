# -*- coding: utf-8 -*-
"""Bring the roadmap's status table back to what the repository actually is.

It read **0.7.1-dev**, 120 C# files and 76 package files while the build was 0.13.0-dev with 254
and 134. Six versions of drift in the one table a reader checks first, which is the documentation
defect this project keeps finding: a dated assertion read as current.

Every figure below was measured in the same session it was written, not carried over.
"""
import io
import sys

PATH = "docs/ROADMAP.md"

REPLACEMENTS = [
    ("| **Development version** | 0.7.1-dev (`About.xml`, csproj), branch "
     "`feature/connected-colony-portals` |",
     "| **Development version** | 0.13.0-dev (`About.xml`, csproj), branch `feature/bug-testing` |"),

    ("| **Master TODO** | 134 items checked, 122 open",
     "| **Master TODO** | 190 items checked, 66 open"),

    ("| **Source** | 120 C# files, 18 namespaces, no Harmony |",
     "| **Source** | 254 C# files, 20 namespaces, no Harmony |"),

    ("| **Package** | 76 allowlisted files, 28 Def XMLs, 2 patches, 26 language files, 16 PNGs |",
     "| **Package** | 134 allowlisted files, 48 Def XMLs, 5 patches, 42 language files, "
     "31 PNGs (12 menu slides, 18 gameplay textures, 1 preview) and 4 WAVs |"),

    ("| **Next unblocked minor** | The player-facing how-to for the gameplay and systems, then "
     "the four area types across a gate |",
     "| **Next unblocked minor** | **None. `TODO.md` is empty** - zero open, zero partial. The 53 "
     "rows that cannot close without a launch moved to `TEST.md` on 2026-10-06 |"),

    ("| **Owner questions open** | 3 (inside-start party size; first-exit fixed vs chosen; "
     "opening duration) |",
     "| **Owner questions open** | 0. Two things wait on the owner rather than on an answer: 14 "
     "rotation drawings, and the Quiet Pursuer's race definition |"),
]


def main():
    text = io.open(PATH, encoding="utf-8-sig").read()
    missed = []
    for old, new in REPLACEMENTS:
        if old not in text:
            missed.append(old[:70])
            continue
        text = text.replace(old, new, 1)
    if missed:
        print("REFUSED: %d row(s) did not match; nothing written" % len(missed))
        for row in missed:
            print("  - %s" % row)
        return 1
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("refreshed %d status row(s) in %s" % (len(REPLACEMENTS), PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
