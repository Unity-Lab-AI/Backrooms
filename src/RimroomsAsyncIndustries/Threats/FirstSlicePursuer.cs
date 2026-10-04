using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// What follows a crew through a coordinate — an ordinary RimWorld pawn, hunting by
    /// RimWorld's own rules.
    ///
    /// ## Owner direction, 2026-10-04, verbatim
    ///
    /// *"yeah things that chase you are just npc pawns and wild animals and shit of the gasme
    /// spawned in procedurally and dynamically for randomness encounters, not somew new type of
    /// np0c in the backrooms, they should be nutral, allies, and enemy in all differnt kinds and
    /// relations and scenrios. not some blob figure, just normal core mechanics"*
    ///
    /// ## What this replaced, and why none of it was core mechanics
    ///
    /// The chaser was `RR_QuietPursuer`: a `ThingDef` drawn with `Things/Mote/Black` at 1.4
    /// tiles, driven by a bespoke `Thing_QuietPursuer : ThingWithComps, IAttackTarget` whose own
    /// comment said *"No native pawn AI or unbounded melee attacks."* Concretely it
    ///
    /// - **teleported.** `pursuer.Position = cell` moved it room to room. It never walked, never
    ///   pathfound and never opened a door, so nothing a player knows about RimWorld applied;
    /// - **struck once, scripted.** Two points of blunt damage to a named arm, only against a
    ///   target above 80% health, then it withdrew — win or lose, the same two points;
    /// - **withdrew after three advances**, by a counter;
    /// - **was a blob**, which is the owner's word for it.
    ///
    /// Every one of those is now Core's: a real `Pawn` of a Core `PawnKindDef` in a hostile
    /// faction, spawned two rooms out, which then hunts with the same AI, the same pathing, the
    /// same doors, the same weapons and the same wounds as any hostile anywhere else in the game.
    /// **The file is shorter and does less, which is the point** — the behaviour it used to
    /// simulate is behaviour the game already has.
    ///
    /// ## Procedural, dynamic, and still reproducible
    ///
    /// The kind is drawn from the hostile humanlike kinds this package already vetted for its
    /// psychotic inhabitant families **and from the map biome's own wild animals**, so *"npc
    /// pawns and wild animals and shit of the gasme"* is literal. The draw is
    /// `CampaignSeed.Derive` on the opening id rather than `Rand`, so one opening always meets
    /// the same chaser — reload and it is the same thing coming — while two openings differ.
    ///
    /// ## What was deliberately kept
    ///
    /// The **two-rooms-out placement**, because an encounter that begins on top of you is not an
    /// encounter. The **sighting and withdrawal letters**, because they are how a player learns
    /// anything happened. And the **detection capabilities**: `RR_Cap_EarlyWarning` and
    /// `RR_Cap_Detection` used to widen the grace before a scripted strike, which no longer
    /// exists, so they now widen the **radius at which the chaser is announced**. A branch that
    /// has studied what is down there sees it coming from further off, which is the same promise
    /// paid in the same currency — time, not damage.
    /// </summary>
    public sealed partial class FirstSliceSiteComponent
    {
        /// <summary>
        /// Hostile humanlike kinds a chaser may be.
        ///
        /// The same three `RR_Inhabitant_Psychotic` already draws from, so the package has one
        /// vetted list of *"people down here who will hurt you"* rather than two. All three are
        /// Core; none is authored by this mod.
        /// </summary>
        private static readonly string[] HostileHumanlikeKinds = { "Pirate", "Drifter", "Villager" };

        /// <summary>
        /// How many rooms out a chaser is announced from, by what the branch has researched.
        ///
        /// **These capabilities used to buy grace before a scripted strike.** The strike is gone
        /// with the rest of the bespoke behaviour, so they buy the thing they always promised
        /// instead: knowing sooner. One room is the base — you notice it next door.
        /// </summary>
        private int DetectionRadiusRooms
        {
            get
            {
                RimroomsCampaignComponent campaign = Campaign;
                if (campaign == null) { return 1; }
                // Detection supersedes EarlyWarning rather than stacking, exactly as the grace
                // calculation it replaces did: three rooms, not four.
                if (campaign.HasCapability("RR_Cap_Detection")) { return 3; }
                return campaign.HasCapability("RR_Cap_EarlyWarning") ? 2 : 1;
            }
        }

        /// <summary>
        /// Which Core pawn kind is coming, drawn from the opening rather than from `Rand`.
        ///
        /// Mixes the hostile humanlike kinds with the **map biome's own wild animals**, because
        /// the owner's *"npc pawns and wild animals and shit of the gasme"* is a list of two
        /// things and a roster of only people is half an answer. A biome with no wild animals
        /// falls back to the humanlike kinds, which every map has.
        /// </summary>
        private PawnKindDef ChaserKind()
        {
            var roster = new List<PawnKindDef>();
            foreach (string name in HostileHumanlikeKinds)
            {
                PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(name);
                if (kind != null) { roster.Add(kind); }
            }
            if (map != null && map.Biome != null)
            {
                // Core's own biome roster. Nothing here authors an animal or assumes one exists:
                // a biome that offers none simply contributes none.
                foreach (PawnKindDef animal in map.Biome.AllWildAnimals)
                {
                    if (animal != null && animal.race != null && animal.race.race != null)
                    { roster.Add(animal); }
                }
            }
            if (roster.Count == 0) { return null; }
            roster = roster.OrderBy(kind => kind.defName).ToList();
            // **DERIVED, NEVER `Rand`.** One opening always meets the same chaser, so a reload
            // does not reroll what is hunting you, and two openings differ. The same discipline
            // every saved coordinate property in this package is held to.
            // `Derive` takes an int seed and a stable string key: the BRANCH seed salted
            // with this opening. Same opening, same chaser, across any number of reloads.
            RimroomsCampaignComponent seedSource = Campaign;
            int branchSeed = seedSource == null ? 0 : seedSource.BranchSeed;
            int draw = CampaignSeed.Derive(branchSeed, "chaser:kind:" + (openingId ?? ""), 1);
            if (draw < 0) { draw = ~draw; }
            return roster[draw % roster.Count];
        }

        /// <summary>
        /// Put a chaser two rooms from the crew and let the game take it from there.
        ///
        /// The placement rules are the ones that were already here and already right: never the
        /// threshold room, exactly two rooms out by the link graph, and only into a room a
        /// crew member can actually reach — an unopened room is not a pursuit route, so the
        /// encounter is retried later rather than wasted.
        /// </summary>
        private void StartPursuer(RoomRecord crewRoom, int now)
        {
            if (pursuerEncounterStarted) { return; }
            CoordinateRecord coordinate = Coordinate;
            Dictionary<int, int> distances = DistancesFrom(crewRoom.index);
            PawnKindDef kind = ChaserKind();
            if (kind == null) { return; }
            RoomRecord distant = null;
            IntVec3 cell = IntVec3.Invalid;
            foreach (RoomRecord candidate in coordinate.Rooms.Where(r => r.familyId != "threshold_room" &&
                distances.ContainsKey(r.index) && distances[r.index] == 2).OrderBy(r => r.index))
            {
                if (!TryRoomCell(candidate, out IntVec3 possible)) { continue; }
                if (!crew.Any(p => p != null && !p.Dead && !p.Downed && p.Spawned && p.Map == map &&
                    RoomAt(p.Position)?.Index == crewRoom.Index && map.reachability.CanReach(possible, p.Position,
                        PathEndMode.Touch, TraverseParms.For(TraverseMode.NoPassClosedDoors)))) { continue; }
                distant = candidate;
                cell = possible;
                break;
            }
            if (distant == null) { return; }
            try
            {
                // **AN ORDINARY HOSTILE, MADE THE ORDINARY WAY.** `PawnGenerator` gives it a body,
                // a backstory, gear, health and skills, because it is a person or an animal rather
                // than a manifestation. An animal kind generates with no faction and is turned
                // manhunter instead, which is Core's own way of saying *this one is coming for
                // you* and is why a wild animal chaser needs nothing authored.
                bool animal = kind.race != null && kind.race.race != null && kind.race.race.Animal;
                Faction hostile = animal ? null : Faction.OfAncientsHostile;
                Pawn chaser = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, hostile,
                    PawnGenerationContext.NonPlayer, map.Tile, forceGenerateNewPawn: true));
                if (chaser == null) { return; }
                Thing spawned = GenSpawn.Spawn(chaser, cell, map);
                if (spawned != chaser || !chaser.Spawned || chaser.Map != map)
                { throw new InvalidOperationException("Native spawn did not attach the chaser to its site."); }
                if (animal && chaser.mindState != null)
                {
                    chaser.mindState.mentalStateHandler.TryStartMentalState(
                        MentalStateDefOf.Manhunter, null, true);
                }
                pursuer = chaser;
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Threat] Chaser placement failed; no sighting awarded: " + error);
                if (pursuer != null && !pursuer.Destroyed && (!pursuer.Spawned || pursuer.Map == map))
                { pursuer.Destroy(DestroyMode.Vanish); }
                pursuer = null;
                Note("RR_Event_PursuerPlacementFailed");
                return;
            }
            pursuerEncounterStarted = true;
            pursuerWithdrawn = false;
            pursuerRoom = distant.index;
            // A reported sighting reveals its cell, never an unexplored room graph.
            map.fogGrid.Unfog(cell);
            Note("RR_Event_PursuerSighting", (pursuerRoom + 1).ToString(), "2");
        }

        /// <summary>
        /// Follow where it actually is, and say so. **It is not driven from here.**
        ///
        /// This used to decide the chaser's next room and move it there. A real hostile decides
        /// that itself, so all that is left is reading its position for the readout, announcing
        /// it once it is inside the detection radius, and closing the encounter when it is over.
        /// </summary>
        private void AdvancePursuer(int now, List<Pawn> present, RoomRecord currentCrewRoom)
        {
            if (!pursuerEncounterStarted || pursuerWithdrawn) { return; }
            // Dead, gone, carried off, or downed long enough to stop being a chase. Core decided
            // every one of those; this only notices.
            if (pursuer == null || pursuer.Destroyed || !pursuer.Spawned || pursuer.Map != map ||
                pursuer.Dead)
            { WithdrawPursuer(true); return; }
            // Everybody is home. There is nothing left to chase on this map.
            if (present.Count == 0 || present.All(p => RoomAt(p.Position)?.familyId == "threshold_room"))
            { WithdrawPursuer(true); return; }

            RoomRecord here = RoomAt(pursuer.Position);
            if (here != null) { pursuerRoom = here.index; }

            Pawn closest = present.Where(p => !p.Downed && RoomAt(p.Position) != null &&
                    RoomAt(p.Position).familyId != "threshold_room")
                .OrderBy(p => p.Position.DistanceToSquared(pursuer.Position))
                .ThenBy(p => p.thingIDNumber).FirstOrDefault();
            if (closest == null) { return; }

            // **THE WARNING, AT THE RADIUS THE BRANCH PAID FOR.** Announced once per target: a
            // letter every time it crosses a room boundary would be noise, and the thing a player
            // needs is *it has noticed you and it is close*.
            Dictionary<int, int> fromChaser = here == null
                ? new Dictionary<int, int>() : DistancesFrom(here.index);
            RoomRecord targetRoom = RoomAt(closest.Position);
            int rooms = targetRoom != null && fromChaser.ContainsKey(targetRoom.index)
                ? fromChaser[targetRoom.index] : int.MaxValue;
            if (rooms <= DetectionRadiusRooms)
            {
                if (contactWarningTick < 0 || contactPawn != closest)
                {
                    contactWarningTick = now;
                    contactPawn = closest;
                    Note("RR_Event_PursuerContactWarning", closest.LabelShortCap.ToString());
                }
            }
            else
            {
                contactWarningTick = -1;
                contactPawn = null;
            }
        }

        /// <summary>
        /// Drive it off — with Core's own fear, not by moving it.
        ///
        /// A hostile that has been hurt badly enough to break off is a thing RimWorld already
        /// models, so this asks for that instead of teleporting the chaser down the corridor and
        /// resetting a timer. Called from nowhere special now: Core's combat does the hurting.
        /// </summary>
        public void RepelPursuer()
        {
            if (!pursuerEncounterStarted || pursuerWithdrawn) { return; }
            if (pursuer == null || pursuer.Destroyed || !pursuer.Spawned) { WithdrawPursuer(true); return; }
            bool fled = pursuer.mindState != null && pursuer.mindState.mentalStateHandler != null &&
                pursuer.mindState.mentalStateHandler.TryStartMentalState(
                    MentalStateDefOf.PanicFlee, null, true);
            if (!fled)
            {
                // Nothing to panic with -- an animal already manhunting, or a pawn Core refused
                // the state for. Send it off the map, which is the other ordinary way a hostile
                // stops being this map's problem.
                if (pursuer.mindState != null) { pursuer.mindState.exitMapAfterTick = Find.TickManager.TicksGame; }
            }
            contactWarningTick = -1;
            contactPawn = null;
            Note("RR_Event_PursuerRepelled", (pursuerRoom + 1).ToString());
        }

        /// <summary>
        /// The encounter is over.
        ///
        /// **It no longer destroys the pawn**, and that is deliberate. A dead raider leaves a
        /// corpse to strip and a live one that walked away may be met again; vanishing the thing
        /// a crew just fought is the kind of event that reads as a bug. Only a chaser still
        /// standing on this map when the place is being torn down is removed, and that is done by
        /// the site teardown rather than here.
        /// </summary>
        private void WithdrawPursuer(bool report)
        {
            bool wasActive = pursuerEncounterStarted && !pursuerWithdrawn;
            pursuerWithdrawn = true;
            pursuer = null;
            if (report && wasActive && Coordinate != null) { Note("RR_Event_PursuerWithdrawn"); }
        }

        private Dictionary<int, int> DistancesFrom(int origin)
        {
            var result = new Dictionary<int, int> { { origin, 0 } };
            var pending = new Queue<int>();
            pending.Enqueue(origin);
            while (pending.Count != 0 && result.Count <= 8)
            {
                int current = pending.Dequeue();
                RoomRecord room = Coordinate.Rooms.FirstOrDefault(r => r.index == current);
                if (room == null) { continue; }
                foreach (int next in room.links)
                {
                    RoomRecord nextRoom = Coordinate.Rooms.FirstOrDefault(r => r.index == next);
                    if (nextRoom == null || nextRoom.familyId == "threshold_room" || result.ContainsKey(next)) { continue; }
                    result[next] = result[current] + 1;
                    pending.Enqueue(next);
                }
            }
            return result;
        }

        private bool TryRoomCell(RoomRecord room, out IntVec3 cell)
        {
            foreach (IntVec3 candidate in room.Bounds.Cells.OrderBy(c => c.DistanceToSquared(room.Bounds.CenterCell)))
            {
                if (!candidate.InBounds(map) || !candidate.Standable(map) || candidate.GetFirstPawn(map) != null ||
                    candidate.GetEdifice(map) != null || candidate.GetFirstItem(map) != null) { continue; }
                cell = candidate;
                return true;
            }
            cell = IntVec3.Invalid;
            return false;
        }
    }
}
