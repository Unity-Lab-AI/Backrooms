# -*- coding: utf-8 -*-
"""Every lamp in the Backrooms burned the same colour. They do not any more.

Owner: *"we need more lights and mixedered varies of lights"*.

The count is fixed -- a lamp on every pillar instead of one per room. **The variety is this.**
`CompGlower.GlowColor` and `GlowRadius` are per-instance overrides in Core, which the gate work
already proved by lighting one door blue without touching any other door in the game. So the
lamps can differ from each other without a single new def, a new texture, or a patch.

Four tones, drawn per lamp from the coordinate's own seed:

  * the ordinary warm office white that the yellow rooms are lit with;
  * a colder, bluer fluorescent;
  * a sickly green-yellow, the colour of a tube that is on its way out;
  * and a dim one, reach cut by a third, so a stretch of corridor is darker than the rest
    without ever being dark enough to be unplayable.

**Seeded, so a coordinate is the same place every visit** -- the rule every other generated
property follows, and the one the record system depends on.

Nothing here authors a palette for the player to look at: these are the colours a failing strip
light actually goes, which is why the Backrooms read as a building left running rather than a
set. The owner's *"the basic rooms are well lit"* still holds -- every pillar still has a lamp,
and the dim one is dimmer, not off.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation",
                   "GenStep_BackroomsDestination.cs")

OLD = u'''                        reserved.Add(cell);
                        placedLights.Add(lamp);
                        break;'''

NEW = u'''                        reserved.Add(cell);
                        TintLamp(lamp, coordinate, room, pillar);
                        placedLights.Add(lamp);
                        break;'''

ANCHOR = u"        private static IntVec3 FindWallAttachmentCell(Map map, RoomRecord room, IntVec3 preferred,"

HELPER = u'''        /// <summary>
        /// Give this lamp a tone of its own.
        ///
        /// Owner: *"we need more lights and mixedered varies of lights"*. The count is answered by
        /// a lamp on every pillar; this is the variety.
        ///
        /// **`CompGlower.GlowColor` and `GlowRadius` are per-instance overrides in Core** -- the
        /// same mechanism that lights one door blue without touching any other door in the game --
        /// so lamps differ from each other with no new def, no new texture and no patch.
        ///
        /// Four tones: office white, a colder fluorescent, the green-yellow of a tube on its way
        /// out, and a dim one with its reach cut by a third. **The dim one is dimmer, never off**:
        /// the owner's *"the basic rooms are well lit"* is the theme, and a dark Backrooms is a
        /// different place entirely.
        ///
        /// Seeded from the coordinate and the pillar, so the same lamp is the same colour on
        /// every visit.
        /// </summary>
        private static void TintLamp(Thing lamp, CoordinateRecord coordinate, RoomRecord room,
            IntVec3 pillar)
        {
            if (lamp == null) { return; }
            CompGlower glower = lamp.TryGetComp<CompGlower>();
            if (glower == null) { return; }
            int seed = coordinate == null ? 0 : coordinate.Seed;
            int draw = DestinationService.StableHash(seed,
                "lamp:" + pillar.x + "," + pillar.z, room == null ? 0 : room.Index);
            if (draw < 0) { draw = ~draw; }
            switch (draw % 4)
            {
                case 0:
                    return;                                   // the ordinary office white
                case 1:
                    glower.GlowColor = new ColorInt(188, 206, 232, 0);   // colder fluorescent
                    return;
                case 2:
                    glower.GlowColor = new ColorInt(214, 222, 142, 0);   // a tube going out
                    return;
                default:
                    // Dimmer, not off. A stretch of corridor darker than the rest reads as a
                    // building left running; a dark one reads as a different game.
                    glower.GlowRadius = glower.GlowRadius * 2f / 3f;
                    return;
            }
        }

        private static IntVec3 FindWallAttachmentCell(Map map, RoomRecord room, IntVec3 preferred,'''

text = io.open(GEN, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("CALL ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW, 1)
if text.count(ANCHOR) != 1:
    print("HELPER ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
text = text.replace(ANCHOR, HELPER, 1)
io.open(GEN, "w", encoding="utf-8", newline="").write(text)
print("four tones of lamp, per instance, no new content")
