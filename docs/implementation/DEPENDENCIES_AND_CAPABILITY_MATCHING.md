# Dependencies and capability matching — what Rimrooms actually needs, and how to find it

**Owner direction, 2026-09-28, verbatim:**

> make sure mods needed specifically for our mod as dependacies are properly handled with our single mod Rimrooms properly using them as needed to impliment all features of the mod properly

> remember the mod names might not jump out as the specific ferature we need for our mod so u have to think critically as to what can and should be used and in what whay with what specialities we need in our mod to propely create the needed action function thing and or property or any other coded needed useing critical thinking to achieve our Superior end result in mod functionality

This document is the standing answer to both. Part 1 is the audited dependency position, with evidence. Part 2 is the method for deciding what to build a feature on — and it dissolves blockers that were being treated as content problems when they were framing problems.

---

# Part 1 — the audited dependency position

**Result: Rimrooms requires nothing but base Core, and that is now verified rather than asserted.**

`About.xml` declares no `modDependencies`, and `loadAfter` names only `Ludeon.RimWorld`. The description claims "No DLC or Harmony required by this package." That claim was audited four ways.

### Every non-Rimrooms def the code looks up, and where it comes from

Twelve def names are looked up by string. Each was traced to the package that actually defines it, in the game's own `Data` folders:

| Def | Defined in | Used for |
|---|---|---|
| `Assign`, `Work` | **Core** (`Work` also appears in Biotech, but is defined in Core) | guarded links to native tabs |
| `Door` | **Core** | gate provider, site return thresholds |
| `Chemfuel`, `ChemfuelPoweredGenerator` | **Core** | gate power provider |
| `Concrete`, `PavedTile`, `WaterDeep` | **Core** | site terrain |
| `Heater`, `StandingLamp`, `HiddenConduit` | **Core** | site fixtures |
| `TextBook` | **Core** | field evidence object |

No DLC def, no mod def, nothing from the 294-row profile. **The Core-only claim holds.**

### Patch guarding

Both XML patch files use `PatchOperationConditional`, and the one case that genuinely needs it is handled: of the four Core defs patched, `Autodoor`, `CommsConsole` and `TableMachining` already carry a `<comps>` node, and `Door` does **not** — which is exactly the case the conditional creates the node for. Verified by parsing the Core defs rather than assuming. A patch that silently failed to apply would have meant the designated provider could never be designated, invisibly.

### Failing safely when a def is missing

Four job lookups used `DefDatabase<JobDef>.GetNamed`, which **throws** when the def is absent, against sixty-eight that used `GetNamedSilentFail`. All four were Rimrooms' own defs, so they are present in a healthy load — but a def can be absent for reasons outside this mod's control: another mod patching it away, a load-order conflict, a partially loaded package. All four now refuse gracefully with a keyed reason. There are now **zero** throwing def lookups in the project.

### Optional providers, and why they already work

Two claims from [the profile boundaries](CONNECTED_WORK_PROFILE_BOUNDARIES.md) were checked against what the code actually does, not against intent:

- **OgreStack (row 157) changes effective stack limits, and the integration plan requires Rimrooms to read them at runtime.** It does, by construction: every quantity decision goes through `pawn.carryTracker.MaxStackSpaceEver(def)` and `ThingOwner.GetCountCanAccept`, which read the loaded `stackLimit`. Because no stack size is ever hardcoded and no quantity is computed from a Def constant, OgreStack is respected automatically and its absence changes nothing. This is a case where using Core's API instead of arithmetic bought compatibility for free.
- **Modded doors** are accepted wherever a threshold is needed, because every check tests `anchor is Building_Door` rather than a def name. A wide or modded door works as a gate threshold if it is a `Building_Door`; the one thing not claimed is a multi-cell provider's true opening footprint, which remains a named deferment.

### The standing position

Rimrooms stays **one mod with no hard dependency**. Optional mods are integrated by capability through public API when present, and their absence is never a failure path. Nothing in this project may declare a hard dependency to obtain a *content* asset — Part 2 explains why that is never necessary.

---

# Part 2 — capability matching: the method

**The rule: never ask "is there a mod or a Def called X". Ask "what capability does this feature actually need, and what existing object already has that capability."**

A mod's name describes what its author built it for, not the set of capabilities it exposes. The same is true of a Def name. Deciding what to build on by reading names is how a project ends up either inventing content it is not allowed to invent, or taking a dependency it does not need.

### The structural fact that makes this work here

Rimrooms already demonstrates the technique, in shipped code. `CompProperties_RimroomsGate` is patched onto Core's `Door` and `Autodoor` and stays **dormant until the player designates a specific instance**. The behaviour lives in the comp; the object is Core's.

That means: **any Core object can carry Rimrooms behaviour without a new ThingDef.** So "Core has no item called a survey tag" is never the right question. The right question is "what physical capability does a survey tag need, and what Core object has it" — because the *behaviour* is ours to add either way, under the existing-content-only rule.

### Applying it to the blockers that were being treated as content problems

These rows in [`../DEFERRED.md`](../DEFERRED.md) were framed as "Core has no X". Restated as capabilities, each has a Core answer:

| Legacy object | The capability actually needed | Core object that has it | Why it is the right match |
|---|---|---|---|
| `RR_SurveyTag` | A placeable marker at a junction with a **distinguishable per-instance identity** the player can refer to later | Core art (`SmallSculpture` and family, via `CompArt`) | Per-instance identity is the hard part, and Core art is the only Core thing that *generates* a unique title and description per object. Placeable, minifiable, cheap. The number lives in our comp; the identity is already there. |
| `RR_ReturnBeacon` | A placed object that marks the route home and is visually distinct from a tag | `OrbitalTradeBeacon` | A Core beacon whose entire existing purpose is marking a location. Semantic and visual match; our comp binds the route meaning. Works unpowered as a marker. |
| `RR_FieldRecorder` | A carried item that **holds a saved record** | `TextBook` (already used for evidence) or any Core item | The record lives in the Rimrooms comp, not in the Def. This was never a content requirement. |
| `RR_SealedEvidenceCase` | A container with **real custody** of evidence | Any Core container exposing an inner `ThingOwner` | Real custody is a `ThingOwner`, which Core containers have. And since 0.5.1-dev the connected container haul route delivers into exactly these, so an evidence container is reachable cross-gate for free. |
| `RR_UtilityGenerator` | Enough power for the opening draw | The **power network**, not one generator | See below — this row was factually wrong. |

### The power row was wrong, and its own parenthetical proved it

The deferment read: *"No single Core generator meets the 3,500 W opening draw (`GeothermalGenerator` is 3,600 W)."* Read against Core's actual values, extracted from `Buildings_Power.xml`:

| Core generator | Output |
|---|---|
| `GeothermalGenerator` | **3,600 W** |
| `WindTurbine` | 2,300 W |
| `SolarGenerator` | 1,700 W |
| `WatermillGenerator` | 1,100 W |
| `WoodFiredGenerator` | 1,000 W |
| `ChemfuelPoweredGenerator` | 1,000 W |

3,600 W exceeds 3,500 W, so the stated blocker is contradicted by the number in its own sentence. More fundamentally the question was mis-framed: **a draw is supplied by a power network with batteries, never by a single generator**, and the gate already designates a *battery* as its energy provider and already reads `ChemfuelPoweredGenerator`. Any combination of Core generators that sustains the draw satisfies it.

This row is corrected in the register rather than left standing. It is the clearest example of the owner's point: the obstacle was in how the requirement was written down, not in the game.

### What this does and does not authorise

- It **does** mean no dependency is needed for content. Every legacy custom object has a Core capability match, so M2's existing-content replacement is unblocked on content grounds and the remaining work is implementation and the save-migration decision.
- It **does not** authorise substituting an object whose real behaviour fights the role. The register's own warning stands: `MedicineIndustrial` is an unsafe substitute for an evidence case, because it is a medical resource that other systems consume. A capability match must not have side effects the role cannot tolerate — that is part of the critical thinking, not an exception to it.
- It **does not** change the existing-content-only rule. It makes it achievable.

### How to use this method

1. Write the capability as a sentence about behaviour, not a noun. "A placed object with a per-instance identity that persists at a location" — not "a sign".
2. List what that capability actually requires of the object: identity, custody, placement, power, minifiability, a `ThingOwner`, an interaction cell.
3. Search Core for objects that *have* those properties, ignoring their names and intended purpose.
4. Check for disqualifying side effects: is it consumed, does another system claim it, does it decay, does it need power it will not have.
5. Bind Rimrooms behaviour with a patched comp and runtime designation. Never a new gameplay ThingDef.
6. Only if no Core object has the capability, and the capability is genuinely required, consider a mod — and then name the exact public API relied on, declare the load order, and keep absence a clean refusal rather than a failure.

Step 6 has not been reached for any feature in this project.
