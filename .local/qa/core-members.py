#!/usr/bin/env python3
"""List the members of named Core types, and the user strings that mention a word, from Assembly-CSharp.

The installed game ships only part of its source under `Rimworld/Source`, and there is no
decompiler on this machine. The metadata tables are enough to answer *what does Core call this*
and *which type owns that field*, which is what a Core-API-only mod needs before it touches a
surface it has never used.

Usage:
    python .local/qa/core-members.py UI_BackgroundMain LongEventHandler UIMenuBackgroundManager
    python .local/qa/core-members.py --strings Loading
"""
import sys

import dnfile

ASSEMBLY = r"C:\Program Files (x86)\Steam\steamapps\common\Rimworld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll"


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    pe = dnfile.dnPE(ASSEMBLY)
    md = pe.net.mdtables
    if argv[0] == "--strings":
        needle = argv[1].lower()
        for s in pe.net.user_strings.get_all() if hasattr(pe.net.user_strings, "get_all") else []:
            text = str(s)
            if needle in text.lower():
                print(repr(text)[:160])
        return 0

    wanted = set(argv)
    typedefs = md.TypeDef.rows
    for index, row in enumerate(typedefs):
        name = str(row.TypeName)
        if name not in wanted:
            continue
        print("=" * 70)
        print("%s.%s : %s" % (row.TypeNamespace, name,
                               row.Extends.row.TypeName if row.Extends and row.Extends.row else "?"))
        # dnfile resolves a type's field and method runs into lists of rows already.
        for f in row.FieldList or []:
            print("  field  %s" % f.row.Name)
        for m in row.MethodList or []:
            name = str(m.row.Name)
            if name in (".ctor", ".cctor"):
                continue
            print("  method %s" % name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
