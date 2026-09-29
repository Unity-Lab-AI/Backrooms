# The survey tag becomes a glow pod — 0.10.7-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## The direction

> *"tyhe glow pods can be used and lets not limit the amount as a backrooms instance can have
> 100s of rooms if the player is using 300x300 maps for instance and maybe lets have the glow
> pods color setable"*

> *"color means differnt types of the needs markers"*

The second sentence decides how the first is built, and it is the reason RimWorld's own free
colour picker is **not** enabled on these. The colour *is* settable — you set it by choosing
what the marker is for. A free picker would let a player paint a danger marker the same green
as a cleared one, and the entire value of a colour here is that it reads across a dark room
without selecting anything.

---

## The register, checked first

| Query | Result |
|---|---|
| `register-query.py find glow` | **Zero rows** in 295. |
| `register-query.py find light` | 27 rows, every one incidental — frameworks, DLC, animal apparel. Nothing touches `CompGlower`, glow colour or the glow grid. |
| `register-query.py family "field support"` | 14 rows, all animal mods; the family label is *"Animals and field support"*. |

**Nothing applied.** Recorded because the LAW requires the check to be stated either way, and
because a zero here is itself worth knowing: no mod in the profile competes for the glow grid,
so setting a per-instance glow colour is safe to build on.

---

## What Core's glow pod actually is

Read from `Data/Core/Defs/ThingDefs_Buildings/Buildings_Natural.xml`, not remembered:

| | |
|---|---|
| `thingClass` | `Building` |
| `minifiedDef` | `MinifiedThing` — **so it crates, hauls and installs natively** |
| `CompProperties_Glower` | `glowRadius 6`, `glowColor (113,141,117,0)` |
| `CompProperties_Lifespan` | **`lifespanTicks 1200000`** |
| Description | *"Glows under its own light for a long time, then dies."* |

That lifespan is **twenty in-game days**, and it is the one fact that shaped the design. A
route home that evaporates on day twenty is not a route home.

`CompLifespan.age` is a **public field** (decompiled `Verse.CompLifespan`), so a designated pod
is held at zero and an undesignated one is not touched at all. A glow pod dropped by an insect
hive on an ordinary map still dies on schedule, still glows its own green, and gains one button
that does nothing until pressed.

---

## The shape

The same shape the gate already uses on doors: **a component on every one of them, dormant
until designated.**

| Piece | What it is |
|---|---|
| `RimroomsMarkerTypeDef` | What a marker means. Label, description, `glowColor`, `displayOrder`, `countersDistortion`. Five defs. |
| `CompRimroomsMarker` | On Core's `GlowPod` by conditional patch. Dormant until designated. |
| `Patches/RR_GlowPodMarker.xml` | `PatchOperationConditional`, so running twice is not an error. |

### The five

| Marker | Colour | Meaning |
|---|---|---|
| **route home** | pale blue | the way back, at every junction where it is not obvious |
| **cleared** | green | searched, nothing left worth returning for |
| **danger** | red | something happened here, or is still here |
| **supply cache** | amber | more than one trip's worth is here |
| **unexplored lead** | violet | a way on nobody has taken |

Only **route home** carries `countersDistortion`. That is a field on the def rather than a
hardcoded def name, so what a colour means *mechanically* is data sitting beside the colour.

---

## Every cap found, and removed

The direction was *"lets not limit the amount"*. There were **three**, not one:

1. **One deployed aid per room.** `DeployAid` refused a second marker in a room that already
   had one. Gone with the deploy order.
2. **Six per crew, enforced at dispatch.** The expedition kit check refused to dispatch a crew
   carrying fewer than six survey tags, with its own refusal string. A kit check that will not
   let you leave without exactly six of something is the same limit wearing a hat.
3. **A recipe that made exactly six.** Retired; glow pods are bought by the crate now.

There is no cap of any kind left: not per room, not per coordinate, not per map.

---

## A branch that could never fire

`ResolveDistortion` decided whether a marked junction countered a corridor distortion:

```csharp
bool protectedRoute = DeployedAids().Any(a => a.Beacon && ...) && DeployedAids().Any(a => !a.Beacon && ...);
```

`Beacon` came from `RR_ReturnBeacon`, **retired in 0.9.9-dev**. After that retirement no
deployed aid could ever report `Beacon == true`, so the first clause was permanently false, so
the whole outcome was unreachable. No checker could see it: the code compiled, the property
existed, and the def it depended on was simply never instantiated again.

Marker types gave it a real condition for the first time — a junction marked *route home*, and
still where it was put, counters the distortion.

**Found by reading the code the retirement touched**, three checkpoints after the retirement.
The general lesson is already an invariant in another form: removing a def means removing every
rule that could only be satisfied by it.

---

## Two things that would have been bugs

**Moving a building by writing `Position`.** The corridor distortion moves a marker into the
wrong room. The retired code did `tag.parent.Position = cell`, which works for a small item and
is wrong for a `Building` — a building's cells are registered in the map's thing grid at spawn,
and moving one without despawning leaves the grid pointing at where it used to be. `RelocateTo`
despawns and respawns.

**Re-binding on respawn.** That respawn would immediately re-read the room the marker had just
been moved into and quietly agree with it, erasing the discrepancy the move exists to create. A
`relocating` flag suppresses the rebind for exactly that instant. The rebind itself is wanted in
the other case: a marker a player uninstalls and sets down elsewhere really is in a new room,
and saying otherwise would read exactly like the space having moved it.

---

## Supply, all of it native

**Starting grant.** `ScenPart_StartingThing_Defined` with `GlowPod`, count 8 — up from six
tags. Verified by decompiling: Core's own `GenerateThing` does
`if (thingDef.Minifiable) { thing = thing.MakeMinified(); }`, so the scenario hands over eight
crated pods with **no code from us at all**.

**Procurement.** A catalogue entry, `RR_Procurement_MarkerPods`. One line changed in
`CreateHeldCargo`: `ThingMaker.MakeThing(itemDef).TryMakeMinified()`. An uncrated building
sitting in a cargo hold is a thing no colonist can pick up, and this was latent for **every**
minifiable def the catalogue might ever carry, not only this one.

**Deployment.** The ordinary install order. **Five moving parts became none** — the retired tag
needed an order, a job driver, a reserved cell, a free inventory slot and a per-room limit
before a pawn could put one down.

---

## Retired, archived, never deleted

To `docs/implementation/historical-content/0.10.7-dev/`, in the layout the 0.2.0 retirement
established:

| Retired | |
|---|---|
| `RR_SurveyTag` | ThingDef |
| `RR_MakeSurveyTags` | RecipeDef |
| `RR_DeployRouteAid` | JobDef |
| `CompRouteAid`, `JobDriver_DeployRouteAid` | source |
| `RR_SurveyTag.png` | texture, removed from the package allowlist |
| 11 keyed strings | including the kit refusal and the deploy failures |

`PHASE_2_THREAT_IMPLEMENTATION.md` is a dated record and its **sentences were not touched** —
only the link path, repointed at the archive, which is what the 0.2.0 retirement did too.

---

## Receipts

| | |
|---|---|
| Version | 0.10.7-dev |
| Build | 159 C# files, 82 package files, **0 warnings, 0 errors** |
| New source | `Investigation/RouteMarkers.cs` |
| New defs | `RimroomsMarkerTypeDef` ×5 — a mechanics def, **no gameplay ThingDef** |
| New package files | marker types, the patch, `RR_Markers.xml` |
| New art, audio or texture | **none**, and one texture left |
| Harmony | **none** |
| Checkers | **seven**, all passing |
| Game launched | **no** |

Four Core facts taken from decompiled source rather than memory: `CompLifespan.age` is public,
`CompGlower.SetGlowColorInternal` re-registers the glower itself, `MinifyUtility.TryMakeMinified`
passes non-minifiable things through unchanged, and `ScenPart_StartingThing_Defined` minifies
its own output.
