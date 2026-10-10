# -*- coding: utf-8 -*-
"""Close what this batch actually built. Status marker only; evidence appended."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **"so that on the machine tab its shows the different systems with green and red lights of whether complete/active with a next step section showing what to do next  not every step having its own type up of whats next"**',
  'CLOSED 0.12.85-dev. `OperationsGateSteps.cs` is a status board: one row per system with a '
  'coloured light **and** Core’s own checkbox glyph, and **one** next-step line for the whole '
  'tab. Measured by the new `tools/check-operations-density.py`: **356 on-screen words to 58**. '
  'The light is never the only channel — colour alone fails the accessibility brief and the '
  'player’s colourblind setting cannot help a dot that means something by hue, so '
  '`check-display-style.py` permits the two indicator colours in that file by name and '
  '**requires the glyph beside them**.'),

 ('- [ ] **"and things can be shortend and more concise and dirrect  with tools tips would less cluter it making them all concise and accurate"**',
  'CLOSED 0.12.85-dev. Every instruction still exists **in full** — it moved to the row’s '
  'tooltip. *"accurate"* was the binding half: a label that fits by dropping the condition it '
  'describes is worse than the paragraph, so nothing was shortened by deletion. '
  '`proof-starts.py`’s claim was **strengthened** rather than relaxed: it used to assert that a '
  'done row omitted its instruction, and now asserts that **no** row carries one.'),

 ('- [ ] **"and we dont need things like long string corrdinates list in the operations panel thing like that arnet needed only like the !A-01 address code is needed to be displayed to thew player and save able and useable"**',
  'CLOSED 0.12.85-dev. The code itself was never missing — `CoordinateRecord.label` has been '
  '`AI-01`, `AI-02` since the first version, assigned in discovery order so it is short, unique '
  'and stable. **What leaked was the raw id**, in four places, the worst of them putting a '
  'thirty-character internal string on a button and printing the connection id, the coordinate '
  'id and the code on one line. `CoordinateRecord.AddressCode` is now the single thing every '
  'readout asks for; the internal identifiers moved to a row tooltip for diagnosis.'),

 ('- [ ] **"and the closing of natural portals needs to be an option on the gate itself so pawns can close it with like 25 wood to board it up which makes it close its map freeing up a map from being open so others can be explored"**',
  'CLOSED 0.12.85-dev. `Portals/PortalBoardUp.cs` — a command on the door, a colonist who '
  'fetches 25 wood and carries it there, a progress bar, and then `CoordinateRelease.TryRelease` '
  '— the **same** close path the Operations pane uses, asked rather than restated. The release '
  'conditions are re-checked at the end as well as the start, because a crew can walk into the '
  'place while the boards are being carried across the map, and closing a map with somebody '
  'inside is the one outcome this must never produce. The wood is spent **after** the place '
  'actually closes. One way only, per the standing *"u just can not re open them"*.'),

 ('- [ ] **"up to three differnt operational gates"**',
  'CLOSED 0.12.85-dev. `NativeGateBinding.MaximumOperationalGates = 3`, refused at '
  '**designation** rather than at opening — a player who had built a fourth door, wired it and '
  'crewed it before being told would have spent all of that for nothing. Counted across every '
  'loaded map rather than the local one, because *operational* is a property of the branch.'),

 ('- [ ] **"that can call any address"**',
  'CLOSED 0.12.85-dev as a property of what was **not** built: there is no gate-to-place '
  'pairing anywhere, and the cap added above is on gates alone. That is what makes a second and '
  'third gate worth building rather than three copies of one route.'),

 ('- [ ] **"and we need a Random address option not just company requested task and quests at specific xcorrdinates"**',
  'CLOSED 0.12.85-dev. `Portals/PortalRandomDial.cs`, reachable from the gate itself. **Every '
  'coordinate until now arrived because something named it** — a request, a quest, a contract, '
  'or a door somebody walked into; there was no way to decide *"I want to go and look"*. The '
  '**dial** is unpredictable and the **place** is not: the address is composed from a monotonic '
  'index so the seed derives exactly as every other discovery does, and `Rand` is never touched '
  '— dial the same slot twice and it is the same place, reload and it is still there. Depth is '
  'drawn weighted toward the shallow end, to a maximum of six, because dialling a starting crew '
  'into a depth-six space is not an adventure. **It creates an address, not a map**: nothing '
  'generates and no map slot is spent until somebody crosses.'),

 ('- [ ] **"not three address per gate!!!"**',
  'CLOSED 0.12.85-dev as the correction it was. My reading of the original row said *"three '
  'addresses held per gate"* and I had started building a per-gate address cap off it. The wrong '
  'reading is struck in place in the archive rather than deleted.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    end = text.find(NL + "- [", at + 1)
    if end == -1:
        end = text.index(NL + NL, at)
    row = "- [x] " + text[at:end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
