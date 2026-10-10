import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""
## Owner directions recorded late, second pass

`check-doc-conformance.py` gained a rule on 2026-09-29 requiring that every owner direction
quoted in `FINALIZED.md` also appear here. It immediately found **seven more** that had been
acted on and archived without ever being written into this queue. Each was implemented, so
nothing was lost - but the queue is supposed to be the record of what was asked for, and for
these it was not.

**Verbatim owner direction:** *"make sure u are using the prep docs and the mod spreadsheet and still thinking critical at how we impliment our mods needs across the mods"*

- [x] **HELD as a standing working rule.** The 294 per-mod reviews under `research/reviews/mods/` and the generated register are read before designing, not after. It has recovered misread owner references and, in 0.9.2-dev, produced the Doors Expanded footprints that matched the requested gate sizes exactly.

**Verbatim owner direction:** *"rememrb we are making a mod that works with the other 274, WE ARE NOT EDITING OTHER PEOPLES MODS!"*

- [x] **HELD absolutely.** No file belonging to another mod is ever modified. Compatibility is reached only through conditional runtime patches that apply nothing when the other mod is absent - the owner confirmed this reading explicitly on 2026-09-29 when asked whether a `PatchOperationFindMod` counts as editing. It does not: their files are never touched.

**Verbatim owner direction:** *"continue the work to finish the mod making sure you are using the mod integration register in what all needs to be done"*

- [x] **HELD as a standing working rule.** The register is consulted for every integration question, and **the HTML is the register**, not the spreadsheet.

**Verbatim owner direction:** *"and we cant have backrooms npc pawns all dying off if a person is slow to explore so something needs to be done about like stat or need freezing until discovered with the fog of war"*

- [x] **BUILT 0.8.5-dev, and it was a real defect in work that was otherwise ready to ship.** Everything placed in a coordinate is a live pawn on a live map, so a survivor three rooms away would **starve before a cautious player ever reached them** - impossible for exactly the player most likely to want the rescue. Fog of war was the right signal and the owner named it: RimWorld already tracks per cell whether the player has seen it, so nothing had to be invented or kept in sync. Needs are topped back up on a bounded sweep rather than frozen, because stopping them ticking needs Harmony and the observable result is identical. **Discovery starts their clock.**

**Verbatim owner direction:** *"yes yes continue and remember the back rooms is random on crack and lsd creepy horror flick"*

- [x] **HELD as the tone contract for generation.** Depth 1 stays the sparse yellow rooms; everything past it grows stranger through the palette bands, the coherence decay and the anomalous archetype weighting, so the wrongness is travelled toward rather than presented at the door.

**Verbatim owner direction:** *"get to it hallways can have furniture and produiction benches too remember things are almost completely fucking werid and crazy odd and scary looking the deeping in the backrooms and higher the gete quality and rtesarch levels and tech and stuff ec t ect"*

- [x] **BUILT 0.8.7-dev, and it corrected a wrong finding of mine.** A bench standing in a corridor had been treated as a gap to constrain; the owner's direction is that it **is** the content. So an archetype's declared family constraint now **lapses in a deranged space** instead of being enforced, and what a coordinate produces rises with research finished and depth reached, never above the archetype's own declared ceiling.

**Verbatim owner direction:** *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed to fit vehicals and the like and bigger creatures"*

- [ ] **The adjacent-door-run fallback.** Binding one gate across a run of adjacent 1x1 Core doors, so 1x3 and 2x3 are reachable without Doors Expanded. **Still open.** The single-door half shipped in 0.9.2-dev, where Core's own `OrnateDoor` turned out to supply 1x2 with no mods at all, and the body-size ladder that makes the sizes mean something shipped in 0.9.4-dev.

"""

anchor = u'\n## Owner directions recorded late\n'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('seven more directions recorded verbatim')
