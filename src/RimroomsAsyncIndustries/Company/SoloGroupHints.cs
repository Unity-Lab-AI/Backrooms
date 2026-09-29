using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// What the people who are already in say to themselves.
    ///
    /// **Owner answer, 2026-09-29, verbatim:** *"option three with hints like i need to contact
    /// someone about this crazy shit"*.
    ///
    /// ## Option three: there is no tutorial line here
    ///
    /// The solo/group start gets **no request line at all** until it reaches the corporation, and
    /// then the ordinary line begins. The reason is not difficulty, it is honesty: **nobody is
    /// helping them because nobody knows they exist.** A quest-giver would have to be invented, and
    /// inventing one would be the single most obvious lie this start could tell.
    ///
    /// ## So instead: hints, which describe rather than ask
    ///
    /// Owner, verbatim: *"this is all open eneded they can play how they choose"*. Every line below
    /// is something a person down there would think. **None of them is an objective.** Nothing is
    /// added to a list, nothing is tracked to completion, nothing notices whether the player acted
    /// on it, and nothing repeats. A hint that checked whether you obeyed it would be a quest
    /// wearing a costume.
    ///
    /// Each fires **once ever**, on a condition that is already true when it fires — so a player
    /// who worked it out first simply never hears the hint, which is the correct outcome rather
    /// than a missed step.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>The scenario these belong to. Its stable id; the label is "solo/group".</summary>
        private const string InsideScenarioId = "lone_survivor";

        /// <summary>Hints already said. Saved, because a thought twice is not a thought.</summary>
        private List<string> hintsSaid = new List<string>();

        internal void ExposeSoloGroupHints()
        {
            Scribe_Collections.Look(ref hintsSaid, "rr_hintsSaid", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && hintsSaid == null)
            { hintsSaid = new List<string>(); }
        }

        /// <summary>
        /// Checked on the company's cadence. Returns immediately for every start but this one, and
        /// for this one the moment contact is reached: after that the ordinary request line is the
        /// guidance and a second voice would only muddle it.
        /// </summary>
        internal void TickSoloGroupHints()
        {
            if (corporationContact) { return; }
            if (!string.Equals(scenarioId, InsideScenarioId, System.StringComparison.Ordinal)) { return; }
            if (hintsSaid == null) { hintsSaid = new List<string>(); }

            // A day inside before anybody says anything. Long enough that the first thing a player
            // hears is not a tooltip, short enough to arrive while it still means something.
            if (Find.TickManager.TicksGame < initializedTick + GenDate.TicksPerDay) { return; }

            // Keys are literals, not built from the id. `check-keyed-strings.py` refused the
            // concatenated version and was right to: a key assembled at runtime cannot be checked
            // in either direction, so a typo in one would have shipped as a raw key on screen.
            Say("contact", "RR_Hint_Contact", true);
            Say("surface", "RR_Hint_Surface", AnyoneOnAnOrdinaryMap());
            Say("comms", "RR_Hint_Comms", HasPoweredCommsConsole());
            Say("doorsRunOut", "RR_Hint_DoorsRunOut", KnowsACoordinateAtNaturalLimit());
        }

        /// <summary>
        /// One hint, once. The message is a plain Core message rather than a letter: a letter sits
        /// in the stack demanding to be dealt with, and these are thoughts, not business.
        /// </summary>
        private void Say(string id, string key, bool condition)
        {
            if (!condition || hintsSaid.Contains(id)) { return; }
            hintsSaid.Add(id);
            Messages.Message(key.Translate(), MessageTypeDefOf.NeutralEvent, false);
            RecordEvent("RR_Event_SoloGroupHint", id);
        }

        /// <summary>Somebody is standing somewhere that is not a Backrooms coordinate.</summary>
        private bool AnyoneOnAnOrdinaryMap()
        {
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                Pawn pawn = member == null ? null : member.pawn;
                if (pawn == null || !pawn.Spawned || pawn.Map == null) { continue; }
                if (!(pawn.Map.Parent is RimroomsDestinationMapParent)) { return true; }
            }
            return false;
        }

        /// <summary>
        /// A comms console the branch could actually call out on. Checked live rather than
        /// remembered, because the hint is only worth saying while it is true.
        /// </summary>
        private bool HasPoweredCommsConsole()
        {
            List<Map> maps = Find.Maps;
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || !OwnsMap(map) || map.listerBuildings == null) { continue; }
                List<Building> buildings = map.listerBuildings.allBuildingsColonist;
                for (int slot = 0; slot < buildings.Count; slot++)
                {
                    Building building = buildings[slot];
                    if (building == null || !building.Spawned || building.def == null) { continue; }
                    if (building.def.defName != "CommsConsole") { continue; }
                    CompPowerTrader power = building.TryGetComp<CompPowerTrader>();
                    if (power != null && power.PowerOn) { return true; }
                }
            }
            return false;
        }

        /// <summary>
        /// The branch has reached a coordinate as deep as found doors ever go, so the next step
        /// inward is a machine's job. Says so once; does not ask anybody to build one.
        /// </summary>
        private bool KnowsACoordinateAtNaturalLimit()
        {
            for (int index = 0; index < coordinates.Count; index++)
            {
                CoordinateRecord record = coordinates[index];
                if (record != null && record.Depth >= Portals.NaturalFrontierService.MaximumNaturalDepth)
                { return true; }
            }
            return false;
        }
    }
}
