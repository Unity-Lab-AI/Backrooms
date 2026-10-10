# -*- coding: utf-8 -*-
"""Author the Async Industries gate facility, computed rather than guessed.

Owner, 2026-10-01, verbatim: *"the company start needs a fulley connect and set up sweet ass
facility.. currently it looks like a 6yr old chimp made the facility as the gate is rfree standing
and it now weays looks like a working \"machine\" that should be designed intelligently with like
ballistic glass  walls for viewing the machine remotely and safely with security zones and shit and
lab rooms and shit i mean wtf is this this is a 50million dollar facilty"*.

The old layout was a 44x44 rectangle with eight boxes stamped in it and the furniture listed flat.
This replaces it with a facility that has a plan:

    z=51  +------------------------------------------------------------+ compound wall
          |                 north service corridor (z=50)              |
          |        +--------------------------------------+            |
          |        |            GATE HALL                 |            |
          |        |   the machine. deliberately empty.    |           |
          |        |   aperture door in the north wall     |           |
          |        +=====[ BALLISTIC GLASS ]===+==+========+            |
          |        |          |  AIRLOCK  |    |            |          |
          |        |  CONTROL ROOM, behind the glass        |          |
          |        +--------------------------------------+            |
          |            east-west service corridor (z=24)               |
          |  +--------+ +-----------+ +---------------+                |
          |  |  LABS  | |  SECURE   | |   WORKSHOP    |                |
          |  |        | |  STORAGE  | | machining     |                |
          |  +--------+ +-----------+ +---------------+                |
          |  +--------+ +-----------+ +---------------+                |
          |  | HOUSING| |   MESS    | |   MEDICAL     |                |
          |  +--------+ +-----------+ +---------------+                |
    z=8   +------------------------------------------------------------+

Why a script and not hand-written XML
-------------------------------------
`GenStep_Headquarters.Build` **throws** on any geometry mistake and a throw inside a GenStep costs
the player the start. This is several hundred authored cells. Every door here is computed from the
wall it belongs to, every fixture's footprint is taken from Core's own `<size>`, and
`tools/check-start-layout.py` re-validates the emitted XML offline afterwards -- so the geometry is
derived, checked, and checked again by something that did not write it.
"""
import io
import os
import re
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STARTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")
CORE = os.environ.get("RIMWORLD_PATH",
                      r"C:\Program Files (x86)\Steam\steamapps\common\Rimworld")

# --------------------------------------------------------------------------- Core footprints
def core_sizes():
    data = os.path.join(CORE, "Data", "Core", "Defs")
    by = {}
    for root, _dirs, files in os.walk(data):
        for name in files:
            if not name.lower().endswith(".xml"):
                continue
            try:
                tree = ET.parse(os.path.join(root, name))
            except ET.ParseError:
                continue
            for node in tree.getroot():
                if node.tag != "ThingDef":
                    continue
                record = {"size": node.findtext("size"), "parent": node.get("ParentName"),
                          "interaction": node.findtext("interactionCellOffset"),
                          "hasInteraction": node.findtext("hasInteractionCell") or ""}
                for handle in filter(None, [node.findtext("defName"), node.get("Name")]):
                    by[handle] = record
    return by


SIZES = core_sizes()


def size_of(name):
    seen, cursor = set(), name
    while cursor and cursor in SIZES and cursor not in seen:
        seen.add(cursor)
        record = SIZES[cursor]
        if record["size"]:
            numbers = re.findall(r"-?\d+", record["size"])
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
        cursor = record["parent"]
    return 1, 1


def adjust_for_rotation(cell, size, rotation):
    """Core's `GenAdj.AdjustForRotation`: an even dimension moves the centre before the rect.

    Decompiled from the installed 1.6 assembly. Without it a 3x2 console facing south reads as
    occupying the two rows NORTH of its position, which is how the owner's console appeared to
    overlap the viewing glass it is actually sitting against.
    """
    width, height = size
    if rotation % 2 == 1:
        width, height = height, width
    shift = {0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}[rotation % 4]
    x, z = cell
    if not (size[0] == 1 and size[1] == 1):
        if width % 2 == 0:
            x += shift[0]
        if height % 2 == 0:
            z += shift[1]
    return (x, z), (width, height)


def interaction_cell(cell, offset, rotation):
    """Core's `ThingUtility.InteractionCellWhenAt`: position plus the offset, rotated."""
    ox, oz = offset
    rotation %= 4
    if rotation == 0:
        dx, dz = ox, oz
    elif rotation == 1:
        dx, dz = oz, -ox
    elif rotation == 2:
        dx, dz = -ox, -oz
    else:
        dx, dz = -oz, ox
    return (cell[0] + dx, cell[1] + dz)


def interaction_of(name):
    """(offset, has) for a def, walking ParentName like the size lookup does."""
    seen, cursor, offset, has = set(), name, None, False
    while cursor and cursor in SIZES and cursor not in seen:
        seen.add(cursor)
        record = SIZES[cursor]
        if offset is None and record.get("interaction"):
            numbers = re.findall(r"-?\d+", record["interaction"])
            if len(numbers) >= 3:
                offset = (int(numbers[0]), int(numbers[2]))
        if record.get("hasInteraction", "").strip().lower() == "true":
            has = True
        cursor = record["parent"]
    return offset, has


def occupied(cell, size, rotation=0):
    (cx, cz), (width, height) = adjust_for_rotation(cell, size, rotation)
    min_x = cx - (width - 1) // 2
    min_z = cz - (height - 1) // 2
    return [(x, z) for x in range(min_x, min_x + width) for z in range(min_z, min_z + height)]


# --------------------------------------------------------------------------- the plan
# Every room is (x, z, width, height); walls are the perimeter, interiors the rest. Adjacent
# rooms share a wall line; nested rooms are partitions. Authored for a 60-cell map: the span is
# 44 and Core's edge margin is 8 on each side, which is exactly 60.
ROOMS = [
    # name          x   z   w   h  roofed floor
    ("compound",     8,  8, 44, 44, True,  True),
    ("gatehall",    28, 34, 22, 16, True,  True),
    ("control",     28, 25, 22, 10, True,  True),
    ("airlock",     36, 30,  7,  5, True,  True),
    ("labs",         8, 14, 14, 10, True,  True),
    ("storage",     23, 14, 13, 10, True,  True),
    ("workshop",    37, 14, 15, 10, True,  True),
    ("housing",      8,  8, 14,  7, True,  True),
    ("mess",        23,  8, 13,  7, True,  True),
    ("medical",     37,  8, 15,  7, True,  True),
    # **The western wing, and it is not decoration.** The first authoring left x15..27 by z30..44
    # as one roofed void: `proof-startplacement.py` found 121 cells beyond roof support, and an
    # unsupported roof drops on the pawn who deconstructs the wall holding it. Rooms here leave a
    # nine-cell corridor, which is inside support range from both sides.
    ("security",     8, 25, 11,  9, True,  True),
    ("decon",        8, 34, 11,  9, True,  True),
    ("archive",      8, 43, 11,  8, True,  True),
    # **A POWER ROOM, and a BREEZEWAY for the generators.** Owner, 2026-10-01: *"actuall make
    # onbe of the rooms a power room and where the generators are should be a breeze way thats
    # unroffeced area complete just that area they are in thats inclose by walls and doors"*.
    #
    # The breezeway is the only room in the facility with `roofed: false`, and it is walled and
    # doored like any other: a fuel generator in a sealed room cooks the room, and venting it to
    # the sky while keeping it inside the compound is exactly what a breezeway is for. Both sit
    # east of the x19..21 corridor, which stays open from the service corridor to the north strip.
    ("powerroom",   22, 25,  6,  8, True,  True),
    ("breezeway",   22, 34,  6,  8, False, True),
]

# Columns in the gate hall. Its interior is twenty cells across, so every cell near the middle is
# out of range of all four perimeter walls. A hall for a large machine has columns in it anyway.
PILLARS = [(35, 39), (42, 39), (35, 44), (42, 44)]

# Doors, each on a wall cell. The two airlock doors are automatic: an airlock is two thresholds
# in series through a vestibule, and both being automatic is what makes it a controlled crossing
# rather than two doors somebody left open.
DOORS = [
    (8, 24),    # main entrance, compound west wall -> the east-west service corridor
    (14, 23),   # labs      -> corridor
    (29, 23),   # storage   -> corridor
    (44, 23),   # workshop  -> corridor
    (39, 25),   # control   -> corridor
    (21, 11),   # housing   -> north-south corridor at x=22
    (23, 11),   # mess      -> x=22
    (35, 11),   # mess      -> x=36
    (37, 11),   # medical   -> x=36
    (14, 25),   # security  -> east-west corridor
    (18, 29),   # security  -> west corridor
    (18, 38),   # decon     -> west corridor
    (18, 46),   # archive   -> west corridor
    # The one opening the owner had to cut themselves, found by diffing live doors against
    # authored ones with the facility origin solved at (120, 120): the compound's EAST
    # PERIMETER WALL at the dead end of the east-west service corridor. The corridor the
    # `((9, 24), 42, True)` conduit run follows was walled off at its east end, so there was no
    # way out of the facility on that side.
    (51, 24),   # service corridor -> outside, east perimeter
    (22, 29),   # power room -> west corridor
    (22, 37),   # breezeway  -> west corridor
    (21, 19),   # labs      -> x=22
    (23, 19),   # storage   -> x=22
    (35, 19),   # storage   -> x=36
    (37, 19),   # workshop  -> x=36
    (39, 30),   # control   -> AIRLOCK            (automatic)
    (39, 34),   # airlock   -> GATE HALL          (automatic)
    (39, 49),   # the aperture: gate hall -> north service corridor
]
AUTODOORS = [(39, 30), (39, 34)]

# The viewing walls: the gate hall's south wall, which is also the control room's north wall.
# Two runs, clear of the vestibule's own corners (x=36, x=42) and of the airlock door at x=39.
GLAZING = [
    ((30, 34), 6, True),    # x 30..35
    ((43, 34), 5, True),    # x 43..47
]
GLASS_DEFS = ["RB_ReinforcedGlassWall", "RB_GlassWall"]
GLASS_STUFF = ["Steel"]

# Fixtures, by room, as (def, cell, extras). Placed on interior cells only; every footprint is
# checked against Core's own size below before anything is written.
BUILDINGS = [
    # --- control room: the people who run the machine, behind the glass
    # **WHERE THE OWNER PUT THEM.** 2026-10-01: *"do u see where i moved the comms to and the
    # machining bench thats where i want them so fix there spawn position"*. Read out of
    # `Autosave-3.rws` and converted by the layout offset of (120,120) on their 300-cell map.
    #
    # Facing SOUTH, against the viewing glass: `GenAdj.AdjustForRotation` moves an even-depth
    # building's centre one cell south, so a 3x2 console at (32,33) occupies z32..33 and does NOT
    # touch the glass at z=34. Its interaction cell is (32,31), so the operator stands inside the
    # control room looking north at the console, which looks into the gate hall.
    ("CommsConsole",        (32, 33), {"rotation": 2}),
    # The gate assembly bench, in the control room where the owner moved it.
    ("TableMachining",      (45, 33), {}),
    ("Table1x2c",           (45, 27), {"stuff": "WoodLog"}),
    ("DiningChair",         (44, 27), {"stuff": "WoodLog"}),
    ("DiningChair",         (46, 27), {"stuff": "WoodLog"}),
    ("StandingLamp",        (30, 27), {}),
    ("StandingLamp",        (47, 27), {}),
    ("StandingLamp",        (30, 32), {}),
    ("StandingLamp",        (47, 32), {}),
    ("Heater",              (34, 32), {}),
    # --- gate hall: lit, warmed, and otherwise EMPTY. A machine hall with furniture in it is a
    #     room; the emptiness is what makes it read as a hall for a machine.
    ("StandingLamp",        (31, 37), {}),
    ("StandingLamp",        (46, 37), {}),
    ("StandingLamp",        (31, 46), {}),
    ("StandingLamp",        (46, 46), {}),
    ("Heater",              (33, 37), {}),
    ("Heater",              (44, 37), {}),
    # --- workshop: the machining table the gate assembly is built on
    ("ElectricSmithy",      (46, 16), {}),
    ("Shelf",               (39, 21), {"stuff": "WoodLog"}),
    ("Shelf",               (42, 21), {"stuff": "WoodLog"}),
    ("Shelf",               (45, 21), {"stuff": "WoodLog"}),
    ("StandingLamp",        (49, 19), {}),
    ("Heater",              (49, 16), {}),
    # --- lab wing
    ("SimpleResearchBench", (12, 16), {"stuff": "Steel"}),
    ("SimpleResearchBench", (17, 16), {"stuff": "Steel"}),
    ("Shelf",               (10, 21), {"stuff": "WoodLog"}),
    ("Shelf",               (13, 21), {"stuff": "WoodLog"}),
    ("Shelf",               (16, 21), {"stuff": "WoodLog"}),
    ("StandingLamp",        (19, 19), {}),
    ("Heater",              (19, 16), {}),
    # --- secure storage
    ("Shelf",               (25, 16), {"stuff": "WoodLog"}),
    ("Shelf",               (28, 16), {"stuff": "WoodLog"}),
    ("Shelf",               (31, 16), {"stuff": "WoodLog"}),
    ("Shelf",               (25, 21), {"stuff": "WoodLog"}),
    ("Shelf",               (28, 21), {"stuff": "WoodLog"}),
    ("Shelf",               (31, 21), {"stuff": "WoodLog"}),
    ("GlowPod",             (33, 16), {}),
    ("GlowPod",             (33, 17), {}),
    ("GlowPod",             (33, 18), {}),
    ("GlowPod",             (33, 19), {}),
    ("GlowPod",             (33, 20), {}),
    ("GlowPod",             (33, 21), {}),
    ("GlowPod",             (24, 16), {}),
    ("GlowPod",             (24, 17), {}),
    ("StandingLamp",        (34, 21), {}),
    # --- housing
    ("Bed",                 (10, 10), {"stuff": "WoodLog"}),
    ("Bed",                 (12, 10), {"stuff": "WoodLog"}),
    ("Bed",                 (14, 10), {"stuff": "WoodLog"}),
    ("Bed",                 (16, 10), {"stuff": "WoodLog"}),
    ("Bed",                 (18, 10), {"stuff": "WoodLog"}),
    ("StandingLamp",        (20, 12), {}),
    ("Heater",              (20, 10), {}),
    # --- mess
    ("ElectricStove",       (26, 10), {}),
    ("Table2x2c",           (30, 10), {"stuff": "WoodLog"}),
    ("Stool",               (29, 10), {"stuff": "WoodLog"}),
    ("Stool",               (32, 10), {"stuff": "WoodLog"}),
    ("Stool",               (30, 12), {"stuff": "WoodLog"}),
    ("Stool",               (31, 12), {"stuff": "WoodLog"}),
    ("StandingLamp",        (34, 12), {}),
    ("Heater",              (24, 12), {}),
    # --- medical
    ("Bed",                 (40, 10), {"stuff": "WoodLog", "medical": True}),
    ("Bed",                 (42, 10), {"stuff": "WoodLog", "medical": True}),
    ("Shelf",               (45, 10), {"stuff": "WoodLog"}),
    ("StandingLamp",        (49, 12), {}),
    ("Heater",              (49, 10), {}),
    # --- security office
    ("StandingLamp",        (10, 27), {}),
    ("StandingLamp",        (16, 27), {}),
    ("Shelf",               (10, 31), {"stuff": "WoodLog"}),
    ("Heater",              (16, 31), {}),
    # --- decontamination and lockers
    ("StandingLamp",        (10, 36), {}),
    ("StandingLamp",        (16, 36), {}),
    ("Shelf",               (10, 40), {"stuff": "WoodLog"}),
    ("Shelf",               (13, 40), {"stuff": "WoodLog"}),
    # --- records archive
    ("StandingLamp",        (10, 45), {}),
    ("StandingLamp",        (16, 45), {}),
    ("Shelf",               (10, 48), {"stuff": "WoodLog"}),
    ("Shelf",               (13, 48), {"stuff": "WoodLog"}),
    ("Shelf",               (16, 48), {"stuff": "WoodLog"}),
    # --- the power room: the battery bank, off the gate's own circuit
    ("Battery",             (23, 27), {"batteryFraction": 0.6}),
    ("Battery",             (25, 27), {"batteryFraction": 0.6}),
    ("Battery",             (23, 30), {"batteryFraction": 0.6}),
    ("Battery",             (25, 30), {"batteryFraction": 0.6}),
    ("StandingLamp",        (26, 26), {}),
    # --- the breezeway: generators under open sky, walled and doored
    ("WoodFiredGenerator",  (23, 36), {"fuelFraction": 0.5}),
    ("WoodFiredGenerator",  (25, 39), {"fuelFraction": 0.5}),
    # --- the corridor nook between them
    ("HorseshoesPin",       (20, 33), {"stuff": "Steel"}),
    # --- the archive: THE RECORD BOOKS, without which no expedition can be dispatched
    #
    # `ExpeditionCargo.RecordBooksRequired` is 1, of Core's `TextBook`. The start shipped none,
    # so `RR_Exp_MissingRecordBook` refused the first dispatch on every fresh laboratory start.
    # Owner, from a running game: *"if i use approach gate and dispach to coordinate it says no
    # book, i have no books"*.
    #
    # The recorder was folded into the book at 0.12.24-dev and the stock was never updated to
    # carry one. **Two**: one to take into the field, one in reserve, because a branch that
    # loses its only book cannot work until it makes another.
    ("TextBook",            (11, 47), {}),
    ("TextBook",            (14, 47), {}),
]

# Power: a spine along both service corridors, a column into each wing, and a run up the middle
# of the gate block. A conduit may sit under a wall or a door, which is how the runs cross them.
CONDUITS = [
    ((9, 24), 42, True),    # the east-west service corridor
    ((22, 9), 15, False),   # x=22 column
    ((36, 9), 15, False),   # x=36 column
    ((14, 15), 9, False),   # labs
    ((29, 15), 9, False),   # storage
    ((44, 15), 9, False),   # workshop
    ((14, 9), 6, False),    # housing
    ((29, 9), 6, False),    # mess
    ((44, 9), 6, False),    # medical
    ((39, 25), 10, False),  # control room, through the airlock
    ((39, 35), 14, False),  # gate hall
    ((23, 26), 8, False),   # the power room, through its north wall
    ((23, 34), 7, False),   # the breezeway
    ((14, 26), 8, False),    # security
    ((14, 35), 8, False),    # decon
    ((14, 44), 7, False),    # archive
    ((20, 25), 26, False),   # the west corridor spine
]

ARRIVAL = (39, 29)
STOCK = (27, 19)


# --------------------------------------------------------------------------- derive and verify
def walls_and_interiors():
    walls, interiors = set(), set()
    for (_name, x, z, w, h, _r, _f) in ROOMS:
        max_x, max_z = x + w - 1, z + h - 1
        for cx in range(x, max_x + 1):
            for cz in range(z, max_z + 1):
                if cx in (x, max_x) or cz in (z, max_z):
                    walls.add((cx, cz))
                else:
                    interiors.add((cx, cz))
    return walls, interiors


def verify():
    walls, interiors = walls_and_interiors()
    errors = []
    seen_doors = set()
    for cell in DOORS:
        if cell in seen_doors:
            errors.append("duplicate door %s" % (cell,))
        seen_doors.add(cell)
        if cell not in walls:
            errors.append("door %s is not on a wall" % (cell,))
    for cell in AUTODOORS:
        if cell not in seen_doors:
            errors.append("autodoor %s is not a door" % (cell,))
    glazed = set()
    for (start, length, along_x) in GLAZING:
        for step in range(length):
            cell = (start[0] + (step if along_x else 0), start[1] + (0 if along_x else step))
            if cell not in walls:
                errors.append("glazing %s is not on a wall" % (cell,))
            if cell in seen_doors:
                errors.append("glazing %s is also a door" % (cell,))
            glazed.add(cell)
    taken = {}
    for cell in PILLARS:
        if cell not in interiors:
            errors.append("pillar %s is not inside a room" % (cell,))
        if cell in seen_doors:
            errors.append("pillar %s is a door" % (cell,))
        taken[cell] = ("pillar", cell)
    for (thing, cell, extras) in BUILDINGS:
        rotation = extras.get("rotation", 0)
        offset, has_interaction = interaction_of(thing)
        if has_interaction and offset is not None:
            spot = interaction_cell(cell, offset, rotation)
            if spot not in interiors:
                errors.append("%s at %s cannot be used: its interaction cell %s is not free "
                              "interior" % (thing, cell, spot))
        for occupied_cell in occupied(cell, size_of(thing), rotation):
            if occupied_cell in walls:
                errors.append("%s at %s covers wall %s" % (thing, cell, occupied_cell))
            elif occupied_cell not in interiors:
                errors.append("%s at %s covers %s, outside every room" % (thing, cell, occupied_cell))
            if occupied_cell in taken:
                errors.append("%s at %s overlaps %s at %s" % (thing, cell, taken[occupied_cell][0],
                                                              taken[occupied_cell][1]))
            taken[occupied_cell] = (thing, cell)
    for name, cell in (("arrival", ARRIVAL), ("stock", STOCK)):
        if cell not in interiors:
            errors.append("%s cell %s is not inside a room" % (name, cell))
        if cell in taken:
            errors.append("%s cell %s is under %s" % (name, cell, taken[cell][0]))
    return errors, len(glazed), len(taken)


# --------------------------------------------------------------------------- emit
def emit():
    out = []
    a = out.append
    a("    <mapSize>60</mapSize>")
    a("    <outdoorTerrain>Soil</outdoorTerrain>")
    a("    <floorTerrain>Concrete</floorTerrain>")
    a("    <wallStuff>BlocksGranite</wallStuff>")
    a("    <arrivalCell>(%d, 0, %d)</arrivalCell>" % ARRIVAL)
    a("    <stockCell>(%d, 0, %d)</stockCell>" % STOCK)
    a("    <!-- The facility, as a plan rather than eight boxes in a rectangle. Owner direction")
    a("         2026-10-01. Authored by .local/register/build-async-facility.py and re-validated")
    a("         offline by tools/check-start-layout.py, because GenStep_Headquarters throws on any")
    a("         geometry mistake and a throw there costs the player the start. -->")
    a("    <rooms>")
    for (name, x, z, w, h, roofed, floor) in ROOMS:
        a("      <!-- %s -->" % name)
        a("      <li><x>%d</x><z>%d</z><width>%d</width><height>%d</height>"
          "<roofed>%s</roofed><floor>%s</floor></li>"
          % (x, z, w, h, str(roofed).lower(), str(floor).lower()))
    a("    </rooms>")
    a("    <doors>")
    for cell in DOORS:
        a("      <li>(%d, 0, %d)</li>" % cell)
    a("    </doors>")
    a("    <!-- The airlock between the control room and the gate hall: two thresholds in series")
    a("         through a vestibule, both automatic. Owner: \"with security zones and shit\". -->")
    a("    <autodoors>")
    for cell in AUTODOORS:
        a("      <li>(%d, 0, %d)</li>" % cell)
    a("    </autodoors>")
    a("    <!-- The viewing wall. Owner: \"ballistic glass  walls for viewing the machine remotely")
    a("         and safely\". ReBuild: Doors and Corners is register row 185, stance Optional, and")
    a("         its Planned Use is verbatim \"use the construction and layout tools to create gate")
    a("         control, labs, secure storage, accommodation, service corridors\". Named as")
    a("         STRINGS so a profile without it gets a solid wall instead of a discarded def. -->")
    a("    <glazing>")
    for (start, length, along_x) in GLAZING:
        a("      <li>")
        a("        <start>(%d, 0, %d)</start><length>%d</length><alongX>%s</alongX>"
          % (start[0], start[1], length, str(along_x).lower()))
        a("        <thingDefNames>")
        for name in GLASS_DEFS:
            a("          <li>%s</li>" % name)
        a("        </thingDefNames>")
        a("        <stuffDefNames>")
        for name in GLASS_STUFF:
            a("          <li>%s</li>" % name)
        a("        </stuffDefNames>")
        a("      </li>")
    a("    </glazing>")
    a("    <!-- Columns. A roof is supported only within 6.9 cells of a wall and the gate hall is")
    a("         twenty across, so without these its middle is unsupported and collapses on the")
    a("         pawn who deconstructs the wall holding it. proof-startplacement.py caught exactly")
    a("         that on the first authoring of this facility. -->")
    a("    <pillars>")
    for cell in PILLARS:
        a("      <li>(%d, 0, %d)</li>" % cell)
    a("    </pillars>")
    a("    <buildings>")
    for (thing, cell, extras) in BUILDINGS:
        bits = ["<thing>%s</thing>" % thing]
        if "stuff" in extras:
            bits.append("<stuff>%s</stuff>" % extras["stuff"])
        bits.append("<cell>(%d, 0, %d)</cell>" % cell)
        if extras.get("rotation"):
            bits.append("<rotation>%d</rotation>" % extras["rotation"])
        if extras.get("medical"):
            bits.append("<medical>true</medical>")
        if "fuelFraction" in extras:
            bits.append("<fuelFraction>%s</fuelFraction>" % extras["fuelFraction"])
        if "batteryFraction" in extras:
            bits.append("<batteryFraction>%s</batteryFraction>" % extras["batteryFraction"])
        a("      <li>%s</li>" % "".join(bits))
    a("    </buildings>")
    a("    <conduits>")
    for (start, length, along_x) in CONDUITS:
        a("      <li><start>(%d, 0, %d)</start><length>%d</length><alongX>%s</alongX></li>"
          % (start[0], start[1], length, str(along_x).lower()))
    a("    </conduits>")
    return "\n".join(out)


def main():
    errors, glazed, cells = verify()
    if errors:
        print("LAYOUT REFUSED, %d problem(s):" % len(errors))
        for error in errors:
            print("  - %s" % error)
        raise SystemExit(1)
    print("layout verified: %d rooms, %d doors (%d automatic), %d glazed cells, %d fixture cells"
          % (len(ROOMS), len(DOORS), len(AUTODOORS), glazed, cells))

    text = io.open(STARTS, encoding="utf-8").read()
    # Replace everything from <mapSize> to </conduits> inside the Async start only.
    start_at = text.index("<defName>RR_AsyncIndustriesStart</defName>")
    open_at = text.index("    <mapSize>", start_at)
    close_at = text.index("    </conduits>", open_at) + len("    </conduits>")
    replaced = text[:open_at] + emit() + text[close_at:]
    io.open(STARTS, "w", encoding="utf-8", newline="").write(replaced)
    print("RR_Starts.xml rewritten for RR_AsyncIndustriesStart")


if __name__ == "__main__":
    main()
