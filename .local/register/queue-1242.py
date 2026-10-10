# -*- coding: utf-8 -*-
"""Close rows 206, 302, 1054, 1268, 1269 and 1286-1290. Status changes and appended notes only."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "TODO.md")

original = io.open(PATH, encoding="utf-8").read()

SWEEP = (u"**SWEPT 0.12.42-dev. All twenty-one families are now done, and the last seven "
         u"collapse into five family strings** because the register groups two or three names per "
         u"family: *Materials, cargo and recovered resources*; *Medical, biological and recovery "
         u"systems*; *World operations, contracts and commerce*; *Hospitality and visitor "
         u"economy*; *Staff psychology, relationships and faction standing*. **Every one was "
         u"already honoured and no code changed** -- which is the honest result and is worth "
         u"stating plainly rather than dressing up. What did change is that **four of the rules "
         u"were true only because of the current shape of the package**, and a rule with no check "
         u"behind it is a promise, so `check-register-compliance.py` gained them with their row "
         u"citations: no patch may name a `ThoughtDef` (row 2 -- *\"keep any future company "
         u"thoughts isolated and additive\"*), a `TraderKindDef` (row 17 -- *\"leave calls and "
         u"trader options on the existing Comms Console\"*), a `HediffDef` (the medical family) "
         u"or a `MainButtonDef` (the hospitality family -- *\"instead of replacing their native "
         u"menus\"*), and no patch may alter another def's stat bases (the materials family -- "
         u"*\"preserve each mod's normal material and weight behavior\"*). **The finding worth "
         u"keeping:** the medical family's rule is *\"the core expedition loop must not require "
         u"one medical or Biotech mod to treat a pawn\"*, and **0.12.41-dev came within one "
         u"decision of breaking it** -- had the crew planner's missing-medic gap been written as "
         u"a refusal, which is the obvious way, the loop would have required a medic. It was "
         u"advisory for a different reason and the register independently requires it. Record "
         u"`implementation/HOUSEKEEPING_IMPLEMENTATION.md`, proof `proof-housekeeping.py`. Was: ")

EDITS = [
    (u"- [~] Integrate relevant profile work/storage/hauling providers; account for all 294 rows "
     u"without asserting universal support from a successful load.",
     u"- [x] " + SWEEP + u"Integrate relevant profile work/storage/hauling providers; account for "
     u"all 294 rows without asserting universal support from a successful load."),

    (u"- [~] **Continue the retroactive pass** across the remaining system families.",
     u"- [x] **SWEPT 0.12.42-dev, same sweep as the row above; one deliverable, not two.** All "
     u"twenty-one families done. See that row for the five family strings, the four new checker "
     u"rules with their register citations, and the medical-family finding. Was: **Continue the "
     u"retroactive pass** across the remaining system families."),

    (u"- [ ] **Consequence: reconcile 0.5.0–0.7.1 back into the master backlog.**",
     u"- [x] **RECONCILED 0.12.42-dev, and the row underestimated itself.** It predicted the "
     u"master row count *\"understates the build by roughly thirty points\"*. **It was 56.** The "
     u"master backlog went from **122 open / 134 done to 66 open / 190 done**, and every flip "
     u"names the checkpoint that closed it -- the cross-map work engine row this row was written "
     u"about, the escalation ladder, the gate state machine, the transaction service, all three "
     u"starts, the existing-content replacement, the room library, the economy and evidence "
     u"systems, research tiers 0-3, containment, the vehicle and VGE hooks, and the RWT "
     u"detection. **Two rules were obeyed without exception.** Every original word of every row "
     u"was kept and the note appended after it -- marking a task done changes the status ONLY. "
     u"And **no runtime-acceptance row was flipped**: no game has ever been launched from this "
     u"repository, and marking those accepted would erase the only honest caveat this project "
     u"has. The proof asserts both. Record `implementation/HOUSEKEEPING_IMPLEMENTATION.md`. Was: "
     u"**Consequence: reconcile 0.5.0–0.7.1 back into the master backlog.**"),

    (u"- [ ] **`Rimrooms_Campaign_Economy_v0.2.xlsx` has the same problem and no generator.**",
     u"- [x] **BUILT 0.12.42-dev as `tools/extract-economy-workbook.py`, and \"unopenable\" was "
     u"about Excel rather than about the bytes.** An xlsx is a zip of XML and the standard "
     u"library reads both -- the same realisation that made the register queryable, applied to "
     u"the other workbook. **Five documents linked a file nobody in this repository could read**; "
     u"it transcribes to **five sheets and 381 rows**. It got exactly the treatment this row "
     u"asks for: **tracked source** at `docs/research/campaign-economy-workbook.json`, a "
     u"**generator** with a `--check` mode that re-reads the xlsx and refuses a source that has "
     u"drifted, and an **HTML output** at `outputs/readable/campaign-economy.html`. **Not one "
     u"number was touched.** This row is explicit that it is a different dataset with different "
     u"owners whose content has not been verified, so the transcription is exact and both the "
     u"source and the page say at the top that the figures are transcribed rather than verified "
     u"and that nothing has been observed in play. A generator that silently corrected a figure "
     u"would destroy the only useful property the file has: being what its author wrote. Was: "
     u"**`Rimrooms_Campaign_Economy_v0.2.xlsx` has the same problem and no generator.**"),

    (u"- [ ] **The register preview PNGs under `outputs/`** depict the superseded two-sheet "
     u"layout.",
     u"- [x] **NOTED 0.12.42-dev, and deliberately not deleted** -- this row says removing them "
     u"is the owner's call, so a `README.md` sits beside them instead and states which file is "
     u"authoritative. **Nothing in that folder was removed.** The images are wrong rather than "
     u"merely old: they show **two** sheets, while the register parses **295 rows** out of its "
     u"HTML and the companion economy workbook transcribes to **five** sheets. An image of a "
     u"two-sheet layout is a view of a different file. Was: **The register preview PNGs under "
     u"`outputs/`** depict the superseded two-sheet layout."),

    (u"- [ ] **\"make sure we are foillowing all rimworld and steam TOS and requirments\"**",
     u"- [x] **BUILT 0.12.42-dev as `tools/check-compliance.py`, the thirteenth checker, and the "
     u"queue row four below asked for exactly this: *\"one compliance test, applied to all of "
     u"them\"*.** `COMPLIANCE_AND_OFFICIAL_VERSIONS.md` held the position as a thirteen-row table "
     u"whose own closing line said it *\"is re-run rather than trusted\"*. **It was never "
     u"re-run** -- verified at 0.5.6-dev, read as current for **thirty-six checkpoints**, and "
     u"over those checkpoints **three of its rows stopped being true**: the package went from 76 "
     u"approved files to 89, the fourteen gameplay PNGs it enumerated were deleted at "
     u"0.12.22-dev, and it stated there were **zero** DLC references in package XML while the "
     u"six `MayRequire` gated defs added since are exactly the supported way to write them. **A "
     u"dated table of mechanical checks is the same defect as a dated count**, so the table is "
     u"now executable. It refuses a destructive patch operation, a bundled game binary, Harmony, "
     u"a detour framework, a reflection write into a game type, a non-public field read, a "
     u"shipped file at a texture path that is not ours, AI attribution in anything shipped, the "
     u"QA overlay inside the package, and a reference to an assembly outside the official "
     u"install. **Two of its own rules caught it first:** the licence check flagged a comment "
     u"that *denies* the GPL applies, so it tests for assertion rather than mention; and the "
     u"assembly check read the wrong manifest key and reported *\"0 assemblies, all from the "
     u"official install\"* -- **zero parsed references now fails rather than passing**, because "
     u"a compliance check that finds nothing and says ok is worse than no check. Exit 2 means "
     u"skipped, and skipped is not a pass. Record "
     u"`implementation/HOUSEKEEPING_IMPLEMENTATION.md`, proof `proof-housekeeping.py`. Was: "
     u"**\"make sure we are foillowing all rimworld and steam TOS and requirments\"**"),

    (u"- [ ] **\"when it comes to issues similar and the issue of factions\"**",
     u"- [x] **CLOSED 0.12.42-dev by the same checker.** `FactionDef` authoring adds definitions "
     u"only: `RR_UniverseFactions.xml` names existing pawn kinds and icon paths, and the checker "
     u"refuses a shipped file sitting at a texture path that is not this package's own -- which "
     u"is the exact line between a reference and a redistribution. Was: **\"when it comes to "
     u"issues similar and the issue of factions\"**"),

    (u"- [ ] **\"and pawn heduffs\"**",
     u"- [x] **CLOSED 0.12.42-dev, and the answer is a measurement: this package has no "
     u"`HediffDefs` folder at all.** The checker asserts no patch names a `HediffDef` either, and "
     u"the same rule is now in `check-register-compliance.py` sourced from the medical family's "
     u"own instruction that the expedition loop must not require one medical mod. If a hediff is "
     u"ever added, rule 5 of the compliance document binds it: a missing def is an unavailable "
     u"effect, never an exception. Was: **\"and pawn heduffs\"**"),

    (u"- [ ] **\"and the like\"**",
     u"- [x] **CLOSED 0.12.42-dev, and this row is the one that decided the shape of the whole "
     u"pass.** *\"And the like\"* generalises the rule to every def class the mod may ever add, "
     u"and this row spells out what that means: **one compliance test, applied to all of them.** "
     u"Not a note per def class -- a test. That is `tools/check-compliance.py`, and it tests the "
     u"**shape** rather than a list: no destructive patch operation anywhere, every non-XML "
     u"shipped file this package's own, no file at a texture path that is not ours. Those hold "
     u"for a def class nobody has thought of yet, which is what *\"and the like\"* requires. Was: "
     u"**\"and the like\"**"),

    (u"- [ ] **\"this mod has to be working with official versions\"**",
     u"- [x] **CLOSED 0.12.42-dev by the same checker.** `supportedVersions` is `1.6` alone, "
     u"`LoadFolders.xml` maps `v1.6`, the package bundles no game binary or data file of any "
     u"kind, there is no Harmony and no reflection write into a game type, and the build "
     u"references **five** assemblies -- all from the official install, hashes recomputed each "
     u"checkpoint. **Zero parsed references fails rather than passing**, and a missing manifest "
     u"exits **2, skipped**, because a check that could not run must not report what a check that "
     u"ran and found nothing reports. Was: **\"this mod has to be working with official "
     u"versions\"**"),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:80]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("%d housekeeping rows closed in one write" % len(EDITS))
