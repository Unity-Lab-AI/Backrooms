using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// The weight of being somewhere that is wrong, and what a player can build to hold it off.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"all pawns in the backrooms get a -1 to -10
    /// mood debuff -1 first enter and -10 after being in for long time like 1hr real game time
    /// and you can do things to lower it like security useing real materials not (odd) in theri
    /// surroundings ect ect expound on this too"*
    ///
    /// ## Why this is the piece that ties the mod together
    ///
    /// Until now the odd/ordinary split was purely economic: odd goods sell, ordinary goods do
    /// not. This makes it **psychological**, and in doing so it gives the player a reason to
    /// carry ordinary material *into* a coordinate rather than only carrying odd material out.
    /// That is a genuine tension rather than a decoration — **every ordinary thing hauled in to
    /// make the place bearable is a thing that was not sold**, and every odd fixture left in
    /// place is comfort that was not built.
    ///
    /// It also gives the forward base a purpose. Thirty-one work families can already work
    /// across a gate; this is what makes it worth building somewhere for them to do it from.
    ///
    /// ## The curve
    ///
    /// Pressure is a saved count of ticks a pawn has spent in a coordinate, not a thought with
    /// a timer. Ticks are what let the penalty **decay when they leave rather than snapping
    /// back to nothing** — an hour down there should follow somebody home for a while, which is
    /// both better drama and better play, because it forces shift rotation instead of one
    /// colonist living down there forever.
    ///
    /// * **-1 the moment they arrive.** The place is wrong even when it is comfortable, which is
    ///   why the floor exists at all and why no amount of building removes it.
    /// * **-10 after one real hour of continuous presence**, which at normal speed is
    ///   <see cref="FullPressureTicks"/> ticks. The same unit the gate's opening window uses,
    ///   so the two systems talk about time in the same terms.
    /// * **Recovery runs at <see cref="RecoveryRate"/>× the accumulation rate**, so a rotation
    ///   of shifts works and a single long shift does not.
    ///
    /// ## What a player builds to hold it off
    ///
    /// The owner's instinct — *"security useing real materials not (odd) in theri surroundings"*
    /// — is exactly the right lever, and it is scored from the pawn's **actual** surroundings
    /// rather than from a research unlock or a stat. Four things are read, and all four are
    /// things a player physically does:
    ///
    /// 1. **Ordinary-origin construction around them.** Walls, floors and furniture stamped
    ///    <see cref="ThingOrigin.Outside"/> — material hauled in through a gate. Odd fixtures
    ///    found in place score nothing, which is the whole point.
    /// 2. **Light.** A lit room reads as somewhere, an unlit one reads as the dark.
    /// 3. **A real enclosed room**, rather than a stretch of corridor.
    /// 4. **Somewhere to sit or lie down** that is ordinary-origin.
    ///
    /// Together these cap how fast pressure accumulates. They never remove the floor: a
    /// perfectly appointed room in a coordinate is still a room in a coordinate.
    /// </summary>
    public static class BackroomsPressure
    {
        /// <summary>
        /// One real hour at normal speed. The gate's base opening window is 108,000 ticks for
        /// exactly thirty real minutes, so this is that doubled and the two agree.
        /// </summary>
        public const int FullPressureTicks = 216000;

        /// <summary>Worst mood offset, reached at full pressure with no shelter at all.</summary>
        public const int MaxPenalty = 10;

        /// <summary>Mood offset on arrival, and the floor nothing removes.</summary>
        public const int MinPenalty = 1;

        /// <summary>Pressure sheds this many times faster than it builds.</summary>
        public const float RecoveryRate = 2f;

        /// <summary>
        /// The most shelter can slow accumulation. Never zero: a coordinate is always wearing,
        /// just slowly, so a player cannot build a room that makes the place ordinary.
        /// </summary>
        private const float BestShelterRate = 0.2f;

        /// <summary>
        /// The best shelter can do once a branch knows how to hold a space against what is in it.
        ///
        /// **Entities and containment tier 3: `RR_Cap_SpaceDiscipline`.** 0.12 rather than 0.20.
        ///
        /// **Still never zero**, which is the rule the base constant exists to state: a coordinate
        /// is always wearing, just slowly, and no player may build a room that makes the place
        /// ordinary. This unlock makes a well-built room better; it does not make the Backrooms
        /// somewhere you can live.
        /// </summary>
        private const float DisciplinedShelterRate = 0.12f;

        /// <summary>How often a pawn's surroundings are re-scored. Cheap, but not free.</summary>
        private const int ShelterInterval = 600;

        /// <summary>Radius around a pawn treated as "their surroundings" when there is no room.</summary>
        private const int SurroundingsRadius = 6;

        /// <summary>
        /// How fast pressure drains from somebody who is out of a coordinate.
        ///
        /// **RR_Cap_Decompression** (Fieldcraft, tier 4) doubles it again. A branch that has
        /// learned how to bring people back down gets them ready for the next trip sooner; it does
        /// nothing at all while they are still down there, which is the point -- the place is not
        /// less bad, the rotation is better.
        /// </summary>
        public static float RecoveryRateFor()
        {
            Company.RimroomsCampaignComponent campaign = Current.Game == null ? null
                : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            return campaign != null && campaign.HasCapability("RR_Cap_Decompression")
                ? PractisedRecoveryRate : RecoveryRate;
        }

        /// <summary>Recovery for a branch that has learned to decompress a crew.</summary>
        private const float PractisedRecoveryRate = 4f;

        /// <summary>
        /// The worst mood offset the place can carry for a pawn right now.
        ///
        /// **RR_Cap_SteadyNerve** (Entities, tier 4) lowers the ceiling. It never reaches
        /// <see cref="MinPenalty"/>, for the same reason shelter never reaches zero: the
        /// Backrooms always cost something, and a research project that made them free would be
        /// the campaign contradicting itself.
        /// </summary>
        private static int MaxPenaltyFor()
        {
            Company.RimroomsCampaignComponent campaign = Current.Game == null ? null
                : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            return campaign != null && campaign.HasCapability("RR_Cap_SteadyNerve")
                ? SteadyNervePenalty : MaxPenalty;
        }

        /// <summary>
        /// The reduced ceiling. Six rather than ten, and deliberately well above MinPenalty of
        /// one so the place is never shrugged off.
        /// </summary>
        private const int SteadyNervePenalty = 6;

        /// <summary>
        /// Converts accumulated pressure into the mood offset a thought should carry.
        /// Returns 0 when a pawn has no pressure at all, so no thought is applied.
        /// </summary>
        public static int PenaltyFor(int pressureTicks)
        {
            if (pressureTicks <= 0) { return 0; }
            float fraction = Mathf.Clamp01((float)pressureTicks / FullPressureTicks);
            int ceiling = MaxPenaltyFor();
            int scaled = MinPenalty + (int)Math.Round(fraction * (ceiling - MinPenalty));
            return Math.Max(MinPenalty, Math.Min(ceiling, scaled));
        }

        /// <summary>
        /// How fast pressure accumulates for a pawn right now, as a multiplier on real time.
        /// 1 is unsheltered; <see cref="BestShelterRate"/> is the best a player can build to.
        /// </summary>
        public static float ShelterRateFor(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned) { return 1f; }
            float score = ShelterScore(pawn);
            Company.RimroomsCampaignComponent campaign = Current.Game == null ? null
                : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            float best = campaign != null && campaign.HasCapability("RR_Cap_SpaceDiscipline")
                ? DisciplinedShelterRate : BestShelterRate;
            return Mathf.Lerp(1f, best, Mathf.Clamp01(score));
        }

        /// <summary>
        /// Scores a pawn's surroundings from 0 (raw coordinate) to 1 (a properly built,
        /// lit, enclosed room made of material carried in from outside).
        ///
        /// Read from what is physically there, deliberately. A research unlock or a stat would
        /// be easier and would mean nothing: the owner asked for *"real materials ... in theri
        /// surroundings"*, and the only honest reading of that is to go and look.
        /// </summary>
        public static float ShelterScore(Pawn pawn)
        {
            Map map = pawn == null ? null : pawn.Map;
            if (map == null || !pawn.Spawned) { return 0f; }

            float score = 0f;
            Room room = pawn.GetRoom();
            bool enclosed = room != null && !room.TouchesMapEdge && !room.UsesOutdoorTemperature
                && room.CellCount > 1 && room.CellCount < 400;
            if (enclosed) { score += 0.25f; }

            // Light. A lit place reads as somewhere; the dark reads as the dark.
            float glow = map.glowGrid == null ? 0f : map.glowGrid.GroundGlowAt(pawn.Position);
            score += Mathf.Clamp01(glow) * 0.15f;

            // Ordinary-origin construction and furniture in reach. This is the lever the owner
            // named, and it is the largest single contribution for that reason.
            int ordinary = 0;
            int considered = 0;
            bool ordinarySeat = false;
            foreach (IntVec3 cell in CellsToScore(pawn, room))
            {
                if (!cell.InBounds(map)) { continue; }
                List<Thing> things = cell.GetThingList(map);
                for (int index = 0; index < things.Count; index++)
                {
                    Thing thing = things[index];
                    if (thing == null || thing is Pawn || thing.def == null) { continue; }
                    if (thing.def.category != ThingCategory.Building) { continue; }
                    considered++;
                    if (OddOriginService.OriginOf(thing) != ThingOrigin.Outside) { continue; }
                    ordinary++;
                    if (thing.def.building != null &&
                        (thing.def.building.bed_humanlike || thing.def.IsTable ||
                         thing.def.building.isSittable))
                    { ordinarySeat = true; }
                }
            }
            if (considered > 0)
            { score += Mathf.Clamp01((float)ordinary / considered) * 0.45f; }
            if (ordinarySeat) { score += 0.15f; }

            return Mathf.Clamp01(score);
        }

        /// <summary>
        /// The cells treated as a pawn's surroundings: their room when they are in one, and a
        /// bounded radius when they are standing in open corridor. Capped either way so a
        /// enormous room costs no more to score than a small one.
        /// </summary>
        private static IEnumerable<IntVec3> CellsToScore(Pawn pawn, Room room)
        {
            if (room != null && !room.TouchesMapEdge && room.CellCount > 0 && room.CellCount <= 200)
            {
                foreach (IntVec3 cell in room.Cells) { yield return cell; }
                foreach (IntVec3 cell in room.BorderCells) { yield return cell; }
                yield break;
            }
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(pawn.Position, SurroundingsRadius, true))
            { yield return cell; }
        }

        /// <summary>How often surroundings are re-scored, exposed for the component's timing.</summary>
        public static int ScoreInterval { get { return ShelterInterval; } }
    }
}
