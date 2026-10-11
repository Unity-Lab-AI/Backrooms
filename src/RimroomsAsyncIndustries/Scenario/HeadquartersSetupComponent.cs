using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>RR-SCEN: physical setup receipt survives a refused company initialization.</summary>
    public sealed class HeadquartersSetupComponent : MapComponent
    {
        public int receiptVersion = 1;
        public string startDefName;
        public bool setupStarted;
        public bool setupComplete;
        public bool branchInitialized;

        /// <summary>
        /// Whether the start's opening (the inside start or the natural gate) finished. Separate
        /// from <see cref="branchInitialized"/> so a failed opening can be retried. Read as true
        /// on saves that predate it, which only ever saved after a finished start.
        /// </summary>
        public bool openingComplete;

        /// <summary>The coordinate a first opening attempt created, reused by a retry.</summary>
        public string openingCoordinateId;
        public string failure;
        public List<Pawn> staff = new List<Pawn>();
        public List<string> staffRoles = new List<string>();
        public List<string> placedRecords = new List<string>();
        public bool arrivalStarted;
        public bool arrivalComplete;
        public List<string> arrivalRecords = new List<string>();
        public List<string> acceptedSupplies = new List<string>();

        /// <summary>
        /// What the scenario **promised** the player would start with, in its own words.
        ///
        /// ## Why this exists, and why it is a promise rather than a count
        ///
        /// **Owner report, verbatim:** *"they need to properly spawn in with starting goods"* and
        /// *"my preparecarfully mod food did not appear"*. A 9,216-cell sweep of the live game
        /// found **none** of the Store start's seven `ScenPart_StartingThing_Defined` grants while
        /// every one of its fixtures was present, so the layout ran and the grants did not.
        ///
        /// **Four candidate causes were eliminated by reading the installed game rather than
        /// guessing**, and none of them is it:
        ///
        /// * *the arrival part is missing* — it is not. `ScenPart_RimroomsArrival` **subclasses**
        ///   `ScenPart_PlayerPawnsArriveMethod` and calls `base.GenerateIntoMap`, which is the one
        ///   place in the game that collects `PlayerStartingThings()` and places it.
        /// * *the start spot is wrong* — it is not. Core's `FindPlayerStartSpot` is order 850 and
        ///   only picks a spot when none is valid; ours is set at 800 and kept.
        /// * *the gen steps run out of order* — they do not. Core's `ScenParts` is order **875**,
        ///   after both.
        /// * *the pawns arrive by pod and scatter* — they do not. `PlayerPawnsArriveMethod.Standing`
        ///   is enum zero **and** the scenarios set it explicitly, so the drop is instant.
        ///
        /// And the report's own evidence rules out the obvious remaining one: the pawns'
        /// `MealSurvivalPack` **possessions did arrive**, and possessions travel in the same list
        /// as the grants, through the same `DropThingGroupsNear` call. So the placement ran and
        /// the grants were not in the list it placed.
        ///
        /// ## So this is a diagnostic, not a fix, and that is deliberate
        ///
        /// The queue row says it plainly: *"no fix was written on a hunch"*. What is left needs a
        /// launch — most likely something in the 294-mod profile re-entering the starting-thing
        /// path, which is exactly what *"my preparecarfully mod food did not appear"* points at.
        /// **This makes the next launch answer the question instead of posing it again:** the
        /// promise and the delivery are both recorded on the receipt, and the start reports the
        /// difference.
        ///
        /// Read from `ScenPart.GetSummaryListEntries("PlayerStartsWith")`, which is public, and
        /// which **creates nothing**. Enumerating `PlayerStartingThings()` a second time would
        /// manufacture a second set of goods — the exact double-grant this receipt exists to
        /// prevent, and the reason `ScenPart_RimroomsArrival` says *"no retry may re-enumerate
        /// native starting-thing factories"*.
        /// </summary>
        public List<string> promisedGrants = new List<string>();

        /// <summary>
        /// Item defNames the arrival actually put on the map, counted.
        ///
        /// Separate from <see cref="arrivalRecords"/>, which records every thing including the
        /// pawns and carries load ids. This is the short list a player can be shown.
        /// </summary>
        public List<string> deliveredGrants = new List<string>();

        public HeadquartersSetupComponent(Map map) : base(map) { }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref receiptVersion, "rr_receiptVersion", 1, true);
            Scribe_Values.Look(ref startDefName, "rr_startDefName");
            Scribe_Values.Look(ref setupStarted, "rr_setupStarted");
            Scribe_Values.Look(ref setupComplete, "rr_setupComplete");
            Scribe_Values.Look(ref branchInitialized, "rr_branchInitialized");
            Scribe_Values.Look(ref openingComplete, "rr_openingComplete", true);
            Scribe_Values.Look(ref openingCoordinateId, "rr_openingCoordinateId");
            Scribe_Values.Look(ref failure, "rr_setupFailure");
            Scribe_Collections.Look(ref staff, "rr_startStaff", LookMode.Reference);
            Scribe_Collections.Look(ref staffRoles, "rr_startRoles", LookMode.Value);
            Scribe_Collections.Look(ref placedRecords, "rr_placedRecords", LookMode.Value);
            Scribe_Values.Look(ref arrivalStarted, "rr_arrivalStarted");
            Scribe_Values.Look(ref arrivalComplete, "rr_arrivalComplete");
            Scribe_Collections.Look(ref arrivalRecords, "rr_arrivalRecords", LookMode.Value);
            Scribe_Collections.Look(ref acceptedSupplies, "rr_acceptedSupplies", LookMode.Value);
            Scribe_Collections.Look(ref promisedGrants, "rr_promisedGrants", LookMode.Value);
            Scribe_Collections.Look(ref deliveredGrants, "rr_deliveredGrants", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                staff = staff ?? new List<Pawn>();
                staffRoles = staffRoles ?? new List<string>();
                placedRecords = placedRecords ?? new List<string>();
                arrivalRecords = arrivalRecords ?? new List<string>();
                acceptedSupplies = acceptedSupplies ?? new List<string>();
                // A save written before the grant diagnostic existed has neither list, and an
                // empty promise is honestly "we did not record one" rather than "nothing was
                // promised" -- which is why the report below only speaks when the promise is
                // non-empty.
                promisedGrants = promisedGrants ?? new List<string>();
                deliveredGrants = deliveredGrants ?? new List<string>();
            }
        }
    }
}
