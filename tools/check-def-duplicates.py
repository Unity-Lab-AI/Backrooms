# -*- coding: utf-8 -*-
"""Refuse two defs of the same type sharing a defName, and refuse silently overriding the game.

Why this exists
---------------
**IT WAS WRITTEN AFTER THE DEFECT IT CATCHES WAS ALREADY COMMITTED AND PUSHED.** On 2026-10-06 the
company journal was authored as `RR_RouteRecording` in a new file, while `RR_FieldEquipment.xml`
had declared a ThingDef of that exact name since 0.2.0 -- the found-evidence item, kept loadable so
old saves open. Two ThingDefs, one defName, in one package. RimWorld resolves that by one winning
and the other vanishing, and **which one wins is not something a reader can tell by looking**.

Nothing in a thirty-checker battery noticed. `check-def-references.py` resolves names outward and
is blind to a name declared twice; the build only validates that each file is well-formed XML.

Two rules, and the second is the one that matters on a 296-mod profile:

  1. **No two defs of the same type share a defName inside this package.** Type matters: a JobDef
     and a WorkGiverDef called `RR_WriteUp` are two different defs and perfectly legal, and this
     package has four such pairs on purpose. Comparing names alone would report all four and train
     whoever reads it to ignore the check.

  2. **No def of ours silently overrides a def the game ships.** Declaring `<ThingDef><defName>Shelf`
     does not fail, error or warn -- it REPLACES Core's shelf for every mod in the load order. That
     is the single most antisocial thing a mod can do by accident, and it is invisible without the
     game on disk.

Run from the repository root. Exits non-zero on a duplicate or an override.
"""
import os
import sys
import xml.etree.ElementTree as ElementTree

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs")

GAME_ROOTS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data",
    r"C:\Program Files\Steam\steamapps\common\RimWorld\Data",
    os.path.join(os.path.expanduser("~"), "RimWorld", "Data"),
]

problems = []
notes = []


def declared(root_folder):
    """Every (def type, defName) the XML under this folder declares, with where it was declared."""
    found = {}
    for folder, _subdirs, files in os.walk(root_folder):
        for name in sorted(files):
            if not name.lower().endswith(".xml"):
                continue
            path = os.path.join(folder, name)
            try:
                tree = ElementTree.parse(path)
            except ElementTree.ParseError:
                # The build already refuses malformed XML; reporting it twice is noise.
                continue
            root = tree.getroot()
            if root.tag != "Defs":
                continue
            for child in root:
                if not isinstance(child.tag, str):
                    continue            # a comment node
                name_element = child.find("defName")
                if name_element is None or not (name_element.text or "").strip():
                    continue            # an abstract def, which carries Name= instead
                key = (child.tag, name_element.text.strip())
                found.setdefault(key, []).append(
                    os.path.relpath(path, root_folder).replace(os.sep, "/"))
    return found


def game_data_root():
    for candidate in GAME_ROOTS:
        if os.path.isdir(candidate):
            return candidate
    return None


def main():
    ours = declared(DEFS)
    notes.append("%d def(s) declared by this package" % len(ours))

    # ---------------------------------------------------------------- 1. no duplicate of our own
    duplicates = {key: where for key, where in ours.items() if len(where) > 1}
    if duplicates:
        for (def_type, name), where in sorted(duplicates.items()):
            problems.append("%s %r is declared %d times, in %s. One wins and the other vanishes, "
                            "and which one is not something a reader can tell by looking."
                            % (def_type, name, len(where), " and ".join(sorted(set(where)))))
    else:
        notes.append("no def type declares the same defName twice")

    shared_names = {}
    for def_type, name in ours:
        shared_names.setdefault(name, []).append(def_type)
    legal_pairs = sorted((n, t) for n, t in shared_names.items() if len(t) > 1)
    if legal_pairs:
        notes.append("%d defName(s) shared across DIFFERENT def types, which is legal: %s"
                     % (len(legal_pairs),
                        ", ".join("%s (%s)" % (n, "+".join(sorted(t))) for n, t in legal_pairs[:6])))

    # ---------------------------------------------------------- 2. no silent override of the game
    root = game_data_root()
    if root is None:
        problems.append("no RimWorld Data folder was found, so the override rule could not run. "
                        "A check that cannot look has not passed.")
    else:
        game = {}
        packs = []
        for pack in sorted(os.listdir(root)):
            folder = os.path.join(root, pack, "Defs")
            if not os.path.isdir(folder):
                continue
            packs.append(pack)
            for key in declared(folder):
                game.setdefault(key, pack)
        notes.append("%d def(s) parsed from %s" % (len(game), ", ".join(packs)))

        overrides = sorted(key for key in ours if key in game)
        if overrides:
            for def_type, name in overrides:
                problems.append("%s %r is declared by this package AND by %s. Declaring a def the "
                                "game already ships REPLACES it for every mod in the load order, "
                                "silently. Rename ours, or patch theirs inside a "
                                "PatchOperationFindMod." % (def_type, name, game[(def_type, name)]))
        else:
            notes.append("no def of ours shares a type and name with anything the game ships")

    print("def duplicates")
    for note in notes:
        print("  note: %s" % note)

    if problems:
        print("")
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1

    print("")
    print("PASS: every def this package declares is declared once and overrides nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
