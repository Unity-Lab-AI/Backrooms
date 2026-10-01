using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The clear squad. When every person at the laboratory is down, The Company arrives, and
    /// what it leaves behind is a working facility with nobody in it who remembers.
    ///
    /// **Owner direction, 2026-10-01, verbatim:** *"a the company clear squad when all pawns
    /// incompacitated.. they should arrive do a full sweep of every rroom on the reall world map,
    /// disconnect the gate and burry the dead or incenerate on propery might need to build graves
    /// in the moment then they go through the whole facility fix broken walls and equipment leave
    /// supplies food asurvival meals like starting all over again but this happens in game with
    /// the player never losing the game. but this only happens for the lab secnerio for now"*,
    /// and the short version: *"if u die all pawns incompacitated... \"The Company\" sends in a
    /// goon squad kills every thing takes the dead and leeaves three new pawns to run the
    /// facility ... then they haul everything and repair and shut down the gate and haull abay
    /// all bonds printed that are on the map u lose it all and 25M is deducted from account for
    /// \":restocking the pedycash\" upto 25M from account never going under 0 dollars in
    /// account"*.
    ///
    /// ## The downed do not survive it
    ///
    /// Asked what happens to colonists who are down but alive, the owner answered: ***"the
    /// downed: No Witnesses"***. The trigger **is** total incapacitation, so the squad lands on
    /// people who are breathing, and it does not leave them breathing. **This is a deliberate,
    /// destructive reset of the player's roster**, settled before a line of this was written,
    /// because the other reading — stabilise and keep them — would preserve colonists the owner
    /// has decided do not get preserved.
    ///
    /// ## This is an event, not a unit, and that is a design decision rather than a shortcut
    ///
    /// The owner asked for a squad that *"can kill anything without dying"* and that *"have keeys
    /// to all doors on map"*. **Core cannot make a pawn invulnerable**, and a simulated squad
    /// that could be shot, or stopped by a locked door, would break the single thing this feature
    /// exists to provide: a guarantee that a branch never dies. So the work lands as **one
    /// deterministic operation** and the only pawns the player ever sees are the three who stay.
    ///
    /// Door keys and invulnerability are therefore **moot rather than unimplemented** — there is
    /// no one to stop and no door to open. <see cref="ClearHostiles"/> in
    /// <c>FacilityRelief.cs</c> has worked exactly this way since 0.11.7-dev.
    ///
    /// ## Why this is beside the clean-up team and not inside it
    ///
    /// `FacilityRelief` is the promise for **every** branch in corporation contact: no living
    /// staff anywhere, five replacements, hostiles cleared, crate dropped. The owner scoped this
    /// one: *"this only happens for the lab secnerio for now we will figure out how to impliment
    /// it in other scenreios later"*.
    ///
    /// Keeping them separate is what makes that scoping real. The Store and Solo/Group branches
    /// keep the relief they were promised — **five** staff, and a trigger that waits for actual
    /// death — while the laboratory gets this. Folding the new behaviour into the old path would
    /// have silently rewritten the bargain for two scenarios the owner excluded, and that is the
    /// defect shape this project keeps meeting: one rule, quietly applied where nobody asked for
    /// it.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>
        /// The laboratory start, matched by the id its own `RimroomsStartDef` carries.
        /// `RR_Starts.xml` declares exactly three: `async_industries`,
        /// `furniture_knickknack_store` and `lone_survivor`.
        /// </summary>
        private const string LaboratoryScenarioId = "async_industries";

        /// <summary>
        /// *"25M is deducted from account for \":restocking the pedycash\" upto 25M from account
        /// never going under 0 dollars in account"*.
        ///
        /// **Up to**, and never below zero. A branch holding eight million pays eight million and
        /// is not driven into debt, because the owner said so twice in one sentence.
        /// </summary>
        private const long RestockingChargeUsd = 25000000L;

        /// <summary>
        /// *"leeaves three new pawns to run the facility"*. **Three, and these three.**
        ///
        /// The relief lands five, one per company role, and a proof asserts that count. This is
        /// deliberately a different list rather than a truncation of that one: somebody has to
        /// run the place, keep it standing, and hold the door. Research and medical logistics are
        /// what a rebuilt branch hires back once it is a branch again.
        /// </summary>
        private static readonly string[] ClearSquadRoles = { "operations", "engineering", "security" };

        /// <summary>How many times the squad has come. A record, never a limit — same as the relief.</summary>
        private int clearSquadCount;

        /// <summary>When the squad last came. History, not a countdown; nothing compares it to anything.</summary>
        private int lastClearSquadTick = -1;

        internal void ExposeClearSquad()
        {
            Scribe_Values.Look(ref clearSquadCount, "rr_clearSquadCount", 0);
            Scribe_Values.Look(ref lastClearSquadTick, "rr_lastClearSquadTick", -1);
        }

        /// <summary>How many times The Company has had to clear this facility.</summary>
        public int ClearSquadCount { get { return clearSquadCount; } }

        /// <summary>
        /// Whether this branch is the laboratory. **The whole feature hangs off this.**
        /// *"this only happens for the lab secnerio for now"*.
        /// </summary>
        public bool IsLaboratoryBranch
        {
            get { return string.Equals(scenarioId, LaboratoryScenarioId, StringComparison.Ordinal); }
        }

        /// <summary>
        /// Whether one employed staff member is still **on their feet** anywhere.
        ///
        /// This is the owner's change, and it is a different question from
        /// <c>AnyLivingStaff</c>. That one asks whether anybody is alive and deliberately
        /// **does not** treat downed as dead, with a written reason: *"A branch whose staff are
        /// all unconscious is in trouble, not gone."* **That reasoning still holds for the two
        /// scenarios it was written for**, and it is still what the relief uses. The owner
        /// overruled it for the laboratory only: *"when all pawns incompacitated"*.
        ///
        /// **Anywhere still matters.** A crew standing in a Backrooms coordinate is on its feet,
        /// so a player who has taken everybody through a gate must never come home to this.
        /// </summary>
        private bool AnyCapableStaff()
        {
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed) { continue; }
                Pawn pawn = member.pawn;
                if (pawn == null || pawn.Dead || pawn.Destroyed || pawn.Discarded) { continue; }
                if (pawn.Downed) { continue; }
                return true;
            }
            return false;
        }

        /// <summary>
        /// Every map this branch owns, headquarters first.
        ///
        /// *"a full sweep of every rroom on the reall world map"* is the facility, and *"all bonds
        /// printed that are on the map"* with *"u lose it all"* is everywhere — a fortune in paper
        /// left in a coordinate is still the branch's money and is still lost. One list serves
        /// both, and `OwnsMap` is the predicate that already decides what belongs to this branch.
        /// </summary>
        private List<Map> OwnedMaps()
        {
            var owned = new List<Map>();
            List<Map> maps = Find.Maps;
            if (maps == null) { return owned; }
            Map home = headquarters;
            if (home != null && maps.Contains(home)) { owned.Add(home); }
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map == home || !OwnsMap(map)) { continue; }
                owned.Add(map);
            }
            return owned;
        }

        /// <summary>
        /// Checked on the company's own cadence, from <c>TickFacilityRelief</c>. Cheap in almost
        /// every call: a string comparison and a staff scan that stops at the first person
        /// standing.
        /// </summary>
        internal void TickClearSquad(Map map)
        {
            if (!IsLaboratoryBranch) { return; }
            if (AnyCapableStaff()) { return; }
            try { RunClearSquad(map); }
            catch (Exception error)
            {
                // A guarantee that throws must not take the save with it. The condition stays
                // true, so the next company tick tries again rather than leaving the branch dead
                // with a promise that quietly stopped applying. Same posture as the relief.
                Log.Warning("[Rimrooms] clear squad could not complete: " + error);
            }
        }

        private void RunClearSquad(Map map)
        {
            int now = Find.TickManager.TicksGame;
            List<Map> owned = OwnedMaps();

            // The order matters and is the order the owner described it in.
            //
            // Witnesses first, because the sweep that follows collects *the dead*, and a pawn who
            // is still down when the corpses are gathered would be left on the floor of a
            // finished facility. Hostiles next, so nothing is standing while the squad works.
            int silenced = 0;
            int cleared = 0;
            for (int index = 0; index < owned.Count; index++)
            {
                silenced += SilenceWitnesses(owned[index]);
                cleared += ClearHostiles(owned[index]);
            }

            // *"takes the dead"*, *"burry the dead or incenerate on propery"*.
            int buried = 0;
            int incinerated = 0;
            for (int index = 0; index < owned.Count; index++)
            {
                int burnt;
                buried += InterTheDead(owned[index], out burnt);
                incinerated += burnt;
            }

            // *"fix broken walls and equipment"*, *"and repair"*.
            int repaired = 0;
            for (int index = 0; index < owned.Count; index++)
            { repaired += RepairTheFacility(owned[index]); }

            // *"disconnect the gate"*, *"and shut down the gate"*.
            int gates = 0;
            for (int index = 0; index < owned.Count; index++)
            { gates += ShutDownGates(owned[index]); }

            // *"haull abay all bonds printed that are on the map u lose it all"*.
            long confiscated = ConfiscateBonds(owned);

            // The crate and the three, and nothing is recorded if nobody arrives.
            IntVec3 centre = ReliefDropCell(map);
            var payload = new List<Thing>();
            var arrived = new List<string>();
            for (int index = 0; index < ClearSquadRoles.Length; index++)
            {
                Pawn pawn = GenerateReliefStaff(ClearSquadRoles[index]);
                if (pawn == null) { continue; }
                payload.Add(pawn);
                arrived.Add(ClearSquadRoles[index]);
            }
            if (payload.Count == 0)
            {
                // Nobody arrived, so nothing is charged and nothing is recorded. The facility is
                // still empty and the next tick tries again. **Claiming a clearance that put no
                // one on the map, after charging twenty-five million for it, would be worse than
                // the failure** — which is why the charge is below this line and not above it.
                return;
            }

            CompanySupplyDrop.Fill(payload, ReliefSupplyScale);

            clearSquadCount++;
            lastClearSquadTick = now;

            // *"25M is deducted from account for \":restocking the pedycash\""*. Charged after the
            // arrival is certain, with an operation id carrying the clearance number, so a reload
            // cannot bill the same clearance twice and a second clearance is not mistaken for it.
            long charged = ChargeRestocking();

            DropPodUtility.DropThingsNear(centre, map, payload, 110, false, false, true,
                forbid: false);

            for (int index = 0; index < arrived.Count; index++)
            {
                Pawn pawn = payload[index] as Pawn;
                if (pawn == null) { continue; }
                RegisterClearSquadStaff(pawn, arrived[index], now);
            }

            // *"this happens in game with the player never losing the game"*. Core sets this when
            // the last free colonist goes down and posts the letter 400 ticks later;
            // `CheckOrUpdateGameOver` clears it once a map holds a free colonist again, so three
            // arrivals are usually enough on their own. **Usually is not a guarantee**, and this
            // is one.
            if (Find.GameEnder != null) { Find.GameEnder.gameEnding = false; }

            RecordEvent("RR_Event_ClearSquad", BranchId);
            Find.LetterStack.ReceiveLetter(
                "RR_Clear_Title".Translate(),
                "RR_Clear_Body".Translate(CompanyName, silenced, buried + incinerated,
                    repaired, confiscated.ToString("N0"), charged.ToString("N0"),
                    arrived.Count),
                LetterDefOf.NeutralEvent, new TargetInfo(centre, map));
        }

        /// <summary>
        /// ***"the downed: No Witnesses"***.
        ///
        /// Every one of the branch's own people still breathing when the squad arrives is killed.
        /// The trigger is total incapacitation, so in practice this is everybody who has not
        /// already died — which is the point, and why the owner was asked before it was built.
        ///
        /// ## What is in scope, stated rather than left to be discovered
        ///
        /// **Player-faction humanlikes and prisoners held by the player.** A prisoner in a cell
        /// on the property saw what happened and is covered by the words as written.
        ///
        /// **Animals are not.** A pet is property, not a witness, and the owner's clause is about
        /// who can tell. **Neutral and allied visitors are not either**, and that one is a
        /// deliberate call: a trade caravan butchered on the doorstep is a permanent faction war
        /// nobody asked for, and the goal here is *"like starting all over again"* — not a
        /// diplomatic catastrophe bolted onto a rescue. Hostiles are handled by
        /// <see cref="ClearHostiles"/>, which removes them without corpses.
        ///
        /// Killed rather than destroyed, because *"takes the dead"* needs a body to take, and the
        /// burial that follows is most of what the squad does.
        /// </summary>
        private static int SilenceWitnesses(Map map)
        {
            if (map == null || map.mapPawns == null) { return 0; }
            var doomed = new List<Pawn>();
            IReadOnlyList<Pawn> spawned = map.mapPawns.AllPawnsSpawned;
            for (int index = 0; index < spawned.Count; index++)
            {
                Pawn pawn = spawned[index];
                if (pawn == null || pawn.Dead || pawn.Destroyed) { continue; }
                if (pawn.RaceProps == null || !pawn.RaceProps.Humanlike) { continue; }
                bool ours = pawn.Faction == Faction.OfPlayer;
                bool held = pawn.IsPrisonerOfColony;
                if (!ours && !held) { continue; }
                doomed.Add(pawn);
            }
            int count = 0;
            for (int index = 0; index < doomed.Count; index++)
            {
                Pawn pawn = doomed[index];
                if (pawn.Dead || pawn.Destroyed) { continue; }
                try { pawn.Kill(null); count++; }
                catch (Exception error)
                {
                    // One pawn that will not die must not strand the clearance half-done.
                    Log.Warning("[Rimrooms] clear squad could not resolve " +
                                pawn.LabelShortCap + ": " + error);
                }
            }
            return count;
        }

        /// <summary>
        /// *"burry the dead or incenerate on propery might need to build graves in the moment"*,
        /// and *"use and or build a crematoryium and or graves to bury everthing dead"*.
        ///
        /// ## Why a grave does not fit indoors, which is measured and not assumed
        ///
        /// Core's `Grave` is **(1,2)** — two cells, not one — and needs the **`Diggable`** terrain
        /// affordance. Exactly **ten** Core terrains carry it: `Soil`, `SoilRich`, `Sand`,
        /// `SoftSand`, `Gravel`, `PackedDirt`, `MossyTerrain`, `MarshyTerrain`, `Riverbank` and
        /// `Ice`. **Every constructed floor is excluded** — `Concrete`, `SterileTile`, `MetalTile`,
        /// every stone tile, every carpet, every bridge.
        ///
        /// So **a grave cannot be dug inside the facility at all**, which is the kind of thing
        /// that fails silently at runtime and reads as a feature that never worked. Burial goes to
        /// open ground, and the facility's unroofed breezeway and compound are exactly that.
        ///
        /// ## And the fire is the fallback, honestly described
        ///
        /// Where no ground will take a grave, the corpse is destroyed. **That is the
        /// incineration**, and there is no crematorium built for it: a crematorium runs a bill,
        /// a bill needs a worker, and at this moment there is nobody alive to work it. Building an
        /// unpowered one to stand next to would be scenery pretending to be a mechanism.
        /// </summary>
        private static int InterTheDead(Map map, out int incinerated)
        {
            incinerated = 0;
            if (map == null || map.listerThings == null) { return 0; }
            var dead = new List<Thing>(
                map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse));
            int buried = 0;
            for (int index = 0; index < dead.Count; index++)
            {
                var corpse = dead[index] as Corpse;
                if (corpse == null || corpse.Destroyed || !corpse.Spawned) { continue; }
                if (TryBury(map, corpse)) { buried++; continue; }
                corpse.Destroy(DestroyMode.Vanish);
                incinerated++;
            }
            return buried;
        }

        /// <summary>Digs one grave and puts one body in it, or reports that it could not.</summary>
        private static bool TryBury(Map map, Corpse corpse)
        {
            ThingDef graveDef = DefDatabase<ThingDef>.GetNamedSilentFail("Grave");
            if (graveDef == null) { return false; }

            Rot4 facing;
            IntVec3 cell = FreeGraveCell(map, graveDef, corpse.Position, out facing);
            if (!cell.IsValid) { return false; }

            try
            {
                Thing made = ThingMaker.MakeThing(graveDef, null);
                if (made == null) { return false; }
                made.SetFactionDirect(Faction.OfPlayer);
                Thing grave = GenSpawn.Spawn(made, cell, map, facing);
                var casket = grave as Building_Grave;
                if (casket == null) { return false; }
                // `TryAcceptThing` routes through `innerContainer.CanAcceptAnyOf` and the def's
                // own fixed storage settings, which allow the `Corpses` category. The container
                // despawns the corpse itself, so nothing here moves it first.
                return casket.TryAcceptThing(corpse, false);
            }
            catch (Exception error)
            {
                Log.Warning("[Rimrooms] clear squad could not bury a body: " + error);
                return false;
            }
        }

        /// <summary>
        /// Ground that will take a grave, nearest first.
        ///
        /// **Both cells of the (1,2) footprint are checked**, through `GenAdj.OccupiedRect` so the
        /// rotation is Core's own arithmetic rather than a second copy of it — three separate
        /// models of that rotation maths have already disagreed in this project.
        /// `GenConstruct.CanBuildOnTerrain` is what answers the `Diggable` question, for the same
        /// reason: the affordance list belongs to Core and a table of it here would go stale.
        /// </summary>
        private static IntVec3 FreeGraveCell(Map map, ThingDef graveDef, IntVec3 near,
            out Rot4 facing)
        {
            facing = Rot4.North;
            if (map == null || graveDef == null) { return IntVec3.Invalid; }
            if (!near.IsValid || !near.InBounds(map)) { near = map.Center; }

            var rotations = new[] { Rot4.North, Rot4.East };
            foreach (IntVec3 candidate in GenRadial.RadialCellsAround(near, 24f, true))
            {
                if (!candidate.InBounds(map)) { continue; }
                for (int index = 0; index < rotations.Length; index++)
                {
                    if (!GraveFits(map, graveDef, candidate, rotations[index])) { continue; }
                    facing = rotations[index];
                    return candidate;
                }
            }
            return IntVec3.Invalid;
        }

        private static bool GraveFits(Map map, ThingDef graveDef, IntVec3 cell, Rot4 rotation)
        {
            CellRect rect = GenAdj.OccupiedRect(cell, rotation, graveDef.Size);
            foreach (IntVec3 part in rect)
            {
                if (!part.InBounds(map) || part.Fogged(map)) { return false; }
                if (!part.Standable(map)) { return false; }
                if (part.GetEdifice(map) != null) { return false; }
                if (!GenConstruct.CanBuildOnTerrain(graveDef, part, map, rotation)) { return false; }
                List<Thing> things = part.GetThingList(map);
                for (int index = 0; index < things.Count; index++)
                {
                    Thing thing = things[index];
                    if (thing == null) { continue; }
                    // A grave over a body is the one thing that would wipe what it is for.
                    if (thing is Corpse || thing is Pawn) { return false; }
                    if (thing.def != null && thing.def.category == ThingCategory.Building)
                    { return false; }
                    if (thing.def != null && thing.def.passability == Traversability.Impassable)
                    { return false; }
                }
            }
            return true;
        }

        /// <summary>
        /// *"they go through the whole facility fix broken walls and equipment"*, *"and repair"*.
        ///
        /// **Core's own repairable lister answers this**, through the one wrapper this mod already
        /// has for it in `ConnectedWork`. A hand-rolled scan of damaged buildings would be a second
        /// derivation of a rule Core already owns, and that is the defect this project keeps
        /// meeting — `MaxRoomSpan` against the graph ceiling, three copies of `AdjustForRotation`.
        ///
        /// ## What repair cannot mean, said plainly
        ///
        /// A **destroyed** wall leaves no record of itself: no def, no stuff, no position. So
        /// *"fix broken walls"* is damage restored to full, and a wall that is already rubble
        /// **cannot be rebuilt by anything**. Saying so is better than implying a completeness
        /// that is not there.
        /// </summary>
        private static int RepairTheFacility(Map map)
        {
            if (map == null || Faction.OfPlayer == null) { return 0; }
            List<Thing> damaged =
                ConnectedWork.Providers.RepairProvider.RepairableOn(map, Faction.OfPlayer);
            if (damaged == null) { return 0; }
            var snapshot = new List<Thing>(damaged);
            int repaired = 0;
            for (int index = 0; index < snapshot.Count; index++)
            {
                Thing thing = snapshot[index];
                if (thing == null || thing.Destroyed || !thing.Spawned) { continue; }
                if (thing.def == null || !thing.def.useHitPoints) { continue; }
                if (thing.HitPoints >= thing.MaxHitPoints) { continue; }
                thing.HitPoints = thing.MaxHitPoints;
                repaired++;
                // Core's lister tracks damage, so telling it the building is whole again is what
                // stops a repair job being queued for something with full hit points.
                if (map.listerBuildingsRepairable != null && thing is Building)
                { map.listerBuildingsRepairable.Notify_BuildingRepaired((Building)thing); }
            }
            return repaired;
        }

        /// <summary>
        /// *"disconnect the gate"*, *"and shut down the gate"*.
        ///
        /// A ramp is aborted and an open connection is cut, which is the same call the player's
        /// own emergency cutoff makes — so a gate that was already in emergency is left alone and
        /// the count below is the number of connections this actually closed.
        ///
        /// **The gate stays commissioned.** *"like starting all over again"* is the crew starting
        /// again, not the machine: decommissioning it would make the three arrivals rebuild an
        /// eight-component assembly before they could do the job they were sent for. Shutting it
        /// down is what was asked; dismantling it was not.
        /// </summary>
        private static int ShutDownGates(Map map)
        {
            if (map == null || map.listerBuildings == null) { return 0; }
            int closed = 0;
            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            var snapshot = new List<Building>(buildings);
            for (int index = 0; index < snapshot.Count; index++)
            {
                Building building = snapshot[index];
                if (building == null || building.Destroyed) { continue; }
                Gate.CompRimroomsGate gate = building.TryGetComp<Gate.CompRimroomsGate>();
                if (gate == null || !gate.IsDesignated) { continue; }
                if (gate.IsSpinningUp) { gate.AbortSpinUp(); closed++; continue; }
                if (gate.IsOpening && gate.TriggerEmergencyCutoff().Success) { closed++; }
            }
            return closed;
        }

        /// <summary>
        /// *"haull abay all bonds printed that are on the map u lose it all"*.
        ///
        /// **Destroyed, and credited nowhere.** `BondService.ConsumeBonds` already destroys paper
        /// and returns its face value, which is what `RedeemBondsInRadius` uses to pay a player
        /// banking their own money. **The total is reported and deliberately not posted** — it
        /// goes in the letter so the player is told exactly what the clearance cost them, and it
        /// goes nowhere near <c>PostTransaction</c>. Routing it through `DepositBondPaper` would
        /// have *paid* for it, which is the opposite of *"u lose it all"*.
        /// </summary>
        private static long ConfiscateBonds(List<Map> owned)
        {
            long taken = 0L;
            if (owned == null) { return 0L; }
            for (int index = 0; index < owned.Count; index++)
            {
                Map map = owned[index];
                if (map == null || map.listerThings == null) { continue; }
                var paper = new List<Thing>();
                List<Thing> all = map.listerThings.AllThings;
                for (int item = 0; item < all.Count; item++)
                {
                    Thing thing = all[item];
                    if (thing == null || thing.Destroyed) { continue; }
                    if (Economy.BondService.FaceValueOf(thing) <= 0L) { continue; }
                    paper.Add(thing);
                }
                taken += Economy.BondService.ConsumeBonds(paper);
            }
            return taken;
        }

        /// <summary>
        /// *"25M is deducted from account for \":restocking the pedycash\" upto 25M from account
        /// never going under 0 dollars in account"*.
        ///
        /// **Up to, and never below zero**, which the owner said twice in one sentence. The amount
        /// is clamped to the balance before it is posted rather than relying on
        /// <c>PostTransaction</c>'s own refusal: that refusal would reject the whole charge and
        /// take nothing, where the owner asked for whatever is there.
        ///
        /// The operation id carries the clearance number, so **a reload cannot bill the same
        /// clearance twice** and a second clearance is not mistaken for a replay of the first.
        /// Returns what was actually taken, which is what the letter reports.
        /// </summary>
        private long ChargeRestocking()
        {
            long amount = Math.Min(RestockingChargeUsd, BalanceUsd);
            if (amount <= 0L) { return 0L; }
            string operationId = branchId + ":clearsquad:" + clearSquadCount + ":restocking";
            CompanyActionResult result =
                PostTransaction(operationId, -amount, "RR_Clear_RestockingReason", BranchId);
            // A refused charge is reported as nothing taken rather than as a charge that
            // happened. The clearance itself is not conditional on the money: the guarantee is
            // the facility surviving, and the bill is what the corporation does about it.
            // `Existing()` already sets Success, so a replayed charge reports the
            // amount exactly as the first one did.
            return result.Success ? amount : 0L;
        }

        /// <summary>
        /// Puts a clearance arrival on the books.
        ///
        /// Separate from <c>RegisterReliefStaff</c> only in the id it mints, so the two never
        /// collide in a save where both have fired. Same wage, same payroll, same ordinary
        /// employment from the moment they land: **the clearance is free and keeping the people
        /// afterwards is not.**
        /// </summary>
        private void RegisterClearSquadStaff(Pawn pawn, string role, int now)
        {
            if (pawn == null || pawn.Dead || pawn.Destroyed) { return; }
            string id = branchId + ":clearsquad:" + clearSquadCount + ":" + role;
            for (int index = 0; index < staff.Count; index++)
            {
                if (staff[index] != null && staff[index].id == id) { return; }
            }
            staff.Add(new StaffRecord
            {
                id = id,
                pawn = pawn,
                pawnLoadId = pawn.GetUniqueLoadID(),
                nameAtHire = pawn.LabelShortCap.ToString(),
                role = Personnel.PersonnelRoles.Valid(role) ? role : "operations",
                dailyWageUsd = ReliefDailyWageUsd(),
                hiredTick = now,
                employed = true,
            });
        }
    }
}
