# -*- coding: utf-8 -*-
"""Extract the coordinate SHELL from the destination generator so two gensteps share it.

The shell is the part that carries invariant 13: a Backrooms coordinate has no outside, and
its roof is never removable. Rock to every edge, thick roof over every cell, rooms carved out
of it rather than built on top of it.

The destination generator furnishes that shell for a place reached through a gate -- a gate
anchor, a return cell, an evidence lead. The solo/group start furnishes it for people who are
simply already there and have none of those. Different furniture, same shell, and the shell is
the half that must never differ.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Generation',
                 'GenStep_BackroomsDestination.cs')
s = io.open(p, encoding='utf-8-sig').read()

START = u'                ClearMapContents(map);\n'
END = u'                PlaceNativeDoors(coordinate.Rooms, map);\n'

i = s.index(START)
j = s.index(END) + len(END)
body = s[i:j]
assert u'FillWithRock' in body and u'BuildCorridors' in body and u'BuildRoomWalls' in body, 'shell body looks wrong'

# The call that replaces it, inside Generate().
s = s[:i] + u'                BuildShell(map, coordinate, concrete, voidFloor, wallDef, wallStuff);\n' + s[j:]

# Re-indent the lifted body by four spaces less (it moves from inside a try{} to a method body).
lifted = u'\n'.join(line[4:] if line.startswith(u'    ') else line for line in body.split(u'\n'))

method = (
    u'\n'
    u'        /// <summary>\n'
    u'        /// The coordinate shell: rock to every edge, thick roof over every cell, and the\n'
    u'        /// rooms carved out of it.\n'
    u'        ///\n'
    u'        /// **Shared by both generators on purpose.** A destination reached through a gate\n'
    u'        /// and the place the solo/group start is already standing in are furnished quite\n'
    u'        /// differently - one has a gate anchor and a way home, the other has neither - but\n'
    u'        /// the shell is identical, and the shell is what carries invariant 13: **a Backrooms\n'
    u'        /// coordinate has no outside, and its roof is never removable.**\n'
    u'        ///\n'
    u'        /// A second copy of this would drift, and what would drift out of it is the promise\n'
    u'        /// that you cannot dig your way into open sky. The roof is deliberately\n'
    u'        /// `RoofRockThick` and never `RoofConstructed`: constructed roof can be removed.\n'
    u'        /// </summary>\n'
    u'        internal static void BuildShell(Map map, CoordinateRecord coordinate, TerrainDef concrete,\n'
    u'            TerrainDef voidFloor, ThingDef wallDef, ThingDef wallStuff)\n'
    u'        {\n'
    + lifted +
    u'        }\n'
)

anchor = u'        public override void PostMapInitialized(Map map, GenStepParams parms)'
assert anchor in s, 'PostMapInitialized anchor missing'
s = s.replace(anchor, method + u'\n' + anchor, 1)

io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('BuildShell extracted')
