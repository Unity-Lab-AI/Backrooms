# -*- coding: utf-8 -*-
"""The grand-level claim encoded a direction the owner has since refined.

It asserted *depth 1 is at most eight rooms of at least sixty cells* -- a faithful reading of
*"making the 0 level rooms be grand large spaces and leas than 60-100 romms"* at the time it was
written, and **the thing that produced the nine-room warehouse the owner then walked through.**

Refined, not reversed, and by the owner in the same breath as the complaint:

    *"lets try and fix this so the normal yellow backrooms look isnt the whole floor but the main
     spanw room and going deeping in can mean the numner of branch hallways and rooms distancing
     from the main portal spawn in the back rooms continuw on into the map"*

**Grand was always about the room you arrive in, not about every room.** So the claim now asserts
what that actually requires -- a threshold hall spanning two slots, a level that is a maze around
it, and the ceiling still honoured -- and it would fail just as loudly if the hall were lost as
it did when the maze was missing.

**This is a proof earning its keep rather than being edited to agree.** It refused the change,
the refusal sent me back to the owner's words, and the words said something more precise than the
claim did.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

OLD = u'''check("LEVEL ZERO IS GRAND, AND THE ROOM COUNT GOES DOWN TO PAY FOR IT",
      profile[0][3] >= 60 and profile[0][4] <= 8,
      "-- owner direction, verbatim: *\\"making the 0 level rooms be grand large spaces and leas "
      "than 60-100 romms\\"*. Depth 1 is %d rooms of %d cells; a hall that size cannot fit in the "
      "19-cell slot the planner used before" % (profile[0][4], profile[0][3]))'''

NEW = u'''# **THE GRAND PART IS THE ROOM YOU ARRIVE IN, AND THE REST IS MAZE.** Owner, after walking the
# first level that ever generated: *"not enough rooms"*, *"it needs to be more maze liek and scary
# inducing beyond the main starting themed opening room"*, and the resolution of what had looked
# like a contradiction with *"making the 0 level rooms be grand large spaces"*:
#
#   *"the normal yellow backrooms look isnt the whole floor but the main spanw room"*
#
# The previous claim here required depth 1 to be at most eight rooms of at least sixty cells, and
# that is exactly what produced the nine-room warehouse. It refused this change, the refusal sent
# me back to the owner's words, and the words were more precise than the claim.
_hall_span = SPACING_AT_DEPTH_1 * 2 - SLOT_GAP if 'SPACING_AT_DEPTH_1' in dir() else None

check("A FIRST LEVEL IS A MAZE, NOT A WAREHOUSE",
      profile[0][4] >= 18,
      "-- *\\"not enough rooms\\"*. Depth 1 builds %d rooms; nine on a 300x300 map is a warehouse"
      % profile[0][4])

check("and its rooms are small enough to be rooms rather than halls",
      profile[0][3] <= 48,
      "-- %d cells across. Eighty-cell rooms are what the owner walked through and called not "
      "enough rooms: a handful of them fills the map" % profile[0][3])

check("THE THRESHOLD IS STILL A GRAND HALL, AND IT IS THE ONLY ONE",
      "private static RoomRecord MakeHall(" in planner
      and "spacing * 2 - SlotGap" in planner,
      "-- *\\"the normal yellow backrooms look isnt the whole floor but the main spanw room\\"*. "
      "It spans two slots, so at depth 1 it is about eighty cells across -- the span the whole "
      "level used to have -- while everything past it is about a third of that")

check("the hall takes TWO slots and not four, which is what keeps the chain connected",
      "consumed = 2;" in planner,
      "-- the serpentine exists so consecutive rooms are always grid neighbours and linking needs "
      "no pathfinding. Consuming two keeps that true; a 2x2 hall breaks the adjacency the whole "
      "layout rests on")'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW, 1)

# The claim needs the planner source; make sure it is read.
if "planner = read(" not in text and "planner =" not in text:
    marker = u"check(\"A FIRST LEVEL IS A MAZE, NOT A WAREHOUSE\","
    text = text.replace(marker, u"planner = read(PLANNER)\n\n" + marker, 1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("the grand claim now asserts hall-plus-maze")
