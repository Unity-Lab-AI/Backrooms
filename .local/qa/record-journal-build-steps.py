# -*- coding: utf-8 -*-
"""Put the journal system's build steps into the queue. The brief specified them; nothing tracked them.

**Closing the brief row made the whole system read as handled.** `docs/JOURNAL_AND_QUEST_BRIEF.md`
ends with a nine-step build order and the queue held rows for exactly two of them. A specification
nothing points at is the same as no specification, which is the shape of the defect this repository
already has a rule about: a row stale in its premise rather than its status.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — an unexplored room offers no work, and exploring is a thing you order (2026-10-06)"

S = NL.join([
"### Owner direction — the journal and quest system itself, which the brief specified and nothing tracked (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06), the whole shape of it:** *" + Q + "this is big one to need "
"proper write up before attempting the work and using ask me question where forks and questions about "
"this intrical part of the jobs and quests and how the company recieves the starting journals via "
"droppod and picks up the quest one when propeted to complete a mission with a geen light to show its "
"ready to be sent to complete the quest mission ... and the seend new journals after each quest "
"finished/ starting new quests/missions, its almost like every book recieved needs to be tuned to or "
"capable of listing the current quests its needed for that has been acceptred, with ability to accept "
"more than one quests at a time and a variety to choose from after the inital tutorial like "
"quests." + Q + "*",
"",
"**And verbatim when the owner asked what was left (2026-10-06):** *" + Q + "okay i think there is "
"still shit we havent complete in all ive been telling you" + Q + "*",
"",
"**They were right, and the hole was in the queue rather than in the work.** The brief closed its own "
"row at 0.12.99-dev and ends with a **nine-step build order**; the queue held rows for **two** of "
"them. **A specification nothing points at is the same as no specification** -- and worse here, "
"because a closed brief row reads as a finished system. Full design, section by section: "
"[`JOURNAL_AND_QUEST_BRIEF.md`](JOURNAL_AND_QUEST_BRIEF.md).",
"",
"**Done already, so these are not re-listed:** step 1, the naming fix (`RimroomsRecordBook`, the "
"startup binding, two unmarked issuing routes, checker 27, plant suite 35); the *" + Q + "What is "
"this journal for?" + Q + "* click action; and the record-book wiki pass.",
"",
"- [ ] **Step 2 -- the write-up kinds go on `RimroomsRequestDef` as data.** The owner's own list is "
"*" + Q + "each step has a lab nots, research write up, investigation, analysis, ... what ever the "
"task requires" + Q + "*, and **the ellipsis is the owner saying the list is open**, so a kind is "
"**declared on the request in XML** and never inferred from a quest's name. Data before the job that "
"reads it, which is why this is first: §4.1 of the brief sets out the four named kinds and what each "
"one requires the branch to already hold.",
"- [ ] **Step 3 -- the records desk, and the work giver that staffs it.** Owner's fork answer: "
"*" + Q + "A dedicated write-up desk" + Q + "*, chosen over a toggle on the research bench and over "
"any-table writing, **and recorded as the second approved exception to `CONTENT_REUSE_POLICY.md`.** "
"The art rule still binds: Core's own `Things/Building/Furniture/Table1x2`, verified present in "
"Core's `Buildings_Furniture.xml`. The job is *" + Q + "auto in the pawns work jobs" + Q + "*, so a "
"`WorkGiver` scans for a quest with an outstanding write-up **whose precondition is already met**. "
"**And the pawn is never trapped:** `GateWatch.MustLeave` is the floor here as it is at the console, "
"because a starved pawn at a desk is the same defect one subsystem over.",
"- [ ] **Step 4 -- one writer, two readers, then the green light.** The owner chose "
"*" + Q + "Both, and they must agree" + Q + "*, and the brief spends that risk down rather than "
"accepting it: the write-up job advances the record **and** stamps the book in a **single operation**, "
"record first. So a mismatch cannot be produced by the mod working normally -- only a foreign book, a "
"hand-edited save or damage. Three states: **dark** (write-ups outstanding), **green** (all done, "
"book present and in custody, book agrees), **amber -- unverified** (record complete, no agreeing "
"book). **Amber is why the record is the authority:** burn the book and you lose a deliverable, not a "
"month of work.",
"- [ ] **Step 5 -- the branch ledger, listing every accepted quest.** Owner: *" + Q + "with ability "
"to accept more than one quests at a time" + Q + "*. **Nothing ever prevented several at once** -- "
"`contracts` is a list and `rr.survey.onboarding.v1` is simply the only one a fresh branch is handed. "
"**What was missing is the index**, which is this: quest, coordinate, accepted, write-ups done of "
"required, the light, and what it pays. It lists **accepted** quests only, because a ledger that also "
"listed offers would be an offer board and the Operations pane is already that.",
"- [ ] **Step 6 -- the quest-bound click actions.** The instruction action shipped; these did not, "
"because each needs its underlying action to exist first: **Write up here** (sends the pawn to the "
"nearest free desk), **File in archive**, **Send to company** (only while the light is green). Owner: "
"*" + Q + "sterp by step instructions how to use the journal but not wordy keep it very concise asnd "
"to the point" + Q + "*, so four lines stays the ceiling.",
"- [ ] **Step 7 -- the book goes back by beacon radius.** The owner's fork answer, and it costs "
"nothing new: the same contract `ValuablesExchange` and Core's trade beacon already have -- *what is "
"in the circle is what is on the table* -- and **the facility already ships eight beacons** where the "
"owner placed them. Collection settles through `PostTransaction` on the existing operation id, so it "
"**cannot pay twice**. **§1.1 binds it: no deadline, ever** -- a finished book may sit on a shelf "
"indefinitely, and paperwork never costs a gate window, which a dispatch route would have.",
"- [ ] **Step 8 -- a new book per accepted quest, by drop.** Owner: *" + Q + "the seend new journals "
"after each quest finished/ starting new quests/missions" + Q + "*. Accepting a quest drops its book "
"through the **same** `DropPodUtility.DropThingsNear` path and the same relief drop cell "
"`RecordBookDelivery` already uses, so there is one delivery mechanism in the mod rather than two.",
"- [ ] **Step 9 -- variety after the tutorial, and the wiki for the quest half.** Owner: "
"*" + Q + "a variety to choose from after the inital tutorial like quests" + Q + "*. Three templates "
"exist (`rr.survey.onboarding.v1`, `rr.mission.oddconsignment.v1`, `rr.supply.odd.v1`) and a new "
"family is **XML, not code** -- a `RimroomsRequestDef` with its routes and its write-up list. The "
"tutorial stays first because it is what teaches the loop. **§1.2 binds every family ever added: two "
"routes of two different kinds, and no clock on any of it.** And the wiki gains the quest half, which "
"is the owner's *" + Q + "that shit all needs to be added propely to all the wikis shit where "
"relevant" + Q + "* -- written only after the system exists, because a page describing an unbuilt "
"quest is a published lie.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "the journal and quest system itself, which the brief specified" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("journal build steps recorded, 8 rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
