# -*- coding: utf-8 -*-
"""Refuse to ship a thing this mod authors that nothing reads.

Why this exists
---------------
This project's most expensive defect class, four times over:

  * **0.11.7-dev** -- five `RR_*Staff` PawnKinds, authored and read by nothing.
  * **0.11.8-dev** -- no `IncidentDef` existed, so the storyteller did not know the mod was there.
  * **0.12.11-dev** -- `RimroomsRequestDef`, `RequestRoutes` and seven authored requests were read
    by **zero lines of C#**. The whole campaign had been written and was unreachable, and the
    chart recorded both steps as *done*.
  * **0.12.30-dev** -- `EstablishCorporationContact()` had **no caller**, which left two of the
    three shipped starts with no campaign at all, permanently.

Every one of those passed every checker and every proof of its day. Nothing was wrong with any
individual file; the wiring between them was missing, and no tool looked at wiring.

What "wired" means, precisely
-----------------------------
**A def** is wired when any one of these is true, and the three are genuinely different routes:

  1. its `defName` appears in our C# -- resolved by name;
  2. its **type** is enumerated by our C# (`DefDatabase<ThatType>`) or is a def type **RimWorld
     itself** consumes (`ThingDef`, `ScenarioDef`, `FactionDef`, `RecipeDef`, ...) -- consumed by
     type rather than by name, which is how most content defs work;
  3. its `defName` appears in **another def's XML** -- a cross-reference, which is how the three
     `RimroomsStartDef`s are reached from their `ScenarioDef`s.

Rule 3 exists because leaving it out reported those three starts as dangling when they are not.

**An action** -- a `public` method returning `CompanyActionResult`, which is this mod's whole
player-facing verb surface -- is wired when something other than its own declaration calls it.
That is the rule that catches `EstablishCorporationContact`.

Exit status is the result. Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

# Def types RimWorld resolves itself, so our code never has to name or enumerate them. Kept short
# and explicit: a type added here without a reason is a hole in the check.
#
# **`SoundDef` WAS IN THIS LIST AND IT WAS A HOLE, EXACTLY AS THE LINE ABOVE WARNS.** RimWorld does
# not play a mod's `SoundDef` by enumerating the database -- a cue is played by an explicit call or
# named in another def's field, and nothing else ever reaches it. Listing the type as core-consumed
# therefore declared **every cue wired by existing**, which is the definition of an absence rule
# satisfied by construction.
#
# Measured 2026-10-06: **five of the seventeen shipped cues had no consumer anywhere** --
# `RR_AnalysisComplete`, `RR_ContractPaid`, `RR_CutoffThrown`, `RR_JournalFiled`, `RR_MarkerSet`,
# the whole of `ASSET_REQUESTS.md`'s *"events that happen now and make no sound"* band. They were
# delivered, described on the published asset page, given SoundDefs, and never played. The asset
# page reported them as named because **a cue's own def names it**, and this checker reported them
# as wired because of this line. Two instruments agreeing while nothing plays the sound.
#
# This is the same defect class the docstring above lists four times, and it is the one that
# retired the 0.2.0 art. Removed, so a cue must now be named by our code or by another def.
CORE_CONSUMED = set("""
ThingDef TerrainDef RecipeDef ScenarioDef FactionDef IncidentDef ResearchProjectDef JobDef
WorkGiverDef ThingCategoryDef ThoughtDef HediffDef PawnKindDef ScenPartDef
MapGeneratorDef GenStepDef DesignationCategoryDef WorkTypeDef StatDef TraitDef RulePackDef
MainButtonDef KeyBindingDef TaleDef ColorDef
""".split())

problems = []
notes = []


def fail(message):
    problems.append(message)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def source_files():
    """Hand-written C# only. obj/ and bin/ hold generated copies that would mask a real gap."""
    found = {}
    for root, _, names in os.walk(SRC):
        if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
            continue
        for name in names:
            if name.endswith(".cs"):
                path = os.path.join(root, name)
                found[path] = strip_cs_comments(read(path))
    return found


def declared_defs():
    """defName -> (type name, the def's own declaration body).

    The body is returned because rule 3 has to subtract it. See `check_defs`.
    """
    found = {}
    for path in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
        text = strip_xml_comments(read(path))
        wrapper = re.search(r"<Defs>(.*)</Defs>", text, re.S)
        if wrapper is None:
            continue
        for match in re.finditer(r"<([A-Za-z0-9_.]+)(?:\s[^>]*)?>\s*(.*?)\s*</\1>",
                                 wrapper.group(1), re.S):
            body = match.group(2)
            name = re.search(r"<defName>([^<]+)</defName>", body)
            if name:
                found.setdefault(name.group(1).strip(), (match.group(1), body))
    return found


def check_defs(problems, source_blob):
    declared = declared_defs()
    if not declared:
        fail("no defs parsed at all; the package layout has moved")
        return 0

    # **ENUMERATION, NOT ANY MENTION OF THE DATABASE.** This matched `DefDatabase<T>` anywhere,
    # which counted `DefDatabase<SoundDef>.GetNamedSilentFail(cueId)` as *this type is enumerated*.
    # A by-name lookup on a variable proves the opposite: it says some cue is fetched, and nothing
    # whatever about whether any particular cue is ever reachable. That is how `RR_MarkerSet` stayed
    # "wired" through two separate attempts to catch it -- the plant in `.local/qa/` renamed its only
    # `Play` call and this check stayed green both times.
    #
    # `AllDefs` and `AllDefsListForReading` are the real thing: code that walks every def of a type
    # genuinely consumes all of them. A `GetNamed*` call names its target, so rule 1 already covers
    # the defs it reaches, by the literal in the call.
    enumerated = set(t.split(".")[-1] for t in re.findall(
        r"DefDatabase<([A-Za-z0-9_.]+)>\s*\.\s*AllDefs", source_blob))

    # Every def XML, so a cross-reference from one def to another counts as wiring.
    def_xml = "\n".join(strip_xml_comments(read(path)) for path in
                        glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True))

    for name, (kind, own_body) in sorted(declared.items()):
        short = kind.split(".")[-1]
        if re.search(r"\b" + re.escape(name) + r"\b", source_blob):
            continue
        if short in enumerated or short in CORE_CONSUMED:
            continue
        # A cross-reference means the name appears somewhere OTHER than its own declaration, and
        # **`> 1` was the wrong way to ask that.** A def whose own block names itself twice then
        # cross-references itself. Every one of the seventeen `SoundDef`s does exactly that: the
        # block carries `<defName>RR_MarkerSet</defName>` **and**
        # `<clipPath>Rimrooms/RR_MarkerSet</clipPath>`, because the clip file is named after the
        # cue. So the count was 2 for a cue nothing played, and the rule passed.
        #
        # Measured 2026-10-06 by planting it: renaming the one `Play` call for `RR_MarkerSet` left
        # this check **green**, which is the only reason the loophole was found rather than assumed
        # closed when `SoundDef` came out of `CORE_CONSUMED`.
        #
        # Counting against the def's own body fixes it for every type, not just cues -- any def
        # that happens to repeat its own name inside itself had the same free pass.
        elsewhere = (len(re.findall(r"\b" + re.escape(name) + r"\b", def_xml))
                     - len(re.findall(r"\b" + re.escape(name) + r"\b", own_body)))
        if elsewhere > 0:
            continue
        fail("%s (%s) is declared and nothing reads it: not named in C#, its type is neither "
             "enumerated nor Core-consumed, and no other def references it" % (name, short))
    notes.append("%d def(s) declared, %d type(s) enumerated by our own code"
                 % (len(declared), len(enumerated)))
    return len(declared)


def check_actions(problems, files):
    """Every public CompanyActionResult method must be called from somewhere."""
    signature = re.compile(r"public\s+(?:static\s+)?CompanyActionResult\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    total = 0
    for path, text in sorted(files.items()):
        for match in signature.finditer(text):
            name = match.group(1)
            total += 1
            calls = 0
            for other, body in files.items():
                hits = len(re.findall(r"\b" + re.escape(name) + r"\s*\(", body))
                # Its own file contains the declaration, so one hit there is not a call.
                calls += hits - 1 if other == path else hits
            if calls <= 0:
                fail("%s in %s returns a CompanyActionResult and nothing calls it. A verb with no "
                     "caller is a feature that does not exist -- this is how "
                     "EstablishCorporationContact left two starts with no campaign"
                     % (name, os.path.relpath(path, REPO)))
    notes.append("%d public action method(s) checked for callers" % total)
    return total


def main():
    files = source_files()
    if not files:
        fail("no C# sources found; the source layout has moved")
        return report()
    blob = "\n".join(files.values())
    check_defs(problems, blob)
    check_actions(problems, files)
    check_deployment_chain(problems, files)
    return report()


def check_deployment_chain(problems, files):
    """Every registered deployment provider must be reachable through all three of its links.

    **Owner, 2026-10-05, verbatim:** *"u have a habit of half completing and half wiring up and
    half connecting things"*. This is that class, and the chain is three links long with each one
    in a different kind of file:

        registered in `ConnectedDeploymentProviders`
            -> a `WorkGiver_Connected*` subclass overrides `ProviderId` to return it
                -> a `WorkGiverDef` names that subclass in `giverClass`

    `ConnectedDeploymentProviders.Get(id)` is the **only** consumer -- `All` is never enumerated --
    so a provider whose chain is broken at any link is a thing a pawn can never be asked to do,
    and nothing else in this repository would notice. The registry would still list it, the class
    would still compile, and the work would simply never be offered.

    Measured at 0.12.98-dev: 27 providers, 27 subclasses, all present in defs. **The point of
    writing it down is the twenty-eighth.**
    """
    provider = next((text for path, text in files.items()
                     if path.endswith("ConnectedDeploymentProvider.cs")), None)
    if provider is None:
        problems.append("ConnectedDeploymentProvider.cs is gone; the deployment chain cannot be "
                        "checked, which is a failure rather than a skip")
        return
    code = strip_cs_comments(provider)
    registry = re.search(r"registry\s*=[^;]*?\{(.*?)\};", code, re.S)
    if registry is None:
        problems.append("the deployment provider registry could not be read, so no provider's "
                        "reachability is being checked")
        return
    registered = sorted(set(re.findall(r"\{\s*(\w+),", registry.group(1))))
    if not registered:
        problems.append("the deployment provider registry parsed as empty. An absence rule over "
                        "an empty set passes by construction, which is the trap this guards")
        return

    everything = strip_cs_comments("\n".join(files.values()))
    givers = {}
    for match in re.finditer(
            r"class (WorkGiver_\w+)\s*:\s*WorkGiver_ConnectedDeployment(.*?)(?=class |\Z)",
            everything, re.S):
        used = re.search(
            r"ProviderId\s*\{\s*get\s*\{\s*return ConnectedDeploymentProviders\.(\w+)",
            match.group(2))
        if used:
            givers.setdefault(used.group(1), []).append(match.group(1))

    # `giverClass`, which is RimWorld's own field name. Looking for `workGiverClass` instead found
    # zero and reported all twenty-seven providers unreachable -- a confident wrong answer about
    # shipped work, caught only because the number was too round to believe.
    declared = set()
    for path in sorted(glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True)):
        text = strip_xml_comments(read(path))
        declared.update(re.findall(r"<giverClass>\s*[\w.]*?(\w+)\s*<", text))

    for constant in registered:
        subclasses = givers.get(constant, [])
        if not subclasses:
            problems.append("deployment provider %r is registered and NO WorkGiver subclass "
                            "returns it, so no pawn can ever be asked to do it" % constant)
            continue
        if not any(name in declared for name in subclasses):
            problems.append("deployment provider %r has subclass(es) %s and NONE of them is named "
                            "by a WorkGiverDef's giverClass, so the work is never offered"
                            % (constant, ", ".join(sorted(subclasses))))
    notes.append("deployment chain: %d provider(s) registered, each with a WorkGiver subclass "
                 "named by a WorkGiverDef" % len(registered))


def report():
    print("wiring check")
    for note in notes:
        print("  note: %s" % note)
    if problems:
        print("")
        for problem in problems:
            print("  FAIL %s" % problem)
        print("")
        print("FAILED: %d problem(s)" % len(problems))
        return 1
    print("  everything this mod authors is read by something")
    return 0


if __name__ == "__main__":
    sys.exit(main())
