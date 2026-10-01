# -*- coding: utf-8 -*-
"""The seventh launch's defect, and the only proof here that EXECUTES the thing it checks.

Owner: *"oh my god! look at the debug log!!!! its nothing but red!!!!!!!!!!!!!"*

587 red lines. Every single one of them named `Door`, `Autodoor`, or `CompProperties_Colorable`
and nothing else -- one line in one patch file:

    <li Class="CompProperties_Colorable" />

**There is no such type.** `CompColorable` is declared with a plain `CompProperties` carrying a
`compClass`, which is how Core does it for textiles, apparel and the Ideology floor coverings.
And a `Class` the game cannot resolve does not fail the one node: it throws out of
`DirectXmlToObjectNew`, which **discards the whole ThingDef being parsed.** `Door` and `Autodoor`
left the game, and 585 further errors were other defs failing to cross-reference them.

WHY THIRTEEN CHECKERS AND FORTY-ONE PROOFS MISSED IT. `check_class_references` carried this:

    if not value.startswith("RimroomsAsyncIndustries"):
        continue                      # Core and DLC types; not ours to verify from source.

**The one category it exempted is the category that killed the game** -- and a Core-looking name
is precisely what a typo produces, so the trusted half was the wrong half.

WHY THIS PROOF IS SHAPED DIFFERENTLY FROM THE OTHER FORTY-ONE, and it is the lesson of this
checkpoint. Every other proof reads source text and asserts something about it. **A proof that
reads text cannot tell whether a resolver resolves.** The first draft of the fix read the CLI
metadata `#Strings` heap by splitting on NUL, which silently misses suffix-shared names: it
rejected `<thingClass>Building</thingClass>`, which is correct code, and a text-reading proof
would have happily confirmed the resolver was "present and wired". So this one IMPORTS the
checker and ASKS IT, with names whose answers are known independently:

  * accepted, because they are real and some are only reachable as a shared suffix;
  * rejected, including the exact name that cost the launch.

A blinded resolver, an always-true resolver and a resolver that cannot see suffixes all fail
here, and none of them could be caught by looking at the source.
"""
import importlib.util
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECK = os.path.join(REPO, "tools", "check-package-integrity.py")
PATCH = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Patches",
                     "RR_NativeGateProviders.xml")

failures = []


def check(claim, held, detail=""):
    print("  %s  %s%s" % ("HOLDS " if held else "FAILS!", claim,
                          "" if held else "\n          " + detail))
    if not held:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8").read()


print("")
print("THE CLASS NAME THAT DELETED `Door` FROM THE GAME")
print("=" * 78)
print("")

patch = read(PATCH)

check("the patch no longer names a type the game does not have",
      'Class="CompProperties_Colorable"' not in patch,
      "-- this exact string produced 587 red lines, because a bad Class discards the entire "
      "ThingDef rather than the one comp")

check("and it asks for CompColorable the way Core asks for it",
      "<compClass>CompColorable</compClass>" in patch,
      "-- a plain CompProperties carrying a compClass, as Core does for textiles, apparel and "
      "the Ideology floor coverings; the last of those are buildings, so it is right for a door")

check("the glower beside it is still the Core type, which does exist",
      'Class="CompProperties_Glower"' in patch,
      "-- unchanged: CompProperties_Glower is real, and only the Colorable line was wrong")

print("")
print("THE RESOLVER IS EXECUTED, NOT READ -- the only way to catch what this missed")
print("-" * 78)

spec = importlib.util.spec_from_file_location("rr_integrity", CHECK)
integrity = importlib.util.module_from_spec(spec)
loaded = True
try:
    spec.loader.exec_module(integrity)
except Exception as problem:                                  # noqa: BLE001 - reported, not hidden
    loaded = False
    check("the package-integrity checker imports", False, "-- %r" % (problem,))

if loaded:
    check("the checker exposes a resolver to interrogate",
          hasattr(integrity, "index_game_type_names") and hasattr(integrity, "type_name_exists"),
          "-- if these are renamed this proof must fail rather than quietly skip")

if loaded and hasattr(integrity, "index_game_type_names"):
    heaps = integrity.index_game_type_names()
    if heaps is None:
        check("the installed game's assemblies were found", False,
              "-- without them this proof verifies nothing, so it fails rather than passes. "
              "The checker itself only notes the skip; a proof must not.")
    else:
        check("the metadata name heap is substantial",
              len(heaps) > 500000,
              "-- %d bytes. A near-empty heap means the parse failed and every name would be "
              "rejected" % len(heaps))

        # Known-real. `Building`, `Pawn` and `Filth` are the load-bearing ones: they are stored
        # ONLY as shared suffixes of longer names, so a resolver that splits the heap on NUL
        # rejects them. That draft existed, and it failed correct code.
        for name in ("CompProperties_Glower", "CompColorable", "PatchOperationAdd",
                     "PatchOperationSequence", "ScenPart_StartingThing_Defined", "Building",
                     "ThingWithComps", "IThingGlower"):
            check("resolves the real type %s" % name,
                  integrity.type_name_exists(heaps, name),
                  "-- this type exists in the installed game. Rejecting it would fail correct "
                  "code, which is worse than the hole this check closed")

        # Known-absent. The first is the name that cost the launch.
        for name in ("CompProperties_Colorable", "CompProperties_Colourable",
                     "RR_NoSuchTypeAnywhereInTheGame", "CompProperties_RimroomsNotAThing"):
            check("REJECTS the absent type %s" % name,
                  not integrity.type_name_exists(heaps, name),
                  "-- an always-true resolver passes everything and manufactures confidence; "
                  "that is the state this checker was in for the whole build")

        # THE VERDICT IS DEMANDED, NOT INSPECTED, and the first draft of this claim was the
        # claim-scoping trap for the twenty-first time: it asserted that a COMMENT was absent,
        # so a plant restoring the exemption as `if True: continue` walked straight past it.
        # Asking the function for its answer cannot be satisfied by any amount of rewording.
        verdict = integrity.unresolved_class_names(
            set(["CompProperties_Colorable", "CompProperties_Glower", "Building",
                 "RimroomsAsyncIndustries.Portals.CompProperties_RimroomsEmergence",
                 "RimroomsAsyncIndustries.Portals.CompProperties_NotDeclaredAnywhere"]),
            set(["CompProperties_RimroomsEmergence"]),
            heaps)
        named = dict(verdict)

        check("A CORE NAME THAT DOES NOT EXIST IS REPORTED",
              "CompProperties_Colorable" in named,
              "-- the exact line that cost the seventh launch. Exempting, blinding or "
              "short-circuiting the loop all fail here, because this asks for the output")

        check("one of ours that no source declares is reported",
              "RimroomsAsyncIndustries.Portals.CompProperties_NotDeclaredAnywhere" in named,
              "-- the half that already worked, still planted rather than assumed")

        check("and nothing real is reported",
              not set(["CompProperties_Glower", "Building",
                       "RimroomsAsyncIndustries.Portals.CompProperties_RimroomsEmergence"])
              & set(named),
              "-- reported %r. A check that fails correct code gets deleted" % sorted(named))

print("")
if failures:
    print("%d CLAIM(S) FAILED" % len(failures))
    for claim in failures:
        print("  - %s" % claim)
    sys.exit(1)
print("ALL CLASS-RESOLUTION CLAIMS HOLD")
