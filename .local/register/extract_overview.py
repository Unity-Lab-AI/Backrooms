"""One-off: lift the Overview sheet's narrative rows into tracked text.

The system-family tallies are deliberately NOT extracted. They are a count of the
SystemFamily column, so the generator computes them and they can never drift from
the rows they describe. Only the prose measures and the source links are facts
that live nowhere else.
"""
import csv
import json
import os

ROOT = r"C:\Users\gfour\Desktop\Backrooms"
data = json.load(open(os.path.join(ROOT, ".local", "register", "extract.json"), encoding="utf-8"))
rows = {r: c for r, c in data["overview"]}


def cell(row, column):
    return (rows.get(row, {}).get(str(column), "") or "").strip()


out = []
out.append({"Section": "title", "Label": cell(2, 1), "Value": ""})
out.append({"Section": "title", "Label": cell(3, 1), "Value": ""})
for row in range(6, 18):          # Measure / Result block
    out.append({"Section": "measure", "Label": cell(row, 1), "Value": cell(row, 2)})
for row in range(68, 80):         # Source and validation block
    out.append({"Section": "source", "Label": cell(row, 1), "Value": cell(row, 2)})

for record in out:
    if not record["Label"]:
        raise SystemExit("empty label in extracted overview: %r" % record)

path = os.path.join(ROOT, "docs", "research", "mod-register-overview-2026-09-29.csv")
with open(path, "w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["Section", "Label", "Value"],
                            quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    writer.writerows(out)
print("wrote %s overview rows to %s" % (len(out), path))
