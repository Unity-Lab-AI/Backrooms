# Getting somebody out, and earning what comes against you (0.8.3-dev)

**Baseline:** `d989925` (0.8.2-dev, 145 C# files, 88 package files).

**This checkpoint — 0.8.3-dev:** **147 C# source files** (two new), **89 approved package files** (one new keyed file). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `EB18029C58456A3A99D85440D3808BE9A8A410380CC3895AEE7CA1A95A08F51C`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

Two loose ends closed, both named honestly in the previous checkpoint rather than buried.

## 1. Recruiting a survivor — *"lost pawns"*

0.8.2-dev placed survivors: alive, neutral, carryable out. **Without a way to accept them, a survivor was scenery you could pick up rather than a person you could save.**

**Offering passage, not recruiting.** No negotiation, no recruitment chance, no prisoner step. Somebody lost in the Backrooms who meets a team with a way out **wants to leave**, and making a player roll for that would be a worse story and a worse game.

### The part that matters structurally

The traversal rule is absolute: **an inhabitant may never decide anything about a gate.** A survivor who has not joined *is* an inhabitant — so they cannot cross, and the only way out for them is to be carried, exactly like anything else found down there.

Joining makes them a colonist, and `PortalTraversalPolicy` then permits them to cross on their own **through the same single chokepoint everything else uses**. Nothing here special-cases a gate. That is deliberate: the rule is enforced in one place, and this is one more caller obeying it rather than an exception to it.

The letter says so out loud, because it is the most interesting thing about the interaction: *"They can cross a gate on their own now, which they could not do a moment ago."*

### Dormant unless marked

The comp sits on the human race def, so **every pawn in the game carries it** — and it does nothing unless a coordinate marked that particular person as a survivor it produced. Same dormant-until-designated pattern as the gate, emergence and credit-beacon comps on Core buildings: installing this mod must never change anybody who was not asking for it.

One of your own people must be **present** to make the offer. A survivor cannot be recruited from the other side of a gate by a player looking at a map.

## 2. The cap as a recorded progression step

This was the **last unmet clause of the original 2026-09-28 ladder direction**:

> *"caps on simultaneous encounters, inhabitants and events per opening and per coordinate, where **raising a cap is itself a recorded progression step**"*

0.8.0-dev built the cap and the absolute ceiling. What was missing is that the cap should not simply *be* the ceiling from day one. It has to be **earned, recorded, and visible in the branch's own history** — so a player can look back and see the moment the rules changed, rather than discovering that the world quietly got harder.

### The step is reaching a depth nobody has reached before

Deliberately **not research, and not wealth**.

- Wealth already feeds the ladder's ceiling, so using it again here would **double-count one input**.
- Research is not an act of exploration.
- **Pushing deeper than the branch has ever been is the one thing that is unambiguously the player choosing to escalate.**

So the Backrooms never brings more against somebody than they went looking for. **A branch that stays shallow stays at the opening cap forever**, however rich or advanced it becomes. That is the point, not a side effect.

| | |
|---|---|
| Opening cap | **1** — a first dangerous space is dangerous, not overwhelming |
| Each new deepest coordinate | +1, recorded as an event |
| Absolute ceiling | **3**, unchanged and unreachable past |

Idempotent: reaching the same depth again changes nothing, so a cap cannot be walked up by re-entering one space. Depth 1 never raises anything — every branch starts there, and reaching it is not an achievement.

**A step that hits the ceiling is still recorded**, because the history should show the branch went deeper even when nothing changed.

## Not done, and still named

- **Anomalous events**, as distinct from anomalous rooms and inhabitants.
- **Echoed room shapes.** Outstanding since 0.8.1-dev, and it is the larger of the two: room dimensions feed the saved layout fingerprint, so changing them touches generation's validation path and deserves its own checkpoint rather than being squeezed into this one.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass; 1,182 keyed references all resolving.
- Compliance: one `PatchOperationAdd` adding a dormant comp to a Core def (permitted; `Replace`/`Remove` remain forbidden). **No new PawnKindDef, no new gameplay ThingDef, no asset, no new work type.**

## For the post-completion test phase

Confirming a survivor cannot cross a gate before accepting and can after; confirming the offer is unavailable with nobody present; confirming an ordinary colonist and an ordinary visitor never show the offer; confirming a joined survivor is a full colonist and not a guest; confirming the cap starts at one; confirming it rises only on a new deepest depth and is recorded in the branch history; confirming re-entering the same depth does not raise it; and confirming it never exceeds three.
