using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimroomsAsyncIndustries.Gate;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// The gate's watch posture from the ladder (config-post-strictness). Owner, verbatim: "there needs to be like a driop
    /// down sleector thing stay at post strict mild, default&gt; inbetween strict and mild".
    ///   {"cmd":"gate_posture","posture":"Mild|Balanced|Strict"}   every player gate on the map gets that posture
    /// It writes the same field the gate's watch-posture gizmo writes (CompRimroomsGate.watchPosture). The eat/safety floor
    /// (GateWatch.MustLeave) is checked before the posture in every case, so no posture can keep an operator at a post
    /// to starve.
    /// </summary>
    internal static class SetupTools12
    {
        private static readonly FieldInfo PostureField =
            typeof(CompRimroomsGate).GetField("watchPosture", BindingFlags.Instance | BindingFlags.NonPublic);

        public static string GatePosture(Map map, Dictionary<string, string> a)
        {
            a.TryGetValue("posture", out string want);
            if (!Enum.TryParse(want ?? "", true, out GateWatchPosture posture) || !Enum.IsDefined(typeof(GateWatchPosture), posture))
                return "refused: posture is Mild, Balanced or Strict";
            if (PostureField == null) return "refused: the gate has no watch posture field in this build";
            List<CompRimroomsGate> gates = map.listerThings.AllThings
                .OfType<ThingWithComps>().Select(t => t.GetComp<CompRimroomsGate>()).Where(c => c != null).ToList();
            if (gates.Count == 0) return "refused: no gate on this map";
            foreach (CompRimroomsGate g in gates) PostureField.SetValue(g, posture);
            return "ok: watch posture " + posture + " on " + gates.Count + " gate(s) (the eat/safety floor holds in every posture)";
        }
    }
}
