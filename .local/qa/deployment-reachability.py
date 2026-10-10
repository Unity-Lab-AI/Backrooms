# -*- coding: utf-8 -*-
"""Is every registered deployment provider actually reachable by a pawn?

The chain is three links long and each one is in a different file type:

    provider registered  ->  a WorkGiver subclass overrides ProviderId  ->  a WorkGiverDef
                                                                            names that class

`ConnectedDeploymentProviders.Get(id)` is the only consumer, and `All` is never enumerated -- so a
provider whose chain is broken anywhere is a thing nobody can ever do. This measures all three
links and prints what is missing.
"""
import io
import os
import re

NL = chr(10)
SRC = "src/RimroomsAsyncIndustries"
DEFS = "Mod/Rimrooms - Async Industries/1.6/Defs"


def read_all(root, suffix):
    out = {}
    for base, _, names in os.walk(root):
        for name in sorted(names):
            if name.endswith(suffix):
                path = os.path.join(base, name)
                out[path] = io.open(path, encoding="utf-8-sig").read()
    return out


def main():
    sources = read_all(SRC, ".cs")
    joined = NL.join(sources.values())

    # Link 0: the constants, with their string values.
    provider_file = [t for p, t in sources.items()
                     if p.endswith("ConnectedDeploymentProvider.cs")][0]
    constants = dict(re.findall(
        r'public const string (\w+)\s*=\s*"([^"]+)"', provider_file))

    # Link 0b: which constants the registry actually registers.
    registry = re.search(r"registry\s*=" + r"[^;]*?\{(.*?)\};", provider_file, re.S)
    registered = set(re.findall(r"\{\s*(\w+),", registry.group(1))) if registry else set()

    # Link 1: WorkGiver subclasses and the provider constant each one returns.
    givers = {}
    for match in re.finditer(
            r"class (WorkGiver_\w+)\s*:\s*WorkGiver_ConnectedDeployment(.*?)(?=class |\Z)",
            joined, re.S):
        name, body = match.group(1), match.group(2)
        used = re.search(r"ProviderId\s*\{\s*get\s*\{\s*return ConnectedDeploymentProviders\.(\w+)",
                         body)
        if used:
            givers.setdefault(used.group(1), []).append(name)

    # Link 2: WorkGiverDefs naming a class.
    defs = read_all(DEFS, ".xml")
    declared = set()
    for text in defs.values():
        # RimWorld's field is `giverClass`, not `workGiverClass`. The first version of this
        # script looked for the wrong tag, found zero, and reported all 27 providers unreachable
        # -- a tool that cannot see the feature is worse than no tool, and it nearly produced a
        # confident wrong answer about shipped work.
        declared.update(re.findall(r"<giverClass>\s*[\w.]*?(\w+)\s*<", text))

    print("provider constants           : %d" % len(constants))
    print("registered in the registry   : %d" % len(registered))
    print("have a WorkGiver subclass    : %d" % len(givers))
    print("WorkGiverDef classes declared: %d" % len(declared))
    print("")

    broken = []
    for constant in sorted(registered):
        subclasses = givers.get(constant, [])
        if not subclasses:
            broken.append((constant, constants.get(constant, "?"), "no WorkGiver subclass"))
            continue
        unreached = [s for s in subclasses if s not in declared]
        if len(unreached) == len(subclasses):
            broken.append((constant, constants.get(constant, "?"),
                           "subclass(es) %s in no WorkGiverDef" % ", ".join(subclasses)))

    if not broken:
        print("EVERY registered provider is reachable: subclass and def both present.")
        return
    print("UNREACHABLE -- registered and a pawn can never be asked to do it:")
    for constant, value, why in broken:
        print("  %-26s %-24s %s" % (constant, value, why))


if __name__ == "__main__":
    main()
