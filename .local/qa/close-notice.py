# -*- coding: utf-8 -*-
"""Close the freeze-notice and loading-screen rows. Status marker only."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **"when first loading a new backrooms on gate enter and or using the operations tab machine when finally opening the gate(loading the backrooms)"**',
  'PARTLY CLOSED 0.12.83-dev, and **the Operations pane half is done**: both of its openings — '
  'the laboratory address and a natural doorway — announce before the freeze. '
  '`OperationsPortalNetwork`. **The gate-enter half is genuinely different code and is recorded '
  'rather than claimed**: a pawn walking through is a job tick, and `GateSpinUp` reaches '
  '`EnsureSite` from a tick as well. A tick cannot queue a long event and then carry on, so that '
  'path needs the result chain deferred — the same refactor the row below names.'),

 ('- [ ] **"we need a popup and notice in that portion of the machine gate connection step"**',
  'CLOSED 0.12.83-dev. `Presentation/RimroomsGenerationNotice.cs` — a popup **and** a notice: '
  'the full-screen window before the freeze, and `RR_Generation_FreezeEvent` carried by Core’s '
  'own wait box **through** the freeze, so the message is present in both halves of the pause '
  'rather than only in the one that vanishes.'),

 ('- [ ] **"that pops up befgore the "freeze" of the generation"**',
  'CLOSED 0.12.83-dev, **and this was the whole difficulty.** The earlier finding was right that '
  '`EnsureSite` generates synchronously, so a window added immediately before it draws on the '
  '*next* frame. The answer is not to defer `EnsureSite` — it hands the map back through an '
  '`out` parameter and every caller depends on that — but to move the **work** into '
  '`LongEventHandler.QueueLongEvent`, which is the pattern Core itself uses for settling. That is '
  'legal exactly where nothing waits on a return value, and **a UI button callback is such a '
  'place.** So the pane’s buttons announce, the player dismisses the notice while the game can '
  'still draw, and the generation then runs inside the event.'),

 ('- [ ] **"telling the player "Time has froze due to mass distortions, please wait" but noit that"**',
  'CLOSED 0.12.83-dev. The sense is kept and the words are not: every notice says time has '
  'stopped, that something far larger than this side is the cause, and that waiting is correct. '
  '`proof-menu-slides.py` asserts the phrase *"mass distortions"* is **absent** from the keyed '
  'file, so the placeholder cannot drift back in.'),

 ('- [ ] **"i want u to make a universe of backrooms themed notcie of the pause that is expected"**',
  'CLOSED 0.12.83-dev, and *"expected"* is asserted rather than intended — the proof requires '
  'the words that say so to be present. The company reads *"Async Industries records the interval '
  'as acquisition time and bills it to the client"*; the shop reads *"This happens every time a '
  'door opens onto somewhere new, and it has always finished"*; alone in the dark reads *"Time has '
  'not slowed down. It has stopped. It will start again and you will not have aged a second."*'),

 ('- [ ] **"and propely keep it toned to the experience we are trying to make per scenrio type"**',
  'CLOSED 0.12.83-dev. One keyed string per shipped opening — `RR_AsyncIndustriesStart`, '
  '`RR_FurnitureStoreStart`, `RR_SoloGroupStart` — resolved by `CanTranslate` against the '
  'scenario in `Find.Scenario`, which persists in the save so the tone is right mid-game and not '
  'only at setup. **Resolved by key rather than by a table**, so a scenario added later gets its '
  'own tone by writing the string and touching no code, and anything unauthored falls back to the '
  'generic notice rather than to nothing.'),

 ('- [ ] **"but i dont think we properly did the same for loading screens and the like"**',
  'CLOSED 0.12.83-dev, **and the owner’s instinct was right twice over.** The entry-state waits '
  'now show the art and show it randomly (the index had been pinned to `0` in two places). And '
  'the in-play half, which the earlier finding recorded as unreachable without Harmony, is '
  'answered by owning the surface instead of fighting for Core’s: '
  '`Dialog_RimroomsGenerationNotice` is a frameless full-screen window carrying one of the mod’s '
  'own menu images, drawn from the same list the menu reads. **It is a loading screen with our '
  'art on it, before the longest wait in the mod.**'),

 ('- [ ] **"do it properly"**',
  'CLOSED 0.12.83-dev, and recorded as the instruction it was rather than a sentiment. Not a hook '
  'that happens to fire: the art list moved into one type so the two surfaces cannot drift, the '
  'draw is guarded by `RimroomsWindowState.Clean()` because a leaked zero-alpha colour from any '
  'of 294 other mods would render the whole notice invisible, there is a tone per scenario, and '
  'all of it is held by **8 new claims and 12 new plants** in a suite that did not exist this '
  'morning — the menu art had no plant coverage at all.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:92]))
        problems += 1
        continue
    at = text.index(anchor)
    end = text.find(NL + "- [", at + 1)
    if end == -1:
        end = text.index(NL + NL, at)
    row = text[at:end]
    row = "- [x] " + row[len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
