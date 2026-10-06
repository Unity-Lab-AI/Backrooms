using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// The single place that decides who may pass through a portal and in what
    /// role. Every crossing path must ask this policy, so no later work adapter,
    /// job or scheduler can quietly let the far side walk out on its own.
    ///
    /// Owner rule: inhabitants and monstrosities stay in the Backrooms. Nothing
    /// that is not this company's own pawn crosses under its own will, and an open
    /// connection is never a reason for the far side to move toward the threshold.
    /// Anything else reaches the near side only because one of this company's
    /// pawns physically carried it through by ordinary work.
    ///
    /// **One named exception, added 2026-09-29 on owner direction**: see
    /// <see cref="IncursionFailureKey"/>. In the worst coordinates, on an advanced
    /// machine, with a connection actually open, a hostile that has followed a crew
    /// to the far doorway may come through it, once. Every clause of the rule above
    /// still holds around it: it does not cross *under its own will* -- it has no
    /// will about the gate at all, because
    /// <see cref="MayApproachThresholdForTraversal"/> is still false for everything
    /// and nothing on the far side is ever given a threshold as a destination. It
    /// walks to the doorway because **your people are standing there**, and the gate
    /// notices what is on its doorstep. The decision is still made here and nowhere
    /// else.
    ///
    /// Gate, machine door and portal are one thing; only the connection kind
    /// differs, laboratory or permanently open natural. The rule is per connection
    /// and holds for every gate at once. Opening a second or tenth gate never
    /// relaxes it, and there is no aggregate exception once several are connected.
    /// Every start can eventually run several gates, so nothing here may assume one
    /// gate per branch, per map or per coordinate.
    ///
    /// ## ⛔ INVARIANT #1 WAS REWRITTEN 2026-10-06 BY OWNER DIRECTION, AND ONLY HALF OF IT WENT ⛔
    ///
    /// **Owner, verbatim:** *"not anyone in base, but anyone on your map.. a enemy can break in and
    /// cross the gate to get valuables and members"*, then *"hold up now friendlys can too"*.
    ///
    /// Read carefully, the old invariant bundled **two** rules, and only one is discarded:
    ///
    /// | The rule | Status |
    /// |---|---|
    /// | **One chokepoint. No adapter, scheduler, generator or threat may ever decide a crossing for itself** | **KEPT, UNCHANGED, AND IT IS THE PART THAT MATTERS** |
    /// | The answer is always no for everybody but our own colonists | **DISCARDED** |
    ///
    /// `ARCHITECTURE.md` stated the fear it was built against: *"an open gate can never become an
    /// objective, lure, spawn target, raid route or attack trigger for a later adapter, scheduler,
    /// generator or threat."* **The weight is on *for a later … threat*** — the worry was a feature
    /// quietly growing a crossing of its own. Keeping one chokepoint answers that completely, and it
    /// is independent of what the chokepoint says yes to.
    ///
    /// **`AutonomousNonPlayerTraversalPermitted` is gone rather than left at false**, because a
    /// constant denying what the code beside it now does is the stale-comment failure this project
    /// has a rule about. <see cref="OutboundCrossingFailureKey"/> replaces it: a named method, asked
    /// here and nowhere else.
    ///
    /// **And <see cref="MayApproachThresholdForTraversal"/> IS STILL FALSE FOR EVERYTHING.** That is
    /// not an oversight — it is the surviving half doing real work. Nothing is ever *lured*: a
    /// hostile or a visitor crosses because it wandered to a threshold that happens to be open, and
    /// the gate notices what is already on its doorstep. The gate is never a destination for anybody
    /// who is not ours, so it can still never become an objective, a lure or a raid route.
    ///
    /// `FINALIZED.md` entry 54 said this must stay false *"for everything, forever"*. The archive is
    /// append-only and is not edited: the owner superseded it on 2026-10-06, and this is where that
    /// is recorded.
    /// </summary>
    public static class PortalTraversalPolicy
    {

        /// <summary>
        /// May this pawn traverse **in the course of company work**? Only this company's
        /// available colonists may. Every connected-work adapter asks this before it will
        /// plan a job across a gate, which is what keeps cross-gate work a thing people do
        /// rather than something an animal or a guest can be scheduled into.
        /// </summary>
        public static string TravellerFailureKey(Pawn traveller)
        {
            if (traveller == null) { return "RR_PortalCrossing_PawnNotEligible"; }
            if (traveller.Faction != Faction.OfPlayer || !traveller.IsColonist)
            { return "RR_PortalTraversal_NotOurPerson"; }
            return RimroomsPortalCrossingService.EligibilityFailureKey(traveller);
        }

        /// <summary>
        /// May this pawn cross on its own legs because **the player ordered it to**?
        ///
        /// **Owner direction, 2026-09-29:** a player-owned animal may cross freely. So this is
        /// wider than <see cref="TravellerFailureKey"/> above, and deliberately kept separate
        /// from it: that one governs *work*, and an animal is not scheduled into a bill.
        ///
        /// **The rule this does not weaken** is the one that matters. What the chokepoint
        /// exists to prevent is the **far side** walking out, and the test for that is
        /// ownership: a pawn must belong to the player's faction. A Backrooms inhabitant is
        /// hostile or unfactioned and fails here exactly as it always did.
        /// <see cref="AutonomousNonPlayerTraversalPermitted"/> is still constant false and
        /// <see cref="MayApproachThresholdForTraversal"/> still returns false for everything.
        /// </summary>
        public static string OrderedCrossingFailureKey(Pawn traveller)
        {
            if (traveller == null) { return "RR_PortalCrossing_PawnNotEligible"; }
            if (traveller.Faction != Faction.OfPlayer) { return "RR_PortalTraversal_NotOurPerson"; }
            if (traveller.RaceProps != null && traveller.RaceProps.Animal)
            {
                // Drafted included. Vanilla cannot draft an animal, but **Draftable Animals -
                // Releashed** (register row 78) is in the owner's profile and can, and a pawn
                // under direct combat control does not walk through a gate whatever it is.
                if (!traveller.Spawned || traveller.Dead || traveller.Downed ||
                    traveller.InMentalState || traveller.Drafted)
                { return "RR_PortalCrossing_PawnNotEligible"; }
                return null;
            }
            return TravellerFailureKey(traveller);
        }

        /// <summary>
        /// The largest body a doorway of a given width admits.
        ///
        /// The numbers come from Core's own races rather than from taste: a person is 1.0, a
        /// muffalo is 2.4, a dromedary 2.1, a boomalope 2.0, and the largest thing Core ships
        /// is 4.0. So a one-wide door passes people and working animals, a two-wide door
        /// passes the pack animals a branch would actually want to walk through a gate, and
        /// three wide or more passes anything at all.
        /// </summary>
        public const float SingleWidthMaxBodySize = 1.2f;
        /// <summary>
        /// The body size a two-cell gate will pass, which is what lets pack animals
        /// through: a muffalo is 2.0 and a dromedary 2.2, so 2.5 clears both with room
        /// rather than sitting on top of either number.
        /// </summary>
        public const float DoubleWidthMaxBodySize = 2.5f;

        /// <summary>The body size a doorway this wide admits, or null for no limit.</summary>
        public static float? MaxBodySizeForWidth(int doorwayWidth)
        {
            if (doorwayWidth <= 1) { return SingleWidthMaxBodySize; }
            if (doorwayWidth == 2) { return DoubleWidthMaxBodySize; }
            return null;
        }

        /// <summary>
        /// The width a vehicle needs, and what decides which of the two vehicle gates.
        ///
        /// ## Owner specification, 2026-10-04, verbatim
        ///
        /// *"this is already layed out, people through 1x1 cdoor gates, herd animals through
        /// 2x1 and vehicals through 3.1 and 3x2 depending size"*
        ///
        /// ## The body-size ladder above already did two of the three rungs
        ///
        /// A person is 1.0 and passes a 1x1; a muffalo is 2.4 and does not, so it needs the
        /// 2-wide — *"people through 1x1 ... herd animals through 2x1"*, exactly. **The rung
        /// that did not exist was the vehicle one**: width three returned *no limit*, so a
        /// three-wide gate admitted anything of any footprint and **nothing anywhere could tell
        /// a 1x3 gate from a 2x3 one.** Two of the four legal footprints were the same gate as
        /// far as the game was concerned.
        ///
        /// ## What *"depending size"* resolves to
        ///
        /// A vehicle has a real footprint, and it drives through long-ways: the dimension that
        /// has to clear the aperture is its **narrower** one. The two vehicle gates differ by
        /// **depth** -- a 1x3 is one cell deep, a 2x3 is two -- so:
        ///
        /// - a 1x2 runabout has a narrow side of 1 and goes through the 1x3;
        /// - a 2x3 truck has a narrow side of 2 and needs the 2x3;
        /// - a 3x5 tank has a narrow side of 3 and **fits through neither**, which is the
        ///   honest end of a ladder the owner bounded at four footprints.
        ///
        /// Depth is read as cells-per-width from the gate itself rather than from the def, so a
        /// gate bound across a run of ordinary doors measures the same way a real wide door does.
        ///
        /// ## Recognised by footprint, never by type
        ///
        /// Vehicles come from a mod. Nothing here references one: a thing whose def occupies
        /// more than a single cell is treated as a vehicle, which is true of every vehicle and
        /// of nothing Core ships as a pawn. That keeps the rule working with the vehicle mods in
        /// the profile and working identically with none of them installed.
        /// </summary>
        public const int WidthForPeople = 1;
        public const int WidthForHerdAnimals = 2;
        public const int WidthForVehicles = 3;

        /// <summary>The footprint of a thing, as (narrow, long) in cells.</summary>
        public static IntVec2 FootprintOf(Thing thing)
        {
            if (thing == null || thing.def == null) { return new IntVec2(1, 1); }
            IntVec2 size = thing.def.size;
            int narrow = size.x <= size.z ? size.x : size.z;
            int wide = size.x <= size.z ? size.z : size.x;
            return new IntVec2(narrow < 1 ? 1 : narrow, wide < 1 ? 1 : wide);
        }

        /// <summary>Whether this thing occupies more than one cell, and so drives rather than walks.</summary>
        public static bool IsMultiCellBody(Thing thing)
        {
            IntVec2 footprint = FootprintOf(thing);
            return footprint.x > 1 || footprint.z > 1;
        }

        /// <summary>
        /// Why a multi-cell body cannot pass an aperture this wide and this deep, or null.
        ///
        /// Separate from <see cref="FitFailureKey(Pawn, int)"/> because a vehicle is not refused
        /// for being heavy -- body size says nothing useful about a machine -- it is refused for
        /// not physically fitting the hole.
        /// </summary>
        public static string VehicleFitFailureKey(Thing vehicle, int doorwayWidth, int doorwayDepth)
        {
            IntVec2 footprint = FootprintOf(vehicle);
            if (doorwayWidth < WidthForVehicles)
            { return "RR_PortalTraversal_NeedsVehicleGate"; }
            if (footprint.z > doorwayWidth)
            { return "RR_PortalTraversal_VehicleTooLong"; }
            if (footprint.x > doorwayDepth)
            { return "RR_PortalTraversal_VehicleTooWide"; }
            return null;
        }

        /// <summary>
        /// Whether this pawn physically fits through a doorway of the given width.
        ///
        /// **Owner direction, 2026-09-29:** the larger gate sizes exist *"to fit vehicals and
        /// the like and bigger creatures"*, so size has to actually stop something or the
        /// sizes are decoration.
        ///
        /// Checked where the **connection** is known rather than where a single endpoint is,
        /// because a connection has one width for both directions: the gate is the machine
        /// that forms the aperture, and the doorway waiting on the Backrooms side is just
        /// where you arrive. Checking an endpoint instead would let a pack animal walk in
        /// through a wide gate and then be unable to come home.
        /// </summary>
        public static string FitFailureKey(Pawn traveller, int doorwayWidth)
        {
            return FitFailureKey(traveller, doorwayWidth, 1);
        }

        /// <summary>
        /// The same question with the aperture's depth known, which is what tells the two
        /// vehicle gates apart. Prefer this overload; the one above assumes the shallower gate,
        /// which is the safe assumption rather than the convenient one.
        /// </summary>
        public static string FitFailureKey(Pawn traveller, int doorwayWidth, int doorwayDepth)
        {
            if (traveller == null) { return "RR_PortalCrossing_PawnNotEligible"; }
            // **A MULTI-CELL BODY IS A MACHINE, AND BODY SIZE SAYS NOTHING USEFUL ABOUT ONE.**
            // Asked before the body-size ladder because the two answer different questions: that
            // one is about a creature's bulk, this one is about whether a shape clears a hole.
            if (IsMultiCellBody(traveller))
            { return VehicleFitFailureKey(traveller, doorwayWidth, doorwayDepth); }
            float? limit = MaxBodySizeForWidth(doorwayWidth);
            if (!limit.HasValue) { return null; }
            float size = traveller.RaceProps == null ? 1f : traveller.BodySize;
            return size > limit.Value ? "RR_PortalTraversal_TooLargeForGate" : null;
        }

        /// <summary>
        /// May this object ride through in a carrier's hands? Materials, tools,
        /// equipment, resources, minified furniture and production benches, corpses,
        /// and people or creatures that are actually being carried all qualify. A
        /// pawn that could walk away on its own does not: it would be traversing,
        /// not being carried.
        /// </summary>
        public static string CargoFailureKey(Thing cargo, Pawn carrier)
        {
            if (cargo == null) { return null; }
            if (carrier == null || carrier.carryTracker == null ||
                carrier.carryTracker.innerContainer == null ||
                !carrier.carryTracker.innerContainer.Contains(cargo))
            { return "RR_PortalTraversal_CargoNotCarried"; }
            Pawn passenger = cargo as Pawn;
            if (passenger == null) { return null; }
            // A carried person or creature must genuinely be in someone's arms:
            // downed, dead, or held as a prisoner. Anything still on its feet would
            // be crossing under its own will, which this policy never allows.
            if (passenger.Dead || passenger.Downed || passenger.IsPrisonerOfColony) { return null; }
            return "RR_PortalTraversal_PassengerNotHeld";
        }

        /// <summary>
        /// Whether a spawned thing on either side may be treated as drawn toward a
        /// threshold. Always false: generation, encounters and threats must never
        /// use an open connection as a destination or a trigger to converge on it.
        ///
        /// **Still false after incursion landed, and that is the point.** A hostile that
        /// follows a crew to the doorway does so because *your people are standing there*,
        /// never because a gate is open. Nothing on the far side is ever given a threshold as
        /// a destination.
        /// </summary>
        public static bool MayApproachThresholdForTraversal(Thing thing)
        {
            return false;
        }

        /// <summary>
        /// The one case in which something that is **not ours** may cross, and the only place
        /// that may ever say yes to it.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"and even at higher techs they can come
        /// through the portal into your base and attack, kidnap, steal, do everything npcs can
        /// do in game"*, under the condition chosen when asked: **depth plus technology, while
        /// an opening is live**.
        ///
        /// This is a deliberate, named exception to the rule the rest of this class exists to
        /// enforce, and it is narrow on five axes at once: a live opening, a coordinate at
        /// <see cref="CoordinatePressureLadder.Band.Hostile"/>, a branch that has advanced the
        /// machine at least one tier, a body that fits the opening, and once per opening.
        ///
        /// **It is still the policy deciding, not the pawn.** Nothing about this method is
        /// reachable by an inhabitant: the gate asks about whatever is already standing at its
        /// far doorway, exactly as every other crossing in this mod is decided by asking here.
        /// </summary>
        public static string IncursionFailureKey(Pawn intruder, CompRimroomsGate gate,
            CoordinateRecord coordinate, float colonyWealth)
        {
            if (intruder == null || gate == null || coordinate == null)
            { return "RR_Incursion_NotEligible"; }
            // Ours never "intrudes". A colonist or a player animal at the far doorway is just
            // somebody about to walk home through their own gate.
            if (intruder.Faction == Faction.OfPlayer) { return "RR_Incursion_NotEligible"; }
            if (!intruder.Spawned || intruder.Dead || intruder.Downed) { return "RR_Incursion_NotEligible"; }
            // Something that is not hostile to the branch has no business walking into it, and
            // an unfactioned wanderer is scenery rather than a threat.
            if (intruder.Faction == null || !intruder.Faction.HostileTo(Faction.OfPlayer))
            { return "RR_Incursion_NotEligible"; }
            if (!gate.IsDesignated || gate.IsEmergency || string.IsNullOrEmpty(gate.PortalOpeningId))
            { return "RR_Incursion_NoOpening"; }
            if (gate.IncursionSpentThisOpening) { return "RR_Incursion_AlreadySpent"; }
            if (CoordinatePressureLadder.BandFor(coordinate, colonyWealth) < CoordinatePressureLadder.Band.Hostile)
            { return "RR_Incursion_BandTooLow"; }
            // "even at higher techs" -- the branch has to have advanced the machine. A first
            // gate, unresearched, is never a way in.
            //
            // **RR_Cap_ContainmentProtocol** (Entities and containment, tier 2) raises that
            // floor from one tier to two. A branch that has written real containment procedure
            // buys back the whole first rung of the aperture ladder: nothing follows a crew out
            // until the gate is opened wider than Field Stability allows.
            //
            // **The bound only ever tightens.** Invariant 53 lists five axes that fence
            // incursion in, and this moves one of them in the safe direction -- there is no
            // capability anywhere that lowers it. It is also a genuine choice between branches:
            // push the gate ladder and neglect containment, and the thing you opened the door
            // wider for walks back through it.
            RimroomsCampaignComponent containmentCampaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            int requiredTier = containmentCampaign != null &&
                containmentCampaign.HasCapability("RR_Cap_ContainmentProtocol") ? 2 : 1;
            if (gate.PortalWindowTier < requiredTier) { return "RR_Incursion_TechTooLow"; }
            return FitFailureKey(intruder, gate.GateWidth, gate.GateOpeningDepth);
        }

        /// <summary>
        /// The other direction: something standing on **your** map walking out through an open gate.
        ///
        /// **Owner direction, 2026-10-06, verbatim:** *"not anyone in base, but anyone on your map..
        /// a enemy can break in and cross the gate to get valuables and members"*, and *"hold up now
        /// friendlys can too"*.
        ///
        /// ## Inbound and outbound are not symmetric and must not share bounds
        ///
        /// <see cref="IncursionFailureKey"/> is narrow on five axes because inbound is a threat to the
        /// colony — the player's people, home and stockpile. Outbound threatens a **remote** stockpile
        /// and whoever is standing on it. The severities differ by a lot, so each axis is re-derived
        /// here rather than copied:
        ///
        /// | Incursion's axis | Outbound |
        /// |---|---|
        /// | only while a connection is open | **yes, unchanged.** A closed gate is a wall both ways, and it is the whole counterplay |
        /// | only at the `Hostile` band | **no.** Coordinate danger says nothing about whether a raider in your base should walk through a door |
        /// | only once the machine is advanced | **no.** A first unresearched gate is still a hole, and the hole is the point |
        /// | only if it fits | **yes, unchanged.** `FitFailureKey` on the gate's own width and depth |
        /// | only once per opening | **no.** The doorstep is the cap — see `GateEgress` |
        ///
        /// ## The motive is the bound, and it came out of the owner's own sentence
        ///
        /// *"to get valuables and members"*. So **nothing crosses outbound unless there is something
        /// over there worth crossing for**, which the caller establishes. That is self-limiting in a
        /// way a hand-tuned number is not: it scales with what the player chose to keep down there, and
        /// it makes the risk legible. Store nothing beyond a gate and you are never raided through one.
        ///
        /// ## Still the policy deciding, never the pawn
        ///
        /// <see cref="MayApproachThresholdForTraversal"/> remains false, so nothing on this side is
        /// ever *given* a gate as a destination. This answers a question about something that already
        /// walked to the threshold on its own business.
        /// </summary>
        public static string OutboundCrossingFailureKey(Pawn traveller, CompRimroomsGate gate)
        {
            if (traveller == null || gate == null) { return "RR_Egress_NotEligible"; }
            // Ours going out is work or a player order, and both are answered above. This method is
            // only ever about somebody who is not ours.
            if (traveller.Faction == Faction.OfPlayer) { return "RR_Egress_NotEligible"; }
            if (!traveller.Spawned || traveller.Dead || traveller.Downed || traveller.InMentalState)
            { return "RR_Egress_NotEligible"; }
            // **A carried passenger is not crossing on its own legs.** Anything downed, dead or
            // imprisoned rides in a carrier's hands under `CargoFailureKey`, which is unchanged, and
            // letting it also qualify here would be two routes for one movement.
            if (traveller.CarriedBy != null) { return "RR_Egress_NotEligible"; }

            // **ANYBODY IN YOUR CUSTODY IS NOT SOMEBODY AT YOUR DOORSTEP, AND THIS WAS A REAL HOLE.**
            //
            // A prisoner of the colony keeps their **original faction** -- `HostFaction` is what
            // becomes yours -- so `traveller.Faction != Faction.OfPlayer` above is **true** for one.
            // A prisoner who got out of their cell and was neither downed nor in a mental state
            // therefore passed every clause of this method, and `FindAtDoorstep` would have taken
            // them: a hostile-faction prisoner was even **preferred**, because that scan returns the
            // first hostile it finds. **A captured pawn standing near an open gate was transferred
            // into the coordinate**, which is invariant 17 broken -- *"a prisoner can never cross a
            // gate"* -- and a real loss of somebody the player had taken and might have recruited.
            //
            // `WorldExit.TravellersAt` has always refused a prisoner and a slave for the walk out to
            // the world, and `CargoFailureKey` only ever let a prisoner cross **in somebody's arms**.
            // This path was the one crossing decision with no custody clause at all, and it was
            // written in the same batch that opened outbound crossing at all.
            //
            // **A quest lodger is the same class of mistake with a worse outcome:** a guest you are
            // required to keep safe has their own faction too, so they qualified, and losing one
            // through a gate fails a quest the player never chose to fail.
            //
            // `IsSlave` is already unreachable here -- a slave's faction IS the player's, refused
            // above -- and it is named anyway, because a rule that holds by accident of another
            // clause is a rule that stops holding when that clause moves.
            if (traveller.IsPrisoner || traveller.IsSlave || traveller.IsQuestLodger()
                || traveller.HostFaction != null)
            { return "RR_Egress_InYourCustody"; }
            if (!gate.IsDesignated || gate.IsEmergency || gate.KillSwitchThrown ||
                string.IsNullOrEmpty(gate.PortalOpeningId))
            { return "RR_Egress_NoOpening"; }
            return FitFailureKey(traveller, gate.GateWidth, gate.GateOpeningDepth);
        }
    }
}
