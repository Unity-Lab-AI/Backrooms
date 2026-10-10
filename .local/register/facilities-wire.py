import io

p = 'src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs'
s = io.open(p, encoding='utf-8').read()

pairs = [
 # The coordinate carries the room graph, which is what a facility is assembled from.
 ('                    if (!quiet) { DressRoom(map, room, coordinate.Depth, seed, reserved); }',
  '                    if (!quiet) { DressRoom(map, room, coordinate, seed, reserved); }'),
 ('        private static void DressRoom(Map map, RoomRecord room, int depth, int seed,\n'
  '            HashSet<IntVec3> reserved)\n'
  '        {\n'
  '            RimroomsRoomArchetypeDef archetype = RoomArchetypeService.Select(room.familyId, depth, seed, room.index);',
  '        private static void DressRoom(Map map, RoomRecord room, CoordinateRecord coordinate, int seed,\n'
  '            HashSet<IntVec3> reserved)\n'
  '        {\n'
  '            int depth = coordinate.Depth;\n'
  '            // Owner direction: "facilitys". A room inside a facility is dressed as whatever\n'
  '            // its group is, not as its own roll, which is what turns three rooms into a\n'
  '            // laboratory wing instead of three rooms that each happen to have a bench.\n'
  '            // Resolving through the anchor means every member asks the same question and gets\n'
  '            // the same answer, with nothing stored to fall out of step with the graph.\n'
  '            int anchor = FacilityPlanner.AnchorFor(coordinate, room.index);\n'
  '            RoomRecord dresser = room;\n'
  '            if (anchor >= 0 && anchor != room.index)\n'
  '            {\n'
  '                for (int index = 0; index < coordinate.Rooms.Count; index++)\n'
  '                {\n'
  '                    RoomRecord candidate = coordinate.Rooms[index];\n'
  '                    if (candidate != null && candidate.Index == anchor) { dresser = candidate; break; }\n'
  '                }\n'
  '            }\n'
  '            RimroomsRoomArchetypeDef archetype =\n'
  '                RoomArchetypeService.Select(dresser.familyId, depth, seed, dresser.index);'),
]
for old, new in pairs:
    assert old in s, old[:80]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('facilities wired into room dressing')
