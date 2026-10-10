# -*- coding: utf-8 -*-
"""Record the owner's direction that anything on your map may cross a gate.

This one inverts a founding invariant that six documents assert, so the record names that
collision rather than letting a future reader discover it in a diff.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — an unexplored room offers no work, and exploring is a thing you order (2026-10-06)"

S = NL.join([
"### Owner direction — anything standing on your map may cross a gate, and zoning is the control (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06), four messages in a row.** The first, on finding the wiki "
"saying no guests arrive:",
"",
"> *" + Q + "what??? vistors cant walk through the gate to find work and beds??? we need cross map "
"cordinator or something thats automatic merging maps to cross control so pawns auto get command to "
"cross when mpas call them like a empty bed work task or job ect ect or anything at all" + Q + "*",
"",
"**Then, correcting the scope of who:**",
"",
"> *" + Q + "not anyone in base, but anyone on your map.. a enemy can break in and cross the gate to "
"get valuables and members" + Q + "*",
"",
"**Then, widening it again:**",
"",
"> *" + Q + "hold up now friendlys can too" + Q + "*",
"",
"**Then, on the control surface:**",
"",
"> *" + Q + "all one person choices in zoning" + Q + "*",
"",
"**And then, asked what that meant, the owner settled it before it could be guessed:**",
"",
"> *" + Q + "i mena its upto the play to zone pawns where they want them,, that was the whole cross "
"zone support" + Q + "*",
"",
"**And two forks were answered before those last three arrived**, both at the permissive end, both "
"with their cost stated in the option text before it was chosen: needs **" + Q + "commute" + Q + "** "
"rather than pawns living on the far side, which the option named as *the window closes mid-sleep "
"and the pawn is stranded*; and crossing open to **" + Q + "Anyone standing in your base" + Q + "**, "
"which the option named as *they can die down there, and that is a faction incident with no good "
"explanation*. **Message two then superseded " + Q + "in your base" + Q + " with " + Q + "on your "
"map" + Q + "**, which is wider and sharper: a raider does not need to be a guest.",
"",
"**WHAT IS ALREADY BUILT, MEASURED BEFORE ANY OF THIS WAS DESIGNED, because the first message asks "
"for a thing that largely exists.** `WorkGiver_ConnectedDeployment` has **56 work givers** running "
"on RimWorld's own work loop, so a colonist on the surface is offered a job on the far map and "
"crosses by itself. `WORK_TYPE_COVERAGE_AUDIT` puts **21 of the game's 23 work types** across a "
"gate. **The automatic cross-map coordinator the owner asked for is shipped for WORK.** The gap the "
"owner put their finger on is exact: beds appear in that code only for carrying a **downed** patient "
"to one, so **no healthy pawn ever crosses for a need** -- not an empty bed, not food, not "
"recreation. *" + Q + "like a empty bed work task" + Q + "* is the missing half.",
"",
"## ⛔ THIS DIRECTION INVERTS INVARIANT #1, WHICH SIX DOCUMENTS ASSERT AND ONE CALLS PERMANENT ⛔",
"",
"**Stated plainly rather than discovered in a diff.** `PortalTraversalPolicy` is described in source "
"as *" + Q + "the single chokepoint" + Q + "* and holds two constants:",
"",
"- `AutonomousNonPlayerTraversalPermitted` -- *" + Q + "Deliberately constant. A connection opening "
"never grants any non-player pawn a reason, route or permission to traverse. There is no setting, no "
"research and no upgrade that flips this." + Q + "*",
"- `MayApproachThresholdForTraversal` -- unconditionally false **for everything**.",
"",
"`ARCHITECTURE.md` line 454 states it as an owner rule enforced in source: *" + Q + "an open gate "
"can never become an objective, lure, spawn target, raid route or attack trigger" + Q + "*. "
"`CONNECTED_COLONY_PORTALS.md` line 89 repeats it. Two implementation records repeat it. And "
"`FINALIZED.md` entry **54** reads: *" + Q + "`MayApproachThresholdForTraversal` must stay false for "
"everything, forever. Incursion works *because* nothing is drawn to a gate." + Q + "*",
"",
"**So `GateIncursion` -- the one existing exception, where something follows your crew home -- is "
"safe precisely BECAUSE nothing is drawn to a gate.** Its own words: a hostile *" + Q + "walks to "
"the threshold because **your people are standing there**, not because a door is open" + Q + "*. "
"The owner's direction makes the door itself a reason, which is the exact sentence that invariant "
"was written to forbid.",
"",
"**THE OWNER OUTRANKS THE INVARIANT AND THAT IS NOT IN QUESTION.** What is in question is that "
"eight assertions across six documents and one `const bool` currently say the opposite, and "
"`check-compliance`, `check-campaign-absolutes` and the proof suites assert some of them. **None of "
"this may be edited quietly.** The invariant is rewritten in the owner's words, in the same commit "
"as the first line of code, per DOCS-BEFORE-PUSH -- and the five bounds `GateIncursion` carries must "
"be re-derived, because every one of them was reasoned from an assumption that is about to be false.",
"",
"- [ ] **Write the cross-map traversal brief BEFORE any code**, on the journals' precedent: the "
"owner's own standing pattern for a change this size is *" + Q + "this is big one to need proper "
"write up before attempting the work" + Q + "*. This one rewrites a founding invariant, so the brief "
"has to settle: which pawns may cross and on whose decision; what a need-crossing does when the "
"window closes; what a hostile crossing does to the far map's stockpile and to pawns standing on it; "
"what a friendly crossing means for faction relations when it dies down there; and **what replaces "
"the five bounds that made `GateIncursion` fair**, since each was derived from *nothing is drawn to "
"a gate*.",
"- [ ] **Needs must be able to cross, which is the owner's actual complaint.** Owner: *" + Q + "so "
"pawns auto get command to cross when mpas call them like a empty bed work task or job ect ect or "
"anything at all" + Q + "*, and at the fork, **commuting** rather than living there. Work already "
"crosses through 56 givers; a need does not, because needs are satisfied from Core's **think tree** "
"rather than the work loop. **The route is a `ThinkTreeDef` with `insertTag`**, which is additive "
"XML and not a patch to Core's tree -- so no Harmony and nothing of Core's is taken over.",
"- [ ] **A need-crossing must not strand the pawn, and the owner was shown that cost and took it.** "
"§1.1 makes the window the only clock in the mod, so a pawn asleep on the far side when it closes is "
"stuck until the next opening. **The guard belongs at the decision, not the rescue:** a pawn may not "
"*begin* crossing for a need unless the remaining window covers the walk there, the need, and the "
"walk back. That is computable from `openingTicksRemaining` and a path estimate, and it is the "
"difference between a feature and a pawn-eating hole. **A permanently open natural gate has no "
"window and so has no guard**, which is invariant 12 paying for itself.",
"- [ ] **A hostile may break in and cross for valuables and people.** Owner: *" + Q + "a enemy can "
"break in and cross the gate to get valuables and members" + Q + "*. **This is the strongest part of "
"the direction and it makes an open window a security decision rather than a convenience.** Core "
"already has the behaviour -- an assault lord with stealing and kidnapping -- so what is needed is "
"permission to cross plus a target on the far map. **The counterplay already exists and must be "
"named in the brief rather than invented:** `NativeGateKillSwitch` cuts a connection deliberately, "
"so *close the gate* is a real, learnable answer, exactly as it already is for incursion.",
"- [ ] **A friendly on your map may cross too.** Owner: *" + Q + "hold up now friendlys can "
"too" + Q + "*. So visitors, allies and traders standing on the branch's map may walk through. "
"**The faction consequence is the open question and the brief must settle it rather than discover "
"it:** a guest who dies in a coordinate is a death the player caused by leaving a hole open, and "
"Core will read it as a death on the player's map. Register row 270 (Hospitality) says to "
"*" + Q + "preserve each mod's guest ownership and payment rules" + Q + "*, which is a constraint "
"on whatever is decided.",
"- [ ] **Zoning is the control surface and HALF OF IT IS ALREADY IN THE GAME.** Owner: *" + Q + "all "
"one person choices in zoning" + Q + "*, then *" + Q + "i mena its upto the play to zone pawns where "
"they want them,, that was the whole cross zone support" + Q + "*. "
"**Measured out of the shipped assembly: `Pawn_PlayerSettings.allowedAreas` is a "
"`Dictionary<Map, Area>`**, scribed per pawn and per map. **So RimWorld already stores a separate "
"allowed area for every map a pawn has one on, and already saves it.** Cross-map zoning is not a "
"system to build; it is a system to reach. Once a pawn is on a coordinate the player zones them "
"there with the UI they already know, and Core enforces it with no help from this mod -- which also "
"means **nothing here needs to read or write another map's area**, and that matters because there is "
"**no public per-map setter**: `AreaRestrictionInPawnCurrentMap` writes only to the map the pawn is "
"standing on, and `allowedAreas` is private.",
"- [ ] **BUT ZONING CANNOT BE THE CONTROL FOR ANYBODY ELSE, AND THAT IS MEASURED RATHER THAN "
"ASSUMED.** `Pawn_PlayerSettings.RespectsAllowedArea` returns **false** unless "
"`pawn.Faction == Faction.OfPlayer && pawn.HostFaction == null`, **and false whenever the pawn has a "
"`Lord`**. Raiders have a lord. Visitors, traders and allied squads have lords. Guests have a host "
"faction. **So not one of them respects an allowed area at all**, and *" + Q + "all one person "
"choices in zoning" + Q + "* governs exactly the branch's own colonists. "
"**The hostile and friendly halves therefore need their own permission, not a zone**, and the brief "
"must say which: the gate being open plus `PortalTraversalPolicy` is the only chokepoint that can "
"carry it. **Saying so now is the point** -- building zoning as the universal answer would have "
"produced a raider that ignores it and a player who thinks they are protected by a setting that was "
"never consulted.",
"- [ ] **A need-crossing has to be answered against an explicit `Map`, which the architecture "
"already demands and already does.** Core's bed and food searches are scoped to `pawn.Map`, so they "
"cannot answer *is there a free bed over there*. `ConnectedDeploymentProvider` states the contract "
"this must follow in its own words: a provider answers *is there work of my kind on that map* "
"**against an explicit `Map`**, because *" + Q + "the provider contract forbids asking a native "
"pawn-specific query about a map the worker is not standing on" + Q + "*. **So needs become "
"providers beside the existing 56**, not a copy of Core's think-tree search pointed at a foreign "
"map.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "anything standing on your map may cross a gate" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("cross-map traversal direction recorded, 6 rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
