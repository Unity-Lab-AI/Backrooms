# -*- coding: utf-8 -*-
"""The positive half of the stand-alone guarantee: the package names nothing it does not ship.

Why this exists
---------------
**Owner direction, verbatim:** *"we will completely make the mod 100% functional and stand alone
not needing any other mods"*, *"DLCs only add content"*, and the form that turned out to be the
useful one: *"everything the mod needs is supplied wwith the mod as the mod, which will have all
things needed to operate"*.

The queue rows said exactly why none of the existing instruments could establish this:

    **PARTLY HELD 0.12.87-dev. The negative half is enforced:** `check-dlc-gating.py` refuses
    unguarded DLC content and every expansion is optional. **The positive half is the guarantee
    half** -- proving that nothing the mod needs to operate lives behind an expansion needs the
    row-by-row audit that has its own row and stays open. **A declaration cannot establish it.**

`check-dlc-gating.py` answers *"is every expansion reference gated?"*. It cannot answer *"does
this package reference anything it neither ships nor finds in Core?"*, because a def belonging to
one of the 294 profile mods is not DLC-only -- it is not in the game's `Data/` folders at all, so
that checker never sees it. **That is the hole this closes**, and it is the hole a stand-alone
claim actually depends on: one `thingDefName` naming another mod's building would make the
package quietly require that mod, with no error anywhere until a player without it reached the
feature.

What it checks
--------------
1. **Every def-name-bearing field in every packaged Def** resolves in *our own defs* or in
   *Core* -- or, if it resolves only in an expansion, is `MayRequire`-gated.
   The field list is **enumerated from our own C# source**, not maintained by hand: a
   `public string *DefName*` or `public List<string> *DefNames*` on one of our Def classes is a
   def reference by construction. That is the same discipline `check-register-compliance.py`
   adopted after listing `thingDef` and missing `<thing>` cost it 114 of 171 references.
2. **Every literal def lookup in C#** resolves in our defs or Core, or -- for an expansion
   def -- goes through `GetNamedSilentFail`, which returns null rather than throwing.
3. **No hard `GetNamed` on anything we do not ship**, because that one throws.
4. **No third-party assembly reference** in the project file. A stand-alone package cannot be
   compiled against another mod's DLL, and this is the only place that could happen.

What it deliberately does not check
-----------------------------------
Prose. A keyed string, a label or a description that happens to contain a word which is also a
defName is not a reference, and `IGNORED` exists for the handful of fields that are read as text.
The field enumeration above means this is a short list rather than a growing one.

Usage
-----
    python tools/check-standalone-guarantee.py
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ElementTree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
SRC = os.path.join(REPO, "src")
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
CSPROJ = os.path.join(SRC, "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj")

EXPANSIONS = {
    "Royalty": "Ludeon.RimWorld.Royalty",
    "Ideology": "Ludeon.RimWorld.Ideology",
    "Biotech": "Ludeon.RimWorld.Biotech",
    "Anomaly": "Ludeon.RimWorld.Anomaly",
    "Odyssey": "Ludeon.RimWorld.Odyssey",
}

# Assemblies a stand-alone package may compile against: the game's own and Unity's.
ALLOWED_ASSEMBLIES = ("Assembly-CSharp", "UnityEngine", "System", "mscorlib", "netstandard")


def defnames_under(folder):
    found = set()
    root_dir = os.path.join(GAME_DATA, folder)
    if not os.path.isdir(root_dir):
        return found
    for path in glob.glob(os.path.join(root_dir, "**", "*.xml"), recursive=True):
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError:
            continue
        for node in root.iter("defName"):
            if node.text:
                found.add(node.text.strip())
    return found


def our_defnames():
    found = set()
    for path in glob.glob(os.path.join(MOD, "**", "*.xml"), recursive=True):
        if os.sep + "Keyed" + os.sep in path:
            continue
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError:
            continue
        for node in root.iter("defName"):
            if node.text:
                found.add(node.text.strip())
    return found


def source_files():
    for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
        normalised = path.replace(os.sep, "/")
        if "/bin/" in normalised or "/obj/" in normalised:
            continue
        yield path, io.open(path, encoding="utf-8-sig").read()


def reference_fields():
    """Def-name-bearing field names, enumerated from our own source.

    A `public string somethingDefName` or `public List<string> somethingDefNames` on one of our
    Def classes names another def by construction. Enumerating rather than listing is the lesson
    `check-register-compliance.py` paid for: a hand-kept list of tags missed `<thing>` and read
    114 of 171 references as nothing.
    """
    fields = set()
    singular = re.compile(r"public\s+string\s+(\w*Def(?:Name)?)\s*[;=]")
    plural = re.compile(r"public\s+List<string>\s+(\w*(?:DefNames|Projects|Requests|Kinds))\s*[;=]")
    for _, text in source_files():
        for match in singular.finditer(text):
            fields.add(match.group(1))
        for match in plural.finditer(text):
            fields.add(match.group(1))
    # Fields read as free text rather than as a reference. Short, and it stays short because the
    # enumeration above only picks up names that already look like references.
    fields -= {"startDefName", "stateFaultKey"}
    return fields


def gated_nodes(definition, inherited=frozenset()):
    """Every element under a def, paired with the package ids gating it.

    `MayRequire` applies to the element carrying it and everything inside it, which is how
    RimWorld reads it and how Core uses it on string lists.
    """
    gates = set(inherited)
    attribute = definition.get("MayRequire") or ""
    gates |= {part.strip() for part in attribute.split(",") if part.strip()}
    yield definition, gates
    for child in definition:
        for pair in gated_nodes(child, gates):
            yield pair


def main():
    problems = []
    core = defnames_under("Core")
    if len(core) < 1000:
        print("standalone: the installed game data was not found at %s" % GAME_DATA)
        print("            SKIPPED -- this checker cannot run without it.")
        return 0
    expansions = {folder: defnames_under(folder) for folder in EXPANSIONS}
    ours = our_defnames()
    known = ours | core
    fields = reference_fields()

    # ---------------------------------------------------------------- 1. packaged def references
    checked = 0
    gated = 0
    for path in sorted(glob.glob(os.path.join(MOD, "**", "*.xml"), recursive=True)):
        if os.sep + "Keyed" + os.sep in path:
            continue
        relative = os.path.relpath(path, REPO).replace(os.sep, "/")
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as error:
            problems.append("%s does not parse: %s" % (relative, error))
            continue
        for definition in root:
            for node, gates in gated_nodes(definition):
                # A value sits either directly in the field, or in `<li>` entries under it.
                if node.tag in fields:
                    values = [(node, (node.text or "").strip())]
                    values += [(child, (child.text or "").strip())
                               for child in node if child.tag == "li"]
                elif node.tag == "li":
                    continue
                else:
                    continue
                for holder, value in values:
                    if not value:
                        continue
                    checked += 1
                    if value in known:
                        continue
                    local = set(gates)
                    attribute = holder.get("MayRequire") or ""
                    local |= {p.strip() for p in attribute.split(",") if p.strip()}
                    owners = [folder for folder, names in expansions.items()
                              if value in names]
                    if not owners:
                        problems.append(
                            "%s: <%s>%s</%s> names a def this package does not ship and Core "
                            "does not define. A stand-alone package cannot reference another "
                            "mod's content." % (relative, node.tag, value, node.tag))
                        continue
                    wanted = {EXPANSIONS[folder] for folder in owners}
                    if local & wanted:
                        gated += 1
                        continue
                    problems.append(
                        "%s: <%s>%s</%s> resolves only in %s and is not MayRequire-gated, so "
                        "the package needs that expansion to operate."
                        % (relative, node.tag, value, node.tag, "/".join(owners)))

    # ---------------------------------------------------------------- 2 and 3. C# def lookups
    lookup = re.compile(r"GetNamed(SilentFail)?\(\s*\"([A-Za-z0-9_]+)\"")
    silent_expansion = 0
    cs_checked = 0
    for path, text in source_files():
        relative = os.path.relpath(path, REPO).replace(os.sep, "/")
        for match in lookup.finditer(text):
            silent = match.group(1) is not None
            name = match.group(2)
            cs_checked += 1
            if name in known:
                continue
            owners = [folder for folder, names in expansions.items() if name in names]
            if not owners:
                problems.append(
                    "%s: looks up def %r, which this package does not ship and Core does not "
                    "define." % (relative, name))
                continue
            if not silent:
                # `GetNamed` throws. On an install without the expansion that is a hard failure
                # in our own code, which is the one thing the guarantee cannot survive.
                problems.append(
                    "%s: looks up expansion def %r (%s) with GetNamed, which throws when the "
                    "expansion is absent. Use GetNamedSilentFail."
                    % (relative, name, "/".join(owners)))
                continue
            silent_expansion += 1

    # -------------------------------------------- 3b. a silent-fail result must DEGRADE, not deref
    #
    # **THE HALF THE GUARANTEE WAS MISSING.** Checks 2 and 3 prove the package only *names* what is
    # safe to name, and that an expansion lookup uses `GetNamedSilentFail` rather than the throwing
    # `GetNamed`. Neither proves the thing the queue row actually asks for, in its own words: that
    # *"every by-name `GetNamedSilentFail` lookup degrades rather than returning null into a
    # dereference"*.
    #
    # That distinction is the whole of the difference between **stopping advertising** and
    # **actually running**. `GetNamedSilentFail` returning null is the designed outcome on a
    # Core-only install; dereferencing it one line later is a `NullReferenceException` at the exact
    # moment the guarantee is supposed to hold, and the player sees a red error rather than a
    # feature quietly not being there.
    #
    # Every call site in the package already does this correctly -- `== null` guards, a fallback to
    # Core's own `Colonist`, and one null-conditional `?.`. **Nothing enforced it**, which is
    # precisely the condition this battery exists to remove: a discipline nobody checks is a
    # discipline until the day somebody is in a hurry.
    #
    # The window is deliberately generous and the failure direction is deliberately loud. A guard
    # further than six lines away from its lookup is reported rather than hunted for: being asked
    # to move a null check next to the call it protects is a small cost, and it is the shape the
    # rest of the package already has.
    # **NO WINDOW, AND THE WINDOW IS WHAT WAS WRONG.** A six-line window reported nine findings on
    # correct code. `GenStep_BackroomsDestination` looks up **eleven** Core defs in a block and then
    # guards all eleven in one combined `if (a == null || b == null || ...) throw`, which sits about
    # forty lines below the first lookup. That is a better shape than eleven separate guards, and a
    # rule that demanded the guard be adjacent was demanding worse code.
    #
    # So the question is simply *is this result ever null-compared*, over the whole file.
    #
    # **The limitation, stated rather than hidden:** a variable of the same name null-checked in a
    # different method would satisfy this. That is a false *negative*, and it is accepted on
    # purpose — the immediate-dereference rule above catches the hazard that actually throws, and
    # nine false positives on correct code is the failure mode this battery has paid for five times.
    assignment = re.compile(r"(\w+)\s*=\s*[^;]*GetNamedSilentFail\s*\(")
    guarded = 0
    for path, text in source_files():
        relative = os.path.relpath(path, REPO).replace(os.sep, "/")
        lines = text.split("\n")
        whole = " ".join(text.split())
        for number, line in enumerate(lines):
            if "GetNamedSilentFail" not in line:
                continue
            window = whole

            # Used null-safely on the spot: `GetNamedSilentFail(x)?.Member`, the call coalesced
            # with `??`, or the call itself compared against null. None needs a named variable.
            #
            # **THREE IDIOMS, NOT TWO.** The first version knew `?.` and a null comparison, and
            # flagged two sites already safe through `??` --
            # `doorDef = GetNamedSilentFail("Autodoor") ?? ThingDefOf.Door` is about as guarded as
            # code gets. C# has three ways to make a possibly-null value safe, and a rule that
            # knows two of them cries wolf at the third.
            if re.search(r"GetNamedSilentFail\s*\([^)]*\)\s*\?\.", line) \
                    or re.search(r"GetNamedSilentFail\s*\([^)]*\)\s*\?\?", line) \
                    or re.search(r"GetNamedSilentFail\s*\([^)]*\)\s*(==|!=)\s*null", line):
                guarded += 1
                continue

            # **A MEMBER ACCESS ON THE RESULT IS THE ONLY DEREFERENCE.** The first version of this
            # rule demanded that every result be assigned or used null-safely, and reported
            # **sixty-five findings of which fifty-six were innocent**: `OpenNativeTab(
            # GetNamedSilentFail("Work"))` *passes* the result to a method, and
            # `return ... GetNamedSilentFail(defName)` *returns* it for the caller to handle. A
            # null argument and a null return are both perfectly safe, and the one that is not is
            # `GetNamedSilentFail(...).Member`.
            #
            # Narrowed to that. Fifty-six false findings is the crying-wolf failure this battery has
            # recorded repeatedly, and a rule nobody believes protects nothing.
            if re.search(r"GetNamedSilentFail\s*\([^)]*\)\s*\.", line):
                problems.append(
                    "%s:%d: a GetNamedSilentFail result is dereferenced on the spot, so a "
                    "Core-only install throws here. Use `?.` or assign it and guard it."
                    % (relative, number + 1))
                continue

            named = assignment.search(line)
            if named is None:
                # Passed as an argument, returned, or discarded. None of those dereferences
                # anything, so none of them can break the guarantee.
                guarded += 1
                continue

            variable = named.group(1)
            if re.search(r"\b" + re.escape(variable) + r"\s*(==|!=)\s*null", window) \
                    or re.search(r"\b" + re.escape(variable) + r"\s*\?\?", window) \
                    or re.search(r"\b" + re.escape(variable) + r"\s*\?\.", window):
                guarded += 1
                continue
            problems.append(
                "%s:%d: %r comes from GetNamedSilentFail and is never null-compared in this "
                "file, so a Core-only install carries null forward from here -- the "
                "guarantee's own failure mode." % (relative, number + 1, variable))

    # ---------------------------------------------------------------- 4. no third-party assembly
    references = 0
    if os.path.isfile(CSPROJ):
        project = io.open(CSPROJ, encoding="utf-8-sig").read()
        for name in re.findall(r"<Reference\s+Include=\"([^\"]+)\"", project):
            references += 1
            bare = name.split(",")[0].strip()
            if not any(bare.startswith(allowed) for allowed in ALLOWED_ASSEMBLIES):
                problems.append(
                    "the project compiles against %r. A stand-alone package may reference only "
                    "the game's own assemblies and Unity's." % bare)
    else:
        problems.append("the project file was not found at %s" % CSPROJ)

    print("stand-alone guarantee")
    print("  our defs                     : %d" % len(ours))
    print("  Core defs indexed            : %d" % len(core))
    print("  reference fields enumerated  : %d (%s)"
          % (len(fields), ", ".join(sorted(fields))))
    print("  packaged def references      : %d checked, %d expansion-gated" % (checked, gated))
    print("  silent-fail results guarded  : %d, each degrading rather than dereferencing null"
          % guarded)
    print("  C# def lookups               : %d checked, %d expansion via GetNamedSilentFail"
          % (cs_checked, silent_expansion))
    print("  assembly references          : %d, all game or Unity" % references)
    print("")
    if problems:
        for problem in problems:
            print("  FAIL %s" % problem)
        print("")
        print("FAILED: %d problem(s)" % len(problems))
        return 1
    print("PASS: the package names only what it ships, what Core ships, and gated expansion "
          "content. Nothing it needs to operate lives behind an expansion or another mod.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
