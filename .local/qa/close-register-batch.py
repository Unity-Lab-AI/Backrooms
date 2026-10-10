# -*- coding: utf-8 -*-
"""Close what this batch built. Evidence on the row's own line, nothing past it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 # ===================================================== the register, applied to people and events
 ('- [ ] **"ie events random spanwns"**',
  'CLOSED 0.12.88-dev, both halves. **Spawns:** all twelve inhabitant families now carry a '
  '`tellKey` — one exact wrong detail, read off the pawn itself for as long as the pawn exists, '
  'and `ConfigErrors` refuses a family without one. **Events:** all eight record a trace in the '
  'coordinate through the clue mechanism a room’s furniture already uses, so it appears in '
  'the Atlas, on the map and in the save. '
  '**A LETTER IS NOT A TELL, which is the defect both halves shared.** The letters this package '
  'writes are good — the echo’s reads *"{0} is standing in this space, wearing what they '
  'were wearing this morning. {0} is also at home right now"* — but they fire once and scroll '
  'away, and then the pawn was just a pawn and the event had never happened. '
  '`THREAT_DESIGN_SHEETS.md` asks for *"a visible or otherwise accessible warning"* **and** *"a '
  'recorded outcome"*, and forbids colour or sound as the only cue; a notification in the '
  'history is none of those. The trace is written **before** the letter’s early return, so '
  'an event with no letter key still leaves a record — a plant corrected that claim, which first '
  'compared positions against the send and let a fault slip between the two.'),

 ('- [ ] **"enemies, allies, nuetrals"**',
  'CLOSED 0.12.88-dev. **Ally is the relation that did not exist.** `RR_Inhabitant_Helper` is '
  'somebody who has been down there long enough to know the place, takes the crew’s side '
  'against what else is in it, and **will not leave with them**. The help is real and it is '
  'Core’s: an existing non-hostile humanlike faction and `LordJob_DefendPoint`, so they '
  'fight the psychotic families with ordinary AI — no bespoke assistance behaviour, and nothing '
  'anywhere near a gate, because `PortalTraversalPolicy` is still the only chokepoint and an '
  'inhabitant still never decides anything about one. A new faction would have been exactly the '
  '*"new type of np0c"* the same owner message forbids. '
  '**And an ally is the most unnerving of the three, not the friendliest** — a thing that '
  'attacks you is explicable. `ConfigErrors` refuses `friendly` on any family that is not a '
  'Helper, and refuses friendly-and-hostile together, for the same reason the hostile flag is '
  'checked rather than assumed.'),

 ('- [ ] **"even all the crazy things ive mentioned in the past"**',
  'CLOSED 0.12.88-dev as the gathering it asked for. Twelve of the owner’s own lines are '
  'quoted in a table in the queue with where each one bears — *"its suppose to be a lsd trip"*, '
  '*"i want you to expand and expound on everything in a lsd way"*, *"not just room shape echoes '
  'but echos of thier inhabitance in weird ways"*, *"even wild waky carzxzy creepy things when u '
  'add places and events"*, *"zero weird events or people"*, and the rest. **Not cited — quoted**, '
  'because the direction’s own words were *"even all the crazy things ive mentioned in the '
  'past"* and a reference to a commit is not a gathering.'),

 ('- [ ] **"and anything u can find in the many many prep docs on the Backrooms Universe"**',
  'CLOSED 0.12.88-dev, and **the prep documents turned out to hold the mechanism, not just '
  'atmosphere.** `docs/UNIVERSE_ADAPTATION.md` line 21, written before any of this code existed: '
  '*"Ordinary industrial interiors become uncanny through exact changes ... a shifted doorway, '
  'impossible adjacency, repeated hall, changed room dimensions, or a feature that has moved '
  'since the last visit."* '
  '**The uncanny is one exact change to something ordinary**, which is a testable property '
  'rather than a mood — and that is why the generator’s floors already read while no '
  'encounter did. `proof-unnerving-register.py` turns it into a gate: **no tell and no event '
  'trace may contain a mood adjective** (eerie, creepy, unsettling, strange, weird, sinister, '
  'ominous, uncanny, disturbing, horrifying, terrifying). The lights going out is not uncanny; '
  'the switches being found already off is. `THREAT_DESIGN_SHEETS.md` supplied the fairness '
  'frame and `CAMPAIGN_CONTENT_CATALOG.md` the breadth map. **That one claim could not have been '
  'written without reading the file**, and it is the single most useful thing in this batch.'),

 ('- [ ] **"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"**',
  'CLOSED 0.12.88-dev, and the row’s own note from last batch said exactly what was '
  'missing: *"Ally does not exist"* and *"wild animals also only reach the player through the '
  'chaser"*. Both landed. `RR_Inhabitant_Helper` is the ally; `RR_Inhabitant_FaunaDomestic` and '
  '`_FaunaWild` are animals you **find**, unfactioned and in no mental state, because the '
  'unnerving part is not that one is dangerous — it is that it is in here and something had to '
  'bring it. Named from Core kinds with a fallback chain, and a family is skipped rather than '
  'substituted when none resolves. The comp that carries a tell had to be patched onto Core’s '
  '`AnimalThingBase` for an animal to say anything at all; the limit is recorded in the patch — '
  'a mod animal that does not inherit it reads its tell in the letter instead.'),

 # ===================================================== the event with a person in it
 ('- [~] Add repeated missing-person mysteries with radio fragments, missing crews, delayed return, witness conflict, reappearance/death, rescue, and case closure.',
  'CLOSED 0.12.88-dev. The one item this row had left open was **radio fragments**, and it is '
  'now `RR_Anomaly_RadioFragment`. **All seven events before it were environmental** — lights, '
  'cold, damp, moved objects, a noise — and not one had a person in it, while three of the '
  'owner’s own named examples are people. '
  '**What makes it worth shipping is whose voice it is.** A fragment from nobody is atmosphere; '
  'this one names a colonist who is **standing in the base right now**, falling back to the '
  'lost-pawn register, and with neither there is no fragment at all. That is the owner’s '
  '*"echos of thier inhabitance in weird ways"* and the same move the `Echo` family makes: the '
  'uncanniness is the recognition. '
  '**And mentioning somebody must not resolve them.** `TakeLostPawnName` *removes* what it '
  'returns — correct for a coordinate placing a missing person, who has now been found, and '
  'wrong for anything that merely names one. A non-destructive `LostPawnNames()` was added and a '
  'plant proves the destructive version fails. The voice is derived off the coordinate seed and '
  'opening count, never `Rand`, and the roster is sorted before the draw indexes it.'),

 # ===================================================== the pursuer decision unblocked two rows
 ('- [~] Replace custom creature presentation, room fixtures and terrain with existing native/provider content, retaining learned rules, encounters, procedural variation and saved routes.',
  'CLOSED 0.12.88-dev. The row’s only open item was *"`RR_QuietPursuer` presentation, the '
  'last one"* — and it closed at 0.12.87-dev by the presentation ceasing to exist. Owner: '
  '*"things that chase you are just npc pawns and wild animals and shit of the gasme ... not '
  'some blob figure, just normal core mechanics"*. A chaser is an ordinary `Pawn` of a Core '
  '`PawnKindDef` drawn by `PawnGenerator`, so there is no custom creature presentation left to '
  'replace: the def is retired, `Thing_QuietPursuer.cs` is deleted, and `proof-chaser.py` '
  'asserts both are gone rather than merely unused.'),

 ('- [~] Replace the historical custom gameplay items, benches, terrain, sprites and audio with source-verified existing Core/profile content and saved role bindings; preserve the gate, field gear, evidence, threat and discovery functions.',
  'CLOSED 0.12.88-dev, **and the row was stale — measured rather than assumed.** It said *"'
  'fourteen historical gameplay PNGs still in the package allowlist; they come out once the last '
  'references go, which is gated on the `RR_QuietPursuer` decision"*. Audited the shipped tree: '
  'it holds **thirteen** image files and every one of them is accounted for — **twelve menu '
  'slides**, which are the owner’s approved visual exception, and `About/Preview.png`. '
  '**There is no gameplay art in the package at all, and no audio**: the `Sounds` tree held one '
  'empty folder and zero files, and that folder has been removed so the absence reads off the '
  'tree rather than off a document. The gate this row named is also resolved — the pursuer draws '
  'nothing now, because it is a Core pawn.'),
]

NOTES = [
 ('- [ ] **"remember lsd unnerving feeling with all things"**',
  'MECHANISM BUILT AND ENFORCED 0.12.88-dev; **the row stays open because only a launch judges a '
  'feeling.** What exists now: a `tellKey` on all twelve inhabitant families and a `traceKey` on '
  'all eight events, both refused at load if absent, both read off the thing rather than out of '
  'a notification, and both held to *one exact wrong fact, never a mood adjective* by '
  '`proof-unnerving-register.py` — the rule taken straight out of `UNIVERSE_ADAPTATION.md`. '
  '`plant-unnerving-register.py` is **32 of 32**. '
  '**What it does not cover yet**, named rather than implied: loot and equipment carry no tell of '
  'their own, the room clue texts are still instructional rather than uncanny (deliberately — '
  'they teach the vertical slice and rewriting them would remove teaching the owner valued), and '
  '*"all things"* is open-ended by construction. This is an acceptance row like *"its suppose to '
  'be a lsd trip"* and it closes when the owner plays it, not when a checker passes.'),
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
    line_end = text.index(NL, at)
    marker = "- [~] " if anchor.startswith("- [~]") else "- [ ] "
    row = "- [x] " + text[at:line_end][len(marker):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]

for anchor, note in NOTES:
    found = text.count(anchor)
    if found != 1:
        print("NOTE ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    text = text[:line_end] + " — **" + note + "**" + text[line_end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows, noted %d partial" % (len(CLOSED), len(NOTES)))
