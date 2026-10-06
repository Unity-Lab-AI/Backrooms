using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// A gate holds while ANY qualified pawn is at ANY console bound to it.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"and as for the write up stations u can have
    /// more than one to have more than one pawn doing it as u can have multiple quests going, and
    /// same with the coms and machine benches so that it isnt dependant at one pawn dying at the
    /// gate from starvvation trying to keep it open forever he can leave when another pawn hops on
    /// the other comms console toggled to gate contrtrols with say upto 4 of them available so
    /// pawns can do geate process better and faster"*, then *"maybe tech gated"*, then *"but maybe
    /// not"* -- and at the fork, **not gated: it is a defect, fixed free.**
    ///
    /// ## THE DEFECT WAS WORSE THAN DESCRIBED, AND THAT WAS MEASURED
    ///
    /// `assignedOperator` is a **single `Pawn` reference** saved by `Scribe_References`, and
    /// `IsOperatorOnStation` asked whether **that one colonist** was standing on **the one bound
    /// console's** interaction cell. §1.1 names *"an operator off station, or no operator at all"*
    /// as a failure state, so the gate's whole window was hostage to one named person.
    ///
    /// **And the facility authored exactly one `CommsConsole`**, so there was nowhere for a second
    /// pawn to stand even if the code had allowed it. There was no hand-off anywhere in the mod.
    ///
    /// ## WHAT CHANGED: A STATION QUESTION INSTEAD OF A PAWN QUESTION
    ///
    /// The gate now asks *is somebody at a bound console*, not *is this one colonist there*. The
    /// named `assignedOperator` keeps every other job it had -- it is who the assignment gizmo
    /// names, who calibration is checked against, and who a player ordered to the post -- because
    /// the owner asked for relief, not for the removal of the role.
    ///
    /// **`Qualified` is the same test the old code applied to the named operator**, minus the
    /// identity clause. One derivation, so a pawn who could hold the window before still can and
    /// nobody new slipped in: *"two derivations of one rule is the defect this project keeps
    /// meeting"*.
    ///
    /// ## THE HAND-OFF HAS TO BE SEAMLESS OR IT HAS NOT SOLVED ANYTHING
    ///
    /// The owner's own condition. If the window drops for a single tick while one pawn stands up
    /// and another sits down, the feature is theatre: the gate would enter emergency in exactly
    /// the moment relief was arriving.
    ///
    /// So absence is **counted, not reacted to**. <see cref="ReliefGraceTicks"/> is the window in
    /// which an empty chair is a hand-off rather than an abandonment, and the counter resets the
    /// instant anybody sits down. **A gate with no relief station behaves as it always did** apart
    /// from that grace, which is the honest cost of the feature and is stated rather than hidden:
    /// a player who truly abandons a console now has a short delay before the emergency fires.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>
        /// How long an empty console is a hand-off rather than an abandonment.
        ///
        /// **1,250 ticks, which is half an in-game hour**, and the number comes from what a
        /// hand-off physically is: one pawn's job ends, a work giver offers the post to another,
        /// and that pawn walks to a console somewhere in the facility. Seconds of real time at
        /// normal speed, and the grace has to cover the slowest plausible walk across a sprawling
        /// installation rather than the fastest.
        ///
        /// **Bounded on purpose, and the bound carries its reason.** An unbounded grace would mean
        /// a gate that holds a connection with nobody at the controls, which is the opposite of
        /// what §1.1 says a window depends on. Half an hour is long enough that relief always
        /// arrives in time and short enough that genuine abandonment is still an emergency.
        /// </summary>
        public const int ReliefGraceTicks = 1250;

        /// <summary>
        /// How long no qualified pawn has been at any bound console.
        ///
        /// Saved, because a hand-off interrupted by a save and reload is still a hand-off. Reset
        /// to zero rather than decremented: there is no partial credit for a chair that was warm.
        /// </summary>
        private int operatorAbsentTicks;

        internal void ExposeOperatorRelief()
        {
            Scribe_Values.Look(ref operatorAbsentTicks, "rr_gateOperatorAbsentTicks", 0);
        }

        /// <summary>
        /// Every console a qualified pawn may hold this gate's window from.
        ///
        /// **The gate's own control console first**, because it is the one the branch designated
        /// and the one the assignment gizmo and the spin-up station already use. Then every thing
        /// linked in the `RR_Link_GateRelief` role, which `maxLinked` caps at three -- so four
        /// stations in total, the owner's number.
        ///
        /// An inactive link is excluded through <see cref="IsEquipmentLinkActive"/>, so an
        /// unpowered or switched-off relief station is not a station. That is the same answer Core
        /// gives for an unpowered multi-analyzer.
        /// </summary>
        public IEnumerable<Thing> BoundConsoles
        {
            get
            {
                Thing primary = Console;
                if (primary != null) { yield return primary; }
                RimroomsGateEquipmentDef relief =
                    DefDatabase<RimroomsGateEquipmentDef>.GetNamedSilentFail("RR_Link_GateRelief");
                // A missing role def means the package is incomplete, and the honest answer is the
                // primary console alone rather than a throw during a tick.
                if (relief == null) { yield break; }
                foreach (Thing linked in LinkedEquipment)
                {
                    if (linked == primary) { continue; }
                    if (RoleOf(linked) != relief) { continue; }
                    if (!IsEquipmentLinkActive(linked)) { continue; }
                    yield return linked;
                }
            }
        }

        /// <summary>How many stations this gate can be held from right now. For the readout.</summary>
        public int BoundConsoleCount
        {
            get
            {
                int count = 0;
                foreach (Thing station in BoundConsoles) { if (station != null) { count++; } }
                return count;
            }
        }

        /// <summary>
        /// Whether this pawn may hold a window at all.
        ///
        /// **Every clause here was already in `IsOperatorOnStation`**, applied to the named
        /// operator. The identity clause is the only one removed, which is the whole feature. A
        /// pawn who could not hold the window before still cannot.
        /// </summary>
        public bool QualifiedToStaff(Pawn pawn)
        {
            return pawn != null && IsEmployedStaff(pawn) && pawn.Spawned && pawn.Map == parent.Map
                && !pawn.Dead && !pawn.Destroyed && !pawn.Downed && !pawn.InMentalState
                && pawn.jobs != null;
        }

        /// <summary>
        /// Whether this pawn is at this station, doing the job that holds a window.
        ///
        /// Asks the **job**, not the position alone: a pawn standing on an interaction cell while
        /// hauling past it is not staffing anything, and that was already the old test's rule.
        /// </summary>
        public bool StaffingStation(Pawn pawn, Thing station)
        {
            if (!QualifiedToStaff(pawn) || station == null || !IsConsolePowered(station)) { return false; }
            if (pawn.Position != station.InteractionCell) { return false; }
            Job job = pawn.CurJob;
            return job != null && job.def != null && job.def.defName == "RR_OperateGate"
                && job.GetTarget(TargetIndex.A).Thing == station;
        }

        /// <summary>
        /// Whether anybody at all is holding this gate's window.
        ///
        /// Scans the stations rather than the map's pawns, because a gate has at most four
        /// stations and a colony has any number of colonists. The reserved occupant of an
        /// interaction cell is found through `Map.thingGrid`, which is the same lookup Core uses
        /// to answer *who is standing here*.
        /// </summary>
        /// **One derivation, asked twice.** This was written as its own scan and that was two
        /// derivations of one rule, which is the defect this project keeps meeting -- a later edit
        /// to one loop and not the other would have let the readout and the emergency test
        /// disagree about whether anybody was at the controls.
        public bool AnyOperatorOnStation { get { return CurrentStationOperator != null; } }

        /// <summary>
        /// Whoever is actually holding the window, or null if the chair is empty.
        ///
        /// **For the readout, so it can name the person rather than the role.** The inspect line
        /// used to report only whether the *named* operator was present, which after relief landed
        /// would have read *away* while somebody else held the connection perfectly.
        /// </summary>
        public Pawn CurrentStationOperator
        {
            get
            {
                if (parent == null || parent.Map == null) { return null; }
                foreach (Thing station in BoundConsoles)
                {
                    if (station == null) { continue; }
                    IntVec3 seat = station.InteractionCell;
                    if (!seat.InBounds(parent.Map)) { continue; }
                    List<Thing> here = parent.Map.thingGrid.ThingsListAtFast(seat);
                    for (int index = 0; index < here.Count; index++)
                    {
                        Pawn pawn = here[index] as Pawn;
                        if (pawn != null && StaffingStation(pawn, station)) { return pawn; }
                    }
                }
                return null;
            }
        }

        /// <summary>
        /// Whether the window should be cut for having nobody at the controls.
        ///
        /// **Counted, never reacted to**, so relief walking across the facility is not an
        /// emergency. Called once per tick from the gate's own tick, before the emergency test
        /// that reads it.
        /// </summary>
        internal bool TickOperatorRelief()
        {
            if (AnyOperatorOnStation)
            {
                operatorAbsentTicks = 0;
                return false;
            }
            if (operatorAbsentTicks < int.MaxValue) { operatorAbsentTicks++; }
            return operatorAbsentTicks > ReliefGraceTicks;
        }

        /// <summary>
        /// Whether this gate wants somebody to take a post right now.
        ///
        /// **Only while a connection is actually being held.** A gate that is closed does not need
        /// anybody sitting at it, and a work giver that thought otherwise would park a colonist at
        /// a console for the rest of the campaign. That is the same discipline `ServiceWanted`
        /// already applies to reconditioning: *"the owner's direction was that pawns must not
        /// always be doing this."*
        /// </summary>
        public bool ReliefWanted
        {
            get
            {
                return IsDesignated && IsOpening && !IsEmergency && !KillSwitchThrown
                    && !AnyOperatorOnStation;
            }
        }
    }
}
