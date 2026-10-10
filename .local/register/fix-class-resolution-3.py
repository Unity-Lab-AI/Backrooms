# -*- coding: utf-8 -*-
"""A tenth plant walked straight past the proof, and it is the claim-scoping trap again.

`plant-class-resolution.py` plant 10 restores the behaviour of the exemption:

    if True:
        continue

...and the proof still passed, because the claim it asserted was *"the exempt-everything-but-ours
line is gone"* -- which looks for the absence of a COMMENT. **A comment satisfying a behavioural
claim. The twenty-first instance of that trap, and my own, in the proof written to close a bug
caused by trusting a name.**

THE FIX IS STRUCTURAL RATHER THAN A TIGHTER STRING. The verdict becomes a pure function,
`unresolved_class_names(referenced, declared_types, game_types)`, which returns the names that
will not resolve. The proof calls it with a crafted set and requires `CompProperties_Colorable`
in the answer -- so skipping, blinding, exempting or short-circuiting the loop all fail, because
the proof is now asking for the OUTPUT rather than inspecting the route to it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECK = os.path.join(REPO, "tools", "check-package-integrity.py")
PROOF = os.path.join(REPO, ".local", "register", "proof-class-resolution.py")

OLD = u'''    game_types = index_game_type_names()
    if game_types is None:
        notes.append("game assemblies not found, so Core and DLC type names in defs were not "
                     "resolved; that part is skipped, not passed")

    for value in sorted(referenced):
        simple = value.split(".")[-1]
        if value.startswith("RimroomsAsyncIndustries"):
            if simple not in declared_types:
                fail(problems, "a def names %s, which no C# source file declares" % value)
            continue
        # NOT EXEMPT ANY MORE, AND THE EXEMPTION COST THE SEVENTH LAUNCH.
        # `<li Class="CompProperties_Colorable" />` is a Core-shaped name for a type that does
        # not exist, and a bad Class throws out of DirectXmlToObjectNew -- which discards the
        # WHOLE ThingDef, not the one comp. `Door` and `Autodoor` left the game and the log went
        # red from the top. A typo in a Core name is the likeliest kind of typo there is, so
        # taking Core names on trust was the wrong half to trust.
        if game_types is None:
            continue
        if not type_name_exists(game_types, simple):
            fail(problems, "a def names %s, and no type of that name exists in the installed "
                           "game's assemblies. A Class the game cannot resolve discards the "
                           "entire def being parsed, not just that one node" % value)'''

NEW = u'''    game_types = index_game_type_names()
    if game_types is None:
        notes.append("game assemblies not found, so Core and DLC type names in defs were not "
                     "resolved; that part is skipped, not passed")

    for value, reason in unresolved_class_names(referenced, declared_types, game_types):
        fail(problems, "a def names %s, %s" % (value, reason))


def unresolved_class_names(referenced, declared_types, game_types):
    """The type names in `referenced` the game will not be able to resolve, with the reason.

    A PURE FUNCTION ON PURPOSE, AND THIS IS THE LESSON OF THE SEVENTH LAUNCH TWICE OVER.

    The first lesson was the defect: `<li Class="CompProperties_Colorable" />` names a type that
    does not exist, and a `Class` the game cannot resolve throws out of `DirectXmlToObjectNew`,
    which discards the WHOLE ThingDef rather than the one node. `Door` and `Autodoor` left the
    game and 587 red lines followed from one line.

    The second lesson was how nearly the fix shipped unguarded. A plant that restored the old
    exemption as `if True: continue` walked past the proof, because the proof asserted that a
    COMMENT was absent rather than that a bad name is reported. So the verdict lives here, where
    a proof can hand it a crafted set of names and demand the right answer -- blinding it,
    exempting it or short-circuiting it all change the OUTPUT, which is the only thing the proof
    now accepts as evidence.

    Ours are matched against declared type names in the C# source rather than by reflecting over
    the built assembly, so that half stays honest even when the DLL is stale. Core and DLC names
    are matched against the installed game's own metadata, because a Core-shaped typo is the
    likeliest typo there is and taking those on trust was the wrong half to trust.
    """
    verdicts = []
    for value in sorted(referenced):
        simple = value.split(".")[-1]
        if value.startswith("RimroomsAsyncIndustries"):
            if simple not in declared_types:
                verdicts.append((value, "which no C# source file declares"))
            continue
        if game_types is None:
            continue
        if not type_name_exists(game_types, simple):
            verdicts.append((value, "and no type of that name exists in the installed game's "
                                    "assemblies. A Class the game cannot resolve discards the "
                                    "entire def being parsed, not just that one node"))
    return verdicts'''

text = io.open(CHECK, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("CHECK ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(CHECK, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the verdict is a pure function now")

OLD_CLAIM = u'''        check("the exempt-everything-but-ours line is gone",
              'continue                      # Core and DLC types' not in read(CHECK),
              "-- that comment was the hole: our own names were checked and Core's were taken "
              "on trust, and a Core-shaped typo is the likeliest typo there is")'''

NEW_CLAIM = u'''        # THE VERDICT IS DEMANDED, NOT INSPECTED, and the first draft of this claim was the
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
              "-- reported %r. A check that fails correct code gets deleted" % sorted(named))'''

proof = io.open(PROOF, encoding="utf-8").read()
if proof.count(OLD_CLAIM) != 1:
    print("PROOF ANCHOR PROBLEM: %d" % proof.count(OLD_CLAIM))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(proof.replace(OLD_CLAIM, NEW_CLAIM, 1))
print("the proof demands the verdict instead of reading a comment")
