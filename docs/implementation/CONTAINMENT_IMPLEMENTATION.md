# Containment you can see from the other side of a gate — 0.12.35-dev

**Row closed in part:** 761 — *"containment rooms, security procedures, prisoner/witness
interviews, staff debrief, quarantine, alarm/escape response, evidence custody, and case
records."* Three of the five remaining halves shipped here: **containment rooms**, **security
procedures** and **alarm / escape response**. Staff debrief and quarantine remain, and the row
stays open for them.

No game was launched. Nothing here claims a gameplay, balance, performance or compatibility
result.

---

## 1. The first design was wrong, and Core said so

The obvious build was a set of containment alerts: low containment strength, high activity, an
untended subject. Before writing any of them, Core's own alert classes were enumerated rather than
assumed absent:

```
.local/tools/ilspycmd.exe -l class Assembly-CSharp.dll | grep Alert_
```

**Four already exist:** `Alert_InsufficientContainmentStrength`, `Alert_DangerousActivity`,
`Alert_EntityNeedsTend` and `Alert_NeedHoldingPlatform`. Shipping our own versions would have been
a **second opinion beside a rule the player is already shown** — the exact defect this project
asserts against every time it closes a presentation gap, and the thing a fault plant caught at
0.12.33-dev.

So they were read instead, and every one of them opens the same way:

```csharp
if (Find.CurrentMap == null) { return false; }
... Find.CurrentMap.listerThings ...
```

**Core's containment warnings are about the map on screen.** That is correct for RimWorld, where a
colony is one map. It is wrong for this mod, whose whole premise is several live maps at once — a
headquarters, the coordinates behind its gates, and any registered remote site. **A player standing
in a coordinate watching a crew work gets no warning at all that something is coming off a platform
back home.**

That is the real gap, it is genuinely ours, and it is the same gap the gate alerts closed at
0.10.5-dev by walking `Find.Maps` instead of reading one map.

### And the two sets never overlap, by construction

Both new alerts **skip `Find.CurrentMap` entirely**. On the map you are looking at, Core's four
alerts are the only voice; ours speak only about the maps you are not looking at. Two alerts about
one platform would teach a player to scroll past both, and making the sets disjoint is cheaper and
safer than trying to match Core's conditions exactly and hoping they stay matched across a game
update.

| Alert | Priority | Condition | Why not Core's job |
|---|---|---|---|
| `Alert_RimroomsContainmentBreachElsewhere` | **Critical** | `CompHoldingPlatformTarget.isEscaping` on a map that is not the current one | Core has no escape alert at all, and cannot see another map |
| `Alert_RimroomsContainmentUnpoweredElsewhere` | **High** | a holder with an occupant and `!PowerOn`, on a map that is not the current one | **Core has no unpowered-holder alert of any kind**, on any map |

The unpowered alert stands down for a platform already being escaped from, so one platform never
produces both.

---

## 2. Containment rooms: the tenth facility category, matched by capability

`RimroomsFacilityCategoryDef` is explicitly presentation data — its own doc comment says
*"classification is presentation data, never a capability grant"* — and the branch readiness report
already has nine categories. Containment is the natural tenth, and **no new `ThingDef` was added**,
which the standing existing-content-only constraint requires.

The first attempt was a `buildingDefNames` list naming `HoldingPlatform`. That was wrong twice
over:

* `HoldingPlatform` is an **Anomaly** defName, so a `<li>` naming it would be read by
  `check-dlc-gating.py` as an ungated expansion reference in a mod whose whole claim is Core-only;
* a named list covers **no modded holder**.

So the def carries no names at all. A new `includeContainment` flag matches by capability:

```csharp
if (includeContainment)
{
    if (building.TryGetComp<CompEntityHolder>() != null) { return true; }
    var bed = building as Building_Bed;
    if (bed != null && bed.ForPrisoners) { return true; }
}
```

`CompEntityHolder` is an abstract comp in the always-present base assembly, so this needs no gate,
covers a modded holder for free, and matches nothing at all on an install without Anomaly.

**Prisoner beds are in deliberately.** Containment is not an Anomaly-only idea in this mod — a
branch holding somebody it brought back has a containment problem — and on a Core-only install a
prisoner bed is the only kind of containment there is.

---

## 3. Security procedures: one standing order, wired to machinery that already existed

*"Security procedures"* is the item in row 761 with no obvious shape, and it was settled by looking
for machinery that already exists rather than by inventing a guard system. Two things did:

* `PersonnelRoles` has carried a **`security`** role since the hiring layer shipped, scored on
  Shooting and Melee;
* `CompRimroomsGate.TriggerEmergencyCutoff()` is a public `CompanyActionResult` entry point that
  closes a live connection **and starts the return window**, so one call both shuts the door and
  brings the crew home.

So a security procedure here is a **standing order the player sets once and the branch executes
without being asked** — which is what a procedure is, as against an order. One order, because one
is what the existing machinery supports honestly: *when something gets loose, do we slam the
doors?*

### Why it is a setting rather than just behaviour

Cutting a connection is consequential: it burns the return window and hurries everybody home. A
player running a long extraction may well decide a rattling platform is the lesser problem.
Invariant 28 wants every rule learnable, and a door that slams for reasons the player never agreed
to is the opposite. So:

* it lives on the **campaign component**, not in mod settings — this is a decision this branch made
  in this save, and a second save may answer differently;
* it **defaults to armed**, which is both the safe reading and what a save written before the field
  existed gets for free, because `Scribe_Values` hands back the default for a missing field.
  Defaulting to `false` would have silently disarmed every existing save, which is one of the
  planted faults;
* the branch **says which it is, in both directions**, in the facilities pane.

### What it deliberately does not do

* **It never re-decides what a breach is.** `ContainmentWatch` reports that Core's own
  `isEscaping` is set; the protocol forms no opinion of its own, and the proof asserts `isEscaping`
  appears nowhere in it.
* **It opens nothing, moves nobody, and touches no subject.** It calls one existing method on gates
  that are already open — the same method the player's own cutoff button calls, so the two can
  never disagree about what closing a connection means.
* **It fires once per incident.** The latch is saved, so a save made mid-breach reloads mid-breach
  instead of re-firing and sending a second letter about connections already shut. It is rearmed
  only when nothing anywhere is getting out.

### The alarm as a noun

`SoundTheAlarm` is a console gizmo beside the call to the company: cut everything, now. It runs
**the same body** as the automatic procedure, because two code paths for slam-the-doors are two
chances to disagree. It refuses with a reason when nothing is open, rather than reporting a success
that closed nothing — a button that claims to work while doing nothing teaches a player the alarm
is broken.

It sits on the comms console rather than a gate because it is a branch-wide order and one gate's
cutoff button already exists for one gate. It is disabled with its reason rather than hidden, so a
player learns the alarm exists before the night they need it.

---

## 4. Register rows read before building

`python tools/register-query.py family security` and `use RR-EVD`. The security family is already
swept, and its standing position is that this mod keeps its own threat and containment loops in
Core terms and never requires a security mod to function. **Nothing here reads a weapon, a turret,
a faction or a defensive structure**, so a profile full of security content changes nothing about
it; and because the response is *cut the connection*, a branch with no security staff at all still
gets the procedure, which is the point of a procedure.

Row **8 Anomaly** is *"optional native anomaly touchpoints; Rimrooms supplies its own Core threat,
evidence, and containment loops"*, so nothing here may become the route through the campaign — and
nothing does: these are warnings and a standing order, and both are inert on a branch holding
nothing. Row **140 Name Your Entities** is display naming only, and because the alerts report
**culprits** rather than composing their own names, a renamed entity reads correctly for free. Row
**138 Move Your Monolith** is a layout utility and touches no holder.

Nothing is patched, nothing is required, and every mod may be absent.

---

## 5. Files

**New:** `src/.../Threats/ContainmentWatch.cs`,
`src/.../Presentation/RimroomsContainmentAlerts.cs`,
`src/.../Company/ContainmentProtocol.cs`, `src/.../Company/ContainmentAlarmGizmo.cs`,
`.local/register/proof-containment.py`, this record.

**Edited:** `src/.../Company/RimroomsCampaignComponent.cs` (two saved fields, three accessors,
two scribe lines), `src/.../Company/CampaignServices.cs` (the tick),
`src/.../Facilities/FacilityReport.cs` (the capability match),
`src/.../UI/OperationsFacilities.cs` (the containment section),
`src/.../Gate/CompRimroomsGateConsole.cs` (the gizmo),
`1.6/Defs/RimroomsFacilityDefs/RR_FacilityCategories.xml` (the tenth category),
`1.6/Languages/English/Keyed/RR_Company.xml`, `1.6/Languages/English/Keyed/RR_Portals.xml`,
`CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `docs/NOW.md`, `docs/TODO.md`,
`docs/FINALIZED.md`.

**No new gameplay content.** One facility-category def (presentation data by its own definition),
sixteen keyed strings and two alert classes; no `ThingDef`, `PawnKindDef`, recipe, bench, item,
texture or sound.

## 6. Verification

* **Build 0.12.35-dev** — 186 C# files, 87 package files, **0 warnings, 0 errors**.
* **Assembly reproduced across two clean rebuilds.**
* **Eleven checkers pass. Thirty-two proofs exit zero.**
* **17 of 17 planted faults caught**, including the two that matter most: an alert that starts
  speaking about the map on screen, and the standing order defaulting to disarmed.
* One checker caught a real miss during the build: `RR_Company_Unavailable` was referenced in the
  protocol's refusals and did not exist. **`check-keyed-strings` found it before it shipped.**
* **No game was launched.** Every statement here is structural.
