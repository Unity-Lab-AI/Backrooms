using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Investigation;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Expedition
{
    public static class ExpeditionCargo
    {
        // The return beacon was retired in 0.9.9-dev: the gate's own address book and the
        // saved return threshold already are the route authority, so the item had no job
        // left to do. Owner decision, asked at the fork.
        //
        // The survey tag left in 0.10.7-dev, and its six-per-crew requirement left with it.
        // Owner direction was *"lets not limit the amount"*, and a kit check that refuses to
        // dispatch a crew without exactly six of something is the same limit wearing a hat.
        // Markers are glow pods now: a player brings as many or as few as they like.
        //
        // The counts array carried a fourth entry the loop never read, left over from the
        // beacon. Arrays that disagree about their own length are a bug waiting for somebody
        // to add an item to one of them.
        // The sealed evidence case left in 0.10.9-dev with its requirement. Custody is a
        // shelf linked to a gate as a records archive, which is a place at headquarters
        // rather than an item a crew has to remember to carry out and back.
        //
        // And the field recorder left in 0.12.24-dev, which is the last of the four and the
        // one that closes this list. Its job folded into the record book a crew already
        // carries: one Core TextBook, taken in blank, written in in the field, carried home
        // as the evidence. The recorder and the record stop being two things that can get
        // separated -- which is the answer the 0.9.9-dev plan wrote down and never executed.
        //
        // The kit is one item and this mod does not author it. It is resolved through
        // CompRouteEvidence.NativeCarrierDef rather than by name, so a textbook that is not
        // Core's, or has lost our comp, or is some other mod's book, can never pass as
        // company gear. A pair of parallel arrays is gone with it; the comment above about
        // arrays that disagree about their own length no longer has anything to warn about.
        private const int RecordBooksRequired = 1;

        /// <summary>
        /// The one thing a crew must carry, and the game already ships it.
        ///
        /// Null when it cannot be resolved -- Core's book missing, our comp not patched on,
        /// another mod having replaced it -- and every caller refuses visibly on null rather
        /// than carrying on with no kit requirement at all. A silent null here would make the
        /// kit check pass for a crew carrying nothing, which is the same failure shape as
        /// Named&lt;TerrainDef&gt;("Carpet") returning null and a fallback making the wrong
        /// floor look deliberate for months.
        /// </summary>
        internal static ThingDef RecordBookDef { get { return CompRouteEvidence.NativeCarrierDef; } }

        public static CompanyActionResult CheckKit(IEnumerable<Pawn> crew, Map deployedSite = null, string coordinateId = null)
        {
            ThingDef book = RecordBookDef;
            if (book == null) { return CompanyActionResult.Refused("RR_Exp_MissingRecordBook"); }
            List<Pawn> pawns = crew.Where(p => p != null && !p.Destroyed).Distinct().ToList();
            return pawns.Sum(p => InventoryCount(p, book.defName)) +
                DeployedCount(book.defName, deployedSite, coordinateId) >= RecordBooksRequired
                ? CompanyActionResult.Applied()
                : CompanyActionResult.Refused("RR_Exp_MissingRecordBook");
        }

        public static CompanyActionResult CheckCapacity(Pawn pawn)
        {
            if (pawn == null || pawn.inventory == null || !MassUtility.CanEverCarryAnything(pawn))
            { return CompanyActionResult.Refused("RR_Exp_CannotCarry"); }
            float carried = pawn.carryTracker?.CarriedThing != null && !(pawn.carryTracker.CarriedThing is Pawn) && !(pawn.carryTracker.CarriedThing is Corpse)
                ? pawn.carryTracker.CarriedThing.GetStatValue(StatDefOf.Mass) * pawn.carryTracker.CarriedThing.stackCount : 0f;
            if (MassUtility.GearAndInventoryMass(pawn) + carried > MassUtility.Capacity(pawn) + 0.001f)
            { return CompanyActionResult.Refused("RR_Exp_OverCapacity"); }
            return CompanyActionResult.Applied();
        }

        public static CompanyActionResult QueuePickup(Pawn pawn, Thing item, int count)
        {
            if (!CanLoad(pawn) || item == null || !item.Spawned || item.Map != pawn.Map || item.IsForbidden(pawn) ||
                count < 1 || count > item.stackCount || !pawn.CanReserveAndReach(item, PathEndMode.ClosestTouch, Danger.Deadly, 10, count))
            { return CompanyActionResult.Refused("RR_Exp_PickupUnavailable"); }
            if (MassUtility.WillBeOverEncumberedAfterPickingUp(pawn, item, count))
            { return CompanyActionResult.Refused("RR_Exp_OverCapacity"); }
            Thing carried = pawn.carryTracker?.CarriedThing;
            float carriedMass = carried != null && !(carried is Pawn) && !(carried is Corpse)
                ? carried.GetStatValue(StatDefOf.Mass) * carried.stackCount : 0f;
            if (MassUtility.FreeSpace(pawn) < carriedMass + item.GetStatValue(StatDefOf.Mass) * count)
            { return CompanyActionResult.Refused("RR_Exp_OverCapacity"); }
            Job job = JobMaker.MakeJob(JobDefOf.TakeInventory, item);
            job.count = count;
            job.checkEncumbrance = true;
            pawn.inventory.UnloadEverything = false;
            return pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc, true)
                ? CompanyActionResult.Applied() : CompanyActionResult.Refused("RR_Exp_PickupUnavailable");
        }

        // Plans the complete missing shared kit before issuing native reserving pickup jobs.
        public static CompanyActionResult QueueLoadout(Map headquarters, List<Pawn> crew,
            IEnumerable<Pawn> existingKitOwners = null, Map deployedSite = null, string coordinateId = null)
        {
            if (headquarters == null || crew == null || crew.Count < 1 || crew.Count > 3 || crew.Distinct().Count() != crew.Count ||
                crew.Any(p => !CanLoad(p) || p.Map != headquarters))
            { return CompanyActionResult.Refused("RR_Exp_InvalidCrew"); }
            if (crew.Any(p => p.CurJob?.def == JobDefOf.TakeInventory || p.jobs.jobQueue.Any(q => q.job.def == JobDefOf.TakeInventory)))
            { return CompanyActionResult.Refused("RR_Exp_LoadPending"); }
            List<Pawn> kitOwners = (existingKitOwners ?? crew).Where(p => p != null && !p.Destroyed).Concat(crew).Distinct().ToList();
            var free = crew.ToDictionary(p => p, p =>
            {
                Thing carried = p.carryTracker?.CarriedThing;
                float mass = carried != null && !(carried is Pawn) && !(carried is Corpse)
                    ? carried.GetStatValue(StatDefOf.Mass) * carried.stackCount : 0f;
                return Math.Max(0f, MassUtility.FreeSpace(p) - mass);
            });
            var requests = new List<PickupRequest>();
            ThingDef def = RecordBookDef;
            if (def == null) { return CompanyActionResult.Refused("RR_Exp_MissingRecordBook"); }
            int remaining = Math.Max(0, RecordBooksRequired - kitOwners.Sum(p => InventoryCount(p, def.defName)) -
                DeployedCount(def.defName, deployedSite, coordinateId));
            // Mass comes from the item, never from a constant here. The register's cargo family
            // asks for exactly that -- *"preserve each mod's normal material and weight
            // behavior"* -- and a Core book weighs what Core says it weighs, not what this mod
            // would like it to.
            foreach (Thing item in headquarters.listerThings.ThingsOfDef(def).OrderBy(t => t.thingIDNumber))
            {
                if (remaining == 0) { break; }
                int available = item.stackCount;
                foreach (Pawn pawn in crew.OrderByDescending(p => free[p]))
                {
                    if (remaining == 0 || available == 0) { break; }
                    if (item.IsForbidden(pawn)) { continue; }
                    float mass = Math.Max(0.001f, item.GetStatValue(StatDefOf.Mass));
                    int count = Math.Min(remaining, Math.Min(available, (int)Math.Floor(free[pawn] / mass)));
                    if (count < 1 || !pawn.CanReserveAndReach(item, PathEndMode.ClosestTouch, Danger.Deadly, 10, count)) { continue; }
                    requests.Add(new PickupRequest { pawn = pawn, item = item, count = count });
                    remaining -= count;
                    available -= count;
                    free[pawn] -= mass * count;
                }
            }
            if (remaining > 0) { return CompanyActionResult.Refused("RR_Exp_LoadoutUnavailable"); }
            if (requests.Count == 0) { return CompanyActionResult.Existing(); }
            var ordered = new HashSet<Pawn>();
            foreach (PickupRequest request in requests)
            {
                Job job = JobMaker.MakeJob(JobDefOf.TakeInventory, request.item);
                job.count = request.count;
                job.checkEncumbrance = true;
                request.pawn.inventory.UnloadEverything = false;
                if (!request.pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc, ordered.Contains(request.pawn)))
                { return CompanyActionResult.Refused("RR_Exp_PickupPartiallyQueued"); }
                ordered.Add(request.pawn);
            }
            return CompanyActionResult.Applied();
        }

        private static bool CanLoad(Pawn pawn)
        {
            return pawn != null && pawn.Spawned && pawn.Faction == Faction.OfPlayer && !pawn.Dead && !pawn.Downed &&
                !pawn.InMentalState && pawn.inventory != null && pawn.jobs != null &&
                pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation);
        }

        private static int InventoryCount(Pawn pawn, string defName)
        { return pawn.inventory == null ? 0 : pawn.inventory.innerContainer.Where(t => t.def.defName == defName).Sum(t => t.stackCount); }

        /// <summary>
        /// Kit already put down at the site counts as kit the crew has.
        ///
        /// Nothing in the kit is deployable any more -- the survey tag was the only one, and
        /// it left in 0.10.7-dev -- so this is zero for every remaining entry. It is kept as
        /// the seam rather than deleted because the rule it expresses is still the right one:
        /// a crew that has already placed something has not lost it.
        /// </summary>
        private static int DeployedCount(string name, Map site, string coordinateId)
        {
            return 0;
        }

        internal static IEnumerable<Thing> HeldGear(Pawn pawn)
        {
            if (pawn.inventory != null) { foreach (Thing item in pawn.inventory.innerContainer) { yield return item; } }
            if (pawn.equipment != null) { foreach (Thing item in pawn.equipment.AllEquipmentListForReading) { yield return item; } }
            if (pawn.apparel != null) { foreach (Thing item in pawn.apparel.WornApparel) { yield return item; } }
            if (pawn.carryTracker?.CarriedThing != null && !(pawn.carryTracker.CarriedThing is Pawn)) { yield return pawn.carryTracker.CarriedThing; }
        }

        internal static void Capture(ExpeditionRecord run, IEnumerable<Pawn> members)
        {
            foreach (Pawn pawn in members)
            {
                foreach (Thing item in HeldGear(pawn))
                {
                    if (run.cargo.Any(e => e.item == item)) { continue; }
                    run.cargo.Add(new CargoManifestEntry { id = run.id + ":cargo:" + item.GetUniqueLoadID(), item = item,
                        itemLoadId = item.GetUniqueLoadID(), defName = item.def.defName, labelAtDeparture = item.LabelNoCount,
                        originalCarrier = pawn, originalCount = item.stackCount, originalHitPoints = item.HitPoints,
                        observedCount = item.stackCount, location = CargoLocation.WithCrew });
                }
            }
        }

        internal static void Reconcile(ExpeditionRecord run)
        {
            foreach (CargoManifestEntry entry in run.cargo)
            {
                Thing item = entry.item;
                if (item == null || item.Destroyed)
                { entry.observedCount = 0; entry.location = CargoLocation.Unresolved; }
                else
                {
                    entry.observedCount = item.stackCount;
                    entry.damaged = item.def.useHitPoints && item.HitPoints < entry.originalHitPoints;
                    if (item.MapHeld != null && item.MapHeld == run.headquarters) { entry.location = CargoLocation.Delivered; }
                    else if (item.MapHeld != null && item.MapHeld == run.destination)
                    { entry.location = item.Spawned ? CargoLocation.LeftAtSite : HeldByMember(run, item) ? CargoLocation.WithCrew : CargoLocation.AtSiteInContainer; }
                    else { entry.location = CargoLocation.Elsewhere; }
                }
                if (entry.declaration != CargoDisposition.Unspecified &&
                    !RimroomsExpeditionComponent.CargoDeclarationFitsObservation(run, entry, entry.declaration, entry.declaredCount))
                { entry.declarationNeedsReview = true; }
            }
        }

        private static bool HeldByMember(ExpeditionRecord run, Thing item)
        {
            IThingHolder holder = item.ParentHolder;
            var seen = new HashSet<IThingHolder>();
            while (holder != null && seen.Add(holder))
            {
                Pawn pawn = holder as Pawn;
                if (pawn != null && (run.crew.Contains(pawn) || run.rescueCrew.Contains(pawn) || run.recoveryPassengers.Contains(pawn))) { return true; }
                holder = holder.ParentHolder;
            }
            return false;
        }

        private sealed class PickupRequest { internal Pawn pawn; internal Thing item; internal int count; }
    }
}
