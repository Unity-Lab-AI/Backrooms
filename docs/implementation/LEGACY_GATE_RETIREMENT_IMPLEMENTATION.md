# A gate is a door and nothing else (0.9.0-dev)

**Baseline:** `cd65f6e` (0.8.9-dev, 155 C# files, 92 package files).

**This checkpoint — 0.9.0-dev:** **155 C# source files** (none added, four reduced in size), **79 approved package files** — **thirteen fewer**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `72D0FF07B03FB90FE0DC31615281E2214A0C78ACFF82AF81947488108A12BD3D`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## Why this is first of the four remaining majors

The recorded order is content set → gate model → generator → scenarios → docs, and this is the content set. **It deletes defs**, so anything built against content about to be removed would be built twice. The save break is already declared, so no migration is owed.

It also does something specific for the work immediately after it: retiring `RR_MachineGate` **removes the gate component's second geometry model**, so the multi-cell gate work is written once against one model instead of written and then rewritten.

## What was retired

**Eight defs**, four package XML files, two DefInjected files and **seven textures**, all moved to `historical-content/0.2.0/` rather than deleted, matching the precedent set when the custom audio was retired.

| Retired | Replaced by | Status before removal |
|---|---|---|
| `RR_MachineGate` | a Core `Door` or `Autodoor` the player designates | native path already live |
| `RR_GateConsole` | Core `CommsConsole` and `TableMachining` | native path already live |
| `RR_EmergencyCutoff` | the native kill switch on the gate itself | native path already live |
| `RR_UtilityGenerator` | ordinary Core power on your own grid | no C# consumer at all |
| `RR_FieldAnalysisBench` | designated Core `SimpleResearchBench` / `HiTechResearchBench` | no C# consumer at all |
| `RR_SiteFluorescent` | generation lighting | **no C# consumer at all** |
| `RR_SiteClimateUnit` | nothing; it granted free climate control | **no C# consumer at all** |
| `RR_FadedInstitutionalCarpet` | `BackroomsPalette` colours Core terrain instead | **no C# consumer at all** |

Four of the eight had **no code referring to them whatsoever**. They had been dead weight in the package for some time, shipping textures nobody could ever see.

## What that let the code lose

- **The cutoff component is gone entirely.** Its only host def was `RR_EmergencyCutoff`, and its own gate lookup searched the map for the nearest `RR_MachineGate`. Both are retired, and the native kill switch is what a player actually uses.
- **The station no longer guesses which gate is its own.** It used to fall back to hunting for the nearest `RR_MachineGate`. A station is bound explicitly by the player through the designation UI, and "nearest" stopped being the right answer the moment a branch could run two gates.
- Three config rules describing retired defs, and the dead icon lookups.
- Five orphaned keyed strings.

## A checker gap this exposed, and closed

Retiring the gate textures left **three live C# references to textures that no longer ship** — `ContentFinder<Texture2D>.Get("Buildings/Gate/RR_MachineGate", true)` and two others.

**`check-package-integrity.py` passed clean.** Its texture check only ever read **XML**, and from disk it only ever asked the *weaker* question: does every shipped `.png` have a reference? The serious direction — does every reference have a `.png`? — was never asked of C# at all, and `ContentFinder` reports a missing path at runtime.

The check now scans C# for `ContentFinder<Texture2D>.Get("…")` as well as XML tags.

**It was not validated by planting a fault.** It was validated by **catching three real ones that existed at that moment**, which is stronger evidence than a planted test: the defect was already in the tree and the old checker had already said PASS on it.

`audit-gate0.py` then caught **seven documentation links** pointing at the four files that moved to the archive. Both checkers earned their place in the same checkpoint.

## Not done, and named in `TODO.md`

- **The remaining `IsNativeProvider` branches.** Sixty-odd sites whose else-side is now unreachable. **Deliberately left for its own checkpoint** rather than mixed into a content retirement: the value is code clarity for the multi-cell work, and a diff that says only "remove the dead branch" is reviewable in a way a mixed one is not.
- **The field gear** — `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon`, `RR_SealedEvidenceCase`, `RR_RouteRecording`. These are **not** dead: they carry real mechanics, and the owner has explicitly rejected removing the mechanics to satisfy the asset rule. They need capability replacements built before their defs can go, and that is separate work.
- **`RR_QuietPursuer`**, five `RR_*Staff` PawnKinds and their recipes, which still have code consumers.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass. Package **92 → 79** files. Keyed references 1,214 → 1,207, all resolving; keys 1,270 → 1,265.
- Compliance: **nothing added.** No new def, asset, patch operation or work type — this checkpoint only removes.

## For the post-completion test phase

Confirming a branch can still designate a gate, bind its console and battery, assemble at a machining table and calibrate with all four legacy buildings absent; that the facilities overview lists the Core objects in the gate and control category; that no red error mentions a missing texture or an unresolved def at load; and that a coordinate still generates and looks right with the retired lamp, climate unit and carpet gone.
