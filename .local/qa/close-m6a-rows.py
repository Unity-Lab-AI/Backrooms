# -*- coding: utf-8 -*-
"""Close the M6a rows that genuinely close without a launch, each against what now covers it.

M6a exists because of owner decision 19, 2026-09-29, verbatim *"Split M6a / M6b, build all of
M6a"*. These are its three rows plus the save-migration consequence row.

LAW #0: the verbatim row text is untouched. Evidence is appended.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSURES = [
    ("Validate Def references, language keys, patch targets, load folders, package metadata, "
     "missing textures/audio, logs, build output, and clean-install folder structure.",
     "**CLOSED 0.12.99-dev. ALL NINE SUBJECTS ARE INSTRUMENTED, and the one that was not fully "
     "verified is now.** Each named subject against the instrument that answers it, measured in "
     "this batch: **Def references** -- 214 packaged references checked and 14 expansion-gated "
     "(`check-standalone-guarantee`), 339 defs declared and cross-referenced "
     "(`check-package-integrity`), plus the new foreign-work-type rule that refuses an ungated "
     "reference to a work type no installed game folder defines. **Language keys** -- 2,051 keys, "
     "**0** duplicates, 1,867 literal references all resolving, **0** argument mismatches. "
     "**Patch targets** -- every `PatchOperation` xpath resolved to the defName it selects; "
     "**the seven optional `PH_` door targets that used to read *\"not installed here and cannot "
     "be verified\"* are now VERIFIED against the installed profile mods**, because Doors "
     "Expanded (row 77) and ReBuild: Doors and Corners (row 185) are both in the owner's own 294 "
     "and both on disk, and a renamed optional target applies to nothing and reports nothing. "
     "**Load folders** -- `LoadFolders.xml` maps `v1.6` to `1.6` and the root-file rule checks "
     "it. **Package metadata** -- `About.xml` version, supported versions, packageId, zero "
     "declared dependencies and the 294-row `loadAfter`, all checked, and the description held "
     "to the same claims rules as a reader document. **Missing textures/audio** -- every `RR_` "
     "texture resolves and every package `.png` is referenced; the 12 menu slides are covered by "
     "the folder scan, and the 3 game-asset paths are reported **unverifiable rather than "
     "passed** because they live in asset bundles. No audio ships. **Logs** -- the build logs "
     "clean and the one live error in any launch log is **not ours** (`RimBridgeServer` wants "
     "0Harmony 2.4.2.0). **Build output** -- 103 package files, **0 warnings, 0 errors**. "
     "**Clean-install folder structure** -- the export assembles the package from the build "
     "manifest with a SHA256 per file and a denylist refuses the assembled tree afterwards. "
     "**Nothing on this row needs a launch and nothing on it is open.**"),

    ("Prepare final mod page, description, feature list, screenshots, trailer/preview art, "
     "installation guide, dependencies, DLC matrix, RWT setup, credits, source provenance, "
     "license, FAQ, known issues, and update/support plan.",
     "**CLOSED 0.12.99-dev for its M6a half, which is the half the row's own note scopes to "
     "here.** Every item has an artefact: **description** -- generated from `About.xml` so the "
     "text in the mod list and the text on the repository are one sentence. **Feature list and "
     "installation guide** -- the thirteen wiki pages, live. **Dependencies** -- stated as none, "
     "in the readme's own first line. **DLC matrix** -- the mods page, which exists to say the "
     "expansions are optional and names every one. **RWT setup** -- the multiplayer page, "
     "rewritten from register row 196 and naming RimWorld Together, that it needs Harmony and we "
     "do not, and that everyone needs the same mod list. **Credits, source provenance and "
     "license** -- the credits page: MIT, Ludeon's assemblies not bundled, Kane Pixels and A24 "
     "as indirect influence with no frames or audio included, no other mod's files bundled or "
     "modified, no gameplay art shipped. **FAQ** -- the troubleshooting page, whose *every box is "
     "ticked* section now answers with gate control. **Known issues and update/support plan** -- "
     "`docs/WHATS_NEW.md`, authored this batch. "
     "**AND THE LICENCE LINK ON THE CREDITS PAGE WAS 404 ON THE LIVE SITE, found while closing "
     "this row and read back over HTTP rather than inferred.** The source links `../../LICENSE`; "
     "the renderer's `lstrip(\"./\")` strips the *characters* `.` and `/` and flattened it to "
     "`LICENSE`, which is a perfectly site-relative-looking href for a file that is not at the "
     "site root. **A broken image is visible; a dead link looks exactly like a working link.** "
     "Fixed three ways: the renderer separates `./` noise from a `..` escape, the licence is "
     "**published inside the site** the same way the slide art is, and `check_links_resolve` is "
     "the sibling the image guard shipped without -- six plants hold it. "
     "**The screenshots, trailer and preview-art half needs a running game and is already its "
     "own test-phase row.**"),

    ("Tag release, archive exact source and build artifacts, preserve a known-good server "
     "profile, and publish only features that passed their listed acceptance criteria.",
     "**CLOSED 0.12.99-dev for its M6a half, exactly as the row's own note scopes it:** *\"the "
     "ritual and the archive close here; the actual tag cannot be cut until M6b supplies the "
     "acceptance results this row requires.\"* **`PUBLISHING.md` §8 is the ritual**, written this "
     "batch because it did not exist: six preconditions, five of which are met today and the "
     "sixth of which is the gate -- *every feature in the release notes has a recorded acceptance "
     "result*, and nothing has passed anything because nothing has run. Then three acts: the "
     "version drops `-dev`; an **annotated** tag pushed and read back on both remotes here; and "
     "**the same tag on the mod-only repository**, because that is the one a player downloads and "
     "a version that exists here and not there is a version nobody can obtain. "
     "**And the archive is a property rather than a folder**, which is the honest form: exact "
     "source is the tagged commit on four remote refs, and build artifacts are the manifest with "
     "a SHA256 per file -- a stronger archive than a zip, because it lets a later reader prove a "
     "downloaded copy is the one that was built. **The one piece genuinely missing is the "
     "known-good profile, and it is missing because *known-good* is a launch result.** A release "
     "records the profile it published **against** -- the 294-row snapshot with a parsed "
     "`About.xml` SHA256 per entry -- and does not claim the snapshot was good. **No tag is cut.**"),

    ("**Consequence: save migration becomes a standing obligation from the first published "
     "version.**",
     "**CLOSED AS A DECISION 0.12.99-dev, and the decision is the owner's own.** Asked directly "
     "in this run of questions, the answer was *\"Development-save break is allowed -- declare "
     "it\"*, which matches what they have said twice and never changed: *\"we dont have other "
     "peoples saves we just publish it all and update it as we go fixing bugs\"*. **So the "
     "obligation this row anticipated does not begin yet, and the reason is a version policy "
     "rather than a convenience:** while the version starts with `0.` a build is not promised to "
     "open an older build's save, and the build that wrote a save can always open it, which is "
     "why the old package is preserved. **It is DECLARED rather than assumed** -- "
     "`docs/WHATS_NEW.md` says it to a player in their own terms, and `PUBLISHING.md` §8.5 "
     "forbids a release promising a migration it has not written. The obligation this row names "
     "begins at **`1.0.0`**, which is the first stable under D2's unchanged version policy, and "
     "`SAVE_MIGRATION_POLICY.md` owns it from there."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    missed = []
    done = 0
    for phrase, evidence in CLOSURES:
        hits = [i for i, line in enumerate(lines)
                if line.lstrip().startswith(("- [ ] ", "- [~] ")) and phrase in line]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        index = hits[0]
        raw = lines[index]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[index] = "%s- [x] %s -- %s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        done += 1
    if missed:
        for phrase, count in missed:
            print("NOT CLOSED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
