# -*- coding: utf-8 -*-
"""Record the first launch session: the owner's verbatim direction, four answers, and the read.

LAW #0: every word of the direction goes in. One row per item in the list, never a bundle.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "## Public face: the site, the Workshop page and the collection"

S = NL.join([
"### Owner direction — the first launch: the facility is fixed by hand, the research is invisible, and the journals are wrong (2026-10-06)",
"",
"**Verbatim owner report (2026-10-06), the facility work:** *" + Q + "okay ive started the game and "
"fixed the company facility to how it needs to be, ive added and removed some walls(granite and "
"steel), ive added generatorsand moved some generators), ive added ac units, ive moved a bench or "
"two maybe, ive added hidden conduit where needed and missing(existing and added conduit needs to "
"the vanilla type, not sure if hidden conduit is vanilla), ive removed too many heaters, ive moved "
"some batteries, ive added vents for thhe rooms(and ac units for the main corradoor all vents "
"connect to), you can see the door i moved and set to the gate and where i want it with steel walls "
"on both sides of it and readjusted the room by dleteing some walls." + Q + "*",
"",
"**And verbatim on what must be added:** *" + Q + "We will also need trade beacons in middle of "
"rooms that already have shelfs in them(if room doesnt have a shelf no trade beacon is wanted and "
"not required. and i built a card table and chairs the card table i couldnt complete becasue no "
"cloth(dont worry about cloth) but the card table need to be built and complete when u add it and "
"its charis. and i set 4 ac units to below freezing for a freezer(those should be in the scenerio "
"correctly) ANd thhese places i put everything is exact and purposfully and should use them "
"exactly." + Q + "*",
"",
"**THE READ IS DONE AND SAVED, so none of it depends on the game still being open.** "
"`docs/implementation/evidence/facility-read-2026-10-06/company-facility-changes.txt`, with the raw "
"2,116-cell snapshot kept out of the repository in `.local/qa/`. "
"**The first read was aimed at the wrong place and said so loudly rather than quietly:** it "
"returned 2,116 cells of unexplored mountain, because the authored layout is in its own coordinates "
"and `GenStep_Headquarters` offsets it onto whatever map the player chose. The owner's map is "
"**300×300**, the footprint is 44×44 at (8, 8), so the offset is **(120, 120)** — **confirmed by "
"probing the authored `CommsConsole` and finding it exactly where predicted**, not merely computed.",
"",
"- [~] **Apply the owner's facility changes to `RR_AsyncIndustriesStart`.** Measured against the "
"authored layout, with the generator's own wall rule reconstructed so the report was readable: the "
"raw diff claimed **647 additions** because every room rectangle's edge is a generated `Wall` and "
"those are not in `<buildings>`. Classified: **510 walls, 22 doors and 127 authored things "
"unchanged**; **4 walls added** — `(38,41)` and `(40,41)` **Steel**, `(43,39)` and `(43,44)` "
"granite; **26 authored wall cells now open**, of which **20 hold a wall-mounted thing** (13 "
"`Vent`, 7 `Cooler`) and **6 are genuine deletions** at `(37,34) (38,34) (40,34) (41,34) (42,39) "
"(42,44)`; **36 conduit cells added and 8 no longer there**; **60 cells of added building across "
"13 kinds**; and **10 authored things absent**. "
"**The gate door is legible in the data exactly as described:** an `Autodoor` at `(39,41)` that is "
"on no authored wall cell, flanked by the two Steel walls, with the old doorway run at "
"`(37..41, 34)` deleted.",
"  - [ ] **The generator cannot place a vent or a cooler yet, and that is the blocker for 20 of "
"the 26.** The buildings loop throws `Headquarters furniture intersects a wall/building` on any "
"cell already holding an edifice — correct for an authored overlap, wrong for a `Cooler`, whose "
"whole purpose is to sit in a wall. The fix is to honour the game's own `canPlaceOverWall` and "
"replace **our own** wall on that cell, which is exactly what the game does when a player builds "
"one. **Not a special case for two defs: a property the game already publishes.**",
"  - [ ] **Six genuine wall deletions need a way to be expressed.** Walls are generated from the "
"room rectangles, so a deletion is not a building edit. Either the rooms are re-authored or the def "
"gains a list of cells where no wall is placed. **The second is smaller and does not move three "
"room rectangles to express six cells.**",
"  - [ ] **Trade beacons, one per room that already holds a shelf.** Owner: *" + Q + "if room doesnt "
"have a shelf no trade beacon is wanted and not required" + Q + "*. **38 live shelf cells** across "
"the storage rooms and the gate hall; **no trade beacon exists anywhere** in the facility today. "
"The siting rule is the owner's: the middle of the room, not beside a shelf.",
"  - [ ] **The card table ships complete.** Owner: *" + Q + "the card table need to be built and "
"complete when u add it and its charis" + Q + "*, and *" + Q + "dont worry about cloth" + Q + "*. "
"It read back as **four `PokerTable` frames**, not a finished table, because the owner could not "
"finish it — so the def places the finished thing and its four `Stool`s, and the material question "
"is settled by the owner saying to ignore it.",
"  - [ ] **The four freezer coolers carry their temperature.** Owner: *" + Q + "i set 4 ac units to "
"below freezing for a freezer(those should be in the scenerio correctly)" + Q + "*. They are the "
"four at `(51,19)`–`(51,22)`. A `Cooler`'s target temperature is comp state rather than a spawn "
"argument, so the def needs a field for it the way `batteryFraction` and `fuelFraction` already "
"exist. **A freezer that ships at room temperature is a freezer that quietly is not one.**",
"  - [ ] **Two absent `TextBook`s are NOT deletions and must not be removed from the def.** A "
"`TextBook` is an `Item`, not a building, so a pawn hauls it; the two authored at `(11,47)` and "
"`(14,47)` are simply somewhere else. **The other eight absences are real** — six `Heater`, one "
"`ElectricStove`, one `ElectricSmithy` — and match the owner's own words, *" + Q + "ive removed too "
"many heaters" + Q + "*.",
"",
"**Verbatim owner answer (2026-10-06), asked whether hidden conduit is vanilla:** *" + Q + "All "
"HiddenConduit" + Q + "*. **Both ship in Core** — `PowerConduit` and `HiddenConduit` are Core defs, "
"so the owner's doubt is answered: neither is a mod's. Live the facility holds **193 ordinary and "
"40 hidden**; the def will place **hidden everywhere**.",
"",
"- [ ] **The starting conduit becomes `HiddenConduit` throughout.** The generator hard-codes "
"`ThingDefOf.PowerConduit`, so this is one lookup plus the live set recompressed into runs. The "
"existing *is this cell already a transmitter* test must keep working for both types, or a cell "
"carrying one kind would be given the other on top.",
"",
"### Owner direction — THE RESEARCH IS INVISIBLE WHERE PLAYERS LOOK FOR IT (2026-10-06)",
"",
"**Verbatim owner report (2026-10-06), in capitals:** *" + Q + "AND A MAJOR ISSUE: I DONT SEE ANY "
"RESEARCH FOR THE GATE SYSTEMS AND EVERYTHING THIS MOD HAS!!!!!" + Q + "*",
"",
"**Measured, and the branch is not broken.** `Player.log` carries "
"`[Rimrooms][Company] Initialized ... scenario=async_industries`, fixture tells attached to 1,794 "
"definitions, the odd-origin marker to 2,760, **and not one error or warning**. All **38 company "
"projects get a record at branch initialisation** — `CampaignServices` enumerates every "
"`RimroomsProjectDef` and seeds one each — and the Operations pane lists them. "
"**So nothing is missing; it is in the wrong place.** The projects are `RimroomsProjectDef` and "
"live in an Operations section, and the owner looked in the **Research tab**, which is where every "
"player looks and where this mod contributes nothing. The owner also runs **FluffyResearchTree** "
"and **MintResearch**, and both show nothing for the same reason. **The Operations pane's own "
"*Open Research* button points at the vanilla tab — away from our projects rather than toward "
"them.**",
"",
"- [ ] **Mirror every company project into the vanilla Research tab.** Owner's answer, verbatim: "
"*" + Q + "Mirror them into the vanilla Research tab" + Q + "*, chosen over a single announcing "
"project and over merely renaming the Operations section. So each company project also becomes a "
"real `ResearchProjectDef`: **nine branches by five bands, visible in Research, drawn by "
"FluffyResearchTree, listed by MintResearch**, with prerequisites shown. Clicking one goes to "
"Operations, where an insight is committed — the bespoke mechanics stay the way a project is "
"*advanced* and the vanilla tree becomes the **map**. "
"**The cost was stated before it was chosen and it is the real work:** 38 paired defs that must "
"not drift, so **a checker proves the pairing** — every `RimroomsProjectDef` has exactly one "
"mirror, every mirror has its project, and the labels, descriptions, branches and prerequisites "
"agree. A mirror that drifts is a research tree that lies about what it unlocks.",
"",
"### Owner direction — the journals, the quests, and how data gets back to the company (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06), the whole shape of it:** *" + Q + "this is big one to need "
"proper write up before attempting the work and using ask me question where forks and questions "
"about this intrical part of the jobs and quests and how the company recieves the starting journals "
"via droppod and picks up the quest one when propeted to complete a mission with a geen light to "
"show its ready to be sent to complete the quest mission, even the tutorial mission should have "
"options to fillout the dataand research for the gate steps and send that back to the COMPANY where "
"the journals are taken to a table and written out but these tasks are auto in the pawns work jobs "
"so after doing all the gate steps, each step has a lab nots, research write up, investigation, "
"analysis, ... what ever the task requires and what the company wants as far as data or anaylisiis "
"or retreval and such we can even have like a research bench thats togglable to handling the lab "
"nots write ups in jounrals and things and people brountgh back and major event reports i can think "
"of all kinds of ways tand things it all just need correct combing and integrations  and the seend "
"new journals after each quest finished/ starting new quests/missions, its almost like every book "
"recieved needs to be tuned to or capable of listing the current quests its needed for that has "
"been acceptred, with ability to accept more than one quests at a time and a variety to choose from "
"after the inital tutorial like quests." + Q + "*",
"",
"**And verbatim on the defect in the journals that ship today:** *" + Q + "the starting journals "
"still arnot correct(need to figure this out for generating ones purchased too) both are named "
"wrong and have differ information in the " + Q + "i" + Q + " write up saying incorrectly that one "
"is about nutrition and the othert is about aiming. so the journal shit is very important and needs "
"to be figured out proprly for what we need to be able to log things record whats needed with a "
"pawn click actions with sterp by step instructions how to use the journal but not wordy keep it "
"very concise asnd to the point and that shit all needs to be added propely to all the wikis shit "
"where relevant." + Q + "*",
"",
"**Two forks were put to the owner before any of it is built, as they asked, and both are answered:**",
"",
"- **Journal scope:** *" + Q + "Both — per-quest books plus a branch ledger" + Q + "*. A book per "
"accepted quest for the physical send-back, **and** one master journal listing them all with the "
"green lights. The ledger is the dashboard; the books are the deliverables.",
"- **Where the write-up happens:** *" + Q + "A dedicated write-up desk" + Q + "*. **This overrides "
"the owner's own content-reuse rule and is recorded as a deliberate exception rather than slipped "
"in.** `CONTENT_REUSE_POLICY.md` says gameplay content must use existing providers, with original "
"menu images as the only approved exception. The owner was shown that cost in the option text — "
"*" + Q + "it's a new buildable, and the standing content rule is to reuse existing game "
"content" + Q + "* — and chose it anyway, over a toggle on the existing research bench and over "
"any-table writing. **So the records desk is the second approved exception to that rule**, and it "
"is approved for this purpose only.",
"",
"- [ ] **Write the journal and quest brief BEFORE any code.** The owner's instruction is explicit: "
"*" + Q + "this is big one to need proper write up before attempting the work" + Q + "*. The brief "
"has to settle: the drop-pod arrival of the starting journals and of a new book per accepted quest; "
"the per-step write-up kinds the owner named — **lab notes, research write-up, investigation, "
"analysis** and whatever else a request asks for; the automatic pawn work job that does them at the "
"records desk; the **green light** that says a quest is ready to send; sending the book back; the "
"branch ledger that lists every accepted quest; accepting **more than one at a time**; and the "
"variety offered after the tutorial requests. **§1.2 binds every one of them: two routes of two "
"different kinds, and no clock on any of it.**",
"- [ ] **The starting journals are named wrong and describe the wrong subject.** Owner: both are "
"*" + Q + "named wrong and have differ information in the " + Q + "i" + Q + " write up saying "
"incorrectly that one is about nutrition and the othert is about aiming" + Q + "*. They are Core "
"`TextBook`s placed at `(11,47)` and `(14,47)`, so **they carry Core's own generated title and "
"description** — a vanilla textbook teaches a skill, and the two it rolled were nutrition and "
"shooting. **Repurposing an existing item kept its identity as well as its model.** The fix covers "
"the purchased ones too, which the owner asked for in the same sentence.",
"- [ ] **A journal needs pawn click actions with step-by-step instructions, kept short.** Owner: "
"*" + Q + "with a pawn click actions with sterp by step instructions how to use the journal but not "
"wordy keep it very concise asnd to the point" + Q + "*. **And it all goes into the wiki where "
"relevant**, which is the same sentence's second half and is not optional.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "THE RESEARCH IS INVISIBLE WHERE PLAYERS LOOK" in text:
        print("already recorded; nothing written")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("recorded the launch session: direction verbatim, four answers, and the read")
    return 0


if __name__ == "__main__":
    sys.exit(main())
