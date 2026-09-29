using System.Collections.Generic;
using RimroomsAsyncIndustries.ConnectedWork.Adapters;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// One work family's cross-map route. There is deliberately no generic adapter:
    /// a route planner that handed an arbitrary native WorkGiver a target on another
    /// map would be reading the wrong map's listers, regions and reservations, and
    /// Core's own HasJob methods can call their JobOn counterparts, so a speculative
    /// remote probe can have side effects. Each family therefore gets an explicit
    /// implementation with two clearly separated halves:
    ///
    /// * <see cref="TryPlan"/> — a *candidate* predicate only, written against an
    ///   explicit Map. It may read that map's own listers and storage settings. It
    ///   may never claim a native reservation, a pawn-specific access result or an
    ///   allowed-area result for a map the worker is not standing on.
    /// * <see cref="RevalidateAtFetchSide"/> and the job builders — the definitive
    ///   native validation, which runs only once the worker is physically on the
    ///   map in question, where the native checks mean what they say.
    ///
    /// Every adapter inherits the gate rule unchanged: this company's colonists may
    /// decide to cross in order to work; nothing else may ever decide anything about
    /// a gate, and anything that is not a colonist reaches the near side only as
    /// cargo in a colonist's hands.
    /// </summary>
    public abstract class ConnectedWorkAdapter
    {
        /// <summary>Stable saved identity. Never renamed; a new behaviour gets a new version.</summary>
        public abstract string AdapterId { get; }

        /// <summary>
        /// Bumped when this adapter's planning or execution rules change in a way a
        /// saved intent cannot be trusted across. The component refuses to continue
        /// an intent whose recorded version is not the current one, and closes it as
        /// cancelled rather than executing it under changed rules.
        /// </summary>
        public abstract int AdapterVersion { get; }

        /// <summary>Which work the player sees this as; used only for refusal text.</summary>
        public abstract string LabelKey { get; }

        /// <summary>
        /// Bounded candidate search. Returns an opened intent or null. Must examine a
        /// fixed maximum of candidates per call and must treat a pending route as
        /// "not yet", never as unreachable.
        /// </summary>
        public abstract ConnectedWorkIntent TryPlan(Pawn pawn, RimroomsConnectedWorkComponent work);

        /// <summary>
        /// Definitive native validation at the object's own map, called only when the
        /// worker is actually standing on it. Returns a keyed reason or null.
        /// </summary>
        public abstract string RevalidateAtFetchSide(ConnectedWorkIntent intent, Pawn pawn);

        /// <summary>The local segment that physically takes hold of the object.</summary>
        public abstract Job FetchJob(ConnectedWorkIntent intent, Pawn pawn);

        /// <summary>
        /// Definitive native validation at the destination, called only when the
        /// worker has actually arrived carrying the cargo. This is where the native
        /// storage, bill or patient decision is finally made, because only here do
        /// the native queries read the map they are talking about. Returns a keyed
        /// reason to close the intent, or null to proceed to <see cref="DeliverJob"/>.
        /// </summary>
        public abstract string RevalidateAtStoreSide(ConnectedWorkIntent intent, Pawn pawn);

        /// <summary>The local segment that finishes the work on the destination map.</summary>
        public abstract Job DeliverJob(ConnectedWorkIntent intent, Pawn pawn);

        /// <summary>
        /// How one of this adapter's own refusal keys ends an intent. The default is a
        /// failure, because a committed trip that stopped short is worth the player's
        /// attention. A family overrides this for the outcomes that are simply a
        /// finished trip with a different ending than planned.
        /// </summary>
        public virtual ConnectedWorkPhase TerminalPhaseFor(string failureKey)
        { return ConnectedWorkPhase.Failed; }
    }

    /// <summary>
    /// The families that exist. Adapters are added here one at a time, each with its
    /// own source evidence, rather than by a discovery sweep that would silently
    /// claim support for work nobody reviewed.
    /// </summary>
    public static class ConnectedWorkAdapters
    {
        public const string StorageHauling = "storage-hauling";
        public const string CasualtyRescue = "casualty-rescue";
        public const string ConstructionSupply = "construction-supply";
        public const string BillIngredients = "bill-ingredients";
        public const string MedicineSupply = "medicine-supply";

        private static readonly ConnectedHaulingAdapter hauling = new ConnectedHaulingAdapter();
        private static readonly ConnectedCasualtyAdapter casualties = new ConnectedCasualtyAdapter();
        private static readonly ConnectedConstructionAdapter construction = new ConnectedConstructionAdapter();
        private static readonly ConnectedBillAdapter bills = new ConnectedBillAdapter();
        private static readonly ConnectedMedicineAdapter medicine = new ConnectedMedicineAdapter();
        private static readonly Dictionary<string, ConnectedWorkAdapter> registry =
            new Dictionary<string, ConnectedWorkAdapter>(System.StringComparer.Ordinal)
            {
                { StorageHauling, hauling },
                { CasualtyRescue, casualties },
                { ConstructionSupply, construction },
                { BillIngredients, bills },
                { MedicineSupply, medicine }
            };

        public static IEnumerable<ConnectedWorkAdapter> All { get { return registry.Values; } }

        public static ConnectedWorkAdapter Get(string adapterId)
        {
            ConnectedWorkAdapter adapter;
            return adapterId != null && registry.TryGetValue(adapterId, out adapter) ? adapter : null;
        }
    }
}
