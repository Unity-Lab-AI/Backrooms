# The 294-mod register: a file the owner can actually open, four XML defects, and a generator so it can be kept

**Baseline:** `b5496c9` (0.6.4-dev, 112 C# files, 76 package files).

**This checkpoint — still 0.6.4-dev, deliberately.** **No C# change and no version bump.** 112 C# source files and 76 approved package files unchanged, and the assembly SHA-256 is unchanged at `4057EFD15AAB4B1C609732AB18A02F025C9A98A8D951374CE7333A80C9780728`. The version was **not** bumped because the shipped mod is byte-identical: the register lives under `outputs/`, not in the mod package, so raising `modVersion` would announce a mod change to a player that did not happen, and would also change the assembly hash for an unchanged binary. This checkpoint is tooling, tracked data and documentation. Evidence: [`evidence/mod-register-rebuild-2026-09-29/`](evidence/mod-register-rebuild-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The owner's report, and why it was right

> *"there is a mode .xlml like thing that im not sure is fully working i try to open it but its not human navigatable ... becasue i open it up and i dont see what the preview images show, so idk how it works or if it does"*

The file is `outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx`. Four defects were found in its XML, each verified against the file itself rather than inferred from behaviour — and then a fifth arrived that outranks all of them.

## Defect 0 — the file was never openable on this machine at all

The XML work below was already done when the owner reported what actually happens:

> *"wtf is this xlsx??? i thought it was a spread sheet but it just opens up codex for chatgpt??? wtf i thought it was the mod spreedsheeet! fix it"*

Checked on the machine, and the answer is not a file problem:

```
HKCU:\...\FileExts\.xlsx\UserChoice  ->  no UserChoice for .xlsx
cmd /c assoc .xlsx                   ->  (no output: no association at all)
Excel / LibreOffice / OnlyOffice / WPS -> none found on disk
```

**There is no spreadsheet application installed, and `.xlsx` has no registered association.** Windows handed the extension to an unrelated application that loosely claimed it — in this case the Codex desktop app. So the workbook was never openable here no matter how correct its XML became, and *that* is the real reason the owner never saw what the preview images showed. The four XML defects were real and are fixed, but on their own they would have solved nothing the owner could see.

**The fix is a self-contained HTML register**, built from the same rows in the same pass as the workbook: `Rimrooms_Async_Industries_294_Mod_Integration_Register.html`, beside the workbook in the same folder. It opens by double-click in a browser, which is always present, needs no install, and loads **no external asset**, so it works with no internet connection. It carries the same four views as tabs — Overview, Index, Full register, Mod cards — plus what a spreadsheet could not give: a **live search across all seventeen columns of every row** and filter dropdowns for stance, firmness and system family, with a running count of matches.

The workbook is still built and still verified, because it is correct now and is the right format for anyone who does have a spreadsheet application. But the HTML is the primary deliverable, and the tooling says so.

## The four XML defects

### Defect 1 — every text cell claimed to be a formula result

All 5,009 text cells in the register sheet were written as:

```xml
<x:c r="B2" s="24" t="str"><x:v>Harmony</x:v></x:c>
```

`t="str"` is the OOXML cell type for **a cached string result of a formula**. There is no `<f>` element anywhere in the file — nothing is a formula. Compounding it, `xl/sharedStrings.xml` was an **empty `<sst/>`** with zero entries while `xl/_rels/workbook.xml.rels` still declared a sharedStrings relationship.

The conformant encodings for a literal string are `t="inlineStr"` with an `<is><t>` child, or `t="s"` with an index into a populated sharedStrings part. The file used neither. Excel is lenient here; nothing obliges a stricter reader to be.

### Defect 2 — the rows were pinned shut

Every one of the 294 data rows carried:

```xml
<x:row r="2" ht="78" customHeight="1">
```

78 points is roughly five lines at the 9pt body font. Measured against the content actually in those columns:

| Column | Longest value | Lines needed |
|---|---|---|
| Planned Use | 263 chars | ~6 |
| Compatibility Watch | 300 chars | ~6 |
| FinalDisposition | 177 chars | ~6 |
| **EvidenceBuild** | 274 chars | **~9** |
| **AcceptanceEvidence** | 261 chars | **~8** |

`wrapText` was set, so the text wrapped — and then `customHeight="1"` **forbade Excel from auto-fitting the row**, so it was clipped instead. Five columns were permanently truncated on screen, including every evidence field. `showGridLines="0"` was set and no cell had a border, so what did render had no grid to navigate by.

This is the direct answer to *"i dont see what the preview images show"*: `register-preview.png` is **5160 × 18604 pixels**, a render of the whole grid at once by a tool that expanded it. The file as shipped shows three columns of cut-off text on a white field.

### Defect 3 — the Overview's tallies were stale, and quietly wrong

The Overview sheet listed **45 system families** with a count each, summing to 294. The rows themselves hold **66 distinct families**. Twenty-two families that genuinely exist appear nowhere in that list, and **eleven of the counts it does show disagree with the rows**:

| Family | Overview said | Rows say |
|---|---|---|
| Medical, biological, and recovery systems | 29 | 27 |
| Furniture, clothing, and visual content | 17 | 11 |
| Facilities and spatial construction | 24 | 23 |
| World, environment, and evidence | 10 | 7 |
| Materials, cargo, and recovered resources | 9 | 7 |
| Research and staff development | 9 | 6 |
| Staff jobs, policies, and social systems | 9 | 8 |
| Emergency care and containment response | 6 | 4 |
| Facility construction and material access | 5 | 6 |
| Food service and staff welfare | 4 | 3 |
| Cross-mod fixes and balance patches | 2 | 1 |

Both totals reach 294 only because the stale buckets absorbed the families missing from the list. One family had also been renamed in the rows — *Multiplayer: guild and world exchange* became *Multiplayer: separate colonies and shared-world exchange* — and the Overview kept the old name.

This is the defect that matters most for trust: a reader consulting the Overview to size a workload got a wrong number with nothing to indicate it.

### Defect 4 — it had no source, and it was the only home for six columns

No generator existed anywhere in the repository. Every `.ps1`, `.py`, `.cs` and `.cjs` was searched. The workbook could not be rebuilt, could not be updated, and could not be regenerated if it corrupted.

And it was not merely a view of tracked data. Six of its seventeen columns — **System Family, Backrooms Dependency, Planned Use, Integration Approach, Compatibility Watch, Research Status** — existed in that one binary and **nowhere else in the repository**. Losing the file would have lost that work.

The eleven remaining columns did have a tracked home in `research/rimworld-server-mod-inventory.csv`, and all 294 rows were diffed against it across those eleven columns before anything was changed: **zero mismatches**. The data was sound. The container was not.

## What was built

### One fact, one home

| Source | Owns |
|---|---|
| `research/rimworld-server-mod-inventory.csv` | the eleven inventory and evidence columns. Referenced across the docs and by `audit-gate0.py`; **never rewritten by the generator.** |
| `research/mod-register-integration-fields-2026-09-29.csv` | the six analysis columns lifted out of the orphan workbook, keyed by load order and cross-checked against the inventory on extraction by both `ModID` and `ModName`. |
| `research/mod-register-overview-2026-09-29.csv` | the Overview's prose measures and source links. |

The family, stance and firmness tallies are deliberately **not stored anywhere**. They are counted from the rows on every build, which is the only way defect 3 cannot happen again.

### `tools/research/build-mod-register.py`

Builds **both** outputs from one pass over the same rows, so they cannot disagree with each other. Standard library only — the repository pins no Python packages, and `openpyxl` is not installed on the build machine. A build tool that needs an install is a build tool that stops working.

Four sheets, per the owner's selection:

| Sheet | What it is for |
|---|---|
| **Overview** | measures, the computed tallies, source links. |
| **Index** | seven narrow columns totalling about 143 width units, so it **fits one screen**. One line per mod: load order, name, family, stance, firmness, trace ids, and a link into that mod's card. Autofilter on all seven. |
| **Mod Register** | all seventeen columns, faithful to the original, with autofilter, header and first two columns frozen, and computed row heights. |
| **Mod Cards** | one vertical label/value block per mod, 104 units wide for the value. **Nothing is ever clipped here.** Each card links back to its Index row. |

### The HTML register, sheet by sheet

The same four views as tabs, and two things a spreadsheet could not offer:

| View | What it is for |
|---|---|
| **Overview** | measures, the computed tallies as coloured pills, and clickable source links. |
| **Index** | one line per mod with a **live search box over all seventeen columns of every row**, plus filter dropdowns for stance, firmness and system family, and a running "N of 294 mods shown" count. Clicking a row jumps to that mod's card. |
| **Full register** | all seventeen columns in a scrolling pane with a sticky header. |
| **Mod cards** | a definition list per mod. Nothing is clipped because nothing has a fixed height; the workshop URL is a link and the review record is monospaced. Each card links back to the index. |

Total 1.5 MB, one file, no external asset of any kind. The tab switch happens in script before the fragment scroll, because a hidden section has no layout to scroll within — which is the one thing in the page that is not obvious and is commented as such.

Two derived columns were added because the raw `FinalDisposition` strings take **104 distinct forms**, which is useless as a filter:

- **Stance** — what we do with the mod: Optional 243, Required 17, No integration 16, Configuration only 13, Visual only 3, Unclassified 2.
- **Firmness** — Provisional 200, Settled 94. This is the continue-forward axis: it says how much of the register is still undecided.

The two rows that stay Unclassified (2 SF Grim Reality, 196 RimWorld Together) genuinely do not fit a bucket, and leaving them visibly unclassified is better than forcing them into one.

**Row heights are a floor, not a ceiling.** The height is computed from the longest wrapped cell in the row using a deliberately pessimistic characters-per-line figure, and written **without `customHeight`** — so it renders correctly in a strict reader and Excel remains free to grow it further. That is the specific inversion of defect 2.

The archive is written with a fixed timestamp and sorted part order, so an unchanged source rebuilds **byte-identically** — the same determinism rule the mod assembly follows. Confirmed: two consecutive builds gave SHA-256 `3B3E7BAFBE02C0091C277A18E5B6EF70B993E3B6EA77788590D034E284B27B53`.

### One classification mistake, caught by looking at the output

The Stance buckets were first written with the no-integration phrases tested **above** "optional". That moved 59 mods reading *"optional support; no Rimrooms patch planned"* into **No integration** — the exact opposite of what those rows say. A mod we support without patching is not a mod we ignore. The order now tests "optional" first, with only the strong signals (`exclude`, `unrelated`, a disposition *starting* with "none") ranked above it, and the reason is written into the function so it is not "tidied" back later. The tell was a count jumping from 13 to 72 in one edit; reading the distribution after a classifier change is cheap and worth doing every time.

### `tools/research/check-mod-register.py`

The previous register could not be checked at all, because there was nothing to check it against. This reads every cell back out of the packaged workbook and proves four things:

1. **Round trip** — all 294 rows × 17 columns compared against the CSVs, plus every field of every card compared against the register grid. Anything the writer mangled, misescaped or put in the wrong column surfaces here.
2. **No formula-typed text** — asserts zero `t="str"` cells. Defect 1 cannot return.
3. **Nothing clipped** — asserts no row sets `customHeight`, and that every row's height clears its own longest wrapped cell. Defect 2 cannot return.
4. **The package is well formed** — every part parses, every relationship id resolves, every part has a content type, every style index exists, and every hyperlink and merge points at a cell that was actually written.

And for the HTML register, which matters more because it is the one that gets read: every mod has a card and an index link to it; every recorded value over eleven characters is present **through the same escaper that wrote it**, so a mangled ampersand or angle bracket fails; every filter offers exactly the values the rows contain; tags are balanced, checked with `html.parser` so HTML5 void elements are tolerated rather than demanding XHTML; and **no external asset is referenced**, because a register that needs the internet is a register that stops working.

It found a real bug on its first run — in itself, not the writer: `split_ref` returned `(column, row)` while the value map was keyed `(row, column)`, so every link and merge check failed. Worth recording because the failure mode looked exactly like a broken writer, and the XML had to be read by hand to tell the difference.

### Independent confirmation

`tools/research/audit-gate0.py` already read this workbook and compares **3,234 cells** of it against the inventory CSV. Its reader already handled `inlineStr`, so the rebuilt file passed it unchanged — an independent round-trip that was not written for this purpose.

That same run surfaced a **pre-existing failure** that had nothing to do with the register. `docs/TODO.md` line 79 carried a bare same-file fragment:

```markdown
see [the rule](#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side)
```

It had been copy-pasted from `CONNECTED_COLONY_PORTALS.md` line 104, where that heading actually lives, and the leading filename was lost. The audit had been returning `"result": "FAIL"` on it. Repointed at the real file; the audit now returns `"result": "PASS"` with zero errors.

Worth noting for anyone documenting a broken link in future: the audit's scanner strips fenced code blocks but **not** inline code spans, so quoting a bad link inline recreates it. That is why the example above is fenced.

## Superseded: the preview PNGs

`register-preview.png`, `register-door-check.png`, `register-health-check.png`, `register-security-check.png`, `register-wave10-1.png`, `register-wave10-2.png`, `rwt-row-preview.png` and `Overview.png` all depict the **old two-sheet layout**. They are not deleted here — they are tracked artifacts and removing somebody's evidence is their call, not this checkpoint's — but they should not be read as showing the current file. They are the reason the owner expected something the file never rendered, so leaving them unlabelled would repeat the confusion.

## Not done, and named

- **Re-rendering the previews** against the new layout. No spreadsheet application and no headless browser is installed, so no render can be produced honestly here. Correctness is instead proved structurally, by the round trips above.
- **Registering a `.xlsx` association, or installing a spreadsheet application.** Not done deliberately: changing file associations or installing software on the owner's machine is the owner's call, not a build step. The HTML register removes the need entirely. If the owner does want the workbook openable, installing LibreOffice would do it — the file itself is now verified correct.
- **A Markdown mirror of the register.** Not built: the three CSVs are already greppable, diffable and renderable in Forgejo, and a fourth copy of the same facts is a fourth thing to drift.

## Verification performed

- `tools/research/build-mod-register.py` then `--check`: 294 rows, 26 overview records, sources consistent.
- `tools/research/check-mod-register.py`: 294 × 17 round-tripped, 294 cards field-equal, 0 formula-typed cells, 0 pinned heights, 66 computed tallies.
- `tools/research/audit-gate0.py`: `"errors": []`, `"result": "PASS"`, 3,234 workbook cells compared, 294 review records resolved.
- Determinism: two consecutive builds, identical workbook SHA-256.
- HTML register: 294 cards, 294 index links, every value present and correctly escaped, all three filters complete, balanced nesting, zero external assets.
- `tools/build.ps1`: zero warnings, zero errors; assembly hash unchanged from 0.6.4-dev, as expected for a checkpoint with no C# change.

## For the post-completion test phase

**Open `Rimrooms_Async_Industries_294_Mod_Integration_Register.html` in a browser first** and confirm: all four tabs switch; the search box narrows the index as you type and the count follows it; the three filters combine with the search; clicking a mod jumps to its card and "back to index" returns; a card's longest evidence field reads in full; and the workshop URL opens the right Steam page.

Then, only if a spreadsheet application is ever installed, opening the workbook and confirming: the Index fits the screen without horizontal scrolling; a card shows its longest evidence field in full with no clipping; the Index link jumps to the right card and the card's link returns to the right Index row; the autofilter on Stance and Firmness selects the counts the Overview reports; and no repair prompt appears on open in any spreadsheet application the owner actually uses. That last one is the only claim here that structural verification cannot make, and it is recorded as a runtime row rather than asserted.
