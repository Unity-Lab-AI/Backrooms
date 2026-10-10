# -*- coding: utf-8 -*-
"""Close operator relief, and mark the four-station row partial: consoles done, benches not."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

CLOSED = (
    "**Operator relief: a gate holds while ANY qualified pawn is on ANY console bound to it.**",
    " -- **BUILT 0.12.99-dev. A STATION QUESTION INSTEAD OF A PAWN QUESTION, CHANGED IN ONE PLACE "
    "AND CORRECTING SIX.** "
    "`IsOperatorOnStation` resolved one console and asked whether `assignedOperator` -- one named "
    "colonist -- was standing on that cell. It now returns `AnyOperatorOnStation`, and **every "
    "clause of the old test survives** inside `QualifiedToStaff` and `StaffingStation`: employed "
    "staff, spawned, same map, not dead, destroyed, downed or in a mental state, on the interaction "
    "cell, running `RR_OperateGate` targeting that console, console powered. **Only the identity "
    "clause is gone**, so a pawn who could hold a window before still can and nobody new slipped "
    "in. "
    "**SIX CALL SITES ASKED THAT PROPERTY AND EVERY ONE OF THEM MEANT *is the window being held*** "
    "-- spin-up support, the startup checklist step, the console progress bar, the Operations "
    "refusal, the send-to-station action and the open-connection precondition. **Redefining the "
    "property corrected all six in one derivation rather than six edits that could drift apart.** "
    "`GateSpinUp.SpinUpIsSupported` is the clearest case and had already ruled on it in its own "
    "words: *" + Q + "the same set of conditions a live opening is held by, on purpose: bringing a "
    "connection up cannot require less than keeping one up" + Q + "* -- so a relief operator who "
    "could hold a connection but not ramp one would have contradicted a decision the file already "
    "carried. "
    "**THE HAND-OFF IS SEAMLESS BECAUSE ABSENCE IS COUNTED RATHER THAN REACTED TO**, which is the "
    "owner's own acceptance condition: *" + Q + "he can leave when another pawn hops on the other "
    "comms console" + Q + "*. The emergency test deliberately does **not** read the instantaneous "
    "property; it reads `TickOperatorRelief()`, which counts empty ticks and resets to zero the "
    "moment anybody sits down. `ReliefGraceTicks = 1250`, **half an in-game hour**, derived from "
    "what a hand-off physically is -- one pawn's job ends, the giver offers the post to another, "
    "that pawn walks across a facility -- and bounded, because an unbounded grace would mean a gate "
    "holding a connection with nobody at the controls, the exact opposite of what §1.1 says a window "
    "depends on. **The cost is stated rather than hidden:** a player who truly abandons a console "
    "now has a short delay before the emergency fires. "
    "**AND THE AUTOMATIC HALF WAS THE PART THAT DID NOT EXIST AT ALL.** Measured: the only route "
    "to a staffed console anywhere in the mod was "
    "`assignedOperator.jobs.TryTakeOrderedJob(job, JobTag.Misc)` -- a **forced** job on one named "
    "pawn. **There was no work giver for staffing**, so a second colonist was never offered the "
    "post and therefore could never take it, and four stations would have been four empty chairs. "
    "`WorkGiver_RRStaffGateConsole` is modelled on the two givers already in that file and gated on "
    "`ReliefWanted`, which is false unless the gate is designated, **actually holding a "
    "connection**, not in emergency, not killed and currently unattended -- so a closed gate wants "
    "nobody and the giver costs one boolean per console across a whole campaign. Same discipline "
    "`WorkGiver_RRReconditionGate` states for itself: *" + Q + "the owner's direction was that "
    "pawns must not always be doing this" + Q + "*. "
    "**The need floor is asked before the post is OFFERED, not only inside the job.** "
    "`GateWatch.MustLeave` and `GateWatch.Releases` run in the giver too, because a starving pawn "
    "would otherwise take the post, fail out on the first tick and be offered it again -- a loop "
    "that reads as a colonist twitching at a console. **The job's own absolute floor is unchanged** "
    "and still asked before any posture. "
    "**The readout had to move with it.** The inspect line reported only whether the *named* "
    "operator was present, so after relief landed it would have read *away* while somebody else "
    "held the window perfectly -- a stale readout is the upstream of a player fixing something that "
    "is not broken. It now names whoever is actually holding it, and appends the station count only "
    "when there is more than one, so an ordinary one-console gate's readout is byte-identical. "
    "**`AnyOperatorOnStation` delegates to `CurrentStationOperator` rather than scanning again:** "
    "it was written as its own loop first, and that was two derivations of one rule where a later "
    "edit to one and not the other would have let the readout and the emergency test disagree about "
    "whether anybody was at the controls.")

PARTIAL = (
    "**Up to four consoles, and the same for the machine benches.**",
    " -- **THE CONSOLE HALF IS BUILT 0.12.99-dev AND THE BENCH HALF IS NOT, WHICH IS WHY THIS IS "
    "PARTIAL RATHER THAN CLOSED.** "
    "**Four stations, the owner's number, through a new link role.** `RR_Link_GateRelief` accepts "
    "`CommsConsole` with `maxLinked` **3**: the gate's own control console is the first of the four "
    "and is bound by its own rules, and `EquipmentLinkFailureKey` already refuses a provider in any "
    "role as `AlreadyAProvider`. So three relief stations plus the one provider is four. **Nothing "
    "about the primary binding changed** -- it stays exclusive, and calibration, the assembly bill "
    "and the spin-up station still read it. "
    "**IT IS DELIBERATELY NOT `RR_Link_Radio`, WHICH WOULD HAVE BEEN FREE AND WRONG.** That role "
    "says of itself that it is *" + Q + "never the gate's own control console" + Q + "* and exists "
    "*" + Q + "for listening rather than for running the gate" + Q + "*, with `maxLinked` 2. "
    "Reusing it would have cost nothing to write and meant that **a player reading the radio "
    "room's own description would have been told the opposite of what the link now did.** "
    "**Ungated, and the gate was asked about.** Owner: *" + Q + "maybe tech gated" + Q + "*, then "
    "*" + Q + "but maybe not" + Q + "*, then at the fork *" + Q + "Not gated -- it's a defect, fix "
    "it free" + Q + "*. **And the obvious hook was not one:** `RR_Cap_ReliefWatch` sounds exactly "
    "like this feature and is already spent cutting spin-up decay in `GateSpinUp`, so a reader who "
    "went looking for it would have found a feature that was not there. "
    "**WHAT IS STILL OPEN, AND WHY IT IS NOT A LINK ROLE.** *" + Q + "and same with the coms and "
    "machine benches" + Q + "*. A second `TableMachining` is **already buildable and already "
    "linkable**; what it does not do is let a second pawn work the gate's component bills, because "
    "`EnsureNativeAssemblyBill` places **one bill on the one bound bench**. So the bench half is a "
    "**bill-distribution** question, not a link question: either the bill is split across linked "
    "benches by count, or the component requirement is satisfied from any of them. **Linking a "
    "second bench without answering that would ship a role that changes nothing**, which is exactly "
    "the promise-that-changes-nothing four deleted research projects were deleted for. "
    "**And the cap question is honestly open either way:** four stations sit beside "
    "`MaximumOperationalGates = 3` and `CrewPlanner.MaxCrew = 3`, and whether four is right for "
    "three gates is a thing only play answers. The cap carries its reason meanwhile, per the "
    "standing bounds rule.")


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)

    key, evidence = CLOSED
    hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [ ] ") and key in l]
    if len(hits) != 1:
        print("REFUSED: closed row matched %d time(s)" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)

    key, evidence = PARTIAL
    hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [ ] ") and key in l]
    if len(hits) != 1:
        print("REFUSED: partial row matched %d time(s)" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [~] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)

    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("operator relief closed; the four-station row is partial with the bench half specified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
