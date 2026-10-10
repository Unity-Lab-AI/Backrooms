# -*- coding: utf-8 -*-
"""Close the phase 2 original-content rows, and demote the one that is genuinely partial."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

# (key found in the open row, new marker, evidence appended after the verbatim text)
ROWS = [
    ('**"are we making our own items and benches and gates? becasue if so i fucking love it!"**', "x",
     " -- **BUILT 0.13.0-dev. Six buildings, one terrain and one journal, all carrying the mod's own "
     "art, every one of them added BESIDE its reuse binding rather than replacing it.** The liminal "
     "fluorescent fixture, the company utility generator, the emergency cutoff, the site marker "
     "beacon, the company gate console, the field analysis bench, faded institutional carpet and the "
     "company route recording. **The two fixtures needed no C# at all** -- Core owns glowers and "
     "fuelled power generation, so they behave correctly against every power and breakdown mod in the "
     "profile instead of being a second power system nobody else can read. Record: "
     "`docs/implementation/ORIGINAL_CONTENT_IMPLEMENTATION.md`."),

    ('**"analysis and examination of these pngs and what they are for"**', "x",
     " -- **DONE 0.13.0-dev, and measuring changed two answers.** Thirteen masters at 1254x1254, RGBA "
     "except the carpet which is correctly opaque because terrain is. **Seven shipped in 0.2.0 with "
     "real defs** -- machine gate, gate console, emergency cutoff, utility generator, field analysis "
     "bench, site fluorescent, carpet -- plus all four sounds, and they were retired across 0.9.0-dev, "
     "0.9.9-dev and 0.12.22-dev. **Six never had a def at all.** The two answers that measurement "
     "changed: the field analysis bench is **2.21 : 1**, not taller than wide as the first pass "
     "reported, because that pass was measuring its drop shadow at a zero alpha threshold; and the "
     "site fluorescent is **4.96 : 1**, not 1.25. Both footprints come from the thresholded box."),

    ('**"and if we have what we need to do this all"**', "x",
     " -- **ANSWERED 0.13.0-dev, as an inventory rather than a yes.** What the masters can become "
     "without new authoring: every item and terrain, and any building that reads the same from every "
     "side. What they cannot: **a rotation for anything drawn as a front elevation**, which is the "
     "machine gate, the gate console, the utility generator and the field analysis bench. "
     "`tools/cut-phase2-art.py` prints exactly those four under ROTATIONS WANTED every run, so the gap "
     "is reported by the tool rather than remembered by a person."),

    ('**"a audio folder! sounds dope!!! how do we do sounds can we?"**', "x",
     " -- **BUILT 0.13.0-dev, AND THREE OF THE FOUR WERE PLAYING IN THE WRONG PLACE.** The system was "
     "already complete -- mute settings, volume factor, main-thread and map guards, warn-once, ten "
     "call sites -- and `ResolveNativeCue` existed only to redirect our four cue names at Core sounds. "
     "**Every call site hands the service a map and a cell, and `Message_ThreatSmall`, "
     "`CommsWindow_Open` and `Message_NegativeEvent` are interface sounds that play at the camera**, so "
     "that position was passed in and discarded. Ours are `MapOnly` with a distRange, so a gate "
     "warning comes from the gate. **Where a cue plays is the def's own property now** rather than a "
     "`cueId != " + Q + "RR_GatePowerRise" + Q + "` comparison in code. **Core's sounds stay as the "
     "fallback**, so a package stripped of its Sounds folder gets quieter instead of silent. "
     "**And no row of the 294 touches sound**, so there is no conflict surface at all."),

    ('**"can we do all of this for all our shit?"**', "x",
     " -- **ANSWERED 0.13.0-dev: the code is not the limit, authoring is.** The cue system takes any "
     "`defName`, so audio coverage is bounded only by audio that exists. The texture side is a tool "
     "rather than thirteen hand edits -- `tools/cut-phase2-art.py` derives every shipped frame from "
     "its master, so re-authoring a master and re-running reproduces the package, and **it derives "
     "WHAT ships by reading which paths the defs and the C# actually name.** 15 textures, **532 KB, "
     "from 11.5 MB of masters**."),

    ('**"remember things rotate"**', "x",
     " -- **BUILT 0.13.0-dev AS A BUILD FAILURE RATHER THAN A NOTE.** `check-register-compliance.py` "
     "rule 6b refuses a `Graphic_Multi` of ours missing `_north`, `_east` or `_south`, so one frame can "
     "never quietly be shown four times. The cutoff and the beacon read the same from every side, so "
     "one master honestly produces every facing. **The fluorescent produced a strategy the first draft "
     "was missing**: a flat fixture read from above genuinely turns with its footprint, so its east "
     "frame is its south turned ninety degrees, drawn at **128x384** for the swapped footprint -- "
     "geometry, not a trick. The four front-elevation masters ship **non-rotatable**, named under "
     "ROTATIONS WANTED, because a back view and a side view do not exist and faking them would put a "
     "missing-texture square on three facings."),

    ("**The masters are not game-ready and the gaps are measured, not asserted.**", "x",
     " -- **CUT 0.13.0-dev, BY TOOL, NEVER BY HAND.** Every shipped texture is derived from its master "
     "so the package can be reproduced rather than hand-matched: tight crop at a real alpha threshold, "
     "letterboxed without distorting aspect, at 128 px per tile. **15 textures totalling 532 KB.** "
     "`check-register-compliance.py` rule 6c refuses any shipped gameplay texture over 1024 px on an "
     "axis, which is the rule that catches a master copied in instead of cut."),

    ("**The carpet does not tile and that is only visible in game.**", "x",
     " -- **FIXED 0.13.0-dev, AND THE NUMBER IN THIS ROW IS WRONG. RESTATED RATHER THAN EDITED.** The "
     "**18.3 / 17.8 against a threshold of 6** above was produced by a proxy that compared a sixteen "
     "pixel band on one edge against the band on the other -- which asks *do these two regions look "
     "alike*, not *do these two columns join*. **That proxy scored a provably seamless quad mirror at "
     "7.15**, which is how it was caught. Measuring what tiles actually touch -- column w-1 against "
     "column 0, in units of the texture's own column-to-column difference -- the master is **x1.4 "
     "left/right and x1.7 top/bottom**: a faint seam on a fine weave, not a grid across every room. "
     "**The fix still stands and still earns its place**: quad mirroring takes both to exactly "
     "**x0.00**, because mirrored edges are equal by construction. The cost is stated rather than "
     "hidden -- a quad mirror is symmetric about both axes, which on this weave reads as texture."),

    ("**Six masters never had a Def at all**", "~",
     " -- **TWO OF THE SIX ANSWERED 0.13.0-dev, FOUR DELIBERATELY HELD.** The **route recording** is "
     "the company journal, and the **return beacon** ships as a site marker beacon -- a powered amber "
     "marker, explicitly NOT a route authority, because the gate's own address book took that job in "
     "0.9.9-dev and taking it back would be two places deciding where home is. **Held, with reasons "
     "rather than silence:** the field recorder's job is already the journal's, the survey tag's is "
     "already a `GlowPod`'s and the evidence case's is already a designated `Shelf`'s -- a second "
     "object doing an existing object's job is the duplication the reuse policy still warns about -- "
     "and the Quiet Pursuer needs a race `ThingDef` with `lifeStages` and body graphics rather than a "
     "texture, which on a 296-mod profile is how other people's pawn rendering gets broken. All four "
     "are cut and held out of the package by the cutter, which ships no texture that no def or source "
     "file names."),

    ("**Every instrument and document that asserts *zero gameplay art or audio ships* has to be "
     "restated out loud.**", "x",
     " -- **NINE PLACES, ALL RESTATED RATHER THAN QUIETLY EDITED, 0.13.0-dev.** "
     "**`check-register-compliance.py` rule 6** asserted the opposite and is **replaced, not removed**: "
     "6a provenance (every shipped asset has a master under `assets/source/`, because *never copy "
     "another package's assets* survived the reversal untouched and is now the clause most at risk), "
     "6b rotation, 6c a size ceiling. "
     "**`check-doc-conformance.py`'s `RETIRED_DEFS` was a typed tuple of ten names eleven lines above "
     "its own comment diagnosing typed counts as a dated assertion wearing a check's clothes** -- six "
     "of the ten shipped again, so a rule written to stop documents promising what the package cannot "
     "deliver started refusing them for describing what it **does**. It is derived now, and returns "
     "exactly one name: `RR_MachineGate`, correctly, because it is a texture on a button. "
     "**`CONTENT_REUSE_POLICY.md`** carries both directions with the 2026-09-28 one kept word for "
     "word. **`ARCHITECTURE.md`**, **`ROADMAP.md`**, **`HOWTO.md`**, **`FIRST_SLICE_CONTENT_INVENTORY.md`**, "
     "**`JOURNAL_AND_QUEST_BRIEF.md`** and **`GATE_0_DECISIONS.md`** -- both its latest-decision "
     "paragraph and **#25**, where only *half* reversed: the Quiet Pursuer's art ban is lifted and its "
     "fairness rules stand, so a sprite may never become how a player is warned."),

    ('**"rmeembr this might change the set gate option and stuff on doors"**', "x",
     " -- **BUILT 0.13.0-dev, AND THE OWNER CALLED IT BEFORE IT HAPPENED.** The role test was hard "
     "coded **twice** -- `OperationsGateBinding`'s lister and `NativeGateBinding.ExactProvider` -- so "
     "widening one would have offered a console the other refused, which reads to a player as a broken "
     "button. `RimroomsGateProviders` owns it once. **The component is the allowlist**, which is this "
     "codebase's own principle stated at `NativeDoorProvider`, and **the type is the role**: "
     "`CompRimroomsGateConsole` has always refused to attach to a def that is neither a "
     "`Building_WorkTable` nor a `Building_CommsConsole`, so no def name is tested anywhere except to "
     "ask *is this one ours*. **AND THE OBVIOUS IMPLEMENTATION WAS A REGRESSION IN A FEATURE'S "
     "CLOTHES:** the button binds only on an unambiguous role, so *one more candidate* means a branch "
     "that built our console beside Core's is suddenly told `RR_NativeGate_NoSingleConsole` -- the "
     "owner's own open 2026-10-03 report, caused by adding content. **One of ours wins outright over "
     "any number of native ones**, so building ours can only ever resolve an ambiguity. The battery is "
     "deliberately NOT widened: admitting every `CompPowerBattery` in the profile, in the one role a "
     "crew's way home depends on, is a change nobody asked for."),

    ('**"and the journal"**', "x",
     " -- **BUILT 0.13.0-dev, AND IT CLOSES A COMPLAINT FROM THREE DAYS EARLIER.** Owner, 2026-10-03, "
     "already quoted inside `CompRouteEvidence.cs`: *" + Q + "the company is suppose to supply u with a "
     "journal to do tasks in but they only gave me noraml books named wrong things that dont do "
     "anything" + Q + "*. Under the old direction the only available answer was a Core textbook with a "
     "component patched on, which is literally a normal book named a wrong thing. **Counting the kit "
     "is plural; issuing one is singular** -- `RecordBookDefs` accepts both, `RecordBookDef` returns "
     "ours and falls back to Core's, so a save full of Core books keeps working. **It revives "
     "`RR_RouteRecording` rather than inventing a def**, because `CompRouteEvidence` never stopped "
     "accepting that exact name from this exact package as a 0.2.0 migration path -- so the evidence "
     "pipeline already worked with it. **`IsLegacyCarrier` is `IsCompanyCarrier` now**: *legacy* "
     "stopped being true the moment the def shipped again, and a reader trusting the old name would "
     "have deleted the branch as dead code. **`CompProperties_Book` is declared, not inherited** -- "
     "`BookBase` carries `CompQuality` but Core declares `CompBook` per book, and omitting it would "
     "have made the def silently fail to qualify with every caller falling back forever: working "
     "software, wrong book, no error anywhere. **And one tuned number lost its duplicate**: "
     "`analysisWorkRequired` lives once, as the C# default, with the patch's copy removed in the same "
     "change."),

    ('**"and the comms console and machining bench"**', "x",
     " -- **BUILT 0.13.0-dev.** `RR_GateConsole` is a real `Building_CommsConsole` and "
     "`RR_FieldAnalysisBench` a real `Building_WorkTable`, because `CompRimroomsGateConsole` refuses "
     "to attach to anything else and the binding validator and the Operations pane ask the same "
     "question -- **so the type IS the role test**, and making them plain Buildings would have meant "
     "relaxing three separate checks to admit them. **The console being a real comms console is a "
     "feature rather than a side effect**: `CorporateContact` already requires one, so the company's "
     "own console can hail the company. Register row 148's disposition is honoured unchanged -- "
     "nothing here depends on quests, and the Operations contract board stays the separate board that "
     "card asks for. **The bench ships with no recipes, deliberately**: giving it Core's machining "
     "recipes would make it a better machining table, a balance change nobody asked for, and row 53 "
     "records the mechanism that makes recipes additive later with no code naming them."),

    ('**"need to be able to build upto three gates of differnt sizes to... remember?"**', "x",
     " -- **REMEMBERED, AND IT DECIDED WHAT THE MACHINE GATE IS ALLOWED TO BE, 0.13.0-dev.** "
     "`MaximumOperationalGates = 3`, and the sizes come from **binding a run of adjacent real doors** "
     "-- 1x1, 1x2 on Core's `OrnateDoor`, 1x3 and 2x3 bound, plus Doors Expanded's multi-cell doors "
     "when installed. **A cloned door def would destroy the binding that produces those sizes** and "
     "cut the gate off from register rows 273 Locks, 77 Doors Expanded, 185 ReBuild, 252 Vault Walls "
     "and Doors, 201 Secret Passage Doors and 265 AirtightGarageDoors -- and from the prisoner "
     "crossing, which rides entirely on door permissions. **So `RR_MachineGate` is not a buildable and "
     "never will be.** Its art went where a face-on drawing is correct: **the designation gizmo**, "
     "which draws flat in the interface, so the button that turns a door into a gate stops showing a "
     "picture of the door. **The world-space overlay is NOT built and the reason is stated rather than "
     "implied**: only the owner launches, and shipping a world sprite nobody here can look at is how a "
     "release earns its first screenshot complaint."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, marker, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if (l.lstrip().startswith("- [ ] ") or l.lstrip().startswith("- [~] ")) and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:60], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        body = raw.lstrip()[6:].rstrip()
        lines[hits[0]] = "%s- [%s] %s%s" % (lead, marker, body, evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("updated %d phase 2 row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
