# Gate servicing, modelled on how Questionable Ethics runs its vats (0.7.1-dev)

**Baseline:** `a5373a7` (0.7.0-dev, 119 C# files, 76 package files).

**This checkpoint — 0.7.1-dev:** **120 C# source files** (one new), **76 approved package files** (unchanged — one JobDef, one WorkGiverDef and seven keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `751C315B18A79A9EC9B965759261B987B69EF5B43319D5FA59B1D9C7B8B62C5A`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/gate-servicing-2026-09-29/`](evidence/gate-servicing-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request, and the reference I first misread

> *"kinda like maintaince for growth vats questionable ethitcs so pawns dont have to always do it but there is a cool down dead zone where its fine"*

**"Questionable Ethics" is a mod name, not a description.** It is *Questionable Ethics Enhanced*, **profile row 182**, and the owner was pointing at how **its cloning and organ vats** handle upkeep.

I first read it as "ethically questionable" flavour and went as far as asking which way to take the ethics angle. That was wrong, and the correction mattered: the right reading is a concrete, proven mechanic with numbers behind it, and the wrong one would have produced some atmospheric text and no system at all.

**The register is what recovered it.** Row 182 was one query away, and its review carried the package id and the local install path, which led to the mod's own defs and its own description of the model.

## Their model, in their own words

From the vat building description shipped with that mod:

> *"Requires regular maintenance by a skilled scientist and doctor. A sterile room will significantly decrease the maintenance required. If the vat loses power, it will rapidly lose maintenance."*

and from its own defs: a dedicated low-priority maintenance work giver, a job whose report string is *"monitoring and adjusting"* rather than repairing, and a skill chosen per vat.

Three ideas, all better than a plain service timer:

1. a condition that **decays continuously**, rather than a countdown to a service date;
2. **the room modulates the decay** — keep it clean and the thing barely needs you;
3. **losing power degrades it fast**, so neglect compounds.

**Point 2 is the owner's *"cool down dead zone where its fine"*.** It is not a grace timer bolted on top — it falls out of the model. A well-kept room decays so slowly that nobody is called for a long stretch; a filthy one calls somebody constantly. **The player controls the dead zone by looking after the place**, which is a far better answer than a constant I would have had to pick.

## Nothing of that mod is copied, referenced or depended on

Its defs and its assembly are untouched, the feature works with it absent, and the idea was read from its public description and shipped defs exactly as every other profile row has been read. **The register exists so that shapes proven elsewhere can inform the design without importing anything**, and this is the clearest case of that so far.

That also honours the owner's standing rule, stated earlier the same day: *"we are making a mod that works with the other 274, WE ARE NOT EDITING OTHER PEOPLES MODS!"*

## What was built

A condition on the gate assembly, in ticks, ten days at full.

| Factor | Effect |
|---|---|
| Room cleanliness, sterile (+2) | **×0.5** wear |
| Room cleanliness, neutral (0) | ×1 |
| Room cleanliness, filthy (−5) | **×3** wear |
| No power | **×8** |
| Connection held open | **×3** |

Clamped at both ends so no room configuration can stop wear entirely or run it away. Cleanliness comes from `RoomStatDefOf.Cleanliness` — Core's own number, so a mod that changes how cleanliness is computed changes this too.

**The dead zone is a threshold, and that is the load-bearing detail.** The obvious implementation is "offer the work whenever condition is below full", and it would be wrong — it is the growth-vat-one-nutrition-short problem, and a pawn would top the gate up continuously, which is exactly the *"pawns dont have to always do it"* the direction rules out. So the work is offered only below **25%**, and reconditioning restores **full** condition in one visit. Between the two, nobody is offered the job at all.

`ServiceWanted` is false across that whole band, so the work giver's global scan finds nothing and costs one boolean per console for most of a game.

## How it connects to what is already here

The model is worth having partly because it plugs into systems this mod already built rather than sitting beside them:

- **cleanliness** is maintained by the cleaning family, which already crosses a gate — so a gate chamber on either side of a portal is kept by the same work;
- **power** is the kill switch and the native power binding from the previous checkpoint. Throwing the cutoff now has a cost beyond closing the gate, because an unpowered assembly degrades **eight times** faster;
- **skill** reuses the `Research` work type that calibration already uses, so **no new work type is added** and the player's existing priorities keep meaning what they meant.

## Lapsing stops the next opening. It never slams one shut.

A gate with no condition left **refuses to open** — `NativeBindingFailureKey` reports it, ahead of the generic power failure so the reason is legible.

It does **not** close an opening already running. Ending one for a bookkeeping reason would strand whoever is on the far side, and the emergency-return window exists for real emergencies rather than paperwork. The kill switch closes a gate on purpose; this decides whether one may be opened at all.

## What it costs

Work time by a skilled colonist, and nothing else. No material is consumed, because the direction's ceiling is explicit — *"not crazy amounts"* — and a resource cost on a recurring chore is how maintenance systems turn into a tax.

The work happens at the console, not the door. A door is a `Building_Door` that pawns path through constantly, and reserving one for a long job would fight ordinary traffic; the console already has an interaction cell and a proven job pattern. The job mirrors calibration exactly — same skill, same progress bar, same failure conditions — so the two console jobs cannot disagree about who is allowed to stand there.

Priority **102**, just above ordinary research and calibration, because a lapsed assembly blocks every expedition while research merely waits. It cannot starve research in practice, because it is unavailable across the whole dead zone.

## Saved state

One integer, `rr_gateServiceConditionTicks`, defaulting to **−1** which reads as *full*. Every gate in a 0.7.0-dev save loads in full condition rather than lapsed, which is the only safe default: the alternative would silently disable every existing player's gates on upgrade.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- `tools/check-keyed-strings.py`: 1,135 keys, 0 duplicates, 0 argument mismatches, all references resolving.
- `tools/check-dlc-gating.py`: 6,063 DLC-only defs indexed, 6 references, all gated.
- `tools/research/audit-gate0.py`: PASS, zero errors.
- Compliance: one JobDef and one WorkGiverDef added, **no patch operation, no asset, no new work type**, nothing of another mod copied or referenced. 76 approved package files, 0 missing. Reference manifest recomputed, no drift. No attribution strings.

## Not done, and named

- **A player-facing how-to for the gameplay and systems.** Requested in the same direction as maintenance and still owed. `docs/HOWTO.md` documents the build, not play. This is now the more pressing of the two, because servicing is the third interacting system on the gate — power, cutoff, condition — and a player has no written explanation of how they fit together.

## For the post-completion test phase

Watching a gate in a clean, powered room and confirming its condition falls slowly and nobody is sent to it for a long stretch; letting the room get filthy and confirming the wear factor in the readout rises and reconditioning is wanted much sooner; cutting power and confirming the wear factor jumps to roughly eight times; throwing the kill switch and confirming the same; holding a connection open and confirming the extra wear; letting condition reach zero and confirming the gate refuses to open with a readable reason **and that an opening already running is not closed**; sending a colonist to recondition and confirming one visit restores full condition; confirming nobody is offered the work anywhere above a quarter condition; and loading a 0.7.0-dev save to confirm every existing gate reads as full rather than lapsed.
