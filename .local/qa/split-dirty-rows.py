"""Split the open rows of docs/TODO.md that carry finished-work narrative inside them.

Owner direction, 2026-10-02, verbatim:
  "we need to move all finished items to finalized.md from the todo, the todods
   sahll never hold completed items, they are always to be moved to finalized
   first then deleted from the todods once confirmed virbatium transfer"
and, on being shown the queue still at ~96 KB after the row-level pass:
  "BEcause the todos are still like 100kb and i know that not all unfinished work
   and only unfinished work like it shall be"

THE PROBLEM
-----------
The row-level mover takes `[x]` rows. It cannot see a finished item written INSIDE
an open one -- and that is where the rest of the weight was. One `[~]` row is
3,796 characters, of which roughly 3,000 are SIX COMPLETED PASSES: "FIRST PASS
BUILT 0.6.2-dev ... SIXTH PASS BUILT 0.6.7-dev", three implementation records, and
a closing sentence naming the one thing actually left.

So each row below is split in two:

  * what STAYS in the queue: the original ask, verbatim and untouched, plus the
    clause that says what is actually left;
  * what goes to the ARCHIVE: the closure narrative, verbatim.

Nothing is summarised away. The full original row is written to `FINALIZED.md`
before the queue is touched, so every word of the narrative stays recoverable --
the point is only that a record of finished work does not live in a work queue.

WHAT IS NOT DONE HERE
---------------------
Two rows carry a remainder clause that CONTRADICTS a row closed elsewhere, and
neither is quietly resolved -- resolving a contradiction is a judgement for the
owner, not a side effect of a file move. Both are reported and left as written.
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINALIZED = os.path.join(REPO, "docs", "FINALIZED.md")

BEGIN = "<!-- archived-queue:begin -->"
END = "<!-- archived-queue:end -->"

# (unique prefix of the row, text that replaces the whole row)
#
# The prefix is matched against the row's full line and must hit exactly one row.
# The replacement keeps the ask verbatim; `[C]` marks where the closure history
# was lifted out, pointing at the archive.
SPLITS = [
 ("- [~] Implement every open item in [connected colony portals]",
  "- [~] Implement every open item in [connected colony portals](CONNECTED_COLONY_PORTALS.md#required-implementation-backlog): independent connection ownership, permanent natural portals, free crossing, shared cross-map work/materials, persistent seeds and dynamic inhabitants/complexity. This supersedes dispatch-only travel as the target. — **PARTLY BUILT**; what shipped is archived. **Open:** the individual routes listed below."),

 ("  - [~] The remaining work/needs families, and every installed work giver",
  "  - [~] The remaining work/needs families, and every installed work giver in the 294-row profile. **Next (2026-09-29):** cleaning, repair, firefighting, plants/mining/hunting, prisoner and guest care, wardening, childcare, animals and mechs, refuel and rearm, joy, rituals, hauling providers. Expect most to be short: the deployment shape covers anything done at the far site, and the carry shape covers anything delivered. Read the relevant profile rows for each before writing. — **31 families built, 23 of them deployments; every Core and DLC work type is covered or decided against with its reason recorded. Six build passes archived.** **ONLY REMAINDER: a mod-added work type with its own givers.** The bill family covers modded *benches* inside existing work types automatically, but a wholly new work type gets no provider, because the providers and their giver defs are shipped rather than derived — and it cannot be built against a mod nobody has named. Coverage: [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md), 23 work types, 145 giver defs."),

 ("- [~] **Resume step 5:**",
  "- [~] **Resume step 5:** \"Integrate exact optional work/storage providers and scenario openings, then procedural inhabitants, rare monstrosities, saved events and tech-driven complexity. Keep every wider master TODO feature in scope.\" — **Open:** optional provider adapters, on their own row below. (Scenario openings closed; archived.)"),

 ("- [~] **Resume step 6:**",
  "- [~] **Resume step 6:** \"Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change.\" — each milestone: `./tools/build.ps1`, evidence folder under `implementation/evidence/<name>-<date>/`, build record, master TODO ticks, then cascade-publish per `PUBLISHING.md`. — **Open and structurally must stay open:** runtime acceptance, because only the owner launches."),

 ("- [~] Optional profile interfaces and native priority/schedule/restriction coverage.",
  "- [~] Optional profile interfaces and native priority/schedule/restriction coverage. — **Open:** the optional provider interfaces, on their own row below. (Native priority, schedule and restriction handling closed; archived.)"),

 ("- [~] **Adapter families, one at a time with source evidence per route:**",
  "- [~] **Adapter families, one at a time with source evidence per route.** Eighteen families and decisions closed in order from 0.5.0-dev to 0.6.7-dev; the sequence and the reason for each is archived. Sources: [`research/WORK_TYPE_COVERAGE_AUDIT.md`](research/WORK_TYPE_COVERAGE_AUDIT.md), `CONNECTED_WORK_CORE_API.md`, `CONNECTED_WORK_PROFILE_BOUNDARIES.md`. — **Open:** this row's own remainder clause reads *\"Surgery across a gate is the named remainder\"*, and the surgery row was separately CLOSED at 0.12.33-dev as something Core forbids being built. **Flagged 2026-10-02 rather than resolved** — see *Contradictions found while splitting rows* below."),

 ("- [~] Replace custom creature presentation, room fixtures and terrain",
  "- [~] Replace custom creature presentation, room fixtures and terrain with existing native/provider content, retaining learned rules, encounters, procedural variation and saved routes. — **Open:** `RR_QuietPursuer` presentation, the last one, queue item 6. (Room fixtures and terrain closed; archived.)"),

 ("- [~] Replace the historical custom gameplay items, benches, terrain, sprites and audio",
  "- [~] Replace the historical custom gameplay items, benches, terrain, sprites and audio with source-verified existing Core/profile content and saved role bindings; preserve the gate, field gear, evidence, threat and discovery functions. Follow `CONTENT_REUSE_POLICY.md` and the existing-content replacement map. *(master TODO Phase 5)* — **Open:** fourteen historical gameplay PNGs still in the package allowlist; they come out once the last references go, which is gated on the `RR_QuietPursuer` decision. (Items, benches and terrain closed; archived.)"),

 ("- [ ] **Still unbuilt from the same prep document:**",
  "- [ ] **Still unbuilt from the same prep document:** *\"contradictory accounts\"* from a returning crew - a report that does not match what another crew saw - and staff **prior exposure** affecting how an expedition goes. — **Open:** staff prior exposure. (Contradictory accounts closed 0.12.25-dev; archived.)"),

 ("- [~] Add staff role recommendations, field kit assignment, readiness checks",
  "- [~] Add staff role recommendations, field kit assignment, readiness checks, and basic company tasks while retaining vanilla pawn/work controls. — **Open:** nothing new; field kit assignment is **superseded** with the rest of the custom field gear. Closure archived — review whether this row should now be `[x]`."),

 ("- [ ] Add analyze/interview/compare/review workflows",
  "- [ ] Add analyze/interview/compare/review workflows for equipment, furniture, people, entity remains, recordings, transcripts, route notes, and recovered documents. — **Open:** **review**, the last of the four. (Analyse, interview and compare all closed by 0.12.28-dev; archived, along with the retired-vocabulary sweep that rode with it.)"),

 ("- [~] Add repeated missing-person mysteries with radio fragments",
  "- [~] Add repeated missing-person mysteries with radio fragments, missing crews, delayed return, witness conflict, reappearance/death, rescue, and case closure. — **Open:** radio fragments. (Case records, missing status, the lost-pawn register, the missing-residents request family and witness conflict all closed; archived.)"),

 ("- [~] Complete research branches for facility/power, engineering",
  "- [x] Complete research branches for facility/power, engineering, field safety, equipment, mapping, communication, stability, containment, medicine, logistics, commerce, orbital operations, and deep topology. — **CLOSED 0.12.29-dev: the ladder is complete, tiers 0 to 4.** Flipped from `[~]` to `[x]` on 2026-10-02 because the row's own body already said so — *\"TIER 4 BUILT ... AND THE LADDER IS COMPLETE\"* — and nothing in it named anything left. Detail archived."),

 ("- [~] Containment, interviews, settlement openings, outposts, vehicles, VGE hooks.",
  "- [~] Containment, interviews, settlement openings, outposts, vehicles, VGE hooks. — **Open:** containment, vehicles and the VGE hooks, each listed individually above. (Settlement openings and outposts closed 0.12.13-dev; interviews closed 0.12.28-dev; archived.)"),

 ("- [~] Royalty conditional content:",
  "- [~] Royalty conditional content: titles/quests/faction/psycasts only as optional company routes. — **Open:** no Royalty-specific content is authored. That is honest rather than a gap: it must be an optional route or nothing. (Gating mechanism closed and enforced; archived.)"),

 ("- [~] Ideology conditional content:",
  "- [~] Ideology conditional content: beliefs, meditation, rituals, staff policies, and recreation only when available. — **Open:** no Ideology-specific content authored. (Gating closed; archived.)"),

 ("- [~] Biotech conditional content:",
  "- [~] Biotech conditional content: genes, mechanitors, children, medicine, pollution, and mechanoid options; no mandatory gene/resource dependency. — **Open:** no Biotech-specific content authored. Nothing is mandatory. (Gating closed; archived.)"),

 ("- [~] Anomaly conditional content:",
  "- [~] Anomaly conditional content: containment/research links; Backrooms entities retain a base-game implementation. — **Open:** the containment/research links themselves. (Gating closed, and the Backrooms entities **do** retain a base-game implementation, which is the load-bearing half; `SecurityDoor` is already recognised as a 2x1 gate when present. Archived.)"),

 ("- [~] Odyssey conditional content:",
  "- [~] Odyssey conditional content: gravship/off-world logistics and any compatible space travel. — **Open:** no gravship integration is written, and it stays DLC-optional throughout. (Gating and arc 7's request families closed; archived.)"),

 ("- [~] For each workbook row, close its status with evidence:",
  "- [~] For each workbook row, close its status with evidence: reviewed version, load-order placement, applicable DLC, behavior used/preserved, patch/adaptor/no-code reason, and result. — **Open, and the remainder is in dispute.** This row says 14 of 21 register families swept with 7 to go; the retro-sweep row closed at 0.12.42-dev saying **all twenty-one are done**. **Flagged 2026-10-02 rather than resolved** — see *Contradictions found while splitting rows* below."),

 ("- [~] Make each screen deep-link",
  "- [~] Make each screen deep-link to the relevant pawn, building, map, quest, item, research project, evidence record, contract, or RWT site. — **Open:** deep links out to a pawn, building or research project. (Pane-to-pane links closed; archived.)"),

 ("- [~] Eleven-pane Company Command, deep links, reason codes, native menu remap.",
  "- [~] Eleven-pane Company Command, deep links, reason codes, native menu remap. — **Open:** deep links are partial, and the native menu remap is open and questioned on its own row above. (Twelve panes and reason codes closed; archived.)"),

 ("- [~] Slideshow integration review, additional menu images per shipped scenario.",
  "- [~] Slideshow integration review, additional menu images per shipped scenario. — **Open, and it needs a launch:** the integration **review** itself — how the slides read behind the menu buttons, and whether 30 s dwell and 2 s crossfade feel right — cannot be judged from here. (Six slides and `proof-menu-slides.py` closed at 0.12.17-dev; archived.)"),

 ("- [~] **PART BUILT 0.9.2-dev.** Costs-more-to-run",
  "- [~] **Gate size and what it lets through.** **\"allow differnt capabilities\"** — width is the capability. **Open:** what size lets *through* (body size at the traversal chokepoint); hostiles needing width; how many people cross abreast; whether bulk cargo, pack animals or a vehicle fits; and what the opening draws. To be specified per size as part of the multi-cell gate work. (Costs-more-to-run and more-people-abreast closed 0.9.2-dev, with **no quota anywhere** per *\"we dont want limitations\"*; archived.)"),

 ("- [~] **PART BUILT 0.9.3-dev** for our own defs",
  "- [~] **Informational text on the inspect cards** for everything a player can select or inspect: gates, the station, the beacon, bonds, coordinates and the rest. What it is, what it needs, and why it is not working when it is not. **Open:** an audit of inspect-card text on the station and the beacon, the way the gate already has one. (Our own defs closed 0.9.3-dev — the facilities overview and the procurement list are described and rendered; archived.)"),

 ("- [~] **\"start on the todo weork\"**",
  "- [~] **\"start on the todo weork\"** — **Open:** resume step 4's remaining families, listed under Major M1. (Resume steps 1 to 3 and the gate traversal rule closed in 0.4.2-dev and 0.4.3-dev; archived.)"),
]

CONTRADICTIONS = [
 ("Adapter families / surgery across a gate",
  "The adapter-families row's remainder clause says *\"Surgery across a gate is the named remainder\"*. "
  "The surgery row was separately **CLOSED at 0.12.33-dev** with the finding that it **cannot** be built: "
  "`Bill_Medical.GiverPawn` is the bill giver, so the patient *is* the bill, `WorkGiver_DoBill` reserves it "
  "per-map, and ingredients are searched on the doctor's map around the patient -- doctor, patient and "
  "ingredients must be co-located, so there is no seam and the patient comes home instead. "
  "**If that closure stands, the adapter-families row has no remainder and should be `[x]`.** Not flipped "
  "here: promoting a row on an inference is the thing that put twenty-two unticked rows under headings "
  "saying DONE."),
 ("Workbook rows / the register retro sweep",
  "The workbook row says **14 of 21** register families swept, **7 to go** (medical, world operations, cargo, "
  "hospitality, materials, visitor economy, staff psychology). The retro-sweep row closed at **0.12.42-dev** "
  "stating **all twenty-one families are done**, with four new checker rules and a medical-family finding. "
  "**One of the two is wrong and they cannot both be current.** Not resolved here, because deciding which "
  "is true needs the register read rather than a file moved."),
]


def main():
    apply_it = "--apply" in sys.argv
    text = io.open(TODO, encoding="utf-8").read()
    lines = text.split("\n")

    plan = []
    problems = []
    for prefix, replacement in SPLITS:
        hits = [index for index, line in enumerate(lines) if line.startswith(prefix)]
        if len(hits) != 1:
            problems.append("%d matches for %r" % (len(hits), prefix[:70]))
            continue
        plan.append((hits[0], lines[hits[0]], replacement))

    print("split-dirty-rows")
    print("  splits authored          : %d" % len(SPLITS))
    print("  matched exactly once     : %d" % len(plan))
    if problems:
        print("  PREFIX PROBLEMS:")
        for problem in problems:
            print("      %s" % problem)
        raise SystemExit(1)

    before = sum(len(old) + 1 for _index, old, _new in plan)
    after = sum(len(new) + 1 for _index, _old, new in plan)
    print("  bytes in those rows      : %.1f KB" % (before / 1024.0))
    print("  bytes after the split    : %.1f KB" % (after / 1024.0))
    print("  net reduction            : %.1f KB" % ((before - after) / 1024.0))
    print("  contradictions flagged   : %d" % len(CONTRADICTIONS))

    if not apply_it:
        print()
        print("  PLAN ONLY. Nothing written. Re-run with --apply.")
        return 0

    # ---- archive the FULL original rows first -------------------------------
    archive = []
    archive.append("")
    archive.append("---")
    archive.append("")
    archive.append("## Archived from the queue - finished work written inside open rows (2026-10-02)")
    archive.append("")
    archive.append(BEGIN)
    archive.append("")
    archive.append("**Verbatim owner direction (2026-10-02):** *\"we need to move all finished items to "
                   "finalized.md from the todo, the todods sahll never hold completed items, they are "
                   "always to be moved to finalized first then deleted from the todods once confirmed "
                   "virbatium transfer\"*")
    archive.append("")
    archive.append("**And, on being shown the queue still large after the row-level pass:** *\"BEcause the "
                   "todos are still like 100kb and i know that not all unfinished work and only unfinished "
                   "work like it shall be\"*")
    archive.append("")
    archive.append("**The row-level mover takes `[x]` rows. It cannot see a finished item written INSIDE an "
                   "open one, and that is where the rest of the weight was.** One `[~]` row was **3,796 "
                   "characters**, of which roughly 3,000 were **six completed build passes** - FIRST PASS "
                   "BUILT 0.6.2-dev through SIXTH PASS BUILT 0.6.7-dev - three implementation records, and "
                   "one closing sentence naming the single thing actually left. Twenty-six rows were like "
                   "that to some degree.")
    archive.append("")
    archive.append("Each row below is reproduced **whole and unaltered** as it stood in the queue. What was "
                   "left in `docs/TODO.md` is the original ask, verbatim, plus the clause saying what is "
                   "actually open. **Nothing was summarised away** - every word of every closure narrative "
                   "is here, which is what makes removing it from a work queue safe.")
    archive.append("")

    for _index, old, new in plan:
        archive.append("> moved from `docs/TODO.md`; the row now reads:")
        archive.append("")
        archive.append(new)
        archive.append("")
        archive.append("**Full original row, verbatim:**")
        archive.append("")
        archive.append(old)
        archive.append("")

    archive.append("### Contradictions found while splitting rows, flagged and NOT resolved")
    archive.append("")
    archive.append("Two rows carry a remainder clause that contradicts a row closed elsewhere. **Resolving "
                   "a contradiction is a judgement, not a side effect of a file move**, so both are "
                   "reported and left exactly as written.")
    archive.append("")
    for title, body in CONTRADICTIONS:
        archive.append("- **%s.** %s" % (title, body))
        archive.append("")

    archive.append(END)
    archive.append("")

    existing = io.open(FINALIZED, encoding="utf-8").read()
    io.open(FINALIZED, "w", encoding="utf-8", newline="").write(
        existing.rstrip("\n") + "\n" + "\n".join(archive)
    )
    written = io.open(FINALIZED, encoding="utf-8").read()
    missing = [old for _index, old, _new in plan if old not in written]
    if missing:
        io.open(FINALIZED, "w", encoding="utf-8", newline="").write(existing)
        raise SystemExit("ABORT: %d original rows not present in the archive; FINALIZED.md "
                         "restored, queue untouched." % len(missing))

    # ---- only now rewrite the queue -----------------------------------------
    for index, _old, new in plan:
        lines[index] = new
    io.open(TODO, "w", encoding="utf-8", newline="").write("\n".join(lines))

    print()
    print("  docs/FINALIZED.md        : archive appended, %d lines" % len(archive))
    print("  verbatim confirmation    : all %d original rows present" % len(plan))
    print("  docs/TODO.md             : %d lines, %.1f KB"
          % (len(lines), sum(len(line) + 1 for line in lines) / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
