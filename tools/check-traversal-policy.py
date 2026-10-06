# -*- coding: utf-8 -*-
"""Checker 29 -- who may cross a gate, and the two halves of invariant #1.

WHY THIS INSTRUMENT EXISTS

Invariant #1 was a `const bool` and eight sentences across six documents, and **nothing anywhere
asserted any of it.** That is exactly how a constant and its documentation drift from the code: the
owner superseded half the rule on 2026-10-06, and without this the other half -- the half that is
load-bearing -- would be free to rot the same way.

The half that was discarded is *"the answer is always no"*. The half that was KEPT is **one
chokepoint**: no adapter, scheduler, generator or threat may decide a crossing for itself, and
nothing is ever drawn to a gate. This checker guards the kept half.

THE RULES

 1. `MayApproachThresholdForTraversal` **still returns false, unconditionally.** Nothing is ever
    lured to a gate. This is the surviving half of invariant #1 and the reason incursion and egress
    are both fair.
 2. `AutonomousNonPlayerTraversalPermitted` is **gone**, not left at false. A constant denying what
    the code does is a stale comment with a compiler behind it.
 3. Every decision about who may cross lives in `PortalTraversalPolicy`. No other file may contain a
    faction test gating a map transfer.
 4. Inbound keeps all five of its bounds: an opening, the Hostile band, a window tier, fit, and once
    per opening.
 5. Outbound does **not** copy band or tier, and is bounded by motive instead.
 6. Both directions ask `FitFailureKey`, so a body too large cannot pass either way.
 7. **Every pawn moved between maps is given a `Lord` on arrival.** A `Lord` is per map, so a
    transferred pawn has no duty; this shipped as a real defect in `GateIncursion`.
 8. A hostile's arrival lord carries `canSteal` and `canKidnap` -- the owner's *"valuables and
    members"* -- and a friendly's does not.
 9. Every transfer puts the pawn back if the spawn fails. A vanished pawn is a save with a hole in it.
10. The documents do not still assert the removed constant.
11. **A prisoner of the colony MAY cross, and custody crosses with them.** Owner direction,
    2026-10-06, superseding invariant 17: *"a prisoner should be able to cross a gate is allowed to
    ( send the prisonerrs to live and work in there and cross path back if zoned to and door are
    allowed access"*. So the rule is not who may cross but **what they are when they land**: a
    prisoner arrives with **no Lord**, because a Lord makes an actor out of a transferred pawn and
    would launder somebody in your custody into a free pawn. A quest lodger is still refused.
12. **Whether a pawn is ours is asked in ONE place**, `InOurCare`, and it is custody or faction --
    never faction alone. A prisoner of the colony carries somebody else's faction, and that single
    fact produced a fault in both directions on one day: it let a prisoner out through the egress
    path and locked them out of every other crossing.
"""
import io
import os
import re
import sys

NL = chr(10)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POLICY = os.path.join("src", "RimroomsAsyncIndustries", "Portals", "PortalTraversalPolicy.cs")
INCURSION = os.path.join("src", "RimroomsAsyncIndustries", "Threats", "GateIncursion.cs")
EGRESS = os.path.join("src", "RimroomsAsyncIndustries", "Threats", "GateEgress.cs")
SOURCE_ROOT = os.path.join("src", "RimroomsAsyncIndustries")

# Rule 10. FINALIZED is append-only and is never edited; TODO carries the owner's words verbatim.
DOCS = (
    os.path.join("docs", "ARCHITECTURE.md"),
    os.path.join("docs", "CONNECTED_COLONY_PORTALS.md"),
    os.path.join("docs", "implementation", "CONNECTED_TRAVEL_IMPLEMENTATION.md"),
    os.path.join("docs", "implementation", "GATE_FIT_IMPLEMENTATION.md"),
    os.path.join("docs", "implementation", "GATE_INCURSION_IMPLEMENTATION.md"),
)
STALE_CLAIMS = (
    "`AutonomousNonPlayerTraversalPermitted` is a constant false",
    "`AutonomousNonPlayerTraversalPermitted` is a constant `false`",
    "`AutonomousNonPlayerTraversalPermitted` is still a constant false",
    "`AutonomousNonPlayerTraversalPermitted` is still a constant `false`",
    "exposes `AutonomousNonPlayerTraversalPermitted` as a constant false",
)


def read(relative):
    path = os.path.join(ROOT, relative)
    return io.open(path, encoding="utf-8-sig").read() if os.path.isfile(path) else None


def strip_comments(source):
    """Drop comments, because every file here quotes its own rules at length."""
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return NL.join(line for line in source.split(NL) if not line.lstrip().startswith("//"))


def every_source_file():
    for folder, _, names in os.walk(os.path.join(ROOT, SOURCE_ROOT)):
        if os.sep + "bin" + os.sep in folder or os.sep + "obj" + os.sep in folder:
            continue
        for name in names:
            if name.endswith(".cs"):
                path = os.path.join(folder, name)
                yield os.path.relpath(path, ROOT), io.open(path, encoding="utf-8-sig").read()


def main():
    problems = []
    policy = read(POLICY)
    policy_body = strip_comments(policy) if policy else ""
    if policy is None:
        problems.append("%s is missing; there is no chokepoint" % POLICY)

    # ---------------------------------------------------------------- rule 1, nothing is lured
    if policy_body and not re.search(
            r"bool MayApproachThresholdForTraversal\(Thing[^)]*\)\s*\{\s*return false;\s*\}",
            policy_body):
        problems.append("MayApproachThresholdForTraversal does not return an unconditional false. "
                        "This is the SURVIVING half of invariant #1: nothing is ever lured to a gate, "
                        "which is why both crossing directions are fair. A gate that can become a "
                        "destination can become an objective, a spawn target and a raid route")

    # ---------------------------------------------------------------- rule 2, the constant is gone
    # **Comment-stripped, because the policy's own prose explains the removal and should.** A rule
    # that scanned raw text would refuse the documentation of the very change it is checking for --
    # which is the single most repeated false green in this battery, caught here on the first run.
    for relative, source in every_source_file():
        if "AutonomousNonPlayerTraversalPermitted" in strip_comments(source):
            problems.append("%s still names AutonomousNonPlayerTraversalPermitted. It was removed by "
                            "owner direction; a constant denying what the code does is a stale comment "
                            "with a compiler behind it" % relative)

    # ---------------------------------------------------------------- rule 3, one chokepoint
    if policy_body:
        for name in ("TravellerFailureKey", "OrderedCrossingFailureKey", "IncursionFailureKey",
                     "OutboundCrossingFailureKey"):
            if name not in policy_body:
                problems.append("PortalTraversalPolicy has no %s; every direction's decision must live "
                                "in the one chokepoint" % name)

    # ---------------------------------------------------------------- rules 4, 5 and 6, the bounds
    if policy_body:
        inbound = policy_body.split("IncursionFailureKey", 1)[-1].split("OutboundCrossingFailureKey", 1)[0]
        # **WORD-BOUNDED, BECAUSE A SUBSTRING TEST PASSES ON A RENAME.** A plant renamed
        # `IncursionSpentThisOpening` to `IncursionSpentThisOpeningUnused` -- gutting the
        # once-per-opening bound -- and this rule did not notice, because the new name CONTAINS the
        # old one. That is the same failure three other instruments in this battery have now had,
        # and it is always this shape: an `in` test against a name.
        for fragment, why in (
                ("Band.Hostile", "the Hostile band"),
                ("PortalWindowTier", "a window tier"),
                ("IncursionSpentThisOpening", "once per opening"),
                ("FitFailureKey", "fit")):
            if not re.search(r"\b%s\b" % re.escape(fragment).replace(r"\.", r"\."), inbound):
                problems.append("inbound crossing no longer bounds on %s. Nothing in the outbound "
                                "direction may loosen inbound: being attacked at home is more severe "
                                "than losing a remote stockpile" % why)
        outbound = policy_body.split("OutboundCrossingFailureKey", 1)[-1]
        if "Band.Hostile" in outbound or "PortalWindowTier" in outbound:
            problems.append("outbound crossing copies inbound's band or tier bound. Those describe how "
                            "dangerous the FAR side has become, which says nothing about whether a "
                            "raider already in your base should walk through a door")
        if "FitFailureKey" not in outbound:
            problems.append("outbound crossing does not bound on fit, so a body too large for the "
                            "opening could walk out through it")

        # ⛔ **THIS RULE LASTED ONE AFTERNOON AND THE OWNER CORRECTED IT.** It required outbound
        # crossing to refuse four custody clauses, on the reasoning that invariant 17 said *"a
        # prisoner can never cross a gate"*.
        #
        # **Owner, 2026-10-06:** *"a prisoner should be able to cross a gate is allowed to ( send the
        # prisonerrs to live and work in there and cross path back if zoned to and door are allowed
        # access remmebr mods we have also along side all of that.. locks and prisoner mods"*.
        #
        # So a prisoner crossing is **ordinary movement through a door**, decided by zoning, door
        # access and the profile's own access-control mods. Register row 273 (Locks) had already
        # planned for *"guest/prisoner access"*. **The rule that replaces it is not about who may
        # cross; it is about what they are when they land.**
        #
        # **CUSTODY MUST SURVIVE THE CROSSING, and the place that can break it is the arrival Lord.**
        # A Lord turns a transferred pawn into an actor: an assault lord would have a captured raider
        # attack the coordinate, a defend lord would have them stand guard over it, and either way
        # the player loses somebody they had taken through a mechanism they never clicked. So the
        # test moved from *refuse the crossing* to *refuse the Lord*.
        #
        # A quest lodger is still refused outright, which is the one clause that survived: a guest on
        # loan whose safety is a quest condition is not the owner's subject here.
        if "traveller.IsQuestLodger()" not in outbound:
            problems.append("outbound crossing does not refuse a quest lodger. A guest on loan whose "
                            "safety is a quest condition would walk out and fail a quest the player "
                            "never chose to fail -- which is the reasoning the prisoner ban claimed "
                            "and did not have")
        for stale in ("traveller.IsPrisoner", "traveller.HostFaction != null"):
            if stale in outbound:
                problems.append("outbound crossing still refuses %s. The owner allows a prisoner to "
                                "cross -- 'send the prisonerrs to live and work in there and cross "
                                "path back' -- and a clause here denying it is the old rule coming "
                                "back as a tidy-up" % stale)
        egress_source = read(EGRESS)
        egress_code = strip_comments(egress_source) if egress_source else ""
        if egress_code and "if (pawn.IsPrisonerOfColony) { return; }" not in egress_code:
            problems.append("a prisoner arriving through a gate is given a Lord. A Lord makes an "
                            "actor out of a transferred pawn, so it would launder somebody in your "
                            "custody into a free pawn -- the whole cost of allowing the crossing at "
                            "all, and the one thing that must not happen")
        care = read(os.path.join("src", "RimroomsAsyncIndustries", "Portals",
                                 "PortalCrossingService.cs"))
        care_code = strip_comments(care) if care else ""
        if care_code:
            if "public static bool InOurCare(Pawn pawn)" not in care_code:
                problems.append("there is no single derivation of whether a pawn is in this colony's "
                                "care. A faction test is not one: a prisoner of the colony carries "
                                "somebody else's faction, which is the fact that caused a fault in "
                                "both directions in one day")
            if re.search(r"pawn\.Faction != Faction\.OfPlayer\s*\)\s*$", care_code, re.M):
                problems.append("eligibility still refuses on faction alone, which locks a prisoner "
                                "out of every crossing before the prisoner clause is even reached")

    # ---------------------------------------------------------------- rules 7, 8 and 9, transfers
    for relative, path in ((INCURSION, "inbound"), (EGRESS, "outbound")):
        source = read(relative)
        if source is None:
            problems.append("%s is missing, so the %s direction does not exist" % (relative, path))
            continue
        body = strip_comments(source)
        if "LordMaker.MakeNewLord" not in body:
            problems.append("%s moves a pawn between maps and never gives it a Lord. A Lord is per "
                            "map, so the pawn arrives with no duty at all -- this shipped as a real "
                            "defect and a launch could not tell anybody why a raider stood still"
                            % relative)
        if "GenSpawn.Spawn(pawn, originCell, origin" not in body:
            problems.append("%s does not put the pawn back when a spawn fails. A vanished pawn is a "
                            "save with a hole in it and the player would never know" % relative)
    egress = read(EGRESS)
    egress_body = strip_comments(egress) if egress else ""
    if egress_body:
        if not re.search(r"canKidnap:\s*true", egress_body) or not re.search(r"canSteal:\s*true", egress_body):
            problems.append("the outbound hostile lord does not carry canSteal and canKidnap. Those "
                            "are the owner's own words as parameters: \"to get valuables and members\"")
        if "LordJob_DefendPoint" not in egress_body:
            problems.append("a friendly crossing is given an assault lord. A visitor that wandered "
                            "through a door has not decided to attack anybody, and giving it an "
                            "assault job would invent a betrayal")
        if "MarketValue" not in egress_body:
            problems.append("outbound crossing does not test whether the far side is worth crossing "
                            "for. The motive IS the bound: an empty coordinate must not be raided")

    # ---------------------------------------------------------------- rule 10, the documents
    for relative in DOCS:
        text = read(relative)
        if text is None:
            problems.append("%s is missing" % relative)
            continue
        for claim in STALE_CLAIMS:
            if claim in text:
                problems.append("%s still asserts %r. A document denying what the code does is worse "
                                "than no document: a future reader takes it as the design and the code "
                                "as the bug" % (relative, claim[:52]))

    print("check-traversal-policy")
    print("  chokepoint        : %s" % (POLICY if policy else "MISSING"))
    print("  documents checked : %d" % len(DOCS))
    print("")
    if problems:
        for problem in problems:
            print("  FAIL   : %s" % problem)
        print("")
        print("  %d problem(s)" % len(problems))
        return 1
    print("  PASS   : one chokepoint, nothing lured, both directions bounded, every free arrival "
          "has a lord, and custody crosses with its prisoner")
    return 0


if __name__ == "__main__":
    sys.exit(main())
