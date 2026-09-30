# Two of three starts had no campaign — 0.12.30-dev, 2026-09-29

**Dated record.** Never rewritten. The largest reachability hole found in this project so far, and
it was found by following a row about something else.

---

## What was actually wrong

I opened the row *"the solo/group start has no tutorial line"* and went looking for where a solo
tutorial line would hook in. It does not hook in anywhere, and the reason is much bigger than the
row:

```csharp
/// <summary>
/// Establish contact. One-way: there is deliberately no method to take it back.
/// </summary>
public CompanyActionResult EstablishCorporationContact()
```

**It had no caller. Anywhere.** Defined once, never invoked — with its event already recorded, its
keyed string already written, and nothing in the game able to reach it.

And `corporationContact` gates:

| Gate | File |
|---|---|
| the entire tutorial line | `RequestLine.cs:305` |
| generated requests | `RequestGeneration.cs:186` |
| the `Purchase` success route | `RequestGeneration.cs:90` |
| **the clean-up team that comes for a stranded crew** | `FacilityRelief.cs:122` |

Both the **Store** and **Solo/Group** starts declare `beginsInCorporationContact false`.

**So two of the three shipped starts had no campaign at all, permanently.** No tutorial, no
requests, no catalogue, no rescue — and no way to ever get any. Two thirds of the openings a player
can choose were a sandbox with a locked door.

The documents both said so, and neither was wrong — they were describing something nobody had built:

> `docs/CAMPAIGN_CHART.md`: **Store** — *"Its own layout, and **reaching contact is the
> achievement**"*. **Solo/Group** — *"Same, from a different point of view"*.
>
> `RR_Starts.xml`, in its own comment: *"Reaching contact is the achievement here, not the starting
> condition."*

**The achievement had no mechanism.** And `SoloGroupHints` was already telling the solo player to
build a comms console — a hint pointing at a thing with nothing to do with it.

---

## The owner named the mechanism mid-build

> *"once they "contact the cvompany in comms" they can start async quest line"*

Two decisions in one sentence, and both simplified the design:

1. **It happens on a comms console.** Not an Operations pane action, not a quest, not a new
   building — the thing a branch would obviously use to call somebody.
2. **What it starts is the existing Async line.** Not a parallel solo line.

That second one deleted most of the work I was about to do. `OfferNextTutorialRequest` already
refuses until `corporationContact`, so **nothing had to be authored for the line at all** — it
begins on its own the moment the call succeeds. A separate solo line would have been two voices
teaching the same systems, and I had already found the structural obstacle to one: `TutorialLine()`
returns *every* def with `tutorial = true`, with no notion of which start it belongs to, so a solo
line would have needed a discriminator threaded through the def, the selector and the offer routine.

**None of that was needed.** The owner's answer was smaller and better.

---

## It is earned, because the chart calls it the achievement

A free button on a day-one console would have made the chart's own word wrong. So the call asks for
the whole first loop, done once:

| Requirement | Refusal |
|---|---|
| the branch is operating | `RR_Contact_Inactive` |
| not already on the books | `RR_Contact_AlreadyInContact` |
| a comms console, spawned, player-owned | `RR_Contact_NoConsole` |
| on a map this branch holds | `RR_Contact_NotOurs` |
| **powered** | `RR_Contact_Unpowered` |
| somebody employed, present, awake and **able to speak** | `RR_Contact_NoOperator` |
| a coordinate the branch has been into | `RR_Contact_NoCoordinate` |
| **an analysed record** | `RR_Contact_NoFinding` |

That last one is the substance. An analysed record means a crew found the door, went through, got a
book home, and somebody sat down and read it. **You are not calling to ask for help — you are
calling to tell them you have something**, which is why the corporation takes the call.

`RR_Contact_NoFinding` says so in as many words: *"You have nothing they want. Bring a record book
back from a coordinate and have somebody analyse it, then call."*

### The reason shows on a disabled button, not a missing one

Invariant 28 wants every rule learnable. A vanished gizmo teaches nothing, so the call is always
visible to a branch out of contact and carries its blocker on the tooltip.

And the action **re-checks every condition** rather than trusting the button that offered it — a
gizmo can be clicked on the same tick the generator goes off.

---

## No new comp, no new patch

Core's `CommsConsole` already carries `CompProperties_RimroomsGateConsole`, and that component
already yields two gizmo providers from `Procurement`. So this is a third provider on an
established seam.

One wrinkle worth naming: **that component is also on `TableMachining`.** Nobody telephones a
corporation from a machining table, so the provider refuses anything that is not a
`Building_CommsConsole` — and the proof fault-plants exactly that.

---

## Receipts

| | |
|---|---|
| Version | 0.12.30-dev |
| Build | **178 C# files, 87 package files**, **0 warnings, 0 errors** |
| Assembly | `90E0885C229B6972E5209E3C30B4487F9BB3431AB5B5490A75B6B36188AA1923`, identical across two clean rebuilds |
| Starts that could reach the campaign before | **1 of 3** |
| Starts that can now | **3 of 3** |
| New content | **none.** A gizmo on a Core console, eleven keyed strings |
| New request defs authored for the solo line | **zero**, and that is the owner's answer working |
| Checkers | **ten**, all passing |
| Proofs | **twenty-seven**, all exiting zero |
| Planted faults caught | **9 of 9** |
| Game launched | **no.** Nobody has placed this call |
