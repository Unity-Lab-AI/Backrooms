
---

## 2026-09-29 — Gate servicing, modelled on how Questionable Ethics runs its vats (0.7.1-dev)

### Verbatim owner requests

> *"kinda like maintaince for growth vats questionable ethitcs so pawns dont have to always do it but there is a cool down dead zone where its fine"*

> *"i said questionable ethics, its a mod"*

> *"i said i was refresncing the mod \"Questional ethics\" and how maintaince works on cloning vats and organ vats"*

### A misreading of mine, corrected by the owner, and what recovered it

- [x] **I read "questionable ethics" as flavour** and went as far as asking which way to take the ethics angle, framing it as a content-policy question. It is a **mod name** — *Questionable Ethics Enhanced*, **profile row 182** — and the owner was pointing at a concrete, proven mechanic with numbers behind it. The wrong reading would have produced some atmospheric text and no system at all.
- [x] **The register recovered it in one query.** Row 182 was a single lookup, and its review carried the package id and the local install path, which led straight to the mod's own defs and its own description of the model. This is the clearest demonstration yet of what the 294 reviews are for.

### Their model, read from their own shipped description

- [x] > *"Requires regular maintenance by a skilled scientist and doctor. A sterile room will significantly decrease the maintenance required. If the vat loses power, it will rapidly lose maintenance."*
  Plus, from their defs: a dedicated **low-priority** maintenance giver, and a job whose report string is *"monitoring and adjusting"* rather than repairing. Three ideas, all better than a service timer: a condition that **decays continuously**; **the room modulating the decay**; and **power loss degrading it fast**.
- [x] **The owner's "cool down dead zone" falls out of the model rather than being bolted on.** A well-kept room decays so slowly nobody is called for a long stretch; a filthy one calls somebody constantly. **The player controls the dead zone by looking after the place** — a far better answer than a constant I would have had to pick.
- [x] **Nothing of that mod is copied, referenced or depended on.** Its defs and assembly are untouched and the feature works with it absent. The idea was read from its public description exactly as every profile row is read, honouring *"we are making a mod that works with the other 274, WE ARE NOT EDITING OTHER PEOPLES MODS!"*

### What was built

- [x] **A condition in ticks, ten days at full**, wearing at **×0.5** in a sterile room, **×3** in a filthy one, **×8** with no power, and **×3** while a connection is held open. Clamped at both ends so no room configuration stops wear or runs it away. Cleanliness is `RoomStatDefOf.Cleanliness` — Core's own number.
- [x] **The dead zone is a hard threshold, and that is load-bearing.** "Offer the work whenever condition is below full" would be the growth-vat-one-nutrition-short trap and would have a pawn topping the gate up continuously — exactly the *"pawns dont have to always do it"* the direction rules out. Offered only **below 25%**, restores **full** in one visit. `ServiceWanted` is false across the whole band, so the giver's scan finds nothing and costs one boolean per console for most of a game.
- [x] **It plugs into what already exists.** Cleanliness is kept by the cleaning family, which already crosses a gate, so a chamber either side of a portal is kept by the same work. Power ties to the kill switch built the checkpoint before, which now costs more than closing the gate. Skill reuses the `Research` work type calibration already uses, so **no new work type is added** and existing player priorities keep their meaning.
- [x] **Lapsing stops the next opening and never closes one already running.** Ending an opening for a bookkeeping reason would strand whoever is on the far side; the return window is for real emergencies. The kill switch closes a gate on purpose, this decides whether one may be opened.
- [x] **Cost is work time by a skilled colonist and nothing else** — the direction's ceiling is explicit, *"not crazy amounts"*, and a resource cost on a recurring chore is how maintenance turns into a tax. The job mirrors calibration exactly, at the console rather than the door, because reserving a `Building_Door` for a long job would fight ordinary traffic.

### Saved state

One integer, `rr_gateServiceConditionTicks`, defaulting to **−1 which reads as full**. Every gate in a 0.7.0-dev save loads in full condition rather than lapsed — the only safe default, since the alternative would silently take every existing player's gates out of service on upgrade.

### Documents updated in the same change

`implementation/GATE_SERVICING_IMPLEMENTATION.md` (new record), `TODO.md` (three owner directions captured verbatim, including my misreading and its correction), `DEFERRED.md`, `NOW.md`, `CHANGELOG.md`, `About.xml`, the csproj.

### Build evidence

0.7.1-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **120** C# source files (one new), **76** approved package files (unchanged; one JobDef, one WorkGiverDef and seven keyed strings added to existing files — **no patch operation, no asset, no new work type**). Assembly SHA-256 `751C315B18A79A9EC9B965759261B987B69EF5B43319D5FA59B1D9C7B8B62C5A`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence folder `implementation/evidence/gate-servicing-2026-09-29/`. `check-keyed-strings.py` 1,135 keys with 0 duplicates; `check-dlc-gating.py` passes; `audit-gate0.py` PASS with zero errors; reference manifest recomputed with no drift; no attribution strings. Published via the cascade in `PUBLISHING.md`; refs read back in session output. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Source files modified: 4. Package files modified: 3 (no new files). Docs updated: 6 (1 new).
Owner directions captured verbatim: 3, one of which corrected a misreading of mine.
**Misreadings of mine caught by the owner: 1**, and the right reading turned a vague flavour note into a concrete mechanic with numbers.
Register lookups that recovered the real answer: 1 (row 182, one query).
Nothing of another mod copied, referenced or depended on.
Still open and named: the player-facing how-to for the gameplay and systems, now the more pressing item because power, cutoff and condition are three interacting systems on one gate with no written explanation of how they fit.
