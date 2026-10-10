"""One-off: lift the six analysis columns that live ONLY inside the orphan workbook
into a repo-tracked CSV. After this runs the workbook holds nothing unique."""
import csv
import json
import os

ROOT = r"C:\Users\gfour\Desktop\Backrooms"
data = json.load(open(os.path.join(ROOT, ".local", "register", "extract.json"), encoding="utf-8"))
reg = data["register"]

# Column numbers in the workbook's "Mod Register" sheet.
ANALYSIS = [
    (6, "SystemFamily"),
    (7, "BackroomsDependency"),
    (8, "PlannedUse"),
    (9, "IntegrationApproach"),
    (10, "CompatibilityWatch"),
    (11, "ResearchStatus"),
]

inventory = list(csv.DictReader(
    open(os.path.join(ROOT, "docs", "research", "rimworld-server-mod-inventory.csv"), encoding="utf-8-sig")))
by_order = {r["LoadOrder"]: r for r in inventory}

out_path = os.path.join(ROOT, "docs", "research", "mod-register-integration-fields-2026-09-29.csv")
rows = []
for record in reg[1:]:
    cells = record[1]
    order = cells.get("1", "")
    source = by_order.get(order)
    if source is None:
        raise SystemExit("workbook load order %r is absent from the inventory" % order)
    if (cells.get("2", "") or "").strip() != (source["ModName"] or "").strip():
        raise SystemExit("name disagreement at load order %s" % order)
    row = {"LoadOrder": order, "ModID": source["ModID"], "ModName": source["ModName"]}
    for column, name in ANALYSIS:
        row[name] = (cells.get(str(column), "") or "").strip()
    rows.append(row)

rows.sort(key=lambda r: int(r["LoadOrder"]))
fields = ["LoadOrder", "ModID", "ModName"] + [name for _, name in ANALYSIS]
with open(out_path, "w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

print("wrote %s rows to %s" % (len(rows), out_path))
blank = {name: sum(1 for r in rows if not r[name]) for _, name in ANALYSIS}
print("blank counts:", blank)
