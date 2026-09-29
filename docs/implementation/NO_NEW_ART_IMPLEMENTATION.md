# The last new art is gone — 0.12.22-dev, 2026-09-29

**Dated record.** Never rewritten. Closes the art half of invariant 10.

---

## The count in the row was stale by ten

M2 carried this row:

> **Remove the 14 historical gameplay PNGs from the package allowlist** once their references are
> gone.

**Four shipped.** Ten had already gone in earlier retirements — 0.9.0-dev, 0.9.9-dev, 0.10.7-dev —
and nobody updated the row. That is the **fourth** appearance of the same defect this session: the
assembly hash, the C# file count, the backlog statuses, and now this.

---

## The breach was the art, not the defs

Four defs still named a custom texture. Only **one** of them is a gameplay item at all:

| Def | What it actually is | Invariant 10 |
|---|---|---|
| `RR_ReturnAnchor` | a generator-placed marker; non-deconstructible, non-claimable, no hit points | **permitted** — infrastructure |
| `RR_QuietPursuer` | an `Ethereal` Thing with a custom `thingClass` | **permitted** — a mechanics def |
| `RR_RouteRecording` | **already superseded** — see below | legacy only |
| `RR_FieldRecorder` | a buyable, carryable `ResourceBase` item | **a real breach** |

`RR_RouteRecording` needed nothing at all: `CompRouteEvidence.NativeCarrierDef` already resolves
Core's **`TextBook`**, patched with our comp, and `IsLegacyCarrier` exists purely so saves made
before that switch keep loading.

**So rebuilding working systems was never the fix. The textures were.** Separating the def from its
texture is what made this a small change instead of a redesign.

---

## Every replacement was enumerated, not remembered

`Data/Core/Defs` holds **908 distinct `texPath` values**, and each path below was confirmed present
in at least one real Core def **before** it was used.

That is invariant 19, and it is specifically the discipline that
`Named<TerrainDef>("Carpet")` skipped three checkpoints ago — which shipped the wrong floor in the
yellow rooms for months.

| Def | New path | Why |
|---|---|---|
| `RR_FieldRecorder` | `Things/Item/Equipment/WeaponSpecial/OrbitalTargeter` | a handheld device with a radio, which is what its description already claimed |
| `RR_RouteRecording` | `Things/Item/Book/Schematic/Schematic` | a recorded document, consistent with `TextBook` being the native carrier |
| `RR_ReturnAnchor` | `Things/Building/Furniture/PenMarker` | a marker post |
| `RR_QuietPursuer` | **`Things/Mote/Black`** | see below |

### The Pursuer is better for it

Its own description reads:

> *A motionless figure seems to occupy a nearer room whenever attention shifts.*

Core ships no humanoid-figure Thing texture. A **plain black shape you cannot resolve** is closer to
what that sentence promises than a drawing ever was — you are not meant to get a good look at it.

The M2 row suggested a `Megascarab` reskin. **Declined**: that would put an insect where a figure
belongs, and every learned rule about the Pursuer is about a figure.

**No behaviour changed.** `Thing_QuietPursuer` is untouched.

---

## Archived, not deleted

All four PNGs are in `docs/implementation/historical-content/0.12.22-dev/textures/`. Invariant 37:
retired content is archived, never deleted.

---

## The rule is now a check, as a shape rather than a count

`check-register-compliance.py` asserts:

> every image and sound this package ships is a **menu slide**

`About/` is exempt, because every mod ships a preview and an icon. No number appears in the rule, so
it **cannot go stale** the way *"the 14 historical PNGs"* did.

```
note: ships no gameplay art or audio; menu images only
```

**Fault-planted both ways:**

| Planted fault | Exit | Caught |
|---|---|---|
| a gameplay texture reappears under `Textures/Threats/` | 1 | ✓ |
| a def naming a texture that no longer ships | 1 | ✓ |
| *restored* | **0** | — |

The second one matters as much as the first: a wrong `texPath` returns null from `ContentFinder` and
**fails at runtime with no load error**, which is exactly how the carpet defect hid.

---

## What is still open, stated plainly

**`RR_FieldRecorder` the def.** The art is gone, but it remains the one genuinely buyable, carryable
gameplay `ThingDef` this mod authors. Retiring the def needs a migration decision, because saved
Things reference it — the owner's own rule: *"Migration decision or declared development-save break
before removing any Def a saved Thing references, with the old build preserved."*

That is one row, and it is honestly open rather than quietly closed.

---

## Receipts

| | |
|---|---|
| Version | 0.12.22-dev |
| Build | 174 C# files, **87 package files** (four fewer), **0 warnings, 0 errors** |
| C# changed | **none** |
| Gameplay art or audio shipped | **zero** |
| Menu images shipped | **6**, the single declared exception |
| Core `texPath` values enumerated before choosing | **908** |
| Checkers | **nine**, all passing |
| Proofs | **twenty-one**, all exiting zero |
| Planted faults caught | **2 of 2** |
| Game launched | **no** — these are correct by def and by path, and **nobody has looked at one** |
