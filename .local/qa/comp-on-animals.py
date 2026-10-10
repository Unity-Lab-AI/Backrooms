# -*- coding: utf-8 -*-
"""An animal inhabitant has to be able to carry its tell too.

## The gap this closes

`CompProperties_RimroomsSurvivor` -- which now carries which family a coordinate
produced a pawn as, and therefore its tell -- is patched onto the **human** race
def only. The two new `Fauna` families are animals, so their tell would have had
nowhere to live and the `ConfigErrors` rule demanding one would have been
satisfied on paper while the player could never read it. That is precisely the
defect the rule was written to prevent, arriving in the same change as the rule.

## Attached to Core's animal base, and the limit is stated rather than hidden

**A race-condition xpath does not work here.** `Defs/ThingDef[race/intelligence="Animal"]`
looks right and is unreliable: patches run on the raw XML *before* def
inheritance is resolved, and most Core animal defs inherit `<race>` from
`AnimalThingBase` rather than stating `intelligence` themselves. The xpath would
match a handful of defs and silently miss the rest.

So this patches **`AnimalThingBase`**, Core's own abstract parent, and
inheritance carries it to every animal that uses it -- which is all of Core's and
most mods'.

**An animal from a mod that does not inherit `AnimalThingBase` will not carry the
comp.** That is recorded here and handled rather than ignored: the tell still
reaches the player in the family's letter, which every family has, and nothing
throws -- `TryGetComp` returns null and `MarkInhabitant` is never called. A
missing tell on the card is a reduced reading, not a fault.

Same dormant-until-marked discipline as the human attachment: installing this mod
must never change an animal nobody asked it to change.
"""
import io
import sys

NL = chr(10)
PATH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_NativeGateProviders.xml"

ANCHOR = (
    '      <li Class="PatchOperationAdd">' + NL
    + '        <xpath>Defs/ThingDef[defName="Human"]/comps</xpath>' + NL
    + "        <value>" + NL
    + '          <li Class="RimroomsAsyncIndustries.Threats.CompProperties_RimroomsSurvivor" />'
    + NL
    + "        </value>" + NL
    + "      </li>"
)

ADDITION = '''
      <!-- **AND ON ANIMALS, so a found animal can say what is wrong with it.** Owner,
           2026-10-04: "remember lsd unnerving feeling with all things ie events random
           spanwns, enemies, allies, nuetrals". The comp carries which inhabitant family a
           coordinate produced a pawn as, and therefore its tell; the two Fauna families are
           animals, so without this their tell would have had nowhere to live.

           AnimalThingBase is Core's own abstract parent and inheritance carries the comp to
           every animal that uses it. A race-condition xpath looks like the right answer and is
           not: patches run on the raw XML BEFORE def inheritance is resolved, so
           ThingDef[race/intelligence="Animal"] matches only the few defs that state it
           themselves and silently misses the rest.

           KNOWN LIMIT, stated rather than hidden: an animal from a mod that does not inherit
           AnimalThingBase carries no comp. Its tell then reaches the player in the family's
           letter, which every family has, and nothing throws - TryGetComp returns null and the
           mark is never made. A reduced reading, not a fault.

           Dormant until marked, exactly like the human attachment: installing this mod must
           never change an animal nobody asked it to change. -->
      <li Class="PatchOperationConditional">
        <xpath>Defs/ThingDef[@Name="AnimalThingBase"]/comps</xpath>
        <nomatch Class="PatchOperationAdd">
          <xpath>Defs/ThingDef[@Name="AnimalThingBase"]</xpath>
          <value><comps /></value>
        </nomatch>
      </li>
      <li Class="PatchOperationAdd">
        <xpath>Defs/ThingDef[@Name="AnimalThingBase"]/comps</xpath>
        <value>
          <li Class="RimroomsAsyncIndustries.Threats.CompProperties_RimroomsSurvivor" />
        </value>
      </li>'''

text = io.open(PATH, encoding="utf-8-sig").read()

if "AnimalThingBase" in text:
    print("already attached to the animal base")
    sys.exit(0)
if text.count(ANCHOR) != 1:
    print("ANCHOR NOT UNIQUE (%d); nothing written" % text.count(ANCHOR))
    sys.exit(1)

io.open(PATH, "w", encoding="utf-8-sig", newline=NL).write(text.replace(ANCHOR, ANCHOR + ADDITION))
print("attached the inhabitant comp to Core's AnimalThingBase, with the limit recorded")
