# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

So: **replace this file, never append to it.** Narrative goes to `FINALIZED.md`. A rule that must survive goes to `.claude/CONSTRAINTS.md` or becomes a checker. Open work goes to `docs/TODO.md`.

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, every owner direction verbatim, **open work only** |
| `docs/DECOMPOSED.md` | smallest execution units, **open only** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

---

## ⛔ FORGEJO IS BACK. THE CASCADE IS TEN REFS AGAIN ⛔

**Owner, 2026-10-05, verbatim:** *"okay read now.md to continue then first we need to make the
forgejo pushes, its back up and last cascade to forgejo was a while ago"*

It was back, and the first push attempted was the same one that had failed ten times. It was
accepted. Forgejo had been stuck at `2d0b677` (0.12.90-dev) for four commits; it is now at
`0c2712d` with GitHub, and **both remotes carry every commit.**

**So the cascade is ten refs, and the count is the trap `PUBLISHING.md` §5 warns about in its own
words.** Push **by refspec from the feature branch** — never by creating local
`Prep`/`Develop`/`Main` branches, which that file names as a way previous agents have already got
this wrong:

```
BRANCH=$(git rev-parse --abbrev-ref HEAD)      # never hard-code it
for r in forgejo github; do
  git push $r "$BRANCH"
  for b in Prep Develop Main feature/connected-colony-portals; do
    git push $r "$BRANCH:$b"
  done
done
git ls-remote --heads forgejo; git ls-remote --heads github; git rev-parse HEAD
```

**The outage and its root cause are recorded in `docs/FINALIZED.md`**, not here — this file holds
one record and that one is finished. Read it before investigating any future Forgejo refusal: the
answer was `tmp_objdir_create()` on the server, and nothing on this machine changed between the
last failure and the first success. **An outage is recorded, not re-investigated.**

---
## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04, three times:** *"okay once again.. yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes when u run 10m batteries constantly with every item you work on"*, *"you have run batteries repeatily and you havent even done ten items yet"*, and when I over-corrected: *"no you fucking retard!!!! you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the one instrument covering the file you just touched.** One checker, or one proof, or one plant suite. **Keep writing and extending them.**
- **At publication, once:** 19 checkers → 54 proofs → 28 plant suites.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.**
- **Batch size is 10–12 closed rows.** 0.12.90 nine, 0.12.91 six closed and six noted, 0.12.92 **four closed and five noted** — wrapped early on the owner's word, and the docs rows that stayed open are each waiting on something that is not code.

---

## ⛔ AND THE FIX FOR DEAD CODE IS TO REACH IT, NOT TO DELETE IT ⛔

**Owner, 2026-10-04, verbatim:** *"okay sounds like your deleting shit rather than fixing it by what you said,, that better not be the case"*

Kept here because it is the only correction the owner has had to make twice-over in spirit. I had
removed `RecordsAwaitingReview()` because wiring it would push a density ceiling **I had set
myself**. Wrong trade: **a ceiling I set is mine to manage, not a reason to delete a feature.** It
is wired and cost **zero** screen words — the count rode a string that already existed, which is
what the ceiling was pushing me to find.

---

## State, measured 2026-10-05

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.12.92-dev** — read from `About.xml`, never from a document |
| Build | **231 C# files, 103 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **19 checkers**, **54 proofs**, **28 plant suites**, **1035 plant anchors** |
| Package art | **13 images, all accounted for**: 12 menu slides (the approved exception) + `About/Preview.png`. **No gameplay art, no audio** |
| Queue | **58 open · 20 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |
| Remotes | **`0c2712d` on all TEN refs** — `forgejo` 5 of 5, `github` 5 of 5. Forgejo caught up 2026-10-05 after four commits down |

---

## What 0.12.92-dev changed

**A short batch, wrapped on the owner's word mid-flight.** Four rows closed, five noted, one
measurement that corrected a row.

1. **THE WIKI IS A SITE YOU CAN SCAN.** `jekyll-theme-primer` is gone — the row called it *"a text wall with a margin"* and it was. Our own layout and stylesheet: a persistent index on every page, a summary line at the top of each, a prose column near 68 characters, and headings that read as dividers. No webfont, no script, no external request, no theme gem.
2. **THE INDEX WRITES ITSELF.** `tools/build-site.py` generates `docs/_includes/nav.html` from the wiki directory. `--check` fails the battery when they disagree. **It caught a bug in itself before shipping** — `page.url contains '/wiki/'` is true of every page, so the index would have been marked current everywhere.
3. **All thirteen pages carry `title` and `summary` front matter**, so each says what it is before it says anything else.
4. **CNAME support authored, domain deliberately not named.** The shape, the DNS records and the verification are in `docs/CNAME.example`, inert on purpose: a live `CNAME` for a domain nobody owns stops Pages answering on `github.io` and waits for DNS that never arrives.
5. **Two gaps measured rather than claimed.** `check-doc-conformance.py` already covers every `.md`, so the wiki prose was never uncovered; what *is* uncovered is the site's **non-markdown** files — layout, include, stylesheet, `_config.yml`, a future `CNAME`.
6. **The research row was wrong about T3.** It is fully built, seven projects with their own header; T4 is built too, six of seven with both absences reasoned. **34 capabilities granted, 34 read — a perfect bijection.** What is open is T5/T6, and the file's own rule makes that a knob sweep.

---

## THE NEXT THING

**One small piece of work finishes the docs cluster**, and it is two rows at once: extend
`check-doc-conformance.py` to cover the site's **non-markdown** published files for version and
branch claims, **and** make it refuse a published copy of `TODO.html`/`NOW.html` so the ledger
guard is a guard rather than a comment. Both are in `docs/TODO.md` with the gap already measured.

Then the two deploy rows are **the owner's switches, not work**: Settings → Pages → `main` /
`/docs`, and a domain when you want one.

**T5 of the research tree is a knob sweep**, not an authoring job: 274 tunable constants exist and
34 are claimed by capabilities, so there is somewhere to look — but a tier may only exist where a
player could *name the effect*, and inventing seven projects without that is the lie the file
deletes projects for.

Then: **entity/anomaly design sheets as authored documents**; **vehicles and the VGE hooks**; **the
optional work/storage provider adapters**; and the four expansion rows, each of which needs a
decision about what the optional version of *genes*, *rituals* or *a gravship that carries a
branch* actually is.

**And the two starting-goods rows wait on a launch, not on code.** They are the only rows whose
next step is a `Player.log`.

---

## Read these before touching anything

- **A CLAIM READS ITS OWN DOCUMENTATION. THIS HAS NOW BITTEN THREE TIMES IN TWO BATCHES.** Good documentation explains the thing it avoids **by naming it** — so an absence claim fails on the comment that justifies it. `proof-tenure-and-disposition.py` now carries `code_only()` **and** `xml_only()`. Put every absence assertion through one of them.
- **`in` CANNOT TELL ONE SITE FROM THREE, and this is the recurring one.** A claim asserted the recipe worker class was `in` the file; three recipes carry it, a plant stripped one, two were left, MISSED. Same class as `RecallOptionTicks` last batch. **Count it.**
- **A POSITIONAL CLAIM ENCODES LAYOUT, NOT THE PROPERTY. Also recurring.** Comparing call indices was satisfied by a plant that moved the call **out of its block entirely**. The property was containment; assert it on whitespace-normalised source.
- **ONE PATTERN, ALL THE FILES IT GUARDS.** The clock-name check was strict on `RemoteSiteTenure.cs` and narrower on `RemoteSites.cs`, so an `expiryTick` in registration walked past. A clock is a clock whichever file grows it.
- **A MESSAGE IS NOT A RULE — and that cuts both ways.** A claim asserted a refusal's *message* rather than its condition, and a plant rewrote the message; the claim rightly passed and **the plant was testing nothing**. Assert the test; plant against the test.
- **A SLICE IS A CLAIM TOO.** One claim cut a method at its first `}` — an inline `{ return; }` guard — so it examined four lines and a planted failure sat safely below it. Slice to the next signature, not to the next brace.
- **A `catch` EXISTING IS NOT A `catch` SWALLOWING.** A planted `throw;` walked past a claim that only asserted the handler was there.
- **THE FIX FOR DEAD CODE IS TO REACH IT.**
- **THE BATTERY RUNS ONCE AND THE INSTRUMENTS STAY.** The only thing the owner has had to say three times.
- **THE CASCADE IS TEN REFS** — `forgejo` and `github` × `feature/bug-testing, feature/connected-colony-portals, Prep, Develop, Main`, pushed **by refspec from the feature branch**, never by creating local integration branches. It was five for two versions while the host was down and it is ten again. `PUBLISHING.md` is the authority; read it rather than improvising, which is the one thing the owner has corrected about publishing.
- **WRITING A FILE WITH THE WRONG ENCODING SILENTLY CHANGES IT.** Last batch the version bump stripped three BOMs and the changelog script added one. This batch the bump read with `utf-8-sig` and re-wrote the BOM it found; `git diff --stat` showed version lines only. **Always diff-stat after a scripted edit** — the line counts do not lie.
- **§1.1 IS THE RULE A NEW FEATURE IS MOST LIKELY TO BREAK WITHOUT NOTICING.** Every leasing system ever played has a term. The test that passes: does it read the gate's own window, is it off by default or driven by the player, and can it take anything away?
- **A BILL NEEDS A `Building_WorkTable`.** Core's research benches are `Building_ResearchBench` and have **no bill stack at all**, so a recipe placed on one is a feature nobody can ever reach. Nineteen Core worktables, enumerated from the installed data.
- **READ THE DEF NAME OUT OF THE INSTALLED GAME.** `TableLong` does not exist. Eight Core recipes ship with no `<ingredients>` element, which is how a pure-work recipe was confirmed as Core practice rather than guessed. `.local/tools/ilspycmd.exe` answers API questions the same way.
- **A PICKER AND ITS ACTION MUST AGREE.** Widening `ReviewerFor` for a certification without widening `ReviewAnalysis` would offer a reviewer the action then refuses — the gate's afternoon-costing defect in a different coat.
- **AN IDEMPOTENT LEDGER IS A RECORD.** `PostTransaction` returning `Existing()` meant the start-up payouts and the certifications needed **no new saved state at all**.
- **BANNED VOCABULARY.** *"portal"* → gate/connection; *"doorway"* → door/threshold; *"the machine"* is reserved. `check-info-cards.py` is the authority.
- **THE STAGER REFUSES A PACKAGE EDITED AFTER THE BUILD**, by hash. Rebuild, then stage.
- **A ROW CAN BE STALE, AND THREE WERE.** Measure before building. A row kept open *for the owner to overrule a call* should be re-read when the thing it was waiting on gets built.
- **The mod register is GUIDANCE.** `python tools/register-query.py use <trace>`. **`docs/CAMPAIGN_CHART.md`** beats any prep document.

---

## Findings recorded so nobody re-derives them

- **A row asking for something a LAW forbids is answered by saying so.** *Term* is refused and recorded in `RemoteSiteTenure.cs`, the way the chart records four prep documents' timed investigations as superseded. Building a smaller version of a forbidden thing is worse than not building it.
- **Derived beats stored whenever the inputs are already saved.** Confidence, the material palette, the fixture tell choice — all functions of saved state, so none of them needed a save migration and none can disagree with their own inputs.
- **A reversible cost needs a way out that pays nothing.** Containment charges for ever; destroying a contained record is free in both directions, which is what stops contain-then-cash beating the exchange.
- **`AvailableOnNow` is asked about the bench, not the pawn.** So a per-pawn condition on a bill cannot be a refusal; it has to be idempotence.
- **Core's `GuestStatus.Prisoner` is a whole feature for three lines.** Reach for Core's systems before modelling a second one.
- **A density ceiling is a prompt to write better, not a reason to cut a feature.** Three raises so far, all recorded, every one preceded by a genuine trim.

---

## The live bug that is NOT ours

```
ReflectionTypeLoadException getting types in assembly RimBridgeServer:
expected class 'HarmonyLib.CodeInstruction' in assembly '0Harmony, Version=2.4.2.0'
```

`RimBridgeServer.dll` wants **0Harmony 2.4.2.0**; `brrainz.harmony` ships **2.4.1.0**. Our package loaded clean in the same log. The fix is on the machine.

---

## The queue

```
grep -c '^\s*- \[ \]' docs/TODO.md     # open
grep -c '^\s*- \[~\]' docs/TODO.md    # partial
grep -c '^\s*- \[T\]' docs/TODO.md    # post-completion test phase
grep -c '^\s*- \[x\]' docs/TODO.md    # 0, and it must stay 0
```

```
python tools/archive-finished-todo.py --apply
python tools/verify-archive-move.py                                   # straight after, every time
python tools/check-queue-integrity.py                                 # and this, which the above cannot see
```

`STALE SNAPSHOT` exit **2** is distinct from `FAILED` exit 1 and `VERBATIM TRANSFER CONFIRMED` exit 0. The mover returns **3** for unarchivable prose after a closed row, and writes nothing.

---

## Is it done?

**The build is. The play is not.** `0.12.92-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line — it carries
the fixture-tell attachment count, the fastest signal that the object register reached anything —
then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
