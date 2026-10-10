# -*- coding: utf-8 -*-
"""Append the 0.12.42-dev entry to FINALIZED.md. Appends only; nothing existing is touched."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "FINALIZED.md")

ENTRY = u"""

---

## 0.12.42-dev — the housekeeping, which was not housekeeping. THE BUILD IS DONE

**Rows 206, 302, 1054, 1268, 1269 and 1286–1290.** Owner direction for the run, verbatim:

> *"get to all of that"*

**Every queue row that can close without the game running is now closed.** What remains is the
~8 rows that need a first launch and the 9 the owner excluded. Row 1289's own words asked for the
shape of this whole pass: *"one compliance test, applied to all of them."*

**The register's last seven families collapse into five family strings**, because the register
groups two or three names per family. **Every one was already honoured and no code changed** —
the honest result, stated plainly. What changed is that **four of the rules were true only because
of the current shape of the package**, and a rule with no check behind it is a promise. So
`check-register-compliance.py` gained them, each quoted from the family's own Integration Approach
with its row: no patch may name a `ThoughtDef` (row 2), a `TraderKindDef` (row 17), a `HediffDef`
(the medical family) or a `MainButtonDef` (the hospitality family), and no patch may alter another
def's stat bases (the materials family).

**The medical family's rule is that the expedition loop must not require one medical mod, and
0.12.41-dev came within one decision of breaking it.** The crew planner reports a crew with no
medical skill as a **gap** and does not refuse the dispatch. Had that gap been a refusal — the
obvious way to write it — the loop would have required a medic, and on a profile where a medical
mod owns treatment that is a requirement on that mod. It was advisory for a different reason, and
**the register independently requires it.** The proof asserts it stays advisory. That is the second
time this session the register decided what the right build was; the first was row 821.

**The compliance table said it was re-run rather than trusted, and was never re-run.** Verified at
**0.5.6-dev**, read as current for **thirty-six checkpoints**, and over those checkpoints **three
of its rows stopped being true**: it enumerated 76 approved files and fourteen gameplay PNGs that
were deleted at 0.12.22-dev (89 files now, and those PNGs are gone); it stated **zero** DLC
references in package XML when there are **six**, all `MayRequire`, which is the official
mechanism — so the correct rule was never *no references* but *no ungated reference*; and it said
the `ModsConfig` grep gave one result when it gives five.

**A dated table of mechanical checks is the same defect as a dated count.** So it is executable
now: `tools/check-compliance.py`, the **thirteenth checker**. It refuses a destructive patch
operation, a bundled game binary, Harmony, a detour framework, a reflection write into a game
type, a non-public field read, a shipped file at a texture path that is not ours, AI attribution in
anything shipped, the QA overlay inside the package, and a reference to an assembly outside the
official install. Three rules are **delegated** and named in the report, because a second copy of a
rule is a second thing that can disagree with it. **Exit 2 means skipped, and skipped is not a
pass.**

**Three of its own rules caught it before any plant did.** The licence check flagged
`ConnectedFoodAdapter.cs`, whose comment says Gastronomy's rights are unresolved *so its code must
not be adapted* — the sentence the rule wants the code to contain — so it tests for **assertion**
rather than mention. The assembly check read the wrong manifest key (`references` against the
manifest's `References`) and reported *"ok: references 0 assemblies, all from the official
install"*: **a compliance check that finds nothing and says ok is worse than no check**, so zero
parsed references now fails. And `"MIT" in text` was satisfied by the word **LIMITED** in the MIT
boilerplate, so a plant that replaced the licence outright passed; it tests for `"MIT License"`
now.

**"Unopenable" was about Excel, not about the bytes.** An xlsx is a zip of XML and the standard
library reads both — the realisation that made the register queryable, applied to the other
workbook. `Rimrooms_Campaign_Economy_v0.2.xlsx` is linked from **five documents** and nobody in
this repository could read it; it transcribes to **five sheets and 381 rows**. It got exactly the
treatment row 1268 asks for: tracked source at `docs/research/campaign-economy-workbook.json`, a
generator with a `--check` mode that refuses a source that has drifted, and an HTML output.
**Not one number was touched** — the row is explicit that the content is unverified, and a
generator that silently corrected a figure would destroy the only useful property the file has:
being what its author wrote.

**Nothing in the register outputs folder was deleted.** Row 1269 says removing the superseded PNGs
is the owner's call, so a `README.md` sits beside them naming which file is authoritative. The
images are **wrong rather than old**: they show two sheets, while the register parses 295 rows out
of its HTML and the companion workbook has five sheets.

**Row 1054 predicted the master backlog understated the build by roughly thirty points. It was
56.** `PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` went from **122 open / 134 done** to **66 open /
190 done**, every flip naming the checkpoint that closed it. **Two rules were obeyed without
exception and the proof asserts both:** every original word of every row was kept and the note
appended after it — marking a task done changes the status *only* — and **no runtime-acceptance
row was flipped**, because no game has ever been launched from this repository and marking those
accepted would erase the only honest caveat this project has.

**41 of 41 planted faults caught**, against a baseline verified first. **The first three sweeps
caught 37, then 35, then 40**, and every miss was one of two shapes. **A claim that a rule EXISTS
is not a claim that it RUNS** — `DESTRUCTIVE = (` survives `if False and destructive:` untouched,
and four claims passed against exactly that. **And the harness replaces the first occurrence, so a
plant on a string that appears twice leaves the second satisfying the check** — `MIT` twice in the
licence, `SWEPT 0.12.42-dev` twice in the queue, `check-dlc-gating.py` twice in the checker, and
`RECONCILED 0.12.42-dev` **fifty-six** times, which no count claim could see one of going missing.
**A plant is only a test if it removes the last thing the claim can see.**

**196 C# files, 89 package files**, zero warnings, zero errors — no C# was added this checkpoint.
Assembly SHA-256 `CFAB1B96356D0F7BD7B40A19C22951E577E4597B2ADAFCD56A706F24A3244582`, reproduced by
two clean recompiles. **Thirteen checkers pass, thirty-nine proofs hold**, all read by exit status.
Record: `implementation/HOUSEKEEPING_IMPLEMENTATION.md`.

**No game has ever been launched from this repository, and that is now the only thing left to do.**
The staged copy in Local Mods is **0.12.26-dev** against a build of **0.12.42-dev** — sixteen
checkpoints. Re-staging and a first owner launch through RimSort is the only work that unblocks
anything further.
"""

text = io.open(PATH, encoding="utf-8").read()
assert u"0.12.42-dev — the housekeeping" not in text, "entry already present"
io.open(PATH, "a", encoding="utf-8", newline="").write(ENTRY)
print("FINALIZED.md appended: 0.12.42-dev")
