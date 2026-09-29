using System.Collections.Generic;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>
    /// The alerts readout down the right-hand edge of the screen — a RimWorld display surface
    /// this mod used **none** of until now.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"lets make sure the docs and informations
    /// displays in game are proper to backrrooms universe and rimworld gameplay style of all
    /// displayed informations of varying types to include all"*.
    ///
    /// *"to include all"* is what produced this file. The surface census in
    /// `tools/check-display-style.py` enumerates every place RimWorld shows text and counts how
    /// many of our strings reach each one, **including the ones at zero**, and the alerts
    /// readout came back empty. Every warning this mod had was either a letter you can dismiss
    /// and lose, or a line in an inspect pane you have to already be looking at. The one
    /// surface RimWorld uses for *a thing that is still wrong right now* was unused.
    ///
    /// No def, no asset, no patch and no Harmony: Core's <c>AlertsReadout</c> constructor walks
    /// <c>typeof(Alert).AllLeafSubclasses()</c> and instantiates whatever it finds, so a mod
    /// joins the readout by subclassing <see cref="Alert"/> and nothing else. Verified by
    /// decompiling <c>RimWorld.AlertsReadout</c>.
    ///
    /// **Cost was designed for, not assumed.** Register row 146, *No Hemogen Farm Medical
    /// Alert*, is a profile mod that exists to filter one Core alert, and its review records
    /// the author's own note about *"a possible small alert-check cost with many prisoners"*.
    /// Core calls <c>GetReport</c> on a rotating one-in-twenty-four schedule, so three alerts
    /// would otherwise mean three full building sweeps. <see cref="GateAlertScan"/> makes it at
    /// most one sweep per game tick no matter how many alerts ask.
    /// </summary>
    internal static class GateAlertScan
    {
        private static readonly List<CompRimroomsGate> Cached = new List<CompRimroomsGate>();
        private static int cachedTick = -1;
        private static Game cachedGame;

        /// <summary>
        /// Every designated gate the player owns, across every loaded map, recomputed at most
        /// once per game tick.
        ///
        /// The cache is keyed on the tick **and the game object**. Keying on the tick alone
        /// looks sufficient and is not: loading a second save that happens to sit on the same
        /// tick as the first would hand back the previous game's components, every one of them
        /// despawned. A load always produces a new <see cref="Game"/>, so comparing the
        /// reference closes that off completely.
        ///
        /// The returned list is the live cache rather than a copy, because the callers are
        /// three alerts that read it and discard it. Nothing mutates it.
        /// </summary>
        internal static List<CompRimroomsGate> DesignatedGates()
        {
            Game game = Current.Game;
            int now = game == null || Find.TickManager == null ? -1 : Find.TickManager.TicksGame;
            if (now == cachedTick && ReferenceEquals(game, cachedGame) && now >= 0) { return Cached; }

            cachedTick = now;
            cachedGame = game;
            Cached.Clear();
            if (game == null) { return Cached; }

            List<Map> maps = Find.Maps;
            if (maps == null) { return Cached; }
            for (int m = 0; m < maps.Count; m++)
            {
                Map map = maps[m];
                if (map == null || map.listerBuildings == null) { continue; }
                List<Building> buildings = map.listerBuildings.allBuildingsColonist;
                for (int b = 0; b < buildings.Count; b++)
                {
                    CompRimroomsGate gate = buildings[b].TryGetComp<CompRimroomsGate>();
                    if (gate != null && gate.IsDesignated) { Cached.Add(gate); }
                }
            }
            return Cached;
        }
    }

    /// <summary>
    /// **Critical.** The emergency return window has run out with people still on the far side.
    ///
    /// This is the one state in the whole mod that can quietly cost a player their colonists
    /// while they are looking somewhere else, which is exactly what RimWorld reserves
    /// <see cref="AlertPriority.Critical"/> for. It reuses the gate's own
    /// <c>IsAwaitingRecovery</c> rather than recomputing the condition, so the alert can never
    /// disagree with the inspect pane about whether anybody is stranded.
    /// </summary>
    public class Alert_RimroomsRecoveryOverdue : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_RimroomsRecoveryOverdue()
        {
            defaultLabel = "RR_Alert_RecoveryOverdue".Translate();
            defaultExplanation = "RR_Alert_RecoveryOverdueDesc".Translate();
            defaultPriority = AlertPriority.Critical;
        }

        public override AlertReport GetReport()
        {
            culprits.Clear();
            List<CompRimroomsGate> gates = GateAlertScan.DesignatedGates();
            for (int i = 0; i < gates.Count; i++)
            {
                if (gates[i].IsAwaitingRecovery) { culprits.Add(gates[i].parent); }
            }
            return AlertReport.CulpritsAre(culprits);
        }
    }

    /// <summary>
    /// **High.** A connection has failed while it was open and the return window is running.
    ///
    /// The warning that precedes <see cref="Alert_RimroomsRecoveryOverdue"/>, and the one the
    /// player can still act on. Every threat in this mod owes the player a readable warning, a
    /// learnable rule and a countermeasure; this is the readable warning for the failure the
    /// rest of the gate model is built around.
    /// </summary>
    public class Alert_RimroomsReturnWindowClosing : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_RimroomsReturnWindowClosing()
        {
            defaultLabel = "RR_Alert_ReturnWindowClosing".Translate();
            defaultExplanation = "RR_Alert_ReturnWindowClosingDesc".Translate();
            defaultPriority = AlertPriority.High;
        }

        public override AlertReport GetReport()
        {
            culprits.Clear();
            List<CompRimroomsGate> gates = GateAlertScan.DesignatedGates();
            for (int i = 0; i < gates.Count; i++)
            {
                CompRimroomsGate gate = gates[i];
                if (gate.IsEmergency && gate.EmergencyReturnTicksRemaining > 0) { culprits.Add(gate.parent); }
            }
            return AlertReport.CulpritsAre(culprits);
        }
    }

    /// <summary>
    /// **Medium.** There is a finished gate and nobody assigned to run any of them.
    ///
    /// The condition is deliberately colony-wide rather than per-gate. Firing on *each*
    /// unassigned gate would nag a player who runs one gate properly and keeps a second door
    /// designated for later — which is a reasonable thing to do, and being told off for it
    /// teaches a player to scroll past the alerts. Firing only when **no** finished gate
    /// anywhere has an operator says something that is unambiguously true and unambiguously a
    /// problem: no connection can be brought up at all.
    /// </summary>
    public class Alert_RimroomsNoGateOperator : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_RimroomsNoGateOperator()
        {
            defaultLabel = "RR_Alert_NoGateOperator".Translate();
            defaultExplanation = "RR_Alert_NoGateOperatorDesc".Translate();
            defaultPriority = AlertPriority.Medium;
        }

        public override AlertReport GetReport()
        {
            culprits.Clear();
            List<CompRimroomsGate> gates = GateAlertScan.DesignatedGates();
            for (int i = 0; i < gates.Count; i++)
            {
                CompRimroomsGate gate = gates[i];
                if (!gate.Calibrated) { continue; }
                if (gate.AssignedOperator != null) { culprits.Clear(); return AlertReport.Inactive; }
                culprits.Add(gate.parent);
            }
            return AlertReport.CulpritsAre(culprits);
        }
    }
}
