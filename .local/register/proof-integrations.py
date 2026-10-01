# -*- coding: utf-8 -*-
"""Rows 764, 765, 766, 784, 791: what optional mods are loaded, said in the game, and nothing
patched.

The register forbids patching all four of the mods these rows name, in its own words -- *"no patch
or code/assets copied"* for both gravship chapters, *"do not add vehicles solely because the
framework is installed"* for the vehicle framework, *"do not assume custom dossier or gear
transfers"* for RimWorld Together. So a hook here is a **read-only statement of what is installed
and what this package does about it**, which is also what the rows ask for in their own words:
*"logistics summary/operations links"* and *"feature detection and setup diagnostics"*.

The absolutes in these rows are the point of this file:

  * **no Rimrooms route, gate or expedition may require any of them** (764, 765, 766)
  * **orbital enemies must never mix into Backrooms entity generation** (766)
  * **no statement may describe live shared-colony control or synchronised research** (791)

Run from the repository root.
"""
import csv
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed")
INVENTORY = os.path.join(REPO, "docs", "research", "rimworld-server-mod-inventory.csv")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


integrations = strip_cs_comments(read(os.path.join(SRC, "Core", "InstalledIntegrations.cs")))
integrations_raw = read(os.path.join(SRC, "Core", "InstalledIntegrations.cs"))
pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsFacilities.cs")))
inhabitants = strip_cs_comments(read(os.path.join(SRC, "Threats", "InhabitantService.cs")))
company_keys = read(os.path.join(KEYED, "RR_Company.xml"))
multiplayer = read(os.path.join(REPO, "docs", "MULTIPLAYER.md"))
# Whitespace-normalised, because a hard-wrapped document splits a phrase across a newline and a
# literal search then finds nothing. A first version of this proof reported the document as
# missing "no synchronised research" while the sentence was right there, wrapped -- the search
# was the defect, not the document, for the seventh time this session.
flat = re.sub(r"\s+", " ", multiplayer).lower()
conformance = read(os.path.join(REPO, "tools", "check-doc-conformance.py"))

print("")
print("detection: by package id, and every id is the register's own")
print("-" * 78)

check("detection uses Core's own answer",
      "ModsConfig.IsActive(state.PackageId)" in integrations,
      "-- not a mod name, not a def lookup, not a guess")
check("the installed list is re-read when it changes",
      "ModLister.InstalledModsListHash(true)" in integrations,
      "-- a player can enable a mod and restart into the same save, so a once-only read goes "
      "stale; asking every frame would be a string comparison per mod per frame")

# Every id in the code must be the id the register records for that row. A wrong id is a silent
# "not installed" forever, which is the defect class this project has been caught by five times.
rows = {r["LoadOrder"]: r for r in csv.DictReader(io.open(INVENTORY, encoding="utf-8-sig",
                                                          newline=""))}
declared = re.findall(r"RegisterRow = (\d+),\s*\n\s*PackageId = \"([^\"]+)\"", integrations)
check("five optional mods are tracked",
      len(declared) == 5,
      "-- measured %d" % len(declared))
for row, package in declared:
    record = rows.get(row)
    actual = (record or {}).get("WorkshopID") or (record or {}).get("PackageID") or ""
    check("row %s's package id matches the register (%s)" % (row, package),
          record is not None and package in (actual, (record or {}).get("ModID", "")),
          "-- register says %r for row %s; a wrong id is a silent 'not installed' forever"
          % (actual or (record or {}).get("ModID"), row))

print("")
print("NOTHING BEHAVES DIFFERENTLY BECAUSE A MOD IS INSTALLED")
print("-" * 78)

# The register's instruction is "do not add vehicles solely because the framework is installed".
# The only defence that cannot rot is that nothing except the readout ever asks.
readers = []
for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    if os.sep + "obj" + os.sep in path or os.sep + "bin" + os.sep in path:
        continue
    body = strip_cs_comments(read(path))
    if "InstalledIntegrations" in body:
        readers.append(os.path.basename(path))
check("only the readout and the class itself read the detection",
      sorted(readers) == ["InstalledIntegrations.cs", "OperationsFacilities.cs"],
      "-- measured %s. A detection layer that starts deciding things is exactly how 'do not "
      "add vehicles solely because the framework is installed' gets broken by accident"
      % sorted(readers))
check("the detection class issues no job, order, route or spawn",
      not re.search(r"JobMaker|CompanyActionResult|GenSpawn|Rand\.|SuccessRouteKind", integrations),
      "-- it answers one question and hands out nothing")
check("no gate, route or expedition file mentions a tracked package id",
      not any(package in read(path)
              for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)
              if os.path.basename(path) != "InstalledIntegrations.cs"
              and os.sep + "obj" + os.sep not in path and os.sep + "bin" + os.sep not in path
              for _, package in declared),
      "-- a package id outside the detection class is a dependency forming")

print("")
print("row 766's absolute: orbital enemies never mix into Backrooms generation")
print("-" * 78)

check("inhabitant selection draws ONLY from this mod's own def type",
      "DefDatabase<RimroomsInhabitantDef>" in inhabitants,
      "-- row 766: 'orbital enemies must never mix into Backrooms entity generation'")
check("and it names no other mod's content, faction or pawn kind source",
      not re.search(r"PawnGroupMaker|FactionDef|DefDatabase<PawnKindDef>\.AllDefs", inhabitants),
      "-- a group maker or a faction pawn source would let any installed content in")

print("")
print("row 791: the document, and a checker that refuses the claim")
print("-" * 78)

check("the document exists and denies a shared colony outright",
      "no shared colony" in flat and "no live shared map" in flat and
      "no synchronised research" in flat,
      "-- row 791's absolute, stated rather than implied")
check("it says nothing has been tested, and says it in the opening line",
      "nothing on this page has been tested in play" in flat and
      flat.index("has been tested in play") < 200,
      "-- the caveat belongs at the top, not in a footnote")
check("it does not claim support for anything",
      not re.search(r"\bis supported\b|\bfully supported\b|\bworks with\b", multiplayer, re.I),
      "-- no game has ever been launched from this repository")
check("it records that the server does NOT enforce mods",
      "AllowAllMods=true" in multiplayer and "by hand" in multiplayer,
      "-- the single most likely cause of trouble, and the server will not warn anybody")
check("it records the forced scenario and the disposable-copy advice",
      "Crashlanded" in multiplayer and "disposable copy" in multiplayer)
check("THE MULTIPLAYER PAGE A READER OPENS IS HELD TO THE READER-FACING RULES",
      'os.path.join(WIKI, "multiplayer.md")' in conformance
      and os.path.isfile(os.path.join(REPO, "docs", "wiki", "multiplayer.md")),
      "-- **re-aimed 2026-10-01.** The concise public page is `docs/wiki/multiplayer.md` and it "
      "is in the set; `MULTIPLAYER.md` keeps the server detail a player does not need and a "
      "maintainer does. Otherwise the vocabulary and wall rules skip the page people actually "
      "read")
check("THE CLAIM GUARD EXISTS and is wired into the reader-facing walk",
      "FORBIDDEN_CLAIMS" in conformance and
      "def check_forbidden_claims(" in conformance and
      "\n        check_forbidden_claims(rel, prose, problems)" in conformance,
      "-- row 791 is an absolute, and an absolute with no check is a promise")
check("the guard checks for negation rather than banning the words outright",
      "CLAIM_NEGATORS" in conformance,
      "-- a naive substring ban would fail the one document written to obey the rule, which is "
      "the trap disposition_stance() fell into")
check("and its negator list is documented as maintained rather than complete",
      "Maintained, not complete" in conformance,
      "-- a phrase list cannot anticipate every way English denies something, and the next "
      "person needs to know which way it fails")

for key in ("RR_Integration_Heading", "RR_Integration_Caveat", "RR_Integration_RowActive",
            "RR_Integration_RowAbsent", "RR_Integration_OpenWorld",
            "RR_Integration_VehicleFrameworkName", "RR_Integration_VehicleFrameworkPosition",
            "RR_Integration_RimWorldTogetherName", "RR_Integration_RimWorldTogetherPosition",
            "RR_Integration_GravshipOneName", "RR_Integration_GravshipOnePosition",
            "RR_Integration_VehiclesExpandedName", "RR_Integration_VehiclesExpandedPosition",
            "RR_Integration_GravshipTwoName", "RR_Integration_GravshipTwoPosition"):
    check("%s is translated" % key, "<%s>" % key in company_keys)

print("")
print("the readout the player actually sees")
print("-" * 78)

check("the pane draws the heading with the live count",
      'listing.Label("RR_Integration_Heading".Translate(' in pane and
      "Core.InstalledIntegrations.ActiveCount()" in pane,
      "-- a key present in the file is not a claim that anything is drawn")
check("the caveat is drawn every time, not only when something is loaded",
      'listing.Label("RR_Integration_Caveat".Translate());' in pane,
      "-- loaded means present, not proven, and that has to be said unconditionally")
# Unconditionally, which means the line stands alone in the loop body. Wrapping it in
# `if (state.Active)` leaves the inner text matching, so the indentation is part of the claim.
check("the position is drawn in BOTH states",
      "\n                listing.Label(state.PositionKey.Translate());" in pane and
      "RR_Integration_RowAbsent" in pane,
      "-- a player deciding whether to install one of these needs to know beforehand what this "
      "mod will do with it")
check("the operations link is the native tab, not a surface of ours",
      'OpenNativeTab(DefDatabase<MainButtonDef>.GetNamedSilentFail("World"))' in pane,
      "-- row 765 asks for 'operations links'; a button that opens the game's own surface is "
      "the whole of that, with nothing patched")
check("the section is reached from the facilities pane",
      "DrawIntegrations(listing);" in pane)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: what is installed is said in the game, nothing is patched, and nothing "
      "claims what has not been demonstrated")
