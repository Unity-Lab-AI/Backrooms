# -*- coding: utf-8 -*-
"""Record the unexplored-work fix and the exploration toggle the owner spec'd across four messages."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — the journals, the quests, and how data gets back to the company (2026-10-06)"

S = NL.join([
"### Owner direction — an unexplored room offers no work, and exploring is a thing you order (2026-10-06)",
"",
"**Verbatim owner report (2026-10-06), the defect:** *" + Q + "and something we need to fix is that "
"the pawns when entering the back room instantly try to find tasks and start running of for example "
"to flower pots to plant the flower work, so we need something that spawned in its like flower pots "
"in the backrooms dont pull a pawn to run through the map to plant a flower or other things similar "
"that casue jobs work just being in the game wehn pawns look for axcessible tasks. like make it so "
"unexplored areas can propigate work as no one knows or has been in those rooms yet." + Q + "*",
"",
"**And verbatim on the feature, in the same message:** *" + Q + "and i think we need a explore option "
"thats toggleable like drafting. so the pawns will go room to room  exploring the maze of the map "
"attempting to explore the seed completely until toggled off or completed with a pop notice " + Q
+ "PAwn radioed in exploration complete" + Q + " or something appropriate" + Q + "*",
"",
"**Then three more messages refining it:** *" + Q + "and exploration need journal entry work "
"stuff" + Q + "*, *" + Q + "once completed" + Q + "*, and *" + Q + "can get $$$ form companty and "
"such" + Q + "*.",
"",
"- [x] **FIXED 0.12.99-dev, AND THE CAUSE WAS OURS AND EXPLICIT.** `RoomContentBuilder` called "
"`thing.SetForbidden(false, false)` on **every** piece of room content it placed — two sites, the "
"dressing and the landmark — and the corridor fixtures spawn as `Faction.OfPlayer`. So from the "
"tick a coordinate existed, every pot, bench and bed on it was colony property, unforbidden, and a "
"legitimate work target the full width of a 300×300 maze away. **Not a pathfinding quirk and not "
"vanilla being greedy: the generator did it on purpose, in two lines.** "
"**The mechanism was read out of the shipped assembly rather than guessed at.** "
"`ForbidUtility.IsForbidden(Thing, Pawn)` was decompiled: it tests the thing's own forbidden flag, "
"its cell's `InAllowedArea`, and a lord's extra-forbidden list — **fog is not part of it at all**, "
"so fogging a coordinate would have changed nothing on its own. That left two real mechanisms, and "
"**the forbidden flag beats an allowed area because of the player**: an area would have to be "
"assigned to each crossing pawn, overriding a control the player owns, while the flag touches only "
"content the generator placed. **And forbidding does not restrict movement** — a forbidden thing is "
"not a work target and not haulable; it is not a wall — which is what leaves exploring possible. "
"`UnexploredWorkMapComponent` releases content when its cell stops being fogged, which is Core's "
"own notion of somebody having been there, as a bounded rotating window per invariant 5: 600 cells "
"a second, so a 90,000-cell coordinate is covered in about a minute and a quarter and a room a crew "
"is standing in is reached far sooner. **It only ever un-forbids**, so a thing the player "
"deliberately unforbade keeps that state. **Doors, the gate anchor, the found gate and the conduits "
"are deliberately untouched** — a forbidden door is a door nobody walks through, and the conduits "
"are the power grid rather than scenery.",
"",
"- [ ] **The exploration toggle, ordered like drafting.** Owner: *" + Q + "a explore option thats "
"toggleable like drafting" + Q + "*, the pawn goes *" + Q + "room to room exploring the maze of the "
"map attempting to explore the seed completely until toggled off or completed" + Q + "*, ending "
"with a notice in the owner's own words: *" + Q + "PAwn radioed in exploration complete" + Q + "*. "
"**Drafting is the right comparison and it sets the shape**: a per-pawn toggle the player flips, "
"which overrides ordinary work while it is on and releases the pawn when it is off. "
"**It composes with the fix above rather than duplicating it:** exploring lifts fog, and lifting "
"fog is exactly what makes a room's contents workable — so the toggle is the player's way of saying "
"*go make this coordinate legible*, and the forbidding is what stops that happening by accident.",
"  - [ ] **Completion is a real state, not a guess.** *" + Q + "until toggled off or completed" + Q
+ "* needs a definition of complete that a 300×300 maze can actually reach: every room the planner "
"authored has been entered, which the room records already enumerate, rather than every cell "
"unfogged — a sealed pocket behind unmined rock would otherwise make completion unreachable and the "
"notice would never fire.",
"  - [ ] **Exploration produces journal work when it completes.** Owner: *" + Q + "and exploration "
"need journal entry work stuff" + Q + "*, scoped by the next message to *" + Q + "once "
"completed" + Q + "*. So it is **not** a write-up per room — that would bury a branch in paperwork "
"for walking down a corridor — but one entry for the finished survey of a coordinate. This belongs "
"inside the journal brief rather than beside it, because it is the same mechanism: a write-up job "
"at the records desk, a green light, and a book that goes back.",
"  - [ ] **And the company pays for it.** Owner: *" + Q + "can get $$$ form companty and such" + Q
+ "*. A completed survey is a deliverable, so it posts to the ledger like any other. **§1.2 binds "
"it:** the offer needs two routes of two different kinds, which a survey has naturally — "
"**Document** the finished map, or **Testify** to what the crew saw where a record was lost. "
"**And §1.1 binds it too: no clock on the survey**, however long the maze takes.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "an unexplored room offers no work" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("recorded the exploration direction and the fix")
    return 0


if __name__ == "__main__":
    sys.exit(main())
