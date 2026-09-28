"""Read-only checks of Gate 0 reference integrity; no game, network, or workbook writes.

Run from any directory with Python 3: python tools/research/audit-gate0.py
Output is JSON on stdout. A nonzero exit means a structural mismatch was found.
This checks saved records, not source truth, gameplay, or compatibility.
"""
from collections import Counter
import csv
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "docs/research"
errors = []
counts = {}


def require(condition, message):
    if not condition:
        errors.append(message)


def rows(name):
    with (RESEARCH / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def prose(path):
    text = path.read_text(encoding="utf-8-sig")
    return re.sub(r"(?ms)^ *(`{3,}|~{3,}).*?^ *\1 *$", "", text)


def anchors(path):
    text = prose(path)
    ids = set(re.findall(r'<a\s+(?:id|name)=[\"\x27]([^\"\x27]+)', text))
    used = set()
    for heading in re.findall(r"(?m)^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", text):
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]+>", "", html.unescape(heading)).lower()
        slug = "".join(c for c in heading if c.isalnum() or c in " _-").replace(" ", "-")
        candidate, index = slug, 0
        while candidate in used:
            index += 1
            candidate = f"{slug}-{index}"
        used.add(candidate)
        ids.add(candidate)
    return ids


anchor_cache = {}


def check_link(origin, destination):
    if re.match(r"^[a-z][a-z0-9+.-]*:", destination, re.I) or destination.startswith("//"):
        return
    destination = unquote(html.unescape(destination.strip().strip("<>")))
    name, _, fragment = destination.partition("#")
    target = (origin.parent / name).resolve() if name else origin.resolve()
    require(target.is_relative_to(ROOT), f"Outside-repository link: {origin.relative_to(ROOT)} -> {destination}")
    require(target.exists(), f"Missing link: {origin.relative_to(ROOT)} -> {destination}")
    counts["local_link_occurrences"] = counts.get("local_link_occurrences", 0) + 1
    if fragment and target.is_file() and target.suffix == ".md":
        counts["markdown_fragment_occurrences"] = counts.get("markdown_fragment_occurrences", 0) + 1
        if target not in anchor_cache:
            anchor_cache[target] = anchors(target)
        require(fragment in anchor_cache[target], f"Missing anchor: {origin.relative_to(ROOT)} -> {destination}")


def markdown_links():
    files = sorted([*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md"), *(ROOT / "outputs").rglob("*.md")])
    counts["markdown_files"] = len(files)
    for file in files:
        text = prose(file)
        # Inline links, including balanced parentheses in local destinations.
        for match in re.finditer(r"!?\[[^\]\n]*\]\(", text):
            start, pos, depth = match.end(), match.end(), 1
            while pos < len(text) and depth:
                if text[pos] == "(" and (pos == 0 or text[pos - 1] != "\\"):
                    depth += 1
                elif text[pos] == ")" and text[pos - 1] != "\\":
                    depth -= 1
                pos += 1
            if depth == 0:
                destination = text[start:pos - 1].strip()
                destination = re.sub(r'\s+["\x27].*["\x27]$', "", destination)
                check_link(file, destination)
        for match in re.finditer(r"(?m)^ {0,3}\[[^]]+\]:\s*(<[^>]+>|\S+)", text):
            check_link(file, match.group(1))


def xlsx_rows(path, sheet_name):
    """Extract saved cell values with stdlib; intentionally does not recalculate."""
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    relns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            for item in ET.fromstring(archive.read("xl/sharedStrings.xml")):
                strings.append("".join(t.text or "" for t in item.iterfind(".//s:t", ns)))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheet = next(s for s in workbook.findall("s:sheets/s:sheet", ns) if s.attrib["name"] == sheet_name)
        relation_id = sheet.attrib[f"{{{relns}}}id"]
        relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = next(r.attrib["Target"] for r in relations if r.attrib["Id"] == relation_id)
        target = target.lstrip("/") if target.startswith("/") else "xl/" + target
        result = []
        for row in ET.fromstring(archive.read(target)).findall("s:sheetData/s:row", ns):
            cells = {}
            for cell in row:
                column = re.match(r"[A-Z]+", cell.attrib["r"]).group()
                index = 0
                for char in column:
                    index = index * 26 + ord(char) - 64
                value = cell.find("s:v", ns)
                value = value.text if value is not None else ""
                if cell.attrib.get("t") == "s":
                    value = strings[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(t.text or "" for t in cell.findall(".//s:t", ns))
                cells[index - 1] = value or ""
            result.append([cells.get(i, "") for i in range(max(cells, default=-1) + 1)])
        return result


def registers():
    inventory = rows("rimworld-server-mod-inventory.csv")
    metadata = rows("installed-mod-metadata-2026-09-27.csv")
    require(len(inventory) == len(metadata) == 294, "Inventory/metadata must contain 294 rows each")
    require([int(r["LoadOrder"]) for r in inventory] == list(range(1, 295)), "Inventory row numbers/order differ from 1..294")
    require(len({r["PackageID"].lower() for r in metadata}) == 294, "Metadata has duplicate package IDs")
    features = set(re.findall(r"^\| (RR-[A-Z]+) \|", (ROOT / "docs/FEATURE_TRACEABILITY.md").read_text(encoding="utf-8"), re.M))
    require(len(features) == 17, "Expected 17 feature IDs")
    counts["feature_ids"] = len(features)
    book = ROOT / "outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx"
    data = xlsx_rows(book, "Mod Register")
    sheet_rows = [dict(zip(data[0], row)) for row in data[1:] if row and row[0]]
    require(len(sheet_rows) == 294, "Workbook does not have 294 mod rows")
    mapping = {"LoadOrder": "Load order", "ModName": "Mod", "ModID": "Workshop ID / package ID", "Type": "Profile type", "WorkshopURL": "Workshop URL"}
    mapping.update({s: s for s in ["FeatureTraceIDs", "ReviewRecord", "ReviewStatus", "FinalDisposition", "EvidenceBuild", "AcceptanceEvidence"]})
    comparisons = 0
    for row, meta, sheet in zip(inventory, metadata, sheet_rows):
        key = row["LoadOrder"]
        require(row["ModID"] == meta["InventoryID"] and key == meta["LoadOrder"], f"Metadata identity differs at row {key}")
        for field, value in row.items():
            require(bool(value) or field == "WorkshopURL", f"Inventory row {key} missing {field}")
        for field, heading in mapping.items():
            comparisons += 1
            require(row[field] == sheet.get(heading, ""), f"Workbook mismatch row {key}, field {field}")
        # An explicit unrelated/no-touch disposition is an accepted mapping.
        tags = set(row["FeatureTraceIDs"].split(";"))
        require(tags <= features or tags == {"None—verified unrelated"}, f"Unknown feature ID at row {key}")
        review = ROOT / row["ReviewRecord"]
        require(review.is_file(), f"Missing review at row {key}")
        if review.is_file():
            text = review.read_text(encoding="utf-8-sig")
            require(meta["PackageID"].lower() in text.lower(), f"Review does not identify package at row {key}")
            require("https://" in text, f"Review has no source URL at row {key}")
            require(len(text.split()) >= 80, f"Review unusually short at row {key}; inspect content")
    counts.update(mod_rows=len(inventory), workbook_compared_cells=comparisons, review_records=len({r["ReviewRecord"] for r in inventory}))
    return inventory, metadata


def relationships(inventory, metadata):
    declared = rows("installed-mod-relationships-2026-09-27.csv")
    dispositions = rows("declared-relationship-disposition-matrix-2026-09-27.csv")
    require(len(declared) == len(dispositions) == 914, "Relationship exports must contain 914 records each")
    require(len({r["RelationshipID"] for r in dispositions}) == len(dispositions), "Duplicate relationship IDs")
    for index, (source, decision) in enumerate(zip(declared, dispositions), 1):
        require(str(index) == decision["RelationshipCSVRecordOrdinal"], f"Relationship ordinal differs at {index}")
        for field, value in source.items():
            target = "RelationshipType" if field == "Relationship" else field
            require(value == decision.get(target), f"Relationship {index} differs: {field}")
        from_index = int(source["FromLoadOrder"]) - 1
        require(source["FromPackageID"].lower() == metadata[from_index]["PackageID"].lower(), f"Relationship {index} source package mismatch")
        require(source["EvidenceAboutXmlSHA256"] == metadata[from_index]["AboutXmlSHA256"], f"Relationship {index} metadata hash mismatch")
        require(decision["FromReviewRecord"] == inventory[from_index]["ReviewRecord"], f"Relationship {index} source review mismatch")
        for field in ["ProjectDisposition", "ProjectDispositionBasis", "InteractionTestCandidateBasis", "RuntimeTestStatus"]:
            require(bool(decision[field]), f"Relationship {index} has no {field}")
        if source["TargetInProfile"].lower() == "true":
            to_index = int(source["ToLoadOrder"]) - 1
            require(source["ToPackageID"].lower() == metadata[to_index]["PackageID"].lower(), f"Relationship {index} target package mismatch")
            require(decision["ToReviewRecord"] == inventory[to_index]["ReviewRecord"], f"Relationship {index} target review mismatch")
    internal = [r for r in declared if r["TargetInProfile"].lower() == "true"]
    types = dict(Counter(r["Relationship"] for r in internal))
    pairs = {(r["FromPackageID"].lower(), r["ToPackageID"].lower()) for r in internal}
    require(len(internal) == 602 and len(pairs) == 443, "Declared in-profile record/pair totals differ")
    require(types == {"Requires": 226, "LoadAfter": 371, "LoadBefore": 5}, "Declared in-profile type totals differ")
    counts.update(relationship_records=len(declared), in_profile_records=len(internal), unique_directed_pairs=len(pairs), in_profile_relationship_types=types)


def story_index():
    index = rows("kane-pixels-video-index.csv")
    require(len(index) == len({r["video_id"] for r in index}) == 23, "Story index must have 23 distinct uploads")
    for row in index:
        review = RESEARCH / "reviews/kane-pixels" / (row["video_id"] + ".md")
        require(review.is_file(), f"Missing story review {row['video_id']}")
        require(row["source_url"] == "https://www.youtube.com/watch?v=" + row["video_id"], f"Story source mismatch {row['video_id']}")
        check_link(RESEARCH / "kane-pixels-video-index.csv", row["fan_summary_record"])
    counts["indexed_story_records"] = len(index)


def main():
    markdown_links()
    inventory, metadata = registers()
    relationships(inventory, metadata)
    story_index()
    todo = (ROOT / "docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md").read_text(encoding="utf-8-sig")
    gate = todo.split("## Phase 0", 1)[1].split("## Phase 1", 1)[0]
    counts["gate0_open_boxes"] = len(re.findall(r"^- \[ \]", gate, re.M))
    require(counts["gate0_open_boxes"] == 0, "Gate 0 contains open checklist items")
    print(json.dumps({"scope": "Saved reference/record integrity only; no runtime or source-truth certification", "counts": counts, "errors": errors, "result": "PASS" if not errors else "FAIL"}, indent=2, ensure_ascii=True))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
