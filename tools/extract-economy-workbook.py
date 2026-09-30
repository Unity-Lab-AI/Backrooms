# -*- coding: utf-8 -*-
"""Read `Rimrooms_Campaign_Economy_v0.2.xlsx` without Excel, and write a tracked source for it.

Why this exists
---------------
Queue rows 1268 and 1269, verbatim:

    "`Rimrooms_Campaign_Economy_v0.2.xlsx` has the same problem and no generator. The campaign
     economy workbook is linked from CAMPAIGN_ECONOMY_MODEL.md, CAMPAIGN_ECONOMY_PROGRESSION.md,
     CAMPAIGN_ROSTER_FREEZE.md, FEATURE_TRACEABILITY.md and AI_BUILD_HANDOFF.md, and it is
     equally unopenable on this machine for exactly the same reason. It was left alone here
     deliberately rather than swept up in a register checkpoint: it is a different dataset with
     different owners, and its content has not been verified. When it is addressed it should get
     the same treatment -- tracked source, a generator, and an HTML output."

    "The register preview PNGs under `outputs/` depict the superseded two-sheet layout. Not
     deleted -- they are tracked artifacts and removing them is the owner's call -- but they must
     not be read as showing the current file."

**"Unopenable" was about Excel, not about the bytes.** An xlsx is a zip of XML, and the standard
library reads both. That is the same realisation that made the register queryable -- the HTML is
the register, not the xlsx -- applied to the other workbook. Five documents link this file and
nobody could read it; now anybody can, with no dependency installed.

What this does NOT do
---------------------
**It does not touch the numbers, reconcile them against the build, or assert they are right.**
The row is explicit that this is *"a different dataset with different owners"* whose *"content has
not been verified"*, and a generator that silently corrected a figure would destroy the only
useful property the file has: being what its author wrote. Every cell is transcribed exactly, and
the HTML says so at the top.

Shared-string handling is the one subtlety: xlsx stores repeated text once in `sharedStrings.xml`
and cells reference it by index, so a cell whose type is `s` holds an index rather than a word. A
reader that ignored that would print integers where the labels are.

Usage
-----
    python tools/extract-economy-workbook.py            writes the tracked source + HTML
    python tools/extract-economy-workbook.py --check    verifies the source matches the workbook
"""

import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(REPO, "outputs", "4b7976f0-1820-4ffa-a191-bf7c7f79b010",
                        "Rimrooms_Campaign_Economy_v0.2.xlsx")
SOURCE = os.path.join(REPO, "docs", "research", "campaign-economy-workbook.json")
HTML = os.path.join(REPO, "outputs", "readable", "campaign-economy.html")

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def column_index(reference):
    """`C7` -> 2. Letters are base-26 with no zero, so `AA` is 26 rather than 0."""
    letters = re.match(r"([A-Z]+)", reference or "")
    if not letters:
        return 0
    index = 0
    for character in letters.group(1):
        index = index * 26 + (ord(character) - ord("A") + 1)
    return index - 1


def shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    found = []
    for item in root.findall("m:si", NS):
        # A string can be split across several runs when part of it is styled, so every `t`
        # under the item is joined rather than only the first.
        found.append("".join(node.text or "" for node in item.iter(
            "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
    return found


def sheet_rows(archive, part, strings):
    root = ET.fromstring(archive.read(part))
    rows = []
    for row in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
        cells = {}
        for cell in row.findall("m:c", NS):
            reference = cell.get("r")
            kind = cell.get("t")
            value_node = cell.find("m:v", NS)
            inline = cell.find("m:is", NS)
            if kind == "s" and value_node is not None:
                try:
                    value = strings[int(value_node.text)]
                except (ValueError, IndexError):
                    value = ""
            elif kind == "inlineStr" and inline is not None:
                value = "".join(node.text or "" for node in inline.iter(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
            elif value_node is not None:
                value = value_node.text or ""
            else:
                value = ""
            if value != "":
                cells[column_index(reference)] = value
        if not cells:
            rows.append([])
            continue
        width = max(cells) + 1
        rows.append([cells.get(index, "") for index in range(width)])
    while rows and not rows[-1]:
        rows.pop()
    return rows


def workbook():
    """Every sheet, by its real name, in the workbook's own order."""
    if not os.path.isfile(WORKBOOK):
        sys.stderr.write("the workbook is not at %s\n" % WORKBOOK)
        sys.exit(2)
    with zipfile.ZipFile(WORKBOOK) as archive:
        strings = shared_strings(archive)
        # Sheet names live in workbook.xml and the files they map to live in the rels, so the
        # two have to be joined. Reading the files in name order would guess the order wrong the
        # moment a sheet is inserted rather than appended.
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {}
        for relationship in rels:
            targets[relationship.get("Id")] = relationship.get("Target")
        sheets = []
        for sheet in book.find("m:sheets", NS):
            rid = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/"
                            "relationships}id")
            target = targets.get(rid, "")
            part = "xl/" + target.lstrip("/")
            if part not in archive.namelist():
                part = "xl/worksheets/" + os.path.basename(target)
            if part not in archive.namelist():
                continue
            sheets.append({"name": sheet.get("name"),
                           "rows": sheet_rows(archive, part, strings)})
    return sheets


def render(sheets):
    out = []
    out.append("<!DOCTYPE html>")
    out.append('<html lang="en"><head><meta charset="utf-8">')
    out.append("<title>Rimrooms campaign economy workbook, transcribed</title>")
    # No authored colour and no authored font size, for the same reason the in-game readouts set
    # neither: the reader's own browser settings should apply.
    out.append("<style>body{font-family:system-ui,sans-serif;margin:2rem;max-width:80rem}"
               "table{border-collapse:collapse;margin-bottom:2rem;width:100%}"
               "th,td{border:1px solid currentColor;padding:.3rem .5rem;text-align:left;"
               "vertical-align:top}caption{text-align:left;font-weight:700;padding:.5rem 0}"
               "blockquote{border-left:4px solid currentColor;padding-left:1rem}</style>")
    out.append("</head><body>")
    out.append("<h1>Rimrooms campaign economy workbook, transcribed</h1>")
    out.append("<blockquote><p><strong>These numbers are transcribed, not verified.</strong> "
               "This page is a faithful reading of "
               "<code>Rimrooms_Campaign_Economy_v0.2.xlsx</code> and nothing in it has been "
               "reconciled against the build. The workbook is a separate dataset with its own "
               "authorship; a generator that corrected a figure would destroy the only useful "
               "property it has, which is being what its author wrote.</p>"
               "<p>Generated by <code>tools/extract-economy-workbook.py</code> from the tracked "
               "source at <code>docs/research/campaign-economy-workbook.json</code>. No game has "
               "ever been launched from this repository, so none of these figures has been "
               "observed in play.</p></blockquote>")
    out.append("<p>%d sheet(s): %s</p>"
               % (len(sheets), ", ".join(escape(sheet["name"]) for sheet in sheets)))
    for sheet in sheets:
        rows = sheet["rows"]
        out.append("<table><caption>%s &mdash; %d row(s)</caption>"
                   % (escape(sheet["name"]), len(rows)))
        for number, row in enumerate(rows):
            if not row:
                continue
            tag = "th" if number == 0 else "td"
            out.append("<tr>" + "".join("<%s>%s</%s>" % (tag, escape(cell), tag)
                                        for cell in row) + "</tr>")
        out.append("</table>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def escape(value):
    return (str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    sheets = workbook()
    payload = {
        "note": "Transcribed from Rimrooms_Campaign_Economy_v0.2.xlsx by "
                "tools/extract-economy-workbook.py. Not verified against the build, and not "
                "observed in play.",
        "workbook": os.path.relpath(WORKBOOK, REPO).replace(os.sep, "/"),
        "sheets": sheets,
    }
    serialised = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n"

    if "--check" in sys.argv:
        if not os.path.isfile(SOURCE):
            print("FAIL: %s does not exist; run the generator"
                  % os.path.relpath(SOURCE, REPO).replace(os.sep, "/"))
            return 1
        on_disk = io.open(SOURCE, encoding="utf-8").read()
        if on_disk != serialised:
            print("FAIL: the tracked source no longer matches the workbook. Re-run "
                  "tools/extract-economy-workbook.py")
            return 1
        print("economy workbook: tracked source matches the workbook (%d sheets, %d rows)"
              % (len(sheets), sum(len(s["rows"]) for s in sheets)))
        return 0

    io.open(SOURCE, "w", encoding="utf-8", newline="").write(serialised)
    io.open(HTML, "w", encoding="utf-8", newline="").write(render(sheets))
    print("economy workbook transcribed: %d sheets, %d rows"
          % (len(sheets), sum(len(s["rows"]) for s in sheets)))
    print("  source : %s" % os.path.relpath(SOURCE, REPO).replace(os.sep, "/"))
    print("  html   : %s" % os.path.relpath(HTML, REPO).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
