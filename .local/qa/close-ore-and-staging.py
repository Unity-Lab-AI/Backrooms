# -*- coding: utf-8 -*-
"""Close the ore-density row and the staging-order row."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Core's mineable scatter step was not found, so coordinate ore density is a guess.**",
     " -- **MEASURED AND FIXED 0.12.99-dev, AND THE ANSWER IS THAT THE SCAN NEVER WORKED ON ANY "
     "PROFILE.** The row asked why it missed on the owner's 294-mod profile. **It missed nothing: "
     "there is no such def.** Every `GenStepDef` in Core and all five expansions was enumerated out "
     "of the installed game, and the string `ScatterLumpsMineable` appears in **zero def files**. "
     "The class exists in the assembly and is **constructed in code** -- "
     "`GenStep_RocksFromGrid.Generate` makes one, sets `countPer10kCellsRange` from "
     "`GetResourceBlotchesPer10KCellsForMap(map)`, and runs it. **So the stated fallback was used on "
     "every map this mod has ever generated, on a pure-Core install included, and the log line was "
     "never evidence about the mod list.** "
     "**AND NOTHING EVER LOOKED WRONG BECAUSE THE FALLBACK WAS RIGHT BY COINCIDENCE:** ten is also "
     "the default `result` in Core's own function. **A number that is right by accident is still a "
     "number nobody checked**, which is the whole reason this repository measures instead of "
     "remembering. "
     "**The real source is strictly better than the one the row wanted.** "
     "`GetResourceBlotchesPer10KCellsForMap` is public, static, and reads the **tile's hilliness** -- "
     "4 flat, 8 small hills, 11 large hills, 15 mountainous, 16 impassable. So a coordinate now "
     "carries the ore density of the tile it sits under, the way an ordinary map on that tile does, "
     "instead of one flat figure everywhere; the owner's *" + Q + "a bit more than vanilla like 3x "
     "more deposites than a default map" + Q + "* multiplies a real per-tile number at last. "
     "**Guarded rather than trusted**, because a map with no valid world tile throws on `TileInfo` "
     "and **a generation step may never fail** -- the stated fallback stays for exactly that case and "
     "names the exception type when it fires. "
     "**Wiki in the same commit:** the mining row now says three times an ordinary map, and a new "
     "section says which ordinary map -- the tile you are standing on -- because *" + Q + "three "
     "times vanilla" + Q + " is meaningless to a reader who does not know vanilla varies by terrain."),

    ("**The owner launched a build 21 hours older than the one on disk, and the instrument already said so.**",
     " -- **SETTLED 0.12.99-dev in the durable place, which is what the row asked for.** The row's "
     "own conclusion was that this needs an **ordering** rule rather than a new instrument, *" + Q
     + "settled in `PUBLISHING.md` and `NOW.md`" + Q + "*. **`NOW.md` had it and `PUBLISHING.md` did "
     "not -- and NOW.md is a one-record file that is replaced wholesale**, so the rule was living in "
     "the one document guaranteed to lose it. `PUBLISHING.md` now carries it as its own interdiction, "
     "above the cascade: stage after the last build and **before telling the owner anything is "
     "testable**, and `check-package-integrity` must read PASS before a launch report is trusted. "
     "**The instrument was never missing.** Rule 10 reported *" + Q + "THE STAGED COPY IS NOT THIS "
     "BUILD" + Q + "* with nine differing files before that launch and it was read as an "
     "environmental note because the game was open. **It was the warning working**, which is the "
     "part worth writing down: the failure was in how a reader weighed a true report, so the repair "
     "is an ordering and a sentence rather than code. "
     "**And it has been followed every time since**: five commits in this session each staged after "
     "their build, with `check-package-integrity` PASS recorded before any claim that the tree was "
     "testable. `stage-mod.ps1` also refused once, correctly, when a keyed string changed between "
     "the build and the stage -- which is the common case and the whole reason the refusal exists."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:52], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
