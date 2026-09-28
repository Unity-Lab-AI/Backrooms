using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Threats
{
    public sealed partial class FirstSliceSiteComponent
    {
        private const int TwoGameMinutes = 84;
        private const int OneGameMinute = 42;

        private void StartPursuer(RoomRecord crewRoom, int now)
        {
            if (pursuerEncounterStarted) { return; }
            CoordinateRecord coordinate = Coordinate;
            Dictionary<int, int> distances = DistancesFrom(crewRoom.index);
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_QuietPursuer");
            if (definition == null) { return; }
            RoomRecord distant = null;
            IntVec3 cell = IntVec3.Invalid;
            foreach (RoomRecord candidate in coordinate.Rooms.Where(r => r.familyId != "threshold_room" &&
                distances.ContainsKey(r.index) && distances[r.index] == 2).OrderBy(r => r.index))
            {
                if (!TryRoomCell(candidate, out IntVec3 possible)) { continue; }
                if (!crew.Any(p => p != null && !p.Dead && !p.Downed && p.Spawned && p.Map == map &&
                    RoomAt(p.Position)?.Index == crewRoom.Index && map.reachability.CanReach(possible, p.Position,
                        PathEndMode.Touch, TraverseParms.For(TraverseMode.NoPassClosedDoors)))) { continue; }
                distant = candidate;
                cell = possible;
                break;
            }
            // An unopened room is not a pursuit route. Retry after exploration exposes
            // a valid two-room approach, preserving the encounter opportunity.
            if (distant == null) { return; }
            pursuer = ThingMaker.MakeThing(definition) as Thing_QuietPursuer;
            if (pursuer == null) { return; }
            try
            {
                pursuer.SetFaction(Faction.OfAncientsHostile);
                Thing spawned = GenSpawn.Spawn(pursuer, cell, map);
                if (spawned != pursuer || !pursuer.Spawned || pursuer.Map != map)
                { throw new InvalidOperationException("Native spawn did not attach the new encounter object to its site."); }
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Threat] Encounter placement failed; no sighting awarded: " + error);
                if (pursuer != null && !pursuer.Destroyed && (!pursuer.Spawned || pursuer.Map == map))
                { pursuer.Destroy(DestroyMode.Vanish); }
                pursuer = null;
                Note("RR_Event_PursuerPlacementFailed");
                return;
            }
            pursuerEncounterStarted = true;
            pursuerWithdrawn = false;
            pursuerRoom = distant.index;
            nextAdvanceTick = now + TwoGameMinutes;
            lastObservedCrewRoom = crewRoom.index;
            lastLoudTick = now;
            // A reported sighting reveals its small marker cell, never an unexplored room graph.
            map.fogGrid.Unfog(cell);
            Note("RR_Event_PursuerSighting", (pursuerRoom + 1).ToString(), "2");
        }

        private void AdvancePursuer(int now, List<Pawn> present, RoomRecord currentCrewRoom)
        {
            if (!pursuerEncounterStarted || pursuerWithdrawn) { return; }
            if (pursuer == null || pursuer.Destroyed || !pursuer.Spawned) { WithdrawPursuer(true); return; }
            if (present.All(p => RoomAt(p.Position)?.familyId == "threshold_room")) { WithdrawPursuer(true); return; }
            Dictionary<int, int> distances = DistancesFrom(pursuerRoom);
            Pawn closest = present.Where(p => !p.Downed && RoomAt(p.Position) != null && RoomAt(p.Position).familyId != "threshold_room")
                .OrderBy(p => distances.ContainsKey(RoomAt(p.Position).index) ? distances[RoomAt(p.Position).index] : int.MaxValue)
                .ThenBy(p => p.thingIDNumber).FirstOrDefault();
            if (closest == null) { return; }
            // Authored room bounds can be subdivided by player construction. Check the real route before contact too.
            if (!map.reachability.CanReach(pursuer.Position, closest.Position, PathEndMode.Touch,
                TraverseParms.For(TraverseMode.NoPassClosedDoors)))
            { WithdrawPursuer(true); return; }
            RoomRecord targetRoom = RoomAt(closest.Position);
            if (targetRoom.index == pursuerRoom)
            {
                if (contactWarningTick < 0 || contactPawn != closest)
                {
                    contactWarningTick = now;
                    contactPawn = closest;
                    Note("RR_Event_PursuerContactWarning", closest.LabelShortCap.ToString());
                }
                else if (now - contactWarningTick >= OneGameMinute && !attemptedStrike)
                {
                    attemptedStrike = true;
                    // Only a healthy, upright target with a sound arm can receive this bounded tutorial strike.
                    // Other cases withdraw without converting an existing medical crisis into unavoidable death.
                    BodyPartRecord arm = closest.health.hediffSet.GetNotMissingParts()
                        .FirstOrDefault(p => p.def.defName == "Arm" && closest.health.hediffSet.GetPartHealth(p) > 5f);
                    if (!closest.Downed && closest.health.summaryHealth.SummaryHealthPercent >= 0.8f && arm != null)
                    {
                        closest.TakeDamage(new DamageInfo(DamageDefOf.Blunt, 2f, 0f, -1f, pursuer, arm));
                        Note("RR_Event_PursuerInjury", closest.LabelShortCap.ToString());
                    }
                    WithdrawPursuer(true);
                }
                return;
            }
            contactWarningTick = -1;
            contactPawn = null;
            int loudTick = present.Max(p => p.LastAttackTargetTick);
            bool loud = loudTick > lastLoudTick;
            if (loud) { lastLoudTick = loudTick; }
            if (!loud && currentCrewRoom.index != lastObservedCrewRoom)
            {
                lastObservedCrewRoom = currentCrewRoom.index;
                nextAdvanceTick = now + TwoGameMinutes;
                return;
            }
            if (!loud && now < nextAdvanceTick) { return; }
            if (advances >= 3) { WithdrawPursuer(true); return; }
            // Closed doors break the pursuit. The entity does not open doors or pass through walls.
            if (!map.reachability.CanReach(pursuer.Position, closest.Position, PathEndMode.Touch,
                TraverseParms.For(TraverseMode.NoPassClosedDoors)))
            { WithdrawPursuer(true); return; }
            Dictionary<int, int> toward = DistancesFrom(targetRoom.index);
            RoomRecord here = Coordinate.Rooms.FirstOrDefault(r => r.index == pursuerRoom);
            RoomRecord next = here == null ? null : Coordinate.Rooms.Where(r => here.links.Contains(r.index) &&
                r.familyId != "threshold_room" && toward.ContainsKey(r.index)).OrderBy(r => toward[r.index]).ThenBy(r => r.index).FirstOrDefault();
            if (next == null || !TryRoomCell(next, out IntVec3 cell)) { WithdrawPursuer(true); return; }
            pursuer.Position = cell;
            map.fogGrid.Unfog(cell);
            pursuerRoom = next.index;
            advances++;
            nextAdvanceTick = now + TwoGameMinutes;
            Note("RR_Event_PursuerAdvance", (pursuerRoom + 1).ToString(), toward[pursuerRoom].ToString());
        }

        public void RepelPursuer()
        {
            if (!pursuerEncounterStarted || pursuerWithdrawn) { return; }
            if (pursuer == null || pursuer.Destroyed || !pursuer.Spawned) { WithdrawPursuer(true); return; }
            Pawn visibleCrew = crew.FirstOrDefault(p => p != null && p.Spawned && p.Map == map && !p.Downed && RoomAt(p.Position) != null);
            if (visibleCrew == null) { WithdrawPursuer(true); return; }
            Dictionary<int, int> distances = DistancesFrom(RoomAt(visibleCrew.Position).index);
            RoomRecord here = Coordinate.Rooms.FirstOrDefault(r => r.index == pursuerRoom);
            RoomRecord away = here == null ? null : Coordinate.Rooms.Where(r => here.links.Contains(r.index) &&
                r.familyId != "threshold_room" && distances.ContainsKey(r.index) && distances[r.index] > distances[pursuerRoom])
                .OrderByDescending(r => distances[r.index]).ThenBy(r => r.index).FirstOrDefault();
            if (away == null || !TryRoomCell(away, out IntVec3 cell)) { WithdrawPursuer(true); return; }
            pursuer.Position = cell;
            map.fogGrid.Unfog(cell);
            pursuerRoom = away.index;
            nextAdvanceTick = Find.TickManager.TicksGame + TwoGameMinutes;
            lastLoudTick = Find.TickManager.TicksGame;
            contactWarningTick = -1;
            contactPawn = null;
            Note("RR_Event_PursuerRepelled", (pursuerRoom + 1).ToString());
        }

        private void WithdrawPursuer(bool report)
        {
            bool wasActive = pursuerEncounterStarted && !pursuerWithdrawn;
            pursuerWithdrawn = true;
            if (pursuer != null && !pursuer.Destroyed) { pursuer.Destroy(DestroyMode.Vanish); }
            pursuer = null;
            if (report && wasActive && Coordinate != null) { Note("RR_Event_PursuerWithdrawn"); }
        }

        private Dictionary<int, int> DistancesFrom(int origin)
        {
            var result = new Dictionary<int, int> { { origin, 0 } };
            var pending = new Queue<int>();
            pending.Enqueue(origin);
            while (pending.Count != 0 && result.Count <= 8)
            {
                int current = pending.Dequeue();
                RoomRecord room = Coordinate.Rooms.FirstOrDefault(r => r.index == current);
                if (room == null) { continue; }
                foreach (int next in room.links)
                {
                    RoomRecord nextRoom = Coordinate.Rooms.FirstOrDefault(r => r.index == next);
                    if (nextRoom == null || nextRoom.familyId == "threshold_room" || result.ContainsKey(next)) { continue; }
                    result[next] = result[current] + 1;
                    pending.Enqueue(next);
                }
            }
            return result;
        }
        private bool TryRoomCell(RoomRecord room, out IntVec3 cell)
        {
            foreach (IntVec3 candidate in room.Bounds.Cells.OrderBy(c => c.DistanceToSquared(room.Bounds.CenterCell)))
            {
                if (!candidate.InBounds(map) || !candidate.Standable(map) || candidate.GetFirstPawn(map) != null ||
                    candidate.GetEdifice(map) != null || candidate.GetFirstItem(map) != null) { continue; }
                cell = candidate;
                return true;
            }
            cell = IntVec3.Invalid;
            return false;
        }
    }
}
