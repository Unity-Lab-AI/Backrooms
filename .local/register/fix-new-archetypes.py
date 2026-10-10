# -*- coding: utf-8 -*-
"""The two rooms the owner named by hand that did not exist: a classroom and a weapons locker.

Owner, verbatim: *"not enough weird stuff like a room with a lost person or a room full of bodies
or suppplies or a labratory ofr class room or hospital of manufactuing room or tool sheed or
weapons locker with loot and supplies anssd furnuture all ot of it randomly like and scary freaky
spooky like"*.

Everything else on that list already had an archetype -- laboratory, ward for the hospital,
workshop and machine hall for manufacturing, salvage and storeroom for the tool shed and the
supplies, and the dead are placed by `InhabitantService`. **Two were missing**, and the owner
named both: a **class room** and a **weapons locker**.

Both are built the way all fourteen already are: existing slot kinds and Core thing categories,
so nothing new is shipped. The classroom is seats and a table and books -- the most ordinary room
imaginable, standing empty, which is what makes it the worst one. The weapons locker is storage
and `Weapons`, which is the first archetype in the library that puts something worth taking in
front of the player: *"weapons locker with loot and supplies"*.

Depths chosen against the existing ladder rather than invented. A classroom is as mundane as a
dormitory, so it sits with the shallow set at 2; a weapons locker is a find, so it sits at 3 with
the ward and the machine hall. **With distance counting as depth, both are reachable on a first
level** -- out past the yellow rooms, which is exactly where the owner wants the strangeness.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                    "RimroomsRoomArchetypeDefs", "RR_RoomArchetypes.xml")

NEW = u"""  <RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>
    <defName>RR_Room_Classroom</defName>
    <label>class room</label>
    <description>Chairs facing a table at the front. Somebody set it out for a lesson that was never given, and the chairs are all pointing the right way.</description>
    <minDepth>2</minDepth>
    <weight>1.1</weight>
    <slots>
      <li>
        <kind>Seat</kind>
        <count>4~9</count>
      </li>
      <li>
        <kind>Table</kind>
        <count>1~2</count>
        <chance>0.9</chance>
      </li>
      <li>
        <kind>CategoryMember</kind>
        <category>Books</category>
        <count>1~3</count>
        <chance>0.75</chance>
        <stackCount>1~4</stackCount>
      </li>
      <li>
        <kind>Art</kind>
        <count>0~1</count>
        <chance>0.35</chance>
      </li>
      <li>
        <kind>Storage</kind>
        <count>0~1</count>
        <chance>0.4</chance>
      </li>
    </slots>
  </RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>

  <RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>
    <defName>RR_Room_WeaponsLocker</defName>
    <label>weapons locker</label>
    <description>Racks and lockers, most of them open and most of them empty. Whoever cleared this room was in a hurry, and did not finish.</description>
    <minDepth>3</minDepth>
    <weight>0.9</weight>
    <slots>
      <li>
        <kind>Storage</kind>
        <count>2~4</count>
      </li>
      <li>
        <kind>CategoryMember</kind>
        <category>Weapons</category>
        <count>1~3</count>
        <chance>0.8</chance>
        <stackCount>1~1</stackCount>
      </li>
      <li>
        <kind>CategoryMember</kind>
        <category>Apparel</category>
        <count>1~2</count>
        <chance>0.5</chance>
        <stackCount>1~1</stackCount>
      </li>
      <li>
        <kind>CategoryMember</kind>
        <category>Manufactured</category>
        <count>1~2</count>
        <chance>0.6</chance>
        <stackCount>3~12</stackCount>
      </li>
      <li>
        <kind>Table</kind>
        <count>0~1</count>
        <chance>0.45</chance>
      </li>
    </slots>
  </RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>

"""

text = io.open(DEFS, encoding="utf-8-sig").read()
ANCHOR = u"  <RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>\n    <defName>RR_Room_Laboratory</defName>"
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(DEFS, "w", encoding="utf-8-sig", newline="").write(text.replace(ANCHOR, NEW + ANCHOR, 1))
print("classroom and weapons locker added; sixteen archetypes now")
