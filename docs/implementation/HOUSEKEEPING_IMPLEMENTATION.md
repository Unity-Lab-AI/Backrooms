# The housekeeping, which was not housekeeping — 0.12.42-dev

**Rows 206, 302, 1054, 1268, 1269 and 1286–1290.** The last four entries in the queue, and every
one of them turned out to be about something being **true** rather than about tidying.

**This closes the build.** What remains is the ~8 rows that cannot close before the game runs once
and the 9 the owner excluded.

## The queue rows, verbatim

> *"make sure we are foillowing all rimworld and steam TOS and requirments"* … *"and the like"* —
> **"One compliance test, applied to all of them."** (rows 1286, 1289)

> *"Consequence: reconcile 0.5.0–0.7.1 back into the master backlog. … Until this is reconciled
> the master row count understates the build by roughly thirty points."* (row 1054)

> *"When it is addressed it should get the same treatment — tracked source, a generator, and an
> HTML output."* (row 1268)

## Rows 206 and 302 — the register retro sweep's last seven families

**The seven names collapse into five family strings**, because the register groups two or three
names per family: *Materials, cargo and recovered resources*; *Medical, biological and recovery
systems*; *World operations, contracts and commerce*; *Hospitality and visitor economy*; *Staff
psychology, relationships and faction standing*.

**Every one was already honoured, and no code changed.** That is the honest result and it is worth
stating plainly rather than dressed up.

What *did* change: **four of the rules were true only because of the current shape of the
package**, and a rule with no check behind it is a promise. So `check-register-compliance.py`
gained them, each quoted from the family's own Integration Approach with the row it came from:

| Rule | Source |
|---|---|
| no patch may name a `ThoughtDef` | row 2 SF Grim Reality — *"keep any future company thoughts isolated and additive; do not overwrite its thought definitions"* |
| no patch may name a `TraderKindDef` | row 17 [KV] Call Trade Ships — *"leave calls and trader options on the existing Comms Console; no Rimrooms trade-ship override planned"* |
| no patch may name a `HediffDef` | the medical family, rows 23–272 — *"the core expedition loop must not require one medical or Biotech mod to treat a pawn"* |
| no patch may name a `MainButtonDef` | the hospitality family, rows 62–286 — test state changes *"instead of replacing their native menus"* |
| no patch may alter another def's stat bases | the materials family, rows 52–228 — *"preserve each mod's normal material and weight behavior"* |

### The finding worth keeping

**The medical family's rule is that the expedition loop must not require one medical mod, and
0.12.41-dev came within one decision of breaking it.**

The crew planner reports a crew with no medical skill as a **gap** and does not refuse the
dispatch. Had that gap been written as a refusal — which is the obvious way to write it — the
expedition loop would have required a medic, and on a profile where a medical mod owns treatment
that is a requirement on that mod. It was written as advisory for a different reason, and **the
register independently requires it.** The proof asserts it stays advisory.

That is the second time this session the register changed what the right build was. The first was
row 821, where the hospitality family's *"instead of replacing their native menus"* agreed with the
row's own challenge to itself.

## Rows 1286–1290 — one compliance test, applied to all of them

`docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md` held the position as a thirteen-row table with a *"how
it was checked"* column, and its own closing section said: *"Everything in the verified table is
mechanically checkable, so it is re-run rather than trusted."*

**It was never re-run.** Verified at **0.5.6-dev**, read as current for **thirty-six
checkpoints**, and over those checkpoints **three of its rows stopped being true**:

* it enumerated *"all 18 non-XML package files … 14 historical `RR_` gameplay PNGs"* and *"the
  76-entry approved package list"*. The package is **89** files and **those fourteen PNGs were
  deleted at 0.12.22-dev.**
* it stated *"zero references to Royalty, Ideology, Biotech, Anomaly or Odyssey in any package
  XML"*. There are **six**, all `MayRequire`, which is the official mechanism — so the correct
  rule was never *no references* but *no ungated reference*.
* it stated the `ModsConfig` grep gave *"1 result"*. There are **five**.

**A dated table of mechanical checks is the same defect as a dated count.** So the table is now
executable: `tools/check-compliance.py`, the **thirteenth checker**.

It refuses a destructive patch operation, a bundled game binary, Harmony, a detour framework, a
reflection write into a game type, a non-public field read by reflection, a shipped file sitting at
a texture path that is not ours, AI attribution in anything shipped, the QA overlay inside the
package, and a reference to an assembly outside the official install. Three rules are **delegated**
and named in the report — hard dependencies to `check-register-compliance.py`, DLC gating to
`check-dlc-gating.py`, and what the package may contain to `tools/package-files.json` — because a
second copy of a rule is a second thing that can disagree with it.

**Exit 2 means skipped, and skipped is not a pass.** Same distinction `check-def-fields.py` makes,
for the same reason.

### Three of its own rules caught it first

**The licence check flagged a comment that denies the GPL applies.** `ConnectedFoodAdapter.cs`
says Gastronomy has *"unresolved rights … so its code and art must not be adapted and no adapter is
built"* — which is the sentence the rule wants the code to contain. Testing for **mention** fails
exactly the files that document their own compliance; it now tests for **assertion**, with a
negator list documented as maintained rather than complete. The same trap `disposition_stance()`
fell into and the same one the row 791 claim guard was widened to avoid.

**The assembly check read the wrong manifest key and reported a pass.** The manifest's key is
`References`; the code read `references`. Result: a confident `ok: references 0 assemblies, all
from the official install`. **A compliance check that finds nothing and says ok is worse than no
check** — it is the exact false-pass shape this file was written to remove. Keys are matched
case-insensitively now and **zero parsed references fails rather than passing.**

**The licence check passed a plant that replaced the licence outright.** `"MIT" in text` was
satisfied by the word **LIMITED** in the MIT boilerplate. It tests for `"MIT License"` now. Found
by a plant, which is the only way that ever gets found.

## Rows 1268 and 1269 — the workbook five documents linked and nobody could read

**"Unopenable" was about Excel, not about the bytes.** An xlsx is a zip of XML and the standard
library reads both — the same realisation that made the register queryable (*the HTML is the
register*), applied to the other workbook. `Rimrooms_Campaign_Economy_v0.2.xlsx` transcribes to
**five sheets and 381 rows**, and it is linked from `CAMPAIGN_ECONOMY_MODEL.md`,
`CAMPAIGN_ECONOMY_PROGRESSION.md`, `CAMPAIGN_ROSTER_FREEZE.md`, `FEATURE_TRACEABILITY.md` and
`AI_BUILD_HANDOFF.md`.

It got exactly the treatment the row asks for:

* **tracked source** — `docs/research/campaign-economy-workbook.json`
* **a generator** — `tools/extract-economy-workbook.py`, with a `--check` mode that re-reads the
  xlsx and refuses a source that has drifted
* **an HTML output** — `outputs/readable/campaign-economy.html`

**Not one number was touched.** The row is explicit that this is *"a different dataset with
different owners"* whose *"content has not been verified"*, so the transcription is exact and both
the source and the page state at the top that the figures are transcribed rather than verified and
that nothing has been observed in play. **A generator that silently corrected a figure would
destroy the only useful property the file has: being what its author wrote.**

Two subtleties the reader has to get right. **Shared strings**: xlsx stores repeated text once and
cells reference it by index, so a reader that ignored `sharedStrings.xml` would print integers
where the labels are. **Sheet order**: names live in `workbook.xml` and the files they map to live
in the rels, so reading worksheets in filename order guesses wrong the moment a sheet is inserted
rather than appended.

### Row 1269 — the superseded PNGs

The row says removing them *"is the owner's call"*, so **nothing was deleted.** A `README.md` sits
beside them naming which file is authoritative. The images are **wrong rather than merely old**:
they show **two** sheets, while the register parses **295 rows** out of its HTML and the companion
workbook transcribes to **five** sheets. An image of a two-sheet layout is a view of a different
file.

## Row 1054 — the master backlog, and the row underestimated itself

It predicted the count *"understates the build by roughly thirty points"*.

**It was 56.** The master backlog went from **122 open / 134 done** to **66 open / 190 done**, and
every flip names the checkpoint that closed it — the cross-map work engine row this row was written
about, the escalation ladder, the gate state machine, the transaction service, all three starts,
the existing-content replacement, the room library, the economy and evidence systems, research
tiers 0–3, containment, the vehicle and VGE hooks, and the RWT detection.

**Two rules were obeyed without exception, and the proof asserts both.**

**Every original word of every row was kept** and the note appended after it. Marking a task done
changes the status *only*; that is a LAW and it is what makes the backlog worth reading.

**No runtime-acceptance row was flipped.** No game has ever been launched from this repository, and
marking those accepted would erase the only honest caveat this project has. They remain open and
visible, which is the point of them.

## The proof, and what the plants found

`.local/register/proof-housekeeping.py` — **thirty-ninth proof**.
`.local/register/plant-housekeeping.py` plants **41 faults across three targets** and all 41 are
caught. The compliance checker is planted with a **real** destructive patch operation, a **real**
reflection write, **real** AI attribution in a **real** shipped file, and a **real** patch naming
each steered def type.

**The first three sweeps caught 37, then 35, then 40.** Every miss was one of two shapes, and both
are now old news in this session:

**A claim that a rule EXISTS is not a claim that it RUNS.** `DESTRUCTIVE = (` survives
`if False and destructive:` completely untouched. Four claims passed against exactly that plant.
Each now asserts the definition **and** the branch that acts on it.

**The harness replaces the FIRST occurrence, so a plant on a string that appears twice leaves the
second one satisfying the check.** `MIT` appears twice in the licence file, `SWEPT 0.12.42-dev`
twice in the queue, `check-dlc-gating.py` twice in the checker — once in its own docstring — and
`RECONCILED 0.12.42-dev` **fifty-six** times, so a count claim could not possibly see one go
missing. **A plant is only a test if it removes the last thing the claim can see.**

And one plant was simply not code: a reflection write planted as a `//` comment, against a checker
that strips comments before reading. The plant was wrong, not the rule.

## Build

**196 C# files, 89 package files**, zero warnings, zero errors. Assembly SHA-256
`CFAB1B96356D0F7BD7B40A19C22951E577E4597B2ADAFCD56A706F24A3244582`, reproduced by two clean
recompiles. **Thirteen checkers pass, thirty-nine proofs hold**, all read by exit status.

No game was launched. Nothing in this batch has been played.
