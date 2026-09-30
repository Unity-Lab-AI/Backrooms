# -*- coding: utf-8 -*-
"""Assert the field recorder's job is the record book's, the def still loads, and nothing grants it.

The property this exists for
---------------------------
`RR_FieldRecorder` was the last genuinely buyable, carryable gameplay `ThingDef` this mod authored,
and therefore the last standing breach of invariant 10. Its art went at 0.12.22-dev. The owner's
decision, asked and answered in the turn it was found, was to **fold its job into the record book a
crew already carries** rather than build a replacement:

    "Fold it into the record book crews already carry"

That is the same answer the 0.9.9-dev plan wrote down and never executed:

    "**Field recorder** | **the book** | One Core `TextBook`: carried in blank, written in the
     field, carried home as the evidence. The recorder and the record stop being two things that
     can get separated."

Four things have to stay true, and no compiler and no checker will say so:

  * **NO SAVE BREAK.** The def stays loadable. Saves made before the switch contain recorders in
    crew inventories and on the floors of coordinates, and the owner's own rule is a *"migration
    decision or declared development-save break before removing any Def a saved Thing references"*.
    So the retirement is achieved entirely by taking away every way to *get* one, and
    `FailedSiteRecovery` deliberately keeps naming it.

  * **IT IS NEVER GRANTED OR SOLD AGAIN.** No recipe, no scenario grant, no catalogue entry, and
    `tradeability` is `None`. This is the half a reader cannot verify, because the absence of a
    grant looks exactly like a grant nobody thought of.

  * **THE KIT IS RESOLVED, NOT NAMED.** `CompRouteEvidence.NativeCarrierDef` is strict: Core's own
    book, a `Book` subclass, carrying our comp exactly once, with `CompBook` and `CompQuality`. A
    def-name string would happily match another mod's `TextBook`. And because that property can
    return null, **every caller must refuse visibly on null** -- a silent null would make the kit
    check pass for a crew carrying nothing, which is precisely how `Named<TerrainDef>("Carpet")`
    left the depth-1 yellow rooms in wood plank flooring for months.

  * **A LOST BOOK IS NOT A DEAD END.** Core gives books `Flammability 1` and `DeteriorationRate 5`,
    and sells `TextBook` only as random outlander stock. Without a company supply route a burnt book
    would refuse every future dispatch for ever.

Run from the repository root.
"""
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    """Comments must never satisfy a claim nor break one.

    This change is documented at length in the very files it changes, and those comments name
    `RR_FieldRecorder` repeatedly while explaining why nothing reads it. A naive search would be
    fooled in both directions. Invariant 130 exists because that has already happened here.
    """
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def body_of(text, signature):
    """The braced body of one member, so a claim is keyed to the member that must hold it."""
    start = text.index(signature)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError("unbalanced body for %r" % signature)


cargo = strip_cs_comments(read(os.path.join(SRC, "Expedition", "ExpeditionCargo.cs")))
site = strip_cs_comments(read(os.path.join(SRC, "Threats", "FirstSliceSiteComponent.cs")))
observations = strip_cs_comments(read(os.path.join(SRC, "Company", "EvidenceObservations.cs")))
comp = strip_cs_comments(read(os.path.join(SRC, "Investigation", "CompRouteEvidence.cs")))
recovery = strip_cs_comments(read(os.path.join(SRC, "Generation", "FailedSiteRecovery.cs")))

items_xml = read(os.path.join(MOD, "Defs", "ThingDefs_Items", "RR_FieldEquipment.xml"))
scenarios_xml = read(os.path.join(MOD, "Defs", "ScenarioDefs", "RR_Scenarios.xml"))
catalogue_xml = read(os.path.join(MOD, "Defs", "RimroomsProcurementCatalogDefs", "RR_ProcurementCatalog.xml"))
keyed_xml = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_Expedition.xml"))

print("")
print("proof: the record book is the recorder, the def survives, and nothing hands one out")
print("")

# ------------------------------------------------------------------ 1. no save break
print("1. the def still loads, because saves reference it")
check("RR_FieldRecorder is still declared",
      "<defName>RR_FieldRecorder</defName>" in items_xml,
      "-- removing a def a saved Thing references needs a migration decision or a declared break")
check("FailedSiteRecovery still names it, deliberately",
      '"RR_FieldRecorder"' in recovery,
      "-- recovery has to tolerate recorders lying on the floors of coordinates in old saves")
check("the legacy route recording is still a supported carrier",
      'defName == "RR_RouteRecording"' in comp,
      "-- the same reasoning: a crew in an old save is holding one and has not stopped recording")

# ------------------------------------------------------------------ 2. never granted or sold
print("")
print("2. there is no way left to obtain one")
recorder_def = items_xml[items_xml.index("<defName>RR_FieldRecorder</defName>"):]
recorder_def = recorder_def[:recorder_def.index("</ThingDef>")]
check("the recorder's tradeability is None",
      "<tradeability>None</tradeability>" in recorder_def,
      "-- its base is ResourceBase with tradeability Buyable, so this override is the whole of it")

recipe_hits = []
recipe_dir = os.path.join(MOD, "Defs", "RecipeDefs")
for name in sorted(os.listdir(recipe_dir)):
    if strip_xml_comments(read(os.path.join(recipe_dir, name))).find("RR_FieldRecorder") >= 0:
        recipe_hits.append(name)
check("no recipe produces a recorder", not recipe_hits, "-- found in %s" % recipe_hits)
check("the retired recipe file is gone from disk",
      not os.path.exists(os.path.join(recipe_dir, "RR_FieldEquipmentRecipes.xml")))
allowlist = json.loads(read(os.path.join(REPO, "tools", "package-files.json")).lstrip(u"﻿"))
check("the package allowlist no longer names it",
      "RR_FieldEquipmentRecipes" not in json.dumps(allowlist),
      "-- an allowlisted file that is not there fails integrity, which is how this gets caught")

check("no scenario grants a recorder",
      "RR_FieldRecorder" not in strip_xml_comments(scenarios_xml),
      "-- two starts granted one; both now grant a textbook")
check("the procurement catalogue does not carry a recorder",
      "RR_FieldRecorder" not in strip_xml_comments(catalogue_xml))

# ------------------------------------------------------------------ 3. resolved, not named
print("")
print("3. the kit is resolved through the strict predicate, and refuses on null")
check("the kit def comes from CompRouteEvidence.NativeCarrierDef",
      "CompRouteEvidence.NativeCarrierDef" in body_of(cargo, "internal static ThingDef RecordBookDef"),
      "-- a def-name string would match another mod's TextBook just as happily")
check("no def-name kit array survives",
      "KitDefs" not in cargo and "KitCounts" not in cargo,
      "-- two parallel arrays that could disagree about their own length")

kit = body_of(cargo, "public static CompanyActionResult CheckKit(")
check("CheckKit refuses when the book cannot be resolved",
      "if (book == null)" in kit and "RR_Exp_MissingRecordBook" in kit,
      "-- a silent null makes the kit check pass for a crew carrying nothing")
loadout = body_of(cargo, "public static CompanyActionResult QueueLoadout(")
check("QueueLoadout refuses on the same null",
      "if (def == null)" in loadout and "RR_Exp_MissingRecordBook" in loadout)
check("the loadout takes mass from the item, never from a constant",
      "GetStatValue(StatDefOf.Mass)" in loadout,
      "-- the register's cargo family asks to preserve each mod's normal weight behaviour")

check("NativeCarrierDef still requires Core provenance",
      "IsCoreMod" in body_of(comp, "public static ThingDef NativeCarrierDef"),
      "-- without it, any mod's TextBook passes as company gear")
check("NativeCarrierDef still requires exactly one of our comps",
      "OfType<CompProperties_RouteEvidence>().Count() == 1" in body_of(comp, "public static ThingDef NativeCarrierDef"),
      "-- two comps on one book is a double-patch, and a book with none cannot hold a record")

# ------------------------------------------------------------------ 4. one rule, both gates
print("")
print("4. surveying and recording now ask the same question")
check("the site tick asks whether a crew member carries the record book",
      "present.Any(CarriesRecordBook)" in site,
      "-- it used to name the recorder def as a string")
check("CarriesRecordBook delegates to the strict carrier predicate",
      "CompRouteEvidence.IsSupportedCarrier" in body_of(site, "internal static bool CarriesRecordBook("))
check("the old name-matching inventory helper is gone",
      "internal static bool HasItem(" not in site,
      "-- its only caller was the recorder check")

book = body_of(observations, "private static bool TryFindRecordBook(")
check("the observation is attributed to the bound record itself",
      "book = record.item;" in book,
      "-- the record and the thing recording it stop being two objects that can get separated")
check("the book must be in a crew member's inventory",
      "innerContainer.Contains(record.item)" in book,
      "-- a book on the floor two rooms back is not being written in")
check("the carrier must be a living, spawned member of this run",
      "member.Dead" in book and "member.Spawned" in book and "member.Map != map" in book)
check("EvidenceObservations no longer resolves the recorder def",
      '"RR_FieldRecorder"' not in observations,
      "-- this was the last live read of it outside recovery tolerance")

# ------------------------------------------------------------------ 5. a lost book is recoverable
print("")
print("5. losing the book is a setback, not a dead end")
check("both starts grant a textbook",
      strip_xml_comments(scenarios_xml).count("<thingDef>TextBook</thingDef>") == 2,
      "-- the headquarters start and the already-inside start")
catalogue = strip_xml_comments(catalogue_xml)
check("the company catalogue sells record books",
      "RR_Procurement_RecordBooks" in catalogue and "<thingDefName>TextBook</thingDefName>" in catalogue,
      "-- Core sells TextBook only as random outlander stock, and books burn at flammability 1")

# ------------------------------------------------------------------ 6. the player is told
print("")
print("6. the refusal reaches the player in the mod's own words")
check("the reworded refusal exists",
      "<RR_Exp_MissingRecordBook>" in keyed_xml)
check("the old key is gone rather than left dangling",
      "RR_Exp_Missing_RR_FieldRecorder" not in keyed_xml,
      "-- a key nothing translates is a key that prints its own name at the player")
check("the refusal is a literal key in C#, not one built at run time",
      '"RR_Exp_MissingRecordBook"' in cargo and '"RR_Exp_Missing_" +' not in cargo,
      "-- a runtime-built key cannot be checked, and this is the fourth one found in this repo")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the book is the recorder, the def still loads, and nothing hands one out")
