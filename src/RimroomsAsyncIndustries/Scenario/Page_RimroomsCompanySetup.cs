using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    public sealed class Page_RimroomsCompanySetup : Page
    {
        private readonly Dictionary<Pawn, string> selectedRoles = new Dictionary<Pawn, string>();
        private List<Pawn> lastRoster = new List<Pawn>();
        private Vector2 scroll;
        private float contentHeight = 1000f;
        private bool reviewed;
        public override string PageTitle { get { return "RR_Setup_Title".Translate(); } }

        public override void DoWindowContents(Rect rect)
        {
            DrawPageTitle(rect);
            Rect body = rect;
            body.yMin += 45f;
            DoBottomButtons(body, "Start".Translate(), null, null, true, false);
            body.yMax -= 60f;
            Rect content = new Rect(0f, 0f, body.width - 20f, contentHeight);
            Widgets.BeginScrollView(body, ref scroll, content);
            var listing = new Listing_Standard();
            listing.Begin(content);
            RimroomsStartDef start = ScenPart_RimroomsStart.Current?.startDef;
            List<Pawn> pawns = null;
            string reason = null;
            listing.Label("RR_Setup_Introduction".Translate());
            if (start == null || start.ConfigErrors().Any() || !StartupReview.TrySelected(out pawns, out reason))
            {
                listing.Label((start == null ? "RR_Start_MissingSetup" : reason ?? "RR_Setup_InvalidConfiguration").Translate());
            }
            else
            {
                SynchronizeRoles(start, pawns);
                listing.Label("RR_Setup_Site".Translate(Find.GameInitData.startingTile.ToString(), start.mapSize));
                listing.Label("RR_Setup_StaffCount".Translate(pawns.Count));
                listing.Label("RR_Setup_Funding".Translate(start.initialFundingUsd.ToString("N0"),
                    start.dailyWageUsd.ToString("N0"), start.dailyOverheadUsd.ToString("N0")));
                foreach (Pawn pawn in pawns)
                {
                    listing.GapLine();
                    listing.Label(pawn.LabelShortCap.ToString());
                    string current = selectedRoles[pawn];
                    if (listing.ButtonText("RR_Setup_Role".Translate(("RR_Setup_Role_" + current).Translate())))
                    {
                        var options = new List<FloatMenuOption>();
                        foreach (RimroomsStaffRole role in start.roles)
                        {
                            string roleId = role.id;
                            options.Add(new FloatMenuOption(("RR_Setup_Role_" + roleId).Translate(), delegate
                            { selectedRoles[pawn] = roleId; reviewed = false; }));
                        }
                        Find.WindowStack.Add(new FloatMenu(options));
                    }
                    RimroomsStaffRole assigned = start.roles.First(r => r.id == current);
                    foreach (string warning in StartupReview.Warnings(pawn, assigned)) { listing.Label(warning); }
                    var gear = new List<string>();
                    if (pawn.equipment != null) { gear.AddRange(pawn.equipment.AllEquipmentListForReading.Select(t => t.LabelCap.ToString())); }
                    if (pawn.apparel != null) { gear.AddRange(pawn.apparel.WornApparel.Select(t => t.LabelCap.ToString())); }
                    if (pawn.inventory != null) { gear.AddRange(pawn.inventory.innerContainer.Select(t => t.LabelCap.ToString())); }
                    listing.Label("RR_Setup_Gear".Translate(gear.Count == 0 ? "RR_Setup_None".Translate().ToString() : string.Join(", ", gear)));
                    List<ThingDefCount> possessions;
                    if (Find.GameInitData.startingPossessions.TryGetValue(pawn, out possessions) && possessions != null && possessions.Count > 0)
                    { listing.Label("RR_Setup_Possessions".Translate(string.Join(", ", possessions.Select(p => p.ThingDef.LabelCap + " ×" + p.Count)))); }
                }
                listing.GapLine();
                listing.Label("RR_Setup_Supplies".Translate());
                foreach (string supply in StartupReview.SupplySummary()) { listing.Label(supply); }
                listing.GapLine();
                listing.Label("RR_Setup_Facility".Translate());
                foreach (var group in start.buildings.Where(b => b.thing != null).GroupBy(b => b.thing))
                { listing.Label(group.Key.LabelCap + " ×" + group.Count()); }
                listing.Label("RR_Setup_FixedInfrastructure".Translate(start.rooms.Count, start.doors.Count, start.conduits.Count));
                foreach (RimroomsBuildingPlan plan in start.buildings)
                {
                    if (plan.fuelFraction > 0f)
                    { listing.Label("RR_Setup_FixedFuel".Translate(plan.thing.LabelCap, Mathf.Clamp01(plan.fuelFraction).ToString("P0"))); }
                    if (plan.batteryFraction > 0f)
                    { listing.Label("RR_Setup_FixedBattery".Translate(plan.thing.LabelCap, Mathf.Clamp01(plan.batteryFraction).ToString("P0"))); }
                }
                listing.Label("RR_Setup_FixedCapacity".Translate());
                listing.CheckboxLabeled("RR_Setup_Confirm".Translate(), ref reviewed);
            }
            contentHeight = listing.CurHeight + 20f;
            listing.End();
            Widgets.EndScrollView();
        }

        private void SynchronizeRoles(RimroomsStartDef start, List<Pawn> pawns)
        {
            if (!lastRoster.SequenceEqual(pawns)) { reviewed = false; lastRoster = new List<Pawn>(pawns); }
            foreach (Pawn old in selectedRoles.Keys.Where(p => !pawns.Contains(p)).ToList()) { selectedRoles.Remove(old); }
            for (int i = 0; i < pawns.Count; i++)
            {
                if (!selectedRoles.ContainsKey(pawns[i]) || !start.roles.Any(r => r.id == selectedRoles[pawns[i]]))
                { selectedRoles[pawns[i]] = start.roles[i % start.roles.Count].id; }
            }
        }

        public override void PostOpen() { base.PostOpen(); reviewed = false; }

        protected override bool CanDoNext()
        {
            List<Pawn> pawns = null;
            string reason = null;
            RimroomsStartDef start = ScenPart_RimroomsStart.Current?.startDef;
            if (start == null || start.ConfigErrors().Any() || !StartupReview.TrySelected(out pawns, out reason))
            { Messages.Message((start == null ? "RR_Start_MissingSetup" : reason ?? "RR_Setup_InvalidConfiguration").Translate(), MessageTypeDefOf.RejectInput, false); return false; }
            SynchronizeRoles(start, pawns);
            if (!reviewed) { Messages.Message("RR_Setup_NeedsReview".Translate(), MessageTypeDefOf.RejectInput, false); return false; }
            Current.Game.GetComponent<RimroomsStartupComponent>().Accept(start, pawns,
                pawns.Select(p => selectedRoles[p]).ToList(), StartupReview.SupplySummary());
            return base.CanDoNext();
        }
    }
}
