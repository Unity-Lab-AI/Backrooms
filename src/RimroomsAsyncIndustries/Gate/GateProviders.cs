using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// Which buildings may fill a gate's three infrastructure roles, and which one is taken without
    /// asking the player.
    ///
    /// **THIS EXISTS BECAUSE THE RULE WAS WRITTEN DOWN TWICE AND THE OWNER SAW IT COMING.** Owner,
    /// 2026-10-06: *"rmeembr this might change the set gate option and stuff on doors"*, and
    /// *"and the comms console and machining bench"*. The def names were hard coded in two places --
    /// the lister in `OperationsGateBinding` and `ExactProvider` here in `NativeGateBinding` -- so
    /// widening one and not the other produces a console that appears in the pane and is then
    /// refused by the validator, which reads to a player as the button being broken.
    ///
    /// **THE COMPONENT IS THE ALLOWLIST, which is this file's own existing principle** -- stated at
    /// `NativeDoorProvider` about doors: *"the component is only ever attached by this mod's own
    /// patches, so carrying the component is the allowlist"*. `CompRimroomsGateConsole` is attached
    /// by `RR_NativeGateProviders.xml` to `CommsConsole` and `TableMachining` and declared directly
    /// on the company's own two buildings, and by nothing else. So membership is the component and
    /// **role is the type**, which is not a new rule: `CompRimroomsGateConsole` already refuses to
    /// attach to a def whose `thingClass` is neither `Building_WorkTable` nor
    /// `Building_CommsConsole`. No def name is tested anywhere below except to ask *is this one
    /// ours*, which is a different question with a different answer.
    ///
    /// **THE PREFERENCE RULE IS THE WHOLE POINT, AND GETTING IT WRONG WOULD HAVE SHIPPED A
    /// REGRESSION DISGUISED AS A FEATURE.** The door's set-gate toggle binds only when a role has
    /// exactly one candidate, so the obvious implementation -- *our building is one more candidate*
    /// -- means a branch that builds the company console **beside** the Core one goes from a
    /// working toggle to `RR_NativeGate_NoSingleConsole`. That is the owner's own open report of
    /// 2026-10-03 arriving by a second route, caused by adding content.
    ///
    /// So: **exactly one of ours wins outright, however many native ones there are.** Building the
    /// company console can only ever resolve an ambiguity, never create one. Two of ours is
    /// genuinely ambiguous and goes to the player, which is the existing contract unchanged.
    /// </summary>
    public static class RimroomsGateProviders
    {
        /// <summary>The company's own console def. Named here once, for the defs and the checkers.</summary>
        public const string CompanyConsole = "RR_GateConsole";

        /// <summary>The company's own assembly bench def.</summary>
        public const string CompanyAssemblyBench = "RR_FieldAnalysisBench";

        /// <summary>
        /// Core's battery, still by name and deliberately so.
        ///
        /// Every other role widened; this one did not. Accepting anything carrying
        /// `CompPowerBattery` would admit every battery in the profile -- Efficient batteries,
        /// Rimatomics and the rest -- which is a gameplay change nobody asked for, in the one role
        /// whose capacity a crew's way home depends on. The company ships no battery of its own, so
        /// there is nothing to widen for.
        /// </summary>
        public const string NativeBattery = "Battery";

        /// <summary>Whether this building is one the company itself builds, rather than a native one.</summary>
        public static bool IsCompanyBuilt(Thing thing)
        {
            if (thing == null || thing.def == null) { return false; }
            return thing.def.defName == CompanyConsole || thing.def.defName == CompanyAssemblyBench;
        }

        /// <summary>A gate console: carries the component, and is a comms console by type.</summary>
        public static bool IsConsole(Thing thing)
        {
            return thing is Building_CommsConsole && thing.TryGetComp<CompRimroomsGateConsole>() != null;
        }

        /// <summary>An assembly bench: carries the component, and is a work table by type.</summary>
        public static bool IsAssemblyBench(Thing thing)
        {
            return thing is Building_WorkTable && thing.TryGetComp<CompRimroomsGateConsole>() != null;
        }

        /// <summary>A reserve battery: Core's battery def, holding a real battery component.</summary>
        public static bool IsBattery(Thing thing)
        {
            return thing != null && thing.def != null && thing.def.defName == NativeBattery
                && thing.TryGetComp<CompPowerBattery>() != null;
        }

        /// <summary>
        /// The candidate to bind without asking, or null when the player has to choose.
        ///
        /// One of ours beats any number of native ones. More than one of ours is a real choice and
        /// is handed back. With none of ours it is the original rule exactly: the sole native one,
        /// or nothing.
        /// </summary>
        public static Thing Preferred(IEnumerable<Thing> candidates)
        {
            if (candidates == null) { return null; }
            Thing company = null;
            Thing native = null;
            int companyCount = 0;
            int nativeCount = 0;
            foreach (Thing candidate in candidates)
            {
                if (candidate == null) { continue; }
                if (IsCompanyBuilt(candidate)) { companyCount++; company = candidate; }
                else { nativeCount++; native = candidate; }
            }
            if (companyCount == 1) { return company; }
            if (companyCount > 1) { return null; }
            return nativeCount == 1 ? native : null;
        }
    }
}
