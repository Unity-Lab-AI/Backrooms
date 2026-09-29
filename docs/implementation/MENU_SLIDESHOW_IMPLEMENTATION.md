# The menu takes any number of slides — 0.12.16-dev, 2026-09-29

**Dated record.** Never rewritten.

---

## What was asked, and what I could not do

> *"and some of the art for the manu menu … needs to have like content scenrio art like and
> ecounter and like lab opertions or gate industrial usage and scary creepy backrrom univers sill
> art … in dramatic and tragic and creepy moments of differnt scense and possible run ins, go hand
> ful or so or all these needs to be genrated well and rimwolrd styled"*

**This session has no image-generation tool.** That was established by searching the available
tool surface rather than assumed, and it was said plainly instead of worked around. The owner's
answer was immediate and correct:

> *"okay ill get another ai to tdo the art in parrallel"*

So the work here is the half that makes a parallel art track land cleanly: **the slideshow accepts
any number of slides with no code change, and the brief is precise enough to produce drop-in
files.**

---

## The slide list was hardcoded

```csharp
private static readonly string[] TexturePaths =
{
    "UI/Menu/RR_Menu_FacilityThreshold_v2",
    "UI/Menu/RR_Menu_FieldSurvey_v2"
};
```

Every new image would have needed a C# edit, a rebuild and a determinism run — which is exactly
the wrong shape when the art and the code are being produced by different parties at the same
time. It is now `ContentFinder<Texture2D>.GetAllInFolder`, and `GetAllInFolder` was confirmed to
exist on the installed 1.6 assembly by decompiling `Verse.ContentFinder<T>` rather than by
remembering it.

### A bare folder scan would have been a compatibility defect

`UI/Menu` is a **generic content path**, and `ContentFinder` resolves across **every loaded mod**.
A scan with no filter would pull another mod's menu art into this slideshow. In the 294-mod target
install that is not a risk, it is a certainty.

**The `RR_Menu_` prefix is load-bearing**, and the doc comment says so at the site so nobody
"simplifies" it away later.

### Order is ordinal, per invariant 26

Slides sort ordinally by name. A slideshow whose running order depends on whatever order the
loader happened to return is one nobody can describe, and nobody can reproduce a screenshot from.

---

## Two integrity notes that had been wrong since the art was added

`check-package-integrity.py` reported this on **every single run**:

```
note: texture ships but nothing references it: UI/Menu/RR_Menu_FacilityThreshold_v2.png
note: texture ships but nothing references it: UI/Menu/RR_Menu_FieldSurvey_v2.png
```

Both were referenced the whole time. The checker only recognised
`ContentFinder<Texture2D>.Get("literal")`, and the old code called `Get(variable)` out of an array
— which no regex can follow.

**A note nobody can act on is noise, and noise is how a real finding gets scrolled past.** The
checker now understands `GetAllInFolder`, resolves the folder through the `const` that names it,
and reports the folder with its slide count instead:

```
note: folder scanned by GetAllInFolder, 2 texture(s) covered: UI/Menu
```

**This is not a widening.** `GetAllInFolder` genuinely loads every image under the folder, so
treating them as referenced is what the API does. The more serious direction — *a reference that
does not ship* — is untouched.

---

## The keyed checker was right to complain, and was fixed by its own design

`SlidePrefix = "RR_Menu_"` looks exactly like a keyed string, and `check-keyed-strings.py` failed
on it. Correctly: it cannot tell a translation key from a texture-name prefix by spelling.

That file's stated design is **classified by call site, not by name** — the same principle
`check-display-style.py` documents. So the fix follows it: a `const string` counts as internal
**only when it is passed to `StartsWith`**. A const that merely looks like a prefix, or one later
handed to `Translate`, is still checked as a keyed string.

**Fault-planted, because a narrowing that is not proved narrow is a widening.** An undeclared
`RR_` const that is *not* used in `StartsWith` still makes the checker exit 1; removing it returns
it to 0.

---

## The brief

`docs/MENU_ART_BRIEF.md`. Three things make it usable by someone who cannot read this codebase:

**Real numbers, read out of the source.** 1920 × 1080 at 16:9 (the two existing slides are
1672 × 941 — the same aspect). The version label occupies `x 350 → ~770, y 10 → 74`. The
expansion strip occupies the bottom-left 104 px. 30 s dwell, 2 s crossfade.

**The palette the mod already ships**, from `BackroomsPalette.cs` — so the art matches the game
rather than a general idea of the Backrooms. Depth 1 is the sacred yellow rooms. A gate is **an
ordinary door, tinted blue** — not a portal ring, not a vortex. The company is 1990s industrial:
CRTs, beige plastic, paper, cable runs.

**Twelve scenes, every one depicting something the mod actually contains.** The threshold, gate
assembly, spin-up, a field survey, marked routes, coherence decay, something waiting at the
threshold, a crew that did not come back, the clean-up team, the store basement, the solo start,
and a door standing free of any wall in a residential street. **None of it is invented lore**,
which is the point — the menu should show the game. A cut-down priority set of five is named.

**The one manual step is stated and cannot be skipped:** each new PNG needs a line in
`tools/package-files.json`, and the brief warns **not** to add the line before the file exists,
because a listed-but-missing file breaks the staging script — which the checker also catches.

---

## Receipts

| | |
|---|---|
| Version | 0.12.16-dev |
| Build | 173 C# files, 87 package files, **0 warnings, 0 errors** |
| Images produced here | **none** — no image-generation tool exists in this session |
| Slides the code now accepts | **any number**, no code change |
| Wrong integrity notes fixed | **2**, wrong on every run since the art was added |
| Checker narrowings, each fault-planted | **2** |
| Checkers | **eight**, all passing |
| Proofs | **eighteen**, all exiting zero |
| Game launched | **no** — dwell, crossfade and legibility behind the menu buttons are **unverified by play** |
