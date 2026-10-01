# -*- coding: utf-8 -*-
"""The setup page drew three lines and stopped, and Core did it silently on purpose.

Owner, verbatim: *"the review company start up screen when i press start game on prepare carfully
says: 'Those are in the supplies list below' but there are no lists or supplies on the card pop up
at all.. so what the fuck?"* and then *"that pop up should list all the equipemnet for the gate
that u get added to ur start on top of what u fill out in edb prepare carfully"*.

WHAT THE LIVE GAME SHOWED. A screenshot of the running page, brightened four times over, is
blank below the third line: no roster, no funding, no supplies, no facility, and only the first of
five gate prerequisites. **The log contains no exception at all** -- so nothing threw, and the
page's own `RR_Setup_DrawFault` reporting had nothing to report.

THE CAUSE IS `Verse.Listing`, AND IT IS DESIGNED TO BE SILENT:

    protected void NewColumnIfNeeded(float neededHeight)
    { if (!maxOneColumn && curY + neededHeight > listingRect.height) { NewColumn(); } }

    public void NewColumn() { curY = 0f; curX += ColumnWidth + 17f; }

`Begin` sets `ColumnWidth = listingRect.width` unless a custom width was set, so overflowing the
rect moves drawing a full width to the right -- outside the `Widgets.BeginGroup(rect)` that
`Begin` opened, which clips it. Everything past that point is painted off the edge.

**And it is self-reinforcing.** `CurHeight => curY`, which `NewColumn` just reset to zero, so
`contentHeight = listing.CurHeight + 20f` records the second column instead of the total. The
scroll content shrinks, the wrap comes sooner, and it settles at a few lines. That also explains
the missing scrollbar: by then the content really did fit.

WHY NO PROOF COULD HAVE CAUGHT THIS BY READING OUR SOURCE. Every line of our code was correct.
The defect was an unset Core default interacting with a height we compute from a value Core
resets. **It is the same family as the seventh launch**: a claim about what our text says, where
the truth lived in the game's own behaviour. So the claims below are about the Core contract --
`maxOneColumn` set wherever a listing is single-column, and deliberately NOT set where a real
second column is wanted.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
PAGE = os.path.join(SRC, "Scenario", "Page_RimroomsCompanySetup.cs")
COMPONENT = os.path.join(SRC, "Scenario", "RimroomsStartupComponent.cs")
SETTINGS = os.path.join(SRC, "Core", "RimroomsMod.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed", "RR_StartupSetup.xml")

failures = []


def check(claim, held, detail=""):
    print("  %s  %s%s" % ("HOLDS " if held else "FAILS!", claim,
                          "" if held else "\n          " + detail))
    if not held:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8").read()


print("")
print("A LISTING THAT OVERFLOWS DRAWS ITSELF OFF THE EDGE OF THE WORLD")
print("=" * 78)
print("")

# Every listing in the package, and whether it declares which it is. A new listing that sets
# neither must fail here rather than ship with a silent truncation nobody will see until a
# player's content happens to get long enough.
sources = []
for folder, _, names in os.walk(SRC):
    if os.sep + "obj" in folder or os.sep + "bin" in folder:
        continue
    for name in names:
        if name.endswith(".cs"):
            sources.append(os.path.join(folder, name))

total = 0
single = 0
multi = 0
undeclared = []
for path in sources:
    body = read(path)
    for match in re.finditer(r"(\w+)\s*=\s*new Listing_Standard\(\)", body):
        total += 1
        name = match.group(1)
        after = body[match.end():match.end() + 900]
        if re.search(r"\b%s\.maxOneColumn\s*=\s*true" % re.escape(name), after):
            single += 1
        elif re.search(r"\b%s\.ColumnWidth\s*=" % re.escape(name), after):
            multi += 1
        else:
            undeclared.append("%s:%s" % (os.path.basename(path), name))

print("     listings found: %d   single-column: %d   deliberately multi-column: %d"
      % (total, single, multi))

check("EVERY LISTING DECLARES WHETHER IT IS ONE COLUMN OR MORE",
      not undeclared,
      "-- undeclared: %s. A listing that sets neither gets Core's default, which wraps a full "
      "column-width to the right, outside the group it clips to, and loses everything after the "
      "overflow with no exception and nothing in the log" % ", ".join(undeclared))

check("and at least one is deliberately multi-column, so this is a real distinction",
      multi >= 1,
      "-- if nothing wanted two columns the honest fix would have been a helper, not a flag on "
      "each site")

check("the settings window is the multi-column one, and keeps its own width",
      "ColumnWidth = (inRect.width - 34f) / 2f" in read(SETTINGS)
      and "maxOneColumn" not in read(SETTINGS),
      "-- its priority sliders wrap into a real second column on purpose. Setting the flag there "
      "would break a working layout, which is the difference between a sweep and a "
      "find-and-replace")

page = read(PAGE)
check("THE SETUP PAGE'S SCROLLING LISTING IS ONE COLUMN",
      "listing.maxOneColumn = true;" in page,
      "-- this is the page the owner was looking at when it stopped after three lines")

check("and so is the pinned confirm row",
      "gate.maxOneColumn = true;" in page,
      "-- that rect is sized to one checkbox, so a label wrapping to a second line would push "
      "the box off to the right and Start could never be satisfied")

check("the page still measures its content from the listing it just drew",
      "contentHeight = listing.CurHeight + 20f;" in page,
      "-- with one column CurHeight is the true total, so this converges instead of collapsing")

print("")
print("THE SUPPLIES COME FROM THE DEF, NOT FROM A SCENARIO ANOTHER MOD REWRITES")
print("-" * 78)

component = read(COMPONENT)

check("the company's own supplies are read from the AUTHORED scenario def",
      "internal static ScenarioDef AuthoredScenario(RimroomsStartDef start)" in component
      and "DefDatabase<ScenarioDef>.AllDefsListForReading" in component,
      "-- EdB Prepare Carefully swaps the live scenario's starting-thing parts for parts built "
      "from the player's edited equipment, so the live scenario cannot report what the company "
      "contributes. Register row [85]: Optional, Provisional, never a runtime dependency")

check("matched by the start it declares, not by position or name",
      "ours != null && ours.startDef == start" in component,
      "-- a renamed or re-ordered scenario must still resolve, and a start with no scenario must "
      "return null rather than silently reporting the first one it finds")

check("AND IT STILL NEVER BUILDS OBJECTS TO DESCRIBE THEM",
      "PlayerStartingThings" not in component.split("internal static List<string> CompanySupplies")[1],
      "-- GetSummaryListEntries is Core's public phrasing and costs nothing; "
      "PlayerStartingThings constructs real Things and must never be called to draw a page")

check("no reflection was used to reach the protected count fields",
      "GetField(" not in component and "BindingFlags" not in component
      and "GetValue(" not in component,
      "-- ScenPart_ThingCount.thingDef/stuff/count are protected, and this package uses no "
      "Harmony and no reflection. Core already exposes the same information publicly")

check("BOTH LISTS ARE DRAWN, which is what was actually asked for",
      '"RR_Setup_CompanySupplies".Translate()' in page
      and '"RR_Setup_Supplies".Translate()' in page
      and "StartupReview.CompanySupplies(start)" in page
      and "StartupReview.SupplySummary()" in page,
      '-- owner: *"the equipemnet for the gate that u get added to ur start ON TOP OF what u '
      'fill out in edb prepare carfully"*. Both, each under its own heading')

check("an empty list says so instead of showing a heading over nothing",
      page.count('listing.Label("RR_Setup_None".Translate());') >= 2,
      "-- a bare heading with nothing under it is the bug the owner reported, and it must not be "
      "possible to reproduce it by having genuinely nothing to list")

check("and a disagreement between the two lists is stated",
      "EquipmentManagedElsewhere" in page and "RR_Setup_SuppliesDiffer" in page,
      "-- something else managing the equipment is a legitimate choice; two lists that disagree "
      "with no explanation is not")

print("")
print("AND THE GATE LINE STOPS ASSERTING SOMETHING THAT IS FALSE FOR TWO OF THREE STARTS")
print("-" * 78)

keyed = read(KEYED)
check("RR_Setup_GateCost no longer promises the materials are present",
      "Those are in the supplies below." not in keyed,
      "-- the bill wants 100 steel and 8 components; the Furniture Store start arrives with 80 "
      "steel and no components at all, so that sentence was simply untrue there. It was written "
      "against the Async start and asserted for all three")

check("it points at the list instead, which is now actually drawn",
      "Check the starting supplies below for them." in keyed,
      "-- the list beneath is the evidence; pointing at evidence only works once the evidence is "
      "on screen, which is the other half of this checkpoint")

for key in ("RR_Setup_CompanySupplies", "RR_Setup_SuppliesDiffer"):
    check("the new key %s is written" % key, "<%s>" % key in keyed,
          "-- a key used in code and missing from Keyed draws its own raw name to the player")

print("")
if failures:
    print("%d CLAIM(S) FAILED" % len(failures))
    for claim in failures:
        print("  - %s" % claim)
    sys.exit(1)
print("ALL SETUP-PAGE CLAIMS HOLD")
