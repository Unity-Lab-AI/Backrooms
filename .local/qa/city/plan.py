"""Crashlanded city master plan -- districts with real floor plans, composed symmetrically about x = 128.

    python .local/qa/city/plan.py      -> plan.json, plan.txt, plan.png

Every room is a rectangle (outer wall line inclusive). Districts on the west are mirrored in
SHAPE on the east (x -> 256 - x) but carry their own use, so the city reads symmetrical while
each district is laid out for what it does.
"""
import json, os

AX = 128
def mx(x): return 2 * AX - x

rooms = []
def room(name, x0, z0, x1, z1, use, mirror_name=None, mirror_use=None, door=None, mdoor=None):
    rooms.append(dict(name=name, x0=x0, z0=z0, x1=x1, z1=z1, use=use, door=door))
    if mirror_name:
        md = mdoor if mdoor else ([mx(door[0]), door[1]] if door else None)
        rooms.append(dict(name=mirror_name, x0=mx(x1), z0=z0, x1=mx(x0), z1=z1, use=mirror_use, door=md))

# ---------------- perimeter -------------------------------------------------------------
PER = dict(x0=86, z0=140, x1=170, z1=212)

# ---------------- south: gatehouse, office, security --------------------------------------
room("Gatehouse / killbox", 122, 140, 134, 150, "entry killbox: barricades, turrets, embrasures; outer gate z140, inner gate z150", door=[128, 150])
room("Office", 96, 142, 118, 154, "comms console, trade beacons, operations desk, ledger", "Security HQ", "armory, guard post, turret control; vault behind it", door=[118, 148])
room("Records annex", 104, 142, 109, 147, "records shelves (company books)", "Vault", "VAULT -- silver, gold, gems, ivory, serum; one door, from Security only", door=[106, 147])

# ---------------- middle: homes west, factory east ---------------------------------------
room("Home district", 88, 158, 120, 174, "colonist homes: 3-wide hall z165-167 (owner: no single-width hallways), bedrooms 6x5 both sides", "Factory", "factory floor: storehouse 136-148 (built first), workshop hall 149-168 mined into the mountain", door=[120, 166])
for i, x in enumerate(range(89, 119, 6)):
    room("Bedroom S%d" % (i + 1), x, 158, x + 6, 164, "bedroom", "Factory bay S%d" % (i + 1), "factory bay", door=[x + 3, 164])
    room("Bedroom N%d" % (i + 1), x, 168, x + 6, 174, "bedroom", "Factory bay N%d" % (i + 1), "factory bay", door=[x + 3, 168])

# ---------------- centre: palace ---------------------------------------------------------
room("Throne hall", 120, 174, 136, 188, "THRONE ROOM: throne north centre, columns, carpet, braziers", door=[128, 174])
room("Altar room", 112, 174, 119, 188, "altar / ideogram, ritual spot", "Royal suites", "royal bedrooms (2 suites 7x7): king and royal", door=[119, 181])

# ---------------- west/east flanks of the palace: guests vs prison -----------------------
room("Guest quarter", 88, 174, 110, 188, "single beautified guest rooms (bed prices set), guest dining", "Prison", "SECURE PRISON: cells off a central guarded hall, prison commons, double walls, one sally port", door=[110, 181])
room("Store", 88, 174, 97, 188, "shop / sell zone for guests", "Prison commons", "prison commons / work room (Prison Labor)", door=[97, 181])

# ---------------- north: the massive lab, hospital, cloning ------------------------------
room("THE LAB", 108, 192, 148, 210, "MASSIVE LAB: hi-tech benches in rows, multi-analyzers, server racks, records; north is the lab head's office", door=[128, 192])
room("Hospital", 88, 192, 106, 210, "hospital: sterile tile, hospital beds, vitals monitors, medicine shelf", "Cloning lab", "CLONING LAB (Questionable Ethics): grower vats, genome sequencer, nutrient storage", door=[106, 201])

# ---------------- avenue & ring ------------------------------------------------------------
AVENUE = dict(x0=124, z0=151, x1=132, z1=173, note="grand avenue, unroofed, from gatehouse to throne hall")
RING = dict(z0=189, z1=191, note="3-wide ring corridor between palace row and lab row")

# ---------------- walls ------------------------------------------------------------------
walls, doors = set(), set()
def ring(r, target):
    for x in range(r["x0"], r["x1"] + 1):
        target.add((x, r["z0"])); target.add((x, r["z1"]))
    for z in range(r["z0"], r["z1"] + 1):
        target.add((r["x0"], z)); target.add((r["x1"], z))
ring(PER, walls)
for r in rooms:
    ring(r, walls)
for r in rooms:
    if r.get("door"):
        doors.add(tuple(r["door"]))
for x in range(126, 131):  # outer gate in the perimeter
    doors.add((x, 140))
walls -= doors

# Re-seat the whole plan on another map: CITY_OX / CITY_OZ shift every cell, CITY_TAG names the output.
OX, OZ = int(os.environ.get("CITY_OX", 0)), int(os.environ.get("CITY_OZ", 0))
TAG = os.environ.get("CITY_TAG", "")
def shift_rect(r):
    r = dict(r)
    for k in ("x0", "x1"):
        if k in r: r[k] += OX
    for k in ("z0", "z1"):
        if k in r: r[k] += OZ
    if r.get("door"): r["door"] = [r["door"][0] + OX, r["door"][1] + OZ]
    return r
PER, AVENUE, RING = shift_rect(PER), shift_rect(AVENUE), shift_rect(RING)
rooms = [shift_rect(r) for r in rooms]
walls = {(x + OX, z + OZ) for x, z in walls}
doors = {(x + OX, z + OZ) for x, z in doors}

here = os.path.dirname(os.path.abspath(__file__))
json.dump({"perimeter": PER, "avenue": AVENUE, "ring": RING, "rooms": rooms, "shift": [OX, OZ],
           "walls": sorted(map(list, walls)), "doors": sorted(map(list, doors))},
          open(os.path.join(here, "plan%s.json" % TAG), "w"), indent=1)
print(len(walls), "walls", len(doors), "doors", len(rooms), "rooms")
try:
    from PIL import Image, ImageDraw
    S = 8
    im = Image.new("RGB", ((PER["x1"] - PER["x0"] + 3) * S, (PER["z1"] - PER["z0"] + 3) * S), (30, 30, 30))
    d = ImageDraw.Draw(im)
    def P(x, z): return ((x - PER["x0"] + 1) * S, (PER["z1"] - z + 1) * S)
    for x, z in walls: d.rectangle([P(x, z), (P(x, z)[0] + S - 1, P(x, z)[1] + S - 1)], fill=(200, 200, 200))
    for x, z in doors: d.rectangle([P(x, z), (P(x, z)[0] + S - 1, P(x, z)[1] + S - 1)], fill=(220, 140, 40))
    for r in rooms:
        if r["x1"] - r["x0"] >= 10:
            d.text((P(r["x0"] + 1, r["z1"] - 1)), r["name"], fill=(120, 220, 255))
    im.save(os.path.join(here, "plan%s.png" % TAG))
except ImportError:
    pass
