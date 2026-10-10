# -*- coding: utf-8 -*-
"""Core's `Listing` silently wraps into an invisible second column, and it ate the setup page.

Owner, verbatim: *"the review company start up screen when i press start game on prepare carfully
says: 'Those are in the supplies list below' but there are no lists or supplies on the card pop up
at all.. so what the fuck?"*

**The supplies were not the only thing missing. The page stopped drawing after three lines** -- no
roster, no funding, no supplies, no facility, and only the first of five gate prerequisites. A
screenshot of the live game brightened four times over shows the region is genuinely empty, and
**the log contains no exception at all.**

THE CAUSE IS CORE, AND IT FAILS SILENTLY BY DESIGN. `Verse.Listing.GetRect` calls:

    protected void NewColumnIfNeeded(float neededHeight)
    {
        if (!maxOneColumn && curY + neededHeight > listingRect.height) { NewColumn(); }
    }

    public void NewColumn() { curY = 0f; curX += ColumnWidth + 17f; }

`Listing.Begin` sets `ColumnWidth = listingRect.width` unless a custom width was given. So when
content exceeds the listing rect's height, the listing starts a new column **a full width plus 17
to the right** -- outside the `Widgets.BeginGroup(rect)` that `Begin` opened, which clips it.
**Everything past the overflow point is drawn off the edge of the world.** No exception, no
warning, nothing in the log.

AND IT IS SELF-REINFORCING, which is why the page collapsed to three lines rather than losing just
the tail. `CurHeight => curY`, and `NewColumn` reset `curY` to zero, so:

    contentHeight = listing.CurHeight + 20f;

records the height of the *second* column instead of the total. Next frame the scroll content is
that much shorter, so the wrap happens sooner, so `CurHeight` is smaller again -- a runaway that
settles at a few lines. It also explains the missing scrollbar: by then the content genuinely did
fit.

THE FIX IS CORE'S OWN FLAG. `maxOneColumn = true` is exactly the switch that disables this, and
with it `CurHeight` is the true total, so `contentHeight` converges in one frame and the scroll
view scrolls properly.

SWEPT RATHER THAN PATCHED WHERE IT HURT. Eight listings exist in this package and **not one set
the flag**, so every scrolling list carried the same silent truncation -- including the Operations
board, which is the main window of the mod. Seven are fixed here.

**The eighth is deliberately left alone:** `RimroomsMod.DoSettingsWindowContents` sets its own
`ColumnWidth` to half the window precisely so the priority sliders wrap into a real, visible
second column. Setting the flag there would break a working two-column layout. That is the
difference between a sweep and a find-and-replace.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

NOTE = ("// One column. Core's Listing silently wraps a full column-width to the RIGHT when "
        "content\n            // outgrows the rect, outside the group it clips to, and resets "
        "CurHeight doing it -- so the\n            // page loses its tail AND under-reports its "
        "height, which shrinks the rect again.\n            ")

EDITS = [
    (os.path.join(SRC, "Scenario", "Page_RimroomsCompanySetup.cs"),
     "            var listing = new Listing_Standard();\n            listing.Begin(content);",
     "            var listing = new Listing_Standard();\n            " + NOTE
     + "listing.maxOneColumn = true;\n            listing.Begin(content);"),

    (os.path.join(SRC, "Scenario", "Page_RimroomsCompanySetup.cs"),
     "            var gate = new Listing_Standard();\n            gate.Begin(confirm);",
     "            var gate = new Listing_Standard();\n"
     "            // Same flag for the same reason: this rect is sized to one checkbox, so a\n"
     "            // label that wraps to a second line would push the box off to the right.\n"
     "            gate.maxOneColumn = true;\n            gate.Begin(confirm);"),

    (os.path.join(SRC, "UI", "ExpeditionRecordDialogs.cs"),
     "            var listing = new Listing_Standard(); listing.Begin(content);",
     "            var listing = new Listing_Standard(); listing.maxOneColumn = true;\n"
     "            listing.Begin(content);"),

    (os.path.join(SRC, "UI", "ExpeditionRecordDialogs.cs"),
     "            var listing = new Listing_Standard(); listing.Begin(inRect);",
     "            var listing = new Listing_Standard(); listing.maxOneColumn = true;\n"
     "            listing.Begin(inRect);"),

    (os.path.join(SRC, "UI", "MainTabWindow_Operations.cs"),
     "            Listing_Standard listing = new Listing_Standard();\n            listing.Begin(content);",
     "            Listing_Standard listing = new Listing_Standard();\n            " + NOTE
     + "listing.maxOneColumn = true;\n            listing.Begin(content);"),
]

# The two personnel listings are textually identical, so they are replaced together rather than
# anchored -- an ambiguous anchor is how a plant gets scored wrong.
PERSONNEL = os.path.join(SRC, "UI", "OperationsPersonnel.cs")
P_OLD = "            var listing = new Listing_Standard(); listing.Begin(content);"
P_NEW = ("            var listing = new Listing_Standard(); listing.maxOneColumn = true;\n"
         "            listing.Begin(content);")

problems = []
texts = {}
for path, old, _ in EDITS:
    text = texts.get(path)
    if text is None:
        text = io.open(path, encoding="utf-8").read()
        texts[path] = text
    if text.count(old) < 1:
        problems.append("0 of %r in %s" % (old[:52], os.path.basename(path)))

personnel = io.open(PERSONNEL, encoding="utf-8").read()
if personnel.count(P_OLD) != 2:
    problems.append("%d of the personnel listing (want 2)" % personnel.count(P_OLD))

if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for path, old, new in EDITS:
    texts[path] = texts[path].replace(old, new, 1)
for path, text in texts.items():
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("one column: %s" % os.path.basename(path))

io.open(PERSONNEL, "w", encoding="utf-8", newline="").write(personnel.replace(P_OLD, P_NEW))
print("one column: OperationsPersonnel.cs (both listings)")

settings = io.open(os.path.join(SRC, "Core", "RimroomsMod.cs"), encoding="utf-8").read()
print("settings window left two-column on purpose: %s"
      % ("maxOneColumn" not in settings))
