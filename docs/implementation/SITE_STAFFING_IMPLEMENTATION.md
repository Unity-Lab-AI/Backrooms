# Remote sites need people — 0.12.8-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including a third proof claim of mine
that could not fail. Never rewritten.

---

## What this is

**Arc 5's third piece**, and a guarantee the owner named mid-checkpoint that turned out to be
already true.

> *"Remote sites need people, supplies, signals, protection, and an exit plan."*

Sites went on the books at 0.12.6. Supplies reached them at 0.12.7. **People are this one.**

---

## The register, checked first

`Animals and field support` (14 rows) and `Staff jobs, policies, and social systems` (8), the two
families that touch who is where and what they are doing. Every row is *Optional* or *Settled*,
and none changes what it means for a place to be attended. Nothing applied.

---

## Staffing gates arrival, not ordering

The design decision that mattered, and the alternatives were both wrong:

| Option | Why not |
|---|---|
| Gate the **order** on staffing | Punishes planning. Anybody would order supplies *while* the crew is still walking there — that is the sane thing to do and the mod should not forbid it |
| Gate **nothing** on staffing | *"Remote sites need people"* becomes a sentence in a document |

So there are **two predicates**, and the split is the whole piece:

- **`CanReceiveDeliveryAt`** — is the address acceptable? On the books, and reachable. **Order
  ahead freely.**
- **`CanUnloadAt`** — can it actually be unloaded *now*? The address, **plus somebody there.**

A shipment to an empty site **waits**. `SetAwaiting` holds the cargo, keeps the payment recorded
and retries — nothing is lost and the fix is obvious: send somebody. A supplier does not unload
into an empty field with nobody to sign for it.

**The headquarters is never held to this.** A branch with nobody alive at home has a far bigger
problem, and the clean-up team already owns it.

### What counts as staffed

Employed, alive, **present on that map**, and **not downed**. Somebody unconscious on the floor
cannot take delivery of anything, and pretending otherwise would make the rule a formality. A
prisoner or a slave is never staff.

Checked live, with no assignment to maintain — a site is staffed when people are there and
unstaffed the moment they leave. That is the honest reading of *"needs people"*, and it means
there is no record to go stale and nothing for the player to remember to update.

The pane shows **three** states rather than two, because *"reachable but nobody there"* is the one
a player needs to see — it is the state that quietly holds their shipments.

---

## The guarantee that was already kept

Mid-checkpoint:

> *"and remmebr turning off a company gate with pawns inside doesnt lose control of those pawns
> they have to survive till a reconnection is made so they can escape"*

**This was already true, in every part**, and it was verified rather than assumed:

| Part | Where it lives |
|---|---|
| the map a stranded crew stands on is never removed | `ShouldRemoveMapNow` returns `false` **unconditionally** |
| an expiring window touches no pawn | the expiry path sets a failure key and records activity, and that is all |
| player control is never surrendered | no gate source calls `PassToWorld` — the one act that keeps a pawn alive while taking it away |
| a reconnection exists and the player arranges it | `RecoverPortalOpening`, costing energy, needing a calibrated gate and an operator on station |
| nothing about it is timed | the recovery path has no expiry, deadline or countdown of any kind |
| the player is told | `Alert_RimroomsRecoveryOverdue`, keyed on the gate's own `IsAwaitingRecovery` |

**So nothing was built for it, and a proof was written instead.** That is the right response to a
guarantee that already holds, because the specific way this would break is an obvious-looking
optimisation:

> *"a coordinate with nobody on it and no live connection does not need to stay loaded"*

That one line would delete a map with a crew standing on it, take colonists away from somebody
**permanently**, and produce no compiler error, no checker failure, and no symptom until a player
lost five people. `proof-stranded-crew.py` fails the instant `ShouldRemoveMapNow` grows a
condition — any condition — because any condition there is a condition under which somebody's
colonists vanish.

Planting exactly that optimisation fails it, as does despawning the crew on expiry, as does giving
recovery a deadline.

---

## A third claim of mine that could not fail

The ordering claim was written with a conditional fallback:

```python
"CanUnloadAt" not in procurement.split("private int TryDeliver")[0]
if "private int TryDeliver" in procurement else "CanUnloadAt" in procurement
```

**`private int TryDeliver` does not exist in that file.** So the whole expression collapsed to
`"CanUnloadAt" in procurement` — trivially true, always, no matter what the code did.

> **A claim with a conditional fallback is a claim that can be trivially true.**

Replaced with a property that cannot degenerate: `CanUnloadAt` has **exactly one** call site and
`CanReceiveDeliveryAt` has **exactly three** (quote, accept, redirect). If anybody ever gates the
order on staffing, the first count moves.

And the second version of that claim was **also wrong** — I wrote `== 2` and the real number is
three. It failed immediately and honestly, which is the difference between a wrong claim and a
claim that cannot fail: **the wrong one tells you.**

Third fail-open in one day, all three mine, all three found by fault-planting rather than by
reading. That is what fault-planting is for, and it is why invariant 109 exists.

---

## Fault-planted seven ways across two proofs

| Fault planted | Caught by |
|---|---|
| staffing gates the order too | *"staffing is consulted at exactly one place, the arrival"* |
| arrival stops checking staffing | *"arrival waits when nobody is there"* |
| downed pawns count as staffing | *"staffing does not count the downed"* |
| an unstaffed site becomes a recovery case rather than a wait | *"arrival waits when nobody is there"* |
| **the empty-coordinate "optimisation"** | *"a coordinate map is NEVER removed"* **and** *"the decision is unconditional"* |
| window expiry despawns the crew | *"window expiry does not call DeSpawn"* |
| recovery gains a countdown | *"recovery has no Deadline"* |

All restored, both proofs holding.

---

## Receipts

| | |
|---|---|
| Version | 0.12.8-dev |
| Build | 172 C# files, 86 package files, **0 warnings, 0 errors** |
| Guarantees verified rather than built | **1**, and proved instead |
| Proof claims found unable to fail | **1**, by fault-planting |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| New keyed strings | **2** |
| Checkers | **eight**, all passing |
| Proofs | **eleven** — a new one, fault-planted three ways |
| Game launched | **no**, and nothing here has been played |

**Still owed in arc 5:** the exit plan — a gate anchored at a registered site, which the ownership
predicate now permits and nothing yet does. Then the chart's relay stations, caches, field
shelters, guarded leases, resupply and evacuation missions.
