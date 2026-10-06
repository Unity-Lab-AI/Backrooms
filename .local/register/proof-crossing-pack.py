# -*- coding: utf-8 -*-
"""Claims about the pack-is-not-a-cargo-route rule and the three work-behaviour providers.

Queue row: **Optional work/storage provider adapters**, narrowed twice. The storage half closed
through `IHaulDestination`; what remained was *"behaviour those mods add beyond the interface, plus
the work-behaviour providers (Pick Up And Haul, Haul To Stack, Prison Labor), each still needing
its own review"*, with each needing *"its own source review and a `PatchOperationFindMod` so it
applies nothing when the mod is absent (invariant 42)"*.

**The register already held two of the three answers, and the third was a hole in our own code.**

* **Haul to Stack (107)** -- register, verbatim: *"Connected-work check added 2026-09-29: none
  needed -- this mod has no cross-map surface."* Nothing to build.
* **Prison Labor (288)** -- the register said *"a prisoner given work by this mod can never cross a
  gate"* and called it settled. **The owner overruled that on 2026-10-06**: *"a prisoner should be
  able to cross a gate is allowed to ( send the prisonerrs to live and work in there and cross path
  back if zoned to and door are allowed access"*. So a prisoner given work by this mod MAY cross,
  the register row is corrected, and the axis that replaced it -- custody survives the crossing --
  is owned by `check-traversal-policy.py` rather than restated here.
* **Pick Up And Haul (164)** -- the one real finding, and it is **ours, not the mod's**. Every
  cargo rule and the receipt itself govern `carryTracker`; nothing looked at `pawn.inventory`, so
  anything in a pack crossed unrecorded. That mod makes it routine rather than rare.

**No adapter and no patch for any of the three**, so invariant 42 holds by there being nothing to
apply -- which is a stronger result than a correctly-gated patch, not a weaker one.

Absence claims go through `code_only`. Every file here documents what it avoids by naming it --
`DropAllNearPawn` is named in a comment precisely to say it is *not* used -- so a claim that read
comments would fail on the sentence that justifies it.
"""
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
POLICY = os.path.join(SRC, "Portals", "CrossingInventoryPolicy.cs")
SERVICE = os.path.join(SRC, "Portals", "PortalCrossingService.cs")
TRAVERSAL = os.path.join(SRC, "Portals", "PortalTraversalPolicy.cs")
ADAPTERS = os.path.join(SRC, "ConnectedWork", "Adapters")
GIVERS = os.path.join(SRC, "ConnectedWork")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Portals.xml")


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def code_only(text):
    """C# with `///` documentation, `//` comments and `/* */` blocks removed."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


def flat(text):
    """Whitespace-normalised: a positional claim encodes layout, containment is the property."""
    return " ".join(text.split())


def slice_method(text, name):
    """A method body, cut to the NEXT member rather than to the next brace.

    Cutting at the first `}` is how an earlier claim examined four lines of a method and let a
    planted fault sit below an inline guard. This cuts at the next signature.
    """
    match = re.search(r"(?m)^\s*(?:public|private|internal|protected)[^\n;=]*\b"
                      + re.escape(name) + r"\s*\(", text)
    if not match:
        return ""
    rest = text[match.end():]
    following = re.search(r"(?m)^\s*(?:public|private|internal|protected)\s", rest)
    return text[match.start():match.end() + (following.start() if following else len(rest))]


policy = read(POLICY)
policy_code = code_only(policy)
service = read(SERVICE)
service_code = code_only(service)
traversal_code = code_only(read(TRAVERSAL))
keyed = read(KEYED)

CLAIMS = []


def claim(label, ok, detail=""):
    CLAIMS.append((label, bool(ok), detail))


# ------------------------------------------------- Core decides what a pack may keep, not us
has_freight = slice_method(policy_code, "HasFreight")
claim("the pack rule asks Core what is not the pawn's to keep",
      "FirstUnloadableThing" in has_freight,
      "Core keeps drug-policy amounts, inventoryStock entries and a colonist's packable food")
claim("no hand-rolled keep-list reimplements Core's rule",
      "DrugPolicy" not in policy_code and "inventoryStock" not in policy_code,
      "two definitions of 'not theirs to keep' is how they come to disagree")
claim("DropAllNearPawn is NOT used anywhere",
      "DropAllNearPawn" not in policy_code and "DropAllNearPawn" not in service_code,
      "it empties the whole pack, so a pawn would lose its own medicine at a threshold")
claim("an empty container is answered without asking Core",
      "innerContainer.Count == 0" in has_freight)

# -------------------------------------------------------------- the drop, bounded and honest
drop = slice_method(policy_code, "DropFreight")
claim("the drop loop is bounded by a constant",
      "MaximumFreightStacks" in drop and "for (int guard" in flat(drop),
      "FirstUnloadableThing recomputes, so a silently failing drop would spin for ever")
claim("the bound is declared as a constant rather than written inline",
      re.search(r"public const int MaximumFreightStacks\s*=\s*\d+", policy_code) is not None)
claim("a failed drop breaks out instead of retrying for ever",
      drop.count("break;") >= 2, "one for nothing left, one for a drop that would not land")
claim("the drop refuses to run on an unspawned pawn",
      "!pawn.Spawned" in drop and "pawn.Map == null" in drop,
      "after DeSpawn there is no map to drop onto")
claim("the drop reports how many stacks it put down",
      "return dropped;" in drop)
claim("a zero or negative count is never passed to TryDrop",
      "freight.Count < 1 ? 1 : freight.Count" in flat(drop))

# ------------------------------------------------------- where it is called, and where it is not
forward = service_code[:service_code.index("private PortalCrossingResult TryRecoverToSource")]
claim("the forward crossing path clears the pack",
      "CrossingInventoryPolicy.DropFreight(pawn)" in forward)
claim("the pack is cleared BEFORE the pawn is despawned",
      forward.index("CrossingInventoryPolicy.DropFreight") < forward.index("pawn.DeSpawn();"))
claim("the pack is cleared BEFORE any cargo custody changes hands",
      forward.index("CrossingInventoryPolicy.DropFreight")
      < forward.index("TryTransferToContainer"))
claim("a pack that will not empty refuses the crossing rather than crossing with it",
      "HasFreight(pawn)" in forward and "RR_PortalCrossing_PackNotCleared" in forward)
recover = slice_method(service_code, "TryRecoverToSource")
claim("the ROLLBACK path does not clear the pack",
      "CrossingInventoryPolicy" not in recover,
      "a crossing that failed through no fault of the pawn must not cost it its goods")
claim("exactly one call site drops freight",
      service_code.count("CrossingInventoryPolicy.DropFreight") == 1,
      "`in` cannot tell one site from three; this is counted")
claim("the refusal key is declared in the keyed file",
      keyed.count("<RR_PortalCrossing_PackNotCleared>") == 1)

# ------------------------------------------------- nothing references the mod that raised it
claim("the policy names no third-party mod, namespace or type",
      not re.search(r"PickUpAndHaul|Mehni|HaulToStack|jkluch|prisonlabor|avius", policy,
                    re.I),
      "the behaviour is identical with every one of them absent, which is invariant 42 "
      "satisfied by there being nothing to apply")
claim("the policy uses only Verse",
      [line for line in policy.split("\n") if line.startswith("using ")] == ["using Verse;"])
claim("no new saved state was introduced",
      "Scribe" not in policy_code,
      "the drop count is not needed after the crossing, and derived beats stored")

# ------------------------- Prison Labor's axis, INVERTED BY OWNER DIRECTION 2026-10-06
#
# **This claim was the register's settled line, and the owner overruled it.** Row 288, Prison Labor:
# *"Settled on one axis: a prisoner given work by this mod can never cross a gate.
# PortalTraversalPolicy admits only Faction.OfPlayer colonists."* The claim asserted exactly that,
# by construction, in every entry point.
#
# **Owner, 2026-10-06:** *"a prisoner should be able to cross a gate is allowed to ( send the
# prisonerrs to live and work in there and cross path back if zoned to and door are allowed access
# remmebr mods we have also along side all of that.. locks and prisoner mods"*.
#
# So a prisoner given work may cross, and the axis that replaces it is **custody survives the
# crossing**. That rule is owned by `check-traversal-policy.py` -- named here rather than copied,
# because two derivations of one rule is the defect this project keeps meeting.
#
# What this proof is entitled to assert is the shape of the gate it reads: the question is custody
# **or** faction, asked in one place, and never faction alone. Faction alone is what locked a
# prisoner out of every crossing while letting them out through the egress path on the same day.
# **COUNTED, because a plant gutting ONE gate left the other standing and this passed.** The work
# gate and the ordered gate both ask it; a containment test cannot tell one from two.
claim("the traveller gate asks CUSTODY, not faction alone",
      traversal_code.count("RimroomsPortalCrossingService.InOurCare(traveller)") == 2
      and "!traveller.IsColonist" not in traversal_code,
      "a prisoner of the colony keeps its own faction and is held by HostFaction, so a faction "
      "test is not a test of whose pawn it is")
adapter_files = sorted(f for f in os.listdir(ADAPTERS) if f.endswith(".cs"))
gated = [f for f in adapter_files
         if "TravellerFailureKey" in code_only(read(os.path.join(ADAPTERS, f)))]
claim("EVERY connected-work adapter gates on the traveller policy",
      len(adapter_files) > 0 and len(gated) == len(adapter_files),
      "%d of %d" % (len(gated), len(adapter_files)))
giver_files = sorted(f for f in os.listdir(GIVERS)
                     if f.startswith("WorkGiver_") and f.endswith(".cs"))
giver_gated = [f for f in giver_files
               if "TravellerFailureKey" in code_only(read(os.path.join(GIVERS, f)))]
claim("EVERY connected work giver gates on the traveller policy",
      len(giver_files) > 0 and len(giver_gated) == len(giver_files),
      "%d of %d" % (len(giver_gated), len(giver_files)))
claim("the gate is one function, not a condition copied into nine files",
      traversal_code.count("public static string TravellerFailureKey") == 1,
      "one pattern, all the files it guards")
# **RESTATED AT 0.12.99-dev, AND THIS PROOF HAD BEEN FAILING UNRUN SINCE THE CONSTANT WENT.** The
# claim was:
#
#     claim("autonomous non-player traversal is still a constant false",
#           "AutonomousNonPlayerTraversalPermitted = false" in flat(traversal_code))
#
# The owner rewrote invariant #1 on 2026-10-06 and the constant was **deleted rather than left at
# false**, because a constant denying what the code beside it does is a stale comment with a
# compiler behind it. So this claim demanded the opposite of the shipped design, and nothing said so
# because nobody ran this proof between the deletion and now. **That is the fourth instrument this
# session found asserting something the code had stopped doing**, and it is the loudest kind: a
# straightforward red, which is the lucky direction.
#
# **It is not replaced with a copy of checker 29's rules.** That checker owns the retirement and owns
# *nothing is ever lured*; restating either here would be two derivations of one rule. What this
# proof is about is the crossing PACK -- what a traveller may carry and who may be carried -- so the
# claim becomes the thing this file is entitled to assert: the constant is gone, and the question it
# used to answer now lives in one named place.
claim("the retired traversal constant is gone, not left at false",
      "AutonomousNonPlayerTraversalPermitted" not in code_only(traversal_code),
      "owner rewrote invariant #1; check-traversal-policy.py owns the rule now")
claim("and the permission question still lives in the one chokepoint",
      "public static string OutboundCrossingFailureKey" in traversal_code
      and "public static string IncursionFailureKey" in traversal_code,
      "both crossing directions decided in PortalTraversalPolicy and nowhere else")

# ---------------------------------------------------------------------------------- report
bad = [(label, detail) for label, ok, detail in CLAIMS if not ok]
for label, ok, detail in CLAIMS:
    print("%s  %s" % ("ok   " if ok else "FAIL!", label))
    if detail and not ok:
        print("       %s" % detail)
print("")
print("%d of %d claims hold" % (len(CLAIMS) - len(bad), len(CLAIMS)))
sys.exit(1 if bad else 0)
