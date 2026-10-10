# -*- coding: utf-8 -*-
"""The seventh launch: a Class name that does not exist deleted `Door` from the game.

Owner: *"oh my god! look at the debug log!!!! its nothing but red!!!!!!!!!!!!!"* -- and the log
opens with it:

    Exception loading def from file Buildings_Structure.xml: System.ArgumentException:
      Could not find type named CompProperties_Colorable from node
      <li Class="CompProperties_Colorable" />
    Could not resolve cross-reference to Verse.ThingDef named Door (wanter=relatedBuildCommands)
    Could not resolve cross-reference: No Verse.ThingDef named Autodoor found ...   (x many)

**There is no `CompProperties_Colorable` type in RimWorld.** `CompColorable` is declared with a
plain `CompProperties` carrying a `compClass`, which is how Core does it for textiles, apparel and
the Ideology floor coverings -- the last of which are buildings, so it is the right mechanism for a
door, it was only spelled with a class that does not exist.

AND A BAD `Class` DOES NOT FAIL ONE COMP. It throws out of `DirectXmlToObjectNew`, which
**discards the entire ThingDef being parsed**: `Door` and `Autodoor` were gone from the game, so
every def that referenced them failed to cross-resolve and the log went red from the top.

WHY NOTHING CAUGHT IT, and this is the part worth fixing. `check_class_references` has resolved
`Class="..."` since 0.12.x -- but it carried this line:

    if not value.startswith("RimroomsAsyncIndustries"):
        continue                      # Core and DLC types; not ours to verify from source.

**The one category of name it exempted is the category that just killed the game.** Our own type
names were checked; Core's were taken on trust, and a Core-looking name is exactly what a typo
produces. So the check now resolves those too, against the type names in the installed game's own
assemblies, read straight out of the CLI metadata `#Strings` heap -- no dependency, no reflection,
no DLL load.

The heap is an over-approximation: it holds every metadata name, not only type names, so a
mis-spelling that happens to collide with some member name elsewhere could still pass. That is
stated in the check rather than glossed, and it is strictly sounder than the exemption it
replaces -- it cannot fail correct code, and it does catch this.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECK = os.path.join(REPO, "tools", "check-package-integrity.py")

OLD_CONST = u'GAME_DATA = r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\RimWorld\\Data"'
NEW_CONST = u'''GAME_DATA = r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\RimWorld\\Data"
GAME_MANAGED = r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\RimWorld\\RimWorldWin64_Data\\Managed"'''

OLD_BODY = u'''    for value in sorted(referenced):
        if not value.startswith("RimroomsAsyncIndustries"):
            continue                      # Core and DLC types; not ours to verify from source.
        simple = value.split(".")[-1]
        if simple not in declared_types:
            fail(problems, "a def names %s, which no C# source file declares" % value)'''

NEW_BODY = u'''    game_types = index_game_type_names()
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
        if simple not in game_types:
            fail(problems, "a def names %s, and no type of that name exists in the installed "
                           "game's assemblies. A Class the game cannot resolve discards the "
                           "entire def being parsed, not just that one node" % value)'''

OLD_INDEX = u'''def index_game_defs():'''

NEW_INDEX = u'''def strings_heap(path):
    """Every name in one managed assembly's CLI metadata `#Strings` heap.

    Read straight from the PE: section table -> CLI header -> metadata root -> stream headers.
    No reflection and no DLL load, so it works off any copy of the game on any platform and
    cannot execute anything it reads.

    The heap holds every metadata name -- types, fields, methods, parameters -- so membership
    proves a name EXISTS somewhere in the assembly rather than proving it is a type. That makes
    this an over-approximation: it can let an unusual mis-spelling through, and it can never
    reject a name that really is a type. Deliberate, because the alternative on offer was
    checking nothing at all.
    """
    try:
        data = io.open(path, "rb").read()
    except IOError:
        return None
    try:
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\\0\\0":
            return None
        coff = pe + 4
        section_count = struct.unpack_from("<H", data, coff + 2)[0]
        optional_size = struct.unpack_from("<H", data, coff + 16)[0]
        optional = coff + 20
        magic = struct.unpack_from("<H", data, optional)[0]
        directories = optional + (96 if magic == 0x10B else 112)
        cli_rva = struct.unpack_from("<I", data, directories + 14 * 8)[0]

        sections = []
        table = optional + optional_size
        for index in range(section_count):
            base = table + index * 40
            virtual_size, virtual_address, _, raw = struct.unpack_from("<IIII", data, base + 8)
            sections.append((virtual_address, max(virtual_size, 1), raw))

        def file_offset(rva):
            for virtual_address, virtual_size, raw in sections:
                if virtual_address <= rva < virtual_address + virtual_size:
                    return raw + (rva - virtual_address)
            return None

        cli = file_offset(cli_rva)
        if cli is None:
            return None
        metadata = file_offset(struct.unpack_from("<I", data, cli + 8)[0])
        if metadata is None or data[metadata:metadata + 4] != b"BSJB":
            return None
        version_length = struct.unpack_from("<I", data, metadata + 12)[0]
        cursor = metadata + 16 + version_length + ((-version_length) % 4) + 2
        stream_count = struct.unpack_from("<H", data, cursor)[0]
        cursor += 2
        for index in range(stream_count):
            offset, size = struct.unpack_from("<II", data, cursor)
            cursor += 8
            end = data.index(b"\\0", cursor)
            name = data[cursor:end].decode("ascii", "replace")
            cursor = end + 1
            cursor += (-(cursor - metadata)) % 4
            if name == "#Strings":
                blob = data[metadata + offset:metadata + offset + size]
                return set(part.decode("utf-8", "replace") for part in blob.split(b"\\0") if part)
    except (struct.error, ValueError, IndexError):
        return None
    return None


def index_game_type_names():
    """Type names the installed game can resolve: Core plus every installed DLC.

    DLC code lives in `Data/<Dlc>/Assemblies`, so a def naming an Anomaly or Odyssey type
    resolves here exactly as the game resolves it -- and if the DLC is absent, so is the name,
    which is the honest answer rather than a pass.
    """
    paths = []
    for name in ("Assembly-CSharp.dll", "Assembly-CSharp-firstpass.dll"):
        paths.append(os.path.join(GAME_MANAGED, name))
    paths += sorted(glob.glob(os.path.join(GAME_DATA, "*", "Assemblies", "*.dll")))

    names = set()
    for path in paths:
        found = strings_heap(path)
        if found:
            names |= found
    return names or None


def index_game_defs():'''

OLD_CALL = u"    check_class_references(problems)"
NEW_CALL = u"    check_class_references(problems, notes)"

OLD_SIG = u"def check_class_references(problems):"
NEW_SIG = u"def check_class_references(problems, notes):"

OLD_IMPORT = u"""import os
import re
import sys"""
NEW_IMPORT = u"""import os
import re
import struct
import sys"""

OLD_PRINT = u'    print("  game defs indexed:  %s" % ("%d" % len(game_defs) if game_defs else "skipped"))'
NEW_PRINT = u'''    print("  game defs indexed:  %s" % ("%d" % len(game_defs) if game_defs else "skipped"))
    _type_names = index_game_type_names()
    print("  game type names:    %s" % ("%d" % len(_type_names) if _type_names else "skipped"))'''

EDITS = [(OLD_IMPORT, NEW_IMPORT), (OLD_CONST, NEW_CONST), (OLD_INDEX, NEW_INDEX),
         (OLD_SIG, NEW_SIG), (OLD_BODY, NEW_BODY), (OLD_CALL, NEW_CALL), (OLD_PRINT, NEW_PRINT)]

text = io.open(CHECK, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(CHECK, "w", encoding="utf-8", newline="").write(text)
print("class-resolution hole closed: %d edits" % len(EDITS))
