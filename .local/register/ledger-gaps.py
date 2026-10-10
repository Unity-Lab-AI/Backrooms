import io

FAM = "**31 families, 23 of them deployments**"

# --- CHANGELOG
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.6.7-dev - 2026-09-29 - every kind of work in the game now crosses a gate

- **Containers on the other side get tended.** A fermenting barrel that wants wort or has beer ready, an egg box with eggs in it, and a pack animal you marked to unload will all now pull somebody across a gate.
- Nobody crosses for a barrel with no wort on that side, or one sitting at a temperature that would ruin it.
- **Somebody will cross a gate to flick a switch, open a container, or eject fuel** — but only where you marked it. Nothing is guessed.
- **With the Odyssey expansion, somebody will cross to fish** a zone you painted on the other side. Water you never zoned attracts nobody.
- All of it is tunable while the game runs, like the rest.

That closes the last of the gaps found when every kind of work in the game was listed out and checked. Every one is now either handled or deliberately left alone with the reason written down.

Full record: [the last work type gaps](docs/implementation/WORK_TYPE_GAPS_CLOSED_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- TODO
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = "- [ ] **Hauling upkeep deployment** — the carry families cover material crossing a gate, but the `Hauling` givers that are **local container operations on the far map** have no coverage at all:"
new = ("- [x] **Hauling upkeep deployment** — **BUILT 0.6.7-dev.** All thirty `Hauling` givers enumerated and classified: seven covered by existing carry families, three **decided against** because their semantics are map-bound (`HelpGatheringItemsForCaravan` and `LoadTransporters` depart from their own map; `HaulToPortal` is Core's own portal system), eleven DLC container givers named and left open pending a custody review, and four built here. Its continue priority follows the **Hauling ladder's own documented exception** rather than the generic rule. Was: the carry families cover material crossing a gate, but the `Hauling` givers that are **local container operations on the far map** have no coverage at all:")
assert old in s
s = s.replace(old, new, 1)
old = "- [ ] **BasicWorker deployment, and Fishing settled first**"
new = ("- [x] **BasicWorker deployment, and Fishing settled first** — **BOTH BUILT 0.6.7-dev.** BasicWorker is purely designation-driven (`Flick`, `Open`, `EjectFuel`), so it reuses `FieldworkScan`. `Fishing` was settled and then overtaken: a coordinate *does* carry water (`GenStep_BackroomsDestination` uses `WaterDeep` as its void floor), but the deciding fact is that Core will not fish anywhere the player has not painted a `Zone_Fishing` — so it is the growing-zone shape and the terrain question is not load-bearing. Was: ")
assert old in s
s = s.replace(old, new, 1)
s = s.replace("**FIFTH PASS BUILT 2026-09-29 in 0.6.6-dev:** dark study — **28 families, 20 of them deployments**. Record `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`.",
              "**FIFTH PASS BUILT 2026-09-29 in 0.6.6-dev:** dark study — 28 families. Record `implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md`. **SIXTH PASS BUILT 2026-09-29 in 0.6.7-dev:** hauling upkeep, BasicWorker and Fishing — " + FAM + ". **Every work type in the game is now either covered or decided against with its reason recorded.** Record `implementation/WORK_TYPE_GAPS_CLOSED_IMPLEMENTATION.md`.", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- DEFERRED
p = 'docs/DEFERRED.md'
s = io.open(p, encoding='utf-8').read()
old = "- [ ] **Hauling upkeep deployment** — open. The `Hauling` givers that are local container operations on the far map, including `HaulMechsToCharger`."
new = ("- [x] **Hauling upkeep deployment** — **BUILT 0.6.7-dev**, " + FAM + ". All thirty Hauling givers classified; three decided against as map-bound; eleven DLC container givers named and open. Superseded text, kept per the never-delete rule: *open. The `Hauling` givers that are local container operations on the far map, including `HaulMechsToCharger`.*\n"
       "- [ ] **The eleven DLC container hauling givers** — open, and named rather than guessed at: `HaulToGeneBank`, `HaulToGrowthVat`, `CarryToGrowthVat`, `CarryToGeneExtractor`, `CarryToSubcoreScanner`, `HaulMechsToCharger`, `EmptyWasteContainer` (Biotech), `HaulToBiosculpterPod` (Ideology), `TakeBioferriteOutOfHarvester`, `TakeEntityToHoldingPlatform`, `TransferEntity` (Anomaly). Each carries a pawn or a live subject into a machine or moves an entity between platforms, so each needs its own review of what that does to **custody** before a worker is sent across a gate for it.\n"
       "- [x] **`Strip`** — left out of hauling upkeep deliberately: stripping a corpse or prisoner is custody-adjacent and needs its own review.")
assert old in s
s = s.replace(old, new, 1)
old = "- [ ] **BasicWorker deployment** — open. `Flick` and `Open` are designation-driven, which is the fieldwork pattern."
new = "- [x] **BasicWorker deployment** — **BUILT 0.6.7-dev**, reusing `FieldworkScan`. `ExtractSkull` and `ChangeTreeMode` (Ideology ritual-adjacent) and `BasicReleasePrisoner` (warden work) are deliberately not included. Superseded text: *open. `Flick` and `Open` are designation-driven, which is the fieldwork pattern.*"
assert old in s
s = s.replace(old, new, 1)
old = "- [ ] **`Fishing`** — open as a **generation** question first, not a work question."
new = ("- [x] **`Fishing`** — **SETTLED AND BUILT 0.6.7-dev.** The generation question was answered yes (`GenStep_BackroomsDestination` uses `WaterDeep` as its void floor) and then turned out not to be load-bearing: Core will not fish anywhere the player has not painted a `Zone_Fishing`, so this is the growing-zone shape and the player decides. Odyssey-gated in both C# and XML. Superseded text: *open as a **generation** question first, not a work question.*")
assert old in s
s = s.replace(old, new, 1)
s = s.replace("→ **the two remaining gaps**: hauling upkeep and BasicWorker, with `Fishing` a generation question first.",
              "→ ~~hauling upkeep, BasicWorker and Fishing~~ (ALL BUILT 0.6.7-dev; " + FAM + "). **Every work type in the game is now either covered or decided against with its reason recorded.**", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- ARCHITECTURE
p = 'docs/ARCHITECTURE.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("→ **the two remaining gaps** (hauling upkeep, BasicWorker; `Fishing` is a generation question first).",
              "→ ~~hauling upkeep, BasicWorker, Fishing~~ (ALL BUILT 0.6.7-dev; " + FAM + "). **Every work type in the game is now either covered or decided against with its reason recorded.**", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- ROADMAP
p = 'docs/ROADMAP.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("**twenty-eight cross-map work families, twenty of them deployments** including bill work as five families one per work type and dark study;",
              "**thirty-one cross-map work families, twenty-three of them deployments**, covering or explicitly deciding against every work type in Core and all five expansions;", 1)
s = s.replace(" two work-type gaps remain (hauling upkeep, BasicWorker)", " no work-type gaps remain", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- REGRESSION_CONTAINMENT
p = 'docs/REGRESSION_CONTAINMENT.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("**28 families, 20 of them deployments** as of 0.6.6-dev. Hauling upkeep and BasicWorker remain; `Fishing` is a generation question first.",
              FAM + " as of 0.6.7-dev. **No work-type gaps remain** — every work type in Core and all five expansions is covered or decided against.", 1)
old = "| `is Bill_Production` used as a test that excludes autonomous or mech bills |"
new = ("| A cross-gate **Hauling** priority placed \"just above Core's highest giver in the type\" | That rule does **not** apply to Hauling. The cross-gate hauling ladder is calibrated against `HaulGeneral` (15) and deliberately loses to Core's urgent hauling — `CONNECTED_FOOD_IMPLEMENTATION.md` states it outright. Read the existing records before picking a number |\n"
       "| `is Bill_Production` used as a test that excludes autonomous or mech bills |")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- coverage audit
p = 'docs/research/WORK_TYPE_COVERAGE_AUDIT.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("| Hauling | 30 | Core/Ideology/Biotech/Anomaly | `storage-hauling`, `casualty-rescue`, `fuel-supply` carry | **Partly** — see below |",
              "| Hauling | 30 | Core/Ideology/Biotech/Anomaly | carry families + `hauling-upkeep` deployment | **Covered 0.6.7-dev** for Core; eleven DLC container givers named and open |", 1)
s = s.replace("| BasicWorker | 6 | Core/Ideology | none | **Gap — candidate** |",
              "| BasicWorker | 6 | Core/Ideology | `basic-worker` deployment | **Covered 0.6.7-dev** |", 1)
s = s.replace("| **Fishing** | 1 | Odyssey | **none** | **Gap — candidate, lowest value** |",
              "| **Fishing** | 1 | Odyssey | `fishing` deployment | **Covered 0.6.7-dev** |", 1)
s = s.replace("| Art | 5 | Core | `bill-ingredients` carry + `bill-work-art` deployment | **Covered 0.6.5-dev** for sculpting; painting remains a candidate |",
              "| Art | 5 | Core | `bill-ingredients` carry + `bill-work-art` deployment | **Covered 0.6.5-dev** for sculpting; painting is designation work and belongs with `basic-worker`, recorded below |", 1)
s = s.replace("**As of 0.6.6-dev: eighteen work types have a deployment.** Two are decided against permanently. **Two genuine gaps remain** — `BasicWorker` and the local-container half of `Hauling`, with `Fishing` a generation question before it is a work question.",
              "**As of 0.6.7-dev: twenty-one work types have a deployment.** Two are decided against permanently. **No work-type gaps remain.** Every work type in Core and all five expansions is either covered or decided against with its reason recorded. What stays open is narrower and named: the eleven DLC *container* hauling givers, which each need a custody review, and the four painting givers in `Art`.", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- NOW
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("| Published | 0.6.6-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |",
              "| Published | 0.6.7-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |")
s = s.replace("| Build | 115 C# source files, 76 approved package files, zero warnings, zero errors |",
              "| Build | 117 C# source files, 76 approved package files, zero warnings, zero errors |")
s = s.replace("| Assembly | SHA-256 `238DA7119BECD99E080312C23FAC129E6996C805AD2A48A1E2405656CF86DEA0`, reproduced by two full recompiles after deleting `obj/` and `bin/` |",
              "| Assembly | SHA-256 `9A73827B2E0F6C6AC33712BE447CEA5C7F8959C72820080AE7C2C00BA75A8EAE`, reproduced by two full recompiles after deleting `obj/` and `bin/` |")
s = s.replace("**Twenty-eight cross-map work families, twenty of them travel-to-work deployments.**",
              "**Thirty-one cross-map work families, twenty-three of them travel-to-work deployments. Every work type in the game is covered or decided against.**")
s = s.replace("- **Register checkpoint, still 0.6.4** —",
              "- **0.6.7** — **hauling upkeep, BasicWorker and Fishing**, closing the last work-type gaps. All thirty `Hauling` givers classified; three decided against as map-bound.\n- **Register checkpoint, still 0.6.4** —", 1)
old = s[s.index("1. **The four work-type gaps**"):s.index("2. **A portal whose far side is an ordinary map**")]
new = """1. ~~**The four work-type gaps**~~ — **ALL CLOSED.** Bill work 0.6.5-dev, dark study 0.6.6-dev, hauling upkeep / BasicWorker / Fishing 0.6.7-dev. **Every work type in Core and all five expansions is now covered or decided against with its reason recorded**; joy, rituals, `Patient` and `PatientBedRest` are decided no. Do not reopen any of it — read `research/WORK_TYPE_COVERAGE_AUDIT.md`. What remains here is narrower and named in `DEFERRED.md`: the **eleven DLC container hauling givers** (each needs a custody review before a worker crosses for it) and the **four painting givers** in `Art`.
"""
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated for 0.6.7-dev")
