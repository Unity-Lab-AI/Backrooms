# -*- coding: utf-8 -*-
"""Close the Spatial T6 row, which the owner approved and which needed content first."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Spatial T6, the seventh level, which the owner approved and which needs content first.**",
     " -- **BUILT 0.12.99-dev as `RR_Spatial_DeepFrontier`, AND THE CONTENT WAS AUTHORED RATHER THAN "
     "THE LIMITATION SHIPPED.** "
     "The row offered two answers and said the second was *" + Q + "a stated limitation rather than a "
     "blocker" + Q + "*. **The first cost nothing but authoring, so shipping the limitation would "
     "have been a choice to ship less:** a palette band in this mod is a selection of Core terrain, a "
     "stuff and a colour, which is exactly what the other five are. "
     "**`RR_Palette_Undercroft`, the sixth band** -- the floor has given up and the ground is coming "
     "through. **`Mud` was the obvious floor for it and would have been a defect**, found by measuring "
     "Core rather than by assuming: Mud declares only `Bridgeable` and `WaterproofConduitable` "
     "affordances and a path cost of **14**, so a band floored in it is a level **nothing can be built "
     "on and nobody can cross at speed** -- and it is a level a player FINDS rather than builds, so "
     "they would meet it with no warning. `BrokenAsphalt` carries Light, Medium and Heavy at path cost "
     "0. The band also asks for **no floor tint**, because a colour on terrain that does not expect "
     "one is a silent no-op, which is the exact failure this file already carries a long comment about "
     "from `Named<TerrainDef>(" + Q + "Carpet" + Q + ")` returning null for versions. "
     "**AND THE BAND DERIVATION STOPPED WRAPPING, which fixed a fault that was already shipped.** It "
     "was `% Bands`: at five bands a **depth-six** coordinate came up **Poolrooms** on half its seeds, "
     "so the deepest place a branch could reach wore the second shallowest face in the game, and a "
     "built gate at depth twelve looked like depth two. It saturates now. Depths two to five land on "
     "exactly the bands they always did; every case that changed was a deep space wearing a shallow "
     "face. "
     "**THE RESEARCH HALF RETIRES A RESTRAINT, AND THAT HAD TO BE DONE OUT LOUD.** "
     "`proof-research-tier4.py` asserted *" + Q + "THE NATURAL DEPTH REACH IS NOT RESEARCH-DRIVEN, "
     "WHATEVER ITS VALUE" + Q + "*, and the owner then approved a tier whose entire subject is that "
     "number. **The old claim went on PASSING after the code stopped honouring it** -- it looked for "
     "`HasCapability(...) ? <something>MaximumNaturalDepth` and the new code reads "
     "`? DeepFrontierNaturalDepth : MaximumNaturalDepth`, an identifier that does not end in the name "
     "the pattern wanted. **A green instrument over a dead restraint is worse than no instrument, and "
     "leaving it green because it happened to pass would have been the dishonest move.** It is "
     "restated to what it always protected and still protects: **the reach is bounded, and ONE place "
     "decides it.** "
     "**THREE PLACES READ THE REACH AND ONE OF THEM CARRIED ITS OWN COPY.** "
     "`PortalRandomDial.DeepestBlindDial` was `const int = 6` with a comment saying it matched the "
     "natural cap -- **and a comment is not a derivation.** Left alone it would have shipped a branch "
     "that could walk to depth seven while a blind dial refused to send anybody there and "
     "`SoloGroupHints` still told them six was the end, a hint that **fires once and cannot be taken "
     "back**. All three now go through `NaturalFrontierService.NaturalDepthReach()`, and nothing "
     "outside that file reads the base constant at all. "
     "**Instruments: proof 61 `proof-research-tier6.py` and plant suite 38, 18 of 18 planted faults "
     "caught**, including Mud returning as the floor, the derivation going back to wrapping, and the "
     "dial getting its own six back. **Docs in the same commit:** the chart's tier table and branch "
     "table, the sweep's candidate 6 and its recommendation row, the wiki's band list, look list and "
     "both depth claims in `gates.md`, and two figures struck from `ALTERNATE_START_BRIEFS.md` that "
     "the code had stopped having."),
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
    print("closed %d tier-6 row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
