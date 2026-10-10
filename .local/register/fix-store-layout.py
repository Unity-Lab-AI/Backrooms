# -*- coding: utf-8 -*-
"""Fix two real crashes in the store layout, and one wrong claim in the proof.

THE ASSERTION WAS WRONG (invariant 130, third time this session). It said a room's wall must
not land inside another room's interior. The generator does not care about interiors -- it
throws only when a wall lands where an EDIFICE already is:

    if (cell.GetEdifice(map) != null) { throw ... "wall intersects generated structure" }

An interior cell has no edifice. Interior rooms sitting inside an outer shell is exactly how
the Async Industries headquarters is built and has always worked. The real rule is that two
rooms must not share a wall CELL.

THE BUILDINGS WERE GENUINELY WRONG. A 2x2 WoodFiredGenerator at (36,22) occupies z=23, which
is the stockroom's south wall, and the same for the Battery. Both would have thrown at
new-game. Moved into clear interior.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ the real crashes
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Defs',
                 'RimroomsStartDefs', 'RR_Starts.xml')
sub(p,
    u'      <li><thing>WoodFiredGenerator</thing><cell>(36, 0, 22)</cell><fuelFraction>0.5</fuelFraction></li>\n'
    u'      <li><thing>Battery</thing><cell>(33, 0, 22)</cell><batteryFraction>0.4</batteryFraction></li>',
    u'      <li><thing>WoodFiredGenerator</thing><cell>(36, 0, 20)</cell><fuelFraction>0.5</fuelFraction></li>\n'
    u'      <li><thing>Battery</thing><cell>(33, 0, 17)</cell><batteryFraction>0.4</batteryFraction></li>')

# The shelf at (32,20) would now sit beside the generator rather than under it; keep it clear.
sub(p, u'      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(32, 0, 20)</cell></li>',
       u'      <li><thing>Shelf</thing><stuff>WoodLog</stuff><cell>(31, 0, 20)</cell></li>')

# ------------------------------------------------------------------ the wrong claim
p = os.path.join(REPO, '.local', 'register', 'proof-starts.py')
sub(p, u"""    walls, interior, floors = set(), set(), set()
    overlap_fault = []
    for (x, z, w, h) in start["rooms"]:""",
u"""    #    The first version of the wall rule asserted that a room's wall must not land inside
    #    another room's interior, and it failed on a layout that is correct -- an interior room
    #    inside an outer shell, which is how the Async headquarters has always been built. THE
    #    ASSERTION WAS WRONG (invariant 130). `GenStep_Headquarters` throws only when a wall
    #    lands where an EDIFICE already is, and an interior cell has none. The real rule is that
    #    two rooms must not share a wall CELL.
    walls, interior, floors = set(), set(), set()
    overlap_fault = []
    for (x, z, w, h) in start["rooms"]:""", 'utf-8')

sub(p, u"""                edge = cx in (x, x + w - 1) or cz in (z, z + h - 1)
                if edge:
                    # The generator throws if a wall lands where a structure already is.
                    if (cx, cz) in interior:
                        overlap_fault.append((cx, cz))
                    walls.add((cx, cz))
                else:
                    if (cx, cz) in walls:
                        overlap_fault.append((cx, cz))
                    interior.add((cx, cz))
                    walls.discard((cx, cz))
                floors.add((cx, cz))""",
u"""                edge = cx in (x, x + w - 1) or cz in (z, z + h - 1)
                if edge:
                    # Wall on wall is the collision the generator actually throws on.
                    if (cx, cz) in walls:
                        overlap_fault.append((cx, cz))
                    walls.add((cx, cz))
                else:
                    interior.add((cx, cz))
                floors.add((cx, cz))""", 'utf-8')

sub(p, u'    check("%s has no wall landing inside another room" % name, not overlap_fault,\n'
       u'          "-- generator throws at " + str(sorted(set(overlap_fault))[:4]))',
       u'    check("%s has no two rooms sharing a wall cell" % name, not overlap_fault,\n'
       u'          "-- generator throws at " + str(sorted(set(overlap_fault))[:4]))', 'utf-8')

print('store buildings moved off the walls; the wall claim restated')
