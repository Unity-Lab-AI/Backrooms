using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// Tracks how long each person has spent inside a coordinate, and sheds it when they leave.
    ///
    /// Saved per pawn rather than derived, because the whole point of the curve is that it
    /// **persists across leaving**. A thought with a timer resets; a hediff would work but adds
    /// a def and a body part to a system that is really just one number per person.
    ///
    /// Bounded by construction: the list only ever holds people who have pressure, and anybody
    /// who sheds back to zero is dropped from it. A colony that has never opened a gate carries
    /// an empty list and costs one comparison per interval.
    /// </summary>
    public sealed class BackroomsPressureComponent : GameComponent
    {
        private const int Interval = 60;

        /// <summary>Saved, in parallel. Pawn references and their accumulated ticks.</summary>
        private List<Pawn> pawns = new List<Pawn>();
        private List<int> pressure = new List<int>();

        /// <summary>
        /// Cached shelter rate per pawn, refreshed on a slower cadence than the tick.
        /// Not saved: it is re-derived from the world in under a second of game time, and a
        /// stale saved score would be a lie about a room the player has since rebuilt.
        /// </summary>
        private readonly Dictionary<Pawn, float> shelterCache = new Dictionary<Pawn, float>();
        private int nextShelterScan;

        public BackroomsPressureComponent(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref pawns, "rr_pressurePawns", LookMode.Reference);
            Scribe_Collections.Look(ref pressure, "rr_pressureTicks", LookMode.Value);
            Scribe_Collections.Look(ref occupiedCoordinates, "rr_pressureOccupiedCoordinates", LookMode.Value);
            if (Scribe.mode != LoadSaveMode.PostLoadInit) { return; }
            // A save from before this was recorded has no answer; whoever is already inside on
            // the first sweep is treated as having arrived before the save, not as a new arrival.
            if (occupiedCoordinates == null)
            {
                occupiedCoordinates = new List<string>();
                occupancyUnknownAfterLoad = true;
            }
            pawns = pawns ?? new List<Pawn>();
            pressure = pressure ?? new List<int>();
            // A dropped reference leaves a hole. Rebuild rather than trusting the pairing,
            // because a mismatched parallel list would assign one person's hours to another.
            for (int index = pawns.Count - 1; index >= 0; index--)
            {
                if (pawns[index] == null || index >= pressure.Count)
                {
                    pawns.RemoveAt(index);
                    if (index < pressure.Count) { pressure.RemoveAt(index); }
                }
            }
            while (pressure.Count > pawns.Count) { pressure.RemoveAt(pressure.Count - 1); }
        }

        public override void GameComponentTick()
        {
            int now = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;
            if (now % Interval != 0) { return; }

            bool rescoreShelter = now >= nextShelterScan;
            if (rescoreShelter)
            {
                nextShelterScan = now + BackroomsPressure.ScoreInterval;
                shelterCache.Clear();
            }

            // Everybody currently inside a coordinate gains; everybody on the list who is not
            // sheds. Walking the maps is cheaper than walking every pawn in the game, because a
            // colony with no open coordinate has no Backrooms map at all.
            var inside = new HashSet<Pawn>();
            List<Map> maps = Find.Maps;
            for (int mapIndex = 0; mapIndex < maps.Count; mapIndex++)
            {
                Map map = maps[mapIndex];
                if (!OddOriginService.IsBackroomsMap(map)) { continue; }
                IReadOnlyList<Pawn> present = map.mapPawns == null ? null : map.mapPawns.AllPawnsSpawned;
                if (present == null) { continue; }
                int occupantsHere = 0;
                for (int index = 0; index < present.Count; index++)
                {
                    Pawn pawn = present[index];
                    if (!Affected(pawn)) { continue; }
                    occupantsHere++;
                    inside.Add(pawn);
                    float rate;
                    if (!shelterCache.TryGetValue(pawn, out rate))
                    {
                        rate = BackroomsPressure.ShelterRateFor(pawn);
                        shelterCache[pawn] = rate;
                    }
                    Add(pawn, Mathf.Max(1, Mathf.RoundToInt(Interval * rate)));
                }
                NoteCoordinateHistory(map, occupantsHere);
            }
            // A coordinate whose map has gone is no longer occupied; forgetting it means a later
            // map for the same coordinate starts empty and its arrival is recorded.
            occupiedCoordinates.RemoveAll(id => !sweptCoordinates.Contains(id));
            sweptCoordinates.Clear();
            occupancyUnknownAfterLoad = false;

            for (int index = pawns.Count - 1; index >= 0; index--)
            {
                Pawn pawn = pawns[index];
                if (pawn == null) { Remove(index); continue; }
                if (inside.Contains(pawn)) { continue; }
                pressure[index] -= Mathf.RoundToInt(Interval * BackroomsPressure.RecoveryRateFor());
                if (pressure[index] <= 0) { Remove(index); }
            }
        }

        /// <summary>
        /// Records what this coordinate's own history is owed: one visit each time somebody
        /// arrives in a space that was empty, and worked time while anybody is in it.
        ///
        /// A visit is counted on the **empty-to-occupied transition** rather than on a gate
        /// opening, and the difference is deliberate: the owner's rule is that pressure rises
        /// from *operating history at that coordinate*, and a gate opened onto a space nobody
        /// walks into is not operating history. It also means the count cannot be inflated by
        /// cycling a gate from the safe side.
        ///
        /// Both figures are saved on the coordinate, so a revisit resumes rather than rerolls.
        /// </summary>
        private void NoteCoordinateHistory(Map map, int occupants)
        {
            var site = map.Parent as Generation.RimroomsDestinationMapParent;
            if (site == null) { return; }
            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { return; }
            CoordinateRecord coordinate = null;
            for (int index = 0; index < campaign.Coordinates.Count; index++)
            {
                if (campaign.Coordinates[index] != null &&
                    campaign.Coordinates[index].Id == site.CoordinateId)
                { coordinate = campaign.Coordinates[index]; break; }
            }
            if (coordinate == null) { return; }

            sweptCoordinates.Add(coordinate.Id);
            bool isOccupied = occupants > 0;
            bool wasOccupied;
            if (!occupiedLastSweep.TryGetValue(map, out wasOccupied))
            {
                // First sweep of this map since load: resume from the saved state, so occupants
                // who were already inside do not replay their arrival.
                wasOccupied = occupancyUnknownAfterLoad
                    ? isOccupied
                    : occupiedCoordinates.Contains(coordinate.Id);
            }
            if (isOccupied && !wasOccupied)
            {
                coordinate.NoteOpened();
                // Pushing deeper than the branch has ever been is a recorded progression step,
                // and it is the only thing that raises the encounter cap. Deliberately not
                // research and not wealth: wealth already feeds the ladder's ceiling, so using
                // it again here would double-count one input, and research is not an act of
                // exploration. The Backrooms never brings more against somebody than they went
                // looking for.
                campaignForHistory?.NoteDepthReached(coordinate.Depth);
                // Living inhabitants are placed on ARRIVAL, against the band as it stands right
                // now, rather than baked in at generation. That is what makes the ladder's
                // guarantees real: a first visit is genuinely quiet, and a band that rises
                // later genuinely shows.
                InhabitantService.PopulateOnArrival(map, coordinate);
                AnomalyEventService.OnArrival(map, coordinate);
                // "a feature that has moved since the last visit" - the one uncanny change
                // from UNIVERSE_ADAPTATION.md that had never been built. Runs after
                // NoteOpened so it can see that this is a return rather than a first visit.
                Generation.RevisitDisplacement.OnArrival(map, coordinate);
            }
            NoteLosses(map, coordinate);
            if (isOccupied) { coordinate.NoteOccupancy(Interval); }
            occupiedLastSweep[map] = isOccupied;
            if (isOccupied)
            { if (!occupiedCoordinates.Contains(coordinate.Id)) { occupiedCoordinates.Add(coordinate.Id); } }
            else { occupiedCoordinates.Remove(coordinate.Id); }
        }

        private static RimroomsCampaignComponent campaignForHistory
        {
            get
            {
                return Verse.Current.Game == null
                    ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            }
        }

        /// <summary>
        /// Records anybody of ours who has died inside this coordinate, so a later *missing*
        /// inhabitant can carry a name the player recognises.
        ///
        /// Read from corpses present rather than hooked into death, for the same reason the
        /// construction echo samples rather than hooks: it costs a bounded scan of an already
        /// short list, and it is correct for a body carried in from elsewhere and left here too.
        /// </summary>
        private static void NoteLosses(Map map, CoordinateRecord coordinate)
        {
            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || map.listerThings == null) { return; }
            List<Thing> corpses = map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse);
            if (corpses == null) { return; }
            for (int index = 0; index < corpses.Count; index++)
            {
                var corpse = corpses[index] as Corpse;
                if (corpse == null || corpse.InnerPawn == null) { continue; }
                Pawn dead = corpse.InnerPawn;
                // Only our own people count as lost. A generated body was never ours to lose.
                if (dead.Faction == null || !dead.Faction.IsPlayer) { continue; }
                if (dead.RaceProps == null || !dead.RaceProps.Humanlike) { continue; }
                campaign.NoteLostPawn(dead.LabelShortCap);
            }
        }

        /// <summary>
        /// Whether each Backrooms map had anybody in it on the previous sweep. Runtime only; the
        /// saved form is <see cref="occupiedCoordinates"/>, read on the first sweep after a load,
        /// because treating existing occupants as fresh arrivals would replay arrival effects.
        /// </summary>
        private readonly Dictionary<Map, bool> occupiedLastSweep = new Dictionary<Map, bool>();

        /// <summary>Saved. Coordinate ids that were occupied on the last sweep.</summary>
        private List<string> occupiedCoordinates = new List<string>();

        /// <summary>Not saved. Coordinate ids seen during the current sweep.</summary>
        private readonly HashSet<string> sweptCoordinates = new HashSet<string>();

        /// <summary>Not saved. True only after loading a save that predates the field above.</summary>
        private bool occupancyUnknownAfterLoad;

        /// <summary>
        /// Who the pressure applies to.
        ///
        /// The owner said *"all pawns in the backrooms"*, and the honest reading is everybody
        /// who does not belong there. A generated inhabitant is not unsettled by its own home,
        /// and applying this to natives would be both wrong and invisible, since nothing reads
        /// their mood. So: humanlike, mood-bearing, and **not native to the Backrooms** —
        /// which in practice is the player's people and anyone they carried in.
        /// </summary>
        private static bool Affected(Pawn pawn)
        {
            if (pawn == null || pawn.Dead || !pawn.Spawned) { return false; }
            if (pawn.RaceProps == null || !pawn.RaceProps.Humanlike) { return false; }
            if (pawn.needs == null || pawn.needs.mood == null) { return false; }
            Map origin = pawn.Map;
            if (origin == null) { return false; }
            // Anything whose own faction is hostile-native to a coordinate is left alone; the
            // player's colonists, prisoners, slaves and guests are all in scope.
            return pawn.Faction != null && pawn.Faction.IsPlayer;
        }

        private void Add(Pawn pawn, int ticks)
        {
            int index = pawns.IndexOf(pawn);
            if (index < 0)
            {
                pawns.Add(pawn);
                pressure.Add(0);
                index = pawns.Count - 1;
            }
            pressure[index] = Mathf.Min(BackroomsPressure.FullPressureTicks, pressure[index] + ticks);
        }

        private void Remove(int index)
        {
            pawns.RemoveAt(index);
            if (index < pressure.Count) { pressure.RemoveAt(index); }
        }

        /// <summary>Accumulated pressure for one person, in ticks. Zero when they have none.</summary>
        public int PressureFor(Pawn pawn)
        {
            if (pawn == null) { return 0; }
            int index = pawns.IndexOf(pawn);
            return index < 0 || index >= pressure.Count ? 0 : Math.Max(0, pressure[index]);
        }

        /// <summary>The live component, or null outside a game.</summary>
        public static BackroomsPressureComponent Current
        {
            get
            {
                return Verse.Current.Game == null
                    ? null : Verse.Current.Game.GetComponent<BackroomsPressureComponent>();
            }
        }
    }

    /// <summary>
    /// Turns accumulated pressure into the mood offset a pawn actually feels.
    ///
    /// A state thought rather than a memory, because the penalty must track the number
    /// continuously — rising while somebody is down there, falling once they are out — and a
    /// memory would need adding and removing by hand on every change.
    /// </summary>
    public sealed class ThoughtWorker_RRBackroomsPressure : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            BackroomsPressureComponent tracker = BackroomsPressureComponent.Current;
            if (tracker == null) { return ThoughtState.Inactive; }
            int penalty = BackroomsPressure.PenaltyFor(tracker.PressureFor(p));
            if (penalty <= 0) { return ThoughtState.Inactive; }
            // Stage 0 is -1, stage 9 is -10.
            return ThoughtState.ActiveAtStage(Mathf.Clamp(penalty - 1, 0, 9));
        }
    }
}
