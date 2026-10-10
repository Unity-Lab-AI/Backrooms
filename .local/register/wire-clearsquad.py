# -*- coding: utf-8 -*-
"""Wire the clear squad in: the fork, the save, and one visibility change.

Three edits, each with a reason that is not "it compiles".

1. **`TickFacilityRelief` forks on the scenario.** The laboratory gets the squad; the Store and
   Solo/Group branches keep the relief they were promised. The owner scoped it: *"this only
   happens for the lab secnerio for now"*.

2. **The relief's trigger comment is corrected rather than left standing.** It reads *"Downed is
   also not dead. A branch whose staff are all unconscious is in trouble, not gone."* That is
   **still true for the two scenarios it was written for** and is now false as a statement about
   the whole mod, so it is scoped rather than deleted. **A reason nobody believes is worse than
   no reason.**

3. **`RepairProvider.RepairableOn` becomes `internal`.** The squad needs Core's repairable lister
   and this is the one wrapper the mod already has for it. Making it callable is how *"fix broken
   walls and equipment"* gets **one derivation** instead of a second hand-rolled scan -- the
   defect this project keeps meeting.

And `ExposeClearSquad()` joins the save, beside the relief's own.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
RELIEF = os.path.join(SRC, "Company", "FacilityRelief.cs")
COMPONENT = os.path.join(SRC, "Company", "RimroomsCampaignComponent.cs")
UPKEEP = os.path.join(SRC, "ConnectedWork", "Providers", "UpkeepProviders.cs")
SQUAD = os.path.join(SRC, "Company", "CompanyClearSquad.cs")

EDITS = []

# ---------------------------------------------------------------- 1 + 2. the fork and the comment
EDITS.append((RELIEF, u"""        /// Downed is also not dead. A branch whose staff are all unconscious is in trouble, not
        /// gone, and replacing people who are going to stand back up would be the corporation
        /// paying twice for the same jobs.
        /// </summary>""", u"""        /// Downed is also not dead. A branch whose staff are all unconscious is in trouble, not
        /// gone, and replacing people who are going to stand back up would be the corporation
        /// paying twice for the same jobs.
        ///
        /// **That reasoning holds for the Store and the Solo/Group branches and the owner has
        /// overruled it for the laboratory.** Owner, 2026-10-01: *"a the company clear squad when
        /// all pawns incompacitated"*, and on the people it lands on: *"the downed: No
        /// Witnesses"*. The laboratory's trigger is <c>AnyCapableStaff</c> in
        /// <c>CompanyClearSquad.cs</c>, which counts downed as lost; this one is unchanged and is
        /// still what the other two scenarios use. The comment is scoped rather than deleted
        /// because it is still a true statement about the path it guards.
        /// </summary>"""))

EDITS.append((RELIEF, u"""            if (!corporationContact) { return; }
            Map map = headquarters;
            if (map == null || !Find.Maps.Contains(map)) { return; }
            if (AnyLivingStaff()) { return; }""", u"""            if (!corporationContact) { return; }
            Map map = headquarters;
            if (map == null || !Find.Maps.Contains(map)) { return; }
            // **The laboratory takes a different path entirely and never reaches the relief.**
            // Owner: *"this only happens for the lab secnerio for now we will figure out how to
            // impliment it in other scenreios later"*. Returning here is what keeps that scoping
            // real: the squad handles the dead as well as the downed, so running both would land
            // eight people and charge twenty-five million for three of them.
            if (IsLaboratoryBranch) { TickClearSquad(map); return; }
            if (AnyLivingStaff()) { return; }"""))

# ---------------------------------------------------------------- 3. the save
EDITS.append((COMPONENT, u"            ExposeFacilityRelief();",
              u"            ExposeFacilityRelief();\n            ExposeClearSquad();"))

# ---------------------------------------------------------------- 4. one derivation of repair
EDITS.append((UPKEEP, u"""        private static List<Thing> RepairableOn(Map map, Faction faction)
        {""", u"""        /// <summary>
        /// Core's own repairable list for a named map and faction.
        ///
        /// **Internal rather than private because the clear squad calls it.** *"fix broken walls
        /// and equipment"* needs the set of damaged player buildings, and this is already the
        /// mod's single wrapper for the question. A second hand-rolled scan would be a second
        /// derivation of a rule Core owns, which is the defect this project keeps meeting.
        /// </summary>
        internal static List<Thing> RepairableOn(Map map, Faction faction)
        {"""))

# ---------------------------------------------------------------- 5. a redundant disjunction
# `CompanyActionResult.Existing()` already sets Success true, so `|| AlreadyApplied` can never
# change the answer. A condition that cannot matter reads as though it can.
EDITS.append((SQUAD, u"            return result.Success || result.AlreadyApplied ? amount : 0L;",
              u"            // `Existing()` already sets Success, so a replayed charge reports the\n"
              u"            // amount exactly as the first one did.\n"
              u"            return result.Success ? amount : 0L;"))

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old[:56], os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    io.open(path, "w", encoding="utf-8-sig", newline="").write(text.replace(old, new, 1))

failures = []
relief = io.open(RELIEF, encoding="utf-8-sig").read()
if u"if (IsLaboratoryBranch) { TickClearSquad(map); return; }" not in relief:
    failures.append("the fork is not in TickFacilityRelief")
if u"the owner has\n        /// overruled it for the laboratory" not in relief:
    failures.append("the trigger comment was not scoped")
if u"private bool AnyLivingStaff()" not in relief:
    failures.append("AnyLivingStaff was changed; the other two scenarios must keep it")
component = io.open(COMPONENT, encoding="utf-8-sig").read()
if u"ExposeClearSquad();" not in component:
    failures.append("the clear squad is not saved")
upkeep = io.open(UPKEEP, encoding="utf-8-sig").read()
if u"internal static List<Thing> RepairableOn" not in upkeep:
    failures.append("RepairableOn is still private")
squad = io.open(SQUAD, encoding="utf-8-sig").read()
if u"result.AlreadyApplied ? amount" in squad:
    failures.append("the redundant disjunction is still there")

for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("wired: the fork, the scoped comment, the save, one derivation of repair")
