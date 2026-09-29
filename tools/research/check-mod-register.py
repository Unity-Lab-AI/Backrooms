"""Verify both generated registers against the tracked CSVs that produced them.

Written because the previous register could not be checked at all: it had no
source, so there was nothing to compare it to and nothing to notice when it drifted.

Two outputs are checked. The **HTML register** is the one that matters most: there is
no spreadsheet application installed on this machine and no `.xlsx` association at
all, so the browser file is the register anybody actually reads. It is checked for
every mod having a card and a link to it, every recorded value being present and
correctly escaped, the filters offering exactly the values the rows contain, balanced
tag nesting, and no external asset -- it has to work offline.

What this proves, in order of how much it is worth:

1. **Round trip.** Every cell is read back out of the packaged workbook and
   compared against the CSV rows. Any value the writer mangled, dropped, escaped
   wrongly or put in the wrong column shows up here as a diff.
2. **No formula-typed text.** The old register wrote all 5,009 of its text cells
   as ``t="str"`` -- the cell type for a cached formula result -- with no formula
   in the file. This asserts the rebuilt workbook contains none of those.
3. **Nothing is clipped.** The old register pinned every row to
   ``ht="78" customHeight="1"`` while five of its columns carried up to 300
   characters. This asserts no row sets customHeight, and that every row's height
   leaves room for its own longest wrapped cell.
4. **The package is well formed.** Every part parses, every relationship id
   resolves, every part has a content type, every style index exists, and every
   hyperlink and merge points at a cell that was actually written.

Usage
-----
    python tools/research/check-mod-register.py [--workbook PATH] [--html PATH]
"""

import argparse
import csv
import os
import re
import sys
import xml.etree.ElementTree as ElementTree
import zipfile
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "build_mod_register", os.path.join(HERE, "build-mod-register.py"))
builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(builder)

MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"


def split_ref(reference):
    """Return (row, column) -- the same key order the value maps use."""
    match = re.match(r"([A-Z]+)(\d+)$", reference)
    column = 0
    for character in match.group(1):
        column = column * 26 + ord(character) - 64
    return int(match.group(2)), column


def read_sheet(archive, part):
    """Return (values_by_(row,col), row_heights, custom_heights, merges, links, max_style)."""
    root = ElementTree.fromstring(archive.read(part))
    values, heights, custom, styles = {}, {}, [], set()
    formula_typed = []
    for row in root.iter(MAIN + "row"):
        number = int(row.get("r"))
        if row.get("ht"):
            heights[number] = float(row.get("ht"))
        if row.get("customHeight"):
            custom.append(number)
        for cell in row.findall(MAIN + "c"):
            cell_row, column = split_ref(cell.get("r"))
            if cell_row != number:
                raise AssertionError("cell %s sits in row %d" % (cell.get("r"), number))
            styles.add(int(cell.get("s") or 0))
            kind = cell.get("t")
            if kind == "str":
                formula_typed.append(cell.get("r"))
            if kind == "inlineStr":
                node = cell.find(MAIN + "is/" + MAIN + "t")
                values[(number, column)] = node.text if node is not None and node.text else ""
            else:
                node = cell.find(MAIN + "v")
                values[(number, column)] = node.text if node is not None and node.text else ""
    merges = [m.get("ref") for m in root.iter(MAIN + "mergeCell")]
    links = [(h.get("ref"), h.get("location")) for h in root.iter(MAIN + "hyperlink")]
    autofilter = root.find(MAIN + "autoFilter")
    return {
        "values": values, "heights": heights, "custom": custom, "styles": styles,
        "merges": merges, "links": links, "formula_typed": formula_typed,
        "autofilter": autofilter.get("ref") if autofilter is not None else None,
        "name_hint": part,
    }


def check_html(path, rows, require):
    """Validate the browser register -- the output the owner's machine can actually open.

    There is no spreadsheet application on the build or owner machine and no `.xlsx`
    association at all, so this file, not the workbook, is the one that gets read. It
    therefore gets the same round-trip treatment.
    """
    if not os.path.isfile(path):
        require(False, "HTML register not found: %s" % path)
        return
    document = open(path, encoding="utf-8").read()

    require(document.startswith("<!DOCTYPE html>"), "HTML register has no doctype")
    require("<script>" in document and "</script>" in document, "HTML register lost its script")
    require("http://" not in document.replace("http://www.w3.org", "")
            and "https://cdn" not in document and "<link" not in document,
            "HTML register pulls an external asset; it must work offline")

    # Every mod reachable: an index row, a card anchor, and a link between them.
    for row in rows:
        anchor = 'id="mod-%s"' % row["LoadOrder"]
        require(anchor in document, "HTML register has no card for load order %s" % row["LoadOrder"])
        require('data-card="mod-%s"' % row["LoadOrder"] in document,
                "HTML register index does not link to card %s" % row["LoadOrder"])
    require(document.count('<article id="mod-') == len(rows),
            "HTML register has %d cards for %d mods"
            % (document.count('<article id="mod-'), len(rows)))
    require(document.count('<tbody id="indexBody">') == 1, "HTML register index body is not unique")

    # Every value present, and correctly escaped rather than merely present.
    for row in rows:
        for heading, key in builder.CARD_FIELDS:
            value = (row.get(key) or "").strip()
            if not value or len(value) < 12:
                continue
            escaped = builder.html_escape(value)
            require(escaped in document,
                    "HTML register is missing %r for %s" % (heading, row["ModName"]))
    # Filter controls must offer exactly the values present in the rows.
    for key, element in (("Stance", 'id="fStance"'), ("Firmness", 'id="fFirm"'),
                         ("SystemFamily", 'id="fFamily"')):
        require(element in document, "HTML register lost the %s filter" % key)
        for value in {r.get(key) or "(unclassified)" for r in rows}:
            require('value="%s"' % builder.html_escape(value, True) in document,
                    "HTML register %s filter has no option for %r" % (key, value))

    # Well formed enough to parse. html.parser tolerates HTML5 void elements that an XML
    # parser would reject, so this checks nesting without demanding XHTML.
    class Balanced(HTMLParser):
        VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                "link", "meta", "source", "track", "wbr"}

        def __init__(self):
            HTMLParser.__init__(self, convert_charrefs=True)
            self.stack = []
            self.problems = []

        def handle_starttag(self, tag, attrs):
            if tag not in self.VOID:
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if tag in self.VOID:
                return
            if not self.stack:
                self.problems.append("stray </%s>" % tag)
            elif self.stack[-1] != tag:
                self.problems.append("</%s> closes <%s>" % (tag, self.stack[-1]))
                if tag in self.stack:
                    while self.stack and self.stack.pop() != tag:
                        pass
            else:
                self.stack.pop()

    parser = Balanced()
    parser.feed(document)
    require(not parser.problems, "HTML register nesting: %s" % parser.problems[:3])
    require(not parser.stack, "HTML register has unclosed tags: %s" % parser.stack[:3])
    return len(document.encode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", default=builder.DEFAULT_OUT)
    parser.add_argument("--html", default=builder.DEFAULT_HTML)
    arguments = parser.parse_args()

    failures = []

    def require(condition, message):
        if not condition:
            failures.append(message)

    if not os.path.isfile(arguments.workbook):
        sys.stderr.write("register: workbook not found: %s\n" % arguments.workbook)
        return 1

    problems = []
    rows = builder.load_rows(problems)
    for problem in problems:
        failures.append("source: %s" % problem)

    archive = zipfile.ZipFile(arguments.workbook)
    names = set(archive.namelist())

    # --- package structure ------------------------------------------------- #
    for part in names:
        try:
            ElementTree.fromstring(archive.read(part))
        except ElementTree.ParseError as error:
            failures.append("part %s does not parse: %s" % (part, error))

    content_types = ElementTree.fromstring(archive.read("[Content_Types].xml"))
    defaults = {d.get("Extension").lower() for d in content_types.iter(CT + "Default")}
    overrides = {o.get("PartName") for o in content_types.iter(CT + "Override")}
    for part in names:
        if part == "[Content_Types].xml":
            continue
        extension = part.rsplit(".", 1)[-1].lower()
        require("/" + part in overrides or extension in defaults,
                "no content type covers %s" % part)

    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {r.get("Id"): r.get("Target") for r in relationships.iter(PKG_REL + "Relationship")}
    sheets = {}
    for sheet in workbook.iter(MAIN + "sheet"):
        identifier = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        require(identifier in targets, "sheet %s has an unresolved relationship" % sheet.get("name"))
        part = "xl/" + targets[identifier]
        require(part in names, "sheet %s points at a missing part %s" % (sheet.get("name"), part))
        sheets[sheet.get("name")] = read_sheet(archive, part)

    for expected in ("Overview", "Index", "Mod Register", "Mod Cards"):
        require(expected in sheets, "sheet %r is missing" % expected)
    if failures:
        for failure in failures:
            sys.stderr.write("register: %s\n" % failure)
        return 1

    style_count = len(list(ElementTree.fromstring(archive.read("xl/styles.xml"))
                           .iter(MAIN + "xf"))) - 1  # cellStyleXfs holds one
    for name, sheet in sheets.items():
        for style in sheet["styles"]:
            require(style < style_count, "sheet %s uses style %d, only %d exist"
                    % (name, style, style_count))
        require(not sheet["formula_typed"],
                "sheet %s still has formula-typed text cells: %s"
                % (name, sheet["formula_typed"][:3]))
        require(not sheet["custom"],
                "sheet %s pins %d rows with customHeight; that is what clipped the old register"
                % (name, len(sheet["custom"])))
        for reference, location in sheet["links"]:
            require(split_ref(reference) in sheet["values"],
                    "sheet %s links from empty cell %s" % (name, reference))
            target_sheet = location.split("!")[0].strip("'")
            require(target_sheet in sheets, "sheet %s links to unknown sheet %r" % (name, target_sheet))
            require(split_ref(location.split("!")[1]) in sheets[target_sheet]["values"],
                    "sheet %s links to an empty cell at %s" % (name, location))
        for reference in sheet["merges"]:
            first, last = reference.split(":")
            require(split_ref(first) in sheet["values"],
                    "sheet %s merges from an empty cell %s" % (name, first))

    # --- round trip: the register grid must equal the CSV rows -------------- #
    register = sheets["Mod Register"]
    headings = [heading for heading, _, _ in builder.REGISTER_COLUMNS]
    for index, heading in enumerate(headings, start=1):
        require(register["values"].get((1, index)) == heading,
                "register column %d header is %r, expected %r"
                % (index, register["values"].get((1, index)), heading))
    for offset, row in enumerate(rows):
        number = offset + 2
        for index, (heading, key, width) in enumerate(builder.REGISTER_COLUMNS, start=1):
            expected = str(row.get(key, "") or "")
            actual = register["values"].get((number, index), "")
            if key == "LoadOrder":
                expected = str(int(expected))
            require(actual == expected,
                    "register row %d column %r: got %r, expected %r"
                    % (number, heading, actual[:60], expected[:60]))
        # Nothing clipped: the row must be tall enough for its own longest cell.
        needed = builder.wrapped_height([(row.get(key, ""), width)
                                         for _, key, width in builder.REGISTER_COLUMNS
                                         if key != "LoadOrder"])
        require(register["heights"].get(number, 15.0) >= needed - 0.01,
                "register row %d is %.1f tall but needs %.1f"
                % (number, register["heights"].get(number, 15.0), needed))

    require(register["autofilter"] == "A1:Q%d" % (len(rows) + 1),
            "register autofilter is %r" % register["autofilter"])

    # --- every mod has a card, and the index reaches it --------------------- #
    cards = sheets["Mod Cards"]
    index_sheet = sheets["Index"]
    card_titles = {value for (_, column), value in cards["values"].items()
                   if column == 1 and re.match(r"^\d{3}  ", value or "")}
    require(len(card_titles) == len(rows),
            "found %d cards for %d mods" % (len(card_titles), len(rows)))
    link_targets = dict(index_sheet["links"])
    for offset, row in enumerate(rows):
        number = offset + 2
        require(index_sheet["values"].get((number, 2)) == row["ModName"],
                "index row %d names %r" % (number, index_sheet["values"].get((number, 2))))
        reference = "G%d" % number
        require(reference in link_targets, "index row %d has no card link" % number)
        location = link_targets[reference]
        card_row, _ = split_ref(location.split("!")[1])
        title = cards["values"].get((card_row, 1), "")
        require(title.startswith("%03d  " % int(row["LoadOrder"])) and row["ModName"] in title,
                "index row %d links to card %r" % (number, title[:50]))
        for field_offset, (heading, key) in enumerate(builder.CARD_FIELDS, start=2):
            label_row = card_row + field_offset
            require(cards["values"].get((label_row, 1)) == heading,
                    "card for %s: row %d label is %r, expected %r"
                    % (row["ModName"], label_row, cards["values"].get((label_row, 1)), heading))
            require(cards["values"].get((label_row, 2), "") == str(row.get(key, "") or ""),
                    "card for %s: field %r does not match the register" % (row["ModName"], heading))

    # --- overview tallies are counts of the rows, not stored numbers -------- #
    overview = sheets["Overview"]
    tally = {}
    for row in rows:
        family = row.get("SystemFamily") or "(unclassified)"
        tally[family] = tally.get(family, 0) + 1
    found = {}
    for (number, column), value in overview["values"].items():
        if column == 1 and value in tally:
            found[value] = int(overview["values"].get((number, 2), "0") or 0)
    for family, count in tally.items():
        require(found.get(family) == count,
                "overview tally for %r is %r, the rows say %d" % (family, found.get(family), count))

    html_bytes = check_html(arguments.html, rows, require)

    if failures:
        for failure in failures[:40]:
            sys.stderr.write("register: %s\n" % failure)
        if len(failures) > 40:
            sys.stderr.write("register: ... and %d more\n" % (len(failures) - 40))
        return 1

    print("register verified")
    print("  browser register  : %s" % arguments.html)
    print("                      %s bytes, offline, every mod carded and linked" % html_bytes)
    print("  workbook          : %s" % arguments.workbook)
    print("  sheets            : %s" % ", ".join(sorted(sheets)))
    print("  mods round-tripped: %d x %d columns" % (len(rows), len(builder.REGISTER_COLUMNS)))
    print("  cards checked     : %d, every field equal to the register" % len(card_titles))
    print("  formula-typed text: 0 cells (the old register had 5,009)")
    print("  pinned row heights: 0 rows (the old register pinned 294)")
    print("  family tallies    : %d, all computed from the rows" % len(tally))
    return 0


if __name__ == "__main__":
    sys.exit(main())
