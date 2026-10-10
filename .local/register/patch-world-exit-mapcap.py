# -*- coding: utf-8 -*-
"""Add the owner's five-map cap to the world exit: claim under it, caravan over it."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Portals', 'WorldExit.cs')

s = io.open(PATH, encoding='utf-8-sig').read()

old_start = s.index('        public CompanyActionResult LeaveThroughWorldExit(Thing door)')
old_end = s.index('        /// <summary>\n        /// Who walks out:')

new = '''        /// <summary>
        /// The most maps this branch may hold at once, counting **everything**: its headquarters,
        /// every Backrooms coordinate currently loaded, every registered site, and every tile it
        /// has claimed by walking out of a door.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"but at that not a player can have up to
        /// five maps if settings are right so lets have that 5 map count be universal max for back
        /// rooms main map and claiming maps where u pop out and anything over 5 maps defaults to
        /// caravans"*.
        ///
        /// So five is **our** universal cap, and it sits **on top of** the player's own
        /// `Prefs.MaxNumberOfPlayerSettlements` rather than arguing with it. Whichever is stricter
        /// wins, which is the only reading that respects a setting the player chose.
        /// </summary>
        internal const int MaximumBranchMaps = 5;

        /// <summary>Every loaded map this branch holds, by the one ownership predicate.</summary>
        public int BranchMapCount
        {
            get
            {
                int count = 0;
                List<Map> maps = Find.Maps;
                if (maps == null) { return 0; }
                for (int index = 0; index < maps.Count; index++)
                {
                    if (OwnsMap(maps[index])) { count++; }
                }
                return count;
            }
        }

        /// <summary>
        /// Whether walking out may **claim** the tile as a map, or must form a caravan instead.
        ///
        /// Two gates, and the stricter one wins:
        ///
        /// * **Ours**, <see cref="MaximumBranchMaps"/> — five, counting the Backrooms coordinate
        ///   the crew is standing in as one of them, because the owner's cap is on maps held and a
        ///   coordinate is a map held.
        /// * **The player's**, `SettleUtility.PlayerSettlementsCountLimitReached`, which reads
        ///   `Prefs.MaxNumberOfPlayerSettlements`. Somebody who set that to one meant it.
        /// </summary>
        public bool CanClaimAnotherMap
        {
            get
            {
                if (!CanOperate) { return false; }
                if (BranchMapCount >= MaximumBranchMaps) { return false; }
                return !SettleUtility.PlayerSettlementsCountLimitReached;
            }
        }

        /// <summary>
        /// Walk out through this door.
        ///
        /// **Two outcomes, decided by the map cap**, per the owner's direction:
        ///
        /// | Maps held | What happens | Touches `PassToWorld` |
        /// |---|---|---|
        /// | under the cap | the tile is **claimed** and the crew walks onto a new map | **no** |
        /// | at or over it | the crew forms a **caravan** they control | yes |
        ///
        /// The claiming path is both the common case and the safer one: it never hands a pawn to
        /// the world pool at all, so the narrowed stranded-crew guarantee is not even reached
        /// until somebody is already holding five maps.
        ///
        /// **This is the only place in the mod that reaches Core's caravan formation or its
        /// settling, and it runs only from a player command.** No tick, work giver, incident or
        /// scheduler calls it, and `proof-world-exit.py` asserts it has exactly one caller.
        /// </summary>
        public CompanyActionResult LeaveThroughWorldExit(Thing door)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            WorldExitRecord record = WorldExitFor(door);
            if (record == null) { return CompanyActionResult.Refused("RR_WorldExit_NotHere"); }
            if (!record.DestinationValid)
            { return CompanyActionResult.Refused("RR_WorldExit_DestinationGone"); }
            if (door == null || !door.Spawned || door.Map == null)
            { return CompanyActionResult.Refused("RR_WorldExit_DoorUnavailable"); }

            Map map = door.Map;
            PlanetTile from = map.Tile;
            if (!from.Valid) { return CompanyActionResult.Refused("RR_WorldExit_NoAnchorTile"); }

            List<Pawn> leaving = TravellersAt(door);
            if (leaving.Count == 0) { return CompanyActionResult.Refused("RR_WorldExit_NobodyHere"); }

            CompanyActionResult result = CanClaimAnotherMap
                ? ClaimTileAndWalkOut(record, leaving)
                : FormCaravanAndWalkOut(record, from, leaving);
            if (!result.Success) { return result; }

            record.usedTick = Find.TickManager.TicksGame;
            RecordEvent("RR_Event_WorldExitUsed", record.id, leaving.Count.ToString());
            return result;
        }

        /// <summary>
        /// Claim the tile and put the crew on it.
        ///
        /// **The map is generated before anybody is despawned.** That ordering is the whole safety
        /// property: if settling or generation fails, nothing has moved and the way out is still
        /// there to try again. Invariant 55 — a transfer that can lose a pawn is a corruption, not
        /// a threat — so the risky window is one pawn wide and it puts them back if a spawn fails.
        ///
        /// Claiming uses `SettleUtility.AddNewHome`, Core's own settling, so the new map is an
        /// ordinary player settlement that every mod in the register already understands. Nothing
        /// bespoke, and no `PassToWorld` anywhere on this path.
        /// </summary>
        private CompanyActionResult ClaimTileAndWalkOut(WorldExitRecord record, List<Pawn> leaving)
        {
            PlanetTile tile = record.Tile;
            Settlement settlement;
            Map claimed;
            try
            {
                settlement = SettleUtility.AddNewHome(tile, Faction.OfPlayer);
                if (settlement == null) { return CompanyActionResult.Refused("RR_WorldExit_CouldNotClaim"); }
                claimed = GetOrGenerateMapUtility.GetOrGenerateMap(tile, null);
            }
            catch (System.Exception)
            {
                // Generation is the one step here that can throw, and it throws before any pawn
                // has been touched. Report it rather than leaving a half-claimed world.
                return CompanyActionResult.Refused("RR_WorldExit_CouldNotClaim");
            }
            if (claimed == null) { return CompanyActionResult.Refused("RR_WorldExit_CouldNotClaim"); }

            IntVec3 arrival = FindArrivalCell(claimed);
            if (!arrival.IsValid) { return CompanyActionResult.Refused("RR_WorldExit_NoArrivalCell"); }

            int moved = 0;
            for (int index = 0; index < leaving.Count; index++)
            {
                Pawn pawn = leaving[index];
                if (pawn == null || !pawn.Spawned) { continue; }
                Map origin = pawn.Map;
                IntVec3 was = pawn.Position;
                IntVec3 cell = CellFinder.RandomClosewalkCellNear(arrival, claimed, 6);
                if (!cell.IsValid || !cell.InBounds(claimed)) { cell = arrival; }
                pawn.DeSpawn();
                if (GenSpawn.Spawn(pawn, cell, claimed) == null)
                {
                    // Put them back rather than leaving anybody unspawned. The same rule the
                    // solo/group opening follows: a step that loses a person is worse than a step
                    // that does not happen.
                    GenSpawn.Spawn(pawn, was, origin);
                    continue;
                }
                moved++;
            }
            if (moved == 0) { return CompanyActionResult.Refused("RR_WorldExit_NobodyMoved"); }

            RecordEvent("RR_Event_WorldExitClaimed", record.id, settlement.Label);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Form a caravan instead, because the branch is already holding its five maps.
        ///
        /// **Core does the leaving.** `CaravanExitMapUtility.ExitMapAndCreateCaravan` despawns the
        /// pawns, forms the caravan, notifies the map and sets the route. Hand-rolling that is how
        /// a pawn gets lost, and it is also what every transport mod in the register's RR-OUT group
        /// already hooks into — Carryalls, Giddy-Up 2, Pack Mules, Alpha Vehicles Age of Sail.
        ///
        /// This is the **only** path in the mod that reaches `PassToWorld`, it is reached only when
        /// the map cap is already met, and it is reached only from a player's click.
        /// </summary>
        private CompanyActionResult FormCaravanAndWalkOut(WorldExitRecord record, PlanetTile from,
            List<Pawn> leaving)
        {
            Caravan formed = CaravanExitMapUtility.ExitMapAndCreateCaravan(
                leaving, Faction.OfPlayer, from, record.Tile, record.Tile, sendMessage: false);
            // A null caravan means Core refused and nobody has moved. Say so rather than
            // reporting a success that did not happen.
            if (formed == null) { return CompanyActionResult.Refused("RR_WorldExit_CouldNotForm"); }
            RecordEvent("RR_Event_WorldExitCaravan", record.id, formed.Label);
            return CompanyActionResult.Applied();
        }

        /// <summary>Somewhere standable on the claimed map. Core's own centre-out search.</summary>
        private static IntVec3 FindArrivalCell(Map map)
        {
            IntVec3 found;
            if (CellFinderLoose.TryFindRandomNotEdgeCellWith(10,
                cell => cell.Standable(map) && !cell.Fogged(map), map, out found))
            { return found; }
            return map.Center.Standable(map) ? map.Center : IntVec3.Invalid;
        }

'''

io.open(PATH, 'w', encoding='utf-8-sig', newline='').write(s[:old_start] + new + s[old_end:])
print('world exit: five-map cap added, claim under it and caravan over it')
