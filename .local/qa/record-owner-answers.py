# -*- coding: utf-8 -*-
"""Record the owner's answers to twelve blocking questions, verbatim, and close what they settle."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner answers — twelve blocking questions, asked and answered (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"okay use ask me questions to clear everything up with each question and subquestion having write in ability\"*",
"",
"Twelve decisions were blocking work and are now made. **Every answer is recorded verbatim**, including the two that were written in rather than chosen from a list.",
"",
"| Question | Verbatim answer |",
"|---|---|",
"| Room count for the deep bands | *\"Raise to 80 as a middle\"* |",
"| Expansion-optional content | *\"option 2 and 3 not thin but thick\"* |",
"| A `Backrooms` PlanetLayer | *\"Don't add one — close all three\"* |",
"| Outpost / town-distortion / company-in-crisis starts | *\"Write briefs for all three\"* |",
"| Steam and the Workshop through Playwright | *\"Not yet — ask again when the mod is ready to publish\"* |",
"| A real domain | *\"Not yet — leave it on the github.io path\"* |",
"| Save migration | *\"Development-save break is allowed — declare it\"* |",
"| Research T5/T6 | *\"Sweep the constants and propose the tiers to you\"* |",
"| How thick the expansion content is | *\"option 1,2,3 but all deffered thats massive\"* |",
"| Entity and anomaly design sheets | *\"option 1 but also deffered as this is deep\"* |",
"| Catalogue and exchange-rate balance | *\"Make them player-visible settings\"* |",
"| The launch-blocked rows | *\"They stay blocked — I'll launch when I launch\"* |",
"",
"- [x] **\"Raise to 80 as a middle\"** — **BUILT AND MEASURED 0.12.98-dev.** `MaxSlotsPerAxis` 8 → **9** and `MaxRooms` 60 → **80**, because eighty rooms needs eighty-one slots to sit in. **Measured over 200 seeds at seven depths before it was kept:** depth 1 and 2 **did not move at all** (33 and 47 rooms — their grids are below the ceiling either way, which is the shallow look protected); **depth 3 went 60 → 63 rooms and its fill went UP**, 44.9% → 47.1%; **depth 4 and deeper reach the full eighty** at 42.6% fill, 2.3 points below where they were. `refused 0/200` and `fellback 0` at every band, degree **5.22 → 5.49**, back-to-back pairs **3,115 → 3,194**. "
"**The cost is in the span and it is the honest trade:** the widest room at depth 4+ falls **62 → 54 cells**. That is *\"going deeping in can mean the numner of branch hallways and rooms distancing from the main portal spawn\"* arriving in the numbers. **And both doc comments that asserted the old values were rewritten** — one said `MaxRooms` was *\"unchanged at 60\"* and the grid *\"64 slots\"* — because a stale comment is what somebody reads when they write a page.",
"- [x] **\"Don't add one — close all three\"** — **ALL THREE PLANETLAYER ROWS CLOSED 0.12.98-dev on the owner's decision, with the measurement that informed it recorded.** The five-map cap is **not layer-aware**: `SettleUtility.PlayerSettlementsCountLimitReached` counts `map.IsPlayerHome && map.Parent is Settlement` plus gravship landings, and a coordinate is a `RimroomsDestinationMapParent`, so **our maps already do not count against it** — `OpenMapBudget` counts them deliberately instead. A layer would therefore buy no capacity, and it **would** add a navigable world-view surface with its own gizmo and tab that a player would reasonably expect to work. **Nothing is lost by not having one**, and the two unmeasured unknowns stop mattering because nothing hangs on them.",
"- [x] **\"Development-save break is allowed — declare it\"** — **DECLARED 0.12.98-dev, and this is the standing position from here.** Saves **may** break between development versions, **no migration is owed**, and the old build is preserved so a save can be opened with the build that wrote it. It matches what the owner said earlier and has not changed: *\"we dont have other peoples saves we just publish it all and update it as we go fixing bugs\"*. **This unblocks removing the one remaining legacy def** — the hidden analysis bench, which new starts already do not spawn, cannot be built, and no company job uses. `SAVE_MIGRATION_POLICY.md` records the terms; the obligation begins at first publication, not now.",
"- [x] **\"Not yet — ask again when the mod is ready to publish\"** — **STEAM IS UNTOUCHED AND STAYS UNTOUCHED 0.12.98-dev.** No Playwright, no account access, no page, no collection. **Recorded as a decision with a trigger rather than as a blocked row**: the question is asked again when the mod is ready to publish, and until then nothing in this project reaches Steam. The write-ups remain authoring work that can be done from the same source as the site whenever they are wanted, so three descriptions of one mod cannot disagree.",
"- [x] **\"Not yet — leave it on the github.io path\"** — **NO DOMAIN, AND NOTHING NEEDS UNDOING LATER 0.12.98-dev.** Every link the site emits is **relative**, so it follows whatever domain serves it; `CNAME.example` already documents the file and `check-doc-conformance` already refuses a malformed one. **So the work when a domain arrives is one file and two DNS records, not a rewrite.**",
"",
"### Deferred as major work, on the owner's own words",
"",
"**Two answers deferred rather than scheduled, and both say why in the owner's words:** *\"option 1,2,3 but all deffered thats massive\"* and *\"option 1 but also deffered as this is deep\"*. **`DEFERRED.md` is closed and never takes a row**, so these move to `docs/ROADMAP.md`, which is the ledger for major grain — that is a grain escalation rather than a parking space, and the decision travels with them.",
"",
"- [x] **The four expansion rows — Royalty, Ideology, Biotech, Odyssey — moved to `ROADMAP.md` as one major item 0.12.98-dev.** The decision is made and recorded: **all four get thick content, not thin hooks**, a gravship that carries a branch is the headline, and **a brief comes before any code** so the largest remaining piece of work is not built on a guess. Nothing is required, every piece stays absent-safe, and the stand-alone guarantee is untouched. **It leaves the working queue because it is a milestone, not a task.**",
"- [x] **Entity and anomaly design sheets moved to `ROADMAP.md` 0.12.98-dev**, scoped by the owner's choice: **sheets for the twelve inhabitants that actually ship** — each with its readable tell, its limit and its counter — rather than designing entities that do not exist. **Documenting what is real, not inventing more.**",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "twelve blocking questions" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d closed" % SECTION.count("- [x] "))
