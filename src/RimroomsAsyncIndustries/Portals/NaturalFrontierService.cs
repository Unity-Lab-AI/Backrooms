using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Generation;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// How a further natural gate is actually found in play.
    ///
    /// Everything this needs already existed: the deterministic discovered-coordinate
    /// API, natural-edge registration, and the coordinate/seed owner that recalls a
    /// saved space instead of rebuilding it. What was missing was the trigger — the
    /// moment in the game where one of this company's people looks at a doorway deeper
    /// in and records that it leads somewhere new. Without it the permanently-open
    /// natural half of the design was unreachable except by the player wiring an
    /// address by hand, and a deterministic coordinate API sat with no caller at all.
    ///
    /// Bounded, and deliberately so. A frontier is a property of the doorway's own
    /// position under the place's own stable seed, so the same doorway is always the same
    /// answer: reopening a known space never rerolls what it leads to. At most
    /// <see cref="MaximumFrontiersPerCoordinate"/> gates are ever found on one coordinate,
    /// and the campaign's own coordinate cap bounds the whole graph. This propagates further
    /// spaces without preallocating infinity, which is exactly what the contract asks for.
    ///
    /// **Two kinds of origin, per the owner's topology direction of 2026-09-29.** A doorway
    /// leading onward may be found inside the Backrooms, as before, *or* on an ordinary map —
    /// a colony or a generated world site — because portals are findable on world maps too and
    /// the link kind that brought you somewhere never restricts where you can go next. The
    /// ordinary-map case is deliberately rarer, capped at one per map, and **never applies to a
    /// door the player built**: turning somebody's own wall door into a permanent way into the
    /// Backrooms would change an existing colony just by installing this mod, which the content
    /// policy forbids. A way onward is found in something that was already standing there.
    ///
    /// Save compatibility is exact: a Backrooms origin still produces byte-for-byte the same
    /// discovered-coordinate id and the same seed key it produced before ordinary maps were
    /// allowed, so every coordinate already discovered in an existing save resolves to the same
    /// space. The ordinary-map case uses a distinct key so the two can never collide.
    ///
    /// This finds a *way through*. It does not generate inhabitants, encounters or
    /// pressure; what waits on the other side is the escalation ladder's business.
    /// </summary>
    public static class NaturalFrontierService
    {
        public const string SurveyJobDefName = "RR_SurveyFrontier";

        /// <summary>
        /// Fewest ways onward a coordinate offers, whatever its size.
        ///
        /// **Owner direction, 2026-09-30:** four to six per level, *"1 per ~15 rooms"*. Two was
        /// right when a coordinate was six rooms on a 60x60 map; a 300x300 level with dozens of
        /// rooms and two doors onward is a maze with the exits hidden rather than a place with
        /// ways through it.
        ///
        /// **What made raising this safe is the map budget**, not a change of mind about
        /// finiteness. The old summary said raising it was a design decision because the cap was
        /// the only thing keeping the chain finite. It no longer is: `OpenMapBudget` bounds how
        /// many places can be open at once regardless of how many doors exist, so the number of
        /// doors and the cost of the graph are now separate questions.
        /// </summary>
        internal const int MinimumFrontiersPerCoordinate = 4;

        /// <summary>Most ways onward a coordinate will ever offer.</summary>
        internal const int MaximumFrontiersPerCoordinate = 6;

        /// <summary>Rooms per extra way onward, above the minimum.</summary>
        internal const int RoomsPerExtraFrontier = 20;

        /// <summary>
        /// How many ways onward THIS coordinate offers: the minimum, plus one for every
        /// <see cref="RoomsPerExtraFrontier"/> rooms it has, never more than
        /// <see cref="MaximumFrontiersPerCoordinate"/>.
        ///
        /// Read from the coordinate's own room count rather than from its depth, so it stays
        /// correct if the planner's depth profile changes again.
        /// </summary>
        internal static int FrontiersFor(CoordinateRecord coordinate)
        {
            int rooms = coordinate == null || coordinate.Rooms == null ? 0 : coordinate.Rooms.Count;
            int allowed = MinimumFrontiersPerCoordinate + rooms / RoomsPerExtraFrontier;
            return allowed > MaximumFrontiersPerCoordinate ? MaximumFrontiersPerCoordinate : allowed;
        }

        /// <summary>
        /// The deepest coordinate a found door will ever lead to. **Six.**
        ///
        /// ## The number, and the one it replaced
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"with natural portals deeper to an extent
        /// till they would need to buidl theri own gate"*. The depth chosen at that fork was
        /// **three**, and it was **raised from 3 to 6 at 0.12.49-dev** by owner direction
        /// 2026-09-30, alongside the map budget that makes a deeper chain affordable. The original
        /// three bands were chosen when a level was 60x60 and two doors wide; at 300x300 they are
        /// a different proposition.
        ///
        /// **The superseded three is recorded here and nowhere else, deliberately.** This comment
        /// used to carry *two* `summary` blocks -- the first still arguing for three in full, the
        /// second noting the raise -- and the published wiki copied the first one and told every
        /// reader the free ways through stop at depth 3. **A stale doc comment is not a tidiness
        /// problem; it is the upstream of a published lie**, because a comment is what somebody
        /// reads when they write the page. One block, current value first.
        ///
        /// So the Backrooms hands a branch six bands for free and then stops handing out ways
        /// onward. Going further is a machine's job, which is the convergence this start needs:
        /// the place gives you enough to learn on and then asks you to become an engineer.
        ///
        /// **Six is the FREE reach. A branch can earn a seventh** — see
        /// <see cref="DeepFrontierNaturalDepth"/>, and read the reach through
        /// <see cref="NaturalDepthReach"/> rather than from this constant.
        ///
        /// **This caps going DEEPER, never coming OUT.** The way-out draw runs first and is not
        /// subject to this, because a crew standing at the deepest band must always be able to
        /// find a door that leads home. Capping both would have turned it into a trap, and
        /// invariant 28 forbids an unavoidable failure.
        ///
        /// **It does not restrain the player, only the free ways in.** Owner, verbatim: *"this
        /// is all open eneded they can play how they choose"*. A built gate reaches any depth it
        /// has earned, exactly as before.
        /// </summary>
        internal const int MaximumNaturalDepth = 6;

        /// <summary>
        /// The deepest a found door leads for a branch that has earned it. **Seven.**
        ///
        /// **Spatial tier 6: `RR_Cap_DeepFrontier`**, the top of the whole tree, and the only
        /// project in it that moves a number this file calls a cap.
        ///
        /// ## This retires a restraint rather than slipping past one
        ///
        /// `proof-research-tier4.py` asserted *"THE NATURAL DEPTH REACH IS NOT RESEARCH-DRIVEN,
        /// WHATEVER ITS VALUE"*, and that claim was correct for every tier up to four. **The owner
        /// approved a Spatial tier 6 whose subject is exactly this number**, so the restraint is
        /// restated rather than deleted and rather than quietly circumvented: what it always
        /// protected is that **the reach is BOUNDED and that one place decides it**, and both are
        /// still true and still asserted. A capability raises the bound by one; nothing makes it
        /// unbounded, and nothing else in the mod gets to have an opinion about it.
        ///
        /// ## Why one, and why seven is a real place rather than a bigger number
        ///
        /// A seventh level had no look of its own until 0.12.99-dev: `BackroomsPalette.Bands` was
        /// five, and the band derivation wrapped, so depth seven would have come up Poolrooms — the
        /// second shallowest face in the game on the deepest space in it. **The sweep called that a
        /// content question before a research question and it was right.** The sixth band
        /// (`RR_Palette_Undercroft`) and the saturating band derivation are what make the seventh
        /// level somewhere, and this constant is only honest because they exist.
        /// </summary>
        internal const int DeepFrontierNaturalDepth = 7;

        /// <summary>
        /// How deep found doors lead for this branch, as it currently stands.
        ///
        /// **THE ONE PLACE THAT DECIDES IT, and that is the whole point of the method existing.**
        /// Three places read the reach: the refusal in <see cref="Discover"/>, the blind dial's
        /// deepest rung, and the hint that tells a branch it has gone as deep as found doors go.
        /// The dial carried **its own constant six** with a comment saying it matched this one —
        /// two derivations of one rule, which is the defect this project keeps meeting, and it would
        /// have shipped a branch that could walk to depth seven while a blind dial still refused to
        /// send anybody there and a hint still claimed six was the end.
        ///
        /// A null campaign answers with the unearned reach: not knowing what a branch has learned is
        /// not the same as knowing it has learned this.
        /// </summary>
        internal static int NaturalDepthReach()
        {
            RimroomsCampaignComponent campaign = Campaign();
            return campaign != null && campaign.HasCapability("RR_Cap_DeepFrontier")
                ? DeepFrontierNaturalDepth
                : MaximumNaturalDepth;
        }

        /// <summary>
        /// Roughly one doorway in this many is a frontier. Combined with the cap above,
        /// a space with many doors still yields at most two ways onward.
        /// </summary>
        internal const int FrontierRarity = 12;

        /// <summary>
        /// Rarity once a branch reads a space well enough to spot a way onward sooner.
        ///
        /// **Spatial tier 3: `RR_Cap_CoordinateReading`.** One doorway in eight rather than one in
        /// twelve.
        ///
        /// **This changes WHEN, never HOW MANY.** The number a coordinate offers is
        /// <see cref="FrontiersFor"/>, and this capability only makes them easier to spot.
        /// </summary>
        internal const int PractisedFrontierRarity = 8;

        /// <summary>
        /// How many ways onward may ever be found on an **ordinary** map — a colony, or a
        /// generated world site. One, deliberately. The Backrooms is where doorways lead
        /// somewhere else; the world is where that is a rare and notable event, and a base
        /// riddled with anomalous doors would be both wrong and intrusive.
        /// </summary>
        internal const int MaximumFrontiersPerOrdinaryMap = 1;

        /// <summary>
        /// Rarity on an ordinary map, much lower than inside the Backrooms for the same
        /// reason as the cap above.
        /// </summary>
        internal const int WorldFrontierRarity = 40;

        /// <summary>
        /// Ordinary-map rarity for a branch that has learned to read a surface.
        ///
        /// **RR_Cap_SurfaceReading** (Spatial, tier 4). This is the ORDINARY-MAP number and not
        /// the per-coordinate one: the restraint that the per-coordinate frontier cap is not a
        /// research knob still holds, and `MaximumFrontiersPerOrdinaryMap` is untouched too. What
        /// changes is how often a door on your own map turns out to lead somewhere, which is a
        /// different question about a different place.
        /// </summary>
        internal const int ReadSurfaceFrontierRarity = 28;

        /// <summary>
        /// Where a frontier draw is anchored. A generated coordinate has its own saved seed
        /// and its own id; an ordinary map has neither, so it uses the branch seed and an id
        /// derived from the map. Both are stable for the life of the save, which is the only
        /// property the draw actually needs.
        /// </summary>
        private sealed class FrontierOrigin
        {
            internal string OriginId;
            internal int Seed;
            internal int Rarity;
            internal int Cap;
            internal string KeyPrefix;
        }

        /// <summary>
        /// Whether this door is a dead end: walkable on exactly one side, with rock behind it.
        ///
        /// ## The owner's rule
        ///
        /// *"gates natural need to not also be used and needed as normal doors, becasue on the
        /// other side was the rest of the backrooms map"*.
        ///
        /// A door between two rooms is a door the player walks through to get around the level.
        /// Making it a permanently open one-way gate to another map takes that route away and
        /// turns ordinary movement into a trap. **And a way onward is something you find; you
        /// cannot find a door you were already using.**
        ///
        /// ## Why a dead-end door is exactly the right answer
        ///
        /// These already exist, and the owner asked for them one checkpoint ago:
        /// `RoomLayoutPlanner.FalseOpening` puts *"doors to now where"* a third of the way along
        /// a blank wall, and `PlaceNativeDoors` builds a real Core door in each. **So the door
        /// that should not be there is the door that leads somewhere else** -- which is the
        /// setting, written in geometry, at no content cost.
        ///
        /// Measured from the MAP, not from the room graph, because that is what the player sees.
        /// A door with one walkable side has nothing behind it whatever the planner intended, and
        /// a door the player has since walled off stops being a candidate on its own.
        /// </summary>
        internal static bool LeadsNowhere(Thing door)
        {
            if (door == null || !door.Spawned || door.Map == null) { return false; }
            Map map = door.Map;
            int open = 0;
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            for (int index = 0; index < directions.Length; index++)
            {
                IntVec3 side = door.Position + directions[index];
                if (!side.InBounds(map)) { continue; }
                // Another door counts as a way through: two doors in a row is still a route.
                if (side.Walkable(map) || side.GetEdifice(map) is Building_Door) { open++; }
            }
            // Exactly one walkable side. A door in open floor has four, an ordinary door between
            // two spaces has two, and a dead end has one.
            return open == 1;
        }

        /// <summary>
        /// Whether this doorway is one that leads onward and has not been recorded yet.
        /// Pure and side-effect free: it generates nothing and records nothing, so it
        /// is safe to ask about every door on a map during work scanning.
        /// </summary>
        public static bool IsFrontierCandidate(Thing door)
        {
            CoordinateRecord source;
            FrontierOrigin origin;
            return Evaluate(door, out source, out origin) == null;
        }

        /// <summary>
        /// Record this doorway as a permanently open natural gate to a further space.
        /// Idempotent: the coordinate id and seed are derived, and both the campaign
        /// record and the graph edge answer "already exists" on a replay rather than
        /// creating a second one.
        /// </summary>
        public static CompanyActionResult Discover(Thing door)
        {
            CoordinateRecord source;
            FrontierOrigin origin;
            string refusal = Evaluate(door, out source, out origin);
            if (refusal != null || origin == null) { return CompanyActionResult.Refused(refusal ?? "RR_Frontier_Unavailable"); }
            RimroomsCampaignComponent campaign = Campaign();

            // Derived from where it was found and the doorway's own position, so a replay of
            // the same discovery resolves to the same space with the same seed rather than
            // inventing another one. For a Backrooms origin this is byte-for-byte the id the
            // service produced before ordinary maps were allowed, so every coordinate already
            // discovered in an existing save still resolves to exactly the same space.
            string discoveryId = DiscoveryIdFor(origin, door);
            // A doorway inside the Backrooms may lead *out* instead of deeper. That is the
            // other half of the owner's topology direction, and it is what makes
            // `backrooms > map > backrooms` chains route end to end.
            //
            // Asked before the coordinate is minted, because minting one and then not using
            // it would leave a space nobody can reach recorded against the branch.
            if (source != null)
            {
                CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);
                if (wayOut != null) { return wayOut; }
            }

            CoordinateRecord discovered;
            // Depth is one more than wherever this doorway was found. A frontier on an
            // ordinary world map mints depth 1 -- the shallow, yellow-carpet Backrooms --
            // and every step inward adds one, which is what lets the place stop looking
            // like itself the further a branch pushes.
            int depth = source == null ? 1 : source.Depth + 1;
            // The natural chain stops here. Checked AFTER the way-out attempt above, so a crew
            // at the deepest natural band can still find a door home -- capping both directions
            // would make that band a trap.
            //
            // Refused rather than silently minting a shallower space: a doorway that led
            // somewhere other than where it should would be a quieter and worse lie than being
            // told plainly that nothing natural goes further than this.
            if (depth > NaturalDepthReach())
            { return CompanyActionResult.Refused("RR_Frontier_BeyondNaturalReach"); }
            // **This gate is blocked; you are holding open too many gates.**
            //
            // Owner direction, 2026-09-30, verbatim: *"dont let them go more than 5 remember the
            // games mechanics and limits built in if they find a gate to a world map tile or a
            // deeper backrroms and they have 5 mpas they should gett a warning this gate is
            // blocked your holding open too many gates, but per scerio styled"*, and *"5 is the
            // limit of other colonies available so a backrooms level should be one colonly
            // bacskicly in my thinking"*. See Portals/OpenMapBudget.
            //
            // **Asked here, after the way-out attempt above, and that is deliberate.** A doorway
            // may lead OUT instead of deeper, and a way home costs no map: it records a world
            // tile, it does not mint a place. Blocking it at the cap would strand a crew that is
            // deep and full up with nothing but the route they walked in by -- the same trap the
            // depth cap above is ordered to avoid. So the budget stops the mod opening ANOTHER
            // PLACE; it never closes the last door home.
            //
            // Refused before `CreateDiscoveredCoordinate`, so a blocked gate leaves no
            // half-minted coordinate recorded against the branch.
            if (!OpenMapBudget.CanOpenAnother)
            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }
            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered);
            if (!created.Success || discovered == null) { return created; }

            CompanyActionResult registered = PortalAddressService.RegisterNaturalAddress(
                door, PortalAddressService.ApproachCellFor(door), discovered);
            if (registered.Success && !registered.AlreadyApplied)
            {
                // Origin id, not the coordinate's: an ordinary map has no CoordinateRecord at
                // all, so reading source.Id here would have thrown for exactly the case this
                // change exists to support.
                campaign.RecordEvent("RR_Event_FrontierDiscovered", discovered.Id, origin.OriginId);
            }
            return registered;
        }

        /// <summary>
        /// The id of the space this doorway leads to, **bounded so that going deeper stays
        /// possible.**
        ///
        /// ## What was wrong
        ///
        /// This was `origin.OriginId + ":" + KeyPrefix + x + "," + z`, and a coordinate's id
        /// embeds its parent's entire id. So the id grew by about eighty characters per level:
        /// 88 for the first step inward, **168 for the second** -- past
        /// <see cref="RimroomsCampaignComponent.MaximumDiscoveryIdLength"/>, refused with
        /// `RR_Company_InvalidRequest`. **The Backrooms could never be more than two levels
        /// deep**, and `MaximumNaturalDepth` was unreachable.
        ///
        /// ## Why the long form is kept whenever it fits
        ///
        /// Byte-for-byte what it always was, so **every coordinate already discovered in a save
        /// resolves to exactly the same space.** Only an id that would be refused is shortened,
        /// and an id that would be refused never existed in a save to begin with.
        ///
        /// ## Why two hashes
        ///
        /// `StableHash` is a 31-bit FNV value. One of them shared by two parents would merge two
        /// different places into one coordinate -- a far worse outcome than a refusal. Two
        /// independent derivations of the same saved id make that vanishingly unlikely, and both
        /// are derived from the id alone, so a reload resolves identically.
        /// </summary>
        private static string DiscoveryIdFor(FrontierOrigin origin, Thing door)
        {
            string position = origin.KeyPrefix + door.Position.x + "," + door.Position.z;
            string full = origin.OriginId + ":" + position;
            if (full.Length <= RimroomsCampaignComponent.MaximumDiscoveryIdLength) { return full; }
            int first = DestinationService.StableHash(0, origin.OriginId, 1);
            int second = DestinationService.StableHash(origin.OriginId.Length, origin.OriginId, 7);
            return "o" + first.ToString("x8") + second.ToString("x8") + ":" + position;
        }

        /// <summary>
        /// Whether this doorway leads out of the Backrooms rather than deeper into it, and if
        /// so, recording it against the way home the player marked.
        ///
        /// Returns **null** when this is not a way out, so the caller falls through to minting
        /// a new coordinate exactly as it always did.
        ///
        /// ## Three things decide it, in this order
        ///
        /// 1. **A second, independent draw.** It uses a distinct key from the frontier draw, so
        ///    which doorways lead onward and which of those lead out can never correlate. Like
        ///    every other generated property it is derived from the coordinate's own saved seed
        ///    and the doorway's position, so the answer is stable across saves and revisits.
        /// 2. **A way home must already be marked.** With no marked door there is nowhere for a
        ///    way out to come up, so the doorway leads deeper instead. That is a fallback rather
        ///    than a refusal: the survey still finds something.
        /// 3. **The player marked it.** Nothing here ever picks a door on the player's own map,
        ///    which is the rule 0.6.3-dev established and this inherits.
        ///
        /// When several ways home are marked, the one used is chosen by an ordinal sort of
        /// their load ids indexed by the same draw — deterministic, so the same doorway does
        /// not come up somewhere different on a reload.
        /// </summary>
        private static CompanyActionResult TryRecordWayOut(Thing door, FrontierOrigin origin,
            RimroomsCampaignComponent campaign)
        {
            if (door == null || origin == null || campaign == null) { return null; }

            // **THE KIND IS DECIDED FOR THE GUARANTEED PAIR, NOT DRAWN.** A way onward leads out
            // one time in three otherwise, and left to that draw both guaranteed doorways could
            // come up the same way -- which would satisfy "two portals" while delivering one
            // kind, and the owner asked for *"a protal to the world map AND a deeper in portal"*.
            CoordinateRecord guaranteeSource = campaign.Coordinates == null ? null
                : campaign.Coordinates.FirstOrDefault(candidate => candidate != null
                    && candidate.Id == origin.OriginId);
            bool leadsOut;
            if (guaranteeSource != null
                && GuaranteedFrontiers.IsGuaranteed(door, guaranteeSource, out leadsOut))
            {
                // The deeper one is never diverted out; returning null sends the caller on to
                // mint a coordinate, which is exactly what it does for an ordinary deeper find.
                if (!leadsOut) { return null; }
                return campaign.RecordWorldExit(door, origin.OriginId, origin.Seed);
            }

            int draw = CampaignSeed.Derive(origin.Seed,
                "wayout:" + door.Position.x + "," + door.Position.z, 1);
            int share = campaign.HasCapability("RR_Cap_WayHomeDiscipline")
                ? PractisedEmergenceShare : EmergenceShare;
            if (draw % share != 0) { return null; }

            List<CompRimroomsEmergence> anchors = CompRimroomsEmergence.Anchors();
            if (anchors.Count == 0)
            {
                // No marked door anywhere. This used to return null, so the way out became a way
                // DEEPER -- which meant a branch with nothing marked could never find a way out at
                // all, and that is a dead end for exactly the player least equipped for one.
                //
                // Instead the way out leads to a world tile the branch does not hold, and the crew
                // walks out as a caravan. Owner decision 2026-09-29.
                return campaign.RecordWorldExit(door, origin.OriginId, origin.Seed);
            }
            anchors.Sort((left, right) => string.CompareOrdinal(
                left.parent.GetUniqueLoadID(), right.parent.GetUniqueLoadID()));
            CompRimroomsEmergence anchor = anchors[draw % anchors.Count];

            CompanyActionResult registered = PortalAddressService.RegisterEmergenceAddress(
                door, PortalAddressService.ApproachCellFor(door), anchor);
            // A refusal here is not a reason to mint a coordinate instead. The draw said this
            // doorway leads out; if the marked door is momentarily unusable the honest answer
            // is that the survey found nothing this time, and it can be tried again.
            if (registered.Success && !registered.AlreadyApplied)
            { campaign.RecordEvent("RR_Event_WayOutDiscovered", origin.OriginId); }
            return registered;
        }

        /// <summary>The label of the space a recorded frontier leads to, for player text.</summary>
        public static string DiscoveredLabelFor(CoordinateRecord discovered)
        {
            if (discovered == null) { return string.Empty; }
            return string.IsNullOrEmpty(discovered.Label) ? discovered.Id : discovered.Label;
        }

        /// <summary>
        /// One evaluation used by both the predicate and the action, so the thing a
        /// worker was sent to survey cannot differ from the thing that gets recorded.
        /// Returns a keyed refusal, or null when the doorway is a live candidate.
        /// </summary>
        private static string Evaluate(Thing door, out CoordinateRecord sourceCoordinate,
            out FrontierOrigin frontierOrigin)
        {
            sourceCoordinate = null;
            frontierOrigin = null;
            RimroomsCampaignComponent campaign = Campaign();
            RimroomsPortalNetwork network = Network();
            if (campaign == null || !campaign.CanOperate || network == null || network.HasStateFault)
            { return "RR_Frontier_Unavailable"; }
            if (!(door is Building_Door) || !door.Spawned || door.Destroyed || door.Map == null ||
                !campaign.OwnsMap(door.Map))
            { return "RR_Frontier_NotADoor"; }

            // Two kinds of place a doorway can lead onward from, per the owner's topology
            // direction of 2026-09-29: the link kind that brought you somewhere never
            // restricts where you can go next, and portals are findable on world maps too.
            RimroomsDestinationMapParent site = door.Map.Parent as RimroomsDestinationMapParent;
            FrontierOrigin origin;
            if (site != null && site.LayoutReady)
            {
                CoordinateRecord record = campaign.Coordinates.FirstOrDefault(candidate => candidate != null &&
                    candidate.Site == site && candidate.Id == site.CoordinateId);
                if (record == null) { return "RR_Frontier_NotInTheBackrooms"; }
                // The way home is never a frontier.
                if (door == site.ReturnAnchor) { return "RR_Frontier_IsTheWayBack"; }
                // Unchanged from the original id and key so every coordinate already
                // discovered in an existing save resolves to exactly the same space.
                origin = new FrontierOrigin
                {
                    OriginId = record.Id,
                    Seed = record.Seed,
                    Rarity = campaign.HasCapability("RR_Cap_CoordinateReading")
                        ? PractisedFrontierRarity : FrontierRarity,
                    Cap = FrontiersFor(record),
                    KeyPrefix = "frontier:"
                };
                sourceCoordinate = record;
            }
            else
            {
                // An ordinary map: a colony, or a generated world site. Rarer, capped at one,
                // and with one hard restriction that protects the player's own base.
                //
                // **A door the player built is never a frontier.** Turning somebody's own
                // wall door into a permanent way into the Backrooms would change an existing
                // colony just by installing this mod, which the content policy forbids, and
                // it would be the kind of surprise nobody asked for. A way onward is found in
                // something that was already standing there.
                if (door.Faction == Faction.OfPlayer) { return "RR_Frontier_PlayerBuilt"; }
                // A designated laboratory gate has a machine for this and is not a frontier.
                if (door.TryGetComp<CompRimroomsGate>() != null) { return "RR_Frontier_IsAMachineGate"; }
                origin = new FrontierOrigin
                {
                    OriginId = "map:" + door.Map.uniqueID,
                    Seed = campaign.BranchSeed,
                    Rarity = campaign.HasCapability("RR_Cap_SurfaceReading")
                        ? ReadSurfaceFrontierRarity : WorldFrontierRarity,
                    Cap = MaximumFrontiersPerOrdinaryMap,
                    // A distinct key, so an ordinary-map draw can never collide with a
                    // Backrooms one even if a seed and a position happened to coincide.
                    KeyPrefix = "worldfrontier:"
                };
            }
            frontierOrigin = origin;

            IntVec3 approach = PortalAddressService.ApproachCellFor(door);
            if (!PortalAddressService.UsableThreshold(door, approach, door.Map))
            { return "RR_Frontier_Obstructed"; }

            // **A GATE IS NEVER A DOOR SOMEBODY NEEDS.** Owner: *"gates natural need to not also
            // be used and needed as normal doors, becasue on the other side was the rest of the
            // backrooms map"*. Checked here so the glow, the float menu and the discovery all
            // agree -- `IsFrontierCandidate` and `Discover` both come through this method.
            if (!LeadsNowhere(door)) { return "RR_Frontier_LeadsNowhere"; }

            IReadOnlyList<PortalConnectionRecord> edges = network.Connections;
            int foundHere = 0;
            for (int index = 0; index < edges.Count; index++)
            {
                PortalConnectionRecord edge = edges[index];
                if (edge == null || edge.First == null || edge.Second == null) { continue; }
                if (edge.First.Anchor == door || edge.Second.Anchor == door)
                { return "RR_Frontier_AlreadyRecorded"; }
                if (edge.Kind == PortalConnectionKind.Natural && edge.First.Map == door.Map) { foundHere++; }
            }
            // **THE GUARANTEE.** Owner: *"every backrooms instance need a protal to the world
            // map and a deeper in portal"*. Two doorways per coordinate are chosen once and skip
            // both the cap and the draw below -- everything above still applies to them, because
            // a guarantee that skipped the safety checks would be a bug with a promise attached.
            bool guaranteedLeadsOut;
            bool guaranteed = sourceCoordinate != null
                && GuaranteedFrontiers.IsGuaranteed(door, sourceCoordinate, out guaranteedLeadsOut);

            // Exempt from the cap, and only they. A level that has already found its four-to-six
            // ways onward would otherwise refuse the pair, which makes a guarantee conditional.
            if (!guaranteed && foundHere >= origin.Cap) { return "RR_Frontier_NoneLeftHere"; }

            // The draw is over the doorway's position under this place's own stable seed.
            // Position is stable for the life of the map, so the answer never changes on a
            // reload or a revisit.
            //
            // **One doorway in twelve, and a whole level can roll none.** That is what the owner
            // walked: a Backrooms with no way deeper and no way out, and nothing to tell them the
            // dice simply had not come up.
            if (guaranteed) { return null; }
            int draw = CampaignSeed.Derive(origin.Seed,
                origin.KeyPrefix + door.Position.x + "," + door.Position.z, 1);
            if (draw % origin.Rarity != 0) { return "RR_Frontier_LeadsNowhere"; }
            return null;
        }

        /// <summary>
        /// One in this many ways onward inside the Backrooms leads out instead of deeper,
        /// when the player has marked somewhere for it to come up. Deliberately common: a way
        /// home is the thing that makes the rest of the topology usable rather than a trap.
        /// </summary>
        private const int EmergenceShare = 3;

        /// <summary>
        /// The share once a branch has drilled getting people home.
        ///
        /// **Fieldcraft tier 3: `RR_Cap_WayHomeDiscipline`.** One draw in two rather than one in
        /// three produces a way out to the world instead of a way deeper. This belongs to
        /// Fieldcraft rather than Spatial because it is not about reading a space, it is about
        /// **coming back out of one** -- the same subject as the return drill and the relief watch.
        /// </summary>
        private const int PractisedEmergenceShare = 2;

        private static RimroomsCampaignComponent Campaign()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); }
        private static RimroomsPortalNetwork Network()
        { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsPortalNetwork>(); }
    }

    /// <summary>
    /// Offers the survey as ordinary work, so a doorway that leads onward is found by
    /// someone actually walking up to it and looking, in their own work order.
    /// </summary>
    public sealed class WorkGiver_SurveyFrontier : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest
        { get { return ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial); } }

        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }

        public override Danger MaxPathDanger(Pawn pawn) { return Danger.Some; }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            // Free on headquarters and on any map that has already given up all the
            // ways onward it has, which is the overwhelmingly common case.
            if (pawn == null || !pawn.Spawned || pawn.Map == null) { return true; }
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate || !campaign.OwnsMap(pawn.Map)) { return true; }
            RimroomsPortalNetwork network = Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.HasStateFault) { return true; }
            // Both kinds of place can hold a way onward now, with different caps: a generated
            // coordinate may give up two, an ordinary map at most one.
            RimroomsDestinationMapParent site = pawn.Map.Parent as RimroomsDestinationMapParent;
            bool inBackrooms = site != null && site.LayoutReady;
            int cap = inBackrooms
                ? NaturalFrontierService.MaximumFrontiersPerCoordinate
                : NaturalFrontierService.MaximumFrontiersPerOrdinaryMap;
            int foundHere = network.Connections.Count(edge => edge != null && edge.First != null &&
                edge.Kind == PortalConnectionKind.Natural && edge.First.Map == pawn.Map);
            return foundHere >= cap;
        }

        private Job SurveyJob(Pawn pawn, Thing thing, bool forced)
        {
            if (!NaturalFrontierService.IsFrontierCandidate(thing)) { return null; }
            if (!pawn.CanReserveAndReach(thing, PathEndMode.Touch, pawn.NormalMaxDanger(), 1, -1, null, forced))
            { return null; }
            JobDef definition = DefDatabase<JobDef>.GetNamedSilentFail(NaturalFrontierService.SurveyJobDefName);
            return definition == null ? null : JobMaker.MakeJob(definition, thing);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return SurveyJob(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        { return SurveyJob(pawn, t, forced); }
    }

    /// <summary>
    /// Walk to the doorway, study it, and record where it leads. The candidate check
    /// is re-asked throughout, so a doorway that stops qualifying mid-survey ends the
    /// job instead of recording something that is no longer true.
    /// </summary>
    public sealed class JobDriver_SurveyFrontier : JobDriver
    {
        private const int SurveyTicks = 600;

        /// <summary>
        /// Survey time once a branch has reference standards to measure against.
        ///
        /// **Measurement tier 3: `RR_Cap_RapidSurvey`.** Ten seconds rather than fourteen at
        /// normal speed. Visible on the progress bar the job already draws, which is the point:
        /// an unlock nobody can see happening is the thing invariant 136 deletes.
        /// </summary>
        private const int RapidSurveyTicks = 420;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        { return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed); }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !NaturalFrontierService.IsFrontierCandidate(job.targetA.Thing));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            RimroomsCampaignComponent surveyCampaign = Current.Game == null ? null
                : Current.Game.GetComponent<RimroomsCampaignComponent>();
            int surveyTicks = surveyCampaign != null && surveyCampaign.HasCapability("RR_Cap_RapidSurvey")
                ? RapidSurveyTicks : SurveyTicks;
            Toil survey = Toils_General.Wait(surveyTicks, TargetIndex.A);
            survey.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            survey.WithProgressBarToilDelay(TargetIndex.A);
            yield return survey;
            Toil record = ToilMaker.MakeToil("RR_SurveyFrontier");
            record.initAction = RecordDiscovery;
            record.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return record;
        }

        private void RecordDiscovery()
        {
            Thing door = job.targetA.Thing;
            CompanyActionResult result = NaturalFrontierService.Discover(door);
            if (result.Success && !result.AlreadyApplied)
            {
                Messages.Message("RR_Frontier_Discovered".Translate(pawn.LabelShortCap),
                    door, MessageTypeDefOf.PositiveEvent, false);
                return;
            }
            if (!result.Success && !string.IsNullOrEmpty(result.MessageKey))
            { Messages.Message(result.MessageKey.Translate(), door, MessageTypeDefOf.RejectInput, false); }
        }
    }
}
