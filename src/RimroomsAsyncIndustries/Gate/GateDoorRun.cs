using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// One gate spanning a run of adjacent ordinary doors, so 1×3 and 2×3 exist without any mod.
    ///
    /// **Owner direction, verbatim:** *"i suppose the fallback is okay of building mulitple doors
    /// 1x1 to make the sizes needed to fit vehicals and the like"*, and the answer on record for
    /// the fork was **BOTH paths** — Doors Expanded's real 1×3 and 2×3 doors when somebody runs
    /// it, and a bound run of Core 1×1 doors when they do not.
    ///
    /// The single-door half shipped at 0.9.2-dev: Core's own `OrnateDoor` is 2×1, so 1×2 was
    /// already free. **1×3 and 2×3 are what this adds.**
    ///
    /// ## The run is ONE gate, not several
    ///
    /// Invariant 32: there is exactly one way a laboratory gate opens, through the spin-up, and
    /// every entry point routes into it. So exactly one door in the run is the gate and the rest
    /// are **extensions** of it: an extension reports `IsDesignated` false, has no address, no
    /// spin-up, no console and no window of its own. It is a hole in the same wall.
    ///
    /// Invariant 47: **a connection has one width, in both directions.** Per-endpoint measuring
    /// traps an animal in the Backrooms, so width is measured once, off the whole run's rectangle,
    /// and both sides read the same number.
    ///
    /// Invariant 41: **throughput is never capped.** A bound run gets more opening cells and no
    /// quota, exactly as a real wide door does. There is no counter here either.
    ///
    /// ## A run is a rectangle with no holes in it
    ///
    /// Everything downstream already works off a `CellRect` — `GateEntryCells` walks the rect and
    /// steps one cell outward, `GateWidth` counts what it finds, `GateCellCount` is the area. A
    /// straight line of N adjacent 1×1 doors **is** a 1×N rect, and two such lines side by side
    /// are a 2×N one, so the union flows through all of it unchanged.
    ///
    /// The one thing that has to be checked is that the rectangle is **solid**: every cell in it
    /// holds a door belonging to the run. A ring of five doors around a gap has a legal-looking
    /// bounding box and is not a opening.
    ///
    /// And the resulting footprint is validated against the **same four shapes** a single door is,
    /// so a run cannot reach a size a real door could not.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        /// <summary>Doors bound into this gate. Empty for every single-door gate, which is most.</summary>
        private List<Thing> nativeRunExtensions = new List<Thing>();

        /// <summary>The gate this door is part of, when it is an extension rather than a gate.</summary>
        private Thing nativeRunHost;

        /// <summary>
        /// This door is part of somebody else's gate.
        ///
        /// Read by `IsDesignated`, which is what keeps invariant 32 true: an extension can never
        /// be operated, dialled, bound to a console or given an address, because as far as every
        /// other system is concerned it is not a gate at all.
        /// </summary>
        public bool IsRunExtension
        {
            get
            {
                return nativeRunHost != null && !nativeRunHost.Destroyed && nativeRunHost.Spawned &&
                    nativeRunHost != parent;
            }
        }

        public IReadOnlyList<Thing> RunExtensions { get { return LiveExtensions(); } }

        /// <summary>How many doors make up this gate, including the one that is the gate.</summary>
        public int RunDoorCount { get { return LiveExtensions().Count + 1; } }

        /// <summary>
        /// The rectangle this gate actually occupies: its own door plus every live extension.
        ///
        /// Falls back to the parent's own rect whenever the run is empty or does not form a solid
        /// rectangle, so a run that loses a door to a raid degrades to the doors that remain
        /// rather than reporting a hole as a opening.
        /// </summary>
        internal CellRect RunRect
        {
            get
            {
                CellRect own = parent == null || !parent.Spawned ? CellRect.Empty : parent.OccupiedRect();
                List<Thing> extensions = LiveExtensions();
                if (extensions.Count == 0 || own.Area <= 0) { return own; }

                int minX = own.minX, maxX = own.maxX, minZ = own.minZ, maxZ = own.maxZ;
                for (int index = 0; index < extensions.Count; index++)
                {
                    CellRect rect = extensions[index].OccupiedRect();
                    if (rect.minX < minX) { minX = rect.minX; }
                    if (rect.maxX > maxX) { maxX = rect.maxX; }
                    if (rect.minZ < minZ) { minZ = rect.minZ; }
                    if (rect.maxZ > maxZ) { maxZ = rect.maxZ; }
                }
                CellRect union = CellRect.FromLimits(minX, minZ, maxX, maxZ);

                // Solid or nothing. A bounding box is not a opening.
                if (union.Area != extensions.Count + own.Area) { return own; }
                if (!LegalGateFootprint(new IntVec2(union.Width, union.Height))) { return own; }
                return union;
            }
        }

        private List<Thing> LiveExtensions()
        {
            var live = new List<Thing>();
            if (nativeRunExtensions == null) { return live; }
            for (int index = 0; index < nativeRunExtensions.Count; index++)
            {
                Thing door = nativeRunExtensions[index];
                if (door == null || door.Destroyed || !door.Spawned) { continue; }
                if (parent == null || door.Map != parent.Map) { continue; }
                if (door == parent) { continue; }
                live.Add(door);
            }
            return live;
        }

        /// <summary>
        /// Bind one adjacent ordinary door into this gate.
        ///
        /// Every clause refuses, per invariant 136, and the owner's rule on rebinding applies
        /// unchanged: *"gate doors expansions can NOT be done on a working gate"*, where a ramp
        /// counts as working.
        /// </summary>
        public CompanyActionResult ExtendGateAcrossRun(Thing door)
        {
            if (!IsDesignated) { return CompanyActionResult.Refused("RR_GateRun_NotAGate"); }
            if (IsRunExtension) { return CompanyActionResult.Refused("RR_GateRun_AlreadyAnExtension"); }
            if (IsOpening || IsSpinningUp) { return CompanyActionResult.Refused("RR_GateRun_ActiveCannotExtend"); }
            if (parent == null || !parent.Spawned || parent.Map == null)
            { return CompanyActionResult.Refused("RR_GateRun_NotAGate"); }

            if (door == null || door.Destroyed || !door.Spawned || door.Map != parent.Map ||
                !(door is Building_Door) || door.Faction != Faction.OfPlayer)
            { return CompanyActionResult.Refused("RR_GateRun_NotADoor"); }
            if (door == parent) { return CompanyActionResult.Refused("RR_GateRun_SameDoor"); }
            if (door.def == null || door.def.size.x != 1 || door.def.size.z != 1)
            { return CompanyActionResult.Refused("RR_GateRun_NotSingleCell"); }

            CompRimroomsGate other = door.TryGetComp<CompRimroomsGate>();
            // A door that is itself a gate, or already part of another one, is not available.
            // Invariant 32 again: one gate, one spin-up, one address.
            if (other == null) { return CompanyActionResult.Refused("RR_GateRun_NotADoor"); }
            if (other.IsDesignated) { return CompanyActionResult.Refused("RR_GateRun_AlreadyAGate"); }
            if (other.IsRunExtension)
            { return CompanyActionResult.Refused("RR_GateRun_AlreadyAnExtension"); }

            nativeRunExtensions = nativeRunExtensions ?? new List<Thing>();
            if (nativeRunExtensions.Contains(door)) { return CompanyActionResult.Existing(); }

            // Try it, then keep it only if the result is a real opening. Checking the shape after
            // the fact is the only honest way to ask "would this still be a legal gate", because
            // legality is a property of the whole run rather than of the door being added.
            nativeRunExtensions.Add(door);
            CellRect proposed = RunRect;
            bool solid = proposed.Area == RunDoorCount &&
                LegalGateFootprint(new IntVec2(proposed.Width, proposed.Height));
            if (!solid)
            {
                nativeRunExtensions.Remove(door);
                return CompanyActionResult.Refused("RR_GateRun_NotASolidRun");
            }

            other.nativeRunHost = parent;
            NativeCampaign?.RecordEvent("RR_Event_GateRunExtended", parent.LabelShortCap,
                RunDoorCount.ToString(), GateWidth.ToString());
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Return every extension to being an ordinary door.
        ///
        /// Refused while the gate is working, for the same reason extending it is.
        /// </summary>
        public CompanyActionResult ReleaseGateRun()
        {
            if (IsOpening || IsSpinningUp)
            { return CompanyActionResult.Refused("RR_GateRun_ActiveCannotExtend"); }
            if (nativeRunExtensions == null || nativeRunExtensions.Count == 0)
            { return CompanyActionResult.Existing(); }
            for (int index = 0; index < nativeRunExtensions.Count; index++)
            {
                Thing door = nativeRunExtensions[index];
                CompRimroomsGate other = door == null ? null : door.TryGetComp<CompRimroomsGate>();
                if (other != null && other.nativeRunHost == parent) { other.nativeRunHost = null; }
            }
            nativeRunExtensions.Clear();
            return CompanyActionResult.Applied();
        }

        // Literal keys, never assembled. `check-keyed-strings.py` refused the concatenated
        // version and was right to: a key built at run time cannot be checked in either
        // direction, so a typo in one would ship as a raw key on screen. This is the FIFTH time
        // this project has caught that pattern, which is why the checker exists.

        /// <summary>
        /// Every ordinary door touching this run that could legally join it.
        ///
        /// Cardinal neighbours of every cell the run already holds, which is how a run grows
        /// along a wall. Tested by actually proposing each one, so a candidate is only listed if
        /// binding it would really produce a solid legal opening -- a diagonal neighbour or a
        /// door that would make an L never appears, rather than appearing and then refusing.
        ///
        /// Sorted ordinally by position before being returned. Invariant 26: a menu whose rows
        /// move between frames is a menu somebody misclicks.
        /// </summary>
        internal List<Thing> AdjacentRunCandidates()
        {
            var found = new List<Thing>();
            if (!IsDesignated || IsRunExtension || parent == null || !parent.Spawned) { return found; }
            Map map = parent.Map;
            if (map == null) { return found; }

            CellRect rect = RunRect;
            var seen = new HashSet<Thing>();
            foreach (IntVec3 cell in rect)
            {
                for (int side = 0; side < 4; side++)
                {
                    IntVec3 candidate = cell + GenAdj.CardinalDirections[side];
                    if (!candidate.InBounds(map) || rect.Contains(candidate)) { continue; }
                    Building edifice = candidate.GetEdifice(map);
                    if (edifice == null || !seen.Add(edifice)) { continue; }
                    if (!WouldJoinRun(edifice)) { continue; }
                    found.Add(edifice);
                }
            }
            found.Sort(delegate(Thing left, Thing right)
            {
                int byX = left.Position.x.CompareTo(right.Position.x);
                return byX != 0 ? byX : left.Position.z.CompareTo(right.Position.z);
            });
            return found;
        }

        /// <summary>
        /// Whether binding this door would really work, asked by trying it and putting it back.
        ///
        /// Cheaper than reimplementing the solidity and legality rules a second time, and
        /// impossible to get out of step with them -- which a second implementation would.
        /// </summary>
        private bool WouldJoinRun(Thing door)
        {
            if (door == null || !(door is Building_Door) || door == parent) { return false; }
            if (door.Destroyed || !door.Spawned || door.Faction != Faction.OfPlayer) { return false; }
            if (door.def == null || door.def.size.x != 1 || door.def.size.z != 1) { return false; }
            CompRimroomsGate other = door.TryGetComp<CompRimroomsGate>();
            if (other == null || other.IsDesignated || other.IsRunExtension) { return false; }

            nativeRunExtensions = nativeRunExtensions ?? new List<Thing>();
            if (nativeRunExtensions.Contains(door)) { return false; }
            nativeRunExtensions.Add(door);
            CellRect proposed = RunRect;
            bool legal = proposed.Area == RunDoorCount &&
                LegalGateFootprint(new IntVec2(proposed.Width, proposed.Height));
            nativeRunExtensions.Remove(door);
            return legal;
        }

        private void OpenGateRunMenu()
        {
            var options = new List<FloatMenuOption>();
            List<Thing> candidates = AdjacentRunCandidates();
            for (int index = 0; index < candidates.Count; index++)
            {
                Thing door = candidates[index];
                options.Add(new FloatMenuOption(
                    "RR_GateRun_Extend".Translate(door.LabelShortCap),
                    delegate { ShowOrderResult(ExtendGateAcrossRun(door)); }));
            }
            if (RunDoorCount > 1)
            {
                options.Add(new FloatMenuOption("RR_GateRun_Release".Translate(),
                    delegate { ShowOrderResult(ReleaseGateRun()); }));
            }
            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_GateRun_NoCandidate".Translate(), null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        internal void ExposeGateRun()
        {
            Scribe_Collections.Look(ref nativeRunExtensions, "rr_gateRunExtensions", LookMode.Reference);
            Scribe_References.Look(ref nativeRunHost, "rr_gateRunHost");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && nativeRunExtensions == null)
            { nativeRunExtensions = new List<Thing>(); }
        }
    }
}
