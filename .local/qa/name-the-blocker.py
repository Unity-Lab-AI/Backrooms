# -*- coding: utf-8 -*-
"""Make every open row name its own blocker, and close the ones whose blocker turned out to be met.

`tools/check-queue-pointers.py` (checker 25) found five statements of open work resolved by
position instead of by subject, and **three of the five pointed at rows that had already been
closed and archived**. So this does two things in one pass, because they are the same fact:

  * replaces the pointer with the subject, and
  * where the subject turns out to be built, closes the row against the measurement.

LAW #0: every original word stays. Evidence is appended with ` -- ` and the status letter is the
only character ever changed in place.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

# (status, anchor phrase, evidence) -- status is the new letter, or None to leave it alone.
EDITS = [
    # ---------------------------------------------------------------- the five pointer faults
    ("T", "**Open:** the individual routes listed below.",
     "**EVERY ROUTE ON THIS ROW IS BUILT; WHAT IS LEFT IS A LAUNCH. 0.12.99-dev.** The pointer "
     "*\"the individual routes listed below\"* was the shape checker 25 was written against, and "
     "replacing it with the subjects is what showed the row was finished: **independent "
     "connection ownership, permanent natural portals, free crossing, shared cross-map "
     "work/materials, persistent seeds and dynamic inhabitants** all ship. Cross-gate work is "
     "**31 families, 23 of them deployments**, and every work type in Core and all five "
     "expansions is covered or decided against with its reason recorded "
     "(`research/WORK_TYPE_COVERAGE_AUDIT.md`). **The only remaining step on any of its routes "
     "is runtime acceptance, which only the owner's launch can give**, so it belongs in the "
     "test phase rather than the working queue where it reads as something somebody could pick "
     "up."),

    ("x", "The remaining work/needs families, and every installed work giver in the 294-row "
          "profile.",
     "**CLOSED 0.12.99-dev, AND THE REMAINDER WAS MEASURED RATHER THAN LEFT AS AN UNKNOWN.** The "
     "row's last open piece read *\"ONLY REMAINDER: a mod-added work type with its own "
     "givers... it cannot be built against a mod nobody has named.\"* **Every mod in the profile "
     "is named** -- by the register, with a review card each -- and **288 of the 294 are "
     "installed on disk**, so the claim was checkable. Scanned 2026-10-05: **twelve profile mods "
     "add thirteen work types**, each giver class decompiled against its installed assembly "
     "rather than guessed at. **Exactly one is buildable and it is now built:** `MedicalTraining` "
     "from **Medical Dissection (register row 274)**, whose `WorkGiver_DoDissectionBill` derives "
     "from **`WorkGiver_DoBill`** and carries `fixedBillGiverDefs` -- so `BillWorkProvider`, "
     "which unions bench defs by capability and names nothing, already covered it. One provider "
     "registration, one giver def pair gated `MayRequire=\"Heremeus.MedicalDissection\"`, one "
     "label, and **no code anywhere referencing that mod**. **The other twelve are a closed "
     "decision with the reason recorded:** they are `WorkGiver_Scanner`, `WorkGiver_Warden` or "
     "`WorkGiver_RescueDowned` subclasses, and the only generic candidate query available "
     "(`PotentialWorkThingsGlobal`) reads `pawn.Map` -- the one map a deployment question is "
     "never about. All thirteen are tabulated in the audit so nobody re-derives this."),

    ("x", "**Resume step 4:**",
     "**CLOSED 0.12.99-dev.** Its one open child -- the remaining work/needs families -- closed "
     "in this batch against the thirteen mod-added work types measured off disk. **Saved work "
     "intents, quantity leases and native destination job revalidation ship, and so do physical "
     "hauling, construction, bills, research, medical, food and bed**, with priorities, "
     "schedules, areas, locks, custody and real inventory preserved -- `CrossingInventoryPolicy` "
     "is the inventory half, and it drops freight on the near side using **Core's own** "
     "`FirstUnloadableThing` keep-list so a pawn never loses its own medicine at a threshold."),

    ("x", "**Resume step 5:** \"Integrate exact optional work/storage providers and scenario "
          "openings,",
     "**CLOSED 0.12.99-dev, and the optional-provider half is a register decision rather than "
     "unwritten code.** The pointer said *\"optional provider adapters, on their own row "
     "below\"* and no such row exists. Reading the register instead of the pointer settles it: "
     "**every mod in the storage and hauling family has a final disposition of use-native, keep "
     "the vanilla fallback, no patch.** Row **164 Pick Up And Haul** says it in its own words -- "
     "*\"Cross-map work is unaffected by design: the connected families run their own job driver "
     "and work givers, not `WorkGiver_HaulGeneral`, so this mod has no seam to patch\"* -- and "
     "names the one real hole, a worker crossing with gathered inventory, **which is already "
     "closed by `CrossingInventoryPolicy`**. Row 157 OgreStack is *configuration only*. The "
     "rest of the row ships: **procedural inhabitants** (twelve defs), **rare monstrosities**, "
     "**saved events**. **The one piece genuinely open is the T5 and T6 research bands**, which "
     "has its own row naming the subject rather than a position."),

    ("T", "**Resume step 6:**",
     "**MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words.** It says *\"Open and "
     "structurally must stay open: runtime acceptance, because only the owner launches.\"* "
     "**Every source and build milestone it asks for is met** -- build, evidence folder, build "
     "record, ticks, cascade -- and the cascade is now twelve refs with the tool receipting "
     "itself. What is left is acceptance, and acceptance is a launch. **A row whose only "
     "remaining step is an owner launch does not belong in the working queue.**"),

    ("x", "Optional profile interfaces and native priority/schedule/restriction coverage.",
     "**CLOSED 0.12.99-dev.** The pointer said *\"the optional provider interfaces, on their own "
     "row below\"* and no such row exists. **The interfaces are built and they are the only "
     "shape the register permits:** `InstalledIntegrations` is a read-only statement of which "
     "tracked optional mods are loaded and what this package's position on each is, by register "
     "row, with ids read from the register's own CSV. **The register forbids the obvious build "
     "in its own words** -- row 247 and row 281 both say *\"No patch or code/assets copied\"*, "
     "and row 11 says *\"do not add vehicles solely because the framework is installed\"*. So a "
     "hook here cannot be a patch and cannot make any Rimrooms route depend on anything. "
     "**Nothing reads the class, asserted by proof**, because a detection layer that starts "
     "deciding things is how that instruction gets broken by accident. Native priority, schedule "
     "and restriction handling closed earlier and is archived."),

    ("x", "Containment, interviews, settlement openings, outposts, vehicles, VGE hooks.",
     "**CLOSED 0.12.99-dev -- ALL SIX SUBJECTS ARE SETTLED, and the row was being held open by a "
     "pointer to rows that do not exist.** It said *\"vehicles and the VGE hooks, each listed "
     "individually above\"*; there is no such row for either, and checker 25 now refuses that "
     "construction. **Vehicles and the VGE hooks are built** -- `InstalledIntegrations` tracks "
     "register rows **11 Vehicle Framework**, **249 Vanilla Vehicles Expanded**, **247 VGE "
     "Chapter 1** and **281 VGE Chapter 2**, and its header records why that read-only shape is "
     "the whole deliverable rather than a reduced one: all four cards forbid patching or copying, "
     "and row 281 makes a connected mission *\"only a future optional bridge **after "
     "verification**\"* -- which is a launch, not code. Containment closed 0.12.90-dev; "
     "interviews 0.12.28-dev; settlement openings and outposts 0.12.13-dev. **Nothing on this "
     "row is open any more.**"),
]

# Prose that is not a row and therefore has no status, fixed in place by replacement because
# every original word of it survives in the replacement text.
PROSE = [
    ("Four genuine gaps remain, recorded below as new rows because this is new information "
     "rather than a restatement.",
     "Four genuine gaps remain, recorded below as new rows because this is new information "
     "rather than a restatement. **ALL FOUR WERE BUILT AT 0.6.7-dev AND ARE ARCHIVED, so this "
     "sentence described four rows that no longer exist** -- `DarkStudy`, hauling upkeep, "
     "`BasicWorker` and `Fishing`. Corrected 0.12.99-dev by checker 25, which refuses a "
     "statement of open work resolved by position: a pointer survives the thing it points at, "
     "and this one advertised four pickups with nothing behind them."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    missed = []
    done = 0
    for status, phrase, evidence in EDITS:
        hits = [i for i, line in enumerate(lines)
                if line.lstrip().startswith(("- [ ] ", "- [~] ", "- [T] ")) and phrase in line]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        index = hits[0]
        raw = lines[index]
        lead = raw[:len(raw) - len(raw.lstrip())]
        body = raw.lstrip()[6:].rstrip()
        letter = status if status else raw.lstrip()[3]
        lines[index] = "%s- [%s] %s -- %s" % (lead, letter, body, evidence)
        done += 1

    for old, new in PROSE:
        if text.count(old) != 1:
            missed.append((old[:60], text.count(old)))
            continue
        joined = NL.join(lines)
        if joined.count(old) != 1:
            missed.append((old[:60], joined.count(old)))
            continue
        lines = joined.replace(old, new, 1).split(NL)
        done += 1

    if missed:
        for phrase, count in missed:
            print("NOT EDITED (%d matches): %s" % (count, phrase[:72]))
        print("refusing to write a partial batch")
        return 1

    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("edited %d row(s)/passage(s)" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
