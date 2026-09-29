using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>One guarded native arrival. No retry may re-enumerate native starting-thing factories.</summary>
    public sealed class ScenPart_RimroomsArrival : ScenPart_PlayerPawnsArriveMethod
    {
        public override void GenerateIntoMap(Map map)
        {
            if (Find.GameInitData == null || ScenPart_RimroomsStart.Current == null ||
                map.Tile != Find.GameInitData.startingTile) { return; }
            HeadquartersSetupComponent receipt = map.GetComponent<HeadquartersSetupComponent>();
            if (receipt == null || receipt.receiptVersion != 2 || !receipt.setupComplete)
            { throw new InvalidOperationException("[Rimrooms] Native arrival requires the prepared headquarters receipt."); }
            if (receipt.arrivalStarted) { return; }
            receipt.arrivalStarted = true;
            var before = new HashSet<Thing>(map.listerThings.AllThings);
            try
            {
                // Core creates the edited scenario supplies/possessions and places the actual selected pawns.
                base.GenerateIntoMap(map);
                if (receipt.staff.Any(p => p == null || !p.Spawned || p.Map != map || p.Faction != Faction.OfPlayer))
                { receipt.failure = "RR_Setup_ArrivalIncomplete"; return; }
                receipt.arrivalComplete = true;
            }
            catch (Exception exception)
            {
                receipt.failure = "RR_Setup_ArrivalIncomplete";
                Log.Error("[Rimrooms][Scenario] Native arrival interrupted; its receipt prevents a second stock grant: " + exception);
                // Preserve the generated map/known placements and show a failed-start report after map generation.
            }
            finally
            {
                // Record observed placements even when native creation/placement stopped partway through.
                // This is not a promise that an opaque native factory returned every requested item.
                foreach (Thing thing in map.listerThings.AllThings.Where(t => !before.Contains(t)).ToList())
                {
                    receipt.arrivalRecords.Add(thing.GetUniqueLoadID() + ":" + thing.def.defName + ":" + thing.stackCount);
                    if (thing.def.category == ThingCategory.Item) { thing.SetForbidden(false, false); }
                }
            }
        }
    }
}
