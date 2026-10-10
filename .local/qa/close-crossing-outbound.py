# -*- coding: utf-8 -*-
"""Close the hostile, friendly and zoning-limit rows. The colonist-needs rows stay open."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**A hostile may break in and cross for valuables and people.**",
     " -- **BUILT 0.12.99-dev as `GateEgress`, and it is the strongest idea in the direction because "
     "it gives an open window a second meaning nothing had to be invented for.** A connection cost "
     "power and attention; it is now **a hole in the base something can go through**. "
     "**THE MOTIVE IS THE BOUND AND IT CAME OUT OF THE OWNER'S OWN SENTENCE.** Incursion's five axes "
     "do not transfer -- coordinate band and gate tier describe how dangerous the *far* side has "
     "become, which says nothing about whether a raider already inside your base should walk through a "
     "door. *" + Q + "to get valuables and members" + Q + "* is the rule instead: nothing crosses "
     "unless the far map holds loot worth taking or a person worth carrying off. **Self-limiting where "
     "a tuned number is not, and legible**: store nothing beyond a gate and you are never raided "
     "through one; build a vault down there and you built a target, and you can see that you did. "
     "**The cap is the doorstep, not once per opening, and that is a deliberate departure.** Inbound "
     "is capped at one because the player is attacked at home and *close and reopen* is the learnable "
     "rule. A raid is a group: one raider peeling off while nineteen ignore it reads as a bug. **So "
     "the player's defence IS the cap** -- a raid stopped in the killbox never reaches the threshold. "
     "**Six steps reused from `GateIncursion` with the ends swapped, and two of its properties are "
     "the reason rather than economy:** candidates are taken in a **fixed radial order** so *" + Q
     + "the same situation resolves the same way on every machine" + Q + "*, and the transfer **puts "
     "the pawn back if the spawn fails**, because *" + Q + "a vanished hostile is a save with a hole "
     "in it" + Q + "*. "
     "**Counterplay already existed and was not reinvented.** `NativeGateKillSwitch` means *close the "
     "gate* answers this exactly as it answers incursion, and `GateWidth`/`GateOpeningDepth` feed "
     "`FitFailureKey` -- so *" + Q + "a narrow gate is a real defensive choice rather than the starter "
     "option" + Q + "* gains a second reason to be true. "
     "**AND THE BRIEF FOUND A DEFECT THAT HAD ALREADY SHIPPED, now fixed in the same change.** A "
     "`Lord` is per map, and `GateIncursion.Transfer` despawned an intruder out from under its duty "
     "and spawned it with none -- **so a hostile that followed a crew home arrived with no assault "
     "behaviour at all**, and whether it attacked was a question only a launch could answer. Both "
     "directions now call `LordMaker.MakeNewLord` on arrival, the pattern `InhabitantService` already "
     "used, with **`canSteal: true` and `canKidnap: true`** -- the owner's words as parameters -- plus "
     "`canTimeoutOrFlee: true`, because something that came through a door into somebody else's base "
     "reasonably gives up and leaves, unlike an inhabitant in its own space."),

    ("**A friendly on your map may cross too.**",
     " -- **BUILT 0.12.99-dev in the same mechanism, with a different lord and a different letter.** "
     "Owner: *" + Q + "hold up now friendlys can too" + Q + "*. A visitor, trader or allied squad "
     "member standing at an open threshold may walk through. "
     "**A friendly gets `LordJob_DefendPoint`, never an assault job**, because a pawn that wandered "
     "through a door has not decided to attack anybody and giving it an assault lord would invent a "
     "betrayal the player never caused. "
     "**THE FACTION CONSEQUENCE IS MADE VISIBLE RATHER THAN SILENT, which is the cost the fork named "
     "and the owner accepted.** A guest who dies in a coordinate is a death the player caused by "
     "leaving a hole open, and Core books it on their watch. So a friendly crossing raises a letter as "
     "loudly as a hostile one, naming who went and through which gate: **the one thing that must not "
     "happen is a faction penalty arriving with no story the player can connect it to.** "
     "**And nothing is lured.** A friendly crosses because it wandered to a threshold that happens to "
     "be open, exactly as a hostile does. `MayApproachThresholdForTraversal` is **still false for "
     "everything**, so the gate is never a destination for anybody who is not ours -- which is the "
     "surviving half of invariant #1 doing real work."),

    ("**BUT ZONING CANNOT BE THE CONTROL FOR ANYBODY ELSE, AND THAT IS MEASURED RATHER THAN ASSUMED.**",
     " -- **ANSWERED 0.12.99-dev: the hostile and friendly halves got their own permission, which is "
     "what this row said they needed.** `PortalTraversalPolicy.OutboundCrossingFailureKey` is that "
     "permission, and it lives in the **one chokepoint** rather than anywhere a zone is read. "
     "**The measurement stands and is why:** `RespectsAllowedArea` returns false unless the pawn is "
     "player-faction with no host faction, **and false whenever the pawn has a `Lord`** -- and raiders, "
     "visitors, traders and allied squads all have lords. So not one of them would ever have consulted "
     "a zone. **Building zoning as the universal answer would have shipped two lies at once:** a raider "
     "that ignores the player's zones, and a player who believed a setting was protecting them. "
     "**AND INVARIANT #1 WAS REWRITTEN RATHER THAN QUIETLY BROKEN, which was the real work here.** It "
     "bundled two rules and only one went. **Kept:** one chokepoint, nothing drawn to a gate. "
     "**Discarded:** the answer is always no. `AutonomousNonPlayerTraversalPermitted` is **removed** -- "
     "a constant denying what the code beside it does is a stale comment with a compiler behind it -- "
     "while `MayApproachThresholdForTraversal` **stays unconditionally false**, which is what still "
     "stops an open gate becoming an objective, a lure or a raid route. "
     "**Five documents rewritten in the same commit** per DOCS-BEFORE-PUSH, plus the `GateIncursion` "
     "class comment that still said *" + Q + "Invariant #1 holds exactly as written" + Q + "*. "
     "**`FINALIZED.md` entry 54 is NOT edited** -- the archive is append-only, so its *" + Q + "must "
     "stay false for everything, forever" + Q + "* stands as written and the supersession is recorded "
     "where the rule now lives. "
     "**And nothing asserted any of this before, which is how it could have rotted.** "
     "`check-traversal-policy.py` is **checker 29**, ten rules: nothing is lured, the constant is gone "
     "from code, every direction's decision is in the chokepoint, inbound keeps all five bounds, "
     "outbound copies neither band nor tier, both ask fit, every arrival gets a lord, the hostile lord "
     "carries steal and kidnap and the friendly's does not, every transfer rolls back, and no document "
     "still asserts the removed constant. **Its first run caught itself** reading the policy's own "
     "prose explaining the removal -- a rule about code must read code, not the documentation of the "
     "change it is checking for."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:50], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d crossing row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
