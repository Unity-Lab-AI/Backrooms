# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

The [artwork handoff this replaces](implementation/evidence/authored-rotations-2026-10-06/) is preserved as dated evidence, as is the handoff before it. **Narrative goes to `FINALIZED.md`; a rule that must survive becomes a checker.**

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | **the test phase — 58 rows, and it is now guarded like the other three** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## ⛔ FIVE SHIPPED CUES HAD NO CONSUMER, AND EVERY INSTRUMENT WAS GREEN ⛔

**Owner, 2026-10-06:** *"okay now full wiki updates and checks of everything written in totality is accurate and uptodate and there is a asset gallery organizable just like the mod registry with their images listing there details"*

**`RR_AnalysisComplete`, `RR_ContractPaid`, `RR_CutoffThrown`, `RR_JournalFiled`, `RR_MarkerSet`** — the whole of `ASSET_REQUESTS.md`'s *"events that happen now and make no sound"* band. Delivered, measured, described on the published asset page, given `SoundDef`s, and **never played by one line of code.**

**This is the defect class that retired the 0.2.0 art**, and two instruments agreed it was fine:

- the asset page counted a cue as *named* because **a cue's own def names it**;
- `check-wiring.py` counted it as *wired* because **`SoundDef` sat in its core-consumed list** — and that list's own comment says *"a type added here without a reason is a hole in the check."*

All five are wired now, at the call sites the brief itself names.

**IT TOOK THREE FIXES TO MAKE ONE RULE REAL, AND THE PLANT FOUND THE SECOND AND THIRD.** After removing `SoundDef` from the list the plant stayed green, twice:

1. Rule 3 asked whether a name appears *"somewhere OTHER than its own declaration"* and implemented that as a **global count > 1**. Every cue's block names itself twice — `<defName>` and the `<clipPath>` of the identically-named file — so **each cue cross-referenced itself.** Now counted against the def's own body, which closes it for every def type rather than for cues.
2. `enumerated` matched `DefDatabase<T>` **anywhere**, so `DefDatabase<SoundDef>.GetNamedSilentFail` counted as *this type is enumerated*. A by-name lookup on a variable proves the opposite of what it was read as. Restricted to `AllDefs`, and the count of enumerated types fell from **33 claimed to 19 real.**

**Suite 44 is `plant-cue-consumer`, 2 of 2.** Three further plants were written for the loopholes themselves and **deleted**: loosening a rule on a tree where every cue is wired fails nothing, so they asserted something untrue. The two cue plants already guard all three — reopen any loophole and they turn MISSED.

---

## ⛔ TWO DEFECTS IN MY OWN WORK FROM THE PREVIOUS BATCH ⛔

**The aura and the animations read neither accessibility setting.** `PortalAuraEnabled` and `PortalReducedMotion` were honoured only in the older fleck effect, whose docstring promises *"a player who turned the effect off gets a plainly tinted door and nothing moving."*

**That promise broke the moment the new aura shipped.** A player who had already switched it off would have watched the flecks stop and **a new strobing light appear**, plus three new animated sequences. The worst possible answer to an accessibility preference.

**The shipped label settled the shape, and my first fix had it wrong.** `RR_NativeGate_ReducedMotion` reads *"Reduce gate motion (hide aura; keep status text)"* — it promises the aura is **hidden**, so holding each state's colour and merely stopping the pulse was not the promise being kept. Both settings now return the glower to exactly what it did before that file existed. The compensation is already built: every state has a message, a pane indicator or both.

**What neither setting offers is colour without motion.** Said here rather than quietly invented — a third option is a new shipped setting and a new label, which is the owner's call.

---

## ⛔ THE GALLERY'S PICTURES WERE BROKEN WHERE THEY WERE BEING READ ⛔

**Owner, 2026-10-06:** *"okay but im not seeing the pictures of the assets in the wiki with theri right up details and how the are used in game play"*

**They were not there to see.** One relative path has to resolve from two different layouts and only one was ever served:

| Layout | `assets/art/gallery/X.png` resolves to | Was it there |
|---|---|---|
| Published site, **flat** — `docs/wiki/assets.md` → `docs/assets.html` | `docs/assets/art/gallery/` | **yes**, the exporter writes it |
| Repository, **nested** — read at `docs/wiki/assets.md` | `docs/wiki/assets/art/gallery/` | **no such directory** |

The gallery was built for the published site and never for the tree the owner actually reads. The 52 pictures are written to **both** locations now, and it was **verified by resolving all 52 references against disk** rather than by looking at the page: 52 referenced, 0 missing.

**`--check` passed the whole time, because it compared the markdown with itself and nothing else.** It now fails when a referenced picture is absent or a leftover one remains — proved by holding one back and reading the failure.

**And adding 52 PNGs under `docs/` crashed `check-doc-conformance` outright**, because it read every published non-markdown file as text while its own docstring said *"Binary files are never read."* That claim was true only because no binary had ever been published there.

**A *How you use it* column, 69 of 69 written.** *What it is* describes the drawing, *In game* names the def that loads it, and **neither says what a player does with the thing.**

One asset was also mis-categorised as a *Building*: `RR_MachineGate` is **no longer a buildable** — that def was retired, and the texture is now only the Set Gate button's icon — but it still sits under `Things/Building/`, so the folder decided its category and invited a reader to look for it in the build menu.

---

## The asset gallery

**One table, 69 rows, 52 pictures, nine columns, sortable and searchable.**

***"Just like the mod registry"* decided the shape twice over.** One full list rather than six grouped tables is the correction the owner already made to the register page. It is also the **only** way the page becomes organizable: the search box and sortable headings attach to **any table with at least twenty body rows**, by size rather than by a flag. Six tables of twelve, thirty-four, six, one and seventeen got the tooling on exactly one of them.

| | |
|---|---|
| Renderer | **It could not show an image at all.** No page had ever used one. Images are tried before links, or the link rule eats `[alt](src)` and leaves a bare `!` |
| Escape paths | An image source is deliberately **not** passed through `rewrite_target`, which carries `..` through intact so the export's guard can refuse a page that climbs out of the site |
| Transparency | **Checkerboarded behind every picture.** Most of these textures are mostly transparent — a gate frame is an outline around a hole — and on a flat background the thing the reader came to check reads as an empty cell |
| Weight | Fifteen oversized originals resampled to 192 px, everything at or below 256 px copied untouched. **1.3 MB for the whole gallery** |
| Pillow absent | Full-size copies at the same paths, with a note. The markup and the image guard are identical either way |

---

## The wiki, in totality

All sixteen pages read end to end. The two worst gaps were **features the owner asked for that the wiki never mentioned**.

| Page | What was wrong |
|---|---|
| `gates.md` | Said a gate was *"blue, with a blue glow"*. **No mention of the five state colours, the three animation sequences, or the gate's voice.** Now has all three plus a table of what each switch turns off |
| `interface.md` | **Claimed accessibility and named none of the seven settings that implement it** |
| `credits.md` | *"the four company sound cues"*. Seventeen ship |
| The mod's own settings | *"Existing game sound cues accompany gate and field events"* — **a player-facing string still describing the world before the reversal** |
| `CAMPAIGN_CHART.md` | *"Six tiers"*, directly above its own seven-row table and its own seven-band summary |
| `company.md` | Insight buys unlocks across *"nine branches"* while one of the nine deliberately ships nothing — and it contradicted itself two paragraphs later with *"five branches reach it and three do not"* |
| `build-site.py` | Still called the twelve slides *"the only art in the package"*. **83 textures and 17 cues ship** |
| Two player-facing pages | Used the banned word for a thing running out — `company.md` and `troubleshooting.md`, both while *denying* that anything does. The archive records that word as **reworded rather than exempted** the last time it came up, and an earlier draft of this very file was refused for it |
| `asset-descriptions.json` | A mojibaked em dash, being published |

---

## RimSort was named in no public-facing file

**Owner, 2026-10-06:** *"and make sure the right locations suggest the sorter we use Rimsort with links and shit that we use with the instructions on setup in the wiki"*

Measured before anything was written: **zero mentions across all sixteen wiki pages, the README and `WHATS_NEW.md`** — while **two of this project's own instruments depend on it by name.** `stage-mod.ps1` stages into RimSort's local mods folder, and `check-package-integrity` reads RimSort's `settings.json` to prove the staged copy is the build. *The thing the whole publication loop runs on was a secret from the reader.*

Six locations name it now: `install.md` with its own section, `mods.md`, `index.md`, `links.md`, `troubleshooting.md`, and **`About.xml`** — the player-facing description a mod manager itself displays, which said *"how to set up your mod manager"*.

**The generic sentence is kept wherever it is still true.** Any manager that reads a declared load order does the same job and the game's own mod list works, so naming the one in use must not read as a requirement this mod does not have.

**The setup instructions are built around the four folders, not around buttons.** Locations are what a reader has to get right and they do not change between releases; exact labels do, and inventing one publishes a wrong instruction. **The config folder is called out** as the only one of the four a sort writes to — a wrong one is the shape of *"I sorted and nothing happened"*, now its own troubleshooting entry.

---

## ⛔ THE TEST LEDGER WAS THE ONE TIER WITH NO GUARD ⛔

**Owner, 2026-10-06:** *"so are you ready to start mass chacking off (T) test items as we do them?"*

**The answer was no until three things were fixed, and the first is the one that mattered.** `check-queue-integrity.py` listed three queues. `docs/TEST.md` was created on 2026-10-06 and **never added**, so **none of its four rules could fire on the rows about to be worked through** — a row closed as `[x]` would have sat there indefinitely, and a section with no marker was invisible to every count. That is the exact defect rule 4 was written for after it happened to `TODO.md` hours earlier.

**Added, and it failed immediately with five findings.**

**One was an empty heading that had been there since the file was born** — *"a prisoner IS allowed to cross a gate"*, its verbatim body and closure record already in `FINALIZED.md`. A heading reading as outstanding test work over nothing. **The archiver's own sweep could never have cleaned it:** it swept a heading only when something in its body was moving *in that run*, so it could clean a heading it had just emptied and never one emptied in an earlier batch.

**AND THE FIRST FIX FOR THAT WAS WRONG AND WAS APPLIED BEFORE BEING READ.** Measuring the body to the next *anchor* counted a `**...:**` lead-in as the end of the section, so **four headings were swept away from their own content**, leaving the owner's verbatim quotes under nothing — the stranded-body defect the sweep exists to prevent, caused by the sweep, in one run. **The reassembly identity held throughout**, which is exactly why it could not see it: *where a line goes is not what that proof proves.* Caught by reading the diff, reverted, re-fixed to measure to the next heading.

**The remaining four sections were a real fork and went to the owner**, who answered ***"All four get [T] rows"***. So the ledger is **58 rows**, each with what to look for, and **two of them say on themselves that they are confirmed by reading rather than by launching** — the file's header claimed *"every row needs a launch"* and no longer overstates it.

**AND THE MOVER NOW HAS AN INSTRUMENT, WHICH IS WHY ANY OF THAT WAS POSSIBLE.** `archive-finished-todo.py` is the tool the LAW names as the proof of verbatim transfer and it had **no plant suite and no proof of its own** — so a wrong fix to it reached a real ledger. Proof 65 and suite 45 ask the question directly against crafted input: *does the sweep give a heading and its body the same label?* The two guards that look closest both pass on the defect — the reassembly identity holds because every line is still either kept or moved, and rule 1 looks for an **indented** continuation while an orphaned paragraph is not indented. A third plant was written and **deleted** for asserting something untrue, the same answer three loophole plants got an hour earlier.

---

## State, measured 2026-10-06

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.13.0-dev** — read from `About.xml`, never from a document |
| Instruments | **33 checkers · 65 proofs · 45 plant suites**, all three batteries run to completion |
| Plant anchors | **1335 findable**, no residue. One anchor re-aimed where `copy_site_art` grew the gallery |
| Gallery | **52 pictures in two places**, and every one of the 52 references resolved against disk from `docs/wiki/` |
| Build | **0 warnings, 0 errors, 200 package files** |
| Queue | `TODO.md` **0 open · 0 partial · 0 `[x]`**, `## Pending` empty rather than quietly occupied · `TEST.md` **58 `[T]`** |
| Assets | **99 files → 69 entries: 52 drawings, 17 cues.** Every one named by something, every one described, 59 with a master and the other ten menu backgrounds, which have nothing to cut |
| Staging | `check-package-integrity` reads **PASS** — *"staged copy matches the build at 0.13.0-dev, every file compared by content"* |

---

## ⛔ NEVER RUN THE PLANT SUITES WHILE ANOTHER AGENT IS WRITING ⛔

A suite writes a **real fault into a real file**, runs a verifier, then restores the file from its own copy. Anything written inside that window is **silently reverted**. The battery takes over ten minutes; nothing may be edited while it runs, including by this agent.

**And a plant that cannot trust the tree refuses instead of lying.** `plant-class-resolution` aborts with *"ABORTED: check-package-integrity.py does not pass clean"* rather than reporting faults that are really a half-delivered package. That abort is the behaviour to keep.

---

## ⛔ A NATURAL GATE STAYS A PLAIN DOOR ⛔

**Owner, 2026-10-06:** *"natural gates dont look like the machine in the real univiverse of backrooms they are mainly just normal doors and walls that u can majicly walk through but lets keep natural doors just normal doors in game so there is distinction for it"*

The frame draws on `CompRimroomsGate` and keys on `IsDesignated`. A permanent natural gate is `CompRimroomsEmergence` and gets nothing. **That asymmetry is the information:** a framed opening was built, an unframed one was found. Recorded in `GateWorldFrames.cs` where anybody tempted to "fix" it would be standing, and in `gates.md` where a player reads it.

---

## ⛔ ONE HOLD LEFT ⛔

**THE FORGEJO HOLD STANDS.** *"the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"*. **Six refs**: `github` × five branches, plus `github/main` on the mod-only repository. The remote is **held, not removed**, and the exporter prints the hold and its reason every run.

**Local `Main`, `Develop`, `Prep` and `feature/connected-colony-portals` sit behind their remotes**, because the cascade pushes this branch's HEAD to each remote ref rather than checking each branch out. The remote refs are the published record. Said here so nobody reads `git branch -v` and concludes the cascade failed.

---

## ⛔ STAGE BEFORE THE OWNER LAUNCHES ⛔

- `powershell -File tools/stage-mod.ps1 -UpdateExisting` — **the staged copy is the copy a launch loads.**
- `python tools/check-package-integrity.py` must read **PASS** before any launch report is trusted. It compares every staged file by content: *the version is a label; the bytes are what runs.*
- **Re-stage after any build.** Two of this batch's failures were the staged copy going stale behind an edit made after staging.

---

## Read these before touching anything

- **CONTENT WITH NO CONSUMER IS THIS PROJECT'S MOST EXPENSIVE DEFECT, AND IT HAS NOW HAPPENED TO ART, TO DEFS AND TO AUDIO.** Ask what *plays* a cue, not what declares it.
- **A RULE SATISFIED BY ITS SUBJECT NOT BEING THERE IS NOT A RULE** — and a rule can be satisfied three different ways at once. Only the plant proved which.
- **A PLANT THAT STAYS GREEN AFTER A FIX IS TELLING YOU THE FIX WAS INCOMPLETE.** Twice in this batch.
- **A SETTING'S SHIPPED LABEL IS THE CONTRACT.** *"hide aura"* means hidden, not dimmer.
- **ALL GREEN IS NOT THE SAME CLAIM AS ALL TRUE.**
- **A NUMBER COPIED BETWEEN DOCUMENTS IS HOW BOTH BECOME WRONG.** Ask the generator. Files and entries are different numbers and the page states both.
- **A NUMBERED SEQUENCE IS NAMED BY ITS PREFIX.** Both instruments know this now; for months only one did.
- **A `SoundDef` HAS NO LABEL.** Walking back for one found an unrelated def's.
- **A FOLDER SCAN NAMES EVERY FILE IN IT.**
- **MEASURE, THEN PUBLISH.** A seam metric scored a provably seamless tile at 7.15 and a figure ten times too large was published before it was checked.
- **A DROP SHADOW IS NOT THE OBJECT.**
- **THE COMPONENT IS THE ALLOWLIST.**
- **A GENERATED PAGE CAN BE "UP TO DATE" AND STILL BROKEN.** A check that compares a document with itself says nothing about the files it points at. Resolve the references against disk.
- **AN INSTRUMENT THAT CRASHES CANNOT REPORT**, and a docstring claiming a property is not the property. *"Binary files are never read"* was written above code that read everything.
- **USE THE WRITE TOOL FOR SCRIPTS, NEVER A BASH HEREDOC.** Broken **three** times in this session and corrected each time. It is the most repeated personal lapse in this handoff's history; the rule is recorded and still gets broken under time pressure.
- **MIND THE DEPTH WHEN A SCRIPT MOVES.** A `dirname` short by one level reads somebody else's files.
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved. **Nothing in this mod ever runs out, and the word for that is banned too** — even in a sentence denying it, which `check-campaign-absolutes` enforces and which refused an earlier draft of this very line. **Reword; never widen the rule.**

---

## THE NEXT THING

**A launch.** `TODO.md` is empty, every battery has run to completion against this tree, the staged copy is this build byte for byte, and the published gallery shows every asset the package ships.

**The 58 rows in `TEST.md` almost all need the game running — the owner alone launches, sorts and publishes.**

**Read a launch log in this order:** `Player.log`, grep the **first** `[Rimrooms]` line, then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.

## Is it done?

**No.** `PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`, the master TODO, still carries unticked scope nobody has reconciled against what now ships. Read it rather than trusting a count from any handoff, this one included. **An empty minor queue never meant a finished mod** — and this batch is the proof: the queue was empty while five shipped cues had never once played.
