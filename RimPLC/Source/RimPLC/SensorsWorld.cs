using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// Inventory section D (2026-10-13): pawn setup, trade, caravans, pods, quests, pens, power nets, storage, ideology
    /// roles/rituals and visitors (Hospitality). Normal cadence, each block guarded on its own; a key that cannot be read
    /// is left out, never a fake 0.
    /// Mod register checked before building (docs/research/mod-register-integration-fields-2026-09-29.csv): Simple
    /// sidearms (sidearms live in the inventory -- the setup check reads both), Wall Orbital Trade Beacon (beacons are
    /// counted by class, not def name), No Quests Without Comms (comms_consoles is read next to the quest counts),
    /// Hospitality (Continued) / Invite to Stay / Storefront and Real Faction Guest (guests read through vanilla guest
    /// state; guest beds by class name), the storage family (Adaptive/LWM/Warehouse/RimFridge: storage counted by
    /// Building_Storage, so modded shelves count), More filters for animals' pen (pens are the vanilla pen marker).
    /// All read-only: nothing here patches or changes another mod.
    /// </summary>
    public static class SensorsWorld
    {
        public static void Read(Dictionary<string, object> st, Map home, List<Pawn> crew)
        {
            if (home == null) return;
            Guard(() => Setup(st, crew));
            Guard(() => Trade(st, home));
            Guard(() => Caravans(st));
            Guard(() => Pods(st, home));
            Guard(() => Quests(st));
            Guard(() => Pens(st, home));
            Guard(() => PowerNets(st, home));
            Guard(() => Storage(st, home));
            Guard(() => Ideology(st, home));
            Guard(() => Visitors(st, home));
        }

        private static void Guard(Action a)
        {
            try { a(); }
            catch (Exception) { }
        }

        private static int Count(Map home, string defName)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            return d == null ? -1 : home.listerThings.ThingsOfDef(d).Count;
        }

        /// <summary>
        /// pawns_unconfigured: colonists whose setup has never been complete. A pawn is set up when, at one scan, it is
        /// armed with a primary and a melee sidearm (violent pawns), hostility response Attack (violent pawns), self-tend
        /// on (pawns who can doctor), works at least one job, and has the no-drug policy (owner: "drugs are for
        /// hospitality guests"). Once set up, the pawn is remembered in the save (RimPLCGameComponent.ConfiguredPawns) so
        /// a dropped weapon later is the unarmed rung's job, not a "never configured" warning.
        /// </summary>
        private static void Setup(Dictionary<string, object> st, List<Pawn> crew)
        {
            RimPLCGameComponent comp = RimPLCGameComponent.Get();
            if (comp == null) return;
            int open = 0;
            foreach (Pawn p in crew)
            {
                string id = p.GetUniqueLoadID();
                if (comp.ConfiguredPawns.Contains(id)) continue;
                if (IsSetUp(p)) comp.ConfiguredPawns.Add(id);
                else open++;
            }
            st["pawns_unconfigured"] = (double)open;
        }

        public static bool IsSetUp(Pawn p)
        {
            bool violent = !p.WorkTagIsDisabled(WorkTags.Violent);
            if (violent)
            {
                if (p.equipment?.Primary == null) return false;
                bool melee = (p.equipment.AllEquipmentListForReading.Any(e => e.def.IsMeleeWeapon)) ||
                             (p.inventory?.innerContainer.Any(t => t.def.IsMeleeWeapon) ?? false);
                if (!melee) return false;
                if (p.playerSettings == null || p.playerSettings.hostilityResponse != HostilityResponseMode.Attack) return false;
            }
            if (!p.WorkTypeIsDisabled(WorkTypeDefOf.Doctor) && (p.playerSettings == null || !p.playerSettings.selfTend)) return false;
            if (p.workSettings == null || !p.workSettings.EverWork) return false;
            if (!DefDatabase<WorkTypeDef>.AllDefsListForReading.Any(w => w.visible && p.workSettings.GetPriority(w) > 0)) return false;
            // the policy label is what the player sees ("No drugs" in Core); a renamed policy needs the word "no"
            string drug = p.drugs?.CurrentPolicy?.label ?? "";
            if (drug.IndexOf("no", StringComparison.OrdinalIgnoreCase) < 0) return false;
            return true;
        }

        private static void Trade(Dictionary<string, object> st, Map home)
        {
            st["trade_ships_in_orbit"] = (double)home.passingShipManager.passingShips.Count;
            st["trade_beacons"] = (double)home.listerBuildings.allBuildingsColonist.Count(b => b is Building_OrbitalTradeBeacon);
            st["comms_consoles"] = (double)home.listerBuildings.allBuildingsColonist.Count(b => b is Building_CommsConsole);
            st["silver"] = (double)home.resourceCounter.Silver;
        }

        private static void Caravans(Dictionary<string, object> st)
        {
            List<Caravan> mine = Find.WorldObjects.Caravans.Where(c => c.IsPlayerControlled).ToList();
            st["caravans_out"] = (double)mine.Count;
            st["caravan_pawns_out"] = (double)mine.Sum(c => c.PawnsListForReading.Count(p => p.IsColonist));
        }

        private static void Pods(Dictionary<string, object> st, Map home)
        {
            int pods = Count(home, "TransportPod"), launchers = Count(home, "PodLauncher");
            if (pods >= 0) st["transport_pods"] = (double)pods;
            if (launchers >= 0) st["pod_launchers"] = (double)launchers;
        }

        private static void Quests(Dictionary<string, object> st)
        {
            List<Quest> qs = Find.QuestManager.QuestsListForReading;
            st["quests_active"] = (double)qs.Count(q => q.State == QuestState.Ongoing && !q.hidden);
            st["quests_offered"] = (double)qs.Count(q => q.State == QuestState.NotYetAccepted && !q.hidden);
        }

        private static void Pens(Dictionary<string, object> st, Map home)
        {
            int pens = 0, outside = 0;
            foreach (Building b in home.listerBuildings.allBuildingsColonist)
                if (b.TryGetComp<CompAnimalPenMarker>() != null) pens++;
            foreach (Pawn a in home.mapPawns.SpawnedColonyAnimals)
                if (AnimalPenUtility.NeedsToBeManagedByRope(a) && AnimalPenUtility.GetCurrentPenOf(a, false) == null) outside++;
            st["pen_markers"] = (double)pens;
            st["pen_animals_unpenned"] = (double)outside;
        }

        /// <summary>Conduit routing: power nets that have consumers but no live source (a cut or unrouted conduit).</summary>
        private static void PowerNets(Dictionary<string, object> st, Map home)
        {
            int nets = 0, dead = 0;
            foreach (PowerNet n in home.powerNetManager.AllNetsListForReading)
            {
                if (n.powerComps.Count == 0) continue;
                nets++;
                if (!n.HasActivePowerSource) dead++;
            }
            st["power_nets"] = (double)nets;
            st["power_nets_dead"] = (double)dead;
        }

        /// <summary>Stockpiles and storage buildings; how many have the same filter as the first (storage copy).</summary>
        private static void Storage(Dictionary<string, object> st, Map home)
        {
            List<Zone_Stockpile> piles = home.zoneManager.AllZones.OfType<Zone_Stockpile>().ToList();
            st["stockpiles"] = (double)piles.Count;
            st["storage_buildings"] = (double)home.listerBuildings.allBuildingsColonist.Count(b => b is Building_Storage);
            st["stockpiles_default_priority"] = (double)piles.Count(z => z.settings.Priority == StoragePriority.Normal);
        }

        private static void Ideology(Dictionary<string, object> st, Map home)
        {
            if (!ModsConfig.IdeologyActive) return;
            Ideo ideo = Faction.OfPlayer?.ideos?.PrimaryIdeo;
            if (ideo == null) return;
            List<Precept_Role> roles = ideo.RolesListForReading;
            st["ideo_roles"] = (double)roles.Count;
            st["ideo_roles_unassigned"] = (double)roles.Count(r => r.ChosenPawnSingle() == null);
            st["ideo_leader_assigned"] = roles.Any(r => r.def.leaderRole && r.ChosenPawnSingle() != null);
            st["ritual_spots"] = (double)Math.Max(0, Count(home, "RitualSpot"));
            st["ideo_rituals"] = (double)ideo.PreceptsListForReading.OfType<Precept_Ritual>().Count();
        }

        /// <summary>Visitors and Hospitality guests. Guest beds by class name: Hospitality's Building_GuestBed
        /// (UNVERIFIED class name, from the Hospitality source; no Hospitality reference is compiled in).</summary>
        private static void Visitors(Dictionary<string, object> st, Map home)
        {
            int visitors = 0, guests = 0;
            foreach (Pawn p in home.mapPawns.AllPawnsSpawned)
            {
                if (!p.RaceProps.Humanlike || p.Faction == null || p.Faction.IsPlayer || p.IsPrisoner || p.IsSlave) continue;
                if (p.HostileTo(Faction.OfPlayer)) continue;
                visitors++;
                if (p.guest != null && p.guest.HostFaction == Faction.OfPlayer) guests++;
            }
            st["visitors"] = (double)visitors;
            st["hospitality_guests"] = (double)guests;
            st["guest_beds"] = (double)home.listerBuildings.allBuildingsColonist.Count(b =>
                b.def.thingClass != null && b.def.thingClass.Name.IndexOf("GuestBed", StringComparison.Ordinal) >= 0);
        }
    }
}
