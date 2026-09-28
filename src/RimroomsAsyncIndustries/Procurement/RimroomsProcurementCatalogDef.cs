using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Procurement
{
    /// <summary>A price/lead-time rule for ordering an existing RimWorld item Def.</summary>
    public sealed class RimroomsProcurementCatalogDef : Def
    {
        public string thingDefName;
        public long unitPriceUsd;
        public int dispatchDelayTicks;
        public int leadTimeTicks;
        public int maxOrderQuantity = 1000;

        public ThingDef ItemDef { get { return string.IsNullOrEmpty(thingDefName) ? null : DefDatabase<ThingDef>.GetNamedSilentFail(thingDefName); } }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrWhiteSpace(thingDefName)) { yield return "Procurement catalog entry needs a Core ThingDef name."; }
            if (unitPriceUsd <= 0) { yield return "Procurement unit price must be a positive USD estimate."; }
            if (dispatchDelayTicks < 0 || leadTimeTicks <= dispatchDelayTicks || leadTimeTicks > 60000 * 30)
            { yield return "Procurement dispatch and arrival delays must be ordered and no more than 30 in-game days."; }
            if (maxOrderQuantity < 1 || maxOrderQuantity > 1000000)
            { yield return "Procurement quantity limit must be between 1 and 1,000,000."; }
        }
    }
}
