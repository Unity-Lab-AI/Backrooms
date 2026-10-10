# -*- coding: utf-8 -*-
"""Close the two tier-5 research rows the owner approved."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Build the four clean research tiers**",
     " -- **BUILT 0.12.99-dev, all four, each moving a constant that was unclaimed and each visible "
     "without reading source.** "
     "**Facilities T5 `RR_Facilities_ServicingRegime`**, and it fills the gap **" + Q + "1.1 itself "
     "names" + Q + "**: maintenance was the only one of the four factors deciding a gate's window "
     "with no project on it. **IT MOVES WEAR RATHER THAN CAPACITY, AND THAT WAS NOT THE OBVIOUS "
     "CHOICE.** `ServiceCapacityTicks` is the denominator every saved `serviceConditionTicks` is "
     "read against, so raising the tank would have silently rewritten what every already-saved gate's "
     "condition MEANS -- a gate sitting at a full 600,000 would read as half empty the moment the "
     "project completed, and the player would watch a finished research project make their gates "
     "worse. Halving wear produces the card's own sentence with every stored figure still meaning "
     "what it meant, **and it is visible where the player is already looking**: `ServicingReadout` "
     "has always printed the wear multiplier, so the number on the gate's pane halves. The "
     "technician's saving deepens from 0.7 to 0.5 and the untrained figure is untouched, because the "
     "card says a *technician* does it faster and the certification has to stay worth earning. "
     "**Measurement T5 `RR_Measurement_TrainedEye`**: the tell share rises 12 to 18, which is the "
     "sweep's *" + Q + "one step, not uncapped" + Q + "* -- *" + Q + "at 12% a wrong fixture is an "
     "event; at 50% it is wallpaper" + Q + "*. **AND RAISING IT CAN ONLY EVER ADD A TELL, NEVER MOVE "
     "ONE**, which falls out of the existing derivation rather than being arranged: the roll is a "
     "stable hash tested with `roll % 100 >= threshold`, so a larger threshold admits a strict "
     "superset and a coordinate re-read after the research keeps every tell a crew wrote down. That "
     "is what *the trained eye* ought to mean and the opposite of what a reroll would. "
     "**Spatial T5 `RR_Spatial_NearExit`**: a way out lands three to ten tiles out instead of seven "
     "to twenty. **The narrowed band is TRIED and the full band still answers if it finds nothing**, "
     "so the project can never cost a branch a way out it would otherwise have had -- a tier that "
     "sometimes made exits harder to find is a tier a player learns to regret, and the band is narrow "
     "enough that an ocean in the wrong place would have done exactly that. A recorded exit never "
     "moves, because the band is read once and the tile is then saved. "
     "**Entities T5 `RR_Entities_QuietProtocol`** as `MaxEventsPerOpening` **only**, two to one, "
     "confirmed at a second fork. "
     "**Ladder shape continues tiers 0 to 4 rather than restarting:** insight 6, work 22000, "
     "intellectual 8, five route logs, four distortion logs, three entity logs, each prerequisiting "
     "its own branch's tier 4 so no project gates two branches. "
     "**The mirror was REGENERATED, not hand-extended**, which is the whole reason it is a generator: "
     "42 paired `ResearchProjectDef`s, `check-research-mirror.py` PASS, and the sixth band's cost "
     "sits at 7,800 against vanilla's measured ceiling of 8,000. The generator's `!= 38` became a "
     "named `EXPECTED_PROJECTS` with the reason it exists, so the next person to add a tier gets a "
     "refusal that explains itself rather than a magic cliff. "
     "**AND FOUR BRANCHES GOT NOTHING, WHICH IS THE PART A READER CANNOT GET FROM THE DEF FILE.** "
     "Nothing exists above a connection that no longer counts down; every Procurement knob is claimed "
     "by tiers 0 to 3; Commerce's candidates **became player settings** at 0.12.98-dev and a project "
     "over a slider the player already drags is two controls fighting; Transport has no tier 0 by "
     "design. Each absence is recorded beside the tier it is absent from and asserted by "
     "`proof-research-tier5.py` -- **proof 60, with plant suite 37 against it, 22 of 22 planted "
     "faults caught and every touched file verified byte-identical afterwards.** Five of those plants "
     "exist because **an absence cannot be seen by reading the def file**: a reader sees four "
     "projects and has no way to know whether the other five were declined or forgotten."),

    ("**Entities T5 must not touch `QuietRoomFraction`, confirmed by the owner at the fork.**",
     " -- **ENFORCED 0.12.99-dev, and the row asked for exactly the right thing.** "
     "`RR_Entities_QuietProtocol` reads `MaxEventsPerOpening` and nothing else; `QuietRoomFraction` "
     "is 0.5f and untouched. **The rule is in `proof-research-tier5.py` rather than in "
     "`check-campaign-absolutes.py`, and the choice is deliberate.** That checker's subject is the "
     "owner's 2026-09-29 pair -- no deadlines, two success routes -- and adding a third unrelated "
     "absolute would widen a checker's subject until nobody can say what it is for. The tier-5 proof "
     "is the instrument whose subject IS this tier. **One home, because two derivations of one rule "
     "is the defect this project keeps meeting.** "
     "**It reads the deciding function's own body, comments stripped, not the vicinity of the "
     "constant.** `RequiredQuietRooms` and `IsQuietRoom` must contain no `Capability` at all -- the "
     "same technique `proof-research-branches.py` uses for `FrontiersFor`, and for the same recorded "
     "reason: a rule keyed on a capability name appearing within N characters of a constant fails the "
     "moment a legitimate capability-aware line is written nearby, which this repository has done and "
     "paid for. **A rule about code must read code**, which is why the comments are stripped: the "
     "tier-5 comment block NAMES the capability it is forbidding, and checker 29 made precisely that "
     "mistake on its first run. "
     "**`MaxSimultaneousEncounters` is asserted alongside it**, because it is the other half of the "
     "same guarantee and the same three lines would move it. "
     "**And the planted fault proves the rule can fail:** a capability read inserted into "
     "`RequiredQuietRooms` is caught, which is the only evidence that a green instrument over this "
     "means anything."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:52], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d tier-5 row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
