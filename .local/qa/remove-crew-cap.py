# -*- coding: utf-8 -*-
"""Remove the crew cap everywhere it is enforced, claimed or implied.

**Owner, 2026-10-06:** *"rememberber pawns can cross gate as they plkease so no max number"*, then
*"dont know where 3 came from"*, then *"thats gonna have down stream effects especially in operations
tab"*, then *"and wiki and other things, all need accounted for"*.

THEY WERE RIGHT ON ALL FOUR COUNTS, AND THE THIRD WAS THE IMPORTANT ONE. `CrewPlanner.MaxCrew` never
refused anything -- its own class documentation says so. **The real cap is `crew.Count > 3`, in two
dispatch paths**, and removing only the panel's number would have left the planner saying *as many as
you send* while dispatch refused four. That is a worse state than the cap.

And three was never the owner's figure: it is the number of staff roles the Async Industries start
ships, which `SCENARIOS.md` ties a records bonus to. A scenario's headcount became a design cap by
being written down somewhere else.
"""
import io
import sys

NL = chr(10)

EDITS = [
    # ====================================================== the two real refusals
    ("src/RimroomsAsyncIndustries/Expedition/ExpeditionCargo.cs",
     "            if (headquarters == null || crew == null || crew.Count < 1 || crew.Count > 3 || crew.Distinct().Count() != crew.Count ||",
     "            // **NO UPPER BOUND ON A CREW.** Owner: \"pawns can cross gate as they plkease so no"
     + NL +
     "            // max number\". The `crew.Count > 3` that was here is one of the TWO places that"
     + NL +
     "            // actually refused a fourth person -- `CrewPlanner.MaxCrew` only ever printed a number"
     + NL +
     "            // in a panel. A lower bound of one stays: a dispatch with nobody in it is not a trip."
     + NL +
     "            if (headquarters == null || crew == null || crew.Count < 1 || crew.Distinct().Count() != crew.Count ||"),

    ("src/RimroomsAsyncIndustries/Expedition/RimroomsExpeditionComponent.cs",
     "            if (crew == null || crew.Count < 1 || crew.Count > 3 || crew.Distinct().Count() != crew.Count ||",
     "            // The second of the two real refusals. See ExpeditionCargo for the reasoning; both had"
     + NL +
     "            // to go together or the panel and the dispatch would disagree about whether four is"
     + NL +
     "            // allowed, which is worse than either answer."
     + NL +
     "            if (crew == null || crew.Count < 1 || crew.Distinct().Count() != crew.Count ||"),

    # ====================================================== the dead constant
    ("src/RimroomsAsyncIndustries/Expedition/CrewPlanner.cs",
     "        public const int NoCrewCap = int.MaxValue;",
     "        /// (No constant is declared. A cap of `int.MaxValue` is still a cap somebody can read as a"
     + NL +
     "        /// rule, and nothing needs the number: the absence IS the rule.)"),

    # ====================================================== the keyed claims
    ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Expedition.xml",
     "  <RR_Exp_InvalidCrew>Select one to three distinct, available employed staff at headquarters. They must be alive, mobile, controllable, and able to carry their gear.</RR_Exp_InvalidCrew>",
     "  <!-- \"one to three\" became \"at least one\" on owner direction 2026-10-06: \"pawns can cross gate"
     + NL +
     "       as they plkease so no max number\". This string is the refusal a player actually reads when"
     + NL +
     "       dispatch says no, so leaving it claiming a ceiling would have been the cap surviving in the"
     + NL +
     "       one place it is most visible. -->"
     + NL +
     "  <RR_Exp_InvalidCrew>Select at least one distinct, available employed staff member at headquarters. They must be alive, mobile, controllable, and able to carry their gear. There is no upper limit on how many go.</RR_Exp_InvalidCrew>"),

    ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Company.xml",
     "  <RR_UI_ContractTerms>Survey the route, record the distortion, recover the record book and analyse it at headquarters. The optional bonus requires all three crew to return with route, distortion and entity observations. Combat is optional; a recoverable injury does not cancel the bonus.</RR_UI_ContractTerms>",
     "  <!-- \"all three crew\" became \"everybody who went\", which is what the rule always was: the"
     + NL +
     "       EvidenceSettlement test read `InitialCrew.Count == 3` and so could only ever be satisfied by"
     + NL +
     "       a crew of exactly three. Three was the Async Industries start's headcount, not a condition. -->"
     + NL +
     "  <RR_UI_ContractTerms>Survey the route, record the distortion, recover the record book and analyse it at headquarters. The optional bonus requires everybody who went to come back with route, distortion and entity observations. Combat is optional; a recoverable injury does not cancel the bonus.</RR_UI_ContractTerms>"),

    ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_FieldAndThreats.xml",
     "A clear entity observation and all three original crew returning qualify for the bonus.",
     "A clear entity observation and every original crew member returning qualify for the bonus."),

    # ====================================================== the wiki
    ("docs/wiki/first-hour.md",
     "Up to three field staff. The planner checks skill, health and carried weight, and names anyone who",
     "As many field staff as you want to send. There is no cap: the planner checks skill, health and\ncarried weight, and names anyone who"),

    # ====================================================== the scenario document
    ("docs/SCENARIOS.md",
     "an optional **$1,000,000** records bonus if all three crew return with the route, distortion, and entity-observation records",
     "an optional **$1,000,000** records bonus if **every crew member who went** returns with the route, distortion, and entity-observation records (the start ships three staff, which is where the figure \"three\" in earlier drafts came from — it was never a cap, and there is no cap on crew size)"),
]


def main():
    for path, old, new in EDITS:
        text = io.open(path, encoding="utf-8-sig").read()
        if text.count(old) != 1:
            print("REFUSED: %s contains the target %d time(s)" % (path, text.count(old)))
            return 1
        io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new, 1))
        print("updated %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
