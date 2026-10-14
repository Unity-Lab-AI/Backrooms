using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// The room-design layer every placement command asks before it picks a cell.
    ///
    /// Owner, 2026-10-13, verbatim: "she needs like room design tools for differnt types of rooms as she just fills the
    /// room with beds no ryhme or reason and blocks the doors and shit not haviong access keeping a open floor plan with
    /// equipment and furnaturee along the wealls and in center leaving paths but nice and neat". In the test run Beds
    /// walked a room's cells in storage order and the three beds sat in the doorway row.
    ///
    /// The plan of a room, from its walls and doors alone:
    ///   keep-clear  the door cells, every inside cell touching a door, and a one-wide lane from each door straight
    ///               across the room -- nothing is ever placed on these, so every door opens onto floor and the room can
    ///               be crossed;
    ///   wall slots  free cells against a wall (never against a door), with the facing that puts the thing's back to the
    ///               wall -- furniture and equipment go here first, far corners before the door side;
    ///   centre slots free interior cells not against a wall, on a grid that leaves a one-wide path around every piece.
    /// A slot is only offered when the whole footprint of the thing (its size turned by the facing) fits on free floor
    /// inside the room, off the keep-clear cells, and the game accepts the blueprint there.
    ///   {"cmd":"room_plan","x":"..","z":".."}   the plan of the room at that cell, in words, for her to read
    /// </summary>
    internal static class RoomDesign
    {
        public sealed class Slot
        {
            public IntVec3 Cell;
            public Rot4 Rot;
            public bool OnWall;
        }

        public static bool IsRoom(Map map, Room r) =>
            r != null && !r.PsychologicallyOutdoors && !r.TouchesMapEdge && r.CellCount >= 4 && r.CellCount < 400;

        public static bool FreeFloor(Map map, IntVec3 c) =>
            c.InBounds(map) && !map.fogGrid.IsFogged(c) && c.Standable(map) && c.GetEdifice(map) == null &&
            !c.GetThingList(map).Any(t => t.def.IsBlueprint || t.def.IsFrame || t.def.category == ThingCategory.Building);

        private static bool IsWall(Map map, IntVec3 c)
        {
            if (!c.InBounds(map)) return true;                      // the map edge holds like a wall
            Building e = c.GetEdifice(map);
            return e != null && !(e is Building_Door) && e.def.passability == Traversability.Impassable;
        }

        public static List<IntVec3> Doors(Map map, Room r) =>
            r.BorderCells.Where(c => c.InBounds(map) && c.GetEdifice(map) is Building_Door).Distinct().ToList();

        /// <summary>Door cells, the inside cells touching a door, and a one-wide lane from each door across the room.</summary>
        public static HashSet<IntVec3> KeepClear(Map map, Room r)
        {
            var clear = new HashSet<IntVec3>();
            var inside = new HashSet<IntVec3>(r.Cells);
            foreach (IntVec3 d in Doors(map, r))
            {
                clear.Add(d);
                for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        IntVec3 c = new IntVec3(d.x + dx, 0, d.z + dz);
                        if (inside.Contains(c)) clear.Add(c);
                    }
                // the lane: step through the door into the room and keep that heading until the far wall
                IntVec3 step = IntVec3.Invalid;
                foreach (IntVec3 dir in GenAdj.CardinalDirections)
                    if (inside.Contains(d + dir)) { step = dir; break; }
                if (!step.IsValid) continue;
                for (IntVec3 c = d + step; inside.Contains(c); c += step) clear.Add(c);
            }
            return clear;
        }

        private static bool Fits(Map map, Room r, HashSet<IntVec3> clear, ThingDef def, IntVec3 c, Rot4 rot, ThingDef stuff)
        {
            CellRect rect = GenAdj.OccupiedRect(c, rot, def.size);
            foreach (IntVec3 o in rect)
            {
                if (!FreeFloor(map, o) || o.GetRoom(map) != r || clear.Contains(o)) return false;
            }
            // the cell in front stays free floor too, so nothing is boxed in: a bed's foot opens into the room (its head
            // is at the facing end, on the wall), a work table's interaction cell, anything else the cell it faces
            IntVec3 front = def.IsBed ? c - rot.FacingCell
                          : def.hasInteractionCell ? ThingUtility.InteractionCellWhenAt(def, c, rot, map)
                          : rect.CenterCell + rot.FacingCell;
            if (!rect.Contains(front) && (!FreeFloor(map, front) || front.GetRoom(map) != r)) return false;
            return GenConstruct.CanPlaceBlueprintAt(def, c, rot, map, false, null, null, stuff).Accepted;
        }

        /// <summary>
        /// Free cells against a wall (not a door), far corners first, each with the facing that puts the thing's back to
        /// that wall: for a bed the head is at the wall and the foot points into the room; for a stove or a table the
        /// working side faces the room.
        /// </summary>
        public static List<Slot> WallSlots(Map map, Room r, ThingDef def, ThingDef stuff)
        {
            var clear = KeepClear(map, r);
            var doors = Doors(map, r);
            var slots = new List<Slot>();
            foreach (IntVec3 c in r.Cells)
            {
                if (clear.Contains(c) || !FreeFloor(map, c)) continue;
                foreach (IntVec3 dir in GenAdj.CardinalDirections)
                {
                    if (!IsWall(map, c + dir)) continue;
                    // back to the wall: a stove, table or shelf faces away from it. A bed's head is at the facing end, so a
                    // bed faces the wall and stands one cell back: its footprint is {c - dir, c}, head on c against the wall
                    Rot4 rot = def.IsBed ? Rot4.FromIntVec3(dir) : Rot4.FromIntVec3(-dir);
                    IntVec3 at = def.IsBed && def.size.z == 2 ? c - dir : c;
                    if (!Fits(map, r, clear, def, at, rot, stuff)) continue;
                    slots.Add(new Slot { Cell = at, Rot = rot, OnWall = true });
                    break;
                }
            }
            // far from the doors first, then a stable order so repeated calls fill one wall at a time
            return slots.OrderByDescending(s => doors.Count == 0 ? 0 : doors.Min(d => d.DistanceToSquared(s.Cell)))
                        .ThenBy(s => s.Cell.z).ThenBy(s => s.Cell.x).ToList();
        }

        /// <summary>Free interior cells on a grid (every other column and row) with a path left around each piece.</summary>
        public static List<Slot> CentreSlots(Map map, Room r, ThingDef def, ThingDef stuff)
        {
            var clear = KeepClear(map, r);
            CellRect box = CellRect.FromCellList(r.Cells);
            var slots = new List<Slot>();
            foreach (IntVec3 c in r.Cells)
            {
                if (clear.Contains(c) || !FreeFloor(map, c)) continue;
                if (GenAdj.CardinalDirections.Any(dir => IsWall(map, c + dir))) continue;        // the wall ring is for wall slots
                if ((c.x - box.minX) % 2 != 1 || (c.z - box.minZ) % 2 != 1) continue;           // the grid keeps the paths
                foreach (Rot4 rot in new[] { Rot4.South, Rot4.East, Rot4.North, Rot4.West })
                {
                    if (!Fits(map, r, clear, def, c, rot, stuff)) continue;
                    slots.Add(new Slot { Cell = c, Rot = rot, OnWall = false });
                    break;
                }
            }
            return slots.OrderBy(s => s.Cell.DistanceToSquared(box.CenterCell)).ToList();
        }

        /// <summary>Wall slots first, then centre slots: where a piece of furniture goes in this room.</summary>
        public static List<Slot> Slots(Map map, Room r, ThingDef def, ThingDef stuff)
        {
            List<Slot> s = WallSlots(map, r, def, stuff);
            s.AddRange(CentreSlots(map, r, def, stuff));
            return s;
        }

        /// <summary>Place one blueprint in the best slot of the room; the slot taken, or null when nothing fits.</summary>
        public static Slot Place(Map map, Room r, ThingDef def, ThingDef stuff, bool wallOnly = false)
        {
            foreach (Slot s in wallOnly ? WallSlots(map, r, def, stuff) : Slots(map, r, def, stuff))
            {
                if (!GenConstruct.CanPlaceBlueprintAt(def, s.Cell, s.Rot, map, false, null, null, stuff).Accepted) continue;
                GenConstruct.PlaceBlueprintForBuild(def, s.Cell, map, s.Rot, Faction.OfPlayer, stuff);
                return s;
            }
            return null;
        }

        /// <summary>The plan of a room in words: size, doors, what stands in it, how many slots are free.</summary>
        public static string Describe(Map map, Room r)
        {
            var clear = KeepClear(map, r);
            CellRect box = CellRect.FromCellList(r.Cells);
            List<IntVec3> doors = Doors(map, r);
            ThingDef bed = ThingDefOf.Bed;
            int wallFree = WallSlots(map, r, bed, GenStuff.DefaultStuffFor(bed)).Count;
            int centreFree = CentreSlots(map, r, bed, GenStuff.DefaultStuffFor(bed)).Count;
            var things = r.ContainedAndAdjacentThings.Where(t => t.def.category == ThingCategory.Building && !(t is Building_Door) &&
                                                               t.def.passability != Traversability.Impassable)
                          .GroupBy(t => t.def.label).Select(g => g.Count() + " " + g.Key).ToList();
            return "room " + r.ID + ": " + box.Width + "x" + box.Height + " box from " + box.minX + "," + box.minZ + ", " + r.CellCount +
                   " cells, roofed " + (r.OpenRoofCount == 0 ? "fully" : "with " + r.OpenRoofCount + " open") + ", " + doors.Count +
                   " door(s) at " + string.Join(" ", doors.Select(d => d.x + "," + d.z)) + "; keep clear " + clear.Count +
                   " cells (door lanes); free wall slots for a bed-sized piece " + wallFree + ", free centre slots " + centreFree +
                   "; inside: " + (things.Count == 0 ? "nothing yet" : string.Join(", ", things)) +
                   " -- furniture along the walls, equipment in the centre grid, every door lane open";
        }

        public static string RoomPlan(Map map, Dictionary<string, string> a)
        {
            int x = a.TryGetValue("x", out string xs) && int.TryParse(xs, out int xv) ? xv : -1;
            int z = a.TryGetValue("z", out string zs) && int.TryParse(zs, out int zv) ? zv : -1;
            IntVec3 at = new IntVec3(x, 0, z);
            if (!at.InBounds(map)) return "refused: x,z must be a cell inside a room";
            Room r = at.GetRoom(map);
            if (!IsRoom(map, r)) return "refused: " + x + "," + z + " is not inside an enclosed room (outdoors, or the room touches the map edge)";
            return "ok: " + Describe(map, r);
        }
    }
}
