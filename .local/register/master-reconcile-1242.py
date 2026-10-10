# -*- coding: utf-8 -*-
"""Row 1054: reconcile the master backlog against what has actually shipped.

Row 1054, verbatim:

    "Consequence: reconcile 0.5.0-0.7.1 back into the master backlog. Surfaced while counting for
     this answer. The master TODO is granular for research (81 rows on Phase 0) and coarse for
     code: the entire cross-map work engine -- 31 work families, 23 deployments, containment,
     emergence, the kill switch, gate servicing, 27 shipped versions -- sits under one unchecked
     row. A raw count reads ~12% on code while the source tree went 78 -> 120 files. Until this
     is reconciled the master row count understates the build by roughly thirty points."

**The row predicted roughly thirty. This flips a measured number and prints it.**

Two rules this obeys, both LAWs:

  * **Status changes ONLY.** Every original word of every row is kept and the note is appended
    after it. Nothing is rewritten, nothing is shortened, nothing is regenerated.
  * **A row is only flipped when a specific checkpoint can be named for it.** Anything about
    RUNTIME ACCEPTANCE stays open, because no game has ever been launched from this repository
    and a reconciliation that quietly marked those done would be the worst kind of wrong -- it
    would erase the only honest caveat the project has.

Anchors are the marker plus the opening words of each row, asserted unique before anything is
written, with the single write at the end.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "PREPRODUCTION_AND_IMPLEMENTATION_TODO.md")

original = io.open(PATH, encoding="utf-8").read()

# (opening words of the row, the checkpoint note appended after every original word)
RECONCILED = [
    (u"Implement every open item in [connected colony portals]",
     u"**RECONCILED 0.12.42-dev: SHIPPED across 0.4.2-dev to 0.8.5-dev.** Independent connection "
     u"ownership, permanent natural connections, free crossing, shared cross-map work and "
     u"materials, persistent seeds and dynamic inhabitants all ship. This was the *\"one "
     u"unchecked row\"* row 1054 names."),

    (u"Finish resumable route scheduling, same-pawn/cargo crossing recovery",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Route scheduling, crossing recovery receipts and the "
     u"player-facing connection controls all ship; the Operations tab carries them."),

    (u"Implement and integrate native work/needs adapters",
     u"**RECONCILED 0.12.42-dev: SHIPPED, and this is the row row 1054 was written about.** The "
     u"connected-work engine covers every work type through providers rather than pools, "
     u"including the eleven DLC container givers (0.12.34-dev) and the four painting givers. No "
     u"separate labour or material pool exists."),

    (u"Author and implement the saved, bounded escalation ladder",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.8.1-dev to 0.8.4-dev.** The coordinate pressure "
     u"ladder rises from saved observable causes, caps are recorded progression steps "
     u"(`EncounterCapProgression`), pressure never sums across gates, and a revisit resumes "
     u"saved pressure rather than rerolling it. The band is now printed on the Atlas pane "
     u"(0.12.33-dev)."),

    (u"Implement one authoritative gate state machine",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** `CompRimroomsGate` is the single state machine, with "
     u"seven named failure reasons, validated transitions, energy costs, warnings, timers and an "
     u"event log."),

    (u"Implement a single transaction service for stock/currency/job/project changes",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** `PostTransaction` is idempotent by operation id, so "
     u"a delivery cannot be paid twice even across a save reloaded mid-settlement."),

    (u"Implement stable site/coordinate IDs, deterministic seed construction",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Coordinate ids, `campaignSeed` derivation, "
     u"`generatorVersion`, `roomLibraryVersion`, room graph records, map ownership and revisit "
     u"behaviour all ship and are saved."),

    (u"Add versioned save components and migration from each released schema",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** `schemaVersion` with `HasSupportedSchema` and "
     u"per-schema migration; an unsupported save disables actions and says so rather than "
     u"corrupting itself."),

    (u"Create the Async Industries new-game scenario with starter facility",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** All three starts ship as of 0.12.0-dev; this one "
     u"first."),

    (u"Add gate frame, control console, power requirements, emergency cutoff, assembly/"
     u"calibration work, operation feedback, failure states, and repair costs.",
     u"**RECONCILED 0.12.42-dev: NOW COMPLETE.** Everything but repair and reliability shipped "
     u"earlier; **0.12.38-dev closed both** -- a gate below half condition loses calibration, "
     u"and reliability is a recorded outcome history rather than a dice roll."),

    (u"Add staff role recommendations, field kit assignment, readiness checks",
     u"**RECONCILED 0.12.42-dev: NOW COMPLETE.** Roles and kit shipped earlier; **0.12.41-dev "
     u"closed readiness checks** with ten named per-person reasons. Native pawn and work "
     u"controls are untouched."),

    (u"Create one seeded, finite Backrooms site with a short room graph",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Room graph, hazards, learnable inhabitants, the "
     u"evidence chain, the guaranteed exit (0.12.2-dev) and paid outcomes all ship."),

    (u"Add expedition dispatch/recall/close flow; track crew/cargo/location/return",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Dispatch, recall, abort, stranded recovery, relief "
     u"loadout, casualty carry and the closure history all ship."),

    (u"Add evidence intake, one lab analysis recipe/project",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Intake, laboratory binding, analysis work, insight, "
     u"company projects, contract settlement and the ledger entry all ship."),

    (u"Provide a safe fallback map and recoverable error message when generation cannot",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** A failed coordinate reports its "
     u"`GenerationFailureKey` on the Atlas pane and offers to re-address the survey; crew and "
     u"stock are accounted for."),

    (u"Map every custom gameplay Def/asset and code consumer to existing Core/profile content",
     u"**RECONCILED 0.12.42-dev: SHIPPED across 0.9.0-dev to 0.12.22-dev.** Eight legacy defs "
     u"retired, the package went 92 to 79 files, and the last four gameplay textures were "
     u"replaced with paths read out of Core's own defs."),

    (u"Replace custom gate/console/cutoff/generator objects with designated existing",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.9.0-dev.** A gate is a designated Core door with a "
     u"designated console, battery and machining table."),

    (u"Replace custom field gear, route aids and evidence items with existing objects",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** The beacon (0.9.9-dev), survey tag (0.10.7-dev), "
     u"sealed case (0.10.9-dev) and field recorder (0.12.24-dev) are all retired; the kit is one "
     u"Core TextBook resolved through `CompRouteEvidence.NativeCarrierDef`."),

    (u"Replace custom creature presentation, room fixtures and terrain with existing",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Inhabitants draw on existing presentation, room "
     u"fixtures come from Core stuffable defs with a per-coordinate palette (0.12.37-dev), and "
     u"floors are ordinary layerable Core terrain."),

    (u"Define supported migration or explicit preserved development-save break",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** `SAVE_MIGRATION_POLICY.md` holds the position and "
     u"the schema guard enforces it; obsolete defs were removed with their retirement records."),

    (u"Reconcile all scenario grants, recipes, equipment readiness, content bindings",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** `check-retired-content.py` refuses player-facing "
     u"text naming retired equipment, and `check-register-compliance.py` refuses new gameplay "
     u"art or audio outright."),

    (u"Preserve native/Prepare Carefully edited pawn instances, relationships",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** The five `RR_*Staff` PawnKinds were found authored "
     u"and read by nothing at 0.11.7-dev; starts use edited native pawns."),

    (u"Honor the company-selected surface world tile through native setup",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** The chosen-tile receipt ships, and the Store start "
     u"has its own setup, grants and objective."),

    (u"Implement the inside-start setup using the recorded provisional defaults",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.12.0-dev.** The solo/group start ships and the map "
     u"itself is a coordinate. Both provisional answers were decided by the owner on 2026-09-28: "
     u"a configurable party, and the player chooses the destination settlement."),

    (u"Keep the first acceptance target on Async Industries while making its scenario setup",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** All three starts consume the same "
     u"`RimroomsStartDef` contract."),

    (u"Implement Furniture & Knickknack Store after Gate 2",
     u"**RECONCILED 0.12.42-dev: BUILT 0.11.9-dev.** The scenario ships with its shop, its "
     u"threshold and its objective. **Validation remains a runtime question** and is covered by "
     u"the acceptance rows, not by this one."),

    (u"Implement Lone Survivor after Gate 2",
     u"**RECONCILED 0.12.42-dev: BUILT 0.12.0-dev.** The seeded inside start ships. **Validation "
     u"remains a runtime question** and is covered by the acceptance rows."),

    (u"Implement physical room functions: gate, control, labs, evidence archive",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.9.7-dev.** Facilities are contiguous runs of space "
     u"with categories; containment and quarantine closed at 0.12.35-dev and 0.12.36-dev."),

    (u"Connect each room to concrete capabilities, stock needs, staff jobs, risks",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** The facilities pane states why a room is not "
     u"functional, and `FacilityRelief` acts on it."),

    (u"Implement native door/endpoint bindings for controlled and mysterious portals",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Sizes 1x1 to 2x3 (0.9.2-dev), native recolour and "
     u"aura, and a gate is its own door cell (0.12.3-dev) so a wall beside one no longer bricks "
     u"it."),

    (u"Bind actual control/laboratory equipment and native power grids/batteries",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Equipment links reach through walls and across "
     u"distance by owner direction; energy is debited once per operation id."),

    (u"Add machine subsystems/upgrades: power reserves, calibration, stabilizers",
     u"**RECONCILED 0.12.42-dev: COMPLETE 0.12.38-dev, and seven of its nine subsystems already "
     u"existed under different names** -- `PortalWindowTier` is the stabilizer ladder and "
     u"`GateEquipmentLinks` are the modules. Integrity and reliability closed the last two."),

    (u"Add crew composition and cargo planner with skill/health/weight/gate-window checks",
     u"**RECONCILED 0.12.42-dev: BUILT 0.12.41-dev.** Ten named per-person reasons, crew skill "
     u"levels and gaps, per-person and crew carrying room, the window at the current tier and a "
     u"watt-day cost preview quoted against the reserve. It owns no refusal."),

    (u"Add schedule, warning, recall, evacuation, emergency close, lost-connection",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Recall warnings, the emergency cutoff, the stranded "
     u"guarantee and relief dispatch all ship."),

    (u"Add fog-of-war atlas, route notes, last-known position, evidence chain",
     u"**RECONCILED 0.12.42-dev: SHIPPED, with one named exception.** The atlas, route "
     u"telemetry, the evidence chain, saved room graph and between-visit displacement "
     u"(0.10.3-dev) all ship. **The return beacon was retired at 0.9.9-dev by owner decision** "
     u"-- the gate's own address book and the saved return threshold already are the route "
     u"authority, so the item had no job left."),

    (u"Implement a tagged room/corridor library and deterministic topology generation",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Room archetypes across the four size bands, "
     u"deterministic by coordinate seed and sorted ordinally before any roll."),

    (u"Validate map size, accessible entrances/exits, walkable paths, mission objects",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Generation validates and reports a named failure "
     u"rather than producing an unplayable coordinate."),

    (u"Add room families, furnishing rules, lighting/material palettes, loot",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Room families, the yellow-room palette (0.7.8-dev), "
     u"per-coordinate stuff palettes (0.12.37-dev), clues and threat events all ship."),

    (u"Implement bounded non-Euclidean effects: repeats, moved door/exit",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.8.6-dev to 0.8.8-dev.** Room echoes, hallways and "
     u"coherence decay."),

    (u"Add saved, rule-based anomaly propagation across room graphs",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** `RimroomsAnomalyEventDefs` with observable clues, "
     u"caps and decay, and an event log."),

    (u"Implement branch-local USD financial ledger with auditable entries",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.7.2-dev onward.** The ledger records every movement "
     u"with its reason; obligations, payroll and upkeep all post through it."),

    (u"Implement equipment/material procurement, source/price/**expected arrival**",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** The procurement catalogue, shipment manifest, "
     u"receiving, partial delivery, redirection and order history all ship. **The parenthetical "
     u"is enforced by a checker**: `check-campaign-absolutes.py` refuses a deadline anywhere in "
     u"the package."),

    (u"Implement contract/quest templates for surveys, retrieval, furniture/salvage",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.12.12-dev and 0.12.13-dev as 18 generated families, "
     u"more than asked for**, plus the guarded-lease family; the odd-goods consignment mission "
     u"closed the last gap at 0.12.41-dev."),

    (u"Generate bounded story variations from client/faction, coordinate, staffing",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Generated families are offered least-asked first, "
     u"deterministically from the branch seed, and gated on routes the branch can actually take."),

    (u"Add space leasing/claiming with cost, boundaries, term, access/security requirements",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Remote sites go on the books, are billed daily, stop "
     u"being billed while out of reach, and come off the books on release; the guarded-lease "
     u"request family covers the contracted form."),

    (u"Implement evidence provenance/custody/type/value/risk/confidence",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Custody is a shelf linked to a gate as a records "
     u"archive (0.10.9-dev), and the three-observation checklist is the confidence model."),

    (u"Add analyze/interview/compare/review workflows for equipment, furniture, people",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Analysis, interviews, the contradictory-accounts "
     u"fold (row 308) and the recorder fold (row 493) all ship."),

    (u"Add repeated missing-person mysteries with radio fragments, missing crews",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** `LostPawnRegister`, delayed return, witness "
     u"conflict, reappearance, rescue and case closure all ship."),

    (u"Make sale/study/use/contain/release/recruit/detain/transfer choices visible",
     u"**RECONCILED 0.12.42-dev: SHIPPED.** Sale confirmation (0.12.33-dev), settlement records "
     u"and the consequences readout all ship."),

    (u"Define research IDs, tier gates, evidence prerequisites, benches, labor/cost",
     u"**RECONCILED 0.12.42-dev: SHIPPED 0.11.3-dev to 0.12.5-dev.** Tiers 0 to 3 across seven "
     u"branches, each unlock granting a capability real code honours. **Unlocks that changed "
     u"nothing observable were deleted rather than shipped** -- four of them at 0.12.5-dev."),

    (u"Implement containment rooms, security procedures, prisoner/witness interviews",
     u"**RECONCILED 0.12.42-dev: COMPLETE 0.12.36-dev.** Containment rooms, the security "
     u"procedure and the alarm shipped first; the staff debrief closed it, and **quarantine "
     u"turned out to be the same mechanism** because this package has no `HediffDefs` folder at "
     u"all."),

    (u"Add vehicles and space travel as logistics branches",
     u"**RECONCILED 0.12.42-dev: CLOSED 0.12.39-dev as a read-only readout**, because the "
     u"register forbids the obvious build in its own words: *\"do not add vehicles solely because "
     u"the framework is installed\"*."),

    (u"Add VGE Chapter 1 logistics summary/operations links",
     u"**RECONCILED 0.12.42-dev: CLOSED 0.12.39-dev.** *\"No patch or code/assets copied\"* is "
     u"the register's own instruction for this chapter, so the hook is a statement of what is "
     u"installed and what this package does about it."),

    (u"Add VGE Chapter 2 orbital security/contracts/wreck salvage hooks",
     u"**RECONCILED 0.12.42-dev: CLOSED 0.12.39-dev, and this row's absolute is asserted by "
     u"proof** -- `InhabitantService` draws only from `DefDatabase<RimroomsInhabitantDef>`, with "
     u"no `PawnGroupMaker`, `FactionDef` or `AllDefs` pawn-kind source anywhere, so no installed "
     u"content can mix into Backrooms generation."),

    (u"Implement feature detection and setup diagnostics for the pinned RWT release",
     u"**RECONCILED 0.12.42-dev: BUILT 0.12.39-dev.** `ModsConfig.IsActive` against the package "
     u"id read from the register, re-read when `ModLister.InstalledModsListHash` changes. The "
     u"readout states *not loaded*, *loaded*, and -- for both -- **unverified in play**."),

    (u"Document exact server setup and player experience.",
     u"**RECONCILED 0.12.42-dev: WRITTEN 0.12.39-dev as `docs/MULTIPLAYER.md`, and this row's "
     u"absolute now has a checker.** `check-doc-conformance.py` refuses an un-negated claim of "
     u"live shared-colony control or synchronised research in any reader-facing document, and it "
     u"found a real denial in `SCENARIOS.md` on its first run."),
]

text = original
problems = []
anchors = []
for opening, _note in RECONCILED:
    anchor = u"- [ ] " + opening
    count = text.count(anchor)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, opening[:70]))
    anchors.append(anchor)

if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for (opening, note), anchor in zip(RECONCILED, anchors):
    # The row's own words are kept in full; the note goes at the END of the line, after them.
    start = text.index(anchor)
    end = text.index(u"\n", start)
    line = text[start:end]
    rebuilt = u"- [x] " + line[len(u"- [ ] "):].rstrip() + u" — " + note
    text = text[:start] + rebuilt + text[end:]

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("master backlog reconciled: %d rows flipped, every original word kept" % len(RECONCILED))
