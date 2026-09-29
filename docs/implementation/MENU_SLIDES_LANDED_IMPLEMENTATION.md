# Four more menu slides — 0.12.17-dev, 2026-09-29

**Dated record.** Never rewritten. The other half of `MENU_SLIDESHOW_IMPLEMENTATION.md`
(0.12.16-dev): the art arrived.

---

## The drop-in design worked

Four images landed in `1.6/Textures/UI/Menu/`, correctly prefixed, produced on the owner's parallel
track:

| Slide | Scene |
|---|---|
| `RR_Menu_LaboratoryOperations.png` | staff at beige CRT consoles and a wired battery bank beside a faintly blue-tinted open door |
| `RR_Menu_IndustrialGateLogistics.png` | gate logistics, industrial |
| `RR_Menu_CorridorEncounter.png` | the encounter |
| `RR_Menu_SilentRecovery.png` | the quiet aftermath |

**The slideshow picked up all four with no code change**, which is exactly what replacing the
hardcoded two-entry string array in 0.12.16-dev was for. `check-package-integrity.py` now reports
**six textures covered** by the folder scan. Six slides cycle where two did.

The prompts in the provenance record follow the brief closely — painterly not photographic, 1990s
beige CRTs and cables with no holograms, **portals as ordinary human-sized doors with faint blue
frames rather than rings or vortices**, left third kept quiet for the menu buttons, no text or
logos. That is the brief being used rather than read.

---

## What I added, and why it was worth a checkpoint

### A slide can fail silently, and that was likely rather than hypothetical

The slideshow shows only files whose name starts with `RR_Menu_`. So **a correctly-drawn image with
the wrong filename is loaded by nothing, shown to nobody, and no build, checker or log says a
word.** With the art produced separately from the code by a different party, a naming mistake was
probable.

This is the failure class this project keeps rediscovering: the whole request surface read by
nothing, five `PawnKindDef`s authored and unread, three dead gate accessors, two menu textures
reported unreferenced for months. `proof-menu-slides.py` asserts the naming contract, and planting
a stray `MenuBackdrop_NoPrefix.png` makes it exit 1.

### A truncated image fails at load, not at build

Unity reads a PNG when it needs it — long after the build has reported success. A half-finished
copy is the obvious way parallel asset delivery goes wrong, so the proof checks the signature
**and** that `IEND` is the final chunk with zero trailing bytes.

**My first attempt at that check was wrong.** It compared the final eight bytes against a literal
`IEND` chunk and reported **every file as broken, including the two that had already shipped** — the
CRC differs per file, so the comparison could never pass. The check was wrong, not the files, and
it was corrected rather than believed. Confirming the pre-existing files were fine is what made
that obvious.

### Aspect is checked as a set

`BackgroundRect` reads each image's **own** aspect, so mismatched slides letterbox differently and
the crossfade between two of them reads as a bug rather than a transition.

`RR_Menu_LaboratoryOperations.png` is **1672 × 940** against the others' **1672 × 941**. That is a
one-pixel difference, 0.1% of aspect, inside the tolerance — **reported explicitly rather than
hidden, and it does not need regenerating.** The tolerance allows a rounded pixel and refuses a
different shape.

### The proof reads the contract out of the source

`SlideFolder` and `SlidePrefix` are extracted from `RimroomsMenuBackground.cs` rather than restated
in the proof. Renaming either one moves the proof with it, instead of leaving it quietly checking a
value that no longer exists.

---

## Provenance is a release obligation

`outputs/menu-art-2026-09-29/prompts-and-provenance.json` records the tool and the **exact prompt
for each image**. Two reasons it ships rather than being tidied away:

1. **Steam requires AI-content disclosure.** A release-time claim about how art was made needs a
   record made at the time, not reconstructed from memory.
2. **Original menu images are the single declared exception** to this project's no-new-art rule
   (invariant 10). An exception that cannot be audited is not an exception, it is a gap.

The proof asserts the record exists.

---

## Fault-planted three ways

| Planted fault | Exit | Caught |
|---|---|---|
| a slide with no `RR_Menu_` prefix — **would never appear** | 1 | ✓ |
| a prefixed slide missing from the package allowlist | 1 | ✓ |
| a truncated slide | 1 | ✓ |
| *restored* | **0** | — |

---

## Receipts

| | |
|---|---|
| Version | 0.12.17-dev |
| Build | 173 C# files, **91 package files**, **0 warnings, 0 errors** |
| C# changed | **none** |
| Slides cycling | **6**, up from 2 |
| Images produced here | **none** — owner's parallel track |
| Checkers | **eight**, all passing |
| Proofs | **nineteen**, all exiting zero |
| Planted faults caught | **3 of 3** |
| Game launched | **no** — how these read behind the menu buttons, and whether 30 s dwell and 2 s crossfade feel right, are **unverified by play** |
