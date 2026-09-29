using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// Something follows your crew through the gate.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"and even at higher techs they can come
    /// through the portal into your base and attack, kidnap, steal, do everything npcs can do
    /// in game"*, under the condition the owner chose when asked: **depth plus technology,
    /// while an opening is live**, and *"if it reaches the threshold before you close: it comes
    /// through"*.
    ///
    /// ## This inverts the mod's founding rule, so it is bounded in five ways at once
    ///
    /// Everything else in this code base exists to keep the far side on the far side. That
    /// rule is not abandoned here; it is given a **named, narrow exception** that the player
    /// can see coming, cause, and stop:
    ///
    /// 1. **Only while a connection is actually open.** A closed gate is a wall.
    /// 2. **Only at <see cref="CoordinatePressureLadder.Band.Hostile"/>**, the band already
    ///    defined as *"the space stops being forgiving"*. A quiet coordinate never does this.
    /// 3. **Only once the branch has advanced the machine.** You made the gate hold longer;
    ///    that cuts both ways.
    /// 4. **Only if it fits.** A thing too large for the opening cannot come through it, which
    ///    is what makes a narrow gate a real defensive choice rather than the starter option.
    /// 5. **Only one per opening.** Closing and reopening is what resets it, so *"close the
    ///    gate"* is a countermeasure that works and is learnable in one incident.
    ///
    /// ## The inhabitant still decides nothing
    ///
    /// Invariant #1 holds exactly as written. No pawn asks to cross and nothing on the far
    /// side is ever given a gate as a destination -- <see
    /// cref="PortalTraversalPolicy.MayApproachThresholdForTraversal"/> still returns false for
    /// everything, so a hostile walks to the threshold because **your people are standing
    /// there**, not because a door is open. The gate notices what is already on its doorstep
    /// and the policy decides. That is the same shape as every other crossing in the mod.
    /// </summary>
    internal static class GateIncursion
    {
        /// <summary>Checked once a game-second rather than every tick; nothing here is urgent.</summary>
        private const int CheckInterval = 60;

        /// <summary>
        /// How far from the far threshold a hostile counts as "at the doorway". One step,
        /// deliberately: it has to actually reach the doorway, which is what gives a player
        /// the chance to close the gate first.
        /// </summary>
        private const int DoorstepRadius = 1;

        internal static void Tick(CompRimroomsGate gate)
        {
            if (gate == null || gate.parent == null || !gate.parent.Spawned) { return; }
            if (Find.TickManager == null || Find.TickManager.TicksGame % CheckInterval != 0) { return; }
            if (gate.IncursionSpentThisOpening) { return; }
            if (string.IsNullOrEmpty(gate.PortalConnectionId) || string.IsNullOrEmpty(gate.PortalOpeningId)) { return; }
            if (gate.IsEmergency) { return; }

            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (network == null || network.HasStateFault || campaign == null || !campaign.CanOperate) { return; }

            PortalConnectionRecord edge = network.Find(gate.PortalConnectionId);
            if (edge == null || edge.Kind != PortalConnectionKind.Laboratory ||
                edge.First == null || edge.Second == null || edge.First.Anchor != gate.parent) { return; }

            Map farMap = edge.Second.Map;
            Map homeMap = edge.First.Map;
            if (farMap == null || homeMap == null || farMap == homeMap ||
                !Find.Maps.Contains(farMap) || !Find.Maps.Contains(homeMap)) { return; }

            CoordinateRecord coordinate = null;
            IReadOnlyList<CoordinateRecord> coordinates = campaign.Coordinates;
            for (int index = 0; index < coordinates.Count; index++)
            {
                CoordinateRecord record = coordinates[index];
                if (record != null && string.Equals(record.Id, edge.CoordinateId, StringComparison.Ordinal))
                { coordinate = record; break; }
            }
            if (coordinate == null) { return; }

            Pawn intruder = FindAtDoorstep(farMap, edge.Second.ApproachCell, gate, coordinate);
            if (intruder == null) { return; }

            IntVec3 arrival = edge.First.ApproachCell;
            if (!CanArriveAt(intruder, homeMap, arrival)) { return; }
            if (!Transfer(intruder, homeMap, arrival)) { return; }

            gate.NoteIncursionSpent();
            Announce(intruder, homeMap, gate);
        }

        /// <summary>
        /// The first hostile standing at the far doorway that the policy will allow through.
        ///
        /// Candidates are taken in a fixed cell order so the same situation resolves the same
        /// way on every machine, which matters because a coordinate is regenerated from a seed
        /// and two players must see the same thing happen.
        /// </summary>
        private static Pawn FindAtDoorstep(Map farMap, IntVec3 approach, CompRimroomsGate gate,
            CoordinateRecord coordinate)
        {
            if (!approach.IsValid || !approach.InBounds(farMap)) { return null; }
            float wealth = CoordinatePressureLadder.ColonyWealth();
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(approach, DoorstepRadius, true))
            {
                if (!cell.InBounds(farMap)) { continue; }
                List<Thing> things = cell.GetThingList(farMap);
                for (int index = 0; index < things.Count; index++)
                {
                    Pawn candidate = things[index] as Pawn;
                    if (candidate == null) { continue; }
                    if (PortalTraversalPolicy.IncursionFailureKey(candidate, gate, coordinate, wealth) != null)
                    { continue; }
                    return candidate;
                }
            }
            return null;
        }

        private static bool CanArriveAt(Pawn pawn, Map map, IntVec3 cell)
        {
            if (pawn == null || map == null || !cell.IsValid || !cell.InBounds(map) || !cell.Standable(map))
            { return false; }
            if (!GenSpawn.CanSpawnAt(pawn.def, cell, map, pawn.Rotation, canWipeEdifices: false)) { return false; }
            List<Thing> existing = cell.GetThingList(map);
            for (int index = 0; index < existing.Count; index++)
            {
                if (existing[index] is Pawn || GenSpawn.SpawningWipes(pawn.def, existing[index].def))
                { return false; }
            }
            return true;
        }

        /// <summary>
        /// Move it. Preflight is complete before anything is despawned, and a spawn that
        /// somehow fails puts the pawn back where it was rather than losing it -- a vanished
        /// hostile is a save with a hole in it, and the player would never know.
        /// </summary>
        private static bool Transfer(Pawn pawn, Map map, IntVec3 cell)
        {
            Map origin = pawn.Map;
            IntVec3 originCell = pawn.Position;
            Rot4 rotation = pawn.Rotation;
            try
            {
                pawn.DeSpawn();
                Thing spawned = GenSpawn.Spawn(pawn, cell, map, rotation, WipeMode.Vanish);
                if (spawned == pawn && pawn.Spawned && pawn.Map == map) { return true; }
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Threat] Incursion transfer failed; returning the intruder to where it stood: " + error);
            }
            if (!pawn.Spawned && origin != null && Find.Maps.Contains(origin))
            { GenSpawn.Spawn(pawn, originCell, origin, rotation, WipeMode.Vanish); }
            return false;
        }

        private static void Announce(Pawn intruder, Map map, CompRimroomsGate gate)
        {
            Find.LetterStack.ReceiveLetter(
                "RR_Incursion_Label".Translate(),
                "RR_Incursion_Text".Translate(intruder.LabelShortCap, gate.parent.LabelCap),
                LetterDefOf.ThreatBig,
                new TargetInfo(intruder.Position, map));
            Audio.RimroomsAudio.Play("RR_GateWarning", map, intruder.Position, false);
        }
    }
}
