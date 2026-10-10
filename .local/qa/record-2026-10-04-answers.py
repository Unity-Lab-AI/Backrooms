# -*- coding: utf-8 -*-
"""Four owner answers, 2026-10-04, recorded verbatim before any of them is built.

PRE-WORK GATE. LAW #0: their exact sentences, one row per item, nothing
paraphrased or collapsed. One of the four supersedes an earlier direction of
theirs and the earlier one is struck in place rather than removed.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

ANCHOR = "### Session direction, 2026-10-04 — this file ends as a template holding nothing"

SECTION = '''### Owner answers at four forks — the chasers are ordinary pawns, the DLC only adds, and the glass comes out (2026-10-04)

Asked because each one gated work that was already queued, and three of the four changed what gets built rather than how.

**Verbatim owner answer (2026-10-04), on what chases you in the Backrooms:** *"yeah things that chase you are just npc pawns and wild animals and shit of the gasme spawned in procedurally and dynamically for randomness encounters, not somew new type of np0c in the backrooms, they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios. not some blob figure, just normal core mechanics"*

**This retires a bespoke manifestation, and the question that produced it was badly asked.** Owner, same message: *"i have no clue what the fuck you are asking with this question its way to convoluted in how its worded for me to give an anwser and the options dont sound like anything appropriate and are taking paths not listed in anything ive said"* — **and they were right.** The first version of the question offered three paths none of which they had ever mentioned, and it asked about replacing custom art when `RR_QuietPursuer` was **already** drawn with a Core texture (`Things/Mote/Black`). The question was only answerable once it said what the thing actually looks like on screen today.

- [ ] **"things that chase you are just npc pawns and wild animals and shit of the gasme"** — the chasers are **Core pawns and Core animals**, not a thing-def manifestation. `RR_QuietPursuer` is a `ThingDef` with a mote texture and `FirstSlicePursuer` drives it; that is the thing being replaced.
- [ ] **"spawned in procedurally and dynamically for randomness encounters"** — chosen at generation and at event time from what the game already has, so the roster varies by coordinate and by visit rather than being one authored creature.
- [ ] **"not somew new type of np0c in the backrooms"** — **no new pawn kind, no new faction, no new entity type.** This is the standing content-reuse policy applied to the one place that still broke it.
- [ ] **"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"** — **three relations, not one.** A Backrooms encounter can be a hostile raider, a wild animal, a neutral traveller or somebody who helps. Today everything down there is hostile by construction, which is the narrower thing this replaces.
- [ ] **"not some blob figure, just normal core mechanics"** — the 1.4-tile black mote goes. Whatever is down there is rendered by RimWorld's own pawn and animal drawing, because it **is** one.

**Verbatim owner answer (2026-10-04), on gate width:** *"this is already layed out, people through 1x1 cdoor gates, herd animals through 2x1 and vehicals through 3.1 and 3x2 depending size"*

**The capability table was already specified and the row asking for it was the thing out of date.** It also matches two earlier owner lines exactly — *"bigger creatures fit through a wider gate"* and *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed to fit vehicals and the like and bigger creatures"*.

- [ ] **"people through 1x1 cdoor gates"** — a single-cell gate passes colonists and other humanlikes, and nothing larger.
- [ ] **"herd animals through 2x1"** — two cells wide passes animals: pack animals, muffalo, anything herded.
- [ ] **"vehicals through 3.1 and 3x2 depending size"** — three wide passes vehicles, and **3x2 is for the ones a 3x1 cannot take.** Size decides which, so the rule reads from the vehicle rather than from a list of them.

**Verbatim owner answer (2026-10-04), on the company record book:** *"Mark the company-issued ones"*

- [ ] **"Mark the company-issued ones"** — the scenario grant tags the books it hands out, so **those** carry the company label and every bought or looted novel keeps Core's own title. This closes the half of *"its own label and an inspect card"* that was deliberately not built, and the reason it was not built stands: `Patches/RR_ExistingEvidenceBook.xml` puts the comp on **every** Core `TextBook`, so an untagged rename would retitle trade stock and other mods' books.

**Verbatim owner answer (2026-10-04), on the five expansions:** *"every dlc shall be optional and this goes back to a todo i told you was major work, where we will completely make the mod 100% functional and stand alone not needing any other mods, and DLCs only add content and everything the mod needs is supplied wwith the mod as the mod, which will have all things needed to operate(but one thing, issues like the ballistic glass we used needs to be taken out of the starting scenerio to acturatley make sure it isnt needed to play the mod"*

**This is the stand-alone direction restated with a mechanism and one named defect**, and it answers the question as *"neither of your options"*: the five expansions are not non-goals and not content to author — they are **optional additions on top of a package that is already complete without them**.

- [ ] **"every dlc shall be optional"** — confirmed, and already enforced: `check-dlc-gating.py` holds it and all five came out of `modDependencies` at 0.12.86-dev.
- [ ] **"we will completely make the mod 100% functional and stand alone not needing any other mods"** — the guarantee half of the stand-alone work, which has its own row and stays open.
- [ ] **"DLCs only add content"** — a DLC may never be load-bearing. Nothing the mod needs to operate may live behind one, which is the rule the conditional layers are measured against.
- [ ] **"everything the mod needs is supplied wwith the mod as the mod, which will have all things needed to operate"** — **the positive form of the rule, and it is the useful one.** Not merely *"degrades when something is absent"* but *"ships what it needs"*. A graceful fallback that quietly drops a designed feature is a package that is not complete.
- [ ] **"but one thing, issues like the ballistic glass we used needs to be taken out of the starting scenerio to acturatley make sure it isnt needed to play the mod"** — **a real defect, measured: `RR_Starts.xml` names `RB_ReinforcedGlassWall` and `RB_GlassWall` from ReBuild: Doors and Corners (register row 185).** Those are the **only two** non-Core def references in the shipped starts; every other reference in `RR_Starts.xml` and `RR_Scenarios.xml` is Core or ours. The run already degrades to a plain wall when ReBuild is absent — so the mechanism was safe and **the claim was still not provable**, which is exactly the owner's *"to acturatley make sure"*. ~~The viewing wall is ReBuild glass~~ — **superseded by this answer**; the earlier owner direction it served, *"ballistic glass  walls for viewing the machine remotely and safely"*, is kept and is answered a different way.

'''

text = io.open(TODO, encoding="utf-8").read()

if "the chasers are ordinary pawns, the DLC only adds" in text:
    print("already recorded")
    sys.exit(0)
if text.count(ANCHOR) != 1:
    print("ANCHOR NOT UNIQUE (%d); nothing written" % text.count(ANCHOR))
    sys.exit(1)

io.open(TODO, "w", encoding="utf-8", newline=NL).write(text.replace(ANCHOR, SECTION + ANCHOR))
print("recorded 4 owner answers as 17 rows, verbatim")
