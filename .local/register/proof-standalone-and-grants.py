# -*- coding: utf-8 -*-
"""The package needs nothing, expansions only add, and a missing start is reported not guessed.

## What this batch was for

**Owner, verbatim:** *"we will completely make the mod 100% functional and stand alone not needing
any other mods"*, *"DLCs only add content"*, *"everything the mod needs is supplied wwith the mod
as the mod"*, and the two reports behind the start work: *"they need to properly spawn in with
starting goods"* and *"my preparecarfully mod food did not appear"*.

## The two properties worth proving

**OPTIONAL BY CONSTRUCTION, not merely by a gate.** `RimroomsGateEquipmentDef.thingDefNames` is a
`List<string>`, so naming an expansion building creates **no cross-reference at load at all** --
`Fillable` resolves through `GetNamedSilentFail` and `AllInOrder` hides a role nothing can fill.
`MayRequire` is on every expansion entry as a deliberate second line, per entry rather than per
role, because gating the whole role would delete a role that also accepts Core buildings.

**A DIAGNOSTIC MUST NOT BE ABLE TO CAUSE WHAT IT LOOKS FOR.** The starting-goods report reads the
*promise* through `GetSummaryListEntries`, which creates nothing. Enumerating
`PlayerStartingThings()` a second time would manufacture a second set of goods -- the exact
double-grant the arrival receipt exists to prevent, and which that class's own header forbids.

Run from the repository root. Exit status is the result.
"""
import io
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
TOOLS = os.path.join(REPO, "tools")

failures = []


def check(claim, held, because=""):
    print("  %-4s %s %s" % ("OK" if held else "FAIL", claim, because if not held else ""))
    if not held:
        failures.append(claim)


def read(*parts):
    path = os.path.join(*parts)
    if not os.path.isfile(path):
        raise SystemExit("ABORT: %s does not exist, so no claim about it means anything" % path)
    text = io.open(path, encoding="utf-8-sig").read()
    if not text.strip():
        raise SystemExit("ABORT: %s is empty, so no claim about it means anything" % path)
    return text


def code_only(text):
    """Source with comments stripped. An absence claim reads the documentation too."""
    return re.sub(r"//.*", "", re.sub(r"/\*.*?\*/", "", text, flags=re.S))


def xml_only(text):
    """XML with comments stripped, for the same reason."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


print("proof-standalone-and-grants")
print("-" * 78)

roles = read(MOD, "Defs", "RimroomsGateEquipmentDefs", "RR_GateEquipment.xml")
links = read(SRC, "Gate", "GateEquipmentLinks.cs")
arrival = read(SRC, "Scenario", "ScenPart_RimroomsArrival.cs")
start = read(SRC, "Scenario", "ScenPart_RimroomsStart.cs")
receipt = read(SRC, "Scenario", "HeadquartersSetupComponent.cs")
guarantee = read(TOOLS, "check-standalone-guarantee.py")
gating = read(TOOLS, "check-dlc-gating.py")

EXPANSION_ROLES = ("RR_Link_Containment", "RR_Link_Biolab", "RR_Link_Assembly",
                   "RR_Link_OffworldLogistics")

# ============================================= expansions only add content
check("THE FOUR EXPANSION ROLES EXIST",
      all(("<defName>%s</defName>" % name) in roles for name in EXPANSION_ROLES),
      "-- *DLCs only add content*. The Anomaly row's open item was specifically *the "
      "containment/research links themselves*, and containment now exists to link to")

# **OPTIONAL BY CONSTRUCTION.** A string field cannot be an unresolved cross-reference.
check("A ROLE'S ACCEPTED DEFS ARE STRINGS, so naming expansion content cannot fail a load",
      "public List<string> thingDefNames = new List<string>();" in links
      and "thingDefNames.Contains(thing.def.defName)" in links
      and "DefDatabase<ThingDef>.GetNamedSilentFail(thingDefNames[index])" in links,
      "-- there is no def reference to leave dangling. `Fillable` resolves by name and returns "
      "false when nothing does")

check("and a role nothing can fill is hidden from every surface",
      ".Where(definition => definition.Fillable)" in links,
      "-- picker, readout and `RoleFor` all go through `AllInOrder`, so there is one answer to "
      "*which roles exist on this install*")

expansion_entries = re.findall(r'<li MayRequire="(Ludeon\.RimWorld\.\w+)">(\w+)</li>',
                               xml_only(roles))
check("AND MayRequire IS ON EVERY EXPANSION ENTRY as a second line",
      len(expansion_entries) == 14,
      "-- %d gated entries found, expected 14. Belt and braces: the string field already makes "
      "this safe, and the gate makes it safe for a reader too" % len(expansion_entries))

# **PER ENTRY, NOT PER ROLE.** Gating a whole role would delete one that also takes Core buildings.
role_level_gates = re.findall(
    r'<RimroomsAsyncIndustries\.Gate\.RimroomsGateEquipmentDef\s+MayRequire', roles)
check("gated one entry at a time, never the whole role",
      not role_level_gates,
      "-- a role that accepts six buildings, two of them from an expansion, must lose those two "
      "rather than vanish. Core gates string lists the same way in CommonMapGenerator.xml")

check("AND THE GATING CHECKER CAN SEE A PER-ENTRY GATE, which it could not before",
      "def nodes_with_requirements(" in gating
      and gating.count("for node, required in nodes_with_requirements(definition):") == 2,
      "-- it read `MayRequire` off the def alone, so per-entry gating reported as ungated. It "
      "was taught the mechanism rather than worked around, because demanding the attribute on "
      "the def would have pushed the worse shape. **COUNTED, because there are two rules in "
      "that file now and containment could not tell one walk from two** -- adding the "
      "foreign-work-type rule silently made this claim survive a plant that gutted the first "
      "walk entirely, which is `in` cannot tell one site from three, again")

check("and no expansion role is load-bearing for anything",
      all(("<stockTarget>" not in block) for block in
          [roles.split("<defName>%s</defName>" % name)[1].split("</RimroomsAsyncIndustries")[0]
           for name in EXPANSION_ROLES]),
      "-- an expansion role that carried a stock need would put a shortfall line, and therefore "
      "a thing the branch is told it is short of, behind an expansion")

# ============================================= the stand-alone guarantee, as an instrument
# **A MESSAGE IS NOT A RULE -- the mistake this register already recorded once, made again.** The
# first version asserted the text of the refusal; a plant rewrote the message and the claim passed
# on a different line of the same string. What has to hold is the TEST: a value that no expansion
# owns is a problem.
check("THE GUARANTEE IS A CHECKER NOW, not a claim",
      "def main():" in guarantee
      and "                    if not owners:" in guarantee
      and "                        problems.append(" in guarantee,
      "-- the queue row said it: *a declaration cannot establish it*. `check-dlc-gating.py` "
      "could never have, because a profile mod's def is not DLC-only -- it is not in the game's "
      "data at all, so that checker never sees it")

check("and its reference fields are ENUMERATED from our own source",
      "def reference_fields():" in guarantee
      and 'singular = re.compile(r"public\\s+string\\s+(\\w*Def(?:Name)?)\\s*[;=]")' in guarantee,
      "-- the lesson `check-register-compliance.py` paid for: a hand-kept tag list missed "
      "`<thing>` and read 114 of 171 references as nothing")

check("IT REFUSES A HARD GetNamed ON EXPANSION CONTENT",
      "with GetNamed, which throws when the " in guarantee,
      "-- `GetNamedSilentFail` returns null; `GetNamed` throws, and a throw in our own code is "
      "the one thing the guarantee cannot survive")

# Counted: the name appears at its definition AND at the use that enforces it, so `in` was
# satisfied by the use alone when a plant renamed the definition. Third instance this session.
check("and it refuses a third-party assembly reference",
      guarantee.count("ALLOWED_ASSEMBLIES") == 2
      and "A stand-alone package may reference only " in guarantee,
      "-- compiling against another mod's DLL is the only other way the package could need one")

check("AND IT SKIPS RATHER THAN PASSES when the game data is absent",
      'print("            SKIPPED -- this checker cannot run without it.")' in guarantee
      and "if len(core) < 1000:" in guarantee,
      "-- a checker that silently passes on a machine without the game installed is the "
      "absence-claim-against-an-empty-file defect, which cost eight green claims once")

# ============================================= the starting-goods diagnostic
check("THE PROMISE AND THE DELIVERY ARE BOTH RECORDED",
      "public List<string> promisedGrants" in receipt
      and "public List<string> deliveredGrants" in receipt
      and 'Scribe_Collections.Look(ref promisedGrants, "rr_promisedGrants"' in receipt,
      "-- owner: *they need to properly spawn in with starting goods*. A player who starts with "
      "nothing had to sweep nine thousand cells to find out")

# **THE DIAGNOSTIC MUST NOT BE ABLE TO CAUSE THE DEFECT.**
check("THE PROMISE IS READ WITHOUT CREATING ANYTHING",
      'part.GetSummaryListEntries("PlayerStartsWith")' in arrival
      and "PlayerStartingThings()" not in code_only(arrival),
      "-- enumerating `PlayerStartingThings()` again would manufacture a second set of goods, "
      "which is the double-grant this receipt exists to prevent and which this class's own "
      "header forbids in so many words")

check("and it is recorded on both arrival paths",
      code_only(arrival).count("RecordPromisedGrants(receipt);") == 2,
      "-- the fallback path is where a player is most likely to be missing things and most in "
      "need of the report")

# **The catch EXISTING is not the property; the catch SWALLOWING is.** A plant that put `throw;`
# inside it satisfied the first version, and a rethrow here kills Core's whole scenario step --
# which is the fourth-launch defect this file's header exists to remember.
_summary_catch = arrival[arrival.index("try { entries = part.GetSummaryListEntries"):]
_summary_catch = _summary_catch[:_summary_catch.index("if (entries == null)")]
check("A PART THAT WILL NOT SUMMARISE ITSELF COSTS ONE LINE, never a start",
      "would not summarise its " in _summary_catch
      and "continue;" in _summary_catch
      and "throw" not in _summary_catch,
      "-- a scenario part from another mod is entitled to refuse, and 294 of them are installed")

# **THE SLICE WAS THE BUG.** The first version cut the method at its first `}`, which is the
# closing brace of an inline `{ return; }` guard a few lines in -- so the slice examined about
# four lines and a planted `receipt.failure` sat safely below it. Sliced to the next method
# signature instead, which is where the method actually ends.
_report_body = code_only(start)
_report_body = _report_body[_report_body.index("private static void ReportGrantShortfall(Map map)"):]
_report_body = _report_body[:_report_body.index("public CompanyActionResult "
                                                "TryInitializeExistingHeadquarters")]
check("THE REPORT NEVER BLOCKS A START",
      "private static void ReportGrantShortfall(Map map)" in start
      and "ReportGrantShortfall(Verse.Current.Game.CurrentMap);" in start
      and "receipt.failure" not in _report_body
      and "ReceiveLetter" in _report_body,
      "-- setting a failure would turn a short branch into a broken one. The facility, the "
      "people and the account are all fine; only the goods are missing")

check("and it is silent unless the promise was real and nothing arrived",
      "if (receipt.promisedGrants == null || receipt.promisedGrants.Count == 0) { return; }"
      in start
      and "if (receipt.deliveredGrants != null && receipt.deliveredGrants.Count > 0) { return; }"
      in start,
      "-- a partial delivery is not reported, because the promise is human text and the "
      "delivery is defNames; a false alarm on a working start is worse than no report")

check("IT IS SAID BEFORE THE BRANCH INITIALISES",
      start.index("ReportGrantShortfall(Verse.Current.Game.CurrentMap);")
      < start.index("CompanyActionResult result = TryInitializeExistingHeadquarters("),
      "-- a successful branch initialisation would otherwise bury the one thing the player needs "
      "to know")

# **AND IT IS A DIAGNOSTIC, NOT A FIX, WHICH THE ROW REQUIRED.**
check("THE FOUR ELIMINATED CAUSES ARE RECORDED RATHER THAN RE-DERIVED",
      "ScenPart_PlayerPawnsArriveMethod" in receipt
      and "order 850" in receipt and "order **875**" in receipt
      and "is enum zero" in receipt,
      "-- the queue row says *no fix was written on a hunch*. Four candidates were eliminated "
      "against the installed game: the arrival part, the start spot, the gen step order and the "
      "drop method. The next reader does not repeat that work")

# =====================================================================================
# THE CHILDCARE DEFECT'S SECOND SHAPE: A WORK TYPE A PROFILE MOD ADDS
# =====================================================================================
# The DLC rule indexes the game's own `Data` folders, so it can only ask whether a name is
# DLC-only. A work type from a workshop mod is in no `Data` folder at all -- not DLC-only,
# therefore invisible, therefore ungatable by that rule. Thirteen such work types exist across
# twelve mods in the 294 profile. Ungated, each is the identical unresolved cross-reference at
# load that two childcare givers shipped with until 0.6.6-dev.
connected_givers = read(MOD, "Defs", "WorkGiverDefs", "RR_ConnectedWork.xml")

check("THE FOREIGN-WORK-TYPE RULE EXISTS, IS CALLED, AND IS SCOPED TO ONE UNAMBIGUOUS TAG",
      "def foreign_work_types(owner):" in gating
      # **THE CALL, not the definition.** The first version of this claim asserted only that the
      # function existed, and its plant correctly reported MISSED: a rule defined and never
      # invoked is a rule that does nothing, and the identifier was present either way.
      and "    foreign, foreign_checked = foreign_work_types(owner)" in gating
      and "    failures.extend(foreign)" in gating
      and 'if node.tag != "workType":' in gating
      and "known = set(owner) | own_work_types()" in gating,
      "-- widening it to every reference tag would mean guessing what each tag's text is, and a "
      "rule that guesses produces findings nobody trusts")

check("it counts the package's own work types rather than assuming there are none",
      "def own_work_types():" in gating and 'definition.tag != "WorkTypeDef"' in gating,
      "-- authoring one later must not make the rule start reporting it as foreign")

check("A MOD-PROVIDED WORK TYPE IS GATED ON THAT MOD'S OWN PACKAGE ID",
      xml_only(connected_givers).count(
          '<WorkGiverDef MayRequire="Heremeus.MedicalDissection">') == 2
      and xml_only(connected_givers).count("<workType>MedicalTraining</workType>") == 2,
      "-- both givers of the family, counted rather than tested for presence, because one gated "
      "and one bare is the shape that ships a load error to everybody without the mod")

check("and nothing in the package references a type that mod owns",
      "HMDissection" not in code_only(read(
          SRC, "ConnectedWork", "ConnectedDeploymentProvider.cs"))
      and "HMDissection" not in code_only(read(
          SRC, "ConnectedWork", "Providers", "BillWorkProvider.cs")),
      "-- the family is reached entirely through Core's own bill plumbing and a defName string, "
      "so the register's no-patch-no-copy instruction holds by construction")

# =====================================================================================
# A CONTROL FOR WORK THE PLAYER DOES NOT OWN
# =====================================================================================
priorities = read(SRC, "Core", "ConnectedWorkPriorities.cs")

check("A GATED FAMILY DRAWS NO SLIDER, AND THE PANE ASKS THE APPLIER'S OWN QUESTION",
      "if (!ConnectedWorkPriorities.Present(pair)) { continue; }" in code_only(read(
          SRC, "Core", "RimroomsMod.cs"))
      and "if (!TryGivers(pair, out continueGiver, out planGiver)) { continue; }" in code_only(
          priorities),
      "-- four families are MayRequire-gated and the pane drew all of them regardless, "
      "reporting a shipped default of zero because no def had ever loaded to read one from")

check("and BOTH read the same single lookup, counted rather than assumed",
      code_only(priorities).count("GetNamedSilentFail(pair.ContinueDefName)") == 1
      and code_only(priorities).count("GetNamedSilentFail(pair.PlanDefName)") == 1
      and "return TryGivers(pair, out unusedContinue, out unusedPlan);" in code_only(priorities),
      "-- two pieces of code asking the same question separately is what produced the phantom "
      "slider, so the count is the claim: one lookup site for the pane and the applier both")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the package names only what it ships, expansions only add, and a missing "
      "start reports itself instead of being guessed at")
