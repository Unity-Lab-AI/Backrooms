import io

p = 'src/RimroomsAsyncIndustries/Threats/InhabitantService.cs'
s = io.open(p, encoding='utf-8').read()

pairs = []

# Pass the band down: what a hostile does about the player is a property of how bad the
# coordinate has become, not of which family it belongs to.
pairs.append((
 '                for (int made = 0; made < wanted; made++)\n'
 '                {\n'
 '                    if (!PlaceOne(map, coordinate, family, seed + made * 17)) { break; }',
 '                for (int made = 0; made < wanted; made++)\n'
 '                {\n'
 '                    if (!PlaceOne(map, coordinate, family, seed + made * 17, band)) { break; }'))

pairs.append((
 '        private static bool PlaceOne(Map map, CoordinateRecord coordinate,\n'
 '            RimroomsInhabitantDef family, int seed)\n'
 '        {',
 '        private static bool PlaceOne(Map map, CoordinateRecord coordinate,\n'
 '            RimroomsInhabitantDef family, int seed, CoordinatePressureLadder.Band band)\n'
 '        {'))

pairs.append((
 '            if (family.hostile && faction != null)\n'
 '            {\n'
 '                // A defend-this-place lord rather than an assault lord: the warning-first rule\n'
 '                // requires that a player who backs off is not pursued across the whole space.\n'
 '                LordMaker.MakeNewLord(faction,\n'
 '                    new LordJob_DefendPoint(cell, 12f), map, new List<Pawn> { pawn });\n'
 '            }',
 '            if (family.hostile && faction != null)\n'
 '            {\n'
 '                LordMaker.MakeNewLord(faction, HostileLordJob(band, cell), map, new List<Pawn> { pawn });\n'
 '            }'))

for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

helper = '''
        /// <summary>
        /// What a hostile inhabitant does about the people who walked in.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"and at deeper levels i do want
        /// monstrosities and npcs to \\"Chase\\" pawns/ kill them all the way to the gate"*.
        ///
        /// Below <see cref="CoordinatePressureLadder.Band.Hostile"/> this is unchanged and
        /// deliberately so: a defend-this-place lord, because the warning-first rule requires
        /// that **a player who backs off is not pursued across the whole space**. That rule is
        /// what makes a shallow coordinate somewhere a lone survivor can retreat from.
        ///
        /// At `Hostile` it hunts. The band's own definition is *"more than one thing acts, and
        /// the space stops being forgiving"*, which is the owner's "deeper levels" already
        /// written down, so the rule needed no second threshold of its own.
        ///
        /// **Nothing here is new pursuit code.** RimWorld's own assault lord already walks a
        /// hostile to whoever it can reach, which is exactly "all the way to the gate": the
        /// threshold room is excluded from *spawning*, never from being walked into, so a
        /// hunter follows a fleeing crew right to the doorway with nothing added.
        ///
        /// Kidnapping, stealing, fleeing and timing out are all off. A coordinate has map
        /// edges because every generated map does, and a kidnapper carrying somebody off one
        /// would be a disappearance with no story attached to it. What is wanted is something
        /// that follows you, and the countermeasure stays what it always was: leave.
        /// </summary>
        private static LordJob HostileLordJob(CoordinatePressureLadder.Band band, IntVec3 cell)
        {
            if (band < CoordinatePressureLadder.Band.Hostile)
            { return new LordJob_DefendPoint(cell, 12f); }
            return new LordJob_AssaultColony(Faction.OfPlayer, canKidnap: false,
                canTimeoutOrFlee: false, sappers: false, useAvoidGridSmart: false, canSteal: false);
        }
'''

anchor = '        private static Faction FactionFor(RimroomsInhabitantDef family)'
assert anchor in s
s = s.replace(anchor, helper.lstrip('\n') + '\n' + anchor, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('pursuit wired to the band')
