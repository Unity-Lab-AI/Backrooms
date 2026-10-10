# -*- coding: utf-8 -*-
"""Close the cross-map traversal brief row. The five build rows beside it stay open."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROW = "**Write the cross-map traversal brief BEFORE any code**"

EVIDENCE = (
    " -- **WRITTEN 0.12.99-dev: `docs/CROSS_MAP_TRAVERSAL_BRIEF.md`, twelve sections, and the "
    "central finding is that the invariant bundles TWO rules and only one of them is being "
    "discarded.** "
    "`ARCHITECTURE.md` line 454 names the fear it was built against: *" + Q + "an open gate can never "
    "become an objective, lure, spawn target, raid route or attack trigger for a later adapter, "
    "scheduler, generator or threat" + Q + "*. **The weight is on *for a later ... threat*** -- the "
    "worry was a feature quietly growing a crossing of its own. So **one chokepoint, no scattered "
    "permissions, is KEPT unchanged**, and what is discarded is only *the answer is always no*. "
    "`AutonomousNonPlayerTraversalPermitted` stops being a `const bool`, because a constant cannot "
    "express *yes under these conditions* -- and a constant left at false beside code that crosses "
    "anyway is exactly the stale-comment failure this repository has a rule about. "
    "**FINALIZED entry 54 is NOT edited**: the archive is append-only, so the new record states that "
    "the owner superseded it and when. "
    "**FOUR CROSSINGS, AND DIRECTION IS THE DISTINCTION THAT DID NOT EXIST BEFORE TODAY.** Everything "
    "built so far is ours going out and back, or something following us home. The owner's direction "
    "adds **outbound crossing by somebody who is not ours**, which is a fourth case: colonist work "
    "(shipped, 56 givers), colonist needs (missing), hostile **inbound** (`GateIncursion`, five "
    "bounds), hostile or friendly **outbound** (missing). **Inbound and outbound must not share "
    "bounds**, because being attacked at home is more severe than losing a remote stockpile. "
    "**THE MOTIVE IS THE BOUND, AND IT CAME OUT OF THE OWNER'S OWN SENTENCE.** Incursion's five axes "
    "do not transfer -- coordinate band and gate tier describe how dangerous the far side has become, "
    "which says nothing about whether a raider in your base should walk through a door. "
    "*" + Q + "to get valuables and members" + Q + "* is the bound instead: **nothing crosses "
    "outbound unless there is loot or a carryable person over there.** That is self-limiting in a way "
    "a hand-tuned number is not, and it makes the risk legible -- store nothing beyond a gate and you "
    "are never raided through one; build a vault down there and you built a target. "
    "**And the cap is the doorstep rather than once-per-opening**, which is a deliberate departure: "
    "one raider peeling off through a gate while nineteen ignore it reads as a bug rather than a "
    "rule, so **the player's defence is the cap** and a raid stopped in the killbox never reaches the "
    "threshold. "
    "**THE BRIEF FOUND A DEFECT THAT ALREADY SHIPPED.** A `Lord` is per map -- `Map.lordManager` owns "
    "it -- and `GateIncursion.Transfer` despawns, spawns and announces **without creating one**. So "
    "an intruder that follows a crew home today **arrives lordless**, with no duty and no assault "
    "behaviour, and whether it still attacks is a question only a launch answers. The brief refuses "
    "to leave that standing because the outbound work would reproduce it four times over, and the fix "
    "is the established pattern **in this code base**: `InhabitantService` already calls "
    "`LordMaker.MakeNewLord` with `LordJob_AssaultColony(...)`. **For an outbound raider two of its "
    "arguments become the owner's words turned into parameters:** `canSteal: true` for "
    "*" + Q + "valuables" + Q + "* and `canKidnap: true` for *" + Q + "members" + Q + "*. **Incursion's "
    "own missing lord is fixed in the same change**, because fixing it only outbound would leave the "
    "older and worse case alone to spite a tidy diff. "
    "**THE COUNTERPLAY IS ALREADY BUILT AND IS NOT REINVENTED.** `NativeGateKillSwitch` drives "
    "`EnterEmergency(\"RR_NativeGate_KillSwitchThrown\")`, and the tick checks it **before** the "
    "generic power test so the recorded cause says somebody threw it. So *close the gate* answers "
    "every crossing in the brief -- the same lesson incursion already teaches, now doing twice the "
    "work. **And the second counterplay is a layout decision already in the code:** `GateWidth` and "
    "`GateOpeningDepth` feed `FitFailureKey`, so *" + Q + "a narrow gate is a real defensive choice "
    "rather than the starter option" + Q + "* gains a second reason to be true. "
    "**Needs are not work, which is why they are not a fifty-seventh giver.** Rest, food and joy come "
    "from Core's **think tree**, not the work loop, so the route in is a `ThinkTreeDef` with "
    "`insertTag` -- additive XML, no Harmony, nothing of Core's taken over. And the question must be "
    "asked **against an explicit `Map`**, which `ConnectedDeploymentProvider` already demands in its "
    "own words, so needs become providers rather than a copy of Core's search aimed at a foreign map. "
    "**The stranding guard is at the decision, not the rescue:** a pawn may not *begin* a "
    "need-crossing unless the remaining window covers the walk there, the need and the walk back, "
    "checked once before committing, because a guard that fires halfway is how a pawn ends up "
    "stranded mid-corridor. **A permanently open natural gate has no window and so needs no guard**, "
    "which is invariant 12 paying for itself. "
    "**Register checked:** [270] Hospitality's *" + Q + "preserve each mod's guest ownership and "
    "payment rules" + Q + "* binds the friendly case -- a crossing moves a guest and changes nothing "
    "about their status, payment or departure timer. [274] binds kidnapping to Core's own systems. "
    "[60] Capture Them is **not** needed, because kidnapping belongs to the lord rather than to a "
    "work giver. "
    "**And step 8 of the build order is an instrument, for a stated reason:** no existing checker "
    "asserts anything about who may cross, which is precisely how a `const bool` and eight document "
    "assertions could have drifted from the code in the first place.")


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [ ] ") and ROW in l]
    if len(hits) != 1:
        print("REFUSED: row matched %d time(s)" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), EVIDENCE)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("traversal brief row closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
