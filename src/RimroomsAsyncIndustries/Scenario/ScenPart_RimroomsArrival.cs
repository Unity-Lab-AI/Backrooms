using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    /// <summary>
    /// One guarded native arrival. No retry may re-enumerate native starting-thing factories.
    ///
    /// **This class must never throw, and that is the whole lesson of the fourth launch.**
    /// Owner report, 2026-09-30, verbatim: *"i have no pawns on the map to control"*.
    ///
    /// `GenerateIntoMap` is called from Core's `GenStep_ScenParts`, and
    /// `MapGenerator.GenerateContentsIntoMap` abandons a gen step at its first exception. This
    /// method threw when the headquarters receipt was incomplete, so **Core's entire scenario
    /// step died and the player received no colonists and no starting supplies** -- confirmed
    /// against the live game: `rimworld/list_colonists` returned zero.
    ///
    /// A subclass of `ScenPart_PlayerPawnsArriveMethod` is an addition to Core's arrival, not a
    /// replacement for it. When our own part of the work is not ready, Core's still has to
    /// happen.
    /// </summary>
    public sealed class ScenPart_RimroomsArrival : ScenPart_PlayerPawnsArriveMethod
    {
        public override void GenerateIntoMap(Map map)
        {
            if (Find.GameInitData == null || ScenPart_RimroomsStart.Current == null ||
                map.Tile != Find.GameInitData.startingTile) { return; }
            HeadquartersSetupComponent receipt = map.GetComponent<HeadquartersSetupComponent>();
            if (receipt == null || receipt.receiptVersion != 2 || !receipt.setupComplete)
            {
                // The facility did not get built. Deliver Core's arrival anyway: the player
                // keeps the colonists and the supplies they chose, and the failed-startup
                // letter from PostGameStart tells them what is missing.
                Log.Error("[Rimrooms][Scenario] Headquarters receipt incomplete at arrival; " +
                    "falling back to the native arrival so the colony still has its people and stock.");
                if (receipt != null)
                {
                    // Recorded even on the fallback path, so a retry cannot grant stock twice.
                    if (receipt.arrivalStarted) { return; }
                    receipt.arrivalStarted = true;
                }
                try { base.GenerateIntoMap(map); }
                catch (Exception exception)
                { Log.Error("[Rimrooms][Scenario] Native arrival fallback interrupted: " + exception); }
                return;
            }
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
                    // **THE COMPANY'S OWN BOOKS GET THE COMPANY'S LABEL.** Owner,
                    // 2026-10-04: *"Mark the company-issued ones"*. This sweep is already
                    // enumerating exactly what Core created for this arrival, which is the
                    // only moment at which a book is known to have been issued rather than
                    // bought. Marking here means no later code has to go looking for books
                    // -- and so no later code can mistake a traded novel for one of ours.
                    Investigation.CompRouteEvidence issued =
                        thing.TryGetComp<Investigation.CompRouteEvidence>();
                    if (issued != null) { issued.MarkCompanyIssued(); }
                }
            }
        }
    }
}
