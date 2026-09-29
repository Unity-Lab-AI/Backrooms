using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// A role a gate's facility can have equipment linked into.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"these facilities when built will be big so
    /// some shelves and multiples need to be like connect via a option like beds connect to
    /// other furnature in making the gate work properly with everything needed and like things
    /// needed to be on shelves/records that computers and workbenches need to connect to ie we
    /// can use things like the research computer multianalysers and other such things and tool
    /// cabnets for enginners research benches and the like and these facilitys can be massive so
    /// thes connections need to be like on the same power systems and connected to gether via
    /// connections like furnature to beds and reach fare and through walls and manually connected
    /// for use of multi gate facilities"*
    ///
    /// The fillable equipment is **named by capability and enumerated from the installed game**,
    /// never remembered. That mattered here: the owner said *"multianalysers"*, and
    /// `Multianalyzer` is a **ResearchProjectDef**. The building is `MultiAnalyzer`, with a
    /// capital A, in `Buildings_Misc.xml`. Guessing the casing would have produced a role that
    /// silently accepted nothing.
    /// </summary>
    public sealed class RimroomsGateEquipmentDef : Def
    {
        /// <summary>Exact def names that can fill this role. Read from the installed game.</summary>
        public List<string> thingDefNames = new List<string>();

        /// <summary>
        /// How many of this role one gate may hold. *"some shelves and multiples"* — the point
        /// of the direction is that a big facility has several of a thing, so this is not 1.
        /// </summary>
        public int maxLinked = 4;

        /// <summary>Order in the picker and the readout. Sorted ordinally after this.</summary>
        public int displayOrder;

        public bool Accepts(Thing thing)
        {
            return thing != null && thing.def != null && thingDefNames != null &&
                thingDefNames.Contains(thing.def.defName);
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrEmpty(label)) { yield return "An equipment role must have a label; a player picks it by name."; }
            if (string.IsNullOrEmpty(description)) { yield return "An equipment role must have a description; it is shown in the card."; }
            if (thingDefNames == null || thingDefNames.Count == 0)
            { yield return "An equipment role that accepts nothing is a role nobody can fill."; }
            if (maxLinked < 1) { yield return "maxLinked below one makes the role unusable."; }
        }

        public static List<RimroomsGateEquipmentDef> AllInOrder()
        {
            return DefDatabase<RimroomsGateEquipmentDef>.AllDefsListForReading
                .OrderBy(definition => definition.displayOrder)
                .ThenBy(definition => definition.defName, System.StringComparer.Ordinal)
                .ToList();
        }

        /// <summary>The role a thing can fill, or null. First match in display order.</summary>
        public static RimroomsGateEquipmentDef RoleFor(Thing thing)
        {
            foreach (RimroomsGateEquipmentDef role in AllInOrder())
            {
                if (role.Accepts(thing)) { return role; }
            }
            return null;
        }
    }

    /// <summary>
    /// Equipment linked into a gate's facility — the shelves, analysers, benches and cabinets a
    /// big installation is made of.
    ///
    /// **Why this is ours and not Core's facility comps.** RimWorld already has exactly the
    /// relationship the owner described: a bed links to an end table, a research bench links to a
    /// multi-analyzer, a workbench links to a tool cabinet. But **all of the geometry lives on
    /// the facility side**, in <c>CompProperties_Facility</c>, and its defaults are
    /// <c>maxDistance = 8f</c> and <c>requiresLOS = true</c> — read from decompiled Core, not
    /// assumed. The direction is *"reach fare and through walls"*, which is the opposite of
    /// both.
    ///
    /// Changing those on Core's `MultiAnalyzer` or `ToolCabinet` would change **vanilla
    /// research-bench linking for every player and every other mod**, and the profile contains
    /// three wall-mounted facility mods (register rows 254, 256, 257) plus a room-size mod
    /// (row 184). So the reach and the wall-transparency are ours, on our own record, and
    /// **Core's facility comps are left exactly as they are**.
    ///
    /// That also means the two relationships coexist rather than compete: linking a
    /// `MultiAnalyzer` to a gate does **not** consume its Core facility slot and does not stop
    /// it boosting a research bench. Do not "fix" that.
    ///
    /// **Every rule here already existed for the gate's original three providers** — console,
    /// battery, assembly bench. This generalises that shape rather than inventing one:
    ///
    /// | Direction | How |
    /// |---|---|
    /// | *"manually connected"* | Explicit designation only. Proximity never links anything. |
    /// | *"reach fare and through walls"* | No distance check and no line-of-sight check, deliberately. Same map and same branch is the whole spatial rule. |
    /// | *"on the same power systems"* | Any linked thing that **has** a power component must sit on the gate's own power net. |
    /// | *"multiples"* | `maxLinked` per role, defaulting to four rather than one. |
    /// | *"for use of multi gate facilities"* | A thing linked to one gate is refused to every other gate, the same way `ProviderAlreadyBound` already works for the original three. |
    /// | *"like beds connect to other furnature"* | Core's own link lines, drawn with Core's own active and inactive materials. |
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        private List<Thing> gateEquipment = new List<Thing>();

        public IEnumerable<Thing> LinkedEquipment
        {
            get
            {
                if (gateEquipment == null) { yield break; }
                for (int i = 0; i < gateEquipment.Count; i++)
                {
                    Thing thing = gateEquipment[i];
                    if (thing != null && !thing.Destroyed) { yield return thing; }
                }
            }
        }

        public int LinkedCount(RimroomsGateEquipmentDef role)
        {
            if (role == null) { return 0; }
            int count = 0;
            foreach (Thing thing in LinkedEquipment)
            {
                if (role.Accepts(thing)) { count++; }
            }
            return count;
        }

        /// <summary>
        /// Whether a link is doing anything right now.
        ///
        /// A link stays recorded while it is inactive rather than being dropped, because a
        /// player who loses power for an hour has not un-designated their facility. Inactive
        /// links are drawn in Core's own inactive colour, which is the same thing vanilla does
        /// when a multi-analyzer is unpowered.
        /// </summary>
        public bool IsEquipmentLinkActive(Thing thing)
        {
            if (thing == null || thing.Destroyed || !thing.Spawned) { return false; }
            if (!SameNativeHeadquartersThing(thing)) { return false; }
            if (!EquipmentPowerSatisfied(thing)) { return false; }
            CompFlickable flickable = thing.TryGetComp<CompFlickable>();
            return (flickable == null || flickable.SwitchIsOn) && !thing.IsBrokenDown();
        }

        /// <summary>
        /// *"thes connections need to be like on the same power systems"*.
        ///
        /// Applied to anything that **has** a power component, and to nothing else. A `Shelf`
        /// has no power component and therefore no network to be on, so requiring one of a
        /// shelf would make the archive role permanently unfillable. The rule is about powered
        /// equipment being on the gate's system, which is what makes a sprawling installation
        /// one facility rather than several unrelated rooms.
        /// </summary>
        private bool EquipmentPowerSatisfied(Thing thing)
        {
            CompPower power = thing.TryGetComp<CompPower>();
            if (power == null) { return true; }
            CompPowerBattery battery = NativeBatteryComp;
            return battery != null && battery.PowerNet != null && power.PowerNet == battery.PowerNet;
        }

        /// <summary>
        /// Why a thing may not be linked, or null if it may be. Split from the mutation for the
        /// same reason every other check in this mod is: a candidate test and a definitive
        /// action are two different questions and merging them hides which one failed.
        /// </summary>
        public string EquipmentLinkFailureKey(Thing thing)
        {
            if (!IsDesignated) { return "RR_GateLink_GateNotDesignated"; }
            if (IsOpening || IsSpinningUp) { return "RR_GateLink_GateBusy"; }
            if (thing == null || thing.Destroyed) { return "RR_GateLink_Unavailable"; }
            RimroomsGateEquipmentDef role = RimroomsGateEquipmentDef.RoleFor(thing);
            if (role == null) { return "RR_GateLink_WrongKind"; }
            if (!SameNativeHeadquartersThing(thing)) { return "RR_GateLink_Unavailable"; }

            // The gate's own three providers are bound by their own rules and are not equipment.
            if (thing == nativeConsole || thing == nativeBattery || thing == nativeAssemblyBench)
            { return "RR_GateLink_AlreadyAProvider"; }

            if (gateEquipment != null && gateEquipment.Contains(thing)) { return "RR_GateLink_AlreadyLinked"; }
            if (LinkedCount(role) >= role.maxLinked) { return "RR_GateLink_RoleFull"; }

            // *"for use of multi gate facilities"*. Two gates in one building are expected; two
            // gates quietly sharing one shelf are not, because then neither readout is true.
            foreach (Building building in thing.Map.listerBuildings.allBuildingsColonist)
            {
                CompRimroomsGate other = building.TryGetComp<CompRimroomsGate>();
                if (other == null || other == this || !other.IsDesignated) { continue; }
                if (other.gateEquipment != null && other.gateEquipment.Contains(thing))
                { return "RR_GateLink_BoundToAnotherGate"; }
            }
            return null;
        }

        public Company.CompanyActionResult LinkEquipment(Thing thing)
        {
            string failure = EquipmentLinkFailureKey(thing);
            if (failure != null) { return Company.CompanyActionResult.Refused(failure); }
            if (gateEquipment == null) { gateEquipment = new List<Thing>(); }
            gateEquipment.Add(thing);
            return Company.CompanyActionResult.Applied();
        }

        public Company.CompanyActionResult UnlinkEquipment(Thing thing)
        {
            if (gateEquipment == null || thing == null || !gateEquipment.Contains(thing))
            { return Company.CompanyActionResult.Existing(); }
            // Unlinking is always allowed, including mid-opening. A link grants no charge and no
            // work, so removing one can never strand anybody -- which is exactly why binding a
            // provider is refused mid-opening and this is not.
            gateEquipment.Remove(thing);
            return Company.CompanyActionResult.Applied();
        }

        /// <summary>Core's own link lines, so the affordance is one a player already knows.</summary>
        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            if (!IsDesignated || !parent.Spawned) { return; }
            foreach (Thing thing in LinkedEquipment)
            {
                if (!thing.Spawned || thing.Map != parent.Map) { continue; }
                if (IsEquipmentLinkActive(thing))
                {
                    GenDraw.DrawLineBetween(parent.TrueCenter(), thing.TrueCenter());
                }
                else
                {
                    GenDraw.DrawLineBetween(parent.TrueCenter(), thing.TrueCenter(),
                        CompAffectedByFacilities.InactiveFacilityLineMat);
                }
            }
        }

        internal string EquipmentLinkReadout()
        {
            if (!IsDesignated) { return null; }
            List<string> parts = new List<string>();
            foreach (RimroomsGateEquipmentDef role in RimroomsGateEquipmentDef.AllInOrder())
            {
                int linked = LinkedCount(role);
                if (linked == 0) { continue; }
                int active = LinkedEquipment.Count(t => role.Accepts(t) && IsEquipmentLinkActive(t));
                parts.Add("RR_GateLink_RoleReadout".Translate(role.LabelCap, active.ToString(),
                    linked.ToString(), role.maxLinked.ToString()).ToString());
            }
            return parts.Count == 0 ? null : string.Join("\n", parts.ToArray());
        }

        internal Gizmo EquipmentLinkGizmo()
        {
            return new Command_Action
            {
                defaultLabel = "RR_GateLink_Label".Translate(LinkedEquipment.Count().ToString()),
                defaultDesc = "RR_GateLink_Desc".Translate(),
                icon = parent.def.uiIcon,
                action = OpenEquipmentLinkMenu,
            };
        }

        private void OpenEquipmentLinkMenu()
        {
            List<FloatMenuOption> options = new List<FloatMenuOption>();

            foreach (Thing linked in LinkedEquipment.OrderBy(t => t.def.defName, System.StringComparer.Ordinal).ToList())
            {
                Thing target = linked;
                options.Add(new FloatMenuOption("RR_GateLink_Unlink".Translate(target.LabelCap),
                    delegate { ShowOrderResult(UnlinkEquipment(target)); }));
            }

            // Candidates are enumerated from the map rather than remembered, and sorted
            // ordinally before being shown: a list a player picks from must not depend on
            // whatever order the map's building lister happens to be in.
            if (parent.Map != null)
            {
                List<Thing> candidates = new List<Thing>();
                foreach (Building building in parent.Map.listerBuildings.allBuildingsColonist)
                {
                    if (EquipmentLinkFailureKey(building) == null) { candidates.Add(building); }
                }
                foreach (Thing candidate in candidates
                    .OrderBy(t => t.def.defName, System.StringComparer.Ordinal)
                    .ThenBy(t => t.thingIDNumber)
                    .ToList())
                {
                    Thing target = candidate;
                    options.Add(new FloatMenuOption("RR_GateLink_Add".Translate(target.LabelCap),
                        delegate { ShowOrderResult(LinkEquipment(target)); }));
                }
            }

            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_GateLink_NoCandidates".Translate(), null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        internal void ExposeEquipmentLinks()
        {
            Scribe_Collections.Look(ref gateEquipment, "rr_gateEquipment", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (gateEquipment == null) { gateEquipment = new List<Thing>(); }
                // A thing that was deconstructed while the save was closed is not a link any
                // more. Dropping it here rather than tolerating nulls everywhere downstream.
                gateEquipment.RemoveAll(thing => thing == null || thing.Destroyed);
            }
        }
    }
}
