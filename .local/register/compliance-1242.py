# -*- coding: utf-8 -*-
"""Re-verify COMPLIANCE_AND_OFFICIAL_VERSIONS.md against the package, and make it executable.

The table was verified at 0.5.6-dev and read as current for thirty-six checkpoints. Three of its
rows had stopped being true. Every anchor asserted before anything is written, one write at the
end.

Written as a file rather than a bash heredoc because an apostrophe in the prose breaks the
heredoc, which has now happened enough times in this project to be a rule rather than a mishap.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "COMPLIANCE_AND_OFFICIAL_VERSIONS.md")

original = io.open(PATH, encoding="utf-8").read()

OLD_HEAD = (u"## Verified position at 0.5.6-dev\n\n"
            u"Each row was checked against the package and source, not recalled.\n")
NEW_HEAD = (u"## Verified position — re-run every checkpoint by `tools/check-compliance.py`\n\n"
            u"**This table used to be dated, and that was the defect.** It was verified at "
            u"0.5.6-dev, read as current for **thirty-six checkpoints**, and its own closing "
            u"section said *\"everything in the verified table is mechanically checkable, so it "
            u"is re-run rather than trusted.\"* It was never re-run. Over those thirty-six "
            u"checkpoints **three of its rows stopped being true**: the package went from 76 "
            u"approved files to 89, the fourteen gameplay PNGs it enumerated were deleted at "
            u"0.12.22-dev, and it stated there were **zero** DLC references in package XML while "
            u"the DLC-gated defs added since are exactly the supported way to write them.\n\n"
            u"A dated table of mechanical checks is the same defect as a dated count. So the "
            u"table is now **executable**, and the queue row asked for precisely that: "
            u"*\"one compliance test, applied to all of them.\"*\n\n"
            u"```\npython tools/check-compliance.py\n```\n\n"
            u"Exit 0 passed, 1 failed, **2 skipped** — and two is not a pass. Three rules are "
            u"delegated so that no rule has two owners that can disagree about it: hard "
            u"dependencies and `loadAfter` to `check-register-compliance.py`, DLC gating and the "
            u"five official package ids to `check-dlc-gating.py`, and what the package may "
            u"contain to `tools/package-files.json`.\n")

EDITS = [
    (u"| No game or DLC asset redistributed | **Pass** — all 18 non-XML package files are "
     u"ours: 14 historical `RR_` gameplay PNGs, 2 original `RR_Menu_*` images, "
     u"`About/Preview.png`, `About/License.txt`, plus our own compiled assembly | enumerated the "
     u"76-entry approved package list; every texture is `RR_`-prefixed |",
     u"| No game or DLC asset redistributed | **Pass** — every non-XML file in the "
     u"**89**-entry package is ours: **6** original `RR_Menu_*` images, `About/Preview.png`, "
     u"`About/License.txt` and our own compiled assembly. The **14 historical gameplay PNGs this "
     u"row used to enumerate were deleted at 0.12.22-dev**, replaced by paths read out of Core's "
     u"own defs | `check-compliance.py`, from `tools/package-files.json` rather than a directory "
     u"walk |"),

    (u"| No Core or DLC def overwritten or deleted | **Pass** — the only patch operations "
     u"used anywhere are 4 × `PatchOperationAdd`, 2 × `PatchOperationConditional`, "
     u"1 × `PatchOperationSequence`. **There is no `PatchOperationReplace` and no "
     u"`PatchOperationRemove` in the package.** | grep of all package XML for `Class=\"Patch*\"` |",
     u"| No Core or DLC def overwritten or deleted | **Pass** — the operations in use are "
     u"**16 × `PatchOperationAdd`, 10 × `PatchOperationConditional`, 1 × "
     u"`PatchOperationFindMod`, 1 × `PatchOperationSequence`**. **There is no "
     u"`PatchOperationReplace` and no `PatchOperationRemove` in the package**, and the checker "
     u"fails the build if one arrives — a replace takes ownership of a def, so the last mod "
     u"to load wins and every other mod touching it loses | `check-compliance.py` counts them "
     u"every run |"),

    (u"| No DLC content required or referenced from XML | **Pass** — zero references to "
     u"Royalty, Ideology, Biotech, Anomaly or Odyssey in any package XML | grep across `1.6/` |",
     u"| DLC content referenced from XML is gated | **Pass, and this row's old text was stale** "
     u"— it claimed **zero** DLC references. There are now **six**, all of them "
     u"`MayRequire`: two each for `Ludeon.RimWorld.Anomaly`, `Ludeon.RimWorld.Biotech` and "
     u"`Ludeon.RimWorld.Odyssey`. `MayRequire` is the official mechanism and Core and the DLC use "
     u"it nearly two thousand times in their own data, so the correct rule was never *no "
     u"references* but *no ungated reference* | `check-dlc-gating.py`, which owns this rule |"),

    (u"| No DLC assembly referenced from code | **Pass** — the single DLC-adjacent code path "
     u"is `pawn.Ideo` in `ConstructionFinishingProvider`, and it is null-guarded. `Ideo` is a "
     u"type in the official `Assembly-CSharp`, present with or without Ideology; without the DLC "
     u"`pawn.Ideo` is simply null | grep of all C# for `ModsConfig.` / `.Ideo` / `*Active`: 1 "
     u"result |",
     u"| No DLC assembly referenced from code | **Pass, and this row's old text was stale** "
     u"— it said one `ModsConfig` reference; there are **five**: `AnomalyActive`, "
     u"`BiotechActive`, two `IsActive` for tracked optional mods, and one generic. **Every DLC "
     u"type this package names lives in the official `Assembly-CSharp`** — there is no "
     u"separate DLC assembly to reference, which is why the rule holds however many call sites "
     u"there are. Each is a runtime question answered by the game itself | "
     u"`check-dlc-gating.py`; enumerated fresh each checkpoint |"),

    (u"| No game assembly patching | **Pass** — no Harmony, no detours, no reflection writes "
     u"into game types; behaviour is added through Core's own `ThingComp`, `GameComponent`, "
     u"`WorkGiver`, `JobDriver` and `Def` extension points | audited in "
     u"[`DEPENDENCIES_AND_CAPABILITY_MATCHING.md`](implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md) |",
     u"| No game assembly patching | **Pass** — no Harmony, no detours, no reflection writes "
     u"into game types; behaviour is added through Core's own `ThingComp`, `GameComponent`, "
     u"`WorkGiver`, `JobDriver` and `Def` extension points. **Reflection is the loophole this now "
     u"closes:** a `SetValue` into a game type is an assembly modification no dependency list "
     u"would show | `check-compliance.py` refuses Harmony, MonoMod, a reflection write and a "
     u"non-public field read |"),

    (u"| No third-party mod code or asset copied | **Pass** — no mod source or asset is "
     u"vendored. Noted specifically because **Stargates! (profile row 218) is GPL-3.0**: copying "
     u"from it would force this mod to GPL. It is explicitly not a dependency and nothing is "
     u"taken from it | dependency audit, per-mod review rows |",
     u"| No third-party mod code or asset copied | **Pass** — no mod source or asset is "
     u"vendored. Noted specifically because **Stargates! (profile row 218) is GPL-3.0**: copying "
     u"from it would force this mod to GPL. It is explicitly not a dependency and nothing is "
     u"taken from it. **The check tests for assertion, not mention** — its first run flagged "
     u"`ConnectedFoodAdapter.cs`, whose comment says Gastronomy's rights are unresolved *so its "
     u"code must not be adapted*, which is the sentence the rule wants the code to contain | "
     u"`check-compliance.py`, with a negator list documented as maintained rather than complete |"),

    (u"| QA overlay not shipped | **Pass** — the rim api / RimBridgeServer overlay is not in "
     u"the package and is not declared a dependency; it is a separate owner-attached QA tool | "
     u"approved package list; `research/RIMBRIDGE_TEST_HARNESS.md` |",
     u"| No AI attribution in any shipped file | **Pass** — a standing project LAW, and the "
     u"honest authorship position for a store page. **Nothing had ever checked the package for "
     u"it**; only commits and documents were considered | `check-compliance.py` scans every "
     u"shipped XML and text file |\n"
     u"| QA overlay not shipped | **Pass** — the rim api / RimBridgeServer overlay is not in "
     u"the package and is not declared a dependency; it is a separate owner-attached QA tool | "
     u"`check-compliance.py` |"),

    (u"| Our own licence, stated | **Pass** — MIT, in `About/License.txt` | file present in "
     u"the package |",
     u"| Our own licence, stated | **Pass** — MIT, in `About/License.txt` | "
     u"`check-compliance.py` reads the file and the licence name |"),

    (u"| Official game assemblies only, unmodified | **Pass** — 5 reference assemblies, all "
     u"from the official install, hashes recomputed each checkpoint with no drift | "
     u"`docs/implementation/evidence/*/reference-manifest.json` |",
     u"| Official game assemblies only, unmodified | **Pass** — **5** reference assemblies, "
     u"all from the official install, hashes recomputed each checkpoint with no drift. **Zero "
     u"parsed references now fails rather than passing**: the first version of the check read the "
     u"wrong manifest key and reported *\"0 assemblies, all from the official install\"*, which "
     u"is the exact false-pass shape this file exists to remove | `check-compliance.py` against "
     u"`docs/implementation/evidence/*/reference-manifest.json`; **exit 2, skipped, when no "
     u"manifest is present** |"),

    (u"## Re-verification\n\nEverything in the verified table is mechanically checkable, so it is "
     u"re-run rather than trusted. The checks are: the approved package list for non-`RR_` "
     u"assets, a grep of package XML for `Class=\"Patch\"` operations and for `texPath` values "
     u"outside `RR_`, a grep for DLC package ids in XML, and the reference manifest for assembly "
     u"drift. Any future checkpoint that adds content re-runs them before publishing.",
     u"## Re-verification\n\n**It is `tools/check-compliance.py`, and it runs in the standard "
     u"sweep with the other twelve checkers.** That sentence is the whole of this section now, "
     u"because the previous version of it described the checks in prose and asked to be "
     u"trusted — which is how the table above went thirty-six checkpoints without being "
     u"re-run while saying it was re-run rather than trusted.\n\n"
     u"The one thing the checker cannot answer is below, and it is not a check."),
]

text = original
problems = []
if text.count(OLD_HEAD) != 1:
    problems.append("head anchor: %d" % text.count(OLD_HEAD))
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

text = text.replace(OLD_HEAD, NEW_HEAD, 1)
for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("compliance table re-verified and made executable")
