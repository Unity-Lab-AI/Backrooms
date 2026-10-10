# -*- coding: utf-8 -*-
"""Record the owner's direction that a prisoner may cross a gate."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "## Public face: the site, the Workshop page and the collection"

S = NL.join([
"### Owner direction — a prisoner IS allowed to cross a gate, and zoning and doors decide it (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06):**",
"",
"> *" + Q + "A prisoner could cross a gate... a prisoner should be able to cross a gate is allowed "
"to ( send the prisonerrs to live and work in there and cross path back if zoned to and door are "
"allowed access remmebr mods we have also along side all of that.. locks and prisoner mods... u "
"know???" + Q + "*",
"",
"**THIS SUPERSEDES INVARIANT 17 AND CORRECTS A FIX I SHIPPED HOURS EARLIER IN THE WRONG "
"DIRECTION.** I found that a prisoner of the colony could be taken by the outbound crossing, called "
"it a defect against *" + Q + "a prisoner can never cross a gate" + Q + "*, and closed the hole. "
"**The hole was the feature.** The owner's model is that a prisoner crossing is **ordinary movement "
"through a door**, governed by the things the player already controls -- zoning, door access, and "
"the access-control and prisoner mods in the profile -- rather than by a rule of ours.",
"",
"**AND THE REGISTER RECORDED THE OLD BAN AS SETTLED, which is exactly why the LAW says to check "
"it before building.** Row 288, Prison Labor: *" + Q + "Settled on one axis: a prisoner given work "
"by this mod can never cross a gate. PortalTraversalPolicy admits only Faction.OfPlayer "
"colonists" + Q + "*. That disposition is now wrong and the row has to say so -- a settled line the "
"owner has overruled is worse than an open question.",
"",
"**What the register already anticipated, and it is the mechanism the owner is pointing at.** Row "
"273, **Locks**, planned use: *" + Q + "Use lockable doors to define staff, visitor, evidence, "
"armory, quarantine, and gate-perimeter access" + Q + "*, integration approach: *" + Q + "validate "
"door pathing, **guest/prisoner access**, emergency exits" + Q + "*. Row 169 Prison Commons, row 175 "
"Prisoners Dont Have Keys and row 41 Area Unlocker are the rest of it. **The access rule is theirs "
"and the player's; ours is only to stop forbidding it.**",
"",
"- [ ] **A prisoner of the colony may cross a gate, and custody crosses with them.** Four clauses "
"refuse one today and all four were written on the old rule: "
"`RimroomsPortalCrossingService.EligibilityFailureKey` refuses on `Faction != Faction.OfPlayer` "
"**before** it even reaches its `IsPrisoner` clause -- **a prisoner keeps their original faction, "
"which is the same fact that made my own fix necessary and now makes it wrong**; "
"`PortalTraversalPolicy.TravellerFailureKey` admits only `IsColonist`, so Prison Labor work across "
"a gate is impossible; `OrderedCrossingFailureKey` the same for a player's order; and "
"`OutboundCrossingFailureKey`, which is mine from this session. **The crossing must preserve "
"custody**: no faction change and **no arrival Lord**, because a Lord is what turns a transferred "
"pawn into an actor and would launder a prisoner into a free one. *" + Q + "send the prisonerrs to "
"live and work in there and cross path back" + Q + "*",
"- [ ] **Walking out to the WORLD is a different act and stays refused, and the distinction needs "
"stating rather than assuming.** `WorldExit.TravellersAt` excludes a prisoner from the caravan that "
"forms when somebody walks out of a coordinate onto a world tile. **That path calls "
"`PassToWorld`** -- it is the one place in the mod that does -- so a prisoner taken along would "
"leave the player's hands entirely. The owner's words are about crossing a **gate** and coming "
"back; a caravan is not that.",
"- [ ] **Two judgement calls inside this that the owner did not name, both stated so they can be "
"redirected.** A **quest lodger** stays refused: losing one fails a quest the player never chose "
"to fail, and nothing about the prisoner direction touches guests on loan. A **slave** is "
"allowed, because a slave's faction IS the player's -- refusing the more-owned category while "
"admitting the less-owned one is a rule nobody could read a reason for.",
"- [ ] **Every instrument and document that asserts the old ban has to be restated out loud, and "
"this is the fifth such restatement this session.** Checker 29 gained a four-clause custody rule "
"hours ago and now asserts the opposite of the design; plant suite 42 has four plants aimed at it; "
"the register's row 288 calls the ban settled; `WorldExit`'s own comment cites invariant 17 as "
"though it governed gates. **A green instrument over a dead rule is worse than no instrument**, and "
"an archive is never edited -- the supersession is recorded where the rule lives.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "a prisoner IS allowed to cross a gate" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("recorded: 4 open rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
