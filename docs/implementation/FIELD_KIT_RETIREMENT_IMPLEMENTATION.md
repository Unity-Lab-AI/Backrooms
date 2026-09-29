# The field kit, part one (0.9.9-dev)

**Baseline:** `119d9ce` (0.9.8-dev, 158 C# files, 79 package files).

**This checkpoint — 0.9.9-dev:** **158 C# source files**, **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `0E9BEEF6DA1A781EB58E8974340522DF4010EA00004F38F292880677F6FD7F600`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The blocker this clears

The last two scenarios cannot be written while the first one still grants `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon` and `RR_SealedEvidenceCase` — content M2 is retiring. Writing them against it is the exact thing the recorded order exists to prevent.

And these are not deletions. The owner has refused, repeatedly and explicitly, to lose the mechanics: *"Suggestions to remove recorder, route-marker, beacon, case or document custody mechanics remain rejected scope reductions unless an equivalent player function is implemented through existing content."*

So each needed a decision, and each decision needed real Core content behind it.

## Core was enumerated before anything was proposed

Rather than suggesting plausible objects, the installed game was read:

- **26 minifiable defs** — which is what makes a carried, deployable item possible at all. `GlowPod`, `PenMarker`, `OrbitalTradeBeacon`, `Urn`, `ToolCabinet` among them.
- **Essentially one container** with a real `ThingOwner` (`EggBox`), which is what ruled out a like-for-like sealed case and forced an honest question instead of a bad substitution.

## The four answers

| Gear | Becomes | Why |
|---|---|---|
| **Survey tag** | Core **`GlowPod`** | Carried in, placed to mark the route, and it **lights the room**. Marking your way back and pushing the dark back are the same act in this setting. Real item, real weight, real loss. |
| **Return beacon** | **dropped** | The gate's address book (0.8.8-dev) and the saved return threshold already are the route authority. |
| **Evidence case** | a designated HQ **`Shelf`** | The book is carried; custody completes when it reaches a shelf designated as the archive — the same designation pattern as the gate console and the laboratory bench. |
| **Field recorder** | **the book** | One Core `TextBook`: carried in blank, written in the field, carried home as the evidence. The recorder and the record stop being two things that can get separated. |

## Only the beacon shipped here

It is the one that needed **no replacement built**. Its job was genuinely taken over by work already shipped, which makes it a retirement rather than a substitution, and it can be done cleanly in one diff.

Gone: the def, its recipe, its scenario grant, two keyed strings, its deploy button, and all six C# references. `QueueDeployAid` lost its `beacon` parameter — there is one kind of route aid now, so the flag had nothing to select between.

## The checker found the last trace

`RR_ReturnAnchor` — itself legacy, and still live — used the beacon's **texture**. With the beacon gone the package referenced a name it no longer declared.

`check-package-integrity.py` caught it. The texture is renamed to the def that actually uses it, so nothing is left pointing at a dead name. This was **not found by reading the diff**; it was found by the check that exists for exactly this.

## Verified for the next checkpoint

`CompGlower.GlowColor` has a **public setter**, backed by a **saved per-instance `glowColorOverride`**, and `CompProperties_Glower.colorPickerEnabled` turns on RimWorld's own colour picker gizmo.

So settable glow colour needs **no new UI and no new code** — which matters, because the owner's direction is that colour is *semantic*: *"color means differnt types of the needs markers"*, answered as mod-defined marker types each with its own colour, and *"lets not limit the amount as a backrooms instance can have 100s of rooms"*.

## Not done, and named in `TODO.md`

The other three replacements, then the remaining two scenarios.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All five checkers pass; the integrity checker found and then cleared the texture reference.
- Compliance: **nothing added.** This checkpoint only removes.

## For the post-completion test phase

Confirming a new branch starts with no return beacon and no missing-beacon warning; that the expedition kit check passes without one; that survey tags still deploy and recover; that the return anchor still draws; and that no red error mentions a missing def or texture at load.
