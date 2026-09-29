# What you have learned is what you can build — 0.10.9-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## The direction

> *"ie u need certain logs complete to operate the higher teri techs and shit and gate features
> and upgrades all story line in quests layed out and coporation requasts and missions.. and
> remember the mega mother corp is greedy and will basic do anything and put up with anything to
> make sure you succssed to the point of sending clean up teams to your base with all access
> passses to wipe the facitly of all hostals and requisition a new basic team supplies drops like
> a fresh start of sorts so that facilities never die, this is liken the store and solo/group
> scenerios once they reach contact with the corporation"*

Five items, recorded one task each. **This checkpoint builds the first.** The quest layout, the
corporation's character and the never-die rescue are queued behind it, in that order, because a
quest that unlocks a tier needs tiers to unlock and a rescue that restores a facility needs the
facility's own state to be worth restoring.

---

## The register, checked first

Families read: `contracts` (12 rows), `faction standing` (11), `subject casework` (19),
`evidence` (7).

**Nothing to integrate with.** Three rows are adjacent and none needs anything:

- **148 No Quests Without Comms** gates quest arrival behind a comms console, which a gate
  already requires one of.
- **132 More Faction Interaction** adds its own faction quests without touching a mod's own
  quest defs.
- **100 Go Explore!** adds exploration quests, likewise independent.

---

## The defect the direction landed on

`GateProps.portalWindowTierProjects` held **one** name. `GateProps.portalIndefiniteTier` was
**4**.

`PortalWindowTier` counts completed projects from that list, one tier per entry, so the tier
could never exceed **1**. Which means:

- **A standing connection — the top of the gate's own capability ladder — was unreachable**, no
  matter how a branch played, for as long as the mod has existed.
- Incursion, which needs `PortalWindowTier >= 1`, sat at the very top of everything that existed
  rather than partway up.
- The per-tier window multiplier applied at most once.

**No checker could see it.** Every individual value was valid: a list with one valid name, an
integer of 4, a multiplier that was finite and positive. The failure was only visible in the
relationship between two settings in different places, which is the same shape as the retired
beacon condition found in 0.10.7-dev.

It is now covered by an offline proof, below.

---

## Logs are the qualification; insight is the price

Before this, a project cost **spendable insight** and nothing else. Insight is fungible: four
analysed records of the same kind bought exactly what four different ones bought, so nothing in
the game ever asked what a branch had actually **learned**.

Every evidence record has carried three flags all along — `routeRecorded`, `distortionRecorded`,
`entityRecorded` — and **nothing had ever read them as a prerequisite**.

| New field on `RimroomsProjectDef` | Means |
|---|---|
| `requiredRouteLogs` | analysed records carrying a route log |
| `requiredDistortionLogs` | analysed records carrying a distortion log — the space misbehaving |
| `requiredEntityLogs` | analysed records carrying an entity log — something was down there |
| `prerequisiteProjects` | rungs that must be finished first |

**Only `Analyzed` records count.** A book carried home and never put through a bench is recovered
evidence, not a completed log, and the owner's word was *"complete"*.

**A completed log stays completed.** A record that later goes `Missing` keeps its analysed tick,
so a log survives the book burning — the same once-only rule the insight award already followed,
and the same reason `PortalWindowTier` counts completed projects rather than currency. A tier
already earned can never be lost by spending on the next one.

**Checked before insight is spent.** `ProjectQualificationFailureKey` runs ahead of the cost
check, so a branch short of logs is told which kind it is short of instead of being charged and
then refused. Splitting the qualification from the price is the same separation every other check
in this mod uses: merging them hides which one failed.

---

## The four rungs

| Rung | Insight | Work | Route | Distortion | Entity |
|---|---|---|---|---|---|
| **Gate Telemetry** | 1 | 6,000 | 1 | 0 | 0 |
| **Field Stability** | 2 | 9,000 | 2 | 1 | 0 |
| **Sustained Aperture** | 3 | 13,000 | 3 | 2 | 1 |
| **Standing Connection** | 4 | 18,000 | 4 | 3 | 2 |

The order the requirements rise in is the order a branch naturally learns things. Route logs come
from surveying at all. Distortion logs need the space to have misbehaved **while somebody was
recording** — a branch that has only had quiet runs genuinely has nothing to read. Entity logs
need something to have been down there and been seen.

**Sustained Aperture is the rung at which what lives down there can follow a crew out**, and it
requires an entity log. Nothing can come through a gate before the branch has written down that
something is there, which is the readable-warning rule the threat design already owes the player,
arriving one tier early by construction rather than by a separate check.

---

## Custody is a place now, not a receipt

`HasSecuredEvidenceCase` asked whether the expedition that produced a record still had a
`RR_SealedEvidenceCase` **somewhere at headquarters**. That is custody-by-receipt: the case was a
custom item whose only job was to exist, and **it did not matter where the book itself had been
put**.

Owner direction: *"things needed to be on shelves/records that computers and workbenches need to
connect to"*. So `HasArchivedCustody` asks where the book **is**: stored on a shelf linked to a
gate as a `RR_Link_Archive`, the role built in 0.10.8-dev.

Consequences that are all improvements:

- Custody is **visible**. A player can see the shelf, reorganise it, and lose it.
- A facility with several gates has several archives, and **any** of them is custody. The
  corporation cares that the paperwork is filed, not which door it came through.
- The **retired case is gone** — def, recipe, texture, scenario grant, kit requirement and its
  refusal string. Starts grant two shelves instead.

---

## The proof

`.local/register/proof-tier-ladder.py`, asserting rather than printing. It reads the ladder out
of the **source** and the rungs out of the **defs**, so it is checking the relationship that
broke rather than either side of it. Twenty claims, all held:

- **the ladder is at least as long as the indefinite tier** — the assertion that catches the original defect;
- every rung is a project that exists, and none is listed twice;
- **rung N requires rung N−1**, or a branch with enough insight completes the top rung first and skips the ladder;
- every requirement is **non-decreasing** up the ladder — route, distortion, entity, insight and work;
- no prerequisite names a project that does not exist;
- **no cycles**, checked transitively, because a cycle is unreachable content that looks completely normal in every individual def;
- the first rung needs **no prerequisite and no distortion or entity log**, so a new branch can begin the ladder at all.

### Sanity-tested in both directions

| Planted | Result |
|---|---|
| The top rung removed from the ladder — **a reconstruction of the original defect** | **FAIL**: *"3 rungs >= 4 — a standing connection is UNREACHABLE"* |
| The top rung's prerequisite removed | **FAIL**: *"the ladder can be climbed out of order"* |
| Both reverted | **PROOF HELD** |

---

## Receipts

| | |
|---|---|
| Version | 0.10.9-dev |
| Build | 160 C# files, 83 package files, **0 warnings, 0 errors** |
| New defs | 3 more `RimroomsProjectDef` — a mechanics def, **no gameplay ThingDef** |
| Retired | `RR_SealedEvidenceCase`, `RR_MakeEvidenceCase`, one texture, one keyed string — archived to `historical-content/0.10.9-dev/` |
| New art, audio or texture | **none**, and one texture left |
| Harmony | **none** |
| Checkers | **seven**, all passing |
| Game launched | **no** |

Queued next, in the owner's own order: **the corporation's requests and missions as quests**, then
**the clean-up team that means a facility never dies** — scoped to the Store and Solo/Group starts
and only after contact with the corporation, because before contact there is no rescue and that is
what makes those openings frightening.
