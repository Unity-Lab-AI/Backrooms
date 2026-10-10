# -*- coding: utf-8 -*-
"""Close what this batch built. Evidence on the row's own line, nothing past it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 # ============================================ the chasers are ordinary pawns
 ('- [ ] **"things that chase you are just npc pawns and wild animals and shit of the gasme"**',
  'CLOSED 0.12.87-dev. `Threats/FirstSlicePursuer.cs` spawns a real `Pawn` through Core’s own '
  '`PawnGenerator`, drawn from the three hostile humanlike kinds this package already vetted for '
  '`RR_Inhabitant_Psychotic` — Pirate, Drifter, Villager — **and from `map.Biome.AllWildAnimals`**, '
  'because the direction names two things and a roster of only people is half an answer. A wild '
  'animal is turned **manhunter** rather than given a faction, which is Core’s own way of saying '
  '*this one is coming for you* and is why an animal chaser needs nothing authored at all.'),

 ('- [ ] **"spawned in procedurally and dynamically for randomness encounters"**',
  'CLOSED 0.12.87-dev, and **procedural without being a save-scum.** The kind is drawn with '
  '`CampaignSeed.Derive` off the branch seed salted with the opening id — never `Rand` — so one '
  'opening always meets the same chaser and a reload cannot reroll what is hunting you, while two '
  'openings differ. The roster is **ordered by defName before it is indexed**, because a derived '
  'index into an unordered list is reproducible by luck only: def database order is not a promise, '
  'and the same seed would pick different things on different loads. That one has its own plant.'),

 ('- [ ] **"not somew new type of np0c in the backrooms"**',
  'CLOSED 0.12.87-dev. **No new pawn kind, no new faction, no new entity type — and one fewer def '
  'than before.** `RR_QuietPursuer` is out of `RR_SiteObjects.xml` with the owner’s direction left '
  'in the file where it used to be, and `Thing_QuietPursuer.cs` is deleted. Five saved fields went '
  'with them: `advances` counted scripted room hops, `nextAdvanceTick` paced them, `lastLoudTick` '
  'and `lastObservedCrewRoom` decided when one was allowed, and `attemptedStrike` recorded the '
  'single scripted blow. A real hostile paces itself, so none of them had anything left to hold.'),

 ('- [ ] **"not some blob figure, just normal core mechanics"**',
  'CLOSED 0.12.87-dev, and the blob was the smaller half of the problem. It drew as '
  '`Things/Mote/Black` at 1.4 tiles — but it also **teleported**: `pursuer.Position = cell` moved '
  'it room to room, so it never walked, never pathfound and never opened a door. It **struck once, '
  'scripted**: two points of blunt to a named arm, only against a target above 80% health, then it '
  'withdrew — the same two points whether the crew fought well or badly. And it **withdrew after '
  'three advances by a counter**. All of that is Core’s now: same AI, same pathing, same doors, '
  'same weapons, same wounds as any hostile anywhere else in the game. **The file is shorter and '
  'does less, which is the point.** '
  '**AND THIS SUBSYSTEM HAD NO COVERAGE AT ALL, which is why it lasted twenty-seven versions.** '
  'There was no proof and no plant anywhere that mentioned the pursuer. `proof-chaser.py` is 21 '
  'claims and `plant-chaser.py` is **17 of 17 caught**; the load-bearing one is *the chaser '
  'teleports again*, because every other defect followed from that. Two plants reported MISSED on '
  'the first run and **both were my claims being wrong, not the code** — one matched the old '
  'code’s exact three-line layout, and one tested a comment. Both re-aimed.'),

 # ============================================ the gate width ladder
 ('- [ ] **"people through 1x1 cdoor gates"**',
  'CLOSED 0.12.87-dev, and it already held: a person is body size 1.0 against '
  '`SingleWidthMaxBodySize` 1.2, so a single-cell gate passes colonists and anything person-sized '
  'and nothing larger. Named as `WidthForPeople` so the ladder reads as the owner stated it rather '
  'than as two bare floats.'),

 ('- [ ] **"herd animals through 2x1"**',
  'CLOSED 0.12.87-dev, and it already held for the same reason, from Core’s own numbers: a '
  'muffalo is 2.4 and a dromedary 2.1, both past the 1.2 a one-wide admits, both inside the 2.5 a '
  'two-wide does. Named `WidthForHerdAnimals`.'),

 ('- [ ] **"vehicals through 3.1 and 3x2 depending size"**',
  'CLOSED 0.12.87-dev, and **this was the rung that did not exist.** Width three returned *no '
  'limit*, so a three-wide gate admitted anything of any footprint — and **nothing anywhere could '
  'tell a 1x3 gate from a 2x3 one.** Two of the four legal footprints were the same gate as far as '
  'the game was concerned. `GateOpeningDepth` is new (cells per width, derived so a gate bound '
  'across a run of ordinary doors measures the same way a real wide door does) and '
  '`PortalTravelService.DoorwayDepth` carries it to the policy. '
  '**What *"depending size"* resolves to:** a vehicle drives through long-ways, so the dimension '
  'that must clear the aperture is its **narrower** one, and the two vehicle gates differ by '
  'depth. A 1x2 runabout has a narrow side of 1 and takes the 1x3; a 2x3 truck has 2 and needs the '
  '2x3; a 3x5 tank has 3 and **fits through neither**, which is the honest end of a ladder bounded '
  'at four footprints. Three refusals say which of the three it is. '
  '**Recognised by footprint, never by type:** vehicles come from a mod, and nothing here '
  'references one — a thing whose def occupies more than a single cell is treated as a vehicle, '
  'which is true of every vehicle and of nothing Core ships as a pawn.'),

 # ============================================ the company's own book
 ('- [ ] **"Mark the company-issued ones"**',
  'CLOSED 0.12.87-dev. `CompRouteEvidence.companyIssued` is set **once, at the moment of '
  'granting**, and saved: by `ScenPart_RimroomsArrival` in the sweep that was already enumerating '
  'exactly what Core created for this arrival, and by `GenStep_Headquarters` for the two books the '
  'start def places. **Nothing scans for books later, which is what makes it impossible to '
  'retro-tag something a player bought — there is no code path that could.** `TransformLabel` '
  'returns Core’s own label byte for byte on anything unmarked, which is every other `TextBook` '
  'in the game; the reason the label half was not built until now stands and is recorded in place: '
  'the comp is patched onto **every** Core `TextBook`, so an untagged rename would retitle trade '
  'stock, quest rewards and other mods’ books.'),

 # ============================================ the stand-alone declaration
 ('- [ ] **"every dlc shall be optional"**',
  'CLOSED 0.12.87-dev as confirmed and already enforced. `check-dlc-gating.py` holds it, all five '
  '`Ludeon.RimWorld.*` entries came out of `modDependencies` at 0.12.86-dev and remain in '
  '`loadAfter`, and `GATE_0_DECISIONS.md` D4 is back to the position it held when first recorded '
  'on 2026-09-27 — *"Core-only campaign; all five DLC optional detected content"* — which the '
  '2026-10-01 amendment had reversed.'),

 ('- [ ] **"but one thing, issues like the ballistic glass we used needs to be taken out of the starting scenerio to acturatley make sure it isnt needed to play the mod"**',
  'CLOSED 0.12.87-dev. `RB_ReinforcedGlassWall` and `RB_GlassWall` from ReBuild: Doors and Corners '
  '(register row 185) are out of `RR_Starts.xml`; they were the **only two** non-Core def '
  'references in any shipped start. **Nothing changes for a Core-only player** — '
  '`GenStep_Headquarters` already resolved the run with `ResolveFirstLoaded` and left a plain wall '
  'when ReBuild was absent, so those eleven cells were plain steel before and are plain steel now. '
  '**What changes is that the claim is checkable**, which is exactly the owner’s *"to acturatley '
  'make sure"*: a shipped start that names another mod’s defs cannot be audited as stand-alone by '
  'reading it — you have to go and read the C# that resolves it and then decide whether that '
  'particular resolver degrades. `check-register-compliance.py` now refuses any non-Core def '
  'reference in a shipped start or scenario. '
  '**AND THE FIRST VERSION OF THAT RULE READ ALMOST NOTHING.** It listed `thingDef` and missed '
  '`<thing>`, which is **114 of the 171 def references** in the file; a hand-planted foreign def '
  'sailed straight through and it reported PASS. The tag list is now enumerated from the files '
  'rather than guessed, and the same plant fails it. The `glazing` field, the run plan and the '
  'genstep all stay — a scenario may use them — and the earlier owner direction this served, '
  '*"ballistic glass  walls for viewing the machine remotely and safely"*, stays open in the '
  'queue: Core ships no see-through wall, so answering it Core-only is a decision rather than a '
  'tidy-up.'),
]

NOTES = [
 ('- [ ] **"they should be nutral, allies, and enemy in all differnt kinds and relations and scenrios"**',
  'PARTLY BUILT 0.12.87-dev, and the missing third is named. **Enemy** ships: the chaser is a real '
  'hostile and `RR_Inhabitant_Psychotic` / `_PsychoticPack` draw hostile humanlikes. **Neutral** '
  'ships: `RR_Inhabitant_Wanderer`, `_Missing` and `_Survivor` are unfactioned or neutral and are '
  'not hostile to anybody. **Ally does not exist** — there is no family down there that helps a '
  'crew, and *"all differnt kinds and relations"* asks for one. Wild animals also only reach the '
  'player through the chaser so far, not through the inhabitant families. This row stays open on '
  'those two.'),

 ('- [ ] **"DLCs only add content"**',
  'PARTLY HELD 0.12.87-dev. The negative half is enforced: `check-dlc-gating.py` refuses '
  'unguarded DLC content and every expansion is optional. **The positive half is the guarantee '
  'half of the stand-alone work** — proving that nothing the mod needs to operate lives behind an '
  'expansion needs the row-by-row audit that has its own row and stays open. A declaration cannot '
  'establish it and neither can this one.'),
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
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]

for anchor, note in NOTES:
    found = text.count(anchor)
    if found != 1:
        print("NOTE ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:92]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    text = text[:line_end] + " — **" + note + "**" + text[line_end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows, noted %d partials" % (len(CLOSED), len(NOTES)))
