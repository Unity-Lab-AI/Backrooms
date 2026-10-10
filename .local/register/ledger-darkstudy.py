import io

FAM = "**28 families, 20 of them deployments**"

# --- CHANGELOG
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.6.6-dev - 2026-09-29 - study what you contain, through a gate

- **A researcher now crosses a gate to study a contained entity on the other side.** A containment facility reached through a portal is the whole idea of this mod, and until now nobody would walk to one.
- An empty holding platform attracts nobody. Neither does an entity still on its study cooldown, or one whose study you switched off.
- The game's own study work does the studying once your researcher is standing there, exactly as it does at home.
- This needs the Anomaly expansion. Without it the work simply does not exist, rather than misbehaving.

**A load error fixed, present since 0.6.4-dev.** The two cross-gate childcare work entries referred to a work type that only the Biotech expansion adds, with nothing marking them as needing it. On a copy of the game without Biotech that produced an error at startup — in a mod that is supposed to need nothing but the base game. Both are now marked correctly, and a new check reads the game's own data to make sure no future entry can slip through the same way.

Full record: [dark study](docs/implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- TODO
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = "- [ ] **DarkStudy deployment** — Anomaly's single giver `StudyInteract` / `WorkGiver_DarkStudyInteract`, priority 110."
new = ("- [x] **DarkStudy deployment** — **BUILT 0.6.6-dev.** " + FAM + ". Core's own scanner takes an explicit map "
       "(`GetStudiableThingsAndPlatforms(pawn.Map)`) and that method is a pure read of a per-map cache, so the candidate "
       "half is exact rather than reimplemented. Also **closed a second shipped defect**: the two childcare giver defs "
       "referenced the Biotech-only `Childcare` work type with **no `MayRequire`**, an unresolved cross-reference at load "
       "on a Core-only install since 0.6.4-dev — the same careful-C#-beside-a-contradicting-def shape as the "
       "`Bill_Production` defect. `tools/check-dlc-gating.py` now indexes the game's own data (6,063 DLC-only defs) so it "
       "cannot recur. Record `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`. Was: Anomaly's single giver "
       "`StudyInteract` / `WorkGiver_DarkStudyInteract`, priority 110.")
assert old in s
s = s.replace(old, new, 1)
s = s.replace("**FOURTH PASS BUILT 2026-09-29 in 0.6.5-dev:** bill work as **five** families, one per work type — **27 families, 19 of them deployments**. Record `implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md`.",
              "**FOURTH PASS BUILT 2026-09-29 in 0.6.5-dev:** bill work as **five** families, one per work type — 27 families. Record `implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md`. **FIFTH PASS BUILT 2026-09-29 in 0.6.6-dev:** dark study — " + FAM + ". Record `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`.", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- DEFERRED
p = 'docs/DEFERRED.md'
s = io.open(p, encoding='utf-8').read()
old = "- [ ] **DarkStudy deployment** — open. Anomaly, one giver, `[MayRequireAnomaly]`. The most thematically apt item in the audit."
new = ("- [x] **DarkStudy deployment** — **BUILT 0.6.6-dev**, " + FAM + ". Core's `GetStudiableThingsAndPlatforms(map)` is a "
       "pure read of a per-map cache, so the candidate half is exact. Anomaly-gated in both C# and XML. Superseded text, kept "
       "per the never-delete rule: *open. Anomaly, one giver, `[MayRequireAnomaly]`. The most thematically apt item in the audit.*\n"
       "- [x] **DLC-only defs must be gated in XML, not only handled in C#** — the two childcare giver defs had referenced the "
       "Biotech-only `Childcare` work type ungated since 0.6.4-dev. Fixed, and `tools/check-dlc-gating.py` now enforces it "
       "against the game's own shipped data rather than a maintained list of names.")
assert old in s
s = s.replace(old, new, 1)
s = s.replace("→ **the three remaining gaps**: DarkStudy, hauling upkeep, BasicWorker, with `Fishing` a generation question first.",
              "→ ~~DarkStudy~~ (BUILT 0.6.6-dev; " + FAM + ") → **the two remaining gaps**: hauling upkeep and BasicWorker, with `Fishing` a generation question first.", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- ARCHITECTURE
p = 'docs/ARCHITECTURE.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("→ **the three remaining gaps** (DarkStudy, hauling upkeep, BasicWorker; `Fishing` is a generation question first).",
              "→ ~~DarkStudy~~ (BUILT 0.6.6-dev; " + FAM + ") → **the two remaining gaps** (hauling upkeep, BasicWorker; `Fishing` is a generation question first).", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- ROADMAP
p = 'docs/ROADMAP.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("**twenty-seven cross-map work families, nineteen of them deployments** including bill work as five families one per work type;",
              "**twenty-eight cross-map work families, twenty of them deployments** including bill work as five families one per work type and dark study;", 1)
s = s.replace(" three work-type gaps remain (DarkStudy, hauling upkeep, BasicWorker)",
              " two work-type gaps remain (hauling upkeep, BasicWorker)", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- REGRESSION_CONTAINMENT: new rot checks + ritual step
p = 'docs/REGRESSION_CONTAINMENT.md'
s = io.open(p, encoding='utf-8').read()
old = "| `is Bill_Production` used as a test that excludes autonomous or mech bills |"
new = ("| A family count of twenty-seven, or DarkStudy described as an open gap | " + FAM + " as of 0.6.6-dev. DarkStudy was built; hauling upkeep and BasicWorker remain |\n"
       "| A def referencing DLC-only content without `MayRequire`, or the claim that the compliance check covers it | It does **not** — it looks for DLC *package ids*, and a def referencing `Childcare` never mentions Biotech. `tools/check-dlc-gating.py` indexes the game's own data and must pass |\n"
       "| `is Bill_Production` used as a test that excludes autonomous or mech bills |")
assert old in s
s = s.replace(old, new, 1)
old = "### The register is generated, and must be rebuilt in the same change"
new = ("""### DLC-only defs must be gated, and the check is not optional

Any def that references content from an expansion must carry `MayRequire` naming that
expansion's package id. This is **not** covered by the compliance check, which looks for DLC
package ids rather than DLC def *names*: a `WorkGiverDef` reading `<workType>Childcare</workType>`
never mentions Biotech anywhere, and shipped ungated from 0.6.4-dev to 0.6.6-dev because of it.

```
python tools/check-dlc-gating.py
```

It indexes every `defName` under `RimWorld/Data/*/Defs/**`, treats anything not defined by
`Core` as DLC-only, and fails on an ungated reference. Reading the game's own data is the
point — a hand-written list of DLC def names would rot exactly the way the thing it checks
rotted. Run it whenever a def is added or edited.

**Handling a DLC def correctly in C# is not sufficient.** `GetNamedSilentFail` makes the
*code* degrade; it does nothing for an unresolved cross-reference in the *def*. Both halves
are required, and that mismatch has now produced two defects in two consecutive checkpoints.

### The register is generated, and must be rebuilt in the same change""")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- WORK_TYPE_COVERAGE_AUDIT
p = 'docs/research/WORK_TYPE_COVERAGE_AUDIT.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("| **DarkStudy** | 1 | Anomaly | **none** | **Gap — candidate, and the most on-theme of them** |",
              "| **DarkStudy** | 1 | Anomaly | `dark-study` deployment | **Covered 0.6.6-dev** |", 1)
s = s.replace("**As of 0.6.5-dev: seventeen work types have a deployment.** Two are decided against permanently. **Three genuine gaps remain** — `DarkStudy`, `BasicWorker` and the local-container half of `Hauling`, with `Fishing` a generation question before it is a work question.",
              "**As of 0.6.6-dev: eighteen work types have a deployment.** Two are decided against permanently. **Two genuine gaps remain** — `BasicWorker` and the local-container half of `Hauling`, with `Fishing` a generation question before it is a work question.", 1)
s = s.replace("### 2. DarkStudy — one giver, and the most thematically apt thing in the audit",
              "### 2. DarkStudy — BUILT 0.6.6-dev, and the most thematically apt thing in the audit", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- NOW
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("| Published | 0.6.5-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |",
              "| Published | 0.6.6-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |")
s = s.replace("| Build | 114 C# source files, 76 approved package files, zero warnings, zero errors |",
              "| Build | 115 C# source files, 76 approved package files, zero warnings, zero errors |")
s = s.replace("| Assembly | SHA-256 `51D2DB71724A7559FCE6092406040C6660EDCF15817732511D74C3A018D7E8EC`, reproduced by two full recompiles after deleting `obj/` and `bin/` |",
              "| Assembly | SHA-256 `238DA7119BECD99E080312C23FAC129E6996C805AD2A48A1E2405656CF86DEA0`, reproduced by two full recompiles after deleting `obj/` and `bin/` |")
s = s.replace("**Twenty-seven cross-map work families, nineteen of them travel-to-work deployments.**",
              "**Twenty-eight cross-map work families, twenty of them travel-to-work deployments.**")
s = s.replace("- **Register checkpoint, still 0.6.4** —",
              "- **0.6.6** — **dark study**: a researcher crosses to a contained entity. Plus a second shipped defect closed — the childcare giver defs had referenced a Biotech-only work type with no `MayRequire` since 0.6.4, an unresolved cross-reference on a Core-only install. `tools/check-dlc-gating.py` now enforces it from the game's own data.\n- **Register checkpoint, still 0.6.4** —", 1)
old = """   2. **DarkStudy** — Anomaly, one giver, `[MayRequireAnomaly]`. The most on-theme item in the audit: studying a contained entity is the premise of the mod.
   3. **Hauling upkeep**"""
new = """   2. ~~**DarkStudy**~~ — **BUILT 0.6.6-dev.** Do not reopen; read `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`.
   3. **Hauling upkeep**"""
assert old in s
s = s.replace(old, new, 1)
old = "5b. **If any register CSV changed**"
new = ("""5b. **If any def was added or edited**, run `python tools/check-dlc-gating.py`. It must exit zero. Handling a DLC def correctly in C# with `GetNamedSilentFail` does **not** cover an ungated `MayRequire` in the def itself; that mismatch has produced two defects in two consecutive checkpoints.
5c. **If any register CSV changed**""")
assert old in s
s = s.replace(old, new, 1)
old = "25. **The register is generated output; the HTML one is the register.**"
new = ("""25. **A def referencing DLC content carries `MayRequire`; the C# guard is not enough.** `GetNamedSilentFail` makes the *code* degrade and does nothing for an unresolved cross-reference in the *def*. `tools/check-dlc-gating.py` indexes the game's own data and must pass. The compliance check does **not** cover this — it looks for package ids, and a def naming `Childcare` never mentions Biotech.
26. **The register is generated output; the HTML one is the register.**""")
assert old in s
s = s.replace(old, new, 1)
for old_n, new_n in ((26, 27), (27, 28), (28, 29)):
    pass
s = s.replace("26. **A prisoner can never cross a gate; a *secure* slave can.**", "27. **A prisoner can never cross a gate; a *secure* slave can.**", 1)
s = s.replace("27. **The portal topology is an unbounded alternation", "28. **The portal topology is an unbounded alternation", 1)
s = s.replace("28. **Never trust a remembered list of anything against the shipped game data.**", "29. **Never trust a remembered list of anything against the shipped game data.**", 1)
old = "7. `docs/research/WORK_TYPE_COVERAGE_AUDIT.md`"
new = "7. `docs/research/WORK_TYPE_COVERAGE_AUDIT.md`"
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated: CHANGELOG, TODO, DEFERRED, ARCHITECTURE, ROADMAP, REGRESSION_CONTAINMENT, coverage audit, NOW")
