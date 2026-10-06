# The cross-map traversal brief

**This document exists because the owner's direction rewrites a founding invariant**, and the
standing pattern for a change that size is their own: *"this is big one to need proper write up
before attempting the work"*.

## The direction, verbatim, in the order it arrived

> *"what??? vistors cant walk through the gate to find work and beds??? we need cross map cordinator or something thats automatic merging maps to cross control so pawns auto get command to cross when mpas call them like a empty bed work task or job ect ect or anything at all"*

> *"not anyone in base, but anyone on your map.. a enemy can break in and cross the gate to get valuables and members"*

> *"hold up now friendlys can too"*

> *"all one person choices in zoning"*

> *"i mena its upto the play to zone pawns where they want them,, that was the whole cross zone support"*

**Two forks were answered before the last three arrived**, both at the permissive end, both with
their cost printed in the option before it was chosen: needs **commute** rather than pawns living on
the far side, where the option said *the window closes mid-sleep and the pawn is stranded*; and
crossing open to **anyone**, where the option said *they can die down there, and that is a faction
incident with no good explanation*. **Message two then replaced "in your base" with "on your map"**,
which is both wider and sharper — a raider does not need to be a guest.

---

## 0. What already exists, measured before any of this was designed

| Piece | Where | What it already does |
|---|---|---|
| Automatic cross-map **work** | `WorkGiver_ConnectedDeployment` | **56 work givers** on RimWorld's own work loop. A colonist is offered a job on the far map and crosses by itself |
| Work-type coverage | `research/WORK_TYPE_COVERAGE_AUDIT.md` | **21 of the game's 23** work types cross. The two that never will are `Patient` and `PatientBedRest` |
| One crossing implementation | `ConnectedCrossing` | *"exactly one implementation of stepping through a gate for work"*, honouring the pawn's danger policy, allowed area and locked doors |
| The chokepoint | `PortalTraversalPolicy` | Every crossing path asks it. `TravellerFailureKey`, `OrderedCrossingFailureKey`, `IncursionFailureKey`, fit and cargo rules |
| Inbound hostile crossing | `GateIncursion` | Something follows your crew **home**. Bounded on five axes, once per opening |
| Cutting a connection | `NativeGateKillSwitch` | `KillSwitchThrown` drives `EnterEmergency("RR_NativeGate_KillSwitchThrown")` in the gate tick |
| Per-map zoning | `Pawn_PlayerSettings.allowedAreas` | **`Dictionary<Map, Area>`**, scribed per pawn *per map* |
| Lords for spawned hostiles | `InhabitantService` | `LordMaker.MakeNewLord` with `LordJob_AssaultColony(faction, canKidnap:, …, canSteal:)` |

**So the cross-map coordinator the first message asks for is shipped — for work.** The gap the owner
put their finger on is exact: **beds appear in that code only for carrying a *downed* patient to
one.** No healthy pawn ever crosses for a need. *"like a empty bed work task"* is the missing half.

---

## 1. The invariant this rewrites, and the part of it that survives

**`PortalTraversalPolicy` currently holds two absolutes:**

```csharp
// "Deliberately constant. A connection opening never grants any non-player pawn a reason,
//  route or permission to traverse. There is no setting, no research and no upgrade that
//  flips this."
public const bool AutonomousNonPlayerTraversalPermitted = false;

public static bool MayApproachThresholdForTraversal(Thing thing) { return false; }
```

**Eight assertions across six documents say so**, and `FINALIZED` entry 54 says it permanently:
*"`MayApproachThresholdForTraversal` must stay false for everything, forever. Incursion works
**because** nothing is drawn to a gate."*

### 1.1 What the invariant was actually protecting, which is two different things

**Read carefully, it bundles an architectural rule with a gameplay rule, and only one of them is
being discarded.**

| The rule | Status |
|---|---|
| **One chokepoint. No scattered permissions. No adapter, scheduler, generator or threat may ever decide a crossing for itself** | **KEPT, UNCHANGED, AND IT IS THE PART THAT MATTERS** |
| **The answer is always no for everybody but our own colonists** | **DISCARDED by owner direction** |

`ARCHITECTURE.md` line 454 states the fear the invariant was built against: *"an open gate can never
become an objective, lure, spawn target, raid route or attack trigger for a later adapter,
scheduler, generator or threat."* **The words that carry the weight are *for a later … threat* —
the worry was a feature quietly growing a crossing of its own.** Keeping one chokepoint answers that
completely, and it is independent of what the chokepoint says yes to.

### 1.2 So the rewrite is narrow and it is a method, not a constant

`MayApproachThresholdForTraversal` becomes a real question with a real answer, asked of the policy
and nowhere else. `AutonomousNonPlayerTraversalPermitted` **stops being a `const bool`**, because a
constant cannot express *"yes, under these named conditions"* — and a constant left at `false` beside
code that crosses anyway is the stale-comment failure this project has a rule about.

**Both are replaced by one named method per direction**, listed in §2. Nothing else gains a vote.

**Every one of the eight assertions is rewritten in the same commit as the first line of code**, per
DOCS-BEFORE-PUSH, and `FINALIZED` entry 54 is **not** edited — the archive is append-only, so the new
record states that the owner superseded it and when.

---

## 2. Four crossings, and direction is what distinguishes them

**This is the distinction the whole brief turns on, and it did not exist before today.** Everything
built so far is either *ours going out and coming back* or *something following us home*. The owner's
direction adds **outbound crossing by somebody who is not ours**.

| # | Who | Direction | Status today |
|---|---|---|---|
| 1 | Our colonists, for **work** | both | **shipped** — 56 givers |
| 2 | Our colonists, for a **need** | both | **missing** — §3 |
| 3 | A **hostile** on the coordinate, following our crew | **inbound** | **shipped** — `GateIncursion`, five bounds |
| 4 | A **hostile or a friendly** standing on our map | **outbound** | **missing** — §5, §6 |

**Inbound and outbound are not symmetric and must not be given the same bounds.** Inbound is a
threat to the colony — the player's people, home and stockpile. Outbound is a threat to a remote
stockpile and whoever is standing on it. The severities differ by a lot, and §9 is where that is
paid out rather than assumed.

---

## 3. Our colonists, crossing for a need

**The owner chose commuting over living there, and was shown the cost.** So the pawn walks over,
satisfies the need, and walks back.

### 3.1 Why this is not simply a fifty-seventh work giver

**Needs are not work.** Rest, food and recreation are satisfied from Core's **think tree** through
`JobGiver_GetRest`, `JobGiver_GetFood` and the joy givers — not from the work loop, which is the only
thing the 56 givers plug into. A need has no `WorkGiverDef` to copy.

This section specified a `ThinkTreeDef` with `insertTag`. **It was built as a map component instead,
0.12.99-dev, and the brief is corrected here rather than quietly departed from.**

| Why the component won | |
|---|---|
| **Strictly more additive** | An insert still edits the shape of Core's humanlike tree at a tagged point. A component edits nothing at all, and with 294 mods loaded the think tree is one of the most contested structures in the game |
| **Cannot fail silently** | An insert whose tag another mod moves, renames or wraps fails with no symptom: a pawn simply never crosses, and there is nothing anywhere to read |
| **It is what the owner asked for** | *"pawns auto get command to cross"* — a command issued, which is what this is. A think node is a pawn deciding; a command is the branch telling them |

`CrossForNeedMapComponent` runs on every owned map and issues the crossing through
`ConnectedCrossing.StepToward` — **the one implementation of stepping through a gate** — so the pawn's
danger policy, allowed area and locked doors are honoured exactly as they are for work. No Harmony,
and nothing of Core's is taken over.

### 3.2 The question has to be asked against an explicit map, and the contract already says so

Core's bed and food searches are scoped to `pawn.Map`, so **they cannot answer *is there a free bed
over there*.** `ConnectedDeploymentProvider` already states the rule this must follow, in its own
words: a provider answers *is there work of my kind on that map* **against an explicit `Map`**,
because *"the provider contract forbids asking a native pawn-specific query about a map the worker is
not standing on."*

**So needs become providers beside the existing ones** — a rest provider, a food provider, a joy
provider — not a copy of Core's search pointed at a foreign map.

### 3.3 THE STRANDING GUARD, which is the difference between a feature and a pawn-eating hole

**§1.1 of the campaign absolutes makes the gate's window the only clock in the mod.** A pawn asleep
on the far side when it closes is stuck until the next opening.

**The guard belongs at the decision, not at the rescue.** A pawn may not *begin* a need-crossing
unless the remaining window covers all three legs: the walk there, the need, and the walk back. That
is computable from `openingTicksRemaining` plus a path estimate, and it is checked **once, before
committing**, because a guard that fires halfway is how a pawn ends up stranded mid-corridor.

**A permanently open natural gate has no window, and therefore no guard.** Invariant 12 makes that
connection kind permanent, so it pays for itself here: a branch that wants pawns living and sleeping
beyond a gate should be using a natural one, and the rule tells them so by behaving differently.

**What happens when a pawn is stranded anyway** — the window cut by a power loss, a kill switch, a
destroyed gate — is **not** a new system. `emergencyReturnTicksRemaining` and the recall path already
exist for exactly this, and a need-crosser is one more passenger on them.

---

## 4. Zoning: what it governs, and the half of it that cannot work

**Owner:** *"its upto the play to zone pawns where they want them,, that was the whole cross zone
support"*.

### 4.1 The good news, measured

**`Pawn_PlayerSettings.allowedAreas` is a `Dictionary<Map, Area>`** — RimWorld already keeps a
separate allowed area for every map a pawn has one on, and already scribes it. **Cross-map zoning is
a system to reach, not a system to build.** Send a pawn over, zone them there with the UI the player
already knows, and it persists across saves.

**Nothing in this mod needs to read or write another map's area**, which is fortunate, because there
is **no public per-map accessor**: `AreaRestrictionInPawnCurrentMap` writes only to the map the pawn
is standing on, and `allowedAreas` is private. Enforcement is Core's and stays Core's.

### 4.2 THE HALF THAT CANNOT WORK, AND SAYING IT NOW IS THE POINT

```csharp
public bool RespectsAllowedArea
{
    get
    {
        if (!SupportsAllowedAreas)        { return false; }
        if (pawn.GetLord() != null)       { return false; }
        if (pawn.Faction == Faction.OfPlayer) { return pawn.HostFaction == null; }
        return false;
    }
}
```

**Raiders have lords. Visitors, traders and allied squads have lords. Guests have a host faction.
Not one of them consults an allowed area at all.**

**So *"all one person choices in zoning"* governs the branch's own colonists exactly, and nothing
else.** The hostile and friendly halves need their own permission, which is the policy chokepoint and
the gate being open.

**Building zoning as the universal answer would have shipped two lies at once:** a raider that
ignores the player's zones, and a player who believed a setting was protecting them. That is worse
than the feature being absent.

---

## 5. A hostile on your map, crossing outbound

**Owner:** *"a enemy can break in and cross the gate to get valuables and members"*.

**This is the strongest idea in the direction, because it turns an open window into a security
decision instead of a convenience.** Until now a connection cost power and attention; now it is a
hole in the base that something can go *through*.

### 5.1 It mirrors `GateIncursion` exactly, in the other direction

`GateIncursion` is the template and it is a good one: tick on the gate, find a candidate at the far
doorstep, ask the policy, preflight the arrival cell, transfer with rollback, announce with a letter
and a sound. **The outbound version is the same six steps with `edge.First` and `edge.Second`
swapped.**

Reusing its shape matters for a reason beyond economy: its `FindAtDoorstep` takes candidates in a
**fixed radial cell order** so *"the same situation resolves the same way on every machine"*, and its
`Transfer` **puts the pawn back if the spawn fails**, because *"a vanished hostile is a save with a
hole in it."* Both properties are needed outbound too and neither is obvious.

### 5.2 THE MOTIVE IS THE BOUND, and it comes out of the owner's own sentence

**Incursion's five axes do not transfer.** Coordinate band and gate tier bound *inbound* crossing
because they describe how dangerous the far side has become — which says nothing about whether a
raider in your base should walk through a door.

**The owner's words name the bound instead: *"to get valuables and members"*.** So nothing crosses
outbound unless there is something over there worth crossing for — loot, or a person who could be
carried off. **An empty coordinate is not worth breaking into**, and that is self-limiting in exactly
the way a hand-tuned number is not: it scales with what the player actually chose to keep down there.

**And it makes the risk legible.** A player who stores nothing beyond a gate is never raided through
one. A player who builds a vault down there has built a target, and can see that they did.

### 5.3 Once per opening, or all of them?

**Not once per opening, and this is a deliberate departure from incursion.** Inbound is capped at one
because the player is being attacked at home and *"closing and reopening is what resets it"* is the
learnable rule. Outbound has a different fairness shape: a raid is a group, and one raider peeling off
through a gate while nineteen ignore it reads as a bug rather than a rule.

**The cap is the doorstep instead.** Only pawns that actually reach the threshold cross, one per
check, at the same one-second cadence — so a raid that fights its way to the gate goes through, and a
raid that is stopped in the killbox never gets near it. **The player's defence is the cap**, which is
the honest version of a limit.

---

## 6. A friendly on your map, crossing outbound

**Owner:** *"hold up now friendlys can too"*.

**The mechanism is the same as §5 and the consequence is not.** A visitor, trader or allied squad
member standing at an open gate may walk through.

### 6.1 The faction consequence, settled here rather than discovered in play

**A guest who dies in a coordinate is a death the player caused by leaving a hole open**, and Core
will book it as a death on the player's watch. That is the cost the fork named, and the owner took
it.

**So it is made visible rather than silent.** A friendly crossing raises a letter naming who went
through and which gate — the same treatment incursion gets — because the one thing that must not
happen is a faction penalty arriving with no story the player can connect it to.

**Register row 270 (Hospitality) binds the guest case:** *"preserve each mod's guest ownership and
payment rules"*. So a crossing never alters a guest's status, payment or departure timer; it changes
where they are standing and nothing else.

### 6.2 Why no friendly is *sent*

**Nothing lures anybody.** A friendly crosses because it wandered to a threshold that happens to be
open, exactly as a hostile does. **The gate is never a destination for anybody who is not ours** —
which is the surviving half of §1.1 doing real work: the chokepoint says yes or no to something that
already arrived, and never puts a gate on anybody's list.

---

## 7. THE LORD PROBLEM, which exposes a defect that already shipped

**A `Lord` is per map.** `Map.lordManager` owns it, and moving a pawn between maps leaves its lord
behind. A hostile that arrives with no lord has no duty, no assault behaviour and no reason to do
anything in particular.

**`GateIncursion.Transfer` does not create one.** It despawns, spawns, and announces. **So an
intruder that follows a crew home today arrives lordless**, and whether it still attacks is a
question only a launch answers.

**This brief does not get to leave that standing**, because §5 would reproduce it four times over.
The fix is already the established pattern **in this code base**: `InhabitantService` calls
`LordMaker.MakeNewLord(faction, HostileLordJob(…), map, pawns)`, and its hostile job is
`LordJob_AssaultColony(hostileFaction, canKidnap: false, canTimeoutOrFlee: false, sappers: false, useAvoidGridSmart: false, canSteal: false)`.

**For an outbound raider the two false arguments become true**, and they are the owner's own words
turned into parameters:

| Argument | Value | Why |
|---|---|---|
| `canSteal` | **true** | *"to get valuables"* |
| `canKidnap` | **true** | *"and members"* |
| `canTimeoutOrFlee` | **true** | a raider on a map it broke into should be able to give up and leave, unlike an inhabitant in its own space |

**A friendly gets `LordJob_DefendPoint` or its existing visitor job re-made on arrival**, never an
assault job, for the obvious reason.

**And incursion's own missing lord is fixed in the same change**, because fixing it only outbound
would leave the older, worse case alone to spite a tidy diff.

---

## 8. Counterplay, which already exists and must not be reinvented

**`NativeGateKillSwitch` is the answer and it is already built.** `KillSwitchThrown` drives
`EnterEmergency("RR_NativeGate_KillSwitchThrown")` in the gate tick, and the tick checks it **before**
the generic power test precisely so the recorded cause says *somebody threw this*.

**So *close the gate* is a real, learnable, already-implemented answer to every crossing in this
brief** — the same countermeasure incursion already teaches, now doing twice the work. Nothing new is
needed, and inventing a second defence would have been the worse outcome.

**The second counterplay is also already there and is a layout decision:** `GateWidth` and
`GateOpeningDepth` feed `FitFailureKey`, so a narrow gate physically refuses a large body. *"a narrow
gate is a real defensive choice rather than the starter option"* — already written, now with a second
reason to be true.

---

## 9. What replaces incursion's five bounds, axis by axis

**Each of the five was reasoned from an assumption that §1 makes false, so each is re-derived rather
than copied or dropped.**

| Incursion's axis | Still true inbound? | Outbound |
|---|---|---|
| **Only while a connection is open** | yes | **yes, unchanged.** A closed gate is a wall in both directions, and it is the whole counterplay |
| **Only at the `Hostile` band** | yes | **no, and replaced by motive.** Coordinate danger says nothing about a raider in your base. §5.2 |
| **Only once the branch advanced the machine** | yes | **no.** A first unresearched gate is still a hole; the hole is the point |
| **Only if it fits** | yes | **yes, unchanged.** `FitFailureKey` on `GateWidth` and `GateOpeningDepth` |
| **Only one per opening** | yes | **no, and replaced by the doorstep.** §5.3 — the player's defence is the cap |

**Inbound keeps all five.** Nothing in this brief loosens incursion, and the asymmetry is the point:
being attacked at home is more severe than losing a remote stockpile, so it stays the narrower of the
two.

---

## 10. What the register said, checked before designing

`python tools/register-query.py use RR-THREAT`, `card 270`.

| Row | What applied |
|---|---|
| **[4] Core** *(Required)* | Lords, think trees, areas and assault jobs are all base game, so every mechanism here is Core-only by construction |
| **[270] Hospitality** *(Optional)* | *"preserve each mod's guest ownership and payment rules"* — **binds §6.1**: a crossing moves a guest and changes nothing about their status, payment or departure |
| **[274] Detention and subject casework** | *"Use existing prisoner, capture, restraint, and medical systems"* — **binds §7**: a kidnapped colonist is Core's kidnap, not a bespoke one |
| **[60] Capture Them** *(Optional)* | `WorkGiver_CapturePrisoners`, already recorded as not generically buildable as a deployment. **Nothing here needs it** — kidnapping is the lord's, not a work giver's |

---

## 11. The absolutes this is held to

- **§1.1 — the gate's connection is the only duration in the mod.** The stranding guard exists so
  this stays a rule about the gate rather than a rule about pawns dying in their sleep.
- **The solo guarantee is untouched.** Nothing here changes a coordinate's encounter cap, its quiet
  room fraction, or the quiet first visit. An outbound crossing is a thing the *player's map*
  produced, not the coordinate.
- **One chokepoint.** `PortalTraversalPolicy` remains the only place that may say yes, which is the
  half of invariant #1 that is being kept rather than discarded.
- **Core API only, no Harmony.** Needs by a map component rather than a think-tree insert (see §3.1), lords by `LordMaker`, zoning by Core's
  own per-map dictionary, transfer by `DeSpawn`/`GenSpawn` with rollback.
- **No new art, and no new buildable.** Every object involved already exists.

---

## 12. Build order, which is a real dependency chain

1. **The policy rewrite** (§1.2) and the eight document assertions, together, because every later
   step asks the policy and no later step may ship beside a document that denies it.
2. **The lord fix on existing incursion** (§7). Smallest, closes a defect that already shipped, and
   proves the arrival path before anything new uses it.
3. **Outbound crossing for hostiles** (§5), reusing `GateIncursion`'s six steps with the ends
   swapped.
4. **Outbound crossing for friendlies** (§6), which is step 3 with a different lord and a different
   letter.
5. **The need providers** (§3.2) answering against an explicit map.
6. **The stranding guard** (§3.3) — before the think tree can use the providers, never after.
7. **The think tree insert** (§3.1), last of the code, because it is the thing that makes the rest
   fire.
8. **An instrument.** No existing checker asserts anything about who may cross, which is how a
   `const bool` and its eight assertions could have drifted from the code. One checker owns the new
   policy shape, the five-versus-four bound table, and the rule that every arrival gets a lord.
9. **The wiki**, which currently says *"No guests arrive"* and will be wrong the moment step 4 lands.
