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

        /// <summary>
        /// A `ThingCategoryDef` this role is supposed to have stock of, or empty for a role that
        /// holds no stock.
        ///
        /// **Owner direction, verbatim:** *"Connect each room to concrete capabilities, stock
        /// needs, staff jobs, risks, and UI alerts; expose why a room is not functional"*. A role
        /// that only *accepts* equipment is a label; a role that knows what should be kept on it
        /// is a function. An armory with no weapons in it is not an armory, and before this there
        /// was nothing anywhere that could say so.
        ///
        /// A **category** rather than a list of defNames, so Core, every DLC and all 294 profile
        /// mods answer it. `ThingCategoryDef.DescendantThingDefs` is Core's own answer to *what
        /// counts as a weapon*.
        /// </summary>
        public string stockCategoryDefName;

        /// <summary>
        /// How much of <see cref="stockCategoryDefName"/> this role wants held on its linked
        /// things. Zero means the role reports its stock without ever calling it short.
        /// </summary>
        public int stockTarget;

        /// <summary>
        /// Keyed string naming **what actually goes wrong** when the stock is not there.
        ///
        /// The *"risks"* half of the same direction, and deliberately a stated consequence rather
        /// than a number. *"Risk: 3"* tells a player nothing; *"a crew that meets something
        /// hostile down there has nothing to meet it with"* tells them why the empty shelf
        /// matters. Same reasoning as the inhabitant tells: a fact beats an adjective.
        /// </summary>
        public string riskKey;

        public bool Accepts(Thing thing)
        {
            return thing != null && thing.def != null && thingDefNames != null &&
                thingDefNames.Contains(thing.def.defName);
        }

        /// <summary>
        /// Whether anything in the loaded game can actually fill this role.
        ///
        /// **This is the stand-alone guarantee applied to a role.** `thingDefNames` is a list of
        /// exact names and `ConfigErrors` can only see that the list is non-empty — a role naming
        /// only DLC or mod buildings would pass load and then silently accept nothing, which is
        /// the exact failure mode the file header already records for `MultiAnalyzer`'s casing.
        ///
        /// So a role whose every name is absent is **hidden from the picker and the readout**
        /// rather than offered and unfillable. Asked at the call site rather than cached, because
        /// the answer is a property of the loaded game and this is not hot.
        /// </summary>
        public bool Fillable
        {
            get
            {
                if (thingDefNames == null) { return false; }
                for (int index = 0; index < thingDefNames.Count; index++)
                {
                    if (DefDatabase<ThingDef>.GetNamedSilentFail(thingDefNames[index]) != null)
                    { return true; }
                }
                return false;
            }
        }

        /// <summary>The category this role stocks, or null.</summary>
        public ThingCategoryDef StockCategory
        {
            get
            {
                return string.IsNullOrEmpty(stockCategoryDefName)
                    ? null
                    : DefDatabase<ThingCategoryDef>.GetNamedSilentFail(stockCategoryDefName);
            }
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrEmpty(label)) { yield return "An equipment role must have a label; a player picks it by name."; }
            if (string.IsNullOrEmpty(description)) { yield return "An equipment role must have a description; it is shown in the card."; }
            if (thingDefNames == null || thingDefNames.Count == 0)
            { yield return "An equipment role that accepts nothing is a role nobody can fill."; }
            if (maxLinked < 1) { yield return "maxLinked below one makes the role unusable."; }
            // A stock target with nothing to count is a role that can never be satisfied, and a
            // category with no target is a number nobody reads. Both are refused rather than
            // silently ignored, because either one produces a room function that looks
            // implemented and does nothing.
            if (stockTarget > 0 && string.IsNullOrEmpty(stockCategoryDefName))
            { yield return "A role with a stock target must name the category it stocks."; }
            if (!string.IsNullOrEmpty(stockCategoryDefName) && stockTarget <= 0)
            { yield return "A role naming a stock category must state how much it wants."; }
            if (!string.IsNullOrEmpty(riskKey) && stockTarget <= 0)
            { yield return "A role naming a risk must have a stock target, or the risk never shows."; }
        }

        /// <summary>
        /// Every role, in display order — **and only roles the loaded game can actually fill.**
        ///
        /// The filter is the stand-alone guarantee applied here: a role whose buildings all come
        /// from a DLC or a mod the player does not have would otherwise appear in the picker,
        /// accept nothing, and read as broken. See <see cref="RimroomsGateEquipmentDef.Fillable"/>.
        /// Every caller — picker, readout and `RoleFor` — goes through this, so there is one
        /// answer to *which roles exist here*.
        /// </summary>
        public static List<RimroomsGateEquipmentDef> AllInOrder()
        {
            return DefDatabase<RimroomsGateEquipmentDef>.AllDefsListForReading
                .Where(definition => definition.Fillable)
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

        /// <summary>
        /// Which role each linked thing fills, index-matched to <see cref="gateEquipment"/>.
        ///
        /// ## Why the role is stored instead of derived, which it used to be
        ///
        /// **`proof-gate-links.py` caught this and it was a real functional bug, not a style
        /// complaint.** The role used to be worked out from the def alone, through
        /// <see cref="RimroomsGateEquipmentDef.RoleFor"/>, which returns the **first** role in
        /// display order that accepts a thing. That was correct while every def belonged to
        /// exactly one role — and it stopped being correct the moment the armory and the
        /// receiving bay arrived, because **Core ships no weapon rack and no receiving bay**, so
        /// all three of those roles are filled by `Shelf` and `ShelfSmall`.
        ///
        /// Derived, a shelf could therefore *only ever* be the records archive: the armory and
        /// the receiving bay would have been two roles nobody could fill, offered in the picker,
        /// accepting a shelf and then reporting it as an archive. And `LinkedCount` would have
        /// counted one shelf toward all three at once, so every one of the three readouts would
        /// have been wrong in a different direction.
        ///
        /// **So the player says which.** That is also what the direction this whole feature came
        /// from asked for — *"manually connected"* — and it is what a big facility actually
        /// needs: a dozen shelves, some of them the archive and some of them the armory, decided
        /// by the branch rather than by display order.
        ///
        /// Stored as defNames rather than resolved defs, for the same reason every other saved
        /// reference in this mod is: a role removed from the package must leave the link standing
        /// and roleless rather than throw on load.
        /// </summary>
        private List<string> gateEquipmentRoles = new List<string>();

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

        /// <summary>
        /// The role this gate's player assigned to a linked thing, or null if it is not linked.
        ///
        /// **Asked of the record, never of the def.** See <see cref="gateEquipmentRoles"/> for
        /// what asking the def cost.
        /// </summary>
        public RimroomsGateEquipmentDef RoleOf(Thing thing)
        {
            if (thing == null || gateEquipment == null || gateEquipmentRoles == null) { return null; }
            int index = gateEquipment.IndexOf(thing);
            if (index < 0 || index >= gateEquipmentRoles.Count) { return null; }
            string defName = gateEquipmentRoles[index];
            return string.IsNullOrEmpty(defName)
                ? null
                : DefDatabase<RimroomsGateEquipmentDef>.GetNamedSilentFail(defName);
        }

        public int LinkedCount(RimroomsGateEquipmentDef role)
        {
            if (role == null) { return 0; }
            int count = 0;
            foreach (Thing thing in LinkedEquipment)
            {
                if (RoleOf(thing) == role) { count++; }
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
        public string EquipmentLinkFailureKey(Thing thing, RimroomsGateEquipmentDef role)
        {
            if (!IsDesignated) { return "RR_GateLink_GateNotDesignated"; }
            if (IsOpening || IsSpinningUp) { return "RR_GateLink_GateBusy"; }
            if (thing == null || thing.Destroyed) { return "RR_GateLink_Unavailable"; }
            // **The chosen role has to accept the thing, and that is checked rather than
            // assumed.** The caller is a float menu built from the same question, but a UI
            // having offered something is never evidence here -- the same rule
            // `UnlockSupplyTier` states for its three locks.
            if (role == null || !role.Fillable || !role.Accepts(thing))
            { return "RR_GateLink_WrongKind"; }
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

        /// <summary>
        /// Links a thing into a role the player chose.
        ///
        /// The role is a parameter rather than something worked out here, because a shelf can be
        /// an archive, an armory or a receiving bay and only the player knows which this one is.
        /// </summary>
        public Company.CompanyActionResult LinkEquipment(Thing thing,
            RimroomsGateEquipmentDef role)
        {
            string failure = EquipmentLinkFailureKey(thing, role);
            if (failure != null) { return Company.CompanyActionResult.Refused(failure); }
            if (gateEquipment == null) { gateEquipment = new List<Thing>(); }
            if (gateEquipmentRoles == null) { gateEquipmentRoles = new List<string>(); }
            // Kept index-matched by construction: both lists are only ever appended to here and
            // only ever removed from at the same index below.
            AlignRoles();
            gateEquipment.Add(thing);
            gateEquipmentRoles.Add(role.defName);
            return Company.CompanyActionResult.Applied();
        }

        public Company.CompanyActionResult UnlinkEquipment(Thing thing)
        {
            if (gateEquipment == null || thing == null || !gateEquipment.Contains(thing))
            { return Company.CompanyActionResult.Existing(); }
            // Unlinking is always allowed, including mid-opening. A link grants no charge and no
            // work, so removing one can never strand anybody -- which is exactly why binding a
            // provider is refused mid-opening and this is not.
            AlignRoles();
            int index = gateEquipment.IndexOf(thing);
            gateEquipment.RemoveAt(index);
            if (index < gateEquipmentRoles.Count) { gateEquipmentRoles.RemoveAt(index); }
            return Company.CompanyActionResult.Applied();
        }

        /// <summary>
        /// Makes the role list exactly as long as the equipment list.
        ///
        /// **This is the save migration, and it reproduces the old behaviour exactly.** A game
        /// saved before the role was recorded has `gateEquipment` and no roles at all; every one
        /// of those links gets the role `RoleFor` would have derived for it, which is the first
        /// in display order that accepts the def — the same answer that save was already
        /// showing. So nothing a player had linked changes, and from then on the record is
        /// explicit.
        ///
        /// Called before every mutation as well as on load, because a list that can only be
        /// corrected at load time is a list that stays wrong for the rest of a session if
        /// anything ever puts it out of step.
        /// </summary>
        private void AlignRoles()
        {
            if (gateEquipment == null) { gateEquipment = new List<Thing>(); }
            if (gateEquipmentRoles == null) { gateEquipmentRoles = new List<string>(); }
            while (gateEquipmentRoles.Count > gateEquipment.Count)
            { gateEquipmentRoles.RemoveAt(gateEquipmentRoles.Count - 1); }
            while (gateEquipmentRoles.Count < gateEquipment.Count)
            {
                Thing thing = gateEquipment[gateEquipmentRoles.Count];
                RimroomsGateEquipmentDef derived = RimroomsGateEquipmentDef.RoleFor(thing);
                gateEquipmentRoles.Add(derived == null ? "" : derived.defName);
            }
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
                // **`RoleOf`, not `Accepts` -- and this line was missed on the first pass.** The
                // proof's claim caught it. With three roles filled by the same shelf def,
                // `Accepts` would have counted every linked shelf as active in the archive, the
                // armory and the receiving bay at once, so the working count could exceed the
                // linked count on the line right beside it.
                int active = LinkedEquipment.Count(t => RoleOf(t) == role && IsEquipmentLinkActive(t));
                parts.Add("RR_GateLink_RoleReadout".Translate(role.LabelCap, active.ToString(),
                    linked.ToString(), role.maxLinked.ToString()).ToString());
                // **WHY THE ROOM IS NOT FUNCTIONAL, on the gate.** Owner: *"Connect each room to
                // concrete capabilities, stock needs, staff jobs, risks, and UI alerts; expose
                // why a room is not functional"*. A linked armory with nothing in it reported
                // exactly the same as a full one before this.
                string shortfall = StockShortfallReadout(role);
                if (shortfall != null) { parts.Add(shortfall); }
            }
            return parts.Count == 0 ? null : string.Join("\n", parts.ToArray());
        }

        /// <summary>
        /// What this role is holding against what it is supposed to hold, or null when the role
        /// stocks nothing or is stocked.
        ///
        /// ## Counted on the linked things, not on the map
        ///
        /// The whole point of a role is that it names *where* something is kept. A branch with
        /// five rifles in a bedroom does not have an armory, and counting map-wide would have
        /// reported one — which is the same laundering the clue system already refuses.
        ///
        /// Storage is asked through <c>thing.GetSlotGroup</c> rather than by walking cells,
        /// because Core's own slot group is what makes a shelf a container and it answers for
        /// mod storage buildings too. A linked thing with no slot group contributes nothing and
        /// is not an error: an analyser holds no stock and is not supposed to.
        ///
        /// **Silent when the role declares no stock**, so the three original roles read exactly
        /// as they did.
        /// </summary>
        internal string StockShortfallReadout(RimroomsGateEquipmentDef role)
        {
            if (role == null || role.stockTarget <= 0) { return null; }
            ThingCategoryDef category = role.StockCategory;
            if (category == null) { return null; }

            int held = 0;
            foreach (Thing linked in LinkedEquipment)
            {
                // The role the player ASSIGNED, not every role the def could fill. A shelf the
                // branch nominated as its armory is not also its receiving bay, and counting by
                // `Accepts` would have made one shelf satisfy all three shelf roles at once.
                if (RoleOf(linked) != role) { continue; }
                SlotGroup group = linked.GetSlotGroup();
                if (group == null || group.HeldThings == null) { continue; }
                foreach (Thing stored in group.HeldThings)
                {
                    if (stored == null || stored.def == null) { continue; }
                    if (!category.DescendantThingDefs.Contains(stored.def)) { continue; }
                    held += stored.stackCount;
                }
            }
            if (held >= role.stockTarget) { return null; }

            string line = "RR_GateLink_RoleShortfall".Translate(role.LabelCap, held.ToString(),
                role.stockTarget.ToString()).ToString();
            // The consequence, named. *"Risk: 3"* tells a player nothing; what actually goes
            // wrong when the shelf is empty tells them why it matters. Optional, because a role
            // can want stock without anything going wrong when it is short.
            if (!string.IsNullOrEmpty(role.riskKey))
            { line += " " + role.riskKey.Translate().ToString(); }
            return line;
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
                // **The row says which role it is unlinking from.** With three roles filled by
                // the same shelf def, "unlink shelf" three times over would be a menu a player
                // cannot use.
                RimroomsGateEquipmentDef assigned = RoleOf(target);
                options.Add(new FloatMenuOption(
                    "RR_GateLink_UnlinkRole".Translate(target.LabelCap,
                        assigned == null
                            ? "RR_NativeGate_Unselected".Translate().ToString()
                            : assigned.LabelCap.ToString(),
                        WhereLabel(target)),
                    delegate { ShowOrderResult(UnlinkEquipment(target)); },
                    MenuOptionPriority.Default, HighlightOnHover(target)));
            }

            // Candidates are enumerated from the map rather than remembered, and sorted
            // ordinally before being shown: a list a player picks from must not depend on
            // whatever order the map's building lister happens to be in.
            //
            // **ONE ROW PER THING AND ROLE, which is the change the role record forced.** Core
            // ships no weapon rack and no receiving bay, so a `Shelf` answers the archive, the
            // armory and the receiving bay, and only the player knows which this one is. Offering
            // the thing alone and deciding for them is what made the armory and the receiving bay
            // unfillable in the first place.
            if (parent.Map != null)
            {
                var candidates = new List<KeyValuePair<Thing, RimroomsGateEquipmentDef>>();
                foreach (Building building in parent.Map.listerBuildings.allBuildingsColonist)
                {
                    foreach (RimroomsGateEquipmentDef role in RimroomsGateEquipmentDef.AllInOrder())
                    {
                        if (EquipmentLinkFailureKey(building, role) != null) { continue; }
                        candidates.Add(new KeyValuePair<Thing, RimroomsGateEquipmentDef>(
                            building, role));
                    }
                }
                foreach (KeyValuePair<Thing, RimroomsGateEquipmentDef> candidate in candidates
                    .OrderBy(pair => pair.Value.displayOrder)
                    .ThenBy(pair => pair.Key.def.defName, System.StringComparer.Ordinal)
                    .ThenBy(pair => pair.Key.thingIDNumber)
                    .ToList())
                {
                    Thing target = candidate.Key;
                    RimroomsGateEquipmentDef role = candidate.Value;
                    options.Add(new FloatMenuOption(
                        "RR_GateLink_AddRole".Translate(target.LabelCap, role.LabelCap,
                            WhereLabel(target)),
                        delegate { ShowOrderResult(LinkEquipment(target, role)); },
                        MenuOptionPriority.Default, HighlightOnHover(target)));
                }
            }

            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_GateLink_NoCandidates".Translate(), null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        /// <summary>
        /// The room a thing stands in and its cell, so one shelf can be told from another.
        ///
        /// **Found by playing, 2026-10-07.** The records archive had to move off a freezer shelf
        /// onto a lab shelf, and the menu offered some forty rows reading *"Link Wooden shelf as
        /// Records archive"* -- one per shelf and role, all identical. Nothing on the row said
        /// which shelf it was, so the only way to pick the right one was to guess, save and read
        /// the save. The room is Core's own role label, the one the cell inspector shows.
        /// </summary>
        private static string WhereLabel(Thing thing)
        {
            Room room = thing.Spawned ? thing.GetRoom() : null;
            string place = room == null || room.PsychologicallyOutdoors
                ? "RR_GateLink_Outdoors".Translate().ToString()
                : room.GetRoomRoleLabel();
            return "RR_GateLink_Where".Translate(place, thing.Position.x.ToString(),
                thing.Position.z.ToString()).ToString();
        }

        /// <summary>Hovering a row marks the thing on the map, the way Core's own menus do.</summary>
        private static System.Action<UnityEngine.Rect> HighlightOnHover(Thing thing)
        {
            return delegate { TargetHighlighter.Highlight(thing, true, false, true); };
        }

        internal void ExposeEquipmentLinks()
        {
            Scribe_Collections.Look(ref gateEquipment, "rr_gateEquipment", LookMode.Reference);
            Scribe_Collections.Look(ref gateEquipmentRoles, "rr_gateEquipmentRoles",
                LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (gateEquipment == null) { gateEquipment = new List<Thing>(); }
                if (gateEquipmentRoles == null) { gateEquipmentRoles = new List<string>(); }
                // **Aligned BEFORE anything is dropped**, because this is also the migration: a
                // save written before the role was recorded arrives with no roles at all, and
                // `AlignRoles` gives each link the role the old code would have derived for it.
                AlignRoles();

                // A thing that was deconstructed while the save was closed is not a link any
                // more. **Removed in lockstep, never with `RemoveAll`**: the two lists are
                // index-matched, and dropping from one of them alone would silently re-label
                // every link after the gap -- a branch's armory would come back as its canteen.
                for (int index = gateEquipment.Count - 1; index >= 0; index--)
                {
                    Thing thing = gateEquipment[index];
                    if (thing != null && !thing.Destroyed) { continue; }
                    gateEquipment.RemoveAt(index);
                    if (index < gateEquipmentRoles.Count) { gateEquipmentRoles.RemoveAt(index); }
                }
            }
        }
    }
}
