using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// Holds undiscovered inhabitants and bodies exactly as they were until somebody finds them.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"and we cant have backrooms npc pawns all
    /// dying off if a person is slow to explore so something needs to be done about like stat or
    /// need freezing until discovered with the fog of war"*.
    ///
    /// ## This was a real defect, not a refinement
    ///
    /// Everything placed in a coordinate is a live pawn on a live map, so its needs tick from
    /// the moment it exists. A survivor placed three rooms away would **starve to death before
    /// a cautious player ever reached them** — the rescue would be impossible for the exact
    /// player most likely to want it, and it would look like the feature was broken rather than
    /// like the person had died.
    ///
    /// The same applies to a hostile freezing to death in a cold band's coordinate, and to a
    /// body rotting to bones before anybody opens the door it is behind.
    ///
    /// ## Fog of war is the right discovery signal, and it is already there
    ///
    /// The owner named it and it is the correct choice: RimWorld already tracks, per cell,
    /// whether the player has seen it. **Nothing new has to be invented, saved or kept in sync**
    /// — `map.fogGrid.IsFogged` is the question, and it is already the exact question the player
    /// experiences as "have I been there yet".
    ///
    /// ## Holding rather than pausing
    ///
    /// Needs cannot be stopped from ticking without Harmony, so they are **topped back up** on
    /// a bounded sweep instead. The observable result is identical — an undiscovered person is
    /// exactly as they were when the space was made — and it needs no patch to a Core method.
    ///
    /// The moment their cell is uncovered they are released, and from then on they live and
    /// starve and freeze like anybody else. **Discovery is what starts their clock.**
    /// </summary>
    public sealed class InhabitantPreservationComponent : GameComponent
    {
        /// <summary>How often the sweep runs. Needs move slowly; this is far faster than they do.</summary>
        private const int Interval = 500;

        public InhabitantPreservationComponent(Game game)
        {
        }

        public override void GameComponentTick()
        {
            int now = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;
            if (now % Interval != 0) { return; }

            List<Map> maps = Find.Maps;
            if (maps == null) { return; }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (!OddOriginService.IsBackroomsMap(map)) { continue; }
                HoldUndiscovered(map);
            }
        }

        private static void HoldUndiscovered(Map map)
        {
            if (map.fogGrid == null) { return; }

            IReadOnlyList<Pawn> present = map.mapPawns == null ? null : map.mapPawns.AllPawnsSpawned;
            if (present != null)
            {
                for (int index = 0; index < present.Count; index++)
                {
                    Pawn pawn = present[index];
                    if (pawn == null || pawn.Dead || !pawn.Spawned) { continue; }
                    // The player's own people are never held. They are discovered by definition:
                    // somebody is looking at them.
                    if (pawn.Faction != null && pawn.Faction.IsPlayer) { continue; }
                    if (!map.fogGrid.IsFogged(pawn.Position)) { continue; }
                    Hold(pawn);
                }
            }

            if (map.listerThings == null) { return; }
            List<Thing> corpses = map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse);
            if (corpses == null) { return; }
            for (int index = 0; index < corpses.Count; index++)
            {
                Thing thing = corpses[index];
                if (thing == null || !thing.Spawned) { continue; }
                if (!map.fogGrid.IsFogged(thing.Position)) { continue; }
                HoldCorpse(thing);
            }
        }

        /// <summary>
        /// Restores an undiscovered inhabitant to the state they were placed in.
        ///
        /// Needs are refilled rather than frozen, and the temperature and hunger hediffs are
        /// cleared, because a pawn can be killed by either. Clearing them is safe precisely
        /// because this only ever runs on somebody **nobody has seen**: no player decision is
        /// being undone, and nothing observable is being reversed.
        /// </summary>
        private static void Hold(Pawn pawn)
        {
            if (pawn.needs != null)
            {
                List<Need> needs = pawn.needs.AllNeeds;
                if (needs != null)
                {
                    for (int index = 0; index < needs.Count; index++)
                    {
                        Need need = needs[index];
                        if (need == null) { continue; }
                        // Mood is deliberately left alone. A held pawn is not being made happy,
                        // only kept alive, and a forced mood would produce somebody who reads as
                        // uncannily content in a place designed to be unbearable.
                        if (need is Need_Mood) { continue; }
                        if (need.CurLevelPercentage < 1f) { need.CurLevelPercentage = 1f; }
                    }
                }
            }

            if (pawn.health == null || pawn.health.hediffSet == null) { return; }
            RemoveHediff(pawn, HediffDefOf.Malnutrition);
            RemoveHediff(pawn, HediffDefOf.Hypothermia);
            RemoveHediff(pawn, HediffDefOf.Heatstroke);
        }

        private static void RemoveHediff(Pawn pawn, HediffDef definition)
        {
            if (definition == null) { return; }
            Hediff found = pawn.health.hediffSet.GetFirstHediffOfDef(definition);
            if (found != null) { pawn.health.RemoveHediff(found); }
        }

        /// <summary>
        /// Keeps an undiscovered body as fresh as it was placed.
        ///
        /// A body is a find, and the owner's *"findeding dead ones"* is about what they were
        /// carrying and who they were. **A corpse that rotted to bones behind a door nobody
        /// opened has lost the discovery**, and it would look like a bug rather than like time
        /// passing.
        /// </summary>
        private static void HoldCorpse(Thing corpse)
        {
            CompRottable rot = corpse.TryGetComp<CompRottable>();
            if (rot != null && rot.RotProgress > 0f) { rot.RotProgress = 0f; }
        }
    }
}
