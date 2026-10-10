# -*- coding: utf-8 -*-
"""Record the owner's three mid-turn messages about parallel stations and operator relief."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — the journals, the quests, and how data gets back to the company (2026-10-06)"

S = NL.join([
"### Owner direction — one pawn must not be pinned at the console until it starves (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06), three messages in a row:** *" + Q + "and as for the write "
"up stations u can have more than one to have more than one pawn doing it as u can have multiple "
"quests going, and same with the coms and machine benches so that it isnt dependant at one pawn "
"dying at the gate from starvvation trying to keep it open forever he can leave when another pawn "
"hops on the other comms console toggled to gate contrtrols with say upto 4 of them available so "
"pawns can do geate process better and faster" + Q + "*, then *" + Q + "maybe tech gated" + Q + "*, "
"then *" + Q + "but maybe not" + Q + "*.",
"",
"**THE DIAGNOSIS IS CORRECT AND THE DEFECT IS WORSE THAN DESCRIBED.** Measured in source: "
"`CompRimroomsGate.assignedOperator` is a **single `Pawn` reference**, saved by "
"`Scribe_References`, and `IsOperatorOnStation` is what the gate tests. §1.1 names *" + Q + "an "
"operator off station, or no operator at all" + Q + "* as a failure state — so **the gate's window "
"is hostage to one named colonist's bladder.** And the facility authors exactly **one "
"`CommsConsole`**, so there is nowhere for a second pawn to stand even if the code allowed it. "
"**There is no hand-off anywhere in the mod.**",
"",
"**And the obvious hook is not the hook.** `RR_Cap_ReliefWatch` sounds exactly like this and is "
"already spent on something else: it cuts spin-up decay in `GateSpinUp`. `RR_Cap_StandbyDiscipline` "
"halves idle drain. **Neither is an operator relief**, so the name being suggestive would have sent "
"the next reader looking for a feature that is not there.",
"",
"- [ ] **Operator relief: a gate holds while ANY qualified pawn is on ANY console bound to it.** "
"The owner's words are the specification: *" + Q + "he can leave when another pawn hops on the "
"other comms console toggled to gate contrtrols" + Q + "*. So the single `assignedOperator` becomes "
"a station question rather than a pawn question — the gate asks *is somebody at a bound console*, "
"not *is this one colonist there*. **The hand-off must be seamless or it is not a hand-off:** if "
"the window drops for a single tick while one pawn stands up and another sits down, the feature "
"has not solved the problem it was asked to solve.",
"- [ ] **Up to four consoles, and the same for the machine benches.** Owner: *" + Q + "with say upto "
"4 of them available so pawns can do geate process better and faster" + Q + "*. Four is the "
"owner's number. **It sits beside `MaximumOperationalGates = 3` and `CrewPlanner.MaxCrew = 3`, and "
"whether four stations for three gates is right is a thing only play answers** — the cap carries "
"its reason either way, per the standing bounds rule.",
"- [ ] **More than one write-up desk, for the same reason.** Owner: *" + Q + "u can have more than "
"one to have more than one pawn doing it as u can have multiple quests going" + Q + "*. This is the "
"records desk from the journal direction, and it is **parallel by design rather than by accident**: "
"the branch can accept several quests at once, so several pawns must be able to write them up at "
"once. A single desk would re-create the starvation problem one subsystem over.",
"- [ ] **TECH GATING IS AN OPEN QUESTION AND THE OWNER LEFT IT OPEN, in their own words:** "
"*" + Q + "maybe tech gated" + Q + "* and then *" + Q + "but maybe not" + Q + "*. **Recorded as "
"undecided rather than resolved by me**, because the two answers build different things: a gated "
"relief is a capability a branch earns and a reason for a Facilities tier to exist, while an "
"ungated one is a fix to a defect that is punishing the player today. **Asked, not assumed.**",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "one pawn must not be pinned at the console" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("recorded the operator-relief direction, with tech gating left open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
