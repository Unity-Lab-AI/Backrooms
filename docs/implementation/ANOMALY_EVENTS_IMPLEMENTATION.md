# Things that happen, and the echo reaching items (0.8.4-dev)

**Baseline:** `8bb7887` (0.8.3-dev, 147 C# files, 89 package files).

**This checkpoint — 0.8.4-dev:** **149 C# source files** (two new), **91 approved package files** (two new). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `5A5FE6070667CF540A2A4F4C7DD3227DFD5BFC71F175056E3798D3DC3FBD55D1`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"even wild waky carzxzy creepy things when u add places and events"*

0.7.9-dev built the **places**. This is the **events** half, named as outstanding for four checkpoints rather than quietly dropped.

Plus, arriving mid-build:

> *"not just room shape echoes but echos of thier inhabitance in weird ways and items and equipment and production benches"*

Items and equipment are done here. **Inhabitant echoes are the next checkpoint** — they are a different thing entirely and deserve their own.

## Every effect has an answer, because the threat rules demand one

The frozen rules: readable warning, learnable rule, at least one countermeasure, no unavoidable instant failure.

| Event | What it does | The answer |
|---|---|---|
| a presence | a notice, nothing else | nothing to answer |
| the lights go | every light switches off | **flick them back on — vanilla's own switch** |
| the cold comes in | space drops ~12° | clothing, a heater, or leave |
| seepage | the place is filthier | the cleaning family, which already crosses gates |
| things move | loose items relocate | nothing is lost; it is somewhere else |
| a cold that stays | ~25°, deeper | same, harder |
| total blackout | all dark, one-shot | somebody crosses the dark to the switches |

**The lights case is the best of them** because the countermeasure is vanilla: `CompFlickable.SwitchIsOn` has a public setter, so the event uses the same switch a player already knows how to use. That is a far better answer than a bespoke darkness mechanic.

## Nothing here can trap anybody

**No effect damages a pawn, destroys a thing, or blocks a route.** The threshold room is excluded from every effect, always — that is the "no unavoidable instant failure" rule made concrete rather than promised: whatever happens, **walking back out is still possible.**

Rearrangement moves loose items only, never fixtures: the clue system records a landmark per room, and moving one would quietly break a trail a player is following. It also refuses to move **bonds** — a player's money is not scenery — and if a move fails, the item is put back rather than left unspawned.

## Bounded, and it does not replay

At most two events per visit. A non-repeatable event is **recorded on the coordinate**, so a revisit resumes rather than replays — the same rule the escalation ladder follows. A space a player knows should not perform its party trick every single time they walk in; that turns an unsettling event into a chore.

## The echo now reaches items and equipment

The construction echo covered buildings only, which already included production benches. Items were excluded.

**Items needed a different test, and getting it right mattered.** Faction ownership cannot work for them: a stack of steel in a colony stockpile has a null faction exactly like one lying in a Backrooms corridor. So **origin is the test instead**, and it already existed — anything stamped `Outside` came into existence somewhere the player was, and anything from a coordinate is excluded by the same stroke. That is what stops the place echoing its own contents back at itself.

Bonds are excluded from echoing too.

## The comment-dash checker earned itself back

Two of the new def files failed to parse — `--` inside an XML comment again. **The checker added in 0.7.6-dev caught it and named the rule and the line**, instead of the parser's useless *"not well-formed (invalid token)"* at a column.

That is the second time this exact trap has been hit since the check was written, and the first time it cost nothing to diagnose.

## Not done, and named in `TODO.md`

- **Inhabitant echoes** — *"echos of thier inhabitance in weird ways"*. The place copying your *people*, not just your things. Its own checkpoint.
- **Echoed room shapes.** Room dimensions feed the saved layout fingerprint, so changing them touches generation's validation path.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass; 1,183 keyed references all resolving.
- Compliance: two def/keyed files. **No new gameplay ThingDef, no asset, no patch operation, no new work type.**

## For the post-completion test phase

Confirming no event fires on a first visit or in a Quiet band; confirming at most two fire per visit; confirming a non-repeatable event never fires twice in one coordinate; confirming the threshold room is never affected by any of them; confirming lights can be flicked back on; confirming rearrangement never moves a fixture or a bond and never loses anything; confirming cold is survivable with clothing; and confirming deep coordinates now contain items the player has owned.
