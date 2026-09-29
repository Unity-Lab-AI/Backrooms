# NOW — handoff after compaction

**Single-focus tracker.** Distinct from the three-tier ledger:

| File | Grain |
|------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, **every owner direction verbatim** |
| `docs/DECOMPOSED.md` | smallest execution units |
| **`docs/NOW.md`** (this file) | **the handoff** |
| `docs/FINALIZED.md` | permanent archive |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

LAW #0 applies: owner words go in verbatim, everywhere. **This is now enforced** — see invariant #69.

---

## Active

**Nothing in flight. Tree clean, everything published, no half-finished task.** Written deliberately for the session after a compaction.

### State

| | |
|---|---|
| Branch | `feature/connected-colony-portals` |
| Published | **0.12.20-dev**. This handoff is the tip; `git log --oneline -1` is authoritative and the eight refs below match it. |
| Remotes | `forgejo` + `github`, all four refs each at that commit |
| Build | **173 C# files, 91 package files**, zero warnings, zero errors. **Measure this, never carry it** — it said 172 against a real 170 for five checkpoints and only came true by accident: `git ls-tree -r HEAD --name-only | grep -c '^src/.*\.cs$'` |
| Assembly | SHA-256 `93F61D0FD600EE77142EBA18B4184593A91A78FFA7D38258BA87E58744B06371`, reproduced by two clean recompiles. **This line was stale for five checkpoints** — it still held 0.12.4’s hash. Re-read it from the build, never from memory |
| Checkers | **NINE**, all passing |
| Proofs | **TWENTY** in `.local/register/proof-*.py`. **Run them by exit status, not by grepping their output** — four of them print `PASS:` and eleven print `PROOF HELD`, and a grep for one phrasing silently skips the others. That is how four live proofs went unrun for most of this session |
| Chart | **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document |
| Register | `python tools/register-query.py families\|family <x>\|find <x>\|row <n>\|traces\|trace <code>` — **query by `trace`**: it names the Rimrooms feature a row bears on, which is the question *"what applies to what I am building"*. **The HTML is the register**, never the xlsx. **It is GUIDANCE, not law** (owner, 2026-09-29) |
| Readable HTML | `python tools/make-readable-html.py` → `outputs/readable/index.html` |
| Game launches | **none, ever** |

### The standing instruction

> *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Chain checkpoints. Do not finish one and wait.

---

## What shipped this session, 0.7.1 → 0.12.20

| Version | What |
|---|---|
| 0.7.2–0.7.7 | **The economy** — odd origin, supply contracts, pressure, bonds, corporate trader, exchange |
| 0.7.8–0.8.1 | **The look and the ladder** — yellow rooms, archetypes, escalation, construction echo |
| 0.8.2–0.8.5 | **Inhabitants** — wanderers, survivors, anomalies, colonist echoes, fog-of-war holding |
| 0.8.6–0.8.8 | **Shape** — room echoes, hallways, coherence decay, the gate address book |
| 0.8.9 | **Bringing a gate up is work** — operator-driven spin-up with familiarity; gates are blue |
| 0.9.0 | **A gate is a door and nothing else** — 8 legacy defs retired, package 92 → 79 |
| 0.9.1 | **One kind of gate** — 68 dead branches collapsed, a vestigial power model gone, −112 lines |
| 0.9.2 | **A gate has a size** — 1×1 to 2×3; Core's own `OrnateDoor` gives 1×2 free |
| 0.9.3 | **Everything you can look at says what it is** — info cards calibrated to Core's practice |
| 0.9.4 | **What a gate's size lets through** — animals cross; width decides what fits |
| 0.9.5 | **They follow you** — at `Band.Hostile` an inhabitant hunts to the threshold |
| 0.9.6 | **It came through with them** — a bounded, named exception to the founding rule |
| 0.9.7 | **Some places are bigger than a room** — facilities as contiguous runs |
| 0.9.8 | **One tech tree, different starting points** — the tree is derived, not declared |
| 0.9.9 | **The beacon had nothing left to do** — first field-gear retirement |
| 0.10.0 | **The documents say what is true** — sixth checker, 28 stale claims in 10 living docs |
| 0.10.1 | **LAW #0, made checkable** — 10 owner directions found unrecorded |
| 0.10.2 | **One set of words** — gate / connection / threshold, enforced |
| 0.10.3 | **Something is not where you left it** — silent between-visit displacement |
| 0.10.4 | **The register checked backwards** — a LAW, a query tool, a real defect; plus a readable description |
| 0.10.5 | **Every surface the game speaks through** — a seventh checker measured against Core per display surface, and the alerts readout, which this mod used none of |
| 0.10.6 | **The documents use the mod's own words** — the vocabulary and the wall rule reach the reader-facing set; two superseded rules found while reading |
| 0.10.7 | **The survey tag becomes a glow pod** — marker types with colours, three caps removed, and an outcome that could never fire |
| 0.10.8 | **A gate's facility is the equipment linked into it** — shelves, analysers and cabinets link like furniture to a bed, but far, through walls and by hand |
| 0.10.9 | **What you have learned is what you can build** — projects require completed logs; the ladder had one rung and a declared top tier of four |
| 0.11.0 | **The only clock is the gate** — the campaign chart, two offer clocks retired, seven prep documents corrected, eighth checker |
| 0.11.1 | **An offer with more than one way through** — the request shape, routes as a first-class field, contact as a branch state |
| 0.11.2 | **The company asks for six things, then stops asking** — the tutorial line and the hinge; the two-kinds rule forced a better hinge |
| 0.11.3 | **Seven ways into the tree** — research tier 0 across seven branches, each granting a capability real code honours |
| 0.11.4 | **The second rung of every branch** — research tier 1; two vestigial power props found and retired |
| 0.11.5 | **A designated gate is a machine that is on** — three unused props restored, two wired. **Reversed 0.11.4’s retirements.** |
| 0.11.6 | **The second time you do a thing should be cheaper** — research tier 2; three planned unlocks deleted for changing nothing observable |
| 0.11.7 | **The corporation does not write off a branch** — the clean-up team; five `PawnKindDef`s found authored and read by nothing |
| 0.11.8 | **The storyteller finally knows this mod exists** — the first two `IncidentDef`s; no `StorytellerDef`, now asserted |
| 0.11.9 | **A shop with a door in the back** — the Store start; three new-game crashes caught by a new proof |
| 0.12.0 | **You are already in** — the solo/group start; the map itself is a coordinate. **All three starts ship.** |
| 0.12.1 | **The free doors run out** — found doors stop at depth 3; deeper needs a built gate. Corrects 0.12.0 |
| 0.12.2 | **The way out was already there** — the guaranteed exit; two maps, a real coordinate, `GenStep_InsideStart` retired |
| 0.12.3 | **A portal is its own door cell** — a wall beside a gate no longer bricks it; eighth proof |
| 0.12.4 | **Four answers** — supply requirement, deconstruct warning, solo hints; **a tier 0 unlock that did nothing**, found by a new general sweep |
| 0.12.5 | **The queue was in the wrong order** — tier 3 has no knobs to move; the chart authorises arcs 5–8 next. Four hollow unlocks not written |
| 0.12.6 | **A remote base is a costly responsibility** — arc 5 opens: sites on the books, billed daily, and a coordinate is never one |
| 0.12.7 | **Company-to-site logistics** — shipments reach a registered site; a latent cross-map reroute bug fixed before it could bite |
| 0.12.8 | **Remote sites need people** — a shipment to an empty site waits; the stranded-crew guarantee proved rather than rebuilt |
| 0.12.9 | **The exit plan** — a gate may stand at a registered site, with its own facility. Arc 5’s named list complete |
| 0.12.10 | **The handoff** — four live proofs found unrun, five patch scripts un-named as proofs, a stale hash corrected |
| 0.12.11 | **The corporation starts asking** — the mission line reaches a player. **The whole campaign had been authored and read by nothing** |
| 0.12.12 | **The company stops naming things** — generation after the hinge, a filter that can refuse, arc 4’s five families. Fixed 0.12.11’s absolute-state flaw |
| 0.12.13 | **Arcs 5 to 8 have work in them** — thirteen more families, one per item the chart names. **Chart §7 step 8 closed** |
| 0.12.14 | **The queue could not answer the question** — 155 backlog rows re-measured against the code; open rows 254 → 107. **No `FactionDef` exists at all** |
| 0.12.15 | **The universe has factions in it** — seven, all neutral, **no settlements and no new content**. Closes the largest unbuilt owner direction |
| 0.12.16 | **The menu takes any number of slides** — folder-scanned with a load-bearing name prefix, plus the art brief. Two integrity notes that were always wrong, fixed |
| 0.12.17 | **Four more menu slides** — six now cycle. A slide that would never have appeared is caught before it ships; provenance ships for the Steam disclosure |
| 0.12.18 | **The third rung of every branch** — research tier 3, **all seven**, every one moving an observable knob. Two design restraints asserted |
| 0.12.19 | **The yellow rooms were never carpeted** — a real shipped defect; three of my own audit verdicts corrected. **Twentieth proof** |
| 0.12.20 | **The register, by the column that matters** — `trace` querying, and a **ninth checker** verifying how this mod uses other mods |

---

## What is left, in order

The order is the one `docs/CAMPAIGN_CHART.md` §7 authorises. **Read the chart before starting
anything in this list** — it is the authority, and steps 1–5 of its build order are done.

1. ~~**Arcs 5–8.**~~ **CLOSED, 0.12.13-dev.** `docs/CAMPAIGN_CHART.md` §7 step 8 is done: every
   arc now has work a player can be asked to do — **18 generated families across arcs 4–8**, one
   per item the chart names, plus the seven fixed tutorial requests. Arc 5’s *"still unwritten"*
   list turned out to have had real read sites since 0.11.6: the chart’s arc names and the
   research tree’s branch names were describing the same things from two directions.
   **The systems each arc needs still have room to grow**; what is closed is that nothing in the
   chart’s eight arcs is unreachable content. Historical detail follows.
   - **Arc 5, "Build beyond headquarters".** *"Remote sites need people, supplies, signals,
     protection, and an exit plan... A remote base is a costly responsibility rather than free map
     ownership."* **The first piece shipped in 0.12.6-dev**: a branch registers a map it already
     holds, which puts it inside `OwnsMap` and on the daily bill. **Acquisition stays RimWorld's.**
     - **Supplying it: DONE, 0.12.7-dev.** Procurement delivers to any place on the books, and a
       latent cross-map reroute bug was found and fixed before it could swallow a shipment.
     - **Staffing it: DONE, 0.12.8-dev.** A shipment to an unstaffed site waits rather than
       landing in an empty field, checked at arrival so ordering ahead stays possible.
     - **The exit plan: DONE, 0.12.9-dev.** A gate may be designated at a registered site, and it
       needs **its own console, battery and assembly bench there** — a site with a gate is a real
       facility or it is nothing. A way out may come up at a site too, which came free from the
       ownership predicate.
     - **Arc 5's named list is complete**: people, supplies, signals, protection, exit plan.
     - **Still unwritten from the chart:** relay stations, caches, field shelters, guarded leases,
       and resupply and evacuation missions. **Check each against a real read site before
       building** — invariant 136, which deleted four tier 3 projects at 0.12.5.
     - **The chart also names** relay stations, caches, field shelters, guarded leases, resupply
       and evacuation missions. None is written.
   - Arc 6, the outside world — **the `IncidentDef` surface built in 0.11.8 is its home.**
   - Arc 7, industrial reach. **DLC-optional throughout.**
   - Arc 8, deeper systems — partly built already: depth bands, archetypes, the pressure ladder.
2. **Research tiers 3–4, AFTER the arcs.** **Deliberately moved behind them, 0.12.5-dev.** Tier 3
   is *"remote operations: support more than one site; work beyond headquarters"*, and the knob
   sweep found **nothing to move** for Facilities, Fieldcraft, Entities or Commerce, because the
   systems such an unlock would modify are not written. Four of seven projects would have been
   invented effects. Record: `implementation/BUILD_ORDER_CORRECTION.md`.
   - The knobs that **do** exist and are real: `MaximumFrontiersPerCoordinate`, `FrontierRarity`
     and `EmergenceShare` (all three Spatial's, so one branch cannot take them all) and
     `SurveyTicks` (Measurement's).
   - **The ~30 `Maximum*` constants in `ConnectedWork/` are scan budgets, not unlocks.** Raising
     one is a performance decision with no effect a player could name. Do not reach for them.
3. **Generated requests after the hinge. THE MACHINERY IS DONE, 0.12.12-dev.** The eligibility
   filter, the generated offer routine and **arc 4's five families** ship, and progress on a
   generated request is counted from when it appeared. **The thirteen remaining families shipped
   0.12.13-dev**, so this item is closed too: 18 generated families across arcs 4–8, with
   coverage asserted **per arc** — a total would be satisfied by eighteen copies of one arc.
   **Every new route must name a def that exists**, or it can never fire and nothing but
   `proof-request-generation.py` will say so.
   - **Route selection is ANSWERED** (chart §6 item 3 closed): *"Both — filter picks the family,
     card never shrinks."* A family is offered only if the branch can take **two routes of two
     different kinds** from its pool; the card it then shows is the **full authored floor,
     unfiltered**. `RequestRoutes.Available` is not to be modified.
   - **The filter must have teeth.** Invariant 136: every clause has to be able to refuse. A
     `Deliver` route that is "always takeable" makes the whole filter hollow. Refusable readings
     exist for all seven kinds — catalogue carriage, completed logs, living witnesses, project
     availability, redirect target existence.
4. **Still unbuilt from the prep material** — *"contradictory accounts"* from a returning crew;
   staff **prior exposure**; *"respond to openings in settlements"*.
5. **The adjacent-door-run fallback** — 1×3 and 2×3 by binding one gate across a run of adjacent
   1×1 Core doors, for players without Doors Expanded.
6. **`RR_QuietPursuer` presentation** — the last existing-content replacement.
   **The five `RR_*Staff` PawnKinds are NO LONGER part of this item:** they were found already
   authored and read by nothing, and wired as the clean-up team's relief crew in 0.11.7-dev.
   `proof-facility-relief.py` now asserts both directions so they cannot go dead again.
7. **The player-facing how-to.** Written **once**, for both the repo and the site.
8. **Public release** — site, Workshop page, collection. [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md).
    **Correctly last.**
9. **Continue the register retro sweep.** Swept: animals, security, spatial construction,
    expedition logistics, interface, facilities, furniture, storage, power, contracts, faction
    standing, subject casework, evidence, policies. Not yet: medical, world operations, cargo,
    hospitality, materials, visitor economy, staff psychology.
10. Reconcile 0.5.0–0.7.1 into the master backlog; fix the register's `disposition_stance()`
    negation bug; the unknown-def-field checker, **written, proved broken and removed rather than
    shipped**.

### Done since the last handoff, so nobody rebuilds it

**Research:** tiers 0, 1 and 2 across seven branches — **tier 2 complete, and tiers 3–4 deliberately
deferred behind the arcs** (see the queue).

**The corporation:** the clean-up team that means a facility never dies, deterministic and
uncapped · the first two `IncidentDef`s so the player's own storyteller paces the lighter events ·
**no `StorytellerDef`, ever, and it is asserted.**

**All three starts ship.** Async Industries (now opening with eight completed projects) · the
Furniture & Knickknack Store · solo/group, whose map is a real Backrooms coordinate with a
**guaranteed** registered way out and a natural chain that stops at depth 3.

**Arc 5's named list is complete:** sites on the books and billed daily · company-to-site
logistics · staffing, so a shipment to an empty site waits · and the exit plan, a gate at a
registered site with its own console, battery and bench.

**Real defects fixed:** a wall beside a gate no longer bricks it for the life of the save · a
cross-map reroute no longer strands a paid shipment for ever · a tier-0 research card that
promised an unlock and moved nothing now moves something · three dead gate accessors wired ·
five `PawnKindDef`s found authored and read by nothing.

**Guarantees proved rather than rebuilt:** a gate closing on a crew strands them and never takes
them — `ShouldRemoveMapNow` returns false **unconditionally** and no gate source may call
`PassToWorld`.

---

## Invariants — do not break these

Each is a real defect or a pinned fact. Numbering is historical; gaps are deliberate.

### The gate and crossing

1. **`PortalTraversalPolicy` is the only traversal chokepoint.** An inhabitant may never decide anything about a gate.
2. **Two halves of validation, never merged.** A candidate predicate runs against an explicit `Map`.
3. **Remote forbidden checks use the *faction* overload.**
4. **A bounded search that ran out of budget is *pending*, never "no route".**
5. **Every bounded scan is a rotating window, never a prefix.**
6. **Two work givers per family** — high-priority continue, low-priority plan.
7. **Never infer "no local work" from a priority number.**
8. **One commitment per worker**, across every record kind.
9. **Nothing is ever `playerForced`. No quantity is hardcoded.**
10. **No new gameplay ThingDef, PawnKindDef, art or audio.** Match by *capability*. A `FactionDef`, `ThoughtDef` or mechanics def is permitted.
11. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere.
12. **Natural gates have no timer, operator, power, close command or address book, and may not dial.** Enforced by `IsDesignated`, not a second check.
13. **A Backrooms coordinate has no outside**; its roof is never removable; its interior is fully strippable.
14. **A candidate half must ask whether the *target* can take the work.**
15. **A def referencing DLC carries `MayRequire`.**
17. **A prisoner can never cross a gate; a *secure* slave can.**
18. **The topology is an unbounded alternation** of world maps and coordinates.
32. **There is exactly one way a laboratory gate opens** — through the spin-up. Every entry point routes into it.
40. **A gate's width and its footprint are different numbers.** Width decides what fits; footprint decides what it costs.
41. **Throughput is never capped.** A wide gate gets more doorway cells, never a quota. There is no counter, deliberately.
43. **Core ships `OrnateDoor` at 2×1** and `Building_MultiTileDoor` to drive it; Anomaly adds `SecurityDoor`.
47. **A connection has one width, in both directions.** Per-endpoint measuring traps an animal in the Backrooms.
48. **Company work and player orders are two different rules.** `TravellerFailureKey` is colonists-only; `OrderedCrossingFailureKey` admits player animals. **Both refuse a drafted pawn.**
53. **Incursion is the one named exception to the founding rule**, bounded on five axes: live opening, `Band.Hostile`, `PortalWindowTier >= 1`, it must fit, once per opening.
54. **`MayApproachThresholdForTraversal` must stay false for everything, forever.** Incursion works *because* nothing is drawn to a gate.
55. **A transfer that can lose a pawn is a corruption, not a threat.** Preflight fully, then move, and restore on failure.

### Generation and threats

16. **The register is generated output; the HTML one is the register.**
25. **Depth 1 is sacred.** The yellow rooms are fixed, sparse, never deranged. Higher number = deeper (owner-confirmed).
26. **Sort any candidate list ordinally before rolling.** A live trap three times.
27. **Anything saved that feeds the layout fingerprint must be snapshotted, not read live.**
28. **Every threat honours: readable warning, learnable rule, a countermeasure, no unavoidable instant failure.** The threshold room is excluded from every event and inhabitant.
29. **Undiscovered inhabitants are held.** Discovery starts their clock.
50. **`Band.Hostile` is the "deeper levels" threshold** — *"the space stops being forgiving"*. Do not invent a second number.
51. **Below `Band.Hostile` a hostile holds ground; at it, it hunts.**
52. **`LordJob_AssaultColony`'s first parameter is the ASSAULTER's faction.** Passing the player's compiles cleanly and no checker catches it.
57. **A facility is a contiguous run of 2–4 rooms sharing one archetype**, anchored at the lowest index and **stored nowhere**.
58. **Coherence is what wrongness needs.** Do not "fix" facilities by making deep coordinates tidier.
74. **A horror mechanic that fires every time is a mechanic, not horror.** Revisit displacement was weakened from 100% to 66.7% deliberately.
75. **Ownership is the test for "did the player make this".** Generation places with no faction.

### Method

19. **Never trust a remembered list against shipped game data. Enumerate.**
20. **Owner words have been mod names twice.** Search the register before reading a phrase as flavour.
21. **A D-numbered Gate 0 decision can change.** D1 changed 2026-09-29.
22. **The no-tests rule has exactly one exception** (decision 20), in `CONTRIBUTING.md`. Never widen it.
23. **Do not trust a progress percentage from a row count here.**
24. **Nothing is deferred.** Build it, queue it in `TODO.md`, or ask. **Never add a row to `DEFERRED.md`.**
31. **When an existing guarantee already covers a new requirement, say so and rely on it.**
33. **Never tie a penalty rate to a flat constant without proving it against the real stat range.** Express it as a fraction of the observed rate.
34. **Ask at the fork; never flag it for later.** *"dopnt flag shit!!! ask me then and there"*. A flagged question becomes orphaned work.
35. **`ThingComp.ForceColor()` is the tint hook**; a painted colour wins over it. `Notify_ColorChanged()` drops Core's cached graphic.
36. **A checker that reads only one kind of source has a blind side.** Ask both directions, of every source.
37. **Retired content is archived, never deleted** — `docs/implementation/historical-content/<version>/`.
38. **To remove a pervasive flag, delete it and let the compiler enumerate the sites.**
39. **A def field and the XML that sets it are removed in the same change, always.**
42. **A patch target inside `PatchOperationFindMod` is optional by construction**, and only there.
44. **"Like the game does" is measurable. Measure it.** Core describes 0 of 105 work givers and 80 of 80 recipes.
45. **A description nothing renders is text in a file.** Write it and show it in the same checkpoint.
46. **Escapes written through a shell can collapse one level too far and leave an invisible byte.**
49. **Before designing a rule, check it can fire.**
56. **When a founding comment stops describing the code, rewrite it in the same commit.**
59. **When a proof and the code disagree on a constant, change the proof.**
60. **A scenario declares what begins finished, never the tech tree.**
61. **A project that begins finished is also insight-committed.**
66. **Living documents and dated records are different things.** Dated records are **never** rewritten.
67. **A checker that cries wolf is worse than no checker.** Precision before coverage.
68. **The vocabulary is gate / connection / threshold.** Never "portal", "machine gate", "the machine", "doorway" or "gizmo" in player-facing text. **Key names are exempt.**
69. **Every owner direction quoted in `FINALIZED.md` must already exist in `TODO.md`.** A build failure. It found **ten**.
70. **When the owner suspects a process failure, measure it — do not argue.**
72. **A retired def's name outlives the def in player-facing text.** Retiring a def means retiring its vocabulary.
73. **Check a prep document against the build every checkpoint.**
76. **LAW: check the mod register before building.** Filter by system family, read the per-mod review, and **state in the record what was checked** — or that nothing applied. Retroactively too.
77. **The register's `Stance` column is not trustworthy alone.** Row 78 reads `Required`; its review reads `optional`. The review is the authority.
78. **The register HTML has TWO tables**; a naive parse yields 589 rows and silently halves every filter.
79. **Chromium blocks XSLT from `file://`** — a stylesheet on About.xml gives a **blank page**, not a styled one.
80. **RimWorld renders newlines, so a wall of text is a choice.** Fails past 420 chars with no break.
81. **Do not quote a banned string verbatim in a living document** — it trips the rule that bans it. Rephrase.
82. **RimWorld has a different convention per display surface, not one voice.** A float menu row ends with a full stop 7% of the time in Core; an explanatory tooltip does 93% of the time. Writing either in the other's register is the mistake.
83. **Measure a surface, never a file.** The first run of `check-display-style.py` reported seven faults that were not faults, every one from sampling `Letters.xml` or `GameplayCommands.xml` alone when the surface spans several files. The baselines were corrected, not the text.
84. **A census counts the zeroes.** *"to include all"* is only actionable if the report names the surfaces the mod uses **none** of. That is how the alerts readout was found unused. A zero is a question, not a failure.
85. **A count printed with no rule behind it says so.** The inspect pane is counted and not ruled on, because Core builds inspect lines from strings scattered across its keyed files and there is no clean population to measure. A stated limit is not a forgotten one.
86. **Cache an alert scan on the tick AND the game object.** Core calls `GetReport` on a rotating one-in-twenty-four schedule. Keying a cache on the tick alone hands a second save loaded at the same tick the first save's despawned components.
87. **Words quoted from somewhere else are never ours to rewrite.** The vocabulary rule excludes any double-quoted span. The A24 synopsis calls it a doorway; changing that would be misquoting a source, not tidying a vocabulary.
88. **A document that describes the CODE keeps the code's identifiers.** The vocabulary rule covers the eleven reader-facing documents only. Rewriting prose around `PortalCrossingService` would make the documents disagree with the source, which is worse than an old word.
89. **Measure paragraphs, not source lines.** A hard-wrapped document hides a wall behind short lines; a one-line-per-paragraph document reports the paragraph. Threshold 700, grounded in the documents already rewritten for readability, which top out at 542.
90. **A readability rule makes somebody read the paragraph, and reading it finds the lie.** Two superseded rules were found this way, neither of which anybody was looking for: gate and portal as one word, and nothing-ever-crosses-on-its-own after incursion was added.
91. **Retiring a def means retiring every rule only it could satisfy.** A distortion counter tested for a beacon retired three checkpoints earlier, so the outcome was unreachable and no checker could see it.
92. **A Building is moved by despawning and respawning, never by writing `Position`.** Its cells are registered in the map's thing grid at spawn.
93. **Core's `ScenPart_StartingThing_Defined` minifies its own output**, and `MinifyUtility.TryMakeMinified` passes a non-minifiable thing through unchanged. An uncrated building in a cargo hold is a thing nobody can pick up.
94. **`CompLifespan.age` is a public field.** A Core glow pod dies after 1,200,000 ticks; holding a designated one at zero leaves every other glow pod in the game alone.
95. **Count the caps, not the cap.** *"lets not limit the amount"* named one limit and there were three: per room, per crew at dispatch, and per recipe batch.
96. **Core keeps facility-link geometry on the FACILITY side.** `CompProperties_Facility` is `maxDistance = 8f`, `requiresLOS = true`; the consumer comp carries one field and no control over either. Long-range, wall-transparent links must be our own record, or vanilla research linking changes for everyone.
97. **A def name that reads correctly can still be wrong, and nothing will tell you.** `Multianalyzer` is a ResearchProjectDef; the building is `MultiAnalyzer`. RimWorld's XML loader validates neither, so the wrong one loads clean and matches nothing. **Enumerate the installed data.**
98. **A rule and its exemption must both be provably non-empty.** The same-power-net rule applies only to things with a power comp. If every candidate were powered the exemption would be dead code; if none were, the rule would be. Assert both halves.
99. **State what already works before building it again.** Six of the nine items in this direction were already satisfied by rules written for the original three providers.
100. **A ladder must be at least as long as the tier it declares.** `portalWindowTierProjects` held one rung while `portalIndefiniteTier` was 4, so the top of the gate's own capability ladder was unreachable for the whole life of the mod. **Every individual value was valid**; the fault existed only in the relationship between two settings in different files. Covered by `proof-tier-ladder.py`, which reads the ladder from the source and the rungs from the defs.
101. **Fungible currency cannot express what a branch has learned.** Insight bought the same thing whatever produced it. Completed logs are the qualification and insight is only the price; a spent currency is gone and a completed log is not.
102. **Check a qualification before charging for it.** `ProjectQualificationFailureKey` runs ahead of the insight deduction, so a branch short of logs is told which kind.
103. **Custody is a place, not a receipt.** The retired check asked whether an evidence case existed somewhere at headquarters and never asked where the book was. A rule that can be satisfied without the thing it is about being anywhere in particular is not a rule.
104. **A prerequisite chain needs a cycle check, transitively.** A cycle is unreachable content in which every individual def looks completely normal.
105. **ARCHIVE BEFORE REMOVING. Always.** A removal was made by deleting a tuned def field, a const and a keyed string outright, with no `historical-content/` archive. The owner stopped it: *"how tf do you know we didnt need that shit coded up correctly and wasnt unfinished work"*. **The conclusion was right and the method was wrong**, which is the worse failure because it looks like progress.
106. **ASK AT A FORK EVEN WHEN THE READING SEEMS OBVIOUS.** Whether *"offeres and trades"* covered a hiring applicant and a purchase quote was a real fork with two readings. It was guessed, not asked, and finished code was deleted on the strength of the guess.
107. **The only clock is the gate.** No mission, quest, offer, contract or trade ever expires. A delay, a cooldown and a timestamp are all fine; a deadline is not. Enforced by `check-campaign-absolutes.py`.
108. **Every offer carries two or more routes to success**, of at least two different kinds. Enforced before the content exists, so the first offer ever written has to satisfy it.
109. **A clock that bounds nothing is pure pressure.** Both retired offer clocks sat beside a count cap that already bounded the pool. Check what actually bounds a list before believing a timer is load-bearing.
110. **Never widen a rule so that existing text passes.** `banned` and `superseded` were briefly added to the deadline-negation list and taken straight back out; they would have masked a real promise sitting near either word.
111. **Contact is a state on the branch, not a property of a scenario.** `corporationContact` is saved per branch; `beginsInCorporationContact` decides where a start opens. Async Industries begins true, the other two false. **One-way — there is no method to revoke it.**
112. **Our research layers on the shared RimWorld tech tree and never forks it.** Owner: *"the samw universial rimworld tech tree of all our mods in the collection on top of our mod"*.
113. **The authored route floor is assembled BEFORE capability is consulted.** If deriving returns nothing, a request must still offer two ways through. The safety property is the ordering, not the count.
114. **Two routes of the same kind is one route written twice.** A request needs two routes of two DIFFERENT kinds, or the rule is satisfied by text rather than design.
115. **Enforce by absence where you can.** `RimroomsRequestDef` has no deadline field, so one cannot be configured on. Stronger than any check that a value is unset.
116. **Enforce an absolute in two places.** `ConfigErrors` catches a def arriving from a patch or another mod after shipping; a checker catches one in this repository before it ships.
117. **When a rule bites your own design, redesign — do not carve out an exception.** The hinge as charted would have had every route of one kind. The carve-out was tempting and would have been the same failure as widening a negation list. The redesign is better than what it replaced.
118. **A `ThingDef` does not have to live in a file named `ThingDefs*`.** `TextBook` is in `Core/Defs/Books/BookDefs.xml`. A proof that indexes by filename reports correct content as broken, and the obvious response is to "fix" something that works.
119. **An unknown enum-ish string fails silently.** `CompletedLogCount` returns 0 for a log kind it does not recognise, so a typo produces a route that can never be satisfied and never complains. Assert the vocabulary.
120. **The chart is living and must be corrected when it is wrong.** Four corrections this checkpoint, including one where the chart contradicted an owner answer given after it was written.
121. **One generic mechanism beats N typed effect fields.** A `public bool unlocksSomething` tells you nothing about whether anything reads it. Capabilities are strings, and `proof-research-branches.py` asserts **both directions**: a grant with no read is a lie on the card, a read with no grant is dead code.
122. **An unlock nothing honours is worse than no unlock.** The def loads, the project completes, the card reads correctly, and nothing happens. Invisible without a proof.
123. **A plant that produces TWO failures means the proof checks both ends.** Renaming one side of a grant-and-read pair should fail as an orphaned grant AND an orphaned read.
124. **Do not add a hollow entry so a count looks complete.** Transport has no tier 0 project because it is DLC-optional; inventing one to make it eight would be the exact lie the proof exists to catch.
125. **A capability is neither a def nor a keyed string.** `check-package-integrity.py` and `check-keyed-strings.py` both had to be taught that, and both defer to the proof, which catches what neither can see.
126. **A dead PROP is more dangerous than dead code.** It reads exactly like a live one: a plausible name, a sensible default, a validation rule implying somebody cared. `reserveChargePowerWatts` and `returnReserveCapacityWattDays` were declared, validated and read by nothing since 0.9.1-dev.
127. **A property and a field differing only in casing is a trap.** `ReturnReserveCapacityWattDays` read the battery; `returnReserveCapacityWattDays` read nothing. Same class, one character apart.
128. **A validation can guarantee nothing and still look like a guarantee.** The retired clause compared costs against a nominal capacity unrelated to the battery a player binds.
129. **A deeper tier SUPERSEDES rather than stacks.** Read sites check the deeper capability first and fall through, so a card that says "twice as long" means twice.
130. **When a new assertion fails, ask whether the assertion is wrong first.** The depth rule failed on the gate ladder, which is linear by design. The assertion was restated; the ladder was not widened to satisfy it.
131. **UNUSED IS NOT UNWANTED. Wire it, do not retire it.** Owner, verbatim: *"make sure shit isnt unused it was put there for a reason"*. **A value nobody wired is a job nobody finished.** Three gate props were retired across 0.11.4 and 0.11.5 and all three were restored; two are now wired. This is the **second** correction of this shape — see 105, about deleting tuned values.
132. **Sweep the class, do not grep for one name.** The first two dead props were found by stumbling. A sweep of all seventeen gate props found the third **and cleared one an earlier grep had wrongly called dead**, because that grep excluded every line containing `public ` and threw away the property wrapper reading it.
133. **A cost must not become a trap.** Idle draw stops above the emergency-return reserve. A flat battery is a cost a player can see; a crew that cannot be recovered is not, and nothing would have warned them.
134. **When two readings of a value are both defensible, ask.** `reserveChargePowerWatts` is restored and deliberately **not** wired: the reserve is a Core battery RimWorld already charges, so the phrase either duplicates Core or means something else. Guessing would invent a mechanic.
135. **A reversed dated record is annotated, never rewritten.** The 0.11.4 archive opens with a note that the decision was reversed and its body is untouched.
136. **A live read site is not a live effect.** Three tier 2 unlocks were deleted before being written because the knobs they moved were a one-second wait, a cap of 100 orders and a quantity limit already set to a million. **All three would have passed `proof-research-branches.py`**, because the capability would have been read by real code. Open the file, find the value, and ask what a player would observe.
137. **A number displayed and a number spent must come from one place.** Idle draw is read by the gate’s readout and by the tick that drains the reserve; research applied to one and not the other would make the readout lie, silently, because nothing compares them.
138. **Check that a new tier does not switch off the tier below it.** Forward Dispatch halves the dispatch delay, and the lead-time clamp had to be moved onto the effective value or Relays would have stopped biting for exactly the branches holding both.
139. **An orphaned def is more dangerous than a missing one.** Five `RR_*Staff` `PawnKindDef`s were authored, loaded and validated every run and read by **nothing**, and the queue called them *"unbuilt"*. Built and orphaned looks finished from every angle except the one nobody checks. **Third instance of invariant 131 this session.**
140. **A guarantee must not be an incident.** *"Facilities never die"* does not admit the two questions a storyteller asks — whether, and when. The floor is deterministic; the flavour is paced. Owner decision, verbatim: *"Both - guaranteed floor, storyteller flavour"*.
141. **Never ship a `StorytellerDef`.** It is an exclusive slot the player would have to give up Cassandra or Randy for, and it needs portrait art the no-new-art rule forbids. **There is no intelligence in one to borrow** — a `StorytellerComp` rolls a mean-time-between against wealth and population. The director is `IncidentWorker.CanFireNowSub`, which is ours without the slot. Asserted by `proof-incidents.py`.
142. **A proof must not punish an explanation.** The incursion claim failed on this mod’s own comment saying why incursion is excluded. Strip comments and ask about code — a rule that makes documenting a decision expensive teaches people to stop documenting decisions. **Second time this session an assertion was wrong and the code was right** (see 130).
143. **One table, two scales.** The relief crate and the courier crate are one corporation with one warehouse. Two tables drift the first time either is tuned, and the letter keeps promising the old one.
144. **A ledger patch must INSERT, never replace.** The 0.11.7 script’s helper consumed a `FINALIZED.md` section heading because its replacement text did not re-include the anchor. `FINALIZED.md` is append-only; every patch re-includes its anchor and the diff is checked for removed lines.
145. **An assertion written from what the code LOOKS like is a guess; one written from what the code THROWS on is a fact.** All three wrong assertions this session came from the first kind — the depth rule, the incursion word-search, and the wall rule that would have failed the headquarters that ships and works. See 130, 142.
146. **A start layout is a new-game crash nothing else can see.** `GenStep_Headquarters` throws on a wall collision, a door with no wall, or a bad rectangle, and the build and all eight checkers pass regardless. **Read building sizes from Core’s own `ThingDef`s** — a 2×2 generator on a 1×1 assumption put three crashes in a layout that built clean.
147. **A sealed room does not throw.** The map generates and part of it can never be entered, forever, silently. Flood-fill every start from its arrival cell.
148. **Exactly one start begins in corporation contact.** Async Industries. The other two earn it, and until they do there is no clean-up team and no courier. That absence is what makes those openings frightening, and it is asserted.
149. **Core already lets a scenario choose the starting map’s generator.** `Game.InitNewGame` reads `initData.mapGeneratorDef ?? settlement.MapGeneratorDef`, and `GameInitData.mapGeneratorDef` is a public field. **No Harmony is needed to open a game anywhere**, and this mod had already been assigning it from the start def.
150. **Share the half that carries the promises.** The coordinate shell — rock to every edge, `RoofRockThick` over every cell, rooms carved out — is one implementation used by both generators, because invariant 13 lives inside it. The furniture differs; the shell never may. Same reasoning as the anomaly effects at 0.11.8.
151. **A `workerClass` or `genStep Class` that does not resolve fails as ORDINARY BEHAVIOUR, not as a crash.** A missing genstep gives the player a normal colony while the description promises the Backrooms. Assert that every class named in XML exists in source.
152. **A claim that can fail for the wrong reason can also pass for the wrong reason.** The natural-depth ordering claim was a string-index search over a variable name; renaming the variable made it fail open. **Key an assertion off the thing that actually happens** — a refusal, a keyed string, a def name — never off an expression’s spelling. Fourth assertion corrected this session and the first of this kind (see 130, 142, 145).
153. **Cap the free doors, never the way home.** `MaximumNaturalDepth` is checked after the way-out attempt. Capping both directions makes the deepest natural band a trap, which invariant 28 forbids.
154. **Open-ended is a constraint on the content, not a mood.** Owner, verbatim: *"this is all open eneded they can play how they choose"*. A tutorial line offers and describes; it never requires an order, and a step already done by a player who got there first must read as done rather than skipped.
155. **A portal is its own door cell and reserves nothing.** No radius, no claimed cells, no protected zone. Owner, verbatim: *"in the real world you can mine and build and explore directly behind the gates with out actually effecting the gate"*. The only placement rules near a gate belong to **linked equipment**, which has a reach of its own. Enforced by `proof-portal-footprint.py`, including a banned-name check.
156. **A snapshot and a live check, in two different files, is a silent failure waiting.** The approach cell was frozen at registration and validated forever; a wall on it bricked a gate for the life of the save. **Both files read correctly alone.** When a value is snapshotted, ask what happens when the world moves under it.
157. **Find every read site before changing a shared value.** Re-deriving the approach cell live everywhere — the obvious fix — would have tripped the crossing receipt’s equality guard, which is what stops a transfer losing a pawn. The repair is skipped while a crossing is in flight because the read sites were enumerated first.
158. **Sweep the exposed surface, not the fields.** `MinimumPowerHeadroomWatts` applied a research capability and **was itself read by nothing**, so the tier 0 Facilities unlock promised a change and delivered none. `proof-live-effects.py` walks every public property that reads `GateProps` and found two more. **A live read site is not a live effect** (invariant 136); this is the sweep that catches it.
159. **A dead accessor and a dead value are different problems.** `EmergencyReturnCostWattDays` was live as a field and dead as a property: the number reached the code and never reached the player. The fix is to display it, not to wire it again.
160. **Never build a keyed string at runtime.** `"RR_Hint_" + id` cannot be verified in either direction, so a typo ships as a raw key on screen. `check-keyed-strings.py` refuses it and is right to.
161. **Gate an opening requirement at the opening, never in the tick.** `NativeBindingFailureKey` is read every tick; a supply check there would emergency-return a crew already across. A lapse blocks the **next** opening, never the current one.
162. **Acquisition is the game’s; recognition is ours.** RimWorld already settles a second tile and this mod’s topology already emerges a crew elsewhere. A remote site is **registered, never created** — `proof-remote-sites.py` bans `WorldObjectMaker.MakeWorldObject`, `GetOrGenerateMap`, `SettleInEmptyTileUtility` and `MapGenerator.GenerateMap` from that source. Inventing settling would be fighting Core for nothing and first to break on an update.
163. **A recurring cost must be a ratio of the branch’s own economy, never an absolute.** Async runs on $25,000 a day of overhead and the Store on $1,500. One number is a rounding error for one and ruinous for the other; a share of a number each start already tunes is correct for both for free.
164. **A coordinate is never a base.** It is reached through a gate, it is transient, and it is not the player’s to keep. A surcharge that counted coordinates computes zero and looks like progress.
165. **Extend the one predicate, do not thread a second one.** `OwnsMap` has 30 call sites across 16 files; its third clause is what makes work, gates and emergence anchors all reach a registered site at once. Check that **every** consequence is wanted before widening it.
166. **A bug that only exists once you add the feature is the hardest kind to find, because it is not there while you are looking.** The procurement redirect updated the receiving zone and never the receiving map — harmless with one legal map, a shipment lost for ever with two. **Read every WRITE to a record before changing what the record may hold.**
167. **Check what your claim survives before believing it.** The on-the-books claim counted a refusal string; a planted fault removed the guard, left the string, and the proof passed. **Key a claim off the thing that happens** — a guard expression, a refusal, an assignment — never off a token near it. Second instance in one day (see 152).
168. **Permitted is not reachable.** Widening procurement without widening the stockpile menu would have left site delivery legal and unofferable. Every widening needs its surface widened in the same checkpoint.
169. **A crew left on the far side is stranded, never taken.** Owner, verbatim: *"turning off a company gate with pawns inside doesnt lose control of those pawns they have to survive till a reconnection is made so they can escape"*. `ShouldRemoveMapNow` returns false **unconditionally** — any condition there is a condition under which somebody’s colonists vanish. No gate source may ever call `PassToWorld`. Asserted by `proof-stranded-crew.py`.
170. **A claim with a conditional fallback is a claim that can be trivially true.** The ordering claim keyed off a method name absent from the file and collapsed to a tautology. **Third fail-open in one day, all three found by fault-planting and none by reading** — which is what fault-planting is for (109, 152, 167).
171. **Gate a requirement where it bites, not where it is convenient.** Staffing is checked at a shipment’s **arrival**, never at its ordering: gating the order punishes planning, and gating nothing makes the rule a sentence in a document.
172. **A gate runs on the equipment beside it.** `thing.Map == parent.Map` is what makes a remote gate a real facility rather than a remote control for the headquarters. Widening *where* a gate may stand must never widen *what it may draw on*.
173. **Exclude by construction, not by a check somebody must remember.** A designated gate cannot appear in a coordinate because `OperatesAt` admits only registered places and a coordinate can never be registered. Invariant 12 then holds with nothing to forget.
174. **Two questions may share a place-set and must not share a name.** `OperatesAt` and `CanReceiveDeliveryAt` agree today and are different questions; one implementation stops them drifting, two names give the difference somewhere to go when it arrives.
175. **A def shape with content and no reader is not a feature.** `ConfigErrors`, a checker and a proof can all validate a def while nothing in the game consumes it — which is how the entire campaign shipped twice as content nobody could see. **Assert that a content surface is read from outside its own definition**, and restage the defect as a planted fault.
176. **Where two route kinds could resolve to the same expression, split them on what actually differs.** A def rule demanding two different kinds is satisfied by text alone if the runtime asks one question twice. Document is the paperwork and survives the witness dying; Testify is the person and survives the book burning.
177. **Re-measure every count in the handoff; never carry one forward.** The C# file count was wrong by two for five checkpoints, exactly as the assembly hash was. A plausible number is never checked by reading.
178. **Narrowing what a rule measures is legitimate; softening the rule is not.** A word search matching a comment is the wrong population (invariant 130). Strip the comments — then **plant a fault to prove the narrowing did not blind it.**
179. **Grep the ledger before asking the owner anything.** Two of the three questions in the 0.12.10 handoff had already been answered and recorded, and one of them was re-asked the turn after that handoff shipped. One `grep` across `.local/register/` and `docs/` is cheaper than the owner’s patience.
180. **Zero hard dependencies and Core-only are different claims.** The package must load and run against Core alone — a build property. The install it is *designed for* is the 294. Never write an option, doc line or design argument treating a vanilla install as the audience. *"wtf are you talking about core only we have 294 recommend mods you fuck!!!!"*
181. **Absolute state is permanently true once true.** A check like *"does the branch hold twenty meals"* is right for a request asked **once** and wrong for anything repeatable, where it pays out on acceptance. A repeatable job records where it started and asks for that much **more** — keyed by label key, never by list index.
182. **A route naming something that does not exist can never fire, and nothing says so.** A `logKind` typo makes the measurement zero while still counting toward the two-different-kinds rule, so every checker passes and the request ships promising two ways and having one. **Parse the content and assert each route names a real def.** Invariant 49.
183. **A filter clause that cannot refuse is a hollow knob.** Assert no arm of an eligibility switch is `return true`. Invariant 136 has already deleted four projects and three constants here for the same reason.
184. **A route against work already finished is satisfied on sight.** Exclude the completed case at the point of offering, not only at the point of measuring — otherwise the offer itself is a payout button.
185. **A proof failing because its subject MOVED is the proof working.** Retarget it and say so. A claim that survives an arbitrary refactor of the thing it describes is keyed off nothing.
186. **Count coverage per category, never in total.** Eighteen generated families is satisfied by eighteen copies of one arc. The claim that matters is that **each** arc has somewhere to put work, and only a per-arc count catches a family moving between them.
187. **Two documents can describe the same thing from two directions and nobody notices.** Arc 5’s *"still unwritten"* list — relay stations, caches, leases, resupply, evacuation — had had research projects since 0.11.6. **Before building a named item, grep the def names for its nouns.**
188. **A queue nobody re-measures cannot answer "how much is left".** 178 rows carried a status that was never re-checked; 114 of them were built. **Re-measure the queue against the code before answering any question about progress**, and append the evidence so the next reader can re-check rather than trust.
189. **Close a row with a named read site, or leave it open.** A flip on a guess is worse than a stale row, because it removes the thing from view. Anything unverifiable stays open.
190. **Say when a row cannot close without the owner.** Performance, balance, the 294 profile and the compatibility report all need a launch, and only the owner launches. Marking that is honesty, not deferral — and `DEFERRED.md` still gets no rows.
191. **A `FactionDef` is world configuration, and that is the whole of the permission.** It may reuse existing pawn kinds and existing icon paths and nothing else. **Enumerate the installed game for both** — a `factionIconPath` Core does not ship loads clean and fails at runtime, because `ContentFinder` returns null and the faction simply has no icon.
192. **`settlementGenerationWeight` 0 for anything this mod adds to the world.** Seven settlement-generating factions would change every world map every player generates, alongside 294 other mods. An interest group has people and intentions, not towns.
193. **Some correctness is achieved by NOT setting a field.** `FactionDef` has no starting-goodwill field, so *all neutral* is the default and the risk is a flag quietly appearing later. **Assert the absence**, because nothing looks wrong when it does.
194. **`ContentFinder` resolves across every loaded mod, so a folder scan is not ours.** `UI/Menu` is a generic content path; without a name prefix another mod’s art appears in our slideshow. **Scan the folder, then filter by prefix**, and say at the site that the prefix is load-bearing.
195. **A note nobody can act on is noise, and noise is how a real finding gets scrolled past.** Both menu textures were reported unreferenced on every run for months because the checker could not follow `Get(variable)`. **Teach the checker the API** rather than leaving a permanent false note.
196. **When a checker flags something legitimately new, fix it by its own design.** `check-keyed-strings.py` classifies by **call site, not spelling**, so a texture prefix counts as internal only when it is passed to `StartsWith` — and the narrowing was fault-planted to prove it still catches an undeclared key.
197. **A drop-in folder needs a proof that nothing dropped in can fail silently.** A slide named without the prefix is loaded by nothing and shown to nobody, and no build, checker or log says so. When content arrives from outside the code, **assert the naming contract** and plant a stray file to prove it fails.
198. **Validate delivered binary assets structurally, at build.** A truncated PNG fails when Unity reads it, long after the build reported success. Check the signature **and** that `IEND` is the final chunk. My first version of that check compared the last eight bytes literally and condemned every file, including ones already shipping — **the check was wrong, not the files.**
199. **Provenance for generated art is a release obligation, not a nicety.** Steam requires AI-content disclosure and menu images are the single exception to the no-new-art rule. `prompts-and-provenance.json` records tool and prompt per image, and a proof asserts it exists.
200. **A tier deleted for having no knobs is worth re-surveying once the systems land.** Tier 3 had nothing to move for four of seven branches at 0.12.5-dev and a real read site for **all seven** at 0.12.18-dev, because arc 5 wrote the systems in between. **Re-run the sweep; do not carry the old verdict.**
201. **A restraint is only a restraint if breaking it fails.** The per-coordinate frontier cap must never become a research knob, and shelter must never reach zero. Both are asserted and both were fault-planted — otherwise they are comments.
202. **Proximity is not the thing that happens.** A claim that looked for a capability name within 400 characters of a constant broke the moment a legitimate line was written above it. **Key off the assignment, the guard, the exit status — never off what sits nearby.** Fifth time.
203. **A grep for the words you expected, in the file you expected, is not a search.** The mineable-rock fill was marked *"confirmed unbuilt by grep"* while fully shipping, because the code says `Find.World.NaturalRockTypesIn` and contains none of the words searched for. **Condemning correct code on a failed search is worse than trusting a wrong comment.**
204. **`Named<X>("Foo")` on a TEMPLATE def returns null, silently, and a `??` fallback makes the wrong result look deliberate.** Core ships `Carpet` as a `TerrainTemplateDef` and generates `Carpet<Colour>`. The yellow rooms were wood plank flooring from the day they shipped. **Assert that every def a generator names actually resolves.**
205. **A filter that skips the case it guards against is worse than no check.** The floor claim excused terrains with no cost list as *"never built"*, which excused `PackedDirt` — the exact plant it existed to catch. **Only the planted fault found it; reading it would not have.**
206. **The mod register is GUIDANCE, not law.** Owner-corrected 2026-09-29: *"remmebr its not law but guidance"*. Consult it, let it shape the design, and say what it said — but a row does not veto work, and a checker built on it must only assert what is **structural**.
207. **Query the register by `trace`, not only by family.** The trace column names the **Rimrooms feature** a row bears on, which is the question the rule actually asks. It had no query until 0.12.20-dev, and that is precisely why it was the column that got skipped. **A column nobody can ask about is a column nobody consults.**
208. **A `PatchOperationFindMod` does not edit anybody’s files** — owner-confirmed. It patches the loaded def database at runtime and applies nothing when the mod is absent. What would breach *"WE ARE NOT EDITING OTHER PEOPLES MODS"* is **shipping their content here**, and that is what `check-register-compliance.py` asserts.

---

## The warning that matters most right now

**A check that cannot fail manufactures confidence, and every instance of it this session was
mine.** Four, all found by planting faults rather than by reading:

| What could not fail | Why |
|---|---|
| the natural-depth ordering claim | keyed off a **variable name**; renaming it made the claim fail *open* |
| the on-the-books claim | counted a **refusal string** that survived the guard being deleted |
| the staffing ordering claim | had a **conditional fallback** on a method name absent from the file, so it collapsed to a tautology |
| the whole proof runner | **grepped for `PROOF HELD`**, and four live proofs end `PASS:` — so four went unrun for most of the session |

The first three were caught by fault-planting. **The fourth was caught only by writing this
handoff**, which is the argument for writing it.

### The rules that come out of that

- **Key a claim off the thing that happens** — a guard expression, an assignment, a refusal, an
  exit status. Never off a token near it, a variable's spelling, or a count of a string.
- **A claim with a conditional fallback can be trivially true.** If the anchor is missing, the
  whole expression degenerates and says nothing.
- **Plant the fault and confirm it fails for the RIGHT reason.** A claim that fails for the wrong
  reason will pass for the wrong reason too.
- **Check the plant landed.** A patch script asserts before it writes, so a mistyped anchor plants
  nothing — and the proof passing afterwards proves nothing.
- **A wrong claim is far better than an unfalsifiable one.** Three times this session a corrected
  claim was *also* wrong on its first try and failed immediately. That is the system working: the
  wrong one tells you.

**And the older lesson still holds:** when a proof only ever confirms, suspect it. Two designs
changed *because* a proof disagreed — the spin-up decay rate, and revisit displacement firing
every single time.

---

## Standing method

- **Check the register first** (LAW). `python tools/register-query.py family <x>`, then the per-mod review under `docs/research/reviews/mods/`. Say what you checked.
- **Read the prep work.** `UNIVERSE_ADAPTATION.md` had an unbuilt item nobody had noticed for the whole project.
- **A TODO item carries all its related work.**
- **At a fork: ask immediately**, multiple choice with a write-in. Never flag.
- **State what already works before building it again.**
- **Name what is not done, in `TODO.md`, in the same checkpoint.**

## Read these first

1. `docs/NOW.md` — this file.
2. `docs/TODO.md` — every owner direction verbatim.
3. `.claude/CONSTRAINTS.md` — the LAWs, including the register LAW.
4. `docs/GATE_0_DECISIONS.md` — D1–D9 **and** decisions 13–25. D1 changed.
5. `docs/implementation/CONNECTED_WORK_CORE_API.md` — pinned Core facts.
6. `docs/PUBLISHING.md` — the cascade. Follow it literally.

## The checkpoint ritual

1. **Check the register** for the system family being touched, and record what it said.
2. Read every file in full before editing.
3. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — zero warnings. It refuses if csproj and `About.xml` disagree, so bump both.
4. `CHANGELOG.md` in plain player-facing language.
5. Implementation record under `docs/implementation/`.
6. Ledger: `TODO.md`, `NOW.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`.
7. **Every checker** (NINE): `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, `check-campaign-absolutes.py`, `check-doc-conformance.py`, `check-register-compliance.py`, `research/audit-gate0.py`.
7b. **Every proof (TWENTY), by exit status:**

```sh
for p in .local/register/proof-*.py; do python "$p" >/dev/null || echo "FAILED: $p"; done
```

   **Do not grep their output.** Eleven end `PROOF HELD` and four end `PASS:`; grepping one
   phrasing skipped four live proofs for most of one session. Exit status is phrasing-independent.

   The set: `displacement`, `facilities`, `facility-relief`, `fit`, `gate-links`, `incidents`,
   `interior-resource`, `live-effects`, `menu-slides`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-generation`,
   `request-line`, `research-branches`, `spinup`, `starts`, `stranded-crew`, `tier-ladder`,
   `universe-factions`.

   **`patch-*.py` in that directory are one-shot edit scripts, not proofs.** They were once named
   `proof-*` and re-running one would try to re-apply a landed patch and fail confusingly.

   **Sanity-test any new claim by planting a fault** and confirming it fails **for the right
   reason**. Three claims this session passed a planted fault; all three were mine.
8. **Determinism**: delete `obj/` and `bin/`, rebuild **twice**, hashes must match.
9. Commit once atomically; cascade to `Prep`, `Develop`, `Main` on **both** remotes; **read back all eight refs**.

## Gotchas learned the hard way

- **XML comments cannot contain `--`.** Hit **five times**. The checker names the rule and the line.
- **Bash heredocs mangle `\n` and break on apostrophes.** Hit **TEN times**, the last three after this line already said so. **Stop reaching for a heredoc when the payload contains a backslash escape or an apostrophe** — use the Write tool, and a message file for commits.
- **A GitHub push can silently drop some refs.** Read back all eight, every time — it happened once this session.
- **A failed `assert` in a patch script means nothing was written** — the write comes last. So a fault-plant whose anchor was wrong plants nothing, and the proof passing afterwards proves nothing. Check the plant landed.
- `git` index lock goes stale; `rm -f .git/index.lock`.
- **`cd` inside a Bash call persists.** Absolute paths.
- Package manifests are UTF-8 **with BOM** — `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe -t <FullTypeName> "<RimWorld>/RimWorldWin64_Data/Managed/Assembly-CSharp.dll"`. **Empty output means the type name was wrong.**
- C# 7.3: no target-typed conditionals.
- **A def field emitted in XML that no class declares is ignored silently at load.**
- Core's `StockGenerator_Category` has **all-private fields**. `GenRecipe.PostProcessProduct` is **private static**.
- `SetTerrain` **clears** the colour grid. `CompFlickable.SwitchIsOn` has a **public setter**.

## Open owner questions — THERE ARE NONE

**All three reserved decisions were answered on 2026-09-29.** Nothing in this project is now
waiting on the owner. Every remaining item in the queue above is buildable.

### Answered 2026-09-29 — the last three

- ~~**How a generated request picks its routes**~~ — **a declared pool, filtered by capability.**
  A family declares a route **pool** in XML; generation filters it to what the branch can take,
  and **if fewer than two routes of two different kinds survive, the request does not generate.**
  Unblocks queue item 3, closes chart §6 item 3.
- ~~**Whether the eight branches unlock in any order after the hinge**~~ — **all eight, any
  order.** Each branch keeps its own internal tier ladder; no branch gates another. Closes chart
  §6 item 2.
- ~~**The public face**~~ — **everything, including Playwright driving Steam.** The concern was
  stated before the choice and the owner chose it anyway, so it stands and is not re-litigated.
  Still last, and it needs the owner present for the Steam session.

### The question that was never open, and I asked it anyway

**The adjacent-door-run fallback was owner-answered on 2026-09-29 — *"BOTH paths"* — and I put it
back on the table one turn after the handoff audit fixed exactly this defect.** *"wtf are you
talking about core only we have 294 recommend mods you fuck!!!!"*

Two lessons, both load-bearing:

1. **Search the ledger before asking.** `grep` for the subject across `.local/register/` and
   `docs/` costs one command. The answer was sitting in `todo-089.py:37` in capitals.
2. **Zero hard dependencies and Core-only are not the same claim.** The package must *load and
   run* against Core alone — that is a **build** property and it holds. The install this mod is
   *designed for* is **the 294**. Never write an option, a doc line or a design argument that
   treats a vanilla install as the audience.

### Closed earlier this session, so nobody re-asks

- ~~**`reserveChargePowerWatts`**~~ — **a supply requirement before opening.** Wired 0.12.4-dev,
  and wiring it revived `RR_Cap_ReserveDiscipline`, a tier-0 card that had promised an unlock and
  moved nothing.
- ~~**The 250 W idle draw**~~ — **kept.** Confirmed as the intended behaviour; no change needed.
- ~~**Natural gates indestructible**~~ — **relaxed by the owner** to a confirmation warning.
  *"dont worry about it, can we at least do a rim style pop up warning"*.
- ~~**The solo/group tutorial line**~~ — **option three:** no request line until contact, plus four
  hints in the survivors' own voice. None is an objective.
- ~~**The solo/group exit**~~ — **two maps, coordinate is real.** Superseded the earlier
  seed-tile answer once `RimroomsPortalNetwork.Register` was read.
