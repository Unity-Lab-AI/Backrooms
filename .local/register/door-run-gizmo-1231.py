# -*- coding: utf-8 -*-
"""The player-facing half of the bound door run: one gizmo, one float menu.

Kept to the surface the rest of the gate already uses -- a `Command_Action` opening a float menu
of candidates -- because the gate's gizmo bar is already six entries long and a seventh window
would be worse than a seventh button.

Only offered when there is something to offer: a gate with no eligible neighbour and no existing
run does not get a button that can only tell you it did nothing.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def edit(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding='utf-8').read()
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    print('edited %s' % rel)


COMP = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'CompRimroomsGate.cs')

edit(COMP,
     u'''            yield return EquipmentLinkGizmo();''',
     u'''            yield return EquipmentLinkGizmo();

            // The run fallback. Shown only when there is a neighbour to take or a run to give
            // back, so a gate in the middle of a wall with nothing beside it gets no button that
            // could only refuse.
            if (RunDoorCount > 1 || AdjacentRunCandidates().Count > 0)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_GateRun_Label".Translate(RunDoorCount.ToString(),
                        GateWidth.ToString()),
                    defaultDesc = "RR_GateRun_Desc".Translate(),
                    icon = parent.def.uiIcon,
                    action = OpenGateRunMenu
                };
            }''')

RUN = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'GateDoorRun.cs')

edit(RUN,
     u'''        internal void ExposeGateRun()''',
     u'''        /// <summary>
        /// Every ordinary door touching this run that could legally join it.
        ///
        /// Cardinal neighbours of every cell the run already holds, which is how a run grows
        /// along a wall. Tested by actually proposing each one, so a candidate is only listed if
        /// binding it would really produce a solid legal doorway -- a diagonal neighbour or a
        /// door that would make an L never appears, rather than appearing and then refusing.
        ///
        /// Sorted ordinally by position before being returned. Invariant 26: a menu whose rows
        /// move between frames is a menu somebody misclicks.
        /// </summary>
        internal List<Thing> AdjacentRunCandidates()
        {
            var found = new List<Thing>();
            if (!IsDesignated || IsRunExtension || parent == null || !parent.Spawned) { return found; }
            Map map = parent.Map;
            if (map == null) { return found; }

            CellRect rect = RunRect;
            var seen = new HashSet<Thing>();
            foreach (IntVec3 cell in rect)
            {
                for (int side = 0; side < 4; side++)
                {
                    IntVec3 candidate = cell + GenAdj.CardinalDirections[side];
                    if (!candidate.InBounds(map) || rect.Contains(candidate)) { continue; }
                    Building edifice = candidate.GetEdifice(map);
                    if (edifice == null || !seen.Add(edifice)) { continue; }
                    if (!WouldJoinRun(edifice)) { continue; }
                    found.Add(edifice);
                }
            }
            found.Sort(delegate(Thing left, Thing right)
            {
                int byX = left.Position.x.CompareTo(right.Position.x);
                return byX != 0 ? byX : left.Position.z.CompareTo(right.Position.z);
            });
            return found;
        }

        /// <summary>
        /// Whether binding this door would really work, asked by trying it and putting it back.
        ///
        /// Cheaper than reimplementing the solidity and legality rules a second time, and
        /// impossible to get out of step with them -- which a second implementation would.
        /// </summary>
        private bool WouldJoinRun(Thing door)
        {
            if (door == null || !(door is Building_Door) || door == parent) { return false; }
            if (door.Destroyed || !door.Spawned || door.Faction != Faction.OfPlayer) { return false; }
            if (door.def == null || door.def.size.x != 1 || door.def.size.z != 1) { return false; }
            CompRimroomsGate other = door.TryGetComp<CompRimroomsGate>();
            if (other == null || other.IsDesignated || other.IsRunExtension) { return false; }

            nativeRunExtensions = nativeRunExtensions ?? new List<Thing>();
            if (nativeRunExtensions.Contains(door)) { return false; }
            nativeRunExtensions.Add(door);
            CellRect proposed = RunRect;
            bool legal = proposed.Area == RunDoorCount &&
                LegalGateFootprint(new IntVec2(proposed.Width, proposed.Height));
            nativeRunExtensions.Remove(door);
            return legal;
        }

        private void OpenGateRunMenu()
        {
            var options = new List<FloatMenuOption>();
            List<Thing> candidates = AdjacentRunCandidates();
            for (int index = 0; index < candidates.Count; index++)
            {
                Thing door = candidates[index];
                options.Add(new FloatMenuOption(
                    "RR_GateRun_Extend".Translate(door.LabelShortCap),
                    delegate { ShowOrderResult(ExtendGateAcrossRun(door)); }));
            }
            if (RunDoorCount > 1)
            {
                options.Add(new FloatMenuOption("RR_GateRun_Release".Translate(),
                    delegate { ShowOrderResult(ReleaseGateRun()); }));
            }
            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_GateRun_NoCandidate".Translate(), null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        internal void ExposeGateRun()''')

print('gizmo and candidate search added')
