# -*- coding: utf-8 -*-
"""Two corrections to the class-resolution check, both found by running it.

1. THE CHECK I JUST WROTE WOULD HAVE FAILED CORRECT CODE, which is worse than the hole it
   closed. The CLI metadata `#Strings` heap permits **suffix sharing**: a name may be stored
   only as the tail of a longer one, referenced by pointing partway into it. `Building` is
   exactly that -- it is a real type, and splitting the heap on NUL does not find it, so
   `<thingClass>Building</thingClass>` failed. Membership is now a search for `name + NUL`
   anywhere in the heap, which finds whole entries and shared suffixes alike and therefore
   cannot reject a name that really is there. `CompProperties_Colorable` is still absent.

2. **The comment I wrote to explain the fix contained `--`, and `check-package-integrity.py`
   refused the package for it** -- the same rule that caught this at 0.12.53-dev, catching the
   author of the rule. An em-dash in its place.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECK = os.path.join(REPO, "tools", "check-package-integrity.py")
PATCH = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Patches",
                     "RR_NativeGateProviders.xml")

# --------------------------------------------------------------------------- #
# 1. The heap read becomes suffix-aware.
# --------------------------------------------------------------------------- #

OLD_DOC = u'''    The heap holds every metadata name -- types, fields, methods, parameters -- so membership
    proves a name EXISTS somewhere in the assembly rather than proving it is a type. That makes
    this an over-approximation: it can let an unusual mis-spelling through, and it can never
    reject a name that really is a type. Deliberate, because the alternative on offer was
    checking nothing at all.
    """'''

NEW_DOC = u'''    Returned as the raw blob rather than a set of entries, because the heap permits SUFFIX
    SHARING: a name may be stored only as the tail of a longer one and referenced by pointing
    partway into it. `Building` is exactly that, so splitting on NUL finds every obvious name
    and silently misses real types -- the first draft of this check failed
    `<thingClass>Building</thingClass>`, which is correct code. Membership is therefore a
    search for `name + NUL`, which finds whole entries and shared suffixes alike.

    The heap holds every metadata name -- types, fields, methods, parameters -- so a hit proves
    a name EXISTS somewhere in the assembly rather than proving it is a type. That makes this an
    over-approximation: it can let an unusual mis-spelling through, and it can never reject a
    name that really is there. Deliberate in that direction, because a check that rejects
    correct code gets deleted and a check that is merely generous keeps catching this.
    """'''

OLD_RETURN = u'''            if name == "#Strings":
                blob = data[metadata + offset:metadata + offset + size]
                return set(part.decode("utf-8", "replace") for part in blob.split(b"\\0") if part)'''

NEW_RETURN = u'''            if name == "#Strings":
                return data[metadata + offset:metadata + offset + size]'''

OLD_INDEX_DOC = u'''    DLC code lives in `Data/<Dlc>/Assemblies`, so a def naming an Anomaly or Odyssey type
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
    return names or None'''

NEW_INDEX_DOC = u'''    DLC code lives in `Data/<Dlc>/Assemblies`, so a def naming an Anomaly or Odyssey type
    resolves here exactly as the game resolves it -- and if the DLC is absent, so is the name,
    which is the honest answer rather than a pass.

    Returns the concatenated `#Strings` heaps. Ask it a question with `type_name_exists`.
    """
    paths = []
    for name in ("Assembly-CSharp.dll", "Assembly-CSharp-firstpass.dll"):
        paths.append(os.path.join(GAME_MANAGED, name))
    paths += sorted(glob.glob(os.path.join(GAME_DATA, "*", "Assemblies", "*.dll")))

    blobs = []
    for path in paths:
        found = strings_heap(path)
        if found:
            blobs.append(found)
    return b"\\0".join(blobs) or None


def type_name_exists(heaps, simple):
    """Whether the installed game holds a metadata name equal to `simple`.

    `name + NUL` rather than equality against split entries, so a suffix-shared name such as
    `Building` resolves. See `strings_heap` for why that matters.
    """
    try:
        needle = simple.encode("utf-8") + b"\\0"
    except UnicodeEncodeError:
        return False
    return needle in heaps'''

OLD_USE = u'''        if game_types is None:
            continue
        if simple not in game_types:'''

NEW_USE = u'''        if game_types is None:
            continue
        if not type_name_exists(game_types, simple):'''

OLD_COUNT = u'''    _type_names = index_game_type_names()
    print("  game type names:    %s" % ("%d" % len(_type_names) if _type_names else "skipped"))'''

NEW_COUNT = u'''    _heaps = index_game_type_names()
    print("  game name heap:     %s" % ("%d bytes" % len(_heaps) if _heaps else "skipped"))'''

EDITS = [(OLD_DOC, NEW_DOC), (OLD_RETURN, NEW_RETURN), (OLD_INDEX_DOC, NEW_INDEX_DOC),
         (OLD_USE, NEW_USE), (OLD_COUNT, NEW_COUNT)]

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
print("heap membership is suffix-aware now")

# --------------------------------------------------------------------------- #
# 2. The comment that broke its own rule.
# --------------------------------------------------------------------------- #

OLD_COMMENT = u"""          <!-- NO `Class` ATTRIBUTE, AND THIS COST THE SEVENTH LAUNCH. There is no
               `CompProperties_Colorable` type in the game; `CompColorable` is declared with a
               plain `CompProperties` carrying a `compClass`, exactly as Core does it for
               apparel, textiles and the Ideology floor coverings. Naming a type that does not
               exist throws out of `DirectXmlToObjectNew`, and that does not fail one comp --
               it discards the WHOLE ThingDef being parsed, so `Door` and `Autodoor` vanished
               from the game and every def that referenced them failed to cross-resolve. -->"""

NEW_COMMENT = u"""          <!-- NO `Class` ATTRIBUTE, AND THIS COST THE SEVENTH LAUNCH. There is no
               `CompProperties_Colorable` type in the game; `CompColorable` is declared with a
               plain `CompProperties` carrying a `compClass`, exactly as Core does it for
               apparel, textiles and the Ideology floor coverings — the last of which are
               buildings, so it is the right mechanism for a door, it was only spelled with a
               class that does not exist. Naming a type the game cannot resolve throws out of
               `DirectXmlToObjectNew`, and that does not fail the one comp: it discards the
               WHOLE ThingDef being parsed. `Door` and `Autodoor` left the game, every def
               referencing them failed to cross-resolve, and the log went red from the top. -->"""

patch = io.open(PATCH, encoding="utf-8").read()
if patch.count(OLD_COMMENT) != 1:
    print("PATCH ANCHOR PROBLEM: %d" % patch.count(OLD_COMMENT))
    raise SystemExit(1)
io.open(PATCH, "w", encoding="utf-8", newline="").write(patch.replace(OLD_COMMENT, NEW_COMMENT, 1))
print("comment no longer contains the token its own checker refuses")
