# -*- coding: utf-8 -*-
"""Re-measure M1, M2, the standing-constraints block and the in-progress block, 0.12.14-dev.

Third and final pass of the backlog audit. Same rules: STATUS ONLY, every original word kept,
evidence appended.

Much of the standing-constraints block went stale **during this session** -- arc 5's "still owed"
rows, the "thirteen remaining families", "generation after the hinge", and two owner questions that
were answered and wired in 0.12.4-dev. Those are closed here with the version that closed them.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'TODO.md')

BUILT = u'**BUILT.** '
PART = u'**PARTLY BUILT.** '
OPEN = u'**STILL OPEN.** '
HELD = u'**HELD as a standing absolute.** '

VERDICTS = [
    # ------------------------------------------------------------------ M2
    (u'Map every custom gameplay Def/asset and code consumer to existing Core/profile content', u'x',
     BUILT + u'0.9.0-dev retired eight legacy defs and took the package from 92 files to 79; '
     u'0.9.1-dev collapsed 68 dead branches. Everything removed is archived under '
     u'`implementation/historical-content/<version>/` — invariant 37, retired content is archived, '
     u'never deleted.'),
    (u'Replace custom gate/console/cutoff/generator objects with designated existing', u'x',
     BUILT + u'**A gate is an ordinary door you designate and nothing else** (invariant 12 and '
     u'0.9.0-dev). Console, battery and assembly bench are existing installed buildings linked in.'),
    (u'Replace custom field gear, route aids and evidence items with existing objects', u'x',
     BUILT + u'The return beacon (0.9.9-dev), the survey tag and sealed evidence case (0.10.7-dev) '
     u'and the route recording are all retired; custody became **a place the book is** — a shelf '
     u'linked as a records archive (0.10.8-dev) — rather than a custom item existing somewhere.'),
    (u'Replace custom creature presentation, room fixtures and terrain with existing native', u'~',
     PART + u'Room fixtures and terrain use existing content throughout (`BackroomsPalette` names '
     u'Core `TerrainDef`s). **`RR_QuietPursuer` presentation is the last one open** and is queue '
     u'item 6.'),
    (u'Define supported migration or explicit preserved development-save break', u'x',
     BUILT + u'`schemaVersion` 2 with migration at `PostLoadInit`, and the development-save '
     u'boundary documented in the retirement records.'),
    (u'Reconcile all scenario grants, recipes, equipment readiness, content bindings', u'x',
     BUILT + u'All three starts run through `BranchStartRequest`, and `check-package-integrity.py` '
     u'verifies every def reference resolves against installed game data or this package.'),
    (u'Replace the historical custom gameplay items, benches, terrain, sprites and audio', u'~',
     PART + u'Items, benches and terrain: **done**. **Fourteen historical gameplay PNGs remain in '
     u'the package allowlist** and come out once the last references go, which is gated on the '
     u'`RR_QuietPursuer` decision.'),

    # ------------------------------------------------------------------ M1
    (u'Implement every open item in [connected colony portals]', u'~',
     PART + u'The foundation ships: **seven adapters** in `ConnectedWork/Adapters/` — bill, '
     u'casualty, construction, food, fuel, hauling, medicine — plus the tending provider, two work '
     u'givers per family, and every scan a bounded rotating window rather than a prefix '
     u'(invariant 5). Individual open routes are listed below.'),
    (u'Finish resumable route scheduling, same-pawn/cargo crossing recovery and player-facing', u'x',
     BUILT + u'A crossing preflights fully, then moves, and restores on failure — invariant 55: a '
     u'transfer that can lose a pawn is a corruption, not a threat. A bounded scan that ran out of '
     u'budget is **pending**, never "no route" (invariant 4).'),
    (u'Implement and integrate native work/needs adapters, physical ingredient logistics', u'x',
     BUILT + u'Seven adapter families, with physical ingredient logistics through '
     u'`ConnectedBillAdapter` and real cargo movement rather than teleported quantities.'),
    (u'**Resume step 5:** "Integrate exact optional work/storage providers and scenario openings', u'~',
     PART + u'Scenario openings: **done**, all three starts. Optional provider adapters remain — '
     u'see their own row below.'),
    (u'**Resume step 6:** "Continue source/build milestones. Runtime acceptance remains deferred', u'~',
     PART + u'Source and build milestones have continued without a break through 0.12.13-dev. '
     u'**Runtime acceptance is still deferred and structurally must be: only the owner launches.**'),
    (u'Implement actual cross-portal hauling, construction ingredients, bills/production', u'x',
     BUILT + u'All of these route through the adapter families, with real items carried by real '
     u'pawns across a real threshold.'),
    (u'Reconcile jobs and original cargo on closure/reopen, blocked endpoints, death', u'x',
     BUILT + u'And the hardest case is guaranteed rather than best-effort: **a gate closing on a '
     u'crew strands them and never takes them.** `ShouldRemoveMapNow` returns false '
     u'unconditionally and no gate source may call `PassToWorld`, proved by '
     u'`proof-stranded-crew.py`.'),
    (u'Integrate relevant profile work/storage/hauling providers; account for all 294 rows', u'~',
     PART + u'14 of 21 system families swept. **7 remain:** medical, world operations, cargo, '
     u'hospitality, materials, visitor economy, staff psychology. The row is right to forbid '
     u'asserting coverage without evidence — invariant 23.'),
    (u'Replace dispatch-only ordinary travel controls and scenario prerequisites', u'x',
     BUILT + u'Crossing is a real ordered job (`RR_CrossPortal`) rather than a dispatch abstraction, '
     u'and optional missions stay optional.'),
    (u'Persist coordinate/seed/version/site/complexity and generated inhabitants/events', u'x',
     BUILT + u'And anything feeding the layout fingerprint is **snapshotted rather than read live** '
     u'— invariant 27, which was a live trap before it was a rule.'),
    (u'Implement bounded procedural inhabitants/state combinations, rare monstrosities', u'x',
     BUILT + u'0.8.2-dev through 0.8.5-dev: wanderers, survivors, anomalies and colonist echoes, '
     u'with undiscovered inhabitants **held** until fog of war reveals them — because a cautious '
     u'player would otherwise arrive to find everyone already starved.'),
    (u'Author and implement the saved, bounded escalation ladder: a new coordinate starts quiet', u'x',
     BUILT + u'The pressure ladder with depth bands, `Band.Hostile` as the single *"deeper levels"* '
     u'threshold (invariant 50), and coherence decay. Below the band a hostile holds ground; at it, '
     u'it hunts.'),
    (u'Implement connected-site scheduling/streaming and measure performance after an', u' ',
     OPEN + u'Scheduling and streaming ship. **Measuring performance requires an owner-launched '
     u'build, which is the one thing this project cannot do for itself.**'),
    (u'Saved work intents, quantity leases and native destination job revalidation.', u'x',
     BUILT + u'One commitment per worker across every record kind (invariant 8), and destinations '
     u'revalidated rather than trusted from the record.'),
    (u'Work-specific hauling, construction, bill, research, medical and needs adapters.', u'x',
     BUILT + u'All present in `ConnectedWork/Adapters/`.'),
    (u'Optional profile interfaces and native priority/schedule/restriction coverage.', u'~',
     PART + u'Native priority, schedule and restriction handling is respected — nothing is ever '
     u'`playerForced` and no quantity is hardcoded (invariant 9). **Optional provider interfaces '
     u'remain**, on their own row below.'),
    (u'**Adapter families, one at a time with source evidence per route:**', u'~',
     PART + u'Seven families built with source evidence each. **Surgery across a gate is the named '
     u'remainder** and has its own row.'),
    (u'**The remaining medical routes, each needing its own source review.**', u' ',
     OPEN + u'Tending and medicine delivery ship (`ConnectedMedicineAdapter`, `TendingProvider`). '
     u'**Surgery across a gate does not**, and it deliberately waits for its own source review '
     u'rather than being assumed to work like tending.'),
    (u'**Procedural inhabitants, rare monstrosities, evolving saved events, technology-driven', u'x',
     BUILT + u'0.8.2-dev through 0.8.8-dev, and 0.8.7-dev corrected a wrong finding of mine: a '
     u'bench standing in a corridor **is** the content, so an archetype’s family constraint now '
     u'lapses in a deranged space instead of being enforced.'),
    (u'**The saved, bounded escalation ladder** required by the', u'x',
     BUILT + u'See the escalation-ladder row above. Every threat honours invariant 28: readable '
     u'warning, learnable rule, a countermeasure, and no unavoidable instant failure.'),
    (u'**Optional work/storage provider adapters** (Pick Up And Haul 164', u' ',
     OPEN + u'Each needs its own source review and a `PatchOperationFindMod` so it applies nothing '
     u'when the mod is absent (invariant 42). **None is a requirement** — the package must load and '
     u'run against Core alone.'),

    # ------------------------------------------------------------------ standing constraints
    (u'**Continue the retroactive pass** across the remaining system families.', u'~',
     PART + u'14 families swept, 7 to go: medical, world operations, cargo, hospitality, materials, '
     u'visitor economy, staff psychology.'),
    (u'**Still unbuilt from the same prep document:** *"contradictory accounts"*', u' ',
     OPEN + u'And it now has a natural home: `Testify` routes already count **distinct living '
     u'witnesses**, so two crew who disagree is a short step from a mechanism that exists. Pairs '
     u'with the missing interview workflow.'),
    (u'**Still unbuilt from the progression ladder:** step 5\'s *"respond to openings in settlements"*', u'x',
     BUILT + u'**0.12.13-dev**: the witnesses, missing-residents and public-danger request families, '
     u'untimed — because the prep material’s *"timed"* framing was the worst offender against the '
     u'owner absolute that nothing but the gate has a clock.'),
    (u'**Keep doing this.** Each checkpoint should check one prep document', u'x',
     HELD + u'And it keeps paying: this session found the whole request surface read by nothing, '
     u'and that arc 5’s *"still unwritten"* list had had research projects since 0.11.6-dev.'),
    (u'**"all story line in quests layed out and coporation requasts and missions"**', u'x',
     BUILT + u'`CAMPAIGN_CHART.md` lays out the line, and **25 request defs** now implement it: 7 '
     u'fixed tutorial requests including the hinge, and 18 generated families across arcs 4–8.'),
    (u'**"the mega mother corp is greedy and will basic do anything and put up with anything', u'x',
     HELD + u'Greed is the **mechanism** for the patience, not a contradiction of it, and it does '
     u'three things: it waits, it offers routes, and it will not let a facility die.'),
    (u'**"to the point of sending clean up teams to your base with all access passses', u'x',
     BUILT + u'0.11.7-dev, deterministic and uncapped. `AnyLivingStaff` deliberately does not check '
     u'`Spawned`, `Map` or `Downed`, and the party is moved **last** so a failure leaves everyone '
     u'safe.'),
    (u'**"this is liken the store and solo/group scenerios once they reach contact', u'x',
     BUILT + u'Contact is a **state, not a scenario**, and it is one-way: a corporation that has '
     u'seen a return does not forget about a branch.'),
    (u'**"make sure the whole mission line and tech linkange and research tree line chart', u'x',
     BUILT + u'0.11.0-dev. The chart came first, it retired two offer clocks, and it corrected '
     u'seven prep documents **before** any request content existed — which is exactly why no '
     u'deadline ever reached the game.'),
    (u'**"and any and all things i didnt mention that apply"**', u'x',
     HELD + u'The chart covers structure the owner did not enumerate, and it is the authority over '
     u'any prep document.'),
    (u'**"before you randomly and will nilly build out the scenerio quests"**', u'x',
     HELD + u'No ad-hoc content has been written. Every one of the 25 requests traces to a line in '
     u'the chart, and 0.12.5-dev **deleted four planned research projects** rather than invent '
     u'effects for them.'),
    (u'**"that all should play out like a tutoriasl of sorts that turn open ended to campaine"**', u'x',
     BUILT + u'Six fixed requests teaching one system each, then the hinge where the company stops '
     u'naming things, then generation. 0.12.11-dev through 0.12.13-dev.'),
    (u'**"nothing ever ever have time restripctions but the gate(ie power tech and maintanance', u'x',
     HELD + u'**AN ABSOLUTE.** The gate is the only clock. Enforced by `check-campaign-absolutes.py`, '
     u'by the request shape having **no field a deadline could be written into**, and by two proofs '
     u'that search for four clock words by name.'),
    (u'**"but missions and quests and offeres and trades are never time senstive', u'x',
     HELD + u'**AN ABSOLUTE**, enforced by absence: there is nowhere to put an expiry.'),
    (u'**"and never offer only one path but multiple success routes"**', u'x',
     HELD + u'**AN ABSOLUTE**, enforced three ways: `ConfigErrors` at def load, '
     u'`check-campaign-absolutes.py` before shipping, and the eligibility filter refusing to offer '
     u'a generated family the branch cannot answer two different ways.'),
    (u'**Async Industries starts in contact**, with basic gate tech already researched', u'x',
     BUILT + u'It opens with eight completed projects.'),
    (u'**The Store and Solo/Group starts need their own layout and treatment**', u'x',
     BUILT + u'0.11.9-dev and 0.12.0-dev through 0.12.2-dev, each a different point of view on the '
     u'same world.'),
    (u'**All three feed the same universal RimWorld tech tree**', u'x',
     BUILT + u'The tree is **derived, not declared** (0.9.8-dev), so a scenario declares what begins '
     u'finished and never the tree itself — invariant 60. No start can be dead-ended.'),
    (u'**`reserveChargePowerWatts` restored, NOT yet wired - an owner question.**', u'x',
     BUILT + u'**Owner-answered and wired, 0.12.4-dev:** a supply requirement before opening. '
     u'Wiring it also revived `RR_Cap_ReserveDiscipline`, a tier-0 card that had promised an unlock '
     u'and moved nothing.'),
    (u'**Open owner question, found while sweeping:** a designated gate drew **nothing**', u'x',
     BUILT + u'**Owner-answered: keep the 250 W idle draw.** Confirmed as intended; no change '
     u'needed.'),
    (u'**Still owed in arc 5, all three now reachable because of that predicate:**', u'x',
     BUILT + u'**All three shipped**: supplying 0.12.7-dev, staffing 0.12.8-dev, the exit plan '
     u'0.12.9-dev.'),
    (u'**Also named by the chart and unwritten:** relay stations, caches, field shelters', u'x',
     BUILT + u'**0.12.13-dev**, all six as generated request families — and every one turned out to '
     u'have had a research project since 0.11.6-dev.'),
    (u'**Still unwritten from the chart for arc 5:** relay stations, caches, field shelters', u'x',
     BUILT + u'**0.12.13-dev.** Duplicate of the row above; both are closed.'),
    (u'**Next: the thirteen remaining generated families for arcs 5-8**', u'x',
     BUILT + u'**0.12.13-dev**, with coverage asserted **per arc** because a total of eighteen would '
     u'be satisfied by eighteen copies of one arc.'),
    (u'**Next: generation after the hinge.** The arc 4-8 request families plus the eligibility', u'x',
     BUILT + u'**0.12.12-dev.** Every clause of the filter can refuse, asserted, and a finished '
     u'project is not reachable — otherwise the offer itself is a payout button.'),
    (u'**The route model was answered *"1 and 3"* on 2026-09-29**', u'x',
     BUILT + u'Closed by the owner’s conflict resolution: *"Both — filter picks the family, card '
     u'never shrinks."* Eligibility gates the offer; `RequestRoutes.Available` is untouched.'),
]

s = io.open(PATH, encoding='utf-8').read()
tally = {'x': 0, '~': 0, ' ': 0}
missing = []
for anchor, status, note in VERDICTS:
    found = None
    for prefix in (u'- [ ] ', u'  - [ ] ', u'    - [ ] ', u'      - [ ] '):
        target = prefix + anchor
        if target in s and s.count(target) == 1:
            found = (target, prefix)
            break
    if found is None:
        missing.append(anchor[:60])
        continue
    target, prefix = found
    start = s.index(target)
    end = s.index(u'\n', start)
    body = s[start:end].split(u'] ', 1)[1]
    s = s[:start] + prefix.replace(u'[ ]', u'[%s]' % status) + body + u' — ' + note + s[end:]
    tally[status] += 1

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('M1/M2/standing re-measured: %d built or held, %d partial, %d confirmed open'
      % (tally['x'], tally['~'], tally[' ']))
if missing:
    print('ANCHORS NOT MATCHED (%d), left untouched:' % len(missing))
    for anchor in missing:
        print('  %s' % anchor)
