# -*- coding: utf-8 -*-
"""Prepend the 0.12.99-dev changelog entry, keeping only the BOM that is already there."""
import io
import sys

NL = chr(10)
P = "CHANGELOG.md"
Q = chr(34)

LINES = [
"## 0.12.99-dev - 2026-10-05 - The buildable rows were buildable, and three were already done",
"",
"- **OWNER: *" + Q + "read now.md to continue i think we only have a handful of open items but idk",
"  how many of those are buildable and unblocked undiffered, u didnt specify too correctly... so",
"  lets get on the items of the todo that are still outstanding that can be done" + Q + "***",
"- The complaint is fair and the answer is a count rather than a paragraph. **Of sixteen open rows,",
"  two were commissioned work the owner had already answered, four were M6a and close without a",
"  launch, five were held open by pointers to rows that do not exist, and the rest wait on a",
"  launch, Steam or a domain.** Queue **16 open / 11 partial** to **11 open / 4 partial**.",
"",
"### A row held open by a pointer to nothing, five times, and now a checker",
"",
"- **0.12.98-dev found this twice and declined to make it a rule** -- *" + Q + "two cases, and 'the",
"  row below' has no mechanical meaning" + Q + "*. **That judgement was wrong and the measurement is",
"  what changed it.** Counted across the queue: **five** statements of open work resolved by",
"  position instead of by subject, and **three of the five point at rows that were closed and",
"  archived**.",
"- *" + Q + "optional provider adapters, on their own row below" + Q + "* -- no such row.",
"  *" + Q + "the optional provider interfaces, on their own row below" + Q + "* -- no such row.",
"  *" + Q + "containment, vehicles and the VGE hooks, each listed individually above" + Q + "* -- no",
"  such rows. And in prose, *" + Q + "Four genuine gaps remain, recorded below as new rows" + Q + "*",
"  -- **all four were built at 0.6.7-dev**, so the sentence advertised four pickups with nothing",
"  behind them.",
"- **`tools/check-queue-pointers.py` is checker 25**, and the reason it does not cry wolf is that it",
"  refuses one construction rather than one phrase: **a statement of what is still open, resolved by",
"  position.** Twelve lines in the queue carry a positional phrase and only five are faults -- a",
"  heading saying *" + Q + "it binds every row below" + Q + "* is describing its own contents and is",
"  correct. Quoted spans are stripped first, because a row that quotes a pointer in order to record",
"  that it was removed must not fail on its own evidence.",
"- **And the first fix was wrong in a way the checker caught.** Appending the correction while",
"  leaving the pointer standing is the *second opinion* failure already recorded about stacked doc",
"  comments: two statements about one thing, one of them dead. The pointers replaced were **mine**,",
"  appended in earlier batches -- every owner word and every verbatim master-TODO line is untouched.",
"",
"### " + Q + "A mod nobody has named" + Q + " was twelve named mods, installed on this machine",
"",
"- The work-families row's last remainder read *" + Q + "ONLY REMAINDER: a mod-added work type with",
"  its own givers... it cannot be built against a mod nobody has named." + Q + "* **Every mod in the",
"  profile is named -- by the register, with a review card each -- and 288 of the 294 are on disk.**",
"  So the claim was checkable, and checking it was cheaper than leaving a row open on it.",
"- Scanned: **twelve profile mods add thirteen work types**. Every giver class **decompiled against",
"  its installed assembly** rather than inferred from its name.",
"- **Exactly one is buildable and it is now built.** `MedicalTraining` from **Medical Dissection",
"  (register row 274)**, whose `WorkGiver_DoDissectionBill` derives from **`WorkGiver_DoBill`** and",
"  whose giver def carries `fixedBillGiverDefs` -- which is the entire requirement, because",
"  `BillWorkProvider` unions bench defs **by capability** and names nothing. One provider",
"  registration, one giver def pair, one label, and **no code anywhere referencing that mod**.",
"- **The other twelve are a closed decision with the reason recorded.** They are",
"  `WorkGiver_Scanner`, `WorkGiver_Warden` or `WorkGiver_RescueDowned` subclasses, and the only",
"  generic candidate query available -- `PotentialWorkThingsGlobal(pawn)` -- reads `pawn.Map`, which",
"  is the one map a deployment question is never about. All thirteen are tabulated so nobody",
"  re-derives it.",
"",
"### The settings pane drew sliders for work the player does not own",
"",
"- Found while adding the thirteenth work type, and **live since 0.6.4-dev**. Four families are",
"  `MayRequire`-gated -- childcare on Biotech, dark study on Anomaly, fishing on Odyssey, now",
"  medical training on a profile mod. `Apply` had always skipped a family whose giver defs were",
"  absent. **The pane had not.**",
"- So a player without Anomaly was shown a cross-gate dark-study priority slider, **labelled with a",
"  shipped default of 0** because no def had ever loaded to read one from, writing an override keyed",
"  to a defName nothing carries. **A control for work the player does not have is worse than a",
"  missing one** -- it reads as a feature that does nothing.",
"- Both now ask through **one** method. `TryGivers` is the single lookup site: the pane takes the",
"  verdict, the applier takes the defs. **Two pieces of code asking the same question separately is",
"  what produced the phantom control, so the proof COUNTS the lookups** rather than testing for",
"  their presence.",
"- **And `check-standalone-guarantee.py` refused the first version of that refactor, correctly.** A",
"  null guard inferred from a predicate called earlier is a guard a later reordering removes",
"  silently, so the comparison lives beside the lookups it guards.",
"",
"### The DLC gate could not see a mod",
"",
"- `check-dlc-gating.py` indexes the game's `Data` folders and asks whether a referenced name is",
"  DLC-only. **A work type a profile mod adds is in no `Data` folder at all** -- not DLC-only,",
"  therefore invisible. Ungated, it is the identical unresolved cross-reference at load that two",
"  childcare givers shipped with until 0.6.6-dev.",
"- The rule is scoped to `<workType>` deliberately: it is the one tag here whose text is always a",
"  `WorkTypeDef` name and never prose, a number or a class. 75 references, every foreign one gated.",
"  Widening it to every reference tag would mean guessing what each tag's text is.",
"",
"### Seven patch targets nobody could verify were verifiable all along",
"",
"- `check-package-integrity.py` reported *" + Q + "not installed here and cannot be verified" + Q + "*",
"  seven times, every one a `PH_` door. **Both mods that declare them are in the owner's own 294 and",
"  both are installed** -- Doors Expanded (row 77) and ReBuild: Doors and Corners (row 185).",
"- **A note that cannot be checked reads as checked and fine after the third time somebody sees it**,",
"  and this one was hiding the worse outcome: a renamed optional target applies to nothing and",
"  reports nothing, so the gate console silently never appears on that door. Now **an unknown",
"  optional target is a failure**, and the library being unreachable degrades to the old notes",
"  rather than to a silent pass.",
"",
"### The licence link on the published credits page was a 404",
"",
"- **Read back over HTTP, not inferred.** `check_images_resolve` was written the day every banner",
"  404'd and was aimed at `<img src>` because that was the fault in hand. **`<a href>` has the",
"  identical failure mode and the credits page had it.**",
"- The source links `../../LICENSE`; the renderer's `lstrip(" + Q + "./" + Q + ")` strips the",
"  **characters** `.` and `/`, so it came out as `LICENSE` -- a perfectly site-relative-looking href",
"  for a file that is not at the site root. **A broken image is visible. A dead link looks exactly",
"  like a working link.**",
"- Fixed three ways rather than one: the renderer separates `./` noise from a `..` escape so the",
"  guard can see it; **the licence is published inside the site** the same way the slide art is, for",
"  the same reason; and `check_links_resolve` is the sibling the image guard shipped without. **One",
"  pattern, all the references it guards.**",
"",
"### Three design briefs and a tier sweep, both commissioned and both answered",
"",
"- **OWNER: *" + Q + "Write briefs for all three" + Q + "*** -- `docs/ALTERNATE_START_BRIEFS.md`, each",
"  with the four things the row named plus convergence and the dependency boundary. **And writing",
"  them found two of the three recorded premises were illegal:** `town_distortion`'s pressure is",
"  *" + Q + "time pressure" + Q + "* and `isolated_outpost`'s is *" + Q + "uncertain evacuation" + Q,
"  "  + "*, and **CAMPAIGN_CHART.md 1.1 permits one clock and it is the gate's.** Each is replaced",
"  by a cost that grows -- settlement standing, and an account the post cannot reach -- and the old",
"  premises stay recorded as superseded rather than quietly edited.",
"- **OWNER: *" + Q + "Sweep the constants and propose the tiers to you" + Q + "*** --",
"  `docs/research/RESEARCH_T5_T6_SWEEP.md`. **278 constants enumerated, six candidates survive, four",
"  branches honestly get none.** Facilities T5 fills a gap **1.1 itself names**: maintenance is one",
"  of the four factors deciding a gate's window and the only one with no project on it.",
"- **Commerce gets none, and that is the finding.** Its candidates **became player settings** at",
"  0.12.98-dev, which is better: a research tier and a slider over one number is two controls",
"  fighting, and a project whose whole effect is *the slider you already have reads a different",
"  default* is precisely the promise-that-changes-nothing four deleted projects were deleted for.",
"",
"### M6a closes, and the player-facing changelog is authored rather than filtered",
"",
"- **The validation sweep closes against instruments, subject by subject**: 214 def references,",
"  2,051 keys with 0 duplicates and 0 argument mismatches, every patch xpath resolved,",
"  `LoadFolders.xml`, package metadata, textures with the three game-asset paths reported",
"  **unverifiable rather than passed**, 103 files at 0 warnings and 0 errors, and an export that",
"  verifies a SHA256 per file.",
"- **`PUBLISHING.md` section 8 is the release ritual**, written because it did not exist. Six",
"  preconditions; five are met and the sixth is the gate. **The archive is a property rather than a",
"  folder** -- exact source is a tagged commit on four refs and build artifacts are the manifest",
"  with a hash per file, which is stronger than a zip because it proves a downloaded copy is the one",
"  that was built. **The missing piece is a known-good profile, and *known-good* is a launch result.",
"  No tag is cut.**",
"- **`docs/WHATS_NEW.md` is the player-facing record**, written rather than filtered exactly as the",
"  exporter's own comment required. It ships at the public repository root and the generated readme",
"  links it. It says plainly that nothing has been played, that nothing is claimed as tested with",
"  other mods, that co-op is not promised, that development saves may break, and that balance is",
"  unjudged.",
"- **And the save-migration consequence row closes on the owner's own answer:**",
"  *" + Q + "Development-save break is allowed -- declare it" + Q + "*. Declared to a player in their",
"  terms, and the release section forbids promising a migration nobody has written. The obligation",
"  this row anticipated begins at `1.0.0`.",
"",
]


def main():
    raw = io.open(P, "rb").read()
    had = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    marker = "# Changelog" + NL + NL
    if text.count(marker) != 1:
        print("heading matched %d time(s); refusing" % text.count(marker))
        return 1
    if "0.12.99-dev" in text.split(NL)[2]:
        print("entry already present; nothing written")
        return 1
    text = text.replace(marker, marker + NL.join(LINES) + NL, 1)
    out = text.encode("utf-8")
    if had:
        out = b"\xef\xbb\xbf" + out
    io.open(P, "wb").write(out)
    print("changelog entry written (%d lines); BOM %s"
          % (len(LINES), "kept" if had else "absent"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
