"""Refuse to ship a def that sets a field the def class does not have.

Why this exists
---------------
At 0.8.7-dev a real defect was found by hand: ``maxTechLevel`` was emitted in the room
archetype XML for **fourteen** defs while the C# class had no such field. RimWorld logs an
unknown field to the dev console and **carries on loading**, so the setting had been doing
nothing since 0.7.9-dev. The build did not care, none of the checkers looked, and the only
symptom was that a tuning knob the design relied on was silently inert.

Row 922 records that a checker for this was written at the time and **removed rather than
shipped**, because every part verified in isolation and the assembled function reported
nothing -- and *"a checker that silently passes everything is worse than no checker: it
manufactures confidence."* That row asks the next attempt to start from the verified parts,
which is what this does, and to prove it can fail, which the fault plants do.

What it checks, and what it deliberately does not
-------------------------------------------------
**Direct children of every def node**, and only those. That is where the real defect was, and
it is the level at which "what fields does this type have" can be answered without a
reflection host. Nested compound values (``<statBases><Beauty>``) and list items (``<li>``)
are not descended into, and the docstring says so rather than the check quietly implying a
depth it does not have.

Two sources of truth, because this mod ships two kinds of def:

1. **Our own def classes.** Parsed out of ``src/**/*.cs``: every ``public <type> <name>``
   field on the class, plus its declared base class walked up the chain, plus the fields
   ``Verse.Def`` itself carries. A field our XML sets that no class in that chain declares is
   the 0.8.7-dev defect exactly.

2. **What the game's own defs of that type set**, indexed across ``Data/*/Defs``.

3. **The real fields on a game def class**, decompiled from ``Assembly-CSharp.dll`` with the
   same tool the Core source reviews use, and cached against the assembly's timestamp and
   size so a game update invalidates it.

Source 3 exists because source 2 has a hole, and the checker found it on its first honest
run: it reported ``<canMakeRandomly>`` on a FactionDef of ours as unknown, and ``FactionDef``
**does** have that field -- Core simply never writes it in XML, because the default is what
Core wants. **Learning field names from usage can only find the fields somebody happened to
need.**

Sources 2 and 3 are **unioned**, and the union is deliberately generous, because a false
positive blocks a build over a real field while the defect class being hunted is a *typo* --
and a typo matches neither source. When the decompiler or the assembly is absent the checker
still runs on source 2 alone and the summary says so.

Usage
-----
    python tools/check-def-fields.py
"""

import collections
import glob
import io
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ElementTree

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
SRC = os.path.join(REPO, "src")
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

# Verse.Def's own fields, read from the decompiled class rather than remembered. Every def of
# every type may set these.
DEF_BASE_FIELDS = {
    "defName", "label", "description", "descriptionHyperlinks", "ignoreConfigErrors",
    "ignoreIllegalLabelCharacterConfigError", "modExtensions",
}

# Node names inside a Defs file that are not defs at all.
NOT_DEFS = {"Operation", "match", "nomatch", "value", "li"}

# XML attributes, never children. Listed so a reader knows they were considered.
ATTRIBUTES = {"ParentName", "Name", "Abstract", "MayRequire", "MayRequireAnyOf", "Class",
              "Inherit"}


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


# --------------------------------------------------------------------------- #
# Source 1: our own def classes
# --------------------------------------------------------------------------- #

def our_def_classes():
    """class name -> (base class name, set of field names declared on it).

    Verified part, unchanged in shape from the 0.8.7-dev attempt: the field regex reads a
    public field declaration with or without an initialiser, and ignores properties (which
    carry a brace) and methods (which carry a parenthesis).
    """
    classes = {}
    for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
        if os.sep + "obj" + os.sep in path or os.sep + "bin" + os.sep in path:
            continue
        text = read(path)
        # Strip comments so a field name inside prose cannot be read as a declaration.
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        text = "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))
        for match in re.finditer(
                r"\bclass\s+(\w+)\s*:\s*([\w<>, ]+?)\s*\{", text):
            name = match.group(1)
            base = match.group(2).split(",")[0].strip()
            body = class_body(text, match.end() - 1)
            classes[name] = (base, declared_fields(body))
    return classes


def class_body(text, brace_index):
    depth = 0
    for index in range(brace_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace_index:index + 1]
    return text[brace_index:]


def declared_fields(body):
    """Public fields on one class body. A property or method is not a field.

    The declaration is judged on the text **before** any initialiser, and that is the whole
    lesson of this checker's first attempt. Rejecting a line because it contains "(" throws
    away every collection field in the project -- ``public List<string> buildingDefNames = new
    List<string>();`` has a parenthesis in its *initialiser* and is a field -- which is exactly
    the kind of silent under-reading row 922 was written about.

    Measured: the naive rule produced **159 false positives** across nine of the twelve def
    classes, every one of them a collection field. The first version of this checker reported
    nothing at all; this one reported everything. Both failures are the same mistake in the
    same function, which is why the parser is the part that carries the comment.
    """
    fields = set()
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("public "):
            continue
        # Everything up to the first "=" is the declaration; the initialiser is not our
        # business. A method or a property has its parenthesis or brace on this side of it.
        declaration = stripped.split("=", 1)[0].strip()
        if "(" in declaration or "{" in declaration:
            continue
        # public List<string> names = ... ;   /   public int weight;
        match = re.match(r"public\s+(?:readonly\s+)?[\w<>\[\],\.\? ]+?\s+(\w+)\s*;?$",
                         declaration)
        if match:
            fields.add(match.group(1))
    return fields


def fields_for_our_class(name, classes, seen=None):
    """Every field settable on one of our def classes, walking its base chain."""
    seen = seen or set()
    if name in seen or name not in classes:
        return set(DEF_BASE_FIELDS)
    seen.add(name)
    base, fields = classes[name]
    return set(fields) | fields_for_our_class(base, classes, seen) | DEF_BASE_FIELDS


# --------------------------------------------------------------------------- #
# Source 2: what the game's own defs of each type actually set
# --------------------------------------------------------------------------- #

def game_field_index():
    """def node name -> set of direct child names the game's own defs use."""
    index = collections.defaultdict(set)
    for path in glob.glob(os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml"),
                          recursive=True):
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError:
            continue
        for node in root:
            if not isinstance(node.tag, str) or node.tag in NOT_DEFS:
                continue
            for child in node:
                if isinstance(child.tag, str):
                    index[node.tag].add(child.tag)
    return index


# --------------------------------------------------------------------------- #
# Source 3: the real fields on a game def class, read from the assembly
# --------------------------------------------------------------------------- #
#
# The data index above has a hole, and the checker found it on its first honest run: it
# reported `<canMakeRandomly>` on a FactionDef of ours as unknown, and `FactionDef` **does**
# have that field -- Core simply never writes it in XML, because the default is what Core
# wants. Learning field names from usage can only ever find the fields somebody happened to
# need.
#
# So the assembly is asked as well, through the same decompiler the Core source reviews use,
# and the two sources are **unioned**: a field is allowed if the class declares it or if the
# game's own data uses it. That keeps a false positive from blocking a build over a real
# field, which matters more here than catching every conceivable unknown one -- the defect
# class being hunted is a typo, and a typo matches neither source.

ILSPY = os.path.join(REPO, ".local", "tools", "ilspycmd.exe")
MANAGED = os.path.join(os.path.dirname(GAME_DATA), "RimWorldWin64_Data", "Managed",
                       "Assembly-CSharp.dll")
CACHE = os.path.join(REPO, ".local", "def-fields-cache.json")

# Where the game's def classes live. Tried in order; the first that decompiles wins.
DEF_NAMESPACES = ("RimWorld", "Verse", "RimWorld.Planet", "Verse.AI", "Verse.Grammar")


def assembly_field_index(wanted):
    """type name -> declared field names, read from the assembly and cached.

    Returns an empty index rather than failing when the decompiler or the assembly is
    missing. The union with the data index means the checker still works, just less
    precisely, and the summary says which sources were available.
    """
    if not os.path.isfile(ILSPY) or not os.path.isfile(MANAGED):
        return {}, "unavailable"

    stamp = str(os.path.getmtime(MANAGED)) + ":" + str(os.path.getsize(MANAGED))
    cached = {}
    if os.path.isfile(CACHE):
        try:
            payload = json.loads(read(CACHE))
            if payload.get("stamp") == stamp:
                cached = payload.get("fields", {})
        except ValueError:
            cached = {}

    index = {}
    fresh = False
    for name in sorted(wanted):
        if name in cached:
            index[name] = set(cached[name])
            continue
        fields = decompile_fields(name)
        if fields is None:
            continue
        index[name] = fields
        cached[name] = sorted(fields)
        fresh = True

    if fresh:
        try:
            if not os.path.isdir(os.path.dirname(CACHE)):
                os.makedirs(os.path.dirname(CACHE))
            io.open(CACHE, "w", encoding="utf-8").write(
                json.dumps({"stamp": stamp, "fields": cached}, indent=1, sort_keys=True))
        except OSError:
            pass
    return index, "assembly"


def decompile_fields(type_name):
    """Public fields on one game def class, including its base chain."""
    for namespace in DEF_NAMESPACES:
        try:
            output = subprocess.check_output(
                [ILSPY, "-t", namespace + "." + type_name, MANAGED],
                stderr=subprocess.STDOUT).decode("utf-8", "replace")
        except (subprocess.CalledProcessError, OSError):
            continue
        if "class " + type_name not in output:
            continue
        fields = set()
        base = None
        for match in re.finditer(r"\bclass\s+" + re.escape(type_name) +
                                 r"\s*:\s*([\w\.]+)", output):
            base = match.group(1).split(".")[-1]
            break
        body = output[output.index("class " + type_name):]
        fields |= declared_fields(body)
        if base and base not in ("Def", "Editable", "object", type_name):
            inherited = decompile_fields(base)
            if inherited:
                fields |= inherited
        return fields
    return None


# --------------------------------------------------------------------------- #
# The check
# --------------------------------------------------------------------------- #

def main():
    if not os.path.isdir(GAME_DATA):
        sys.stderr.write("def-fields: game Data folder not found; check skipped, not passed\n")
        return 2

    classes = our_def_classes()
    game = game_field_index()

    # Refuse to report a pass on an empty index. Both the 0.8.7-dev failure and the
    # keyed-string parser that found 33 strings instead of 1,499 were silent-empty bugs.
    if not classes:
        sys.stderr.write("def-fields: parsed no C# classes; refusing to report a pass\n")
        return 2
    if len(game) < 50:
        sys.stderr.write("def-fields: indexed only %d game def types; refusing to report a "
                         "pass\n" % len(game))
        return 2

    ours = {name for name in classes if name.endswith("Def")}
    if not ours:
        sys.stderr.write("def-fields: found no def classes of our own; refusing to pass\n")
        return 2

    # Which game def types this package actually uses, so only those are decompiled.
    used = set()
    for path in glob.glob(os.path.join(MOD, "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError:
            continue
        for node in root:
            if isinstance(node.tag, str) and node.tag not in NOT_DEFS:
                short = node.tag.split(".")[-1]
                if short not in ours:
                    used.add(short)
    assembly, assembly_state = assembly_field_index(used)

    problems = []
    checked_defs = 0
    checked_fields = 0
    unknown_types = set()

    for path in sorted(glob.glob(os.path.join(MOD, "**", "Defs", "**", "*.xml"),
                                 recursive=True)):
        relative = os.path.relpath(path, REPO).replace("\\", "/")
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as error:
            problems.append("%s: will not parse (%s)" % (relative, error))
            continue
        for node in root:
            if not isinstance(node.tag, str) or node.tag in NOT_DEFS:
                continue
            # A fully-qualified node name is one of ours; take the last segment.
            short = node.tag.split(".")[-1]
            if short in ours:
                allowed = fields_for_our_class(short, classes)
                source = "the C# class"
            elif short in game or short in assembly:
                # Unioned on purpose: the class declares fields Core never writes, and Core's
                # data uses names the class inherits from a base the decompiler chain missed.
                allowed = (set(game.get(short, ())) | set(assembly.get(short, ()))
                           | DEF_BASE_FIELDS)
                source = ("the class or the game's own defs of this type"
                          if short in assembly else "the game's own defs of this type")
            else:
                unknown_types.add(short)
                continue
            checked_defs += 1
            name = node.findtext("defName") or node.get("Name") or "(unnamed)"
            for child in node:
                if not isinstance(child.tag, str) or child.tag in ATTRIBUTES:
                    continue
                checked_fields += 1
                if child.tag not in allowed:
                    problems.append(
                        "%s: %s <%s> sets <%s>, which %s does not have"
                        % (relative, short, name, child.tag, source))

    print("def-fields")
    print("  our def classes         : %d" % len(ours))
    print("  game def types indexed  : %d" % len(game))
    print("  game classes decompiled : %d (%s)" % (len(assembly), assembly_state))
    print("  defs checked            : %d" % checked_defs)
    print("  direct fields checked   : %d" % checked_fields)
    print("  scope                   : direct children of a def node; nested values and <li> "
          "are not descended into")
    if unknown_types:
        print("  node types not resolved : %s" % ", ".join(sorted(unknown_types)))

    # The guard row 922 asks for: a check that looked at nothing must not report a pass.
    if checked_defs == 0 or checked_fields == 0:
        sys.stderr.write("def-fields: examined %d defs and %d fields; refusing to report a "
                         "pass\n" % (checked_defs, checked_fields))
        return 2

    print("")
    if problems:
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
