using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>One person's field history: how many trips, and which addresses.</summary>
    public sealed class ExposureRecord : IExposable
    {
        internal string crewLoadId;
        internal string crewName;
        internal int trips;
        internal int lastTripTick = -1;
        internal List<string> coordinateIds = new List<string>();

        public string Name { get { return crewName; } }
        public int Trips { get { return trips; } }
        public int LastTripTick { get { return lastTripTick; } }
        public IReadOnlyList<string> CoordinateIds { get { return coordinateIds; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref crewLoadId, "rr_exposureCrewLoadId");
            Scribe_Values.Look(ref crewName, "rr_exposureCrewName");
            Scribe_Values.Look(ref trips, "rr_exposureTrips", 0);
            Scribe_Values.Look(ref lastTripTick, "rr_exposureLastTripTick", -1);
            Scribe_Collections.Look(ref coordinateIds, "rr_exposureCoordinateIds", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && coordinateIds == null)
            { coordinateIds = new List<string>(); }
        }
    }

    /// <summary>
    /// Staff prior exposure. Who has been through a gate, how often, and to where.
    ///
    /// **Owner direction, verbatim:** *"Add configurable company roles, staff schedules,
    /// certifications, training jobs, field history, trust/stress/exposure and equipment
    /// familiarity"*, and on 2026-10-01: *"andf yes do those three things you listed as well"* —
    /// of which this is staff **prior exposure** affecting how an expedition goes. It has been a
    /// named open prep item across two separate rows for most of this project.
    ///
    /// ## Why nothing was recording it, which is the whole defect
    ///
    /// `NoteReturnedFromField` is the one place in the mod where *this person came back from
    /// there* is already established — and all it did was raise a **debrief hold**: transient,
    /// capped at a handful, and **deleted the moment the debrief happens**. So the fact existed
    /// for a few hours of game time and was then thrown away.
    ///
    /// That is the same shape as the contradictory-accounts defect at 0.12.25-dev: *"a mechanism
    /// that existed and threw the disagreement away"*. The fix is the same shape too — keep the
    /// fact, beside the thing that already knew it.
    ///
    /// ## This is a record, not a stat, and never a reference
    ///
    /// Identity is the pawn's **load id string**, never a `Pawn` field. A colonist who leaves,
    /// dies or is captured must not be held alive by the branch's paperwork, and the same
    /// reasoning retired every live reference from <see cref="LostPawnRegister"/>'s design.
    /// A name is carried alongside purely so a readout can say who, after they are gone.
    ///
    /// Unbounded on purpose: a branch's field history is the thing the player built, and
    /// discarding the oldest trips would make a veteran look like a novice. One record per
    /// person, and the address list inside it is deduplicated, so it grows with people and
    /// places rather than with time.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How much a personally experienced address takes off a dial, applied **once**.
        ///
        /// Deliberately shallower than the branch-level familiarity discount and deliberately
        /// **not compounding**: `SpinUpWorkRequiredFor` multiplies the branch factor once per
        /// previous connection, because a branch keeps records. A person is not a record — they
        /// have either walked it or they have not, and the tenth walk does not teach them the way
        /// a tenth filed report teaches the branch.
        /// </summary>
        public const float OperatorExposureFactor = 0.9f;

        private List<ExposureRecord> fieldExposure = new List<ExposureRecord>();

        internal void ExposeFieldExposure()
        {
            Scribe_Collections.Look(ref fieldExposure, "rr_fieldExposure", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && fieldExposure == null)
            { fieldExposure = new List<ExposureRecord>(); }
        }

        /// <summary>Everyone the branch has a field history for.</summary>
        public IReadOnlyList<ExposureRecord> FieldExposure { get { return fieldExposure; } }

        private ExposureRecord ExposureFor(Pawn pawn)
        {
            if (pawn == null || fieldExposure == null) { return null; }
            string loadId = pawn.GetUniqueLoadID();
            for (int index = 0; index < fieldExposure.Count; index++)
            {
                ExposureRecord record = fieldExposure[index];
                if (record != null && record.crewLoadId == loadId) { return record; }
            }
            return null;
        }

        /// <summary>
        /// Records that somebody came back from an address.
        ///
        /// **Called from <c>NoteReturnedFromField</c>**, which is the one place the fact is
        /// already known. Adding a second caller would mean a second definition of *came back*.
        /// </summary>
        internal void NoteFieldExposure(Pawn pawn, string coordinateId)
        {
            if (pawn == null) { return; }
            fieldExposure = fieldExposure ?? new List<ExposureRecord>();
            ExposureRecord record = ExposureFor(pawn);
            if (record == null)
            {
                record = new ExposureRecord
                {
                    crewLoadId = pawn.GetUniqueLoadID(),
                    coordinateIds = new List<string>(),
                };
                fieldExposure.Add(record);
            }
            // Refreshed every trip, so the readout names them as they are called now.
            record.crewName = pawn.LabelShortCap;
            record.trips++;
            record.lastTripTick = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;
            if (!string.IsNullOrEmpty(coordinateId)
                && !record.coordinateIds.Contains(coordinateId))
            { record.coordinateIds.Add(coordinateId); }
        }

        /// <summary>How many field trips this person has come back from. Zero for a novice.</summary>
        public int FieldTripsFor(Pawn pawn)
        {
            ExposureRecord record = ExposureFor(pawn);
            return record == null ? 0 : record.trips;
        }

        /// <summary>
        /// Whether this person has personally been to this address.
        ///
        /// **This is the question the gate asks.** Not how experienced they are in general —
        /// whether they have walked *this* route, which is what makes a dial faster.
        /// </summary>
        public bool HasBeenTo(Pawn pawn, string coordinateId)
        {
            if (string.IsNullOrEmpty(coordinateId)) { return false; }
            ExposureRecord record = ExposureFor(pawn);
            return record != null && record.coordinateIds != null
                && record.coordinateIds.Contains(coordinateId);
        }

        /// <summary>
        /// The dial discount an operator's own experience of an address earns, or 1 for none.
        ///
        /// Returns a multiplier rather than applying anything, so the gate stays the only thing
        /// that decides what spin-up work is — there is exactly one place that arithmetic lives.
        /// </summary>
        public float ExposureDialFactor(Pawn gateOperator, string coordinateId)
        {
            return HasBeenTo(gateOperator, coordinateId) ? OperatorExposureFactor : 1f;
        }
    }
}
