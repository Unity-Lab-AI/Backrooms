# The second time you do a thing should be cheaper — 0.11.6-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including three unlocks it deleted
before writing them. Never rewritten.

---

## What this is

**Step 6 of the build order in `docs/CAMPAIGN_CHART.md`, tier 2**: *"Repeatable operations:
revisit known coordinates and reduce preventable failures."*

Seven projects, one per branch, each requiring its own tier-1 sibling **and a completed distortion
log**. Tier 1 asked only for route logs, because it is about having been through once. This band
asks for the space to have **misbehaved while somebody was recording it** — you cannot study a
preventable failure that has not happened yet.

---

## The register, checked first

`python tools/register-query.py family research` — the **Research and staff development** family
holds six rows: *Do Your F\*\*\*\*\*\* Research* (configuration only), *Mad Skills*, *Misc.
Training*, *Oops All Gene Banks*, *ResearchTree (Eheieh Version)* and *Research Whatever*.

**None of them applies, and the reason is structural rather than lucky.** Every one of those mods
operates on `ResearchProjectDef` and the vanilla research tab. This mod's projects are
`RimroomsProjectDef`, a def of our own, completed at the company laboratory and displayed in the
Operations tab. A research-tree overhaul cannot conflict with a tree it cannot see, and *Research
Whatever* cannot unlock a project it does not know exists.

That separation was an owner decision at a fork — *"Our project defs, as the gate branch is"* —
and this is the checkpoint where it pays for itself.

---

## The seven

| Branch | Project | Capability | What it moves | Read site |
|---|---|---|---|---|
| Facilities and power | **Standby Discipline** | `RR_Cap_StandbyDiscipline` | idle draw ×0.5 | `CompRimroomsGate.IdlePowerDrawWatts` |
| Fieldcraft and medicine | **Relief Watch** | `RR_Cap_ReliefWatch` | spin-up decay ×0.25 | `GateSpinUp` |
| Measurement and evidence | **Reference Standards** | `RR_Cap_ReferenceStandards` | calibration work ×0.6 | `CompRimroomsGate.CalibrationWorkRequired` |
| Spatial mapping and topology | **Known Address** | `RR_Cap_KnownAddress` | familiarity 0.85 → 0.595 | `GateSpinUp.SpinUpFamiliarityFactor` |
| Entities and containment | **Containment Protocol** | `RR_Cap_ContainmentProtocol` | incursion needs tier 2, not 1 | `PortalTraversalPolicy` |
| Communications and logistics | **Forward Dispatch** | `RR_Cap_ForwardDispatch` | dispatch delay ×0.5 | `RimroomsProcurementComponent` |
| Commerce and organisation | **Specialist Recruitment** | `RR_Cap_SpecialistRecruitment` | hiring cooldown ×0.5 | `RimroomsPersonnelComponent` |

### Nothing supersedes anything, and that is the improvement

Tier 1 had **three** capabilities that replaced their tier-0 sibling, because they shared a
number and stacking them would have made *"twice as long"* untrue on the card.

**Every tier-2 project moves a knob no other project touches.** A player holding Efficient
Aperture and Standby Discipline gets both, in full, and neither card has to explain the other:
one is what an open connection costs, the other is the bill for the days the gate is doing
nothing but staying ready.

This was not a goal. It fell out of picking knobs by *"which preventable failure does this
branch actually suffer"* rather than by *"which number does this branch already own"*.

---

## Three unlocks deleted before they were written

`docs/NOW.md` handed this checkpoint seven knobs with the note **"seven live knobs are already
identified and none of them needs inventing"**. Checking them against their real read sites
killed three.

| Knob | Why it was dropped |
|---|---|
| `stablePowerTicksRequired` | It is **60 ticks. One second.** A project halving the wait between power steadying and a gate accepting it would be imperceptible |
| `MaximumOpenOrders` | A **private sanity cap of 100** simultaneous open orders. No player has ever been near it |
| catalogue `maxOrderQuantity` | Already **500 to 1,000,000** per row, and clamped again by `MaximumActiveQuantity`. Raising it changes nothing anybody sees |

**All three have real read sites.** That is exactly what makes them dangerous, and it is the
reason this is written down:

> `proof-research-branches.py` asserts that every granted capability **is read by at least one
> source file**. All three of these would have passed it. The capability would have been read,
> by real code, modifying a real field — and the player would have paid insight for nothing.

**A live read site is not the same thing as a live effect.** The proof cannot close that gap,
because from the outside a read that matters and a read that does not are the same line of code.
It is the same failure family as the beacon condition that could never fire (0.10.7) and the
tier ladder that could never be climbed (0.10.9), one level further in: not *"nothing reads
this"* but *"something reads this and the reading is worthless"*.

The only defence is the one used here — **open the file, find the value, and ask what a player
would observe.** That question is now invariant 136.

---

## Two places that had to agree, and one that would have gone quiet

### The idle draw is read twice

`idlePowerDrawWatts` was wired one checkpoint ago into **two** sites: `CurrentPowerDrawWatts`,
which is what the gate reports drawing, and `SpendIdleDrawTick`, which is what it actually takes
out of the reserve.

Applying Standby Discipline to one and not the other would make **the readout lie about the
drain**, and the two would drift apart silently because nothing compares them. So the capability
lives in a single new `IdlePowerDrawWatts` property and both sites go through it.

**A number displayed and a number spent must come from one place.** There is no checker for
this, and there could not easily be one.

### Forward Dispatch would have switched Relays off

`LeadTimeTicksFor` ends with a clamp that keeps a shipment from arriving before it leaves:

```csharp
return Math.Max(lead, catalog.dispatchDelayTicks + 1);
```

Relays (tier 1) shortens the lead time until it hits that floor. If Forward Dispatch halved the
dispatch delay everywhere **except** this clamp, a branch holding both would keep being held at
the **old** floor — and Relays would quietly stop biting for exactly the players who had invested
in both halves of the branch.

The clamp now measures against the effective delay. **A tier-2 project that turned off its own
tier-1 prerequisite would have been the worst bug in the band**, and nothing would have reported
it: the shipment still arrives, just no sooner than it used to.

---

## Containment Protocol is a choice between branches, not a discount

Incursion is invariant 53, bounded on five axes. One of them is `PortalWindowTier >= 1`.

Containment Protocol raises that floor to 2 for a branch that holds it. **The bound only ever
tightens** — there is no capability anywhere that lowers it — so the exception stays as narrow as
it was written.

What makes it worth a project rather than a flat buff is that the gate ladder and the Entities
branch are **independent**. Push the aperture hard and neglect containment, and the door you
opened wider is a door something can come back through. Invest in containment and the first rung
of the ladder is free of it entirely. Neither is wrong, and the player chooses.

---

## The proof was fault-planted in both directions

Not trusted because it printed `PROOF HELD`:

| Fault planted | Result |
|---|---|
| `RR_Cap_KnownAddress` → `RR_Cap_KnownAddressTypo` in the def | **2 failures** — the typo is read by nothing, and the real capability is granted by nothing |
| `"RR_Cap_ForwardDispatch"` → `"...Ghost"` in the source | **2 failures**, the mirror image |

Both restored, proof holding. **A proof that has only ever passed has not been tested**
(invariant 109).

---

## Receipts

| | |
|---|---|
| Version | 0.11.6-dev |
| Build | 162 C# files, 85 package files, **0 warnings, 0 errors** |
| New defs | 7 `RimroomsProjectDef` — **25 total** |
| Capabilities | **21**, every one granted once and read by real code |
| Unlocks deleted before being written | **3**, all of which would have passed the proof |
| New defs of any other kind, art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **eight**, all passing |
| Proofs | **four**, all holding; one fault-planted in both directions |
| Game launched | **no** |

Next, in the chart's order: the clean-up team — and by owner decision at the fork this session,
**both** a guaranteed floor in our own component and an `IncidentDef` surface so the player's
chosen storyteller paces the lighter world-facing events.
