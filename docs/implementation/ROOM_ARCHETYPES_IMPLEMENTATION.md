# Rooms that are a kind of place (0.7.9-dev)

**Baseline:** `ea96af3` (0.7.8-dev, 138 C# files, 85 package files).

**This checkpoint — 0.7.9-dev:** **140 C# source files** (two new), **86 approved package files** (one new def file). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `10FD715C060E983DA8DCCFB77E273701EBAA0E0053C2781EE8CDF60502179215`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries, to everything imanginable and every variation of them and even wild waky carzxzy creepy things"*

0.7.8-dev made coordinates look different by depth. **A repainted room is still the same room.** This is what makes a deep space strange from the inside.

## Capability, not a list of names

Every furniture slot asks the game **what kind of thing it wants** — *a work table, a bed, something sittable, something with storage, something that emits light, something decorative, anything in this category* — and the def database answers.

A hand-written list of defNames could never deliver *"everything imanginable"*. It would cover Core, miss every DLC, miss all 274 profile mods, and rot the first time anything was renamed. **Asking for a capability means a profile that adds a new workbench puts that workbench in Backrooms workshops the day it is installed, without this mod knowing it exists.**

Candidate lists are cached per session and **sorted ordinally**, which matters more than it looks: unsorted, the list would follow def load order, that order changes with the mod list, and the same seed would produce different rooms on a different machine.

## Depth 1 stays empty, and that is the point

`Select` returns null at depth 1. **The shallow yellow rooms are sparse because that emptiness is the look** — filling them with laboratory equipment would destroy the exact image the setting rests on. Density and strangeness climb with depth instead.

The threshold room is never dressed at any depth either: it is where the player arrives, and the way back must never be buried under scenery.

## Fourteen archetypes, tiered by depth

| Depth 2+ | Depth 3+ | Depth 4+ | Depth 5+ |
|---|---|---|---|
| laboratory, workshop, dormitory, canteen, storeroom, office floor, salvage cache | nursery, machine hall, ward | **gallery**, **the same room again** | **wrong assembly**, **hoard** |

The last four are flagged `anomalous` — the owner's *"wild waky carzxzy creepy things"*. The flag exists so the escalation ladder can later cap how many a coordinate may hold without reworking any of this.

*The same room again* is deliberately fixed-count rather than rolled: identical furniture in identical positions is the whole idea.

## "Every variation of them", without authoring each variation

Every slot carries a **count range** and an **appearance chance**, both rolled from the room's own seed. So two laboratories in one coordinate share an archetype and are **not the same room**, while the same room is identical every time it loads.

## Decoration is never allowed to fail a generation

`TryPlace` returns null instead of throwing. A slot nothing answers is skipped, a fixture that will not fit is skipped, and a room that ends up bare is a bare room.

It is a **separate method** from `Place` rather than a flag on it, deliberately. The required content genuinely must fail loudly if it cannot be placed — the clue system, the power validation and the saved layout all depend on it — and a shared code path with a "do not throw" switch is exactly how that guarantee gets quietly lost later.

Dressing also runs **after** the family fixtures and the landmark, so nothing it does can displace what those systems depend on.

## Two placement rules that protect the player

- **A fixture may be at most 2×2.** A large machine dropped into a Backrooms room can seal the route cross, and the entire point of a coordinate is that somebody has to be able to walk back out.
- **Edifices that are not minifiable are excluded outright.** A wall or door in the middle of a room changes the layout rather than dressing it, and the layout is saved and validated elsewhere.

A definition from an unknown mod that refuses to be constructed is caught and skipped — that is a missing decoration, not a broken coordinate.

## Not done, and named in `TODO.md`

- **Material variety** — *"materials of all types"*. Fixtures currently take their default stuff; choosing stuff per coordinate is its own pass.
- **Anomalous *events*, as distinct from anomalous rooms.** The rooms exist; things that *happen* do not.
- **Escalation against colony wealth**, and the owner's acceptance condition that a solo group can build, supply and escape a high-tier coordinate.
- **Inhabitant and monstrosity families** tiered by depth and wealth.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass. Every referenced `ThingCategoryDef` verified present in Core.
- Compliance: one def file, fourteen archetype defs. **No new gameplay ThingDef, no asset, no patch operation, no new work type.**

## For the post-completion test phase

Confirming a depth-1 coordinate is still sparse and yellow; confirming a depth-3 coordinate has recognisable rooms; confirming the same coordinate is identical after a reload; confirming two rooms of one archetype differ; confirming nothing ever seals the route cross; confirming a threshold room is never dressed; confirming DLC and mod furniture appears when those mods are loaded; and confirming the same seed produces the same rooms under a different mod list order.
