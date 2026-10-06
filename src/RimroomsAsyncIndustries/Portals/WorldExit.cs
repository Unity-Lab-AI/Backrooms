using System.Collections.Generic;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// A way out of the Backrooms that leads to a world tile the branch does not hold.
    ///
    /// ## The gap this fills
    ///
    /// A found way out has always needed a **marked door on a map the branch already owns**. With
    /// nothing marked, `TryRecordWayOut` returned null and the door led deeper instead — so a
    /// branch with no marked anchor could never find a way out **at all**. That is worse than the
    /// row that described this as a missing feature suggested: it was a dead end for exactly the
    /// player least equipped to deal with one.
    ///
    /// ## Why this is a caravan or a CLAIMED tile, never a new world object
    ///
    /// Core already has *"people standing on a world tile you do not own"*, and it is a caravan.
    /// A new `WorldObjectDef` would duplicate that and fight the four Settled transport mods the
    /// register's **RR-OUT** trace groups around this exact feature: Carryalls intercontinental
    /// transport (row 61), Giddy-Up 2 (98), Pack Mules Extended (159) and Alpha Vehicles Age of
    /// Sail (266). All four already integrate with caravans. None integrates with a bespoke world
    /// object of ours.
    ///
    /// **A claimed tile is not that, and this file always claimed one.** Under the map cap,
    /// <see cref="RimroomsCampaignComponent.ClaimTileAndWalkOut"/> calls Core's own
    /// `SettleUtility.AddNewHome` and `GetOrGenerateMap`, so the crew walks onto an ordinary
    /// player settlement every mod in the register already understands. **Nothing here touches
    /// world generation** — an earlier phrasing of this comment implied it did, and that was
    /// overstated: no planet, biome or tile-validity rule is altered by settling a tile Core
    /// chose.
    ///
    /// **Acquisition stays RimWorld's; recognition is ours** — the same rule arc 5 settled for
    /// remote sites.
    ///
    /// ## And the trip is two-way as of 2026-10-03
    ///
    /// Owner: *"currently and incorrectyl there is no way for a pawn to go back into the backrooms
    /// when they exit via a natural gate"*. It was one-way by construction — `LeaveThroughWorldExit`
    /// was the only direction, while `WorldExitRecord` had been saving `coordinateId` and
    /// `doorLoadId` all along with nothing reading them. The claimed path now builds a marked Core
    /// `Door` on the arrival map and registers an `Emergence` edge home **before anybody is
    /// despawned**, so a failure leaves the crew where they were. See
    /// <see cref="RimroomsCampaignComponent.EstablishReturnGate"/>.
    ///
    /// **The caravan path is still one-way, and that is the owner's own earlier rule** — *"anything
    /// over 5 maps defaults to caravans"*. A caravan has no map for a gate to stand on; it walks
    /// home overland, which is what a caravan is for.
    ///
    /// ## The guarantee this narrows, and exactly how far
    ///
    /// The stranded-crew guarantee says **no gate source may ever call `PassToWorld`**, because a
    /// pawn in the world pool is alive and no longer the player's. Forming a caravan calls it —
    /// Core's own `ExitMapAndCreateCaravan` does, unavoidably, for every caravan RimWorld makes.
    ///
    /// **Owner decision, 2026-09-29: build it, because a player caravan is still yours.** The
    /// guarantee exists so the mod never *takes* a crew. A player-faction caravan is fully the
    /// player's — they move it, bring it home, settle it. So the narrowing is precise and the
    /// forbidden cases are unchanged and still asserted:
    ///
    /// | Path | May call `PassToWorld` |
    /// |---|---|
    /// | a gate **closing** on a crew | **never** |
    /// | a return **window expiring** | **never** |
    /// | any **traversal** or crossing | **never** |
    /// | **this**, and only on a player command | yes, into a caravan they control |
    ///
    /// Nothing automatic can reach this code. There is no tick, no work giver and no incident
    /// that calls it: <see cref="RimroomsCampaignComponent.LeaveThroughWorldExit"/> runs from a
    /// gizmo the player clicks, and `proof-world-exit.py` asserts that it has exactly one caller.
    /// </summary>
    public sealed class WorldExitRecord : IExposable
    {
        internal string id;
        internal string coordinateId;
        internal string doorLoadId;

        /// <summary>
        /// The destination, split into its two ints.
        ///
        /// `PlanetTile` is a readonly struct and **not** `IExposable`, and its `layerId` is
        /// private, so it cannot be saved directly. Both halves are stored and the tile is
        /// rebuilt — losing the layer would put a crew on the wrong planet layer, which is the
        /// kind of thing that looks like a teleport bug rather than a save bug.
        /// </summary>
        internal int tileId = -1;
        internal int layerId;

        internal int foundTick = -1;
        internal int usedTick = -1;

        public string Id { get { return id; } }
        public string CoordinateId { get { return coordinateId; } }
        public string DoorLoadId { get { return doorLoadId; } }
        public int FoundTick { get { return foundTick; } }
        public bool Used { get { return usedTick >= 0; } }

        public PlanetTile Tile { get { return new PlanetTile(tileId, layerId); } }

        /// <summary>Whether the saved destination is still a tile the world actually has.</summary>
        public bool DestinationValid
        {
            get
            {
                if (tileId < 0 || Find.WorldGrid == null) { return false; }
                PlanetTile tile = Tile;
                return tile.Valid;
            }
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref doorLoadId, "rr_doorLoadId");
            Scribe_Values.Look(ref tileId, "rr_tileId", -1);
            Scribe_Values.Look(ref layerId, "rr_layerId", 0);
            Scribe_Values.Look(ref foundTick, "rr_foundTick", -1);
            Scribe_Values.Look(ref usedTick, "rr_usedTick", -1);
        }
    }

    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// How far from the branch's headquarters a way out may come up, in world tiles.
        ///
        /// Far enough that walking home is a journey and a decision, near enough that it is not a
        /// death sentence. Core's own new-site range is 7 to 27, and this sits inside it rather
        /// than inventing a second idea of "somewhere else on the planet".
        /// </summary>
        internal const int WorldExitMinimumTiles = 7;
        /// <summary>
        /// The far end of the band a world exit lands in, measured in planet tiles
        /// from the branch. Paired with the minimum above: near enough to be a place
        /// the company could plausibly reach, far enough that coming out is a
        /// relocation rather than a shortcut home.
        /// </summary>
        internal const int WorldExitMaximumTiles = 20;

        /// <summary>
        /// The band a way out lands in once **RR_Cap_NearExit** (Spatial, tier 5) is held: three to
        /// ten tiles instead of seven to twenty, which is roughly half the walk home.
        ///
        /// **Three rather than nought at the near end, and that floor is the point of the pair.**
        /// A way out that surfaces on the branch's own doorstep is not a way out, it is a second
        /// front door, and it would make the whole Spatial branch's subject — *where does this come
        /// out* — stop being a question. The project moves the band; it does not collapse it.
        /// </summary>
        internal const int NearExitMinimumTiles = 3;
        /// <summary>The far end of the narrowed band. See <see cref="NearExitMinimumTiles"/>.</summary>
        internal const int NearExitMaximumTiles = 10;

        private List<WorldExitRecord> worldExits = new List<WorldExitRecord>();

        internal void ExposeWorldExits()
        {
            Scribe_Collections.Look(ref worldExits, "rr_worldExits", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && worldExits == null)
            { worldExits = new List<WorldExitRecord>(); }
        }

        public IReadOnlyList<WorldExitRecord> WorldExits { get { return worldExits; } }

        /// <summary>The unused way out recorded at this door, or null.</summary>
        public WorldExitRecord WorldExitFor(Thing door)
        {
            if (door == null || !CanOperate) { return null; }
            string loadId = door.GetUniqueLoadID();
            for (int index = 0; index < worldExits.Count; index++)
            {
                WorldExitRecord record = worldExits[index];
                if (record != null && !record.Used && record.doorLoadId == loadId) { return record; }
            }
            return null;
        }

        /// <summary>
        /// Record that this door leads out to a world tile.
        ///
        /// **The tile is chosen by Core's own site-placement logic**, not by ours:
        /// `TileFinder.TryFindNewSiteTile` already refuses water, space and impassable terrain and
        /// already honours every mod that patches tile validity. Writing our own validity test
        /// would be a second opinion that disagrees with the game the first time somebody installs
        /// a biome mod.
        ///
        /// **Seeded, so the same door always leads to the same place.** `TileFinder` rolls against
        /// `Rand`, so the roll is wrapped in a pushed state derived from the coordinate's own seed
        /// and the door's position — the same derivation every other generated property uses. A way
        /// out that moved on reload would be a different world every time somebody loaded a save.
        ///
        /// **A recorded way out never moves afterwards, including when the near-exit project
        /// completes.** The band is read once, here, and the tile is then saved on the record. So
        /// the research applies to doors surveyed after it and leaves every exit a branch has
        /// already written down exactly where it is — which is the only reading that does not
        /// relocate a place crews have walked to.
        /// </summary>
        internal CompanyActionResult RecordWorldExit(Thing door, string coordinateId, int seed)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            if (door == null || !door.Spawned || door.Map == null)
            { return CompanyActionResult.Refused("RR_WorldExit_DoorUnavailable"); }
            if (WorldExitFor(door) != null) { return CompanyActionResult.Existing(); }
            if (headquarters == null || Find.WorldGrid == null)
            { return CompanyActionResult.Refused("RR_WorldExit_NoAnchorTile"); }

            PlanetTile from = headquarters.Tile;
            if (!from.Valid) { return CompanyActionResult.Refused("RR_WorldExit_NoAnchorTile"); }

            PlanetTile destination = default(PlanetTile);
            bool found = false;
            Rand.PushState(CampaignSeed.Derive(seed,
                "worldexit:" + door.Position.x + "," + door.Position.z, 1));
            try
            {
                // **RR_Cap_NearExit** (Spatial, tier 5). The narrowed band is TRIED and the full band
                // still answers if it finds nothing, so the project can only ever bring a way out
                // closer and never cost a branch one it would otherwise have had. A tier that
                // sometimes made exits harder to find would be a tier a player learns to regret, and
                // the band is narrow enough that an ocean or a mountain belt in the wrong place would
                // do exactly that.
                if (HasCapability("RR_Cap_NearExit"))
                {
                    found = TileFinder.TryFindNewSiteTile(out destination, from,
                        NearExitMinimumTiles, NearExitMaximumTiles, allowCaravans: false);
                }
                if (!found)
                {
                    found = TileFinder.TryFindNewSiteTile(out destination, from,
                        WorldExitMinimumTiles, WorldExitMaximumTiles, allowCaravans: false);
                }
            }
            finally { Rand.PopState(); }

            // No valid tile is an honest outcome rather than a reason to invent one. The survey
            // simply found nothing this time, exactly as it does when a marked door is unusable.
            if (!found || !destination.Valid)
            { return CompanyActionResult.Refused("RR_WorldExit_NoTileFound"); }

            var record = new WorldExitRecord
            {
                id = branchId + ":worldexit:" + door.GetUniqueLoadID(),
                coordinateId = coordinateId,
                doorLoadId = door.GetUniqueLoadID(),
                tileId = destination.tileId,
                layerId = destination.Layer == null ? 0 : destination.Layer.LayerID,
                foundTick = Find.TickManager.TicksGame,
            };
            worldExits.Add(record);
            RecordEvent("RR_Event_WorldExitFound", record.id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
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
                ? ClaimTileAndWalkOut(record, leaving, door)
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
        private CompanyActionResult ClaimTileAndWalkOut(WorldExitRecord record, List<Pawn> leaving,
            Thing coordinateDoor)
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

            // **THE WAY BACK IN IS BUILT BEFORE ANYBODY IS DESPAWNED.** Owner, 2026-10-03:
            // *"there is no way for a pawn to go back into the backrooms when they exit via a
            // natural gate"*, and at the fork: *"Generate a map on arrival with the gate in it"*.
            //
            // The ordering is the safety property, and it is the same one this method's docstring
            // already claims for generation: if the return gate cannot be established, **nothing
            // has moved and the way out is still there**. Establishing it afterwards would mean a
            // failure stranded a crew on a map instead of on a tile -- worse, because it looks
            // finished.
            //
            // So this method can now refuse where it previously always succeeded under the cap.
            // That is deliberate: a one-way trip IS the defect, and every refusal names its own
            // cause so a player can clear it (releasing a site frees a slot).
            CompanyActionResult returnGate = EstablishReturnGate(record, claimed, coordinateDoor);
            if (!returnGate.Success) { return returnGate; }

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

        /// <summary>
        /// Build the way back in, on the tile they walked out onto.
        ///
        /// ## Owner report and answer, 2026-10-03, verbatim
        ///
        /// *"ther natureal gates in the backrrooms that lead to the world map tiles( these gats
        /// currently dont have a way back into the backrooms ... they need to have a gate spawn in
        /// the world tile that they portal to so they can head back into the backrooms, currently
        /// and incorrectyl there is no way for a pawn to go back into the backrooms when they exit
        /// via a natural gate"*, and at the fork: *"Generate a map on arrival with the gate in it"*.
        ///
        /// **The map was already being generated.** `ClaimTileAndWalkOut` has claimed the tile and
        /// generated its map since the day it was written, and `CanClaimAnotherMap` already bounds
        /// it by the owner's five-map cap *and* `Prefs.MaxNumberOfPlayerSettlements`. What was
        /// missing was only ever the gate standing in it and the edge pointing home, which is why
        /// this is one method rather than the new world object and map generator the queued row
        /// predicted.
        ///
        /// ## Four preconditions, each read out of `RimroomsPortalNetwork.Register`
        ///
        /// * **Line 82, `OwnsMap(firstAnchor.Map)`.** A Core player settlement is neither the
        ///   headquarters nor a coordinate, so `OwnsMap` is false until the map is registered as a
        ///   remote site. `OperatesAt`'s own comment already names this as that predicate's
        ///   purpose — *"a gate may anchor there and a way out may come up on it"* — so this uses
        ///   an audited path rather than widening one. `CompRimroomsEmergence.OrdinaryBranchMap`
        ///   asks the same question, which is why the registration happens before the mark.
        /// * **Lines 90-95, the `Emergence` kind.** The anchor must carry
        ///   <see cref="CompRimroomsEmergence"/>, be designated, be player-faction and have a
        ///   matching approach cell. `Mark()` is what makes it designated, and it is the same
        ///   method the player's own gizmo calls.
        /// * **Lines 278-283, `ValidDoor`.** A `Building_Door`, spawned, with the approach cell
        ///   cardinally adjacent and in bounds. A Core `Door` in steel, made exactly the way
        ///   `GenStep_BackroomsDestination.PlaceNativeDoors` makes every other threshold in this
        ///   mod — **no new ThingDef**, so the content-reuse policy is untouched.
        /// * **Lines 79-81.** The *second* anchor must be the coordinate map, and it is: the door
        ///   the crew walked out of is the natural gate they were standing at.
        ///
        /// ## It cleans up after itself, and that is not optional
        ///
        /// Every failure after the door is spawned destroys it again. A door left standing with no
        /// edge behind it is worse than no door: it is a gate that looks like the way home and is
        /// not, which is the same lie as a section titled DONE full of open rows.
        /// </summary>
        private CompanyActionResult EstablishReturnGate(WorldExitRecord record, Map claimed,
            Thing coordinateDoor)
        {
            if (claimed == null || coordinateDoor == null || !coordinateDoor.Spawned)
            { return CompanyActionResult.Refused("RR_WorldReturn_Unavailable"); }

            CompanyActionResult site = RegisterRemoteSite(claimed);
            if (!site.Success) { return site; }

            ThingDef doorDef = DefDatabase<ThingDef>.GetNamedSilentFail("Door");
            if (doorDef == null) { return CompanyActionResult.Refused("RR_WorldReturn_NoDoorDef"); }

            IntVec3 cell = FindReturnGateCell(claimed);
            if (!cell.IsValid) { return CompanyActionResult.Refused("RR_WorldReturn_NoGateCell"); }

            var gate = ThingMaker.MakeThing(doorDef,
                doorDef.MadeFromStuff ? ThingDefOf.Steel : null) as Building_Door;
            if (gate == null) { return CompanyActionResult.Refused("RR_WorldReturn_NoDoorDef"); }
            gate.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(gate, cell, claimed, Rot4.North);
            if (!gate.Spawned || gate.Map != claimed)
            { return CompanyActionResult.Refused("RR_WorldReturn_GateNotPlaced"); }
            gate.SetForbidden(false, false);

            CompRimroomsEmergence anchor = gate.TryGetComp<CompRimroomsEmergence>();
            if (anchor == null)
            {
                gate.Destroy(DestroyMode.Vanish);
                return CompanyActionResult.Refused("RR_WorldReturn_NoAnchorComp");
            }
            CompanyActionResult marked = anchor.Mark();
            if (!marked.Success) { gate.Destroy(DestroyMode.Vanish); return marked; }

            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null)
            {
                gate.Destroy(DestroyMode.Vanish);
                return CompanyActionResult.Refused("RR_WorldReturn_NoNetwork");
            }

            IntVec3 approach = anchor.ApproachCell;
            IntVec3 farApproach = PortalAddressService.ApproachCellFor(coordinateDoor);
            PortalNetworkResult registered = network.Register(record.id + ":return",
                record.coordinateId, PortalConnectionKind.Emergence,
                gate, approach, coordinateDoor, farApproach);
            if (registered != PortalNetworkResult.Success && registered != PortalNetworkResult.Existing)
            {
                gate.Destroy(DestroyMode.Vanish);
                return CompanyActionResult.Refused("RR_WorldReturn_NotRegistered");
            }

            RecordEvent("RR_Event_WorldReturnGateBuilt", record.id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// A cell on the claimed map a door can stand in, with somewhere to stand beside it.
        ///
        /// The cardinal-neighbour test is not decoration: `ValidDoor` requires the approach cell
        /// to be cardinally adjacent, and `PortalAddressService.ApproachCellFor` finds it by
        /// walking the four cardinals. A cell whose neighbours are all rock or water would spawn a
        /// door that can never be registered, so the search refuses it here rather than
        /// discovering it two steps later with a door already on the map.
        /// </summary>
        private static IntVec3 FindReturnGateCell(Map map)
        {
            IntVec3 found;
            if (CellFinderLoose.TryFindRandomNotEdgeCellWith(12,
                cell => cell.Standable(map) && !cell.Fogged(map) && cell.GetEdifice(map) == null &&
                    HasStandableCardinal(cell, map), map, out found))
            { return found; }
            return IntVec3.Invalid;
        }

        private static bool HasStandableCardinal(IntVec3 cell, Map map)
        {
            foreach (IntVec3 direction in GenAdj.CardinalDirections)
            {
                IntVec3 candidate = cell + direction;
                if (candidate.InBounds(map) && candidate.Standable(map)) { return true; }
            }
            return false;
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

        /// <summary>
        /// Who walks out: player pawns standing on the door's own approach cell or beside it.
        ///
        /// **Deliberately only the player's own, and never a prisoner or a slave.** Invariant 17:
        /// a prisoner can never cross a gate, and walking out into the world is a crossing by any
        /// honest reading. A downed pawn is left too — somebody unconscious on the floor is not
        /// walking anywhere, and taking them would be the mod moving a crew rather than the player.
        /// </summary>
        private List<Pawn> TravellersAt(Thing door)
        {
            var leaving = new List<Pawn>();
            Map map = door.Map;
            IntVec3 approach = PortalAddressService.ApproachCellFor(door);
            if (!approach.IsValid || !approach.InBounds(map)) { return leaving; }

            foreach (IntVec3 cell in GenAdj.CellsAdjacent8Way(door))
            {
                if (!cell.InBounds(map)) { continue; }
                foreach (Thing thing in map.thingGrid.ThingsListAtFast(cell))
                {
                    Pawn pawn = thing as Pawn;
                    if (pawn == null || pawn.Dead || pawn.Destroyed || !pawn.Spawned) { continue; }
                    if (pawn.Faction != Faction.OfPlayer) { continue; }
                    if (pawn.IsPrisoner || pawn.IsSlave || pawn.Downed) { continue; }
                    if (!leaving.Contains(pawn)) { leaving.Add(pawn); }
                }
            }
            return leaving;
        }
    }
}
