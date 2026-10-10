# -*- coding: utf-8 -*-
"""The unnerving register, recorded verbatim with the prep-doc synthesis it asked for.

PRE-WORK GATE, LAW #0. The owner's sentence is a standing constraint on
everything, and it explicitly asks for the earlier directions and the prep
documents to be gathered into it -- *"even all the crazy things ive mentioned in
the past and anything u can find in the many many prep docs"*. So the gathering
is part of the record, not a summary of it: every earlier line below is the
owner's own words, quoted, with where it came from.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

ANCHOR = "### Session direction, 2026-10-04 — this file ends as a template holding nothing"

SECTION = '''### Owner direction — the unnerving register is not a room feature, it is the register everything plays in (2026-10-04)

**Verbatim owner direction (2026-10-04):** *"remember lsd unnerving feeling with all things ie events random spanwns, enemies, allies, nuetrals, even all the crazy things ive mentioned in the past and anything u can find in the many many prep docs on the Backrooms Universe"*

**THE WORD THAT CHANGES THE SCOPE IS *"all things"*.** The LSD direction has been read as an *architecture* direction for eight versions — bent corridors, seven room shapes, roads, neighbourhoods, a per-coordinate motif. All of that is built. **None of it reached a single encounter, spawn or event**, and the owner has now said twice that the register is wider than the walls: *"even wild waky carzxzy creepy things when u add places and events"*, and the complaint that produced it, *"zero weird events or people"*.

**This direction asked to be gathered, so it is gathered here rather than cited.** Every line below is the owner's own, verbatim, with where it was said:

| Owner's words, verbatim | Where it bears |
|---|---|
| *"its suppose to be a lsd trip when it comes to archeteture and shit"* | the original, and the half that is built |
| *"i want you to expand and expound on everything in a lsd way"* | answered at a fork; **"everything"**, not the walls |
| *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"* | the register deepens with depth |
| *"not just room shape echoes but echos of thier inhabitance in weird ways and items and equipment and production benches"* | **the mechanism: who WAS here, read off what they left** |
| *"even wild waky carzxzy creepy things when u add places and events"* | places **and events** |
| *"not enough weird stuff like a room with a lost person or a room full of bodies or suppplies or a labratory ofr class room or hospital of manufactuing room or tool sheed or weapons locker with loot and supplies anssd furnuture"* | named examples, and three of them are **people**, not rooms |
| *"zero weird events or people"* | the complaint, in four words |
| *"with wild random events and layouts and spawns to find and loot!!!!!!"* | events, layouts **and spawns** |
| *"really want the creepy insane looks and feel of the universe"* | the acceptance condition |
| *"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"* | the register scales with depth and band, and must stay survivable |
| *"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"* | the relations this applies across |
| *"and remembner alot of things you should be reviewing the prep materials and registry for especially backroom themed items equip,memntn and questes and logic and game paly and factions and random events and backrooms make ups you should be doing deep dives into the univers's make up of backrroms to properly design all the sustems events and specialities involved with this mod"* | the instruction to do exactly this gathering |

**AND THE PREP DOCUMENTS ALREADY SAY HOW THE FEELING IS PRODUCED, which is the part that was never applied to people.** `docs/UNIVERSE_ADAPTATION.md` line 21, on translating the source: *"Ordinary industrial interiors become uncanny through exact changes ... Use intentional spatial changes such as a shifted doorway, impossible adjacency, repeated hall, changed room dimensions, or a feature that has moved since the last visit."*

**The uncanny is an exact change to something ordinary.** It is not a new monster, a darker palette or a louder sound — the generator already applies that rule to space and it is why the floors read. Applied to an encounter it means: an ordinary RimWorld pawn, in an ordinary RimWorld relation, with **one exact thing wrong about it that the player can read**.

**`docs/THREAT_DESIGN_SHEETS.md` supplies the fairness frame and it binds every row below:** every encounter has *"a visible or otherwise accessible warning, a learnable rule, at least one countermeasure, and a recorded outcome"*; *"Do not use color or sound as the only way to notice a tell"*; first contact *"must not kill a healthy pawn instantly"*; effects are *"bounded, seed-stable, logged against a coordinate, and recoverable after saving and reloading"*. Its own closing section already named this gap — *"The other proposed monstrosities, world-town openings, missing-crew outcomes, infected or altered arrivals, containment escapes, hostile sites ... remain open design work. Do not reuse these two behaviors as a generic random-threat generator."*

- [ ] **"remember lsd unnerving feeling with all things"** — **the standing acceptance condition on every encounter, spawn and event**, in the owner's words. A spawn that is merely a hostile, or merely a neutral, is the thing being complained about. The uncanny is one exact wrong detail on something ordinary, and it must be **readable** — text, never atmosphere alone.
- [ ] **"ie events random spanwns"** — events and spawns, not rooms. `AnomalyEventService` and `InhabitantService` are where this lands.
- [ ] **"enemies, allies, nuetrals"** — **the register applies across all three relations, and an ally is the hardest and the best of them.** Somebody down there who helps is far more unnerving than somebody who attacks, because an attack is explicable. **Ally does not exist yet at all.**
- [ ] **"even all the crazy things ive mentioned in the past"** — the table above is that gathering. Each row is a thing the owner has already asked for and the register has to carry.
- [ ] **"and anything u can find in the many many prep docs on the Backrooms Universe"** — `UNIVERSE_ADAPTATION.md` supplies the mechanism (exact changes to the ordinary), `THREAT_DESIGN_SHEETS.md` the fairness frame, and `CAMPAIGN_CONTENT_CATALOG.md` the breadth map. **The mechanism was the missing piece**, and it was written down before any of this code existed.

'''

text = io.open(TODO, encoding="utf-8").read()

if "the unnerving register is not a room feature" in text:
    print("already recorded")
    sys.exit(0)
if text.count(ANCHOR) != 1:
    print("ANCHOR NOT UNIQUE (%d); nothing written" % text.count(ANCHOR))
    sys.exit(1)

io.open(TODO, "w", encoding="utf-8", newline=NL).write(text.replace(ANCHOR, SECTION + ANCHOR))
print("recorded the unnerving register: 5 rows plus the twelve-quote gathering")
