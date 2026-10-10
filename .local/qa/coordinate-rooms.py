"""List a coordinate's rooms from the newest save: index, family, rect, surveyed.

    python .local/qa/coordinate-rooms.py AI-03 [save-name-prefix]
Marks the first room of each family, which is the one a survey's required room observation reads.
"""
import glob, os, re, sys
import xml.etree.ElementTree as ET

label = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else "rimbridge_save_"
saves = glob.glob(os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Ludeon Studios",
                               "RimWorld by Ludeon Studios", "Saves", prefix + "*.rws"))
path = max(saves, key=os.path.getmtime)
print("save:", os.path.basename(path))
root = ET.parse(path).getroot()
for node in root.iter("li"):
    if node.findtext("rr_label") != label or node.find("rr_rooms") is None:
        continue
    seen = set()
    for i, room in enumerate(node.find("rr_rooms").findall("li")):
        index = int(room.findtext("rr_index") or i)
        family = room.findtext("rr_familyId")
        x, z = int(room.findtext("rr_x")), int(room.findtext("rr_z"))
        w, h = int(room.findtext("rr_width")), int(room.findtext("rr_height"))
        first = family not in seen
        seen.add(family)
        print("%3d %-18s x%d z%d %dx%d surveyed=%s%s" % (index, family, x, z, w, h,
              room.findtext("rr_surveyed") or "False", "  FIRST" if first else ""))
    break
