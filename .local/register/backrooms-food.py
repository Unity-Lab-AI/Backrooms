# -*- coding: utf-8 -*-
"""There is food down there now. Owner: *"there wasnt enough \\"people-food\\" in the back rooms
need to be able to survive a bit if it was a solo start"*.

**Food existed in exactly one of sixteen archetypes**, and that one could not appear on a first
level: `RR_Room_Canteen`, `minDepth 2`, weight 1.1, a **70% chance** of 1 to 3 meal stacks of 2 to
8. Best case about twenty meals somewhere on the floor, usual case none at all, and for the solo
start -- which begins *inside* a coordinate with whatever it holds -- that is the difference
between a scenario and a countdown.

Three changes, all to our own archetype defs, all referencing categories the loaded game already
provides:

  * **the canteen reaches a first level** -- `minDepth` 1, weight 1.1 to 1.6 -- and carries meals
    at certainty rather than at 70%, in stacks worth eating;
  * **the storeroom holds food**, which is what a storeroom in a facility holds. It has the
    highest weight of any archetype at 1.4, so this is the change that actually feeds somebody:
    raw food in quantity, plus a chance of prepared meals;
  * **the dormitory keeps a little by the beds**, because people do.

`FoodRaw` and `FoodMeals` are Core's own thing categories, so this adds nothing and invents
nothing -- it asks the loaded game for what it has, which is the content rule.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                    "RimroomsRoomArchetypeDefs", "RR_RoomArchetypes.xml")

CANTEEN_OLD = u"""    <defName>RR_Room_Canteen</defName>
    <label>canteen</label>
    <description>Tables set for a shift that never came off.</description>
    <minDepth>2</minDepth>
    <weight>1.1</weight>"""
CANTEEN_NEW = u"""    <defName>RR_Room_Canteen</defName>
    <label>canteen</label>
    <description>Tables set for a shift that never came off.</description>
    <!-- Reaches a FIRST level. The solo start begins inside a coordinate with whatever the
         coordinate holds, and food lived only here, behind minDepth 2 and a 70% roll. -->
    <minDepth>1</minDepth>
    <weight>1.6</weight>"""

CANTEEN_FOOD_OLD = u"""      <li>
        <kind>CategoryMember</kind>
        <category>FoodMeals</category>
        <count>1~3</count>
        <chance>0.7</chance>
        <stackCount>2~8</stackCount>
      </li>"""
CANTEEN_FOOD_NEW = u"""      <li>
        <kind>CategoryMember</kind>
        <category>FoodMeals</category>
        <count>3~6</count>
        <stackCount>6~16</stackCount>
      </li>
      <li>
        <kind>CategoryMember</kind>
        <category>FoodRaw</category>
        <count>1~3</count>
        <chance>0.8</chance>
        <stackCount>20~45</stackCount>
      </li>"""

STOREROOM_OLD = u"""    <defName>RR_Room_Storeroom</defName>
    <label>storeroom</label>
    <description>Racking, crates, and stock counted by nobody.</description>
    <minDepth>2</minDepth>
    <weight>1.4</weight>
    <slots>
      <li>
        <kind>Storage</kind>
        <count>2~5</count>
      </li>"""
STOREROOM_NEW = u"""    <defName>RR_Room_Storeroom</defName>
    <label>storeroom</label>
    <description>Racking, crates, and stock counted by nobody.</description>
    <!-- The highest weight of any archetype, so this is the slot that actually feeds anybody.
         A storeroom in a facility holds food; it held everything except food. -->
    <minDepth>1</minDepth>
    <weight>1.4</weight>
    <slots>
      <li>
        <kind>Storage</kind>
        <count>2~5</count>
      </li>
      <li>
        <kind>CategoryMember</kind>
        <category>FoodRaw</category>
        <count>2~4</count>
        <stackCount>25~60</stackCount>
      </li>
      <li>
        <kind>CategoryMember</kind>
        <category>FoodMeals</category>
        <count>1~2</count>
        <chance>0.6</chance>
        <stackCount>4~10</stackCount>
      </li>"""

DORM_OLD = u"""    <defName>RR_Room_Dormitory</defName>
    <label>dormitory</label>"""
DORM_NEW = u"""    <defName>RR_Room_Dormitory</defName>
    <label>dormitory</label>"""

EDITS = [
    (CANTEEN_OLD, CANTEEN_NEW),
    (CANTEEN_FOOD_OLD, CANTEEN_FOOD_NEW),
    (STOREROOM_OLD, STOREROOM_NEW),
]

text = io.open(DEFS, encoding="utf-8-sig").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)

# The dormitory keeps a little by the beds.
DORM_SLOTS = u"""    <defName>RR_Room_Dormitory</defName>"""
index = text.index(DORM_SLOTS)
end = text.index(u"</slots>", index)
dorm_extra = u"""      <li>
        <kind>CategoryMember</kind>
        <category>FoodMeals</category>
        <count>1~2</count>
        <chance>0.5</chance>
        <stackCount>2~6</stackCount>
      </li>
    """
text = text[:end] + dorm_extra + text[end:]

io.open(DEFS, "w", encoding="utf-8-sig", newline="").write(text)
print("canteen reaches depth 1 and is certain; the storeroom and the dormitory hold food")
