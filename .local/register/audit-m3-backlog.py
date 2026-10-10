# -*- coding: utf-8 -*-
"""Re-measure M3's 56 open backlog rows against the shipped code, 0.12.14-dev.

Why
---
The owner asked whether the queue was getting close to complete. It could not answer, because
`docs/TODO.md` carried **178 open rows** in the historical master-backlog section whose status had
never been re-measured against the code. A large fraction of them shipped between 0.7.2 and
0.12.13 and nobody flipped a checkbox. Same defect as the stale assembly hash and the C# file
count: a plausible number that nobody checks.

LAW: never delete TODO info. **Status changes only**, and every original word is kept. Evidence is
APPENDED so a future reader can re-check the flip rather than trust it.

Verdicts used
-------------
  [x]  built, with a named read site, version, or def
  [x]  SUPERSEDED, with the decision that superseded it
  [~]  partly built: what exists and what does not, both named
  [ ]  genuinely open, left alone (a note added only where the row is misleading)
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'TODO.md')

# (unique anchor from the row, new status char, appended evidence)
VERDICTS = [
    # ---------------------------------------------------------------- starts
    (u'Preserve native/Prepare Carefully edited pawn instances',
     u'x', u'**DONE.** All three starts build native pawns through `BranchStartRequest` '
           u'(`Scenario/ScenPart_RimroomsStart.cs`), and the five historical `RR_*Staff` PawnKinds '
           u'were found read by nothing and repurposed as the clean-up crew in 0.11.7-dev. EdB '
           u'Prepare Carefully is register row 85 and is not patched.'),
    (u'Honor the company-selected surface world tile through native setup',
     u'x', u'**DONE, 0.11.9-dev.** The Furniture & Knickknack Store start ships with its own '
           u'setup, grants and objective flow.'),
    (u'Implement the inside-start setup using the recorded provisional defaults',
     u'x', u'**DONE, and both pending answers are now closed.** Party size is player-settable '
           u'(0.12.0-dev) and the first exit is a guaranteed registered way out on a real '
           u'coordinate (0.12.2-dev). No provisional default remains.'),
    (u'Keep the first acceptance target on Async Industries while making its scenario setup',
     u'x', u'**DONE.** `BranchStartRequest` **is** the versioned start contract and all three '
           u'starts consume it; `scenarioVersion` is saved per branch.'),
    (u'Implement Furniture & Knickknack Store after Gate 2',
     u'x', u'**DONE, 0.11.9-dev.** `proof-starts.py` caught three new-game crashes in its layout '
           u'before it shipped.'),
    (u'Implement Lone Survivor after Gate 2',
     u'x', u'**DONE, 0.12.0-dev and 0.12.2-dev.** The map itself is a real Backrooms coordinate '
           u'with a guaranteed registered way out, and the natural chain stops at depth 3.'),
    (u'Add outpost, town-distortion, or company-in-crisis starts only after a design brief',
     u' ', u'**Still open, and correctly gated on its own condition:** no design brief exists. '
           u'Three starts ship. **This needs an owner decision before it is work at all.**'),

    # ---------------------------------------------------------------- rooms, people
    (u'Implement physical room functions: gate, control, labs, evidence archive',
     u'~', u'**Partly built.** The gate, control, analysis and archive functions exist as gate '
           u'equipment link roles (`RR_Link_Archive`, `RR_Link_Analysis`, `RR_Link_Tooling`, '
           u'0.10.8-dev). **Not built as room functions:** quarantine/decontamination, armory, '
           u'radio, receiving, cafeteria. RimWorld already builds rooms; what this mod adds is '
           u'what a gate is *linked to*.'),
    (u'Connect each room to concrete capabilities, stock needs, staff jobs, risks, and UI alerts',
     u'~', u'**Partly built.** A gate reports why it is not functional in its inspect string and '
           u'through the alerts readout (0.10.5-dev). **Not built:** per-room stock needs and '
           u'risk surfacing.'),
    (u'Add applicant/talent pools for candidates, specialists, contractors, survivors',
     u'x', u'**DONE.** `Personnel/ApplicantRecord.cs` and `Personnel/HiringServices.cs`, with '
           u'`RegisterHiredStaff` in `PersonnelServices.cs`.'),
    (u'Add configurable company roles, staff schedules, certifications, training jobs',
     u'~', u'**Partly built.** Configurable roles ship (`AssignCompanyRole`) and equipment '
           u'familiarity drives gate spin-up (0.8.9-dev). **Not built:** certifications, training '
           u'jobs, and **staff prior exposure**, which is still a named open prep item.'),
    (u'Add cafeteria, sleep, recreation, injury recovery, shift rotation, staff needs',
     u'x', u'**SUPERSEDED by the existing-content-only rule.** RimWorld already ships every one '
           u'of these natively and does them better than a mod should. Building parallel versions '
           u'would fight Core for no gain. Invariant 10.'),
    (u'Integrate existing hospitality, guest, prisoner, medical, and QoL systems only through',
     u'x', u'**DONE as a compliance rule, and it is held.** The register sweep covered '
           u'hospitality, medical and QoL; no file belonging to another mod is modified, and every '
           u'native interaction stays available. Owner direction: *"WE ARE NOT EDITING OTHER '
           u'PEOPLES MODS!"*'),

    # ---------------------------------------------------------------- the gate
    (u'Implement native door/endpoint bindings for controlled and mysterious portals',
     u'x', u'**DONE, 0.9.0-dev through 0.9.4-dev.** A gate is an ordinary door you designate; '
           u'Core’s `OrnateDoor` supplies 1×2 with no mods; gates are tinted blue; crossing '
           u'runs through `PortalTraversalPolicy`, the single chokepoint.'),
    (u'Bind actual control/laboratory equipment and native power grids/batteries',
     u'x', u'**DONE.** Equipment links 0.10.8-dev, real power draw 0.11.5-dev, and the reserve '
           u'requirement before opening 0.12.4-dev, which also revived a tier-0 card that had '
           u'promised an unlock and moved nothing.'),
    (u'Migrate the older custom gate/console state or document a preserved development-save',
     u'x', u'**DONE.** Eight legacy defs retired in 0.9.0-dev and 68 dead branches collapsed in '
           u'0.9.1-dev, all archived under `implementation/historical-content/`, with the save '
           u'boundary carried by `schemaVersion` 2.'),
    (u'Add machine subsystems/upgrades: power reserves, calibration, stabilizers',
     u'~', u'**Partly built.** Power reserves, calibration work, the emergency cutoff/kill switch '
           u'and monitoring all ship. **Not built, and confirmed absent by grep:** stabilizers, '
           u'modules, repair and a reliability model. Each would need a real read site before it '
           u'is written — invariant 136.'),
    (u'Add field equipment: protective gear, weapons, restraints, med kits, recorder/camera',
     u'x', u'**SUPERSEDED, deliberately and repeatedly.** Every custom field item was retired: '
           u'the return beacon (0.9.9-dev), the survey tag and evidence case (0.10.7-dev), the '
           u'route recording. **No new gameplay ThingDef may be authored** — invariant 10 — and '
           u'this row predates that rule.'),
    (u'Give every piece of gear a visible effect on detection, safety, information',
     u'x', u'**SUPERSEDED with the row above.** There is no custom field gear to give an effect '
           u'to. The principle survives and is enforced more strictly as invariant 136: an unlock '
           u'that changes nothing observable is deleted rather than shipped.'),
    (u'Add crew composition and cargo planner with skill/health/weight/gate-window checks',
     u' ', u'**Still open, and the row already marks it optional.** Expeditions carry crew and '
           u'cargo; the planner UI does not exist.'),
    (u'Add gate-window progression minutes → hours → days → weeks/months',
     u'x', u'**DONE, 0.5.4-dev.** The tier ladder: 108,000 ticks base, ×3 per earned tier, and '
           u'**no countdown at all** at the indefinite tier. Owner-directed.'),
    (u'Add schedule, warning, recall, evacuation, emergency close, lost-connection',
     u'~', u'**Mostly built.** Recall, emergency close, the kill switch, lost-connection and the '
           u'stranded-crew guarantee all ship, and 0.12.13-dev added the evacuation request '
           u'family. **Not built:** a scheduling surface.'),
    (u'Add fog-of-war atlas, route notes, last-known position, evidence chain',
     u'x', u'**DONE.** Fog of war holds undiscovered inhabitants (0.8.5-dev), the room graph is '
           u'saved, revisit displacement ships (0.10.3-dev), and the evidence chain runs through '
           u'a linked archive shelf (0.10.8-dev). The return beacon is deliberately retired.'),

    # ---------------------------------------------------------------- generation
    (u'Implement a tagged room/corridor library and deterministic topology generation',
     u'x', u'**DONE.** Room archetypes with declared family constraints, deterministic derivation '
           u'from the branch seed, and a saved `generatorVersion` and `roomLibraryVersion`.'),
    (u'Validate map size, accessible entrances/exits, walkable paths, mission objects',
     u'x', u'**DONE.** Generation validates before returning, and `proof-starts.py` reads building '
           u'sizes from Core’s own ThingDefs — which is how three new-game crashes were caught.'),
    (u'Add room families, furnishing rules, lighting/material palettes, loot, salvage',
     u'x', u'**DONE, 0.7.8-dev through 0.8.1-dev**, plus 0.8.7-dev, where the owner’s direction '
           u'that a bench in a corridor **is** the content made an archetype’s family constraint '
           u'lapse in a deranged space instead of being enforced.'),
    (u'Implement bounded non-Euclidean effects: repeats, moved door/exit',
     u'x', u'**DONE, 0.8.6-dev through 0.8.8-dev**, with revisit displacement in 0.10.3-dev — '
           u'weakened from firing 100% of the time to 66.7% **because a proof disagreed**, per '
           u'invariant 74: a horror mechanic that fires every time is a mechanic, not horror.'),
    (u'Add saved, rule-based anomaly propagation across room graphs with observable clues',
     u'x', u'**DONE.** `AnomalyEventService` with four effects, coherence decay, and every threat '
           u'honouring invariant 28: readable warning, learnable rule, a countermeasure, and no '
           u'unavoidable instant failure.'),
    (u'Make equipment meaningfully change what is detected or generated without breaking seed',
     u'~', u'**Half superseded, half held.** Seed reproducibility is held absolutely and anything '
           u'feeding the layout fingerprint is snapshotted rather than read live (invariant 27). '
           u'The **equipment** half died with the field gear — see the field-equipment row above.'),
    (u'Add map state versioning, archival, generator upgrades, explicit migration tests',
     u'x', u'**DONE.** `generatorVersion`, `roomLibraryVersion`, `schemaVersion`, and '
           u'`Generation/FailedSiteRecovery.cs` for a coordinate that cannot load.'),
    (u'Bound active map count, pawn/thing count, graph search, event evaluation',
     u'~', u'**Bounding is done; profiling is not and cannot be.** Every scan in `ConnectedWork/` '
           u'is a bounded rotating window, never a prefix (invariant 5), with roughly thirty '
           u'`Maximum*` scan budgets. **Profiling a long-running save requires launching the game, '
           u'which only the owner does.**'),

    # ---------------------------------------------------------------- economy, missions
    (u'Implement branch-local USD financial ledger with auditable entries, payroll',
     u'x', u'**DONE.** An append-only ledger with a running balance validated on load, '
           u'`PostTransaction` with idempotent operation ids, obligations, payroll, overhead, '
           u'bonds, salvage and the corporate trader.'),
    (u'Implement equipment/material procurement, source/price/**expected arrival**',
     u'x', u'**DONE.** The procurement catalogue with price and lead time, shipments, a receiving '
           u'zone, and delivery to any registered site (0.12.7-dev) — which is where a latent '
           u'cross-map reroute bug was found and fixed before it could swallow a paid shipment.'),
    (u'Implement contract/quest templates for surveys, retrieval, furniture/salvage, samples',
     u'x', u'**DONE, 0.12.12-dev and 0.12.13-dev.** **18 generated request families across arcs '
           u'4–8**, one per item the chart names, covering surveys, samples, instruments, rescue, '
           u'secure access, relay stations, caches, shelters, leases, resupply, evacuation, '
           u'witnesses, missing residents, public danger, heavy cargo, staff, and deeper systems.'),
    (u'Generate bounded story variations from client/faction, coordinate, staffing',
     u'~', u'**Partly built, 0.12.12-dev.** Generation reads branch capability, coordinates '
           u'visited, living witnesses, project qualification and how often a family has been '
           u'asked. **Not read yet:** client/faction identity, company tier, previous outcome, '
           u'opening duration.'),
    (u'Add space leasing/claiming with cost, boundaries, term, access/security requirements',
     u'~', u'**Partly built.** A registered remote site costs a share of base overhead every day '
           u'and can be released with no penalty (0.12.6-dev), and 0.12.13-dev added the guarded-'
           u'lease request family against `RR_Commerce_Leases`. **Not built:** term, renewal, '
           u'eviction. **A release fee must never be added** — it is a deadline wearing a coat.'),
    (u'Implement evidence provenance/custody/type/value/risk/confidence, sample storage',
     u'~', u'**Mostly built.** Provenance by source expedition, custody as *a place the book is* '
           u'(a shelf linked as a records archive, 0.10.8-dev), observations, analysis, research '
           u'value as insight, and a chain of custody. **Not built:** confidence scoring and a '
           u'destruction workflow.'),
    (u'Add analyze/interview/compare/review workflows for equipment, furniture, people',
     u' ', u'**Analysis ships; interview does not, confirmed by grep.** This is the same gap as '
           u'the *"contradictory accounts"* prep item, and the two should be built together.'),
    (u'Add repeated missing-person mysteries with radio fragments, missing crews',
     u'~', u'**Partly built.** Case records, missing status, the lost-pawn register, and the '
           u'missing-residents request family (0.12.13-dev). **Not built:** radio fragments and '
           u'**witness conflict**, which is the *"contradictory accounts"* prep item.'),
    (u'Make sale/study/use/contain/release/recruit/detain/transfer choices visible',
     u'~', u'**Partly built.** Sale through the valuables exchange, study through analysis, '
           u'recruit through hiring, and faction standing exists. **Not built:** contain, release, '
           u'detain and transfer as distinct choices with their own consequences.'),

    # ---------------------------------------------------------------- research, entities
    (u'Define research IDs, tier gates, evidence prerequisites, benches, labor/cost',
     u'x', u'**DONE, 0.9.8-dev through 0.11.6-dev.** The tree is **derived, not declared**; '
           u'projects require completed logs of named kinds; every granted capability is asserted '
           u'to be read by real source by `proof-research-branches.py`.'),
    (u'Complete research branches for facility/power, engineering, field safety, equipment',
     u'~', u'**Seven branches at tiers 0–2, complete. Tiers 3–4 are the next checkpoint**, and '
           u'the knob survey now finds **five of seven branches with real, observable knobs** — up '
           u'from three at 0.12.5-dev, because arc 5 wrote the remote-operations systems a tier-3 '
           u'unlock needs. Fieldcraft and Entities still have none and **will not be invented**.'),
    (u'Author entity/anomaly design sheets first: appearance/readability, AI rules',
     u'~', u'**Partly built.** Inhabitant defs carry AI rules, bands, tells and counters, and the '
           u'escalation ladder is bounded. **Not built as authored design documents**, and the '
           u'`RR_QuietPursuer` presentation is still the last open existing-content replacement.'),
    (u'Implement containment rooms, security procedures, prisoner/witness interviews',
     u' ', u'**Still open, confirmed by grep.** `Generation/BackroomsContainment.cs` is **map** '
           u'containment — a coordinate having no outside — and is unrelated to entity '
           u'containment. Evidence custody and case records do ship.'),
    (u'Implement anomaly openings at ordinary RimWorld settlements as timed quests',
     u'x', u'**SUPERSEDED by chart §1.1, and the untimed version is BUILT.** *"timed quests"* '
           u'breaks the owner absolute that nothing but the gate has a clock; '
           u'`CAMPAIGN_CHART.md` §5 records arc 6’s prep description as **the worst offender '
           u'against it**. 0.12.13-dev shipped the untimed form: witnesses, missing residents and '
           u'public danger, with consequences for **abandonment, never for delay**.'),
    (u'Add outside-gate and inside-site radio stations, supply points, relief teams',
     u'x', u'**DONE, 0.12.13-dev**, plus the clean-up team in 0.11.7-dev. Relay stations, caches, '
           u'field shelters, guarded leases, resupply and evacuation all ship as request families, '
           u'and every one of them turned out to have had a research project since 0.11.6-dev.'),
    (u'Add vehicles and space travel as logistics branches',
     u' ', u'**Still open.** Arc 7’s heavy-cargo and staff-transfer request families ship '
           u'(0.12.13-dev), but no vehicle or space system is written. **DLC- and mod-optional '
           u'throughout**, so this can never become a requirement.'),
    (u'Add VGE Chapter 1 logistics summary/operations links',
     u' ', u'**Still open, and optional by construction.** Any hook lives inside a '
           u'`PatchOperationFindMod`, which applies nothing when the mod is absent — invariant 42.'),
    (u'Add VGE Chapter 2 orbital security/contracts/wreck salvage hooks',
     u' ', u'**Still open, and optional by construction**, with the same `PatchOperationFindMod` '
           u'rule. Orbital enemies must never mix into Backrooms entity generation.'),

    # ---------------------------------------------------------------- M3 tail
    (u'**The remaining rungs of the laboratory duration ladder.**',
     u'x', u'**DONE, and this row’s own complaint is stale.** '
           u'`CompRimroomsGate.portalWindowTierProjects` is a list that now names **three** gate '
           u'projects — `RR_GateFieldStability`, `RR_GateTelemetry`, `RR_GateSustainedAperture` — '
           u'and 0.10.9-dev shipped the log-gated ladder with four rungs.'),
    (u'**Inside-start scenario implementation now that both its questions are decided:**',
     u'x', u'**DONE, 0.12.0-dev and 0.12.2-dev.** Configurable party, and a guaranteed way out on '
           u'a real coordinate rather than a revealed fixed destination.'),
    (u'Room functions, applicant pools, training/certification, wellbeing',
     u'~', u'**Split verdict, see the individual rows above.** Applicant pools **done**; room '
           u'functions and roles **partly**; wellbeing **superseded** because RimWorld ships it.'),
    (u'Contract/quest templates for the 13 mission families, leases, shipment incidents',
     u'x', u'**DONE, 0.12.12-dev and 0.12.13-dev: 18 generated families, more than the 13 '
           u'asked for**, plus the guarded-lease family. Shipment incidents ride the existing '
           u'procurement delay and loss paths.'),
    (u'Research IDs across tiers T0–T6 and the nine branches; entity family sheets',
     u'~', u'**Tiers 0–2 complete across seven branches; T3 is the next checkpoint.** The eighth '
           u'branch (transport and orbital) has **no tier 0 at all, deliberately**, and the tree '
           u'is derived rather than declared, so a tier number is not a promise of a linear chain.'),
    (u'Containment, interviews, settlement openings, outposts, vehicles, VGE hooks',
     u'~', u'**Settlement openings and outposts are DONE (0.12.13-dev).** Containment, '
           u'interviews, vehicles and the VGE hooks remain open and are listed individually above.'),
    (u'Store start; Lone Survivor start. Both starts are fully specified',
     u'x', u'**DONE. All three starts ship** — Async Industries, the Furniture & Knickknack '
           u'Store (0.11.9-dev) and solo/group (0.12.0-dev, 0.12.2-dev).'),
]

s = io.open(PATH, encoding='utf-8').read()
flipped = {'x': 0, '~': 0, ' ': 0}
for anchor, status, note in VERDICTS:
    old = u'- [ ] ' + anchor
    # Some rows are indented sub-bullets.
    indented = u'  - [ ] ' + anchor
    if old in s:
        target, prefix = old, u'- [%s] ' % status
    elif indented in s:
        target, prefix = indented, u'  - [%s] ' % status
    else:
        raise AssertionError('anchor not found: %r' % anchor[:70])
    assert s.count(target) == 1, 'anchor not unique: %r' % anchor[:70]
    # The row keeps every original word; the status changes and evidence is appended at the end
    # of that line only.
    start = s.index(target)
    end = s.index(u'\n', start)
    row = s[start:end]
    body = row.split(u'] ', 1)[1]
    s = s[:start] + prefix + body + u' — ' + note + s[end:]
    flipped[status] += 1

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('M3 backlog re-measured: %d built or superseded, %d partial, %d confirmed open'
      % (flipped['x'], flipped['~'], flipped[' ']))
