# -*- coding: utf-8 -*-
"""Close rows 728, 1028, 1031, 1032 and 1033. Status changes and appended closure notes only.

Every anchor asserted before anything is written, one write at the end.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "TODO.md")

original = io.open(PATH, encoding="utf-8").read()

MISSION = (u"**BUILT 0.12.41-dev as the consignment mission, and what makes it a mission rather "
           u"than a contract with a longer title is a field condition.** The owner's reason names "
           u"four things a demand should make a player do -- **advance, explore, haul, use the "
           u"spaces** -- and the odd-supply contract built at 0.7.3-dev pays for **haul and "
           u"nothing else**: it draws from the union of everything every coordinate ever "
           u"produced, and settles the moment the goods sit at headquarters, so a branch with a "
           u"shelf of odd cotton can fill one without opening a connection at all. A mission "
           u"names **one coordinate**, wants goods **that coordinate produced**, and **does not "
           u"settle until a space at that depth has been surveyed further than it had been when "
           u"the mission was offered**. One open at a time against the contracts' three, offered "
           u"every three days rather than every day, paying double because it also buys the "
           u"survey work. **No deadline** -- `check-campaign-absolutes.py` forbids one and a "
           u"plant that adds an `expiryTick` is caught; a mission is harder because of what it "
           u"asks, never because of a clock. **The obvious design cannot be built and the code "
           u"is why:** `ThingOrigin` has three values and **carries no coordinate at all**, and "
           u"`CompRimroomsOddOrigin.AllowStackWith` lets odd stacks merge, so nothing can ever "
           u"verify *which* coordinate a good came from -- the condition is checked against "
           u"recorded survey state, which cannot be faked by hauling, and the proof asserts the "
           u"mark still carries no coordinate so that tightening it later is possible. "
           u"**Settlement is the contract's settlement** plus one call, because two paths that "
           u"both consume goods and both pay money will eventually disagree about one of them; a "
           u"record with no condition reports it met, so every existing save behaves exactly as "
           u"it did. Record `implementation/PLANNER_AND_MISSIONS_IMPLEMENTATION.md`, proof "
           u"`proof-planner-and-missions.py`. Was: ")

EDITS = [
    # ------------------------------------------------------------------------------- row 728
    (u"- [ ] Add crew composition and cargo planner with skill/health/weight/gate-window "
     u"checks, ready/unready reasons, and cost preview.",
     u"- [x] **BUILT 0.12.41-dev, and the measurement decided the whole shape of it: every "
     u"check this row asks for was already enforced and not one of them was named.** `Dispatch` "
     u"refuses on **fifteen** distinct grounds and `CheckCrew` collapses **five** of them -- "
     u"wrong crew size, a duplicate, cannot walk, not employed, and by extension dead, downed, "
     u"mid-mental-break or incapable of moving -- into the single key **`RR_Exp_InvalidCrew`**. "
     u"Weight was already checked, hauling was already checked, the operator was already held "
     u"back and the debrief hold was already enforced. So a player ticked three boxes, pressed "
     u"dispatch and was told *\"invalid crew\"*: **one message for five conditions across three "
     u"people, naming neither the person nor the condition.** So this is not a second set of "
     u"checks, it is **the same conditions attributed** -- ten named reasons, one per person, "
     u"each reading the state dispatch itself reads (`gate.AssignedOperator`, "
     u"`campaign.AwaitingDebrief`, `ExpeditionCargo.CheckCapacity`, "
     u"`PawnCapacityDefOf.Moving`). **Skill was the one thing genuinely absent**: best level per "
     u"field skill across the selected crew, with the gaps named and **deliberately not "
     u"enforced**, because a player may have good reasons to send two shooters and no medic. "
     u"Weight is `MassUtility`, per person and for the crew. The window is the gate's own tier "
     u"calculation, said as *held* rather than as a number at the indefinite tier. The cost "
     u"preview is watt-days for a full window quoted beside the reserve it has to cover -- and "
     u"it reads `OpeningPowerDrawWatts` off `GateFootprint`, **not** the raw prop: a duplicate "
     u"accessor for the raw prop was written and **the compiler refused it**, which was right "
     u"twice over, because the footprint-scaled one is discounted by `RR_Cap_EfficientAperture` "
     u"and the raw value is not what any gate above 1x1 actually draws. **This row's absolute -- "
     u"*\"must not own connection existence\"* -- is asserted structurally:** the planner "
     u"constructs no `CompanyActionResult`, and the proof enumerates every C# file in the "
     u"package and **refuses any reference to the type from outside `UI/`**, so a call from "
     u"dispatch or gate code fails the build. Deleting the planner would change no outcome in "
     u"the game. Record `implementation/PLANNER_AND_MISSIONS_IMPLEMENTATION.md`, proof "
     u"`proof-planner-and-missions.py`. Was: Add crew composition and cargo planner with "
     u"skill/health/weight/gate-window checks, ready/unready reasons, and cost preview."),

    # ------------------------------------------------------------------------------ row 1028
    (u"- [~] **\"have quests and missions and contracts and stuff for like 1000 (odd) cotton",
     u"- [x] **COMPLETE 0.12.41-dev: all three thirds now exist.** Contracts shipped 0.7.3-dev; "
     u"the 18 generated mission families shipped 0.12.12-dev and 0.12.13-dev; the **odd-goods "
     u"consignment mission** closes the last of it. See rows 1031-1033 below for the mission's "
     u"shape and why it is distinct from a contract. Was: **\"have quests and missions and "
     u"contracts and stuff for like 1000 (odd) cotton"),

    # ------------------------------------------------------------------------------ row 1031
    (u"- [ ] **\"that can give reason for the players to have to advance and excplore and haul "
     u"and use the spaces iin the backrooms\"**",
     u"- [x] " + MISSION + u"**\"that can give reason for the players to have to advance and "
     u"excplore and haul and use the spaces iin the backrooms\"**"),

    # ------------------------------------------------------------------------------ row 1032
    (u"- [ ] **Quests and missions for odd goods**, as distinct from contracts.",
     u"- [x] **BUILT 0.12.41-dev.** Same mechanism as row 1031 above; one deliverable, not two. "
     u"**The 13 mission families this row names were already built** -- 18 of them, at "
     u"0.12.12-dev and 0.12.13-dev -- and **none of them was about odd goods**, which is the gap "
     u"this closes. Was: **Quests and missions for odd goods**, as distinct from contracts."),

    # ------------------------------------------------------------------------------ row 1033
    (u"- [ ] **A player-facing surface for open odd demands.**",
     u"- [x] **BUILT 0.12.41-dev, and this row understates what was wrong.** The pane did list "
     u"them -- and printed **`RR_UI_ContractTerms` on every contract**, which is the *survey* "
     u"contract's terms, written for a different job. So a demand for two hundred odd cotton "
     u"displayed *\"Survey the route, record the distortion, recover the record book and analyse "
     u"it at headquarters.\"* **A confident wrong answer is worse than silence**: silence sends a "
     u"player looking, this stopped them. Meanwhile `requiredThingDefName`, `requiredCount` and "
     u"`deliveredCount` were saved, given public accessors and **read by nothing but the "
     u"settlement code** -- the `check-wiring.py` defect class, in C# where it cannot see it. The "
     u"pane now says what is wanted, how much has been handed over, that ordinary stock will not "
     u"do, and for a mission which coordinate it came out of, the survey progress toward the "
     u"requirement and whether the requirement is met. The survey terms are still shown on a "
     u"survey contract, because they were right for the contract they were written for. Was: "
     u"**A player-facing surface for open odd demands.**"),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:80]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("five rows closed in one write")
