"""Build the 294-mod integration register workbook from tracked text.

Why this script exists
----------------------
The register shipped as a workbook with no generator. It could not be rebuilt,
updated or verified, and six columns of integration analysis existed nowhere but
inside that one binary. Three defects were found in it on 2026-09-29:

1. Every one of its 5,009 text cells was written as ``t="str"`` -- the OOXML cell
   type for a *cached formula result* -- with no formula anywhere in the file, and
   ``xl/sharedStrings.xml`` was an empty ``<sst/>`` while the workbook still
   declared a sharedStrings relationship. Excel tolerates that; stricter readers
   are under no obligation to.
2. All 294 rows were pinned ``ht="78" customHeight="1"``, about five lines at 9pt,
   while five columns carry up to 300 characters. ``customHeight="1"`` forbids
   Excel from auto-fitting, so Planned Use, Compatibility Watch, FinalDisposition,
   EvidenceBuild and AcceptanceEvidence were permanently truncated on screen.
   Gridlines were off and no cell had a border.
3. It had no source. This script is the fix for that one.

Sources of truth, each fact in exactly one place
------------------------------------------------
* ``docs/research/rimworld-server-mod-inventory.csv`` owns the eleven inventory
  and evidence columns and is referenced across the docs; this script never
  rewrites it.
* ``docs/research/mod-register-integration-fields-2026-09-29.csv`` owns the six
  analysis columns lifted out of the orphan workbook.
* ``docs/research/mod-register-overview-2026-09-29.csv`` owns the overview prose.
  The system-family tallies are **not** stored there -- they are counted from the
  rows themselves on every build, so they cannot drift from what they describe.

Output layout
-------------
Four sheets, because seventeen columns across 294 rows is not navigable as one
wide grid however correctly it is encoded.

* **Overview**   -- measures, computed family tallies, source links.
* **Index**      -- fits one screen wide; one line per mod; links into the card.
* **Mod Register** -- all seventeen columns, autofilter, frozen header and first
  two columns, row heights computed to fit the tallest wrapped cell and left
  auto-fittable so Excel may still grow them.
* **Mod Cards**  -- one vertical label/value block per mod. Nothing is ever
  clipped here; this is the sheet to read a single mod in.

Standard library only, by design: the repository pins no Python packages and a
build tool that needs an install is a build tool that stops working.

Usage
-----
    python tools/research/build-mod-register.py            # write the workbook
    python tools/research/build-mod-register.py --check    # validate only
"""

import argparse
import csv
import math
import os
import re
import sys
import zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

INVENTORY_CSV = os.path.join(REPO, "docs", "research", "rimworld-server-mod-inventory.csv")
FIELDS_CSV = os.path.join(REPO, "docs", "research", "mod-register-integration-fields-2026-09-29.csv")
OVERVIEW_CSV = os.path.join(REPO, "docs", "research", "mod-register-overview-2026-09-29.csv")
DEFAULT_OUT = os.path.join(
    REPO, "outputs", "rimrooms-async-industries-register-2026-09-27",
    "Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx")

# The HTML register is the primary deliverable, not a convenience copy.
#
# Owner report, 2026-09-29: *"wtf is this xlsx??? i thought it was a spread sheet but it
# just opens up codex for chatgpt???"* -- checked on the machine and confirmed: there is
# no `.xlsx` association registered at all (`assoc .xlsx` returns nothing) and no
# spreadsheet application installed anywhere -- no Excel, no LibreOffice, no OnlyOffice,
# no WPS. Windows handed the extension to an unrelated app that loosely claimed it.
#
# So the workbook was never openable here, whatever its XML said. This HTML file opens in
# a browser, which is always present, needs no install, and loads no external asset so it
# works offline. Both outputs are built from the same rows in one pass, so they cannot
# disagree with each other.
DEFAULT_HTML = os.path.join(
    REPO, "outputs", "rimrooms-async-industries-register-2026-09-27",
    "Rimrooms_Async_Industries_294_Mod_Integration_Register.html")

EXPECTED_ROWS = 294

# Column order of the full register sheet: (heading, source key, width).
REGISTER_COLUMNS = [
    ("Load order", "LoadOrder", 10),
    ("Mod", "ModName", 38),
    ("Workshop ID / package ID", "ModID", 22),
    ("Profile type", "Type", 10),
    ("Workshop URL", "WorkshopURL", 46),
    ("System Family", "SystemFamily", 30),
    ("Backrooms Dependency", "BackroomsDependency", 44),
    ("Planned Use", "PlannedUse", 44),
    ("Integration Approach", "IntegrationApproach", 44),
    ("Compatibility Watch", "CompatibilityWatch", 44),
    ("Research Status", "ResearchStatus", 34),
    ("FeatureTraceIDs", "FeatureTraceIDs", 22),
    ("ReviewRecord", "ReviewRecord", 40),
    ("ReviewStatus", "ReviewStatus", 26),
    ("FinalDisposition", "FinalDisposition", 44),
    ("EvidenceBuild", "EvidenceBuild", 44),
    ("AcceptanceEvidence", "AcceptanceEvidence", 44),
]

# The card sheet shows the same fields, minus the two that are already in its title.
CARD_FIELDS = [(heading, key) for heading, key, _ in REGISTER_COLUMNS
               if key not in ("LoadOrder", "ModName")]


# --------------------------------------------------------------------------- #
# Derived columns
# --------------------------------------------------------------------------- #

def disposition_stance(text):
    """Coarse bucket for what we actually do with a mod.

    The raw FinalDisposition strings take 104 distinct forms, which is useless as
    a filter. The order of these tests is the priority order: a row reading
    "required only for the selected co-op path; optional for solo play" is
    Required, not Optional.
    """
    lowered = (text or "").lower()
    if not lowered.strip():
        return "Unrecorded"
    if "required" in lowered:
        return "Required"
    if ("exclude" in lowered or "unrelated" in lowered or "no direct" in lowered
            or "no-touch" in lowered or lowered.startswith("none")):
        return "No integration"
    if "configuration" in lowered:
        return "Configuration only"
    if "visual-only" in lowered or "appearance-only" in lowered:
        return "Visual only"
    # "Optional" outranks the weaker no-integration phrases below it on purpose. A row
    # reading "optional support; no Rimrooms patch planned" is a mod we support without
    # patching, not a mod we ignore -- testing the phrases the other way round moved 59
    # supported mods into No integration, which is the opposite of what they say.
    if "optional" in lowered:
        return "Optional"
    if ("no integration" in lowered or "no rimrooms patch" in lowered
            or "no rimrooms dependency" in lowered):
        return "No integration"
    return "Unclassified"


def disposition_firmness(text):
    """Whether this row's disposition is still open. The continue-forward axis."""
    return "Provisional" if (text or "").strip().lower().startswith("provisional") else "Settled"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_rows(problems):
    inventory = read_csv(INVENTORY_CSV)
    fields = {row["LoadOrder"]: row for row in read_csv(FIELDS_CSV)}

    if len(inventory) != EXPECTED_ROWS:
        problems.append("inventory holds %d rows, expected %d" % (len(inventory), EXPECTED_ROWS))
    if len(fields) != EXPECTED_ROWS:
        problems.append("analysis fields hold %d rows, expected %d" % (len(fields), EXPECTED_ROWS))

    rows = []
    for record in inventory:
        order = record["LoadOrder"]
        analysis = fields.get(order)
        if analysis is None:
            problems.append("load order %s has no analysis row" % order)
            analysis = {}
        elif analysis.get("ModID", "") != record.get("ModID", ""):
            problems.append("load order %s: analysis ModID %r disagrees with inventory %r"
                            % (order, analysis.get("ModID"), record.get("ModID")))
        merged = dict(record)
        for key in ("SystemFamily", "BackroomsDependency", "PlannedUse",
                    "IntegrationApproach", "CompatibilityWatch", "ResearchStatus"):
            merged[key] = (analysis.get(key, "") or "").strip()
        merged["Stance"] = disposition_stance(merged.get("FinalDisposition", ""))
        merged["Firmness"] = disposition_firmness(merged.get("FinalDisposition", ""))
        rows.append(merged)

    rows.sort(key=lambda r: int(r["LoadOrder"]))
    seen = [int(r["LoadOrder"]) for r in rows]
    if seen != list(range(1, len(seen) + 1)):
        problems.append("load order is not a contiguous 1..N run")

    for row in rows:
        record = (row.get("ReviewRecord") or "").strip()
        if record and not os.path.isfile(os.path.join(REPO, "docs", record.replace("/", os.sep))):
            # ReviewRecord is written relative to docs/ in the inventory.
            if not os.path.isfile(os.path.join(REPO, record.replace("/", os.sep))):
                problems.append("load order %s: review record not found: %s"
                                % (row["LoadOrder"], record))
    return rows


# --------------------------------------------------------------------------- #
# Minimal OOXML writer
# --------------------------------------------------------------------------- #

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def escape(text):
    text = CONTROL.sub("", str(text))
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def column_name(index):
    name = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


class Sheet(object):
    """One worksheet. Cells are appended row by row in order."""

    def __init__(self, name, widths, freeze=None, show_gridlines=True):
        self.name = name
        self.widths = widths            # list of (first_col, last_col, width)
        self.freeze = freeze            # (x_split, y_split) or None
        self.show_gridlines = show_gridlines
        self.rows = []                  # list of (height_or_None, [(col, value, style, kind)])
        self.merges = []
        self.links = []                 # (ref, location, display)
        self.autofilter = None
        self.max_column = 1

    def add_row(self, cells, height=None):
        """cells: list of (value, style, kind) starting at column A; None skips."""
        packed = []
        for index, cell in enumerate(cells, start=1):
            if cell is None:
                continue
            value, style, kind = cell
            if value is None or value == "":
                if style == 0:
                    continue
                packed.append((index, "", style, "blank"))
            else:
                packed.append((index, value, style, kind))
            self.max_column = max(self.max_column, index)
        self.rows.append((height, packed))
        return len(self.rows)           # 1-based row number of what was just added

    def to_xml(self):
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
        out.append('<worksheet xmlns="%s" xmlns:r="%s">' % (MAIN_NS, REL_NS))
        out.append('<dimension ref="A1:%s%d"/>' % (column_name(self.max_column), max(1, len(self.rows))))
        gridlines = "" if self.show_gridlines else ' showGridLines="0"'
        out.append('<sheetViews><sheetView%s workbookViewId="0">' % gridlines)
        if self.freeze:
            x_split, y_split = self.freeze
            top_left = "%s%d" % (column_name(x_split + 1), y_split + 1)
            pane = "bottomRight" if x_split and y_split else ("topRight" if x_split else "bottomLeft")
            attrs = ""
            if x_split:
                attrs += ' xSplit="%d"' % x_split
            if y_split:
                attrs += ' ySplit="%d"' % y_split
            out.append('<pane%s topLeftCell="%s" activePane="%s" state="frozen"/>'
                       % (attrs, top_left, pane))
            out.append('<selection pane="%s" activeCell="%s" sqref="%s"/>' % (pane, top_left, top_left))
        out.append('</sheetView></sheetViews>')
        out.append('<sheetFormatPr defaultRowHeight="15"/>')
        if self.widths:
            out.append("<cols>")
            for first, last, width in self.widths:
                out.append('<col min="%d" max="%d" width="%g" customWidth="1"/>' % (first, last, width))
            out.append("</cols>")

        out.append("<sheetData>")
        for number, (height, cells) in enumerate(self.rows, start=1):
            if not cells and height is None:
                continue
            attrs = ' r="%d"' % number
            if height is not None:
                # Deliberately no customHeight: this height is a floor that renders
                # correctly everywhere, and Excel stays free to grow the row further.
                attrs += ' ht="%g"' % height
            out.append("<row%s>" % attrs)
            for column, value, style, kind in cells:
                ref = "%s%d" % (column_name(column), number)
                if kind == "n":
                    out.append('<c r="%s" s="%d"><v>%s</v></c>' % (ref, style, escape(value)))
                elif kind == "blank":
                    out.append('<c r="%s" s="%d"/>' % (ref, style))
                else:
                    out.append('<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                               % (ref, style, escape(value)))
            out.append("</row>")
        out.append("</sheetData>")

        # Element order below is fixed by the schema: autoFilter, mergeCells,
        # hyperlinks, pageMargins. Getting it wrong is a repair prompt in Excel.
        if self.autofilter:
            out.append('<autoFilter ref="%s"/>' % self.autofilter)
        if self.merges:
            out.append('<mergeCells count="%d">' % len(self.merges))
            for reference in self.merges:
                out.append('<mergeCell ref="%s"/>' % reference)
            out.append("</mergeCells>")
        if self.links:
            out.append("<hyperlinks>")
            for ref, location, display in self.links:
                out.append('<hyperlink ref="%s" location="%s" display="%s"/>'
                           % (ref, escape(location), escape(display)))
            out.append("</hyperlinks>")
        out.append('<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/>')
        out.append("</worksheet>")
        return "".join(out)


# Style table. Index into cellXfs; see STYLES below for the definitions.
S_DEFAULT = 0
S_TITLE = 1
S_SUBTITLE = 2
S_HEADER = 3          # white bold on navy, wrapped, bordered
S_BODY = 4            # 9pt, top, wrapped, bordered
S_BODY_BAND = 5       # same with a light band fill
S_NUM = 6             # 9pt right aligned, bordered
S_NUM_BAND = 7
S_LINK = 8            # 9pt blue underlined
S_LINK_BAND = 9
S_CARD_TITLE = 10     # white bold 11pt on navy
S_CARD_LABEL = 11     # bold 9pt navy, top, wrapped
S_CARD_VALUE = 12     # 9pt, top, wrapped
S_SECTION = 13        # bold 10pt white on navy (overview section headers)
S_OV_LABEL = 14       # bold 10pt, top, wrapped
S_OV_VALUE = 15       # 10pt, top, wrapped
S_OV_NUM = 16         # 10pt right aligned
S_NOTE = 17           # italic 9pt grey, wrapped

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="{main}">
<fonts count="10">
<font><sz val="11"/><name val="Calibri"/><family val="2"/></font>
<font><b/><sz val="16"/><color rgb="FF172033"/><name val="Arial"/></font>
<font><i/><sz val="10"/><color rgb="FF526174"/><name val="Arial"/></font>
<font><b/><sz val="9"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
<font><sz val="9"/><color rgb="FF172033"/><name val="Arial"/></font>
<font><b/><sz val="9"/><color rgb="FF253858"/><name val="Arial"/></font>
<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
<font><u/><sz val="9"/><color rgb="FF0B5FA5"/><name val="Arial"/></font>
<font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
<font><sz val="10"/><color rgb="FF172033"/><name val="Arial"/></font>
</fonts>
<fills count="4">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF253858"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFF2F5F9"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="2">
<border><left/><right/><top/><bottom/><diagonal/></border>
<border>
<left style="thin"><color rgb="FFD3DAE4"/></left><right style="thin"><color rgb="FFD3DAE4"/></right>
<top style="thin"><color rgb="FFD3DAE4"/></top><bottom style="thin"><color rgb="FFD3DAE4"/></bottom><diagonal/>
</border>
</borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="18">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="3" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="4" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="4" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="4" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="top"/></xf>
<xf numFmtId="0" fontId="4" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="top"/></xf>
<xf numFmtId="0" fontId="7" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="7" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="6" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
<xf numFmtId="0" fontId="5" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="4" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="8" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="5" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="9" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="9" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="top"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>""".replace("{main}", MAIN_NS)


def wrapped_height(values_and_widths, point_size=9, floor=16.0, ceiling=240.0):
    """A row height that actually fits the tallest wrapped cell in the row.

    Characters-per-line is deliberately pessimistic (one char per width unit,
    where 9pt Arial fits rather more) so the computed height errs tall. The
    caller writes it without customHeight, so Excel may grow it further but will
    never shrink it back to a clip.
    """
    line = point_size * 1.32
    lines = 1
    for value, width in values_and_widths:
        text = str(value or "")
        if not text:
            continue
        per_line = max(4, int(width))
        for segment in text.split("\n"):
            lines = max(lines, int(math.ceil(len(segment) / float(per_line))) or 1)
    return min(ceiling, max(floor, lines * line + 5.0))


# --------------------------------------------------------------------------- #
# Sheet construction
# --------------------------------------------------------------------------- #

def build_overview(rows, overview_records):
    sheet = Sheet("Overview", [(1, 1, 46), (2, 2, 96)], show_gridlines=False)
    titles = [r for r in overview_records if r["Section"] == "title"]
    measures = [r for r in overview_records if r["Section"] == "measure"]
    sources = [r for r in overview_records if r["Section"] == "source"]

    if titles:
        sheet.add_row([(titles[0]["Label"], S_TITLE, "s")], height=24)
    if len(titles) > 1:
        sheet.add_row([(titles[1]["Label"], S_SUBTITLE, "s")], height=16)
    sheet.add_row([(("Generated by tools/research/build-mod-register.py from the tracked CSVs "
                     "under docs/research/. Do not hand-edit this workbook; edit the CSV and rebuild."),
                    S_NOTE, "s")], height=28)
    sheet.merges.append("A3:B3")
    sheet.add_row([])

    sheet.add_row([("Measure", S_SECTION, "s"), ("Result", S_SECTION, "s")], height=18)
    for record in measures:
        value = record["Value"]
        numeric = value.isdigit()
        sheet.add_row(
            [(record["Label"], S_OV_LABEL, "s"),
             (value, S_OV_NUM if numeric else S_OV_VALUE, "n" if numeric else "s")],
            height=wrapped_height([(record["Label"], 46), (value, 96)], point_size=10))
    sheet.add_row([])

    tally = {}
    for row in rows:
        family = row.get("SystemFamily") or "(unclassified)"
        tally[family] = tally.get(family, 0) + 1
    sheet.add_row([("System family", S_SECTION, "s"), ("Profile entries", S_SECTION, "s")], height=18)
    for family in sorted(tally):
        sheet.add_row([(family, S_OV_LABEL, "s"), (tally[family], S_OV_NUM, "n")])
    sheet.add_row([("Total", S_OV_LABEL, "s"), (sum(tally.values()), S_OV_NUM, "n")])
    sheet.add_row([])

    sheet.add_row([("Disposition stance", S_SECTION, "s"), ("Profile entries", S_SECTION, "s")], height=18)
    stances = {}
    for row in rows:
        stances[row["Stance"]] = stances.get(row["Stance"], 0) + 1
    for stance in sorted(stances, key=lambda s: (-stances[s], s)):
        sheet.add_row([(stance, S_OV_LABEL, "s"), (stances[stance], S_OV_NUM, "n")])
    sheet.add_row([])

    sheet.add_row([("Disposition firmness", S_SECTION, "s"), ("Profile entries", S_SECTION, "s")], height=18)
    firmness = {}
    for row in rows:
        firmness[row["Firmness"]] = firmness.get(row["Firmness"], 0) + 1
    for state in sorted(firmness, key=lambda s: (-firmness[s], s)):
        sheet.add_row([(state, S_OV_LABEL, "s"), (firmness[state], S_OV_NUM, "n")])
    sheet.add_row([])

    sheet.add_row([("Source and validation", S_SECTION, "s"), ("Reference", S_SECTION, "s")], height=18)
    for record in sources:
        sheet.add_row([(record["Label"], S_OV_LABEL, "s"), (record["Value"], S_OV_VALUE, "s")],
                      height=wrapped_height([(record["Value"], 96)], point_size=10))
    return sheet


INDEX_COLUMNS = [
    ("Load", 7), ("Mod", 40), ("System family", 32), ("Stance", 17),
    ("Firmness", 12), ("Trace IDs", 20), ("Read the card", 15),
]


def build_index(rows, card_rows):
    widths = [(i, i, w) for i, (_, w) in enumerate(INDEX_COLUMNS, start=1)]
    sheet = Sheet("Index", widths, freeze=(0, 1))
    sheet.add_row([(heading, S_HEADER, "s") for heading, _ in INDEX_COLUMNS], height=30)
    for offset, row in enumerate(rows):
        band = offset % 2 == 1
        body = S_BODY_BAND if band else S_BODY
        num = S_NUM_BAND if band else S_NUM
        link = S_LINK_BAND if band else S_LINK
        number = sheet.add_row([
            (int(row["LoadOrder"]), num, "n"),
            (row["ModName"], body, "s"),
            (row["SystemFamily"], body, "s"),
            (row["Stance"], body, "s"),
            (row["Firmness"], body, "s"),
            (row["FeatureTraceIDs"], body, "s"),
            ("open card", link, "s"),
        ], height=wrapped_height([(row["ModName"], 40), (row["SystemFamily"], 32),
                                  (row["FeatureTraceIDs"], 20)]))
        sheet.links.append(("G%d" % number, "'Mod Cards'!A%d" % card_rows[row["LoadOrder"]], "open card"))
    sheet.autofilter = "A1:%s%d" % (column_name(len(INDEX_COLUMNS)), len(rows) + 1)
    return sheet


def build_register(rows):
    widths = [(i, i, w) for i, (_, _, w) in enumerate(REGISTER_COLUMNS, start=1)]
    sheet = Sheet("Mod Register", widths, freeze=(2, 1))
    sheet.add_row([(heading, S_HEADER, "s") for heading, _, _ in REGISTER_COLUMNS], height=34)
    for offset, row in enumerate(rows):
        band = offset % 2 == 1
        body = S_BODY_BAND if band else S_BODY
        num = S_NUM_BAND if band else S_NUM
        cells = []
        measured = []
        for heading, key, width in REGISTER_COLUMNS:
            value = row.get(key, "")
            if key == "LoadOrder":
                cells.append((int(value), num, "n"))
            else:
                cells.append((value, body, "s"))
                measured.append((value, width))
        sheet.add_row(cells, height=wrapped_height(measured))
    sheet.autofilter = "A1:%s%d" % (column_name(len(REGISTER_COLUMNS)), len(rows) + 1)
    return sheet


def build_cards(rows):
    """One vertical block per mod. This is the sheet where nothing is ever clipped."""
    sheet = Sheet("Mod Cards", [(1, 1, 26), (2, 2, 104), (3, 3, 16)], show_gridlines=False)
    card_rows = {}
    for index, row in enumerate(rows):
        title = "%03d  %s  (%s)" % (int(row["LoadOrder"]), row["ModName"], row["ModID"])
        number = sheet.add_row([(title, S_CARD_TITLE, "s"), ("", S_CARD_TITLE, "s"),
                                ("back to index", S_CARD_TITLE, "s")], height=22)
        sheet.merges.append("A%d:B%d" % (number, number))
        sheet.links.append(("C%d" % number, "Index!A%d" % (index + 2), "back to index"))
        card_rows[row["LoadOrder"]] = number

        sheet.add_row([("Stance", S_CARD_LABEL, "s"),
                       ("%s  --  %s" % (row["Stance"], row["Firmness"]), S_CARD_VALUE, "s")])
        for heading, key in CARD_FIELDS:
            value = row.get(key, "")
            sheet.add_row([(heading, S_CARD_LABEL, "s"), (value, S_CARD_VALUE, "s")],
                          height=wrapped_height([(value, 104)]))
        sheet.add_row([])
    return sheet, card_rows


# --------------------------------------------------------------------------- #
# HTML register -- the output the owner's machine can actually open
# --------------------------------------------------------------------------- #

HTML_STYLE = """
:root{--ink:#161b22;--dim:#57606a;--line:#d8dee4;--head:#253858;--band:#f6f8fa;
--accent:#0b5fa5;--warn:#8a5300;--ok:#1a6b38}
*{box-sizing:border-box}
body{margin:0;font:14px/1.5 "Segoe UI",Arial,sans-serif;color:var(--ink);background:#fff}
header{padding:18px 22px 12px;border-bottom:3px solid var(--head);background:#fbfcfd}
h1{margin:0;font-size:21px;color:var(--head)}
.sub{color:var(--dim);font-size:12.5px;margin-top:4px}
.note{margin-top:9px;font-size:12.5px;color:var(--warn);background:#fff8e6;
border:1px solid #f0dca8;border-radius:5px;padding:7px 10px}
nav{display:flex;gap:2px;padding:0 22px;background:var(--head);position:sticky;top:0;z-index:20}
nav button{border:0;background:transparent;color:#c6d2e2;padding:11px 17px;font:600 13px/1 inherit;
cursor:pointer;border-bottom:3px solid transparent}
nav button:hover{color:#fff}
nav button.on{color:#fff;border-bottom-color:#ffc857;background:rgba(255,255,255,.08)}
main{padding:20px 22px 60px}
section{display:none}
section.on{display:block}
table{border-collapse:collapse;width:100%;font-size:13px}
th{background:var(--head);color:#fff;text-align:left;padding:7px 9px;font-weight:600;
position:sticky;top:41px;z-index:10;vertical-align:bottom}
td{border:1px solid var(--line);padding:6px 9px;vertical-align:top}
tbody tr:nth-child(even) td{background:var(--band)}
tbody tr:hover td{background:#eef5fd}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px;
padding:11px;border:1px solid var(--line);border-radius:6px;background:var(--band)}
.controls input,.controls select{font:13px inherit;padding:5px 7px;border:1px solid #b9c2cc;
border-radius:4px;background:#fff}
.controls input{min-width:260px}
.controls label{font-size:12px;color:var(--dim);font-weight:600}
#count{font-size:12.5px;color:var(--dim);margin-left:auto}
.scroller{overflow:auto;max-height:76vh;border:1px solid var(--line);border-radius:6px}
.scroller table{font-size:12px}
.scroller td{min-width:150px;max-width:340px}
.scroller td:first-child,.scroller td:nth-child(2){min-width:0}
a{color:var(--accent)}
.pill{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11.5px;font-weight:600;
white-space:nowrap}
.s-Optional{background:#e7f1fb;color:#0b4a80}
.s-Required{background:#fde8e8;color:#8a1c1c}
.s-Nointegration{background:#eceef1;color:#4a5560}
.s-Configurationonly{background:#f0ebfa;color:#523a86}
.s-Visualonly{background:#eafaf0;color:#14663a}
.s-Unclassified{background:#fff4d6;color:#7a5200}
.f-Provisional{background:#fff4d6;color:#7a5200}
.f-Settled{background:#eafaf0;color:var(--ok)}
article{border:1px solid var(--line);border-radius:7px;margin-bottom:16px;overflow:hidden;
scroll-margin-top:60px}
article>h3{margin:0;background:var(--head);color:#fff;padding:9px 12px;font-size:14.5px;
display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
article>h3 .idx{opacity:.65;font-weight:400;font-size:12.5px}
article>h3 a{color:#ffc857;margin-left:auto;font-size:12px;font-weight:400}
article dl{margin:0;display:grid;grid-template-columns:200px 1fr}
article dt{padding:6px 12px;font-weight:600;color:var(--head);background:var(--band);
border-top:1px solid var(--line);font-size:12.5px}
article dd{margin:0;padding:6px 12px;border-top:1px solid var(--line);font-size:13px}
article dd.empty{color:var(--dim);font-style:italic}
h2{font-size:16px;color:var(--head);margin:26px 0 9px}
h2:first-child{margin-top:0}
.ov{max-width:1050px}
.ov td:first-child{width:330px;font-weight:600;color:var(--head)}
.tally td:first-child{width:430px}
.tally td:last-child{text-align:right;width:120px;font-variant-numeric:tabular-nums}
"""

HTML_SCRIPT = """
var tabs=document.querySelectorAll('nav button');
var panes=document.querySelectorAll('main > section');
function show(name){
  tabs.forEach(function(b){b.classList.toggle('on',b.dataset.pane===name);});
  panes.forEach(function(p){p.classList.toggle('on',p.id===name);});
}
tabs.forEach(function(b){b.onclick=function(){show(b.dataset.pane);};});
show('overview');

var q=document.getElementById('q');
var selStance=document.getElementById('fStance');
var selFirm=document.getElementById('fFirm');
var selFamily=document.getElementById('fFamily');
var rows=Array.prototype.slice.call(document.querySelectorAll('#indexBody tr'));
var count=document.getElementById('count');
function filter(){
  var text=(q.value||'').toLowerCase().trim();
  var st=selStance.value,fm=selFirm.value,fa=selFamily.value,shown=0;
  rows.forEach(function(r){
    var ok=(!st||r.dataset.stance===st)&&(!fm||r.dataset.firm===fm)&&(!fa||r.dataset.family===fa)
      &&(!text||r.dataset.hay.indexOf(text)>-1);
    r.style.display=ok?'':'none';
    if(ok){shown++;}
  });
  count.textContent=shown+' of '+rows.length+' mods shown';
}
[q,selStance,selFirm,selFamily].forEach(function(el){
  el.addEventListener('input',filter);el.addEventListener('change',filter);});
filter();

// A card link has to switch to the Cards pane before the fragment can scroll to it,
// because a hidden section has no layout to scroll within.
document.addEventListener('click',function(event){
  var link=event.target.closest('a[data-card]');
  if(!link){return;}
  event.preventDefault();
  show('cards');
  var target=document.getElementById(link.dataset.card);
  if(target){target.scrollIntoView({block:'start'});}
});
document.addEventListener('click',function(event){
  var back=event.target.closest('a[data-back]');
  if(!back){return;}
  event.preventDefault();
  show('index');
  window.scrollTo(0,0);
  q.focus();
});
"""


def html_escape(text, attribute=False):
    text = CONTROL.sub("", "" if text is None else str(text))
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if attribute:
        text = text.replace('"', "&quot;")
    return text


def pill(value, prefix):
    return '<span class="pill %s%s">%s</span>' % (
        prefix, html_escape(str(value).replace(" ", "").replace("-", "")), html_escape(value))


def build_html(rows, overview_records):
    titles = [r for r in overview_records if r["Section"] == "title"]
    measures = [r for r in overview_records if r["Section"] == "measure"]
    sources = [r for r in overview_records if r["Section"] == "source"]

    def tally(key):
        counts = {}
        for row in rows:
            value = row.get(key) or "(unclassified)"
            counts[value] = counts.get(value, 0) + 1
        return counts

    families = tally("SystemFamily")
    stances = tally("Stance")
    firmness = tally("Firmness")

    out = ['<!DOCTYPE html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           '<title>%s</title>' % html_escape(titles[0]["Label"] if titles else "Mod register"),
           '<style>%s</style>' % HTML_STYLE, '</head>', '<body>']

    out.append("<header>")
    out.append("<h1>%s</h1>" % html_escape(titles[0]["Label"] if titles else "Mod register"))
    if len(titles) > 1:
        out.append('<div class="sub">%s</div>' % html_escape(titles[1]["Label"]))
    out.append('<div class="note">Generated by <code>tools/research/build-mod-register.py</code> '
               'from the tracked CSVs under <code>docs/research/</code>. Do not hand-edit this '
               'file &mdash; edit the CSV and rebuild, or the edit is lost. This page needs no '
               'internet connection and no installed application beyond a browser.</div>')
    out.append("</header>")

    out.append("<nav>")
    for pane, label in (("overview", "Overview"), ("index", "Index"),
                        ("register", "Full register"), ("cards", "Mod cards")):
        out.append('<button data-pane="%s">%s</button>' % (pane, label))
    out.append("</nav>")
    out.append("<main>")

    # ---- Overview ----
    out.append('<section id="overview">')
    out.append("<h2>Measures</h2><table class=\"ov\"><tbody>")
    for record in measures:
        out.append("<tr><td>%s</td><td>%s</td></tr>"
                   % (html_escape(record["Label"]), html_escape(record["Value"])))
    out.append("</tbody></table>")
    for heading, counts, prefix in (("Disposition stance", stances, "s-"),
                                    ("Disposition firmness", firmness, "f-")):
        out.append("<h2>%s</h2><table class=\"ov tally\"><tbody>" % heading)
        for key in sorted(counts, key=lambda k: (-counts[k], k)):
            out.append("<tr><td>%s</td><td>%d</td></tr>" % (pill(key, prefix), counts[key]))
        out.append("</tbody></table>")
    out.append("<h2>System families (%d, counted from the rows)</h2>" % len(families))
    out.append('<table class="ov tally"><tbody>')
    for key in sorted(families):
        out.append("<tr><td>%s</td><td>%d</td></tr>" % (html_escape(key), families[key]))
    out.append("<tr><td><strong>Total</strong></td><td><strong>%d</strong></td></tr>"
               % sum(families.values()))
    out.append("</tbody></table>")
    out.append("<h2>Source and validation</h2><table class=\"ov\"><tbody>")
    for record in sources:
        value = record["Value"]
        if value.startswith("http"):
            shown = '<a href="%s">%s</a>' % (html_escape(value, True), html_escape(value))
        else:
            shown = html_escape(value)
        out.append("<tr><td>%s</td><td>%s</td></tr>" % (html_escape(record["Label"]), shown))
    out.append("</tbody></table></section>")

    # ---- Index ----
    out.append('<section id="index">')
    out.append('<div class="controls">')
    out.append('<input id="q" type="search" placeholder="Search name, family, trace ids, '
               'disposition, evidence…" autocomplete="off">')
    for element_id, label, values in (("fStance", "Stance", sorted(stances)),
                                      ("fFirm", "Firmness", sorted(firmness)),
                                      ("fFamily", "Family", sorted(families))):
        out.append('<label for="%s">%s</label><select id="%s"><option value="">all</option>'
                   % (element_id, label, element_id))
        for value in values:
            out.append('<option value="%s">%s</option>'
                       % (html_escape(value, True), html_escape(value)))
        out.append("</select>")
    out.append('<span id="count"></span></div>')
    out.append('<div class="scroller"><table><thead><tr>'
               "<th>Load</th><th>Mod</th><th>System family</th><th>Stance</th>"
               "<th>Firmness</th><th>Trace IDs</th><th>Card</th>"
               '</tr></thead><tbody id="indexBody">')
    for row in rows:
        haystack = " ".join(str(row.get(key, "") or "") for _, key, _ in REGISTER_COLUMNS).lower()
        out.append('<tr data-stance="%s" data-firm="%s" data-family="%s" data-hay="%s">'
                   % (html_escape(row["Stance"], True), html_escape(row["Firmness"], True),
                      html_escape(row["SystemFamily"], True), html_escape(haystack, True)))
        out.append("<td>%s</td><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td>"
                   "<td>%s</td><td><a href=\"#mod-%s\" data-card=\"mod-%s\">open card</a></td></tr>"
                   % (html_escape(row["LoadOrder"]), html_escape(row["ModName"]),
                      html_escape(row["SystemFamily"]), pill(row["Stance"], "s-"),
                      pill(row["Firmness"], "f-"), html_escape(row["FeatureTraceIDs"]),
                      html_escape(row["LoadOrder"], True), html_escape(row["LoadOrder"], True)))
    out.append("</tbody></table></div></section>")

    # ---- Full register ----
    out.append('<section id="register"><div class="scroller"><table><thead><tr>')
    for heading, _, _ in REGISTER_COLUMNS:
        out.append("<th>%s</th>" % html_escape(heading))
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        for _, key, _ in REGISTER_COLUMNS:
            out.append("<td>%s</td>" % html_escape(row.get(key, "")))
        out.append("</tr>")
    out.append("</tbody></table></div></section>")

    # ---- Cards ----
    out.append('<section id="cards">')
    for row in rows:
        out.append('<article id="mod-%s"><h3><span class="idx">%03d</span> %s '
                   '<span class="idx">%s</span> %s %s'
                   '<a href="#index" data-back="1">back to index</a></h3><dl>'
                   % (html_escape(row["LoadOrder"], True), int(row["LoadOrder"]),
                      html_escape(row["ModName"]), html_escape(row["ModID"]),
                      pill(row["Stance"], "s-"), pill(row["Firmness"], "f-")))
        for heading, key in CARD_FIELDS:
            value = row.get(key, "")
            if key == "WorkshopURL" and value.startswith("http"):
                shown = '<a href="%s">%s</a>' % (html_escape(value, True), html_escape(value))
            elif key == "ReviewRecord" and value:
                shown = "<code>%s</code>" % html_escape(value)
            elif not value:
                shown = "not recorded"
            else:
                shown = html_escape(value)
            out.append("<dt>%s</dt><dd%s>%s</dd>"
                       % (html_escape(heading), "" if value else ' class="empty"', shown))
        out.append("</dl></article>")
    out.append("</section>")

    out.append("</main>")
    out.append("<script>%s</script>" % HTML_SCRIPT)
    out.append("</body></html>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Packaging
# --------------------------------------------------------------------------- #

def package(sheets, path):
    parts = {}
    sheet_entries = []
    for index, sheet in enumerate(sheets, start=1):
        target = "xl/worksheets/sheet%d.xml" % index
        parts[target] = sheet.to_xml()
        sheet_entries.append((index, sheet.name, target))

    workbook = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<workbook xmlns="%s" xmlns:r="%s">' % (MAIN_NS, REL_NS),
                '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="28800" windowHeight="16000"/></bookViews>',
                "<sheets>"]
    for index, name, _ in sheet_entries:
        workbook.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escape(name), index, index))
    workbook.append("</sheets></workbook>")
    parts["xl/workbook.xml"] = "".join(workbook)

    rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for index, _, target in sheet_entries:
        rels.append('<Relationship Id="rId%d" Type="%s/worksheet" Target="worksheets/sheet%d.xml"/>'
                    % (index, REL_NS, index))
    style_id = len(sheet_entries) + 1
    rels.append('<Relationship Id="rId%d" Type="%s/styles" Target="styles.xml"/>' % (style_id, REL_NS))
    rels.append("</Relationships>")
    parts["xl/_rels/workbook.xml.rels"] = "".join(rels)
    parts["xl/styles.xml"] = STYLES

    parts["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
        'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')

    types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
             '<Default Extension="xml" ContentType="application/xml"/>',
             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-'
             'officedocument.spreadsheetml.sheet.main+xml"/>',
             '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-'
             'officedocument.spreadsheetml.styles+xml"/>']
    for index, _, _ in sheet_entries:
        types.append('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.'
                     'openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % index)
    types.append("</Types>")
    parts["[Content_Types].xml"] = "".join(types)

    directory = os.path.dirname(path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    # Fixed timestamp and ordering so an unchanged source rebuilds byte-identically,
    # the same determinism rule the mod assembly follows.
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(parts):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, parts[name].encode("utf-8"))
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=DEFAULT_OUT, help="workbook path to write")
    parser.add_argument("--html", default=DEFAULT_HTML, help="HTML register path to write")
    parser.add_argument("--check", action="store_true", help="validate the sources and write nothing")
    arguments = parser.parse_args()

    problems = []
    rows = load_rows(problems)
    overview_records = read_csv(OVERVIEW_CSV)

    if problems:
        for problem in problems:
            sys.stderr.write("register: %s\n" % problem)
        return 1

    if arguments.check:
        print("register sources are consistent: %d rows, %d overview records" %
              (len(rows), len(overview_records)))
        return 0

    cards, card_rows = build_cards(rows)
    sheets = [build_overview(rows, overview_records), build_index(rows, card_rows),
              build_register(rows), cards]
    package(sheets, arguments.out)

    document = build_html(rows, overview_records)
    directory = os.path.dirname(arguments.html)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    with open(arguments.html, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(document)

    print("wrote %s" % arguments.html)
    print("  the browser register: open this one. No install, no internet.")
    print("  bytes        : %d" % len(document.encode("utf-8")))
    print("wrote %s" % arguments.out)
    print("  sheets       : %s" % ", ".join(sheet.name for sheet in sheets))
    print("  mods         : %d" % len(rows))
    print("  cards        : %d" % len(card_rows))
    print("  register rows: %d" % len(sheets[2].rows))
    print("  card rows    : %d" % len(cards.rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
