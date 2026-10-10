
---

## 2026-09-29 — The register the owner can actually open, and the work-type list checked instead of trusted

**Still 0.6.4-dev. No C# change, no version bump, assembly byte-identical.**

### Verbatim owner requests

> *"read Now. md and any and all revent prep docs as you continue the todo work and take not there is a mode .xlml like thing that im not sure is fully working i try to open it but its not human navigatable but its suppose to spreeadsheet out all the mods and potential uses and issues and theri uses and descriptions and shit if i remember correctly and you should definatly be using it and or fixing it up as you go along with build the Mod here and or update it where need of past work already done and continue it forward and making sure it is human havigate able becasue i open it up and i dont see what the preview images show, so idk how it works or if it does"*

> *"Rimrooms_Async_Industries_294_Mod_Integration_Register this thing is what i was talking about"*

> *"wtf is this xlsx??? i thought it was a spread sheet but it just opens up codex for chatgpt??? wtf i thought it was the mod spreedsheeet! fix it"*

> *"remember map>backrrooms>backrroms , map > backrooms > map > backrooms , and backrromms > map>backrooms>backrooms>map are just a few of the portal connections allowed in the game to different maps in the world"*

> *"with different portal combos built and found"*

### The root cause was not the file

- [x] **`.xlsx` was never openable on this machine.** `assoc .xlsx` returns nothing, there is no `UserChoice` registry key, and **no spreadsheet application is installed** — no Excel, no LibreOffice, no OnlyOffice, no WPS. Windows handed the extension to an unrelated application that loosely claimed it. That, not the XML, is why the owner never saw what the preview images showed. Four hours of correct XML would have changed nothing the owner could see.
- [x] **Fixed by building a format the machine can open.** `Rimrooms_Async_Industries_294_Mod_Integration_Register.html`, beside the workbook. Double-click, browser, no install, **no external asset** so it works offline. Four views as tabs, plus a **live search across all seventeen columns of every row** and stance / firmness / family filters with a running match count — things a spreadsheet could not give. SHA-256 `B98D16F8733DA8DB23D57221C3C87324EB26F21EDD253A835A1F95C56BCF5F71`.
- [x] **Not done deliberately:** changing file associations or installing software on the owner's machine. That is the owner's call, not a build step, and the HTML removes the need.

### Four real XML defects in the workbook, each verified against the file

- [x] **All 5,009 text cells were typed `t="str"`** — the OOXML type for a cached *formula* result — with **no formula anywhere in the file**, and `sharedStrings.xml` was an empty `<sst/>` still declared as a relationship.
- [x] **All 294 rows were pinned `ht="78" customHeight="1"`**, which *forbids* auto-fit, while five columns carry up to 300 characters. Planned Use, Compatibility Watch, FinalDisposition, EvidenceBuild and AcceptanceEvidence were permanently clipped. Gridlines were off and no cell had a border.
- [x] **The Overview's tallies were stale and wrong.** It listed **45** families; the rows hold **66**. Twenty-two real families appeared nowhere in it and **eleven counts disagreed with the rows** — Medical read 29 against an actual 27, Furniture 17 against 11. Both totals reached 294 only because the stale buckets absorbed the missing ones.
- [x] **It had no generator anywhere in the repository**, and **six columns existed only inside that one binary** — System Family, Backrooms Dependency, Planned Use, Integration Approach, Compatibility Watch, Research Status. The other eleven were diffed against the tracked inventory first: **zero mismatches**. The data was sound; the container was not.

### What was built to keep it

- [x] **One fact, one home.** The six orphan columns are now `research/mod-register-integration-fields-2026-09-29.csv` and the overview prose is `research/mod-register-overview-2026-09-29.csv`. The inventory CSV keeps the eleven it already owned and is **never rewritten**. Family, stance and firmness tallies are **not stored at all** — counted from the rows every build, which is the only way defect 3 cannot recur.
- [x] **`tools/research/build-mod-register.py`** — standard library only, because a build tool that needs an install is a build tool that stops working. Builds both outputs in one pass over the same rows so they cannot disagree. Row heights are a **floor written without `customHeight`**, the exact inversion of defect 2. Fixed archive timestamps, so an unchanged source rebuilds byte-identically: workbook SHA-256 `3B3E7BAFBE02C0091C277A18E5B6EF70B993E3B6EA77788590D034E284B27B53` twice.
- [x] **`tools/research/check-mod-register.py`** — round-trips all 294 × 17 cells and every card field back out of the package, asserts zero formula-typed cells and zero pinned heights, and validates the HTML for cards, links, escaping through the same escaper that wrote it, complete filters, balanced tags and **no external asset**.
- [x] **Two derived columns**, because the raw dispositions take **104 distinct forms**. Stance: Optional 243, Required 17, No integration 16, Configuration only 13, Visual only 3, Unclassified 2. Firmness: **Provisional 200, Settled 94** — the continue-forward axis. The two Unclassified rows are left visibly unclassified rather than forced into a bucket they do not fit.
- [x] **A classification mistake caught by reading the output.** Testing the no-integration phrases above "optional" moved **59** mods reading *"optional support; no Rimrooms patch planned"* into No integration — the opposite of what they say. A count jumping 13→72 in one edit was the tell. Order corrected and the reason written into the function.
- [x] **Independent confirmation:** `audit-gate0.py` already compared **3,234** workbook cells against the inventory and passed the rebuilt file unchanged, because its reader already handled `inlineStr`.

### A pre-existing audit failure, found and fixed

- [x] **`audit-gate0.py` had been returning `"result": "FAIL"`.** `docs/TODO.md` line 79 carried a bare same-file fragment copy-pasted from `CONNECTED_COLONY_PORTALS.md` line 104, where that heading actually lives. Repointed; the audit now returns `"result": "PASS"` with zero errors. Also learned: the audit's link scanner strips fenced code blocks but **not** inline code spans, so documenting a broken link inline recreates it.

### Joy and rituals: both decided, no family

- [x] **Joy has no work type at all.** Every `WorkGiverDef` in Core and all five DLC was enumerated: **23 work types, 145 giver defs**, and `Joy` is not among them. `JobGiver_GetJoy` is a `ThinkNode_JobGiver` reading `pawn.needs.joy`. The needs invariant applies exactly as it did to food and rest — a pawn crossing a gate to relax can be stranded by a closing gate, and recreation is what sent it. **Solve it logistically:** furniture is delivered by the existing families and a colonist takes recreation wherever it stands.
- [x] **No `WorkGiverDef` anywhere is ritual-driven.** The only gathering-shaped giver in the whole set is `HelpGatheringItemsForCaravan`, which is `Hauling`. A `LordJob_Ritual` owns its participants' duties for the ritual's duration, so this layer never sees a ritual participant and cannot send one anywhere. One runtime check named rather than mechanised: a colonist holding a live commitment that is then pulled into a ritual.
- [x] **`Patient` and `PatientBedRest` decided against permanently** — a pawn's own medical self-care, already forbidden by the needs invariant and by `CanUseBedNow` refusing an off-map bed.

### The remembered families list was incomplete, and checking it was the point

- [x] **`DarkStudy` and `Fishing` were missing from it entirely**, and neither appears anywhere in the mod's source. Closing the families row on that list would have closed it wrongly. The enumeration is `research/WORK_TYPE_COVERAGE_AUDIT.md`; twelve work types have a deployment, five are covered by the bill carry family, two are decided against, **four are genuine gaps**.
- [x] **The bill gap is the largest, and the bills record left it open.** `CONNECTED_BILLS_IMPLEMENTATION.md` settles delivering ingredients but never decides **who runs the bill**, so a bench on an unstaffed coordinate accumulates material and produces nothing. The `UnfinishedThing` fact it pins argues *for* a deployment: a half-made thing belongs to one colonist, which is why the carry family must never touch one and why a **deployed** worker running Core's own `WorkGiver_DoBill` locally is correct by construction. One family covers Cooking, Crafting, Smithing, Tailoring and sculpting.
- [x] **Mechs needed no family of their own** — mech work lives inside `Smithing`, `Hauling` and `Research`, so it is covered exactly as far as those are, and the remainder falls inside the gaps already named.

### The three hauling providers, closed as register rows

- [x] **Pick Up And Haul (164)** — no seam. The connected families run their own job driver and work givers, not `WorkGiver_HaulGeneral`. The untested direction is the reverse one: a worker carrying inventory it gathered for a near-side stockpile when its crossing begins. Recorded in `CompatibilityWatch`.
- [x] **Haul to Stack (107)** — the publisher states it does nothing while Pick Up And Haul is active, and 164 is selected. That is a page claim, not a reproduced result, so it is recorded as inert **pending the test phase**. Steam also shows an item-removed notice with no stated reason.
- [x] **Prison Labor (288) — settled on the axis that mattered, from Core source.** A prisoner given work by this mod **can never cross a gate**: `PortalTraversalPolicy` admits only `Faction.OfPlayer` colonists, and `Pawn.IsColonist` requires `Faction.IsPlayer`, which a prisoner of the colony never has — prisoners keep their own faction and are held through `HostFaction`.
- [x] **And an undocumented behaviour found while proving it.** `IsColonist` reads `Faction.IsPlayer && RaceProps.Humanlike && (!IsSlave || guest.SlaveIsSecure) && !IsSubhuman`, so **a secure slave may cross a gate and an insecure one may not.** That is correct — Core's own containment judgement draws the line and the escape-risk case is refused — but nobody had written it down. Pinned in `CONNECTED_WORK_CORE_API.md`.

### The topology shape, settled

- [x] **An unbounded alternation of world maps and Backrooms coordinates, in any order, to any depth**, with built gates and found frontiers mixed freely. Not two special cases but one rule. Of the owner's three examples, **`map > backrooms > backrooms` already routes end to end**; the other two resolve to the single open piece, an ordinary-map endpoint, which is already queued. The non-restriction half is already true: routing does not discriminate by `PortalConnectionKind`.

### Documents updated in the same change

`implementation/MOD_REGISTER_REBUILD.md` (new), `research/WORK_TYPE_COVERAGE_AUDIT.md` (new), `implementation/CONNECTED_WORK_CORE_API.md` (the traversal fact), `TODO.md` (three owner directions captured verbatim, 24 rows), `REGRESSION_CONTAINMENT.md` (four doc-rot rows plus the register rebuild step), `CHANGELOG.md`, `NOW.md`, `DEFERRED.md`.

### Build evidence

**Still 0.6.4-dev**, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **112** C# source files and **76** approved package files, both unchanged. Assembly SHA-256 `4057EFD15AAB4B1C609732AB18A02F025C9A98A8D951374CE7333A80C9780728` after deleting `obj/` and `bin/` — **identical to 0.6.4-dev, which is the point.** `build-mod-register.py`, `check-mod-register.py` and `audit-gate0.py` all exit zero. Evidence folder `implementation/evidence/mod-register-rebuild-2026-09-29/`. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files changed: 0 (deliberate — the mod binary is byte-identical). Tools created: 2. Tracked data files created: 2. Docs updated: 8 (2 new).
Owner directions captured verbatim: 5. Register defects found: 5, one of which was the machine having no spreadsheet application at all.
Pre-existing audit failures found and fixed: 1. Mistakes of my own caught by reading output: 2 (a checker key order, a classifier priority).
Undocumented Core behaviours pinned: 1 (a secure slave may cross a gate).
Work families: still 22. Decided against, explicitly: joy, rituals, Patient, PatientBedRest. **Genuine gaps found by enumeration: 4**, two of which were absent from the remembered list.
Still open: the four work-type gaps, the ordinary-map portal endpoint, the three starting sites, floors returning materials when lifted, and the 1990s universe factions.
