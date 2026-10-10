# -*- coding: utf-8 -*-
"""Prepend the 0.12.87-dev entry. Newest first, nothing above it rewritten."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"

ENTRY = """## 0.12.87-dev - 2026-10-04 - The thing chasing you is a person or an animal, a gate's width means something, and the start names no other mod

- **What chases a crew is an ordinary RimWorld pawn now.** Owner: *"things that chase you are
  just npc pawns and wild animals and shit of the gasme spawned in procedurally and dynamically
  for randomness encounters, not somew new type of np0c in the backrooms ... not some blob
  figure, just normal core mechanics"*. It was `RR_QuietPursuer`, a `ThingDef` drawn as a
  1.4-tile black mote and driven by a bespoke `Thing_QuietPursuer` whose own comment read *"No
  native pawn AI or unbounded melee attacks."* Concretely it **teleported** -
  `pursuer.Position = cell` - so it never walked, never pathfound and never opened a door; it
  **struck once, scripted**, two points of blunt to a named arm only above 80% health; and it
  **withdrew after three advances by a counter**. All three are Core's now: a real `Pawn` from
  Core's own `PawnGenerator`, hunting with the same AI, pathing, doors, weapons and wounds as any
  hostile in the game. The def is retired, the class is deleted, and five saved fields that
  existed only to pace a scripted walk went with them.
- **The roster is Core pawn kinds and the map biome's own wild animals**, because the direction
  names two things. An animal is turned **manhunter** rather than given a faction, which is
  Core's way of saying *this one is coming for you* and is why an animal chaser needs nothing
  authored. The humanlike kinds are the three the inhabitant families already vetted, so the
  package has one list of *people down here who will hurt you* rather than two.
- **Procedural, and not a save-scum.** The kind is derived from the branch seed salted with the
  opening id, never `Rand`, so one opening always meets the same chaser and a reload cannot
  reroll what is hunting you. The roster is ordered before it is indexed: a derived index into an
  unordered list is reproducible by luck only, since def database order is not a promise.
- **AND THIS SUBSYSTEM HAD NO COVERAGE AT ALL.** No proof and no plant anywhere mentioned the
  pursuer - twenty-three plant suites, forty-nine proofs, and a 224-line bespoke threat passed
  every gate this project has for twenty-seven versions, because no instrument was pointed at it.
  `proof-chaser.py` is 21 claims and `plant-chaser.py` reports **17 of 17 caught**. Two plants
  reported MISSED on the first run and **both were the claims being wrong, not the code**: one
  matched the old code's exact three-line layout, and one tested a comment.
- **A gate's width decides what fits, including vehicles.** Owner: *"people through 1x1 cdoor
  gates, herd animals through 2x1 and vehicals through 3.1 and 3x2 depending size"*. The first
  two rungs already held from Core's own body sizes. **The vehicle rung did not exist**: width
  three returned *no limit*, so a three-wide gate admitted anything of any footprint and nothing
  anywhere could tell a 1x3 gate from a 2x3 one - two of the four legal footprints were the same
  gate as far as the game was concerned. `GateOpeningDepth` is new and *"depending size"*
  resolves to the vehicle's narrower dimension against the aperture's depth: a 1x2 runabout takes
  the 1x3, a 2x3 truck needs the 2x3, a 3x5 tank fits through neither. Recognised by footprint,
  never by type, so it works with the vehicle mods in the profile and identically with none.
- **The company's own books carry the company's label.** Owner: *"Mark the company-issued
  ones"*. Set once at the moment of granting and saved, by the arrival sweep that was already
  enumerating what Core created and by the genstep that places the start's two. Nothing scans for
  books later, so nothing can retro-tag one a player bought - and every other `TextBook` in the
  game keeps Core's own label byte for byte.
- **The starting scenario names no other mod's defs.** Owner: *"issues like the ballistic glass
  we used needs to be taken out of the starting scenerio to acturatley make sure it isnt needed
  to play the mod"*. `RB_ReinforcedGlassWall` and `RB_GlassWall` were the only two non-Core def
  references in any shipped start. Nothing changes for a Core-only player - the genstep already
  left a plain wall when ReBuild was absent - but the claim is checkable now, which is what *"to
  acturatley make sure"* asks for: `check-register-compliance.py` refuses a non-Core def
  reference in a shipped start or scenario.
- **And the first version of that rule read almost nothing.** It listed `thingDef` and missed
  `<thing>`, which is **114 of the 171 def references** in the file; a hand-planted foreign def
  sailed through and it reported PASS. The tag list is enumerated from the files now, and the
  same plant fails it.

"""

text = io.open(PATH, encoding="utf-8").read()
if "## 0.12.87-dev" in text:
    print("already present")
    sys.exit(0)

head = "# Changelog" + NL + NL
if not text.startswith(head):
    print("CHANGELOG does not start with the expected heading; nothing written")
    sys.exit(1)

io.open(PATH, "w", encoding="utf-8", newline=NL).write(head + ENTRY + text[len(head):])
print("prepended the 0.12.87-dev entry (%d lines)" % (ENTRY.count(NL) + 1))
