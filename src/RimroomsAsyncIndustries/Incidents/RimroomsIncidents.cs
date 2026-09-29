using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Incidents
{
    /// <summary>
    /// The storyteller half of the owner's decision at the fork, verbatim: ***"Both - guaranteed
    /// floor, storyteller flavour"***.
    ///
    /// ## Why this mod has incidents at all
    ///
    /// Until now **every event in this mod fired from its own component tick**, which meant that
    /// whichever storyteller the player chose had never heard of it. A mod that runs beside the
    /// game's event economy rather than inside it always reads as bolted on, and the owner's
    /// question named the reason exactly: *"the “AI” like ai thats not an ai that the
    /// storytellers use"*.
    ///
    /// **There is no intelligence in a storyteller to borrow.** A `StorytellerComp` rolls a
    /// mean-time-between against colony wealth and population and picks from a weighted
    /// `IncidentDef` list. The part that behaves like a director is <see cref="CanFireNowSub"/> --
    /// the conditions -- and that is ours to write without owning the slot.
    ///
    /// ## And why there is deliberately no StorytellerDef
    ///
    /// A `StorytellerDef` is an **exclusive slot**: the player picks exactly one. Shipping ours
    /// would mean asking somebody to give up Cassandra to play this mod, which is the opposite of
    /// the rule this whole project is built on. It also needs portrait art the no-new-art rule
    /// forbids. **Never add one.**
    ///
    /// ## What does NOT belong here
    ///
    /// **The clean-up team.** It is a guarantee -- *"so that facilities never die"* -- and a
    /// storyteller asks the two questions a guarantee does not admit: whether, and when. It stays
    /// deterministic in `FacilityRelief.cs`.
    ///
    /// **Incursion**, which is the one named exception to the founding rule and is bounded on five
    /// axes by `PortalTraversalPolicy`. An incident that also let something out of a gate would be
    /// a second door into the exception, and invariant 53 exists to keep there being one.
    ///
    /// **Anything inside a Backrooms coordinate.** What happens down there is the space's
    /// business, paced by arrival and depth. A storyteller has no view of it and should not.
    /// </summary>
    public abstract class IncidentWorker_Rimrooms : IncidentWorker
    {
        /// <summary>The branch, or null when this save has none. Most saves have none.</summary>
        protected static RimroomsCampaignComponent Branch
        {
            get
            {
                return Current.Game == null
                    ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            }
        }

        /// <summary>
        /// The shared floor: a live branch, and the incident aimed at that branch's own
        /// headquarters.
        ///
        /// **The headquarters check is not decoration.** A player may hold several maps, and a
        /// generated Backrooms coordinate is a map like any other. Without this, a storyteller
        /// could aim a company event at a coordinate, and every one of these events is written
        /// about the place the company lives.
        /// </summary>
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms)) { return false; }
            Map map = parms.target as Map;
            if (map == null) { return false; }
            RimroomsCampaignComponent campaign = Branch;
            return campaign != null && campaign.CanOperate && campaign.Headquarters == map;
        }
    }

    /// <summary>
    /// The space follows a crew home.
    ///
    /// A gate is a hole between a colony and somewhere that does not obey the same rules, and a
    /// branch that has been using one has been leaving it open. Occasionally the wrongness comes
    /// out the near side: the lights in the gate room go, or the room drops several degrees, or
    /// dirt that was not there is there now.
    ///
    /// **It runs the same four effects a coordinate runs**, through
    /// <see cref="AnomalyEventService.FireEffect"/>, because those bodies carry the four promises
    /// in invariant 28 -- readable warning, learnable rule, a countermeasure, and no unavoidable
    /// instant failure. A second copy of them at the headquarters would drift, and what would
    /// drift out are the promises.
    ///
    /// **Scoped to the room a gate stands in**, never the whole colony. That is what makes the
    /// rule learnable: it happens where the hole is, and a player who works that out can keep the
    /// gate room away from anything that minds the cold.
    /// </summary>
    public class IncidentWorker_RimroomsThresholdBleed : IncidentWorker_Rimrooms
    {
        /// <summary>
        /// Rearrangement is deliberately absent.
        ///
        /// In a coordinate, moving a loose item is a horror beat in a place the player is
        /// visiting. In a colony it would shuffle things inside somebody's stockpile, and the
        /// honest description of that is not "unsettling", it is "tedious". The three that remain
        /// are all answered by something the player already knows how to do: flick the switch,
        /// wear a coat, sweep the floor.
        /// </summary>
        private static readonly AnomalyEffect[] Effects =
        { AnomalyEffect.LightsFail, AnomalyEffect.ColdSnap, AnomalyEffect.Seepage };

        /// <summary>Milder than the deep coordinates this leaks out of. A colony has heaters.</summary>
        private const int ColdSnapDegrees = 8;
        private const int SeepageAmount = 10;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms)) { return false; }
            RimroomsCampaignComponent campaign = Branch;
            // The space cannot follow a crew home from somewhere the crew has never been. A
            // branch that has not visited a coordinate has nothing behind its gates yet.
            if (campaign.Coordinates == null || campaign.Coordinates.Count == 0) { return false; }
            return GateRoomCells(parms.target as Map).Count > 0;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = parms.target as Map;
            List<IntVec3> cells = GateRoomCells(map);
            if (cells.Count == 0) { return false; }

            // Invariant 26: sort ordinally before rolling. The effect list is fixed here, but the
            // habit is the point -- a candidate list that follows def or scan order produces
            // different outcomes on different mod lists.
            List<AnomalyEffect> candidates = new List<AnomalyEffect>(Effects);
            candidates.Sort((left, right) => string.CompareOrdinal(left.ToString(), right.ToString()));

            // Every effect is tried, in a rotated order, so a bleed that finds nothing to do --
            // a gate room with no lights in it, say -- becomes a different bleed rather than a
            // letter about nothing.
            int start = Rand.Range(0, candidates.Count);
            for (int step = 0; step < candidates.Count; step++)
            {
                AnomalyEffect effect = candidates[(start + step) % candidates.Count];
                int magnitude = effect == AnomalyEffect.ColdSnap ? ColdSnapDegrees : SeepageAmount;
                if (!AnomalyEventService.FireEffect(map, cells, effect, magnitude)) { continue; }
                SendStandardLetter(parms, new TargetInfo(cells[0], map));
                RimroomsCampaignComponent campaign = Branch;
                if (campaign != null) { campaign.RecordEvent("RR_Event_ThresholdBleed", campaign.BranchId); }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Every cell of every room holding a designated gate.
        ///
        /// **Designated only.** A natural gate has no operator, no power and no address book, and
        /// nothing about it is the company's doing — invariant 12. The bleed is a consequence of
        /// the branch working a hole, so it happens at the holes the branch made.
        /// </summary>
        private static List<IntVec3> GateRoomCells(Map map)
        {
            List<IntVec3> cells = new List<IntVec3>();
            if (map == null || map.listerBuildings == null) { return cells; }
            HashSet<Room> seen = new HashSet<Room>();
            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            for (int index = 0; index < buildings.Count; index++)
            {
                Building building = buildings[index];
                if (building == null || !building.Spawned) { continue; }
                CompRimroomsGate gate = building.TryGetComp<CompRimroomsGate>();
                if (gate == null || !gate.IsDesignated) { continue; }
                Room room = building.Position.GetRoom(map);
                if (room == null || room.UsesOutdoorTemperature || !seen.Add(room)) { continue; }
                foreach (IntVec3 cell in room.Cells)
                {
                    if (cell.InBounds(map)) { cells.Add(cell); }
                }
            }
            return cells;
        }
    }

    /// <summary>
    /// The parent corporation sends a crate nobody asked for.
    ///
    /// **Greed is the mechanism, not a contradiction** (`docs/CAMPAIGN_CHART.md` §4.3). An
    /// investor protecting an investment keeps the investment working, and this is the ordinary
    /// everyday face of the same character that sends a clean-up team when the worst happens.
    ///
    /// It is deliberately **modest** — a fraction of what the clean-up team brings, from the same
    /// table. A branch cannot live on it, and it is not meant to change how anybody plays; it is
    /// meant to be the thing a player points at when they describe what this company is like.
    /// </summary>
    public class IncidentWorker_RimroomsCorporationDelivery : IncidentWorker_Rimrooms
    {
        /// <summary>A courier's crate against a facility rebuild. Not a rescue.</summary>
        private const float CourierScale = 0.4f;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms)) { return false; }
            // Owner direction, verbatim: "clena up tema is only once u are in communication and
            // working with the corporation". A corporation that has not heard of this branch does
            // not send it anything, and for two of the three starts that silence is the point.
            return Branch.CorporationContact;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null) { return false; }

            List<Thing> payload = new List<Thing>();
            CompanySupplyDrop.Fill(payload, CourierScale);
            if (payload.Count == 0) { return false; }

            IntVec3 center;
            try { center = DropCellFinder.TradeDropSpot(map); }
            catch (Exception) { center = map.Center; }
            if (!center.IsValid || !center.InBounds(map)) { center = map.Center; }

            DropPodUtility.DropThingsNear(center, map, payload, 110, false, false, true, forbid: false);
            SendStandardLetter(parms, new TargetInfo(center, map));

            RimroomsCampaignComponent campaign = Branch;
            if (campaign != null) { campaign.RecordEvent("RR_Event_CorporationDelivery", campaign.BranchId); }
            return true;
        }
    }
}
