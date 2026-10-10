import io

# --- TODO: owner direction verbatim
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = """### Owner direction — zones must work on both sides of any gate (2026-09-29)

**Verbatim owner requests (2026-09-29, two items):** *"we also need to make sure zones work properly when putting them on boith sides of any type of gate"* and *"and as a continueations through the gate"*

Full audit in [`research/ZONES_AND_AREAS_ACROSS_A_GATE.md`](research/ZONES_AND_AREAS_ACROSS_A_GATE.md), which covers every zone and area type in the game against what the work layer does with it.

**The constraint that shapes every answer:** a RimWorld `Zone` **cannot span two maps** — `Zone.Map` is single-valued and `ZoneManager` is per-map, and the same holds for every `Area`. So a zone that "continues through the gate" cannot be one object. What it has to mean instead is that two zones, one each side, **behave as one**: goods flow between them, work on either side attracts somebody, and the far one's own settings are what get respected. That is the standard the audit holds every case to.

- [x] **"we also need to make sure zones work properly when putting them on boith sides of any type of gate"** — audited every zone and area type. `Zone_Stockpile` works both directions (the far zone's own filter and priority decide, through `IsValidStorageFor(storeMap, thing)`); `Zone_Fishing` works; `Area_Home` works for cleaning, repair and firefighting; `Area_Allowed` works as a recorded observation plus the definitive check on arrival; `Area_NoRoof` is deliberately emptied inside the Backrooms by the containment rule. **`Zone_Growing` was broken and is fixed** — see below.
- [x] **"and as a continueations through the gate"** — continuation is satisfied functionally rather than by linking objects, and deliberately so. Nothing gives two zones a shared name or copies settings between them, and neither would be an improvement. Two stockpiles either side of a gate are already continuous in the sense that matters: put something in one and a hauler moves it to the other when the other is a better home for it. The failure mode to avoid was never "they are not linked" but **"a zone on the far side is invisible to the work layer, or visible but impossible"**.
- [x] **Zones persist across visits, which is the precondition for all of it** — `RimroomsDestinationMapParent.ShouldRemoveMapNow` returns `false` unconditionally, so a coordinate map is never removed and every zone painted there survives leaving and returning, with its settings.
- [x] **DEFECT FIXED: a growing zone inside the Backrooms could never be sown, and held the worker there anyway.** `ZoneHasWork` decided sowing was wanted from three facts about the *zone* and never asked whether the *cell* could be sown. Coordinate rooms are floored with `Concrete` and `PavedTile`, both of which inherit `FloorBase`, declare no `fertility` and so carry the field default of **0**, while every Core plant needs `fertilityMin` of at least **0.01**. So a grower was sent, Core refused on arrival — **and `HasWorkHere` asked the identical question and also said yes, so the deployment was never released** and the worker stood in the Backrooms indefinitely with a live commitment. Worse than a wasted trip: a wasted trip costs one walk, a deployment that will not release costs a colonist. Fixed by adding Core's own `CanEverPlantAt` and `PlantUtility.GrowthSeasonNow`, both of which read the cell and its own map and take no pawn.
- [x] **A wrong hypothesis corrected on the way** — the first theory was that a fully-roofed coordinate blocks sowing for lack of **sunlight**. It does not: `GrowthSeasonNow` reads room and temperature, not light, and Core sows indoors happily. The real gate is **fertility**, and building on the light theory would have produced a check that tested the wrong thing.
- [ ] **Three area types are not covered, and that is correct only until the far side of a gate can be an ordinary world map.** `Area_BuildRoof` (a coordinate is already all thick rock), `Area_NoRoof` (removal is forbidden there by the world rule), and `Area_SnowOrSandClear` / `Area_PollutionClear` (a coordinate has no outside, so no weather). **Revisit all of them when the ordinary-map endpoint lands** — a colony map does get snow, does want roofs built, and may be polluted.

"""
old = "### Owner direction — the 294-mod register must actually work and be human navigable (2026-09-29)"
assert old in s
s = s.replace(old, block + old, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- DEFERRED: hang the three area types off the ordinary-map endpoint item
p = 'docs/DEFERRED.md'
s = io.open(p, encoding='utf-8').read()
old = "## The 294-mod register, and the work types nobody had enumerated (2026-09-29)"
block = """## Zones and areas across a gate (2026-09-29)

Audit: [`research/ZONES_AND_AREAS_ACROSS_A_GATE.md`](research/ZONES_AND_AREAS_ACROSS_A_GATE.md).

- [x] **Stockpile, fishing, Home and allowed-area behaviour across a gate** — audited and working. The far zone's own settings decide, in every case.
- [x] **Zones persist across visits** — coordinate maps are never removed (`ShouldRemoveMapNow` returns false unconditionally), so painted zones and their settings survive.
- [x] **Growing zones inside the Backrooms** — **DEFECT FIXED 0.6.8-dev.** Concrete and paved floors have fertility 0 and no plant can be sown on them, but the provider reported work anyway and `HasWorkHere` held the deployment open. Core's `CanEverPlantAt` and `GrowthSeasonNow` now gate the per-cell test.
- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear` across a gate** — not covered, and **correctly not covered while the far side of a gate is always a Backrooms coordinate**: a coordinate is already all thick rock, roof removal there is forbidden by the world rule, and it has no outside and therefore no weather. **This row is a dependency of the ordinary-map portal endpoint, not an independent one** — build it in that checkpoint, because a colony map genuinely gets snow, genuinely wants roofs built, and may be polluted.

"""
assert old in s
s = s.replace(old, block + old, 1)
old2 = "- [ ] **The eleven DLC container hauling givers**"
assert old2 in s
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- REGRESSION_CONTAINMENT rot check
p = 'docs/REGRESSION_CONTAINMENT.md'
s = io.open(p, encoding='utf-8').read()
old = "| `is Bill_Production` used as a test that excludes autonomous or mech bills |"
new = ("| A candidate half that asks only whether a **zone** wants work, without asking whether the **cell** can take it | That exact shape was a defect: a growing zone on a coordinate's concrete floor (fertility 0) reported work forever, and because `HasWorkHere` asked the same question the deployment was **held open**. Ask Core's per-target gate too. `research/ZONES_AND_AREAS_ACROSS_A_GATE.md` |\n"
       "| Sowing described as blocked inside the Backrooms by lack of **sunlight** | It is not. `GrowthSeasonNow` reads room and temperature, not light; Core sows indoors. The real gate is **terrain fertility** |\n"
       "| `is Bill_Production` used as a test that excludes autonomous or mech bills |")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- NOW invariant + reading order
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
old = "25. **A def referencing DLC content carries `MayRequire`; the C# guard is not enough.**"
new = ("""25. **A candidate half must ask whether the *target* can take the work, not only whether its *zone or owner* wants it.** A growing zone on a coordinate's concrete floor (fertility 0) reported work forever, and because `HasWorkHere` asks the same question the deployment was **held open** with the worker idle — worse than a wasted trip. See `research/ZONES_AND_AREAS_ACROSS_A_GATE.md`.
26. **A def referencing DLC content carries `MayRequire`; the C# guard is not enough.**""")
assert old in s
s = s.replace(old, new, 1)
for a, b in (("26. **The register is generated output", "27. **The register is generated output"),
             ("27. **A prisoner can never cross a gate", "28. **A prisoner can never cross a gate"),
             ("28. **The portal topology is an unbounded alternation", "29. **The portal topology is an unbounded alternation"),
             ("29. **Never trust a remembered list of anything", "30. **Never trust a remembered list of anything")):
    assert a in s, a
    s = s.replace(a, b, 1)
old = "8. `docs/implementation/MOD_REGISTER_REBUILD.md`"
new = ("8. `docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md` — every zone and area type across a gate, what works, and the three that wait on the ordinary-map endpoint.\n"
       "9. `docs/implementation/MOD_REGISTER_REBUILD.md`")
assert old in s
s = s.replace(old, new, 1)
s = s.replace("9. `docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md`", "10. `docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md`", 1)
s = s.replace("10. `docs/PUBLISHING.md`", "11. `docs/PUBLISHING.md`", 1)
# the ordinary-map endpoint item gains the area dependency
old = "2. **A portal whose far side is an ordinary map**, then **a world tile the branch does not hold.**"
new = ("2. **A portal whose far side is an ordinary map**, then **a world tile the branch does not hold.** **When this lands, also cover `Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` across a gate** — they are uncovered today only because a coordinate has no outside and no removable roof, and a colony map has both.")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated for the zone audit")
