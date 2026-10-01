"""Refuse to ship a def that references DLC-only content without a MayRequire gate.

Why this exists
---------------
On 2026-09-29 the two childcare work giver defs were found referencing
``<workType>Childcare</workType>`` with no gate. `Childcare` is a Biotech
`WorkTypeDef`, so on an install without Biotech that is an **unresolved cross-reference
at load** -- a red error, and the kind nothing in the package was watching for.
The C# side had always degraded correctly through `GetNamedSilentFail`; only the XML
had been forgotten, and nothing was checking it.

**This rule survives the 2026-10-01 dependency change, and matters more because of it.**
`About.xml` now declares 294 hard dependencies, the five expansions among them, after the
owner's direction *"the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT AND MAKE SURE ITS
LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*. So the old justification -- *a mod
whose entire claim is that it needs nothing but Core* -- is **no longer true and has been
removed rather than left standing**. What replaces it is the owner's own answer on posture:
declare the dependency so a manager enforces it, **and keep the graceful guard anyway**, so
a player who ignores the warning degrades instead of crashing. `MayRequire` is that guard in
XML exactly as `GetNamedSilentFail` is in C#, and a gate is now a deliberate second line
rather than the only line.

The existing compliance check looks for DLC *package ids* appearing ungated. It could
never have caught this, because the def never mentions Biotech at all -- it mentions
`Childcare`, and knowing that `Childcare` belongs to Biotech requires reading the
game's own data. That blind spot is the reason this script reads the installed
`Data/` folders rather than a hand-written list of names.

What it does
------------
1. Indexes every `defName` shipped in `RimWorld/Data/*/Defs/**` and records which
   folder defines it. Anything defined outside `Core` is DLC-only.
2. Walks every packaged XML file in the mod and, for each element whose **text** is a
   known DLC-only defName, checks that the def it sits inside carries a `MayRequire`
   naming that DLC's package id.
3. Fails on anything ungated.

False positives are handled by `IGNORED_TAGS`: a keyed language string whose English
text happens to collide with a defName is not a def reference. `Researcher` is the
live example -- the word inside `<RR_Role_research>` collides with an Anomaly def.

Usage
-----
    python tools/check-dlc-gating.py
"""

import glob
import os
import sys
import xml.etree.ElementTree as ElementTree

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

PACKAGE_IDS = {
    "Royalty": "Ludeon.RimWorld.Royalty",
    "Ideology": "Ludeon.RimWorld.Ideology",
    "Biotech": "Ludeon.RimWorld.Biotech",
    "Anomaly": "Ludeon.RimWorld.Anomaly",
    "Odyssey": "Ludeon.RimWorld.Odyssey",
}

# Element names whose text is prose, not a def reference. A keyed string that happens
# to read like a defName is not a cross-reference and must not be gated.
IGNORED_TAGS = {"label", "description", "verb", "gerund", "jobString", "reportString",
                "labelShort", "title", "titleShort", "text", "letterLabel", "letterText"}


def index_game_defs():
    """defName -> the set of Data folders that define it."""
    owner = {}
    for path in glob.glob(os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml"), recursive=True):
        folder = os.path.relpath(path, GAME_DATA).split(os.sep)[0]
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError:
            continue
        for node in root:
            name = node.findtext("defName")
            if name:
                owner.setdefault(name, set()).add(folder)
    return owner


def main():
    if not os.path.isdir(GAME_DATA):
        sys.stderr.write("dlc-gating: game Data folder not found; check skipped, not passed\n")
        return 2

    owner = index_game_defs()
    dlc_only = {name: sorted(folders) for name, folders in owner.items() if "Core" not in folders}
    if not dlc_only:
        sys.stderr.write("dlc-gating: indexed no DLC-only defs; refusing to report a pass\n")
        return 2

    failures = []
    checked = 0
    gated = []
    for path in sorted(glob.glob(os.path.join(MOD, "**", "*.xml"), recursive=True)):
        relative = os.path.relpath(path, REPO).replace("\\", "/")
        # Language files are prose by definition.
        if "/Languages/" in relative:
            continue
        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as error:
            failures.append("%s does not parse: %s" % (relative, error))
            continue
        for definition in root:
            may_require = definition.get("MayRequire") or ""
            required = {part.strip() for part in may_require.split(",") if part.strip()}
            def_name = definition.findtext("defName") or definition.tag
            for node in definition.iter():
                if node.tag in IGNORED_TAGS:
                    continue
                value = (node.text or "").strip()
                if value not in dlc_only:
                    continue
                checked += 1
                wanted = {PACKAGE_IDS[folder] for folder in dlc_only[value]
                          if folder in PACKAGE_IDS}
                if not wanted:
                    continue
                if required & wanted:
                    gated.append("%s <%s>%s</%s> gated by %s"
                                 % (def_name, node.tag, value, node.tag, may_require))
                else:
                    failures.append(
                        "%s: <%s>%s</%s> is defined by %s but the def carries "
                        "MayRequire=%r. Without that expansion this is an unresolved "
                        "cross-reference at load."
                        % (relative, node.tag, value, node.tag,
                           "/".join(dlc_only[value]), may_require or "(none)"))

    if failures:
        for failure in failures:
            sys.stderr.write("dlc-gating: %s\n" % failure)
        return 1

    print("DLC gating verified")
    print("  DLC-only defs known : %d" % len(dlc_only))
    print("  references found    : %d, all gated" % checked)
    for line in gated:
        print("    %s" % line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
