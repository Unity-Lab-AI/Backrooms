# -*- coding: utf-8 -*-
"""Close what this batch built. Evidence on the row's own line, nothing past it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 # ======================================================== the stand-alone guarantee
 ('- [ ] **"we will completely make the mod 100% functional and stand alone not needing any other mods"**',
  'CLOSED 0.12.91-dev — **the audit this row has been waiting for exists, it ran, and it is a '
  'checker now so it cannot rot.** The row said exactly why nothing already in the battery could '
  'establish this: *"A declaration cannot establish it."* '
  '`tools/check-standalone-guarantee.py` is checker **19**, and it answers the question '
  '`check-dlc-gating.py` structurally could not. That one asks *is every expansion reference '
  'gated*; it can never see a reference to one of the **294 profile mods**, because such a def is '
  'not DLC-only — it is not in the game’s data at all. **That was the hole a stand-alone '
  'claim actually rests on:** one `thingDefName` naming another mod’s building would make the '
  'package quietly require that mod, with no error anywhere until a player without it reached the '
  'feature. '
  '**The measurement, first run:** **214** def-name field values across the whole package — '
  '**0** resolve outside Core and our own defs, and the 14 that resolve only in an expansion are '
  'all gated. **64** literal def lookups in C# — **0** hard `GetNamed` on anything we do not '
  'ship, and the 5 expansion lookups all go through `GetNamedSilentFail`. **4** assembly '
  'references, all the game’s own and Unity’s. '
  '**The reference fields are enumerated from our own source**, not listed by hand — the lesson '
  '`check-register-compliance.py` paid for when a hand-kept tag list missed `<thing>` and read '
  '114 of 171 references as nothing. **And it SKIPS rather than passes when the game data is '
  'absent**, because a checker that reports green against nothing is the defect that once gave '
  'eight claims a false pass.'),

 ('- [ ] **"DLCs only add content"**',
  'CLOSED 0.12.91-dev — **the positive half, which is the half the row said was open.** The '
  'negative half was already enforced: `check-dlc-gating.py` refuses unguarded expansion content. '
  'What was missing was proof that **nothing the mod needs to operate lives behind an '
  'expansion**, and that is now measured: every expansion reference in the package is '
  '`MayRequire`-gated, every expansion lookup in C# degrades through `GetNamedSilentFail`, and '
  'the four new expansion roles carry **no stock need and no risk**, so an expansion cannot even '
  'put a *shortfall* line in front of a player. '
  '**And the expansion content added this batch is optional by CONSTRUCTION rather than by a '
  'gate**, which is a stronger guarantee than the gate gives. '
  '`RimroomsGateEquipmentDef.thingDefNames` is a `List<string>`: naming `HoldingPlatform` creates '
  '**no cross-reference at load at all**, `Fillable` resolves it through `GetNamedSilentFail`, and '
  '`AllInOrder` hides a role nothing can fill from the picker, the readout and `RoleFor` alike. '
  'The `MayRequire` on each entry is a deliberate second line, **per entry rather than per '
  'role** — gating the whole role would delete a role that also accepts Core buildings, and '
  'Core gates string lists the same way in `CommonMapGenerator.xml`. '
  '**`check-dlc-gating.py` could not see a per-entry gate** and reported all fourteen as ungated. '
  'It read the attribute off the def alone; it now accumulates down the element tree, which is '
  'how RimWorld reads it. **Taught the mechanism rather than worked around** — demanding the '
  'attribute on the def would have pushed the worse shape, which is how a checker ends up making '
  'the code wrong. Verified still strict: an ungated entry exits 1, a foreign def exits 1, a hard '
  '`GetNamed` exits 1.'),

 ('- [ ] **"everything the mod needs is supplied wwith the mod as the mod, which will have all things needed to operate"**',
  'CLOSED 0.12.91-dev, **and this was the useful form of the rule exactly as the row said.** Not '
  '*"degrades when something is absent"* but *"ships what it needs"* — and the difference is '
  'what the new checker measures. A graceful fallback that quietly drops a designed feature would '
  'pass a degradation test and fail this one. '
  'The package names **334 defs of its own** and references **nothing** outside those and Core '
  'except gated expansion content. Everything the mod needs to operate — the gate and its three '
  'providers, the start layout, every request route, every room archetype slot, every inhabitant '
  'pawn kind, every certification recipe, every facility role that is not an expansion role — '
  'resolves on a **Core-only install**. '
  '**The four expansion roles are the proof of the distinction, not an exception to it:** they '
  'add a containment wing, a biological laboratory, an assembly room and off-world logistics, and '
  'the gate opens, the crews cross, the records are kept and the company pays exactly the same '
  'without any of them.'),

 # ======================================================== Anomaly's named open item
 ('- [~] Anomaly conditional content: containment/research links;',
  'CLOSED 0.12.91-dev. The row’s open item was **specifically** *"the containment/research '
  'links themselves"*, and containment now exists to link to: 0.12.90-dev made **contain** one of '
  'four dispositions of a recovered record, with a daily charge on its own ledger line. '
  '`RR_Link_Containment` is the facility side of it — holding platforms, holding spots and '
  'bioferrite equipment linked as this facility’s containment wing, so a branch that decides '
  'to contain what it brings back has somewhere built for it rather than a shelf and a hope. '
  '**The load-bearing half the row already credited stays true:** the Backrooms entities retain '
  'a base-game implementation and nothing about them moved behind Anomaly. The role is additive, '
  'carries no stock need, and is **hidden entirely on an install without the expansion** by '
  '`Fillable` — not merely gated, but unable to exist. Containment on paper, which is what the '
  'rest of the mod does, is unchanged.'),

 # ======================================================== two measured stale
 ('- [ ] **Still unbuilt from the same prep document:**',
  'CLOSED 0.12.91-dev — **stale, and measured against the source rather than taken from the '
  'row.** Its only remaining item was *"staff prior exposure"*, and that ships and is wired: '
  '`Company/StaffExposure.cs` records a trip at `NoteFieldExposure`, called from '
  '`NoteReturnedFromField` which is the one place *came back from there* is already known; '
  '`ExposureDialFactor` is read by `GateSpinUp`; `FieldTripsFor` and `HasBeenTo` are read by the '
  'crew planner, which names a novice a novice rather than leaving it blank. '
  '**This is the second row to be found stale on this same clause** — 0.12.90-dev found the '
  'personnel row listing prior exposure as not built when it was built and wired. A fact recorded '
  'as missing in two places was missing in neither. (Contradictory accounts closed 0.12.25-dev.)'),

 ('- [ ] **`returnReserveCapacityWattDays` is 2 and a Core `Battery` holds 600**',
  'CLOSED 0.12.91-dev as **the recorded finding it is, not a task.** Its own words are *"Checked '
  'and ruled out rather than assumed"* — it eliminates the bind-time *ReserveTooSmall* refusal '
  'as a cause of the battery defect, and it sits under a section already titled DONE. There is '
  'nothing to build; the value is the elimination, and it belongs in the archive where the next '
  'reader will find it rather than in a queue of open work. '
  '**Ruled-out causes are worth as much as fixes and this batch produced four more of them** — '
  'see the starting-goods rows, where the arrival part, the start spot, the gen step order and '
  'the drop method were each eliminated against the installed game.'),
]

NOTES = [
 ('- [ ] **"they need to properly spawn in with starting goods"**',
  'CAUSE STILL NOT FOUND, AND FOUR CANDIDATES ELIMINATED 0.12.91-dev — **the row stays open '
  'because it says *no fix was written on a hunch* and that still holds.** Eliminated against the '
  'installed game rather than guessed: **(1)** the arrival part is not missing — '
  '`ScenPart_RimroomsArrival` **subclasses** `ScenPart_PlayerPawnsArriveMethod` and calls '
  '`base.GenerateIntoMap`, which is the one place in the game that collects '
  '`PlayerStartingThings()` and places it; **(2)** the start spot is not wrong — Core’s '
  '`FindPlayerStartSpot` is order 850 and only picks when none is valid, ours is set at 800 and '
  'kept; **(3)** the gen steps are not out of order — Core’s `ScenParts` is order **875**, '
  'after both; **(4)** the pawns do not arrive by pod and scatter — `Standing` is enum zero and '
  'the scenarios set it explicitly. '
  '**And the row’s own evidence rules out the next obvious one:** the pawns’ '
  '`MealSurvivalPack` possessions *did* arrive, and possessions travel in the same list as the '
  'grants through the same `DropThingGroupsNear` call — so the placement ran and the grants were '
  'not in the list it placed. '
  '**What landed instead is the thing that makes the next launch answer this.** The receipt now '
  'records what the scenario **promised** and what actually **arrived**, and the start reports '
  'the gap on the letter stack. The promise is read through `GetSummaryListEntries`, which '
  '**creates nothing** — enumerating `PlayerStartingThings()` again would manufacture a second '
  'set of goods, the exact double-grant the receipt exists to prevent. It never blocks a start, '
  'and it is silent unless a promise was recorded and nothing at all arrived.'),

 ('- [ ] **"my preparecarfully mod food did not appear"**',
  'SAME PATH, SAME DIAGNOSTIC 0.12.91-dev. Prepare Carefully’s equipment reaches the map '
  'through `PlayerStartingThings()`, which is the same enumeration the scenario grants use — so '
  'one break explains both halves of the original report, exactly as this row says. '
  '**The new start report names this quarter explicitly**, so the next launch produces a log that '
  'either implicates it or clears it: the letter lists what the scenario promised and says that a '
  'mod supplying starting equipment is the most likely cause, with the request for the '
  '`Player.log`. The row stays open until that log exists.'),

 ('- [~] Royalty conditional content: titles/quests/faction/psycasts only as optional company routes.',
  'NO HONEST HOOK EXISTS YET, AND THAT IS RECORDED RATHER THAN PADDED 0.12.91-dev. Royalty ships '
  '**almost no buildings** — thrones are Core; what it adds is titles, permits, psycasts and the '
  'Empire. None of those is equipment a facility can be linked to, and the row’s own '
  'condition is *"only as optional company routes"*: a success route must be a **thing** '
  '(Deliver/Substitute/Purchase), a **log** (Document/Testify) or a **project** (Research). A '
  'title is none of the three. '
  '**So an honest Royalty hook needs a new route kind**, which is a design decision rather than a '
  'def edit, and inventing a thin one would be the hollow unlock this package keeps refusing. '
  'Stated the same way the project tree states that transport and orbital support has no tier 0 '
  'project, deliberately. The one place Royalty content already reaches the campaign is indirect '
  'and real: the Empire is a faction, and 0.12.90-dev made the world’s faction hostility one '
  'of the four inputs biasing which request family the corporation leads with.'),

 ('- [~] Ideology conditional content: beliefs, meditation, rituals, staff policies, and recreation only when available.',
  'THE RECREATION CLAUSE LANDED 0.12.91-dev; the row stays open for the rest. `RR_Link_Assembly` '
  'is a room the branch gathers in — somewhere to be presentable, somewhere to be heard, and '
  'something to make a noise with — linked from `StylingStation`, `Loudspeaker` and `Drum`, and '
  '**hidden entirely without Ideology** by `Fillable` rather than merely gated. '
  '**One clause of five, and that is said plainly rather than claimed as the row.** Beliefs, '
  'meditation, rituals and staff policies are pawn-level and ideo-level mechanics with no '
  'facility or supply shape, and each would need its own decision about what an *optional* '
  'version looks like.'),

 ('- [~] Biotech conditional content: genes, mechanitors, children, medicine, pollution, and mechanoid options; no mandatory gene/resource dependency.',
  'THE EQUIPMENT CLAUSE LANDED 0.12.91-dev; the row stays open for the rest. `RR_Link_Biolab` is '
  'this facility’s biological wing — gene assembler, gene bank, growth vat, mech gestator, '
  'subcore encoder and softscanner — because what comes back from a coordinate is not always a '
  'thing on a shelf. **Hidden entirely without Biotech** by `Fillable`. '
  '**Nothing is mandatory, which is the clause the row cares most about**, and it is now '
  'measured rather than asserted: `check-standalone-guarantee.py` confirms every Biotech '
  'reference in the package is gated and every Biotech lookup in C# degrades. Genes, children, '
  'medicine and pollution remain unaddressed, each needing its own answer about what optional '
  'means.'),

 ('- [~] Odyssey conditional content: gravship/off-world logistics and any compatible space travel.',
  'THE LOGISTICS CLAUSE LANDED 0.12.91-dev; the row stays open for space travel. '
  '`RR_Link_OffworldLogistics` puts a gravitational engine on the branch’s books, so the '
  'company can account for a facility that is able to leave — a branch that can move is a branch '
  'whose gate is not the only way anything arrives. **Hidden entirely without Odyssey** by '
  '`Fillable`, and the gate works identically without it. '
  '**A gravship actually carrying a branch between tiles is not built**, and that is the larger '
  'half: it needs the same world-object-and-generated-map checkpoint the two outstanding '
  '*"world tile the branch does not hold"* rows name.'),
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
print("closed %d rows, noted %d" % (len(CLOSED), len(NOTES)))
