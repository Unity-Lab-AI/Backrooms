using System.Collections.Generic;
using RimroomsAsyncIndustries.ConnectedWork.Providers;
using Verse;

namespace RimroomsAsyncIndustries.ConnectedWork
{
    /// <summary>
    /// One kind of work that is done *at* the far site rather than carried to it. A
    /// provider answers exactly one question — is there work of my kind on that map
    /// that this worker could do — and never issues the work itself.
    ///
    /// That restraint is the whole design. Once a worker is standing on the destination
    /// map, Core's own work giver for that kind of work is already running there, in
    /// that pawn's own priority order, with every native check reading the map it is
    /// actually talking about. Reimplementing the work would mean reimplementing its
    /// reservations, its skill gates, its blocking-thing handling and its toils, and
    /// getting any of them subtly wrong. So a provider's whole job is to justify the
    /// crossing and then get out of the way.
    ///
    /// The two validation halves are separated exactly as they are for the adapters:
    ///
    /// * <see cref="HasCandidateWork"/> — a candidate predicate against an explicit
    ///   Map. It may read that map's own listers and the facts of the objects on it. It
    ///   may never call a native pawn-specific reachability, reservation or allowed-area
    ///   query for a map the worker is not standing on.
    /// * <see cref="HasWorkHere"/> — the definitive question, asked only of the map the
    ///   worker is physically on, where the native answers mean what they say.
    /// </summary>
    public abstract class ConnectedDeploymentProvider
    {
        /// <summary>Stable saved identity. Never renamed; new behaviour gets a new version.</summary>
        public abstract string ProviderId { get; }

        /// <summary>
        /// Bumped when this provider's rules change in a way a saved deployment cannot
        /// be trusted across. The component refuses to continue a deployment whose
        /// recorded version is not the current one.
        /// </summary>
        public abstract int ProviderVersion { get; }

        /// <summary>Which work the player sees this as; used for refusal and readout text.</summary>
        public abstract string LabelKey { get; }

        /// <summary>
        /// The work type this deployment is justified by, or null if that def is not
        /// present. A null work type makes the provider unavailable rather than
        /// throwing, like every other def lookup in this project.
        /// </summary>
        public abstract WorkTypeDef WorkType { get; }

        /// <summary>
        /// Whether this worker could do this kind of work at all. Map-independent by
        /// construction: it reads the pawn's own work settings and capabilities only, so
        /// it is safe to ask before any map is chosen.
        /// </summary>
        public abstract bool WorkerEligible(Pawn pawn);

        /// <summary>
        /// Bounded candidate search against an explicit map. Must examine a fixed
        /// maximum per call. A window that found nothing means "not this pass", never
        /// "never": planning is retried on a cooldown, so an optimistic miss costs one
        /// delay and a false positive costs a wasted walk.
        /// </summary>
        public abstract bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work);

        /// <summary>
        /// The definitive question, asked only of the map this worker is standing on.
        ///
        /// This one is deliberately *not* windowed. A bounded window that missed the
        /// work would release a deployment while there was still work to do, and the
        /// worker would be planned straight back across the gate — the exact thrash the
        /// record exists to prevent. The cost is the same as one pass of Core's own
        /// scanner for that work type, and it runs only for a worker already deployed.
        /// </summary>
        public abstract bool HasWorkHere(Pawn pawn);
    }

    /// <summary>
    /// The deployment providers that exist. Added one at a time with their own source
    /// evidence, exactly like the adapter families, rather than by a discovery sweep
    /// that would silently claim support for work nobody reviewed.
    /// </summary>
    public static class ConnectedDeploymentProviders
    {
        public const string ConstructionFinishing = "construction-finishing";
        public const string Research = "research";
        public const string Tending = "tending";
        public const string PatientFeeding = "patient-feeding";
        public const string RescueInPlace = "rescue-in-place";
        public const string Cleaning = "cleaning";
        public const string Repair = "repair";
        public const string Firefighting = "firefighting";
        public const string Mining = "mining";
        public const string Hunting = "hunting";
        public const string PlantCutting = "plant-cutting";
        public const string Growing = "growing";
        public const string Warden = "warden";
        public const string Childcare = "childcare";
        public const string AnimalHandling = "animal-handling";

        // Bill work is one family per work type, because Core distinguishes them itself:
        // `WorkGiver_DoBill.StartOrResumeBillJob` compares a recipe's `requiredGiverWorkType`
        // against `def.workType`, and a bench belongs to a work type only through its
        // `WorkGiverDef.fixedBillGiverDefs`. A single provider would have to declare one work
        // type and would pull a cook across a gate for smithing. See `BillWorkProvider`.
        public const string BillWorkCooking = "bill-work-cooking";
        public const string BillWorkCrafting = "bill-work-crafting";
        public const string BillWorkSmithing = "bill-work-smithing";
        public const string BillWorkTailoring = "bill-work-tailoring";
        public const string BillWorkArt = "bill-work-art";

        private static readonly ConstructionFinishingProvider construction =
            new ConstructionFinishingProvider();
        private static readonly ResearchProvider research = new ResearchProvider();
        private static readonly TendingProvider tending = new TendingProvider();
        private static readonly FeedingProvider feeding = new FeedingProvider();
        private static readonly RescueInPlaceProvider rescue = new RescueInPlaceProvider();
        private static readonly CleaningProvider cleaning = new CleaningProvider();
        private static readonly RepairProvider repair = new RepairProvider();
        private static readonly FirefightingProvider firefighting = new FirefightingProvider();
        private static readonly MiningProvider mining = new MiningProvider();
        private static readonly HuntingProvider hunting = new HuntingProvider();
        private static readonly PlantCuttingProvider plantcutting = new PlantCuttingProvider();
        private static readonly GrowingProvider growing = new GrowingProvider();
        private static readonly WardenProvider warden = new WardenProvider();
        private static readonly ChildcareProvider childcare = new ChildcareProvider();
        private static readonly AnimalHandlingProvider animalhandling = new AnimalHandlingProvider();
        private static readonly BillWorkProvider billCooking =
            new BillWorkProvider(BillWorkCooking, "Cooking", "RR_ConnectedWork_BillWorkCookingLabel");
        private static readonly BillWorkProvider billCrafting =
            new BillWorkProvider(BillWorkCrafting, "Crafting", "RR_ConnectedWork_BillWorkCraftingLabel");
        private static readonly BillWorkProvider billSmithing =
            new BillWorkProvider(BillWorkSmithing, "Smithing", "RR_ConnectedWork_BillWorkSmithingLabel");
        private static readonly BillWorkProvider billTailoring =
            new BillWorkProvider(BillWorkTailoring, "Tailoring", "RR_ConnectedWork_BillWorkTailoringLabel");
        private static readonly BillWorkProvider billArt =
            new BillWorkProvider(BillWorkArt, "Art", "RR_ConnectedWork_BillWorkArtLabel");
        private static readonly Dictionary<string, ConnectedDeploymentProvider> registry =
            new Dictionary<string, ConnectedDeploymentProvider>(System.StringComparer.Ordinal)
            {
                { ConstructionFinishing, construction },
                { Research, research },
                { Tending, tending },
                { PatientFeeding, feeding },
                { RescueInPlace, rescue },
                { Cleaning, cleaning },
                { Repair, repair },
                { Firefighting, firefighting },
                { Mining, mining },
                { Hunting, hunting },
                { PlantCutting, plantcutting },
                { Growing, growing },
                { Warden, warden },
                { Childcare, childcare },
                { AnimalHandling, animalhandling },
                { BillWorkCooking, billCooking },
                { BillWorkCrafting, billCrafting },
                { BillWorkSmithing, billSmithing },
                { BillWorkTailoring, billTailoring },
                { BillWorkArt, billArt }
            };

        public static IEnumerable<ConnectedDeploymentProvider> All { get { return registry.Values; } }

        public static ConnectedDeploymentProvider Get(string providerId)
        {
            ConnectedDeploymentProvider provider;
            return providerId != null && registry.TryGetValue(providerId, out provider) ? provider : null;
        }
    }
}
