# -*- coding: utf-8 -*-
"""Prepend the 0.12.97-dev entry. CHANGELOG.md has no BOM and must keep none."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"
HEADING = "# Changelog"

ENTRY = NL.join([
"## 0.12.97-dev - 2026-10-05 - The multiplayer page names the multiplayer mod, and pillars match their room",
"",
"- **OWNER: *\"and how can we have a multiplayer section to the wiki if we dont explain how to Use",
"  Rim Together... i mean thats the multipleyer mod.... u didnt build a whole muliplayer client and",
"  server that i dont know about did you?\"***",
"- **No. Nothing of the sort exists** -- no client, no server, no networking of any kind. But the",
"  point underneath was right and it was **live**: `docs/wiki/multiplayer.md` honestly said what",
"  was not promised and described *\"Each player runs their own company, in their own colony, on",
"  their own map\"* -- **without ever naming RimWorld Together.** A reader landed on a page titled",
"  *Multiplayer*, learned the shape of it, and was told nothing about what software would make any",
"  of it happen. **Describing a shape while withholding the thing that provides it is worse than",
"  having no page.**",
"- **Rewritten from the register rather than from memory.** Row **196, RimWorld Together**,",
"  Workshop `3005289691`, family *\"Multiplayer: separate colonies and shared-world exchange\"*. The",
"  page names it, links it, and explains the model: separate colonies on separate maps, linked by",
"  **offline visits and raids and item and pawn exchange** -- which is exactly why a branch office",
"  fits it, because two players are two companies rather than one company with two managers.",
"- **It records that RimWorld Together needs Harmony and that we do not**, a distinction a reader",
"  will otherwise get backwards. **And that everyone needs the same mod list**, because the",
"  register notes *\"the server does not enforce mod order/settings\"*.",
"- **The denials stay, now correctly attributed.** No shared colony, no shared map, no synchronised",
"  research are **RimWorld Together's own model** and not limits this mod added. Nothing is",
"  announced as tested, per D1, and the untested list is named item by item from the register's own",
"  acceptance evidence: separate starts, an offline visit, a supply or aid exchange, reconnecting",
"  after a drop, and whether anything company-specific transfers at all.",
"",
"### A room's pillars are made of the same thing its walls are, and they were not",
"",
"- **Owner: *\"i think some of that u mentioned is already done.. (walls as pillars)\"*** -- and they",
"  were right. All eight clauses of that row measured as built: the carve changes while the",
"  `Bounds` rect stays, `RoomLayoutPlanner.PillarCells` is the lattice and nowhere else derives it,",
"  spacing comes from `RoofCollapseUtility.RoofMaxSupportDistance` measured at **6.9** from the",
"  installed assembly, depth 1 is a **36-slot grid with rooms about 34 cells across**, and walls are",
"  chosen **per room** past `CoherentDepth` by distance from the spawn hall.",
"- **CHECKING IT FOUND A REAL DEFECT.** The ring around a room was built from the room's own",
"  material while **the pillars standing inside that same room used the level band's** -- stone",
"  walls, wooden columns, in the one room big enough for anybody to notice. A pillar *is* a wall; it",
"  is literally `wallDef`. **Nothing asserted the material, which is exactly how it drifted**: every",
"  claim around it covered *where* the pillars go. Fixed; nothing structural changed because any",
"  wall stuff holds a roof. `plant-coordinate-layout.py` now lands **159 of 159** with a plant that",
"  puts it back.",
"",
"### A proof with thirty-four claims and no plants",
"",
"- **The recorder fold shipped and nobody had ever watched it hold.** `proof-record-book.py` passed",
"  from the day it was written and had **no plant suite at all** -- the condition that makes a proof",
"  decorative, because a claim nobody has seen refuse is indistinguishable from a comment that",
"  agrees with itself.",
"- **`RecorderGap` appeared in no proof at all**, so the fold could have un-folded one site at a",
"  time with no symptom but an expedition that quietly stopped noticing a missing book. Six claims",
"  now cover the four read sites -- two switch cases, the site tick and the request line -- counted",
"  rather than contained, because **a kind handled by one switch and not the other is an",
"  observation that is stored and never surfaces**.",
"- `plant-record-book.py` is new and lands **11 of 11**. Two of its plants were wrong before they",
"  were right: one renamed a declaration while the reference the claim reads lived in another file,",
"  and one aimed at a constant's name when the claim was about refusing on null.",
"- **A third exposed a weak claim.** `QueueLoadout` reads two masses -- the pawn's carried thing and",
"  the item being loaded -- and a claim for bare `GetStatValue(StatDefOf.Mass)` passed while a plant",
"  replaced the item's read with a constant. The claim names the item now.",
"",
"### And two rows that were the same row",
"",
"- **\"A world tile the branch does not hold\" appeared twice**, in two sections, in slightly",
"  different words. Both closed: `ClaimTileAndWalkOut` is the new world object (a Core `Settlement`)",
"  and the generated map (`GetOrGenerateMapUtility.GetOrGenerateMap`), reached from a gizmo the",
"  player clicks, with the map generated and the return gate established **before any pawn is",
"  despawned** so a failure moves nobody. Over the five-map cap it forms a caravan instead, per",
"  *\"anything over 5 maps defaults to caravans\"*.",
"- **A supersession record was holding a checkbox it could never tick** and is archived as the",
"  history it is.",
"- Build 0.12.97-dev, **232 C# files, 103 package files, 0 warnings, 0 errors**. Six rows closed and",
"  archived with `VERBATIM TRANSFER CONFIRMED`; queue **36 open / 20 partial / 38 test / 0",
"  completed**. **No game was launched, and nothing here has been played.**",
"",
])

raw = io.open(PATH, "rb").read()
if raw.startswith(b"\xef\xbb\xbf"):
    print("CHANGELOG.md has a BOM and should not; refusing")
    sys.exit(1)
text = raw.decode("utf-8")
if "0.12.97-dev" in text:
    print("already present; nothing written")
    sys.exit(1)
rest = text[len(HEADING):].lstrip(NL)
io.open(PATH, "wb").write((HEADING + NL + NL + ENTRY + NL + rest).encode("utf-8"))
if io.open(PATH, "rb").read().startswith(b"\xef\xbb\xbf"):
    print("a BOM was added -- ABORT")
    sys.exit(1)
print("prepended %d lines; no BOM added" % ENTRY.count(NL))
