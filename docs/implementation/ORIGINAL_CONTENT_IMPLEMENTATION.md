# Original content — art, audio, and the four things it touched

**Build 0.13.0-dev, 2026-10-06.** The record for the reversal of the existing-content-only
direction and everything that shipped under it.

## The direction

**Owner, 2026-10-06, verbatim:**

> *"read now.md to get back to it and hey i have big question and im excited i just saw the pngs in
> C:\Users\gfour\Desktop\Backrooms\assets\source\phase2 whats phase 2 are we making our own items
> and benches and gates? becasue if so i fucking love it! analysis and examination of these pngs and
> what they are for and if we have what we need to do this all and a audio folder! sounds dope!!!
> how do we do sounds can we? can we do all of this for all our shit?"*

Asked which way to take it, the owner chose **full reversal — our own items and benches**, over
sound-only, over gate-identity-only, and over leaving the 0.2.0 content archived. Then, in order:

> *"remember things rotate"*
>
> *"rmeembr this might change the set gate option and stuff on doors"*
>
> *"and the journal"* · *"journal(s)"*
>
> *"and the comms console and machining bench"*
>
> *"need to be able to build upto three gates of differnt sizes to... remember?"*
>
> *"do it all in the needed order and completely and thouroughly correct to the games requirments
> and having mods not breaking it that are in the suggested list... i cuttenlty have 296 (6DLCs,
> Rimbridge , Rimrooms(locally))"*

## What it reverses, and what it does not

It reverses the binding direction of **2026-09-28** in `CONTENT_REUSE_POLICY.md`. That sentence is
deleted nowhere: it is what retired this art across 0.9.0-dev, 0.9.9-dev and 0.12.22-dev, every
retirement record cites it, and invariant 105 forbids making a removal look like progress.

**Three things did not reverse, and inferring otherwise would have broken the mod.**

| Unchanged | Why |
|---|---|
| **No cloned door def** | Gate sizes come from **binding a run of adjacent real doors** — 1x1, 1x2 on `OrnateDoor`, 1x3 and 2x3 bound, plus Doors Expanded's multi-cell doors. Cloning destroys the binding, and cuts the gate off from register rows 273 Locks, 77 Doors Expanded, 185 ReBuild, 252 Vault Walls and Doors, 201 Secret Passage Doors, 265 AirtightGarageDoors. It is also what a prisoner crossing rides on, since *"if zoned to and door are allowed access"* is door permissions |
| **Never copy another package's assets** | Untouched by the reversal, and now the clause most at risk. `check-register-compliance.py` rule 6a requires every shipped gameplay asset to have a master under `assets/source/` |
| **Reuse stays the default** | Original content is added **beside** every reuse binding. A branch that builds none of it works exactly as before |

## Register consulted before building

| Row | What it said | What was done |
|---|---|---|
| 53 Big Little Mod Patch | *"the bill work family reads its bench set from every loaded WorkGiverDef's `fixedBillGiverDefs`, so any bench this patch bundle links is covered with no code naming it"* | The field analysis bench is a real `Building_WorkTable`, so recipes are additive later with no code naming them. It ships with none |
| 49 Better Electronics | *"electrical gate operation cannot require incidents this mod suppresses"*, *"Do not patch its vanilla incident definitions"* | `CompProperties_Breakdownable` is declared on **our** defs, never patched onto theirs, and no gate progression depends on a breakdown |
| 148 No Quests Without Comms | *"configuration only; Rimrooms objectives must not depend on this quest filter"* | The company console is a real `Building_CommsConsole` and depends on no quest. The journal carries **no** `BookOutcomeProperties_GiveQuest` for the same reason |
| sound family | **Zero rows of 294 touch audio** | No conflict surface for the four cues |
| book family | **Zero rows of 294 touch books** | The journal inherits `BookBase`, so every mod that handles books handles it |

## What shipped

**Audio.** Four original cues, and the system was already built — `RimroomsAudio` has mute
settings, a volume factor, main-thread and map guards, warn-once and ten call sites. `ResolveNativeCue`
existed only to redirect our four cue names at Core sounds.

- **Three of the four were playing in the wrong place.** Every call site hands the service a map and
  a cell; `Message_ThreatSmall`, `CommsWindow_Open` and `Message_NegativeEvent` are interface sounds
  that play at the camera, so that position was passed in and discarded. Ours are `MapOnly` with a
  `distRange` of 12~55. **A gate warning comes from the gate.**
- **Where a cue plays is the def's property now, not a second derivation.** The old code decided with
  `cueId != "RR_GatePowerRise"`; `Usable` reads it off the resolved def and requires every subsound
  to agree, because one `SoundInfo` is built for the whole def.
- **Core's sounds remain as the fallback.** A package stripped of its `Sounds` folder degrades to the
  0.12.x presentation and says so once, rather than going silent.

**Art.** `tools/cut-phase2-art.py` derives every shipped texture from the 1254x1254 masters.
**15 textures, 532 KB, from 11.5 MB of masters.** Four are cut and held.

**Defs.** Six buildings, one terrain, one journal — the liminal fluorescent fixture, the company
utility generator, the emergency cutoff, the site marker beacon, the company gate console, the field
analysis bench, faded institutional carpet, and the company route recording.

## Things rotate

`Graphic_Multi` resolves `_north`, `_east` and `_south`; RimWorld mirrors `_west` from `_east` and
nothing else is free. `check-register-compliance.py` **rule 6b** fails the build on a `Graphic_Multi`
of ours missing any of the three, so one frame can never be shown four times.

| Strategy | Which | Why it is honest |
|---|---|---|
| `uniform` | emergency cutoff, site marker beacon | A button on a box and a lamp on a tripod read the same from every side |
| `flat` | site fluorescent | **A strategy the first draft was missing.** A flat fixture read from above genuinely turns with its footprint, so `_east` is `_south` turned ninety degrees, drawn at 128x384 for the swapped footprint. Geometry, not a trick |
| non-rotatable | machine gate, gate console, utility generator, field analysis bench | Drawn as front elevations with a clear face. No back view and no side view exist, so they ship `Graphic_Single` and the tool prints them under **ROTATIONS WANTED** |

## Adding content was one decision from breaking the door's set-gate button

The role test was hard-coded **twice** — `OperationsGateBinding`'s lister and `NativeGateBinding`'s
`ExactProvider` — so widening one would have offered a console the other refused, which reads to a
player as a broken button. `RimroomsGateProviders` owns it once.

**The component is the allowlist**, which is this codebase's own existing principle, stated at
`NativeDoorProvider` about doors. `CompRimroomsGateConsole` is attached by our patch to `CommsConsole`
and `TableMachining`, declared directly on our two buildings, and attached by nothing else — and it
has always refused to attach to a def whose `thingClass` is neither `Building_WorkTable` nor
`Building_CommsConsole`. **So membership is the component and role is the type.** No def name is
tested except to ask *is this one ours*.

**And the obvious implementation was a regression in a feature's clothes.** The button binds a role
only when it resolves unambiguously, so *our building is one more candidate* means a branch that built
the company console **beside** Core's is suddenly told `RR_NativeGate_NoSingleConsole` — the owner's
own open report of 2026-10-03, caused by adding content. `Preferred` gives exactly one of ours
priority over any number of native ones: **building ours can only ever resolve an ambiguity.**

The battery is deliberately **not** widened. Accepting anything with a `CompPowerBattery` would admit
every battery in the profile, in the one role a crew's way home depends on, and the company ships no
battery to widen for.

## The journal

Owner, **2026-10-03**: *"the company is suppose to supply u with a journal to do tasks in but they
only gave me noraml books named wrong things that dont do anything"*. Under the old direction the only
available answer was a Core textbook with a component patched on — literally a normal book named a
wrong thing.

- **Counting is plural; issuing is singular.** `RecordBookDefs` accepts Core's book and ours;
  `RecordBookDef` returns ours when it resolves and Core's otherwise. A save full of Core books keeps
  working and the company hands out its own.
- **It revives `RR_RouteRecording` rather than inventing a def.** `CompRouteEvidence` never stopped
  accepting that exact name from this exact package — a migration path for 0.2.0 saves — so the
  evidence pipeline already worked with it and an old save finds its recordings legible.
- **`IsLegacyCarrier` became `IsCompanyCarrier`.** *Legacy* stopped being true the moment the def
  shipped again, and a reader trusting the old name would have deleted the branch as dead code. The
  test itself is unchanged and stays looser than `CompanyCarrierDef`, because its other job is
  recognising a carrier in an old save whose def no longer fully resolves.
- **`CompProperties_Book` is declared, not inherited.** `BookBase` carries `CompQuality` and
  `ITab_Book` but Core declares `CompBook` per book. Omitting it would make the def silently fail to
  qualify and every caller would fall back to Core's textbook forever — working software, wrong book,
  no error anywhere.
- **One tuned number lost its duplicate.** `analysisWorkRequired` was written as 3000 in the patch on
  Core's book and would have been written again on ours. It lives once, as the C# default, and the
  patch now relies on it too.

## Measured, not asserted

- **A seam metric reported a failure that did not exist, and the number was published before it was
  checked.** The carpet was called 18.3 against a threshold of 6 — *a grid across every room*. That
  measure compared two edge **regions** for similarity rather than asking whether two columns join,
  and it scored a **provably seamless** quad mirror at 7.15. Measuring what tiles actually touch —
  column w-1 against column 0, in units of the texture's own column-to-column difference — the master
  is **x1.4 / x1.7**, a faint seam. The quad mirror still takes it to **x0.00**. The fix was worth
  making; the alarm was not.
- **A drop shadow is not the object.** Bounding boxes at a zero alpha threshold reported the field
  analysis bench as 966x1130, taller than wide, for a visibly long counter. At a real threshold it is
  **876x396**, and the site fluorescent goes from 1.25 to **4.96**. Both footprints come from the
  thresholded box.
- **No texture ships that nothing names.** The 0.9.0-dev retirement's own words were that the art
  *"had no C# consumer whatsoever and had been shipping textures nobody could see"*. The cutter
  **derives** shipment by reading which paths the shipped defs and the C# source reference. Held:
  `RR_FieldRecorder`, `RR_SurveyTag`, `RR_SealedEvidenceCase`, `RR_QuietPursuer`.

## A new checker, because only the owner launches

`tools/check-def-references.py` parses **12,283 def and abstract names** out of the installed `Data/`
folders — Core and all six expansions — and resolves every `ParentName`, build cost, research
prerequisite, category and Rimrooms type the package names. On a 296-mod profile a typo'd def name is
a red log read as *this mod broke my game*, and it is invisible without the game.

**It passed on its first run, which is not evidence.** Four faults were planted — a missing abstract
parent, a missing research def, a missing build resource and a missing Rimrooms type — and **all four
were caught**, then removed.

It reports **SKIPPED with a non-zero exit** when the game is not on disk, rather than passing. A
checker that passes because it could not look is worse than no checker.

## Two instruments were found stale by this work

- **`check-register-compliance.py` rule 6** asserted *"this package ships gameplay art or audio ...
  Invariant 10 permits original MENU images only"*. A green instrument over a dead restraint is worse
  than no instrument, so it is **replaced rather than removed**: provenance, rotation, and a size
  ceiling.
- **`check-doc-conformance.py`'s `RETIRED_DEFS`** was a typed tuple of ten names, eleven lines above
  a comment diagnosing typed counts as *"a dated assertion wearing a check's clothes"*. Six of the ten
  shipped again, so a rule written to stop the documents promising what the package cannot deliver
  began refusing them for describing what it **does**. It is derived now: archived under
  `historical-content/` and not declared today. `RR_MachineGate` is the only name it still returns,
  which is correct — it is a texture on a button, not a buildable.

## What is not built, named rather than implied

- **The world-space gate overlay.** Drawing the arch across a designated run is a visual judgement
  nobody here can make: only the owner launches, and shipping a world sprite sight unseen is how a
  release earns its first screenshot complaint. The art is used on the designation gizmo instead,
  where a face-on drawing is correct because gizmos draw flat.
- **The Quiet Pursuer's own presentation.** A creature of ours needs a race `ThingDef` with
  `lifeStages` and body graphics, not a texture, and a malformed race def on a 296-mod profile breaks
  other people's pawn rendering. `GATE_0_DECISIONS.md` #25 is restated: the art ban is lifted, the
  rules half stands, and a sprite may never become how a player is warned.
- **The field recorder, the survey tag and the sealed evidence case.** Each one's job is already done
  by something reachable — the journal, a `GlowPod`, and a designated `Shelf`. A second object doing
  an existing object's job is the duplication the reuse policy still warns about, and the owner has
  not asked for any of the three by name.
- **Rotations for the machine gate, gate console, utility generator and field analysis bench.** Only
  the owner can author those.
