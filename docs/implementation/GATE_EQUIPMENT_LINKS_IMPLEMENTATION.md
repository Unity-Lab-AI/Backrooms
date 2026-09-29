# A gate's facility is the equipment linked into it — 0.10.8-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## The direction

> *"get to it and remmebr these facilities when built will be big so some shelves and multiples
> need to be like connect via a option like beds connect to other furnature in making the gate
> work properly with everything needed and like things needed to be on shelves/records that
> computers and workbenches need to connect to ie we can use things like the research computer
> multianalysers and other such things and tool cabnets for enginners research benches and the
> like and these facilitys can be massive so thes connections need to be like on the same power
> systems and connected to gether via connections like furnature to beds and reach fare and
> through walls and manually connected for use of multi gate facilities"*

Nine items, recorded one task each in `TODO.md`.

---

## The register, checked first

Families read: `facilities` (23 rows), `furniture` (12), `storage` (15), `power` (13).

**Nothing to integrate with, and one thing to avoid.** Rows **254 Wall Heater**, **256 Wall
Televisions** and **257 Wall Vitals Monitor** are wall-mounted **facility-linking** furniture,
and row **184 Realistic Rooms Rewritten** changes room sizing. Row 257's review records a
publisher comment about monitors stacking, which nobody has reproduced.

None of them needs integration. All of them are a reason **not to alter Core's shared facility
geometry**, which is the decision this checkpoint turns on.

---

## Why this is ours and not Core's facility comps

RimWorld already has precisely the relationship the owner described. A bed links to an end
table; a research bench links to a multi-analyzer; a workbench links to a tool cabinet. The
obvious move is to reuse it.

It does not work, and the reason is a single fact read from decompiled
`RimWorld.CompProperties_Facility`:

```csharp
public float maxDistance = 8f;
public bool requiresLOS = true;
```

**All of the geometry lives on the facility side.** The consumer side,
`CompProperties_AffectedByFacilities`, carries exactly one field — `linkableFacilities` — and no
control over distance or line of sight whatsoever.

So making our links *"reach fare and through walls"* through Core's comps would mean editing
`maxDistance` and `requiresLOS` on Core's `MultiAnalyzer` and `ToolCabinet`, which would change
**vanilla research-bench linking for every player and every other mod in the profile** —
including the three wall-mounted facility mods above.

The links are therefore ours, on our own saved record, and **Core's facility comps are untouched**.

### The two relationships coexist

A `MultiAnalyzer` linked to a gate **does not** consume its Core facility slot and **does not**
stop boosting a research bench. That is the correct outcome, and it is asserted in the proof so
nobody later "fixes" it.

---

## Every rule already existed for the gate's original three providers

The gate has bound a console, a battery and an assembly bench since the native-provider work.
This checkpoint **generalises that shape** rather than inventing one:

| Direction | How it is met | Where it came from |
|---|---|---|
| *"manually connected"* | Explicit designation only; proximity never links anything | already true of the three providers |
| *"reach fare and through walls"* | **No distance check, no line-of-sight check.** Same map and same branch is the entire spatial rule | already true — `SameNativeHeadquartersThing` has never had a distance test |
| *"on the same power systems"* | Any linked thing that **has** a power component must be on the gate's power net | generalises `NativePowerConnected`, which already required the battery and console to share a net |
| *"some shelves and multiples"* | `maxLinked` per role — 8, 6, 6 — rather than exactly one | new |
| *"for use of multi gate facilities"* | A thing linked to one gate is refused to every other gate | generalises the existing `ProviderAlreadyBound` scan |
| *"like beds connect to other furnature"* | Core's own `GenDraw.DrawLineBetween`, with Core's own `InactiveFacilityLineMat` for a link that is not working | new, and free |

**Stating what already worked before building it again** is the standing method here, and in this
case most of the direction was already satisfied by rules written for a different reason.

---

## The three roles

| Role | Accepts | Max | Note |
|---|---|---|---|
| **records archive** | `Shelf`, `ShelfSmall` | 8 | *"things needed to be on shelves/records"*. This is the queued **evidence-case replacement**: the archive is a link role, not a custom item. |
| **analysis equipment** | `MultiAnalyzer`, `HiTechResearchBench`, `SimpleResearchBench` | 6 | *"the research computer multianalysers and other such things"* |
| **engineering tooling** | `ToolCabinet` | 6 | *"tool cabnets for enginners"* |

All existing Core content, named by capability.

### The def name that was wrong

The owner wrote *"multianalysers"*. **`Multianalyzer` is a `ResearchProjectDef`.** The building
is **`MultiAnalyzer`**, with a capital A, in `Buildings_Misc.xml`.

Found by enumerating the installed game data rather than typing the name that reads correctly.
A role that accepted `Multianalyzer` would have loaded without error, shown up in the picker, and
**silently matched nothing** — there is no def-name validation in RimWorld's XML loader to catch
it. That is now the first assertion in the proof.

---

## The power rule, and why it is not per-role

*"thes connections need to be like on the same power systems"* cannot be applied literally to
every candidate, because **a `Shelf` has no power component and therefore no network to be on**.
Requiring one would make the archive role permanently unfillable — the exact role the direction
asks for.

The rule is applied to **anything that has a power component, and to nothing else**. Measured
over the six candidates:

| Powered | Unpowered |
|---|---|
| `MultiAnalyzer`, `HiTechResearchBench` | `Shelf`, `ShelfSmall`, `SimpleResearchBench`, `ToolCabinet` |

Both halves are non-empty, which the proof asserts in both directions: if every candidate were
powered the exemption would be dead code, and if none were the rule would be.

---

## Inactive links are kept, not dropped

A link whose equipment loses power, gets switched off or breaks down goes **inactive** rather
than being removed. A player who loses power for an hour has not un-designated their facility.
Inactive links draw in Core's own faded line material — the same thing vanilla does for an
unpowered multi-analyzer.

Unlinking, unlike binding a provider, is allowed **mid-opening**: a link grants no charge and no
work, so releasing one can never strand anybody. That asymmetry is deliberate and commented.

---

## The proof

`.local/register/proof-gate-links.py`, asserting rather than printing. Twenty claims, all held:

- every def name a role accepts **exists in the installed game** — the assertion that catches the casing class of bug;
- **no def name appears in two roles**, because `RoleFor` returns the first match in display order and an overlap would make a thing's role depend on display order;
- display orders are distinct;
- every role allows multiples;
- at least one candidate is powered **and** at least one is not;
- `Shelf` specifically is unpowered;
- Core's facility defaults **are still** 8 cells and LOS-required, so the argument above stays true;
- `MultiAnalyzer` and `ToolCabinet` **still carry Core's own facility comp**.

### Sanity-tested in both directions

| Planted | Result |
|---|---|
| `MultiAnalyzer` → `Multianalyzer` (the real mistake) | **FAIL**, named the def and the role |
| `Shelf` added to the tooling role as well | **FAIL**, named both roles |
| Both reverted | **PROOF HELD** |

---

## Receipts

| | |
|---|---|
| Version | 0.10.8-dev |
| Build | 160 C# files, 84 package files, **0 warnings, 0 errors** |
| New source | `Gate/GateEquipmentLinks.cs` |
| New defs | `RimroomsGateEquipmentDef` ×3 — a mechanics def, **no gameplay ThingDef** |
| New package files | the roles, `RR_GateLinks.xml` |
| Core defs patched | **none.** No facility comp, no distance, no LOS, nothing |
| New art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **seven**, all passing |
| Game launched | **no** |

Still open and named in `TODO.md`: **wiring evidence custody to the archive role** — the archive
is the place records belong, and the custody rule that says a book's chain of custody *completes*
when it reaches one is its own change.
