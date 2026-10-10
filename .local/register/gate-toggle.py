# -*- coding: utf-8 -*-
"""A toggle on the door, which is where the owner looked for it.

> *"i have no idea how the gate is suppose to work as there doesnt be a toggle option to turn it
> from a normal door to a machine gate door"*

`CompGetGizmosExtra` opens with

    if (parent.Faction != Faction.OfPlayer || !IsDesignated) { yield break; }

so **an undesignated door offers nothing at all.** Every control for making one a gate lived in the
Operations tab, behind a provider-picking pane -- and with the company's state fault disabling
`CanOperate`, that pane was refusing too. So there was no route from a door to a gate anywhere the
player would look.

The corporate start **does** ship every component the binding needs, which is worth recording
because the owner doubted it: `CommsConsole` at (28,0,29), `Battery` at (44,0,26),
`TableMachining` at (17,0,44) and an `Autodoor` at (29,0,33). Nothing was missing from the
facility; the controls were unreachable.

## What the toggle does, and what it refuses

It binds with the **sole** candidate of each kind. Most branches have exactly one console, one
battery and one machining table, so the toggle simply works -- which is what *"basic components
there and connected just waiting to be switched on"* describes. With none or several of a kind it
refuses and names which, and the Operations pane stays for choosing deliberately.

**Nothing is decided here.** `BindNativeInfrastructure` applies every rule it always did: the
exact provider defs, the reserve size, the entry cell, the headquarters, the branch. This is a
second place to ask, not a second opinion about the answer.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GATE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate", "CompRimroomsGate.cs")
BINDING = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "UI", "OperationsGateBinding.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed", "RR_Gate.xml")

# ------------------------------------------- the scans become reachable, and sole-candidate
B_EDITS = [
    (u"        private static IEnumerable<Thing> AvailableNativeConsoles(RimroomsCampaignComponent campaign)",
     u"        internal static IEnumerable<Thing> AvailableNativeConsoles(RimroomsCampaignComponent campaign)"),
    (u"        private static IEnumerable<Thing> AvailableNativeBatteries(RimroomsCampaignComponent campaign)",
     u"        internal static IEnumerable<Thing> AvailableNativeBatteries(RimroomsCampaignComponent campaign)"),
    (u"        private static IEnumerable<Thing> AvailableNativeAssemblyBenches(RimroomsCampaignComponent campaign)",
     u"        internal static IEnumerable<Thing> AvailableNativeAssemblyBenches(RimroomsCampaignComponent campaign)"),
    (u"        private static IEnumerable<Thing> AvailableNativeBuildings(RimroomsCampaignComponent campaign, string defName)",
     u"""        /// <summary>
        /// The one candidate of a kind, or null when there is none or more than one.
        ///
        /// **The door toggle's whole contract.** A branch with exactly one console, one battery
        /// and one machining table -- which is every start this mod ships -- can be switched on
        /// from the door. Anything ambiguous is refused by name and chosen in this pane instead,
        /// because picking one of several on the player's behalf is a decision, not a shortcut.
        /// </summary>
        internal static Thing SoleCandidate(IEnumerable<Thing> candidates)
        {
            Thing only = null;
            foreach (Thing candidate in candidates)
            {
                if (only != null) { return null; }
                only = candidate;
            }
            return only;
        }

        private static IEnumerable<Thing> AvailableNativeBuildings(RimroomsCampaignComponent campaign, string defName)"""),
]

binding = io.open(BINDING, encoding="utf-8").read()
problems = []
for old, _ in B_EDITS:
    if binding.count(old) != 1:
        problems.append("%d of %r" % (binding.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM (binding): %s" % problem)
    raise SystemExit(1)
for old, new in B_EDITS:
    binding = binding.replace(old, new, 1)
io.open(BINDING, "w", encoding="utf-8", newline="").write(binding)
print("the provider scans are reachable and a sole-candidate helper exists")

# ------------------------------------------------------------------ the gizmo
G_OLD = u"""            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            if (parent.Faction != Faction.OfPlayer || !IsDesignated) { yield break; }"""

G_NEW = u"""            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            if (parent.Faction != Faction.OfPlayer) { yield break; }
            // **THE TOGGLE, ON THE DOOR.** Owner: *"i have no idea how the gate is suppose to
            // work as there doesnt be a toggle option to turn it from a normal door to a machine
            // gate door"*. This method used to yield break here for any undesignated door, so
            // **an ordinary door offered nothing at all** and the only route from a door to a
            // gate was a provider-picking pane in the Operations tab -- which the company's
            // state fault was also refusing. There was no route a player would find.
            if (!IsDesignated)
            {
                foreach (Gizmo gizmo in MakeGateGizmos()) { yield return gizmo; }
                yield break;
            }"""

G_METHOD_ANCHOR = u"""        public override IEnumerable<Gizmo> CompGetGizmosExtra()"""

G_METHOD = u'''        /// <summary>
        /// Turn this door into a machine gate, with the branch's own equipment.
        ///
        /// Offered only on a door at the headquarters, because `BindNativeInfrastructure` requires
        /// every provider to stand there and a button that can only refuse is worse than no
        /// button.
        ///
        /// **Nothing is decided here.** The binding applies every rule it always did -- the exact
        /// provider defs, the reserve size, the entry cell, the branch -- and this only answers
        /// *which* console, battery and bench, and only when there is exactly one of each. That
        /// is every start this mod ships, so the owner's *"basic components there and connected
        /// just waiting to be switched on"* is a single click; anything ambiguous is named and
        /// chosen in the Operations pane, because picking one of several for the player is a
        /// decision rather than a shortcut.
        /// </summary>
        private IEnumerable<Gizmo> MakeGateGizmos()
        {
            RimroomsCampaignComponent campaign = NativeCampaign;
            if (campaign == null || !campaign.CanOperate || parent.Map == null
                || campaign.Headquarters != parent.Map)
            { yield break; }
            if (!NativeDoorProvider()) { yield break; }

            yield return new Command_Action
            {
                defaultLabel = "RR_NativeGate_MakeLabel".Translate(),
                defaultDesc = "RR_NativeGate_MakeDesc".Translate(),
                icon = parent.def.uiIcon,
                action = delegate
                {
                    Thing console = UI.OperationsGateBinding.SoleCandidate(
                        UI.OperationsGateBinding.AvailableNativeConsoles(campaign));
                    Thing battery = UI.OperationsGateBinding.SoleCandidate(
                        UI.OperationsGateBinding.AvailableNativeBatteries(campaign));
                    Thing bench = UI.OperationsGateBinding.SoleCandidate(
                        UI.OperationsGateBinding.AvailableNativeAssemblyBenches(campaign));
                    if (console == null || battery == null || bench == null)
                    {
                        // Named, not silent: the player needs to know which piece to build or
                        // which choice to make, and "it did nothing" tells them neither.
                        ShowOrderResult(CompanyActionResult.Refused(
                            console == null ? "RR_NativeGate_ChooseConsole"
                            : battery == null ? "RR_NativeGate_ChooseBattery"
                            : "RR_NativeGate_ChooseBench"));
                        return;
                    }
                    ShowOrderResult(BindNativeInfrastructure(console, battery, bench,
                        OppositeEntrySideDefault));
                }
            };
        }

''' + G_METHOD_ANCHOR

gate = io.open(GATE, encoding="utf-8").read()
for old in (G_OLD, G_METHOD_ANCHOR):
    if gate.count(old) != 1:
        print("ANCHOR PROBLEM (gate): %d of %r" % (gate.count(old), old[:64]))
        raise SystemExit(1)
gate = gate.replace(G_OLD, G_NEW, 1)
gate = gate.replace(G_METHOD_ANCHOR, G_METHOD, 1)
io.open(GATE, "w", encoding="utf-8", newline="").write(gate)
print("the door carries the toggle")

# ------------------------------------------------------------------ the strings
K_ANCHOR = u"  <RR_NativeGate_KillSwitchThrown>"
K_NEW = (u"  <RR_NativeGate_MakeLabel>Make this a machine gate</RR_NativeGate_MakeLabel>\n"
         u"  <RR_NativeGate_MakeDesc>Commission this door as the branch's machine gate, using the "
         u"headquarters comms console, battery reserve and machining table. The gate still has to "
         u"be assembled, calibrated and powered before it will open.</RR_NativeGate_MakeDesc>\n"
         u"  <RR_NativeGate_ChooseBench>No single machining table to commission against. Build one "
         u"at the headquarters, or choose between them on the Operations gate "
         u"pane.</RR_NativeGate_ChooseBench>\n")

keyed = io.open(KEYED, encoding="utf-8-sig").read()
if keyed.count(K_ANCHOR) != 1:
    print("ANCHOR PROBLEM (keyed): %d" % keyed.count(K_ANCHOR))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(
    keyed.replace(K_ANCHOR, K_NEW + K_ANCHOR, 1))
print("keyed strings written")
