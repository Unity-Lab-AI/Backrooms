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

## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔

**Owner, 2026-10-04, three times:** *"okay once again.. yu should be completeing like near a dozen items before you run the whole battery. i told you i can NOT be waiting 40 minutes when u run 10m batteries constantly with every item you work on"*, *"you have run batteries repeatily and you havent even done ten items yet"*, and when I over-corrected: *"no you fucking retard!!!! you still need to do instrament checks and build them when needed just dont run them for every fucking code change"*

- **During the work:** run **only the one instrument covering the file you just touched.** One checker, or one proof, or one plant suite. **Keep writing and extending them.**
- **At publication, once:** 18 checkers → 53 proofs → 27 plant suites.
- **If a sweep finds something, fix it and re-run ONLY the instrument that failed.**
- **Batch size is 10–12 closed rows.** 0.12.88 eight, 0.12.89 eleven, 0.12.90 **nine**.

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
| Version | **0.12.90-dev** — read from `About.xml`, never from a document |
| Build | **231 C# files, 103 package files**, zero warnings, zero errors |
| Dependencies | **ZERO declared.** `loadAfter` carries the 294-row profile and is checked against the register |
| Instruments | **18 checkers**, **53 proofs**, **27 plant suites** |
| Package art | **13 images, all accounted for**: 12 menu slides (the approved exception) + `About/Preview.png`. **No gameplay art, no audio** |
| Queue | **67 open · 21 partial · 38 `[T]` · 0 `[x]`** |
| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |

---

## What 0.12.90-dev changed

1. **CERTIFICATIONS AND TRAINING JOBS.** The person-level twin of a company project. Each one is an **ordinary bill** on a bench, modelled on `RR_AssembleMachineGate` — no new work giver, no new job driver, no new building. **Core enforces the skill floor** through `skillRequirements`, so no pawn can ever spend a day's work and be told no at the end.
2. **Three certifications, three named consumers, nothing hollow.** Spin-up dial, reviewer qualification, reconditioning work. **Security and medical logistics have none, deliberately** — no surface would act on one.
3. **Contain, release, transfer, destroy — and detain.** Four decisions about a recovered thing, plus the one that belongs to a person. **Containment charges every day on its own ledger line**; transfer pays **less** than the exchange, because taking less *is* the decision; destroy is **the only option that needs nothing**.
4. **Detain is Core's prisoner system**, not a second model. A few lines, because needs, recruitment, escape and the warden job all already exist.
5. **Confidence is derived and never stored.** A stored score could disagree with its own inputs. And it **moves what the corporation pays**, so it is not a readout.
6. **The generator can see four more things about the branch** — tier, previous outcome, opening duration, the world's hostility. **Bias, never a filter**, clamped both ways.
7. **"Term" is REFUSED, not built.** §1.1 forbids a countdown on anything the player maintains. Eviction is allowed because it is a **consequence of not paying**, visible on the ledger and cleared by paying; **no time passing ever evicts anybody.**
8. **Three rows closed on measurement.** The company book's blocker was solved by `companyIssued` at 0.12.87; gate size and what it lets through was fully built; equipment-versus-seed was held on one half and superseded on the other.

---

## THE NEXT THING

**The DLC-conditional content rows** (Royalty, Ideology, Biotech, Anomaly, Odyssey) are the
largest honest cluster left. Each says *no DLC-specific content is authored*, and each is gated
correctly already — so the work is authoring content that is **optional by construction**. The
Anomaly one is the nearest: its row names *containment/research links*, and containment now
exists to link to.

Then: **entity/anomaly design sheets as authored documents** (the last clause on that row);
**vehicles and the VGE hooks**; **the optional work/storage provider adapters**; **T3 of the
research tree**.

And the one the owner keeps naming: **the stand-alone guarantee half** — every
`GetNamedSilentFail` degrades, both `PatchOperation`s stay guarded, no Def assumes a DLC. The
`Fillable` guard on equipment roles and the *every-recipe-must-reach-a-real-worktable* finding are
that rule applied in two places; it belongs everywhere a defName is named.

---

## Read these before touching anything

- **A CLAIM READS ITS OWN DOCUMENTATION. THIS HAS NOW BITTEN THREE TIMES IN TWO BATCHES.** Good documentation explains the thing it avoids **by naming it** — so an absence claim fails on the comment that justifies it. `proof-tenure-and-disposition.py` now carries `code_only()` **and** `xml_only()`. Put every absence assertion through one of them.
- **`in` CANNOT TELL ONE SITE FROM THREE, and this is the recurring one.** A claim asserted the recipe worker class was `in` the file; three recipes carry it, a plant stripped one, two were left, MISSED. Same class as `RecallOptionTicks` last batch. **Count it.**
- **A POSITIONAL CLAIM ENCODES LAYOUT, NOT THE PROPERTY. Also recurring.** Comparing call indices was satisfied by a plant that moved the call **out of its block entirely**. The property was containment; assert it on whitespace-normalised source.
- **ONE PATTERN, ALL THE FILES IT GUARDS.** The clock-name check was strict on `RemoteSiteTenure.cs` and narrower on `RemoteSites.cs`, so an `expiryTick` in registration walked past. A clock is a clock whichever file grows it.
- **THE FIX FOR DEAD CODE IS TO REACH IT.**
- **THE BATTERY RUNS ONCE AND THE INSTRUMENTS STAY.** The only thing the owner has had to say three times.
- **THE CASCADE IS TEN REFS.** `forgejo, github` × `feature/connected-colony-portals, Prep, Develop, Main`, **plus `feature/bug-testing` on both**. `PUBLISHING.md`.
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

**The build is. The play is not.** `0.12.90-dev` is staged and published; the next action that unblocks anything is a launch, and only the owner launches.

Read a launch log in this order: `Player.log`, grep the **first** `[Rimrooms]` line — it carries
the fixture-tell attachment count, the fastest signal that the object register reached anything —
then `python .local/qa/bridge.py call rimworld/list_letters '{}'`.
