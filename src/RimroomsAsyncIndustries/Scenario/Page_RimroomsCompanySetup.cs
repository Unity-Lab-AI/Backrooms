using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimroomsAsyncIndustries.UI;
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
        private string companyNameBuffer;

        /// <summary>Set when a draw throws, and then shown on the page rather than swallowed.</summary>
        private string drawFault;
        public override string PageTitle { get { return "RR_Setup_Title".Translate(); } }

        public override void DoWindowContents(Rect rect)
        {
            // Known-good IMGUI state for this draw, restored on the way out. The first real
            // launch of this mod opened this page with its title and buttons drawn and its body
            // completely empty, with nothing in the log -- the signature of inherited global
            // draw state in a 288-mod load. See RimroomsWindowState.
            using (RimroomsWindowState.Clean())
            {
                DrawBody(rect);
            }
        }

        private void DrawBody(Rect rect)
        {
            DrawPageTitle(rect);
            Rect body = rect;
            body.yMin += 45f;
            DoBottomButtons(body, "Start".Translate(), null, null, true, false);
            body.yMax -= 60f;

            // ------------------------------------------------------------------ pinned, top
            // The introduction is drawn OUTSIDE the scroll view on purpose. It is the one thing
            // on this page that is true in every state, so a failure anywhere below cannot take
            // it down with it -- and a page that shows something is a page a player can report.
            Rect intro = body;
            intro.height = Text.CalcHeight("RR_Setup_Introduction".Translate(), body.width - 20f);
            Widgets.Label(intro, "RR_Setup_Introduction".Translate());
            body.yMin += intro.height + 8f;
            if (body.height <= 0f) { return; }

            RimroomsStartDef pinned = ScenPart_RimroomsStart.Current?.startDef;

            // **The company name field is pinned too, and this is the second thing the first
            // launch found.** It used to sit inside the scroll view, a few hundred pixels down a
            // list long enough to need scrolling, and the owner's report was *"there is no box to
            // type in my company name"*. It was drawn -- the log proves DrawReview completed --
            // and that is not the same as reachable.
            //
            // **A control the player is required to use must not be scrollable out of view.**
            if (pinned != null)
            {
                if (companyNameBuffer == null)
                { companyNameBuffer = RimroomsStartupComponent.SuggestedName(pinned); }
                Rect nameLabel = body;
                nameLabel.height = Text.CalcHeight("RR_Setup_CompanyName".Translate(),
                    body.width - 20f);
                Widgets.Label(nameLabel, "RR_Setup_CompanyName".Translate());
                body.yMin += nameLabel.height + 2f;

                Rect field = new Rect(body.x, body.yMin, Mathf.Min(420f, body.width - 20f), 30f);
                // Given a visible border so it reads as something to type in rather than as
                // another line of the paragraph above it. `Widgets.DrawBox` is Core's own and
                // authors no colour -- the first draft of this used
                // `DrawBoxSolid(field, new Color(0.12f, 0.12f, 0.12f))`, which is exactly the
                // authored palette this package refuses to impose, in the one folder
                // `check-display-style.py` was not scanning. The checker's scope was widened
                // rather than the exception being taken.
                Widgets.DrawBox(field);
                companyNameBuffer = Widgets.TextField(field.ContractedBy(2f), companyNameBuffer);
                body.yMin += field.height + 10f;
                if (body.height <= 0f) { return; }
            }

            // ------------------------------------------------------- pinned, bottom: the gate
            // The confirm checkbox is what blocks Start, and it used to be the LAST line of a
            // list that needed scrolling -- so the page refused to start and the reason for the
            // refusal was off screen. Reserved before the scroll view is measured, so the thing
            // that blocks the button is always beside the button.
            float confirmHeight = Mathf.Max(30f, Text.CalcHeight("RR_Setup_Confirm".Translate(),
                body.width - 48f));
            Rect confirm = new Rect(body.x, body.yMax - confirmHeight, body.width - 20f,
                confirmHeight);
            body.yMax -= confirmHeight + 8f;

            Rect content = new Rect(0f, 0f, body.width - 20f, contentHeight);
            Widgets.BeginScrollView(body, ref scroll, content);
            var listing = new Listing_Standard();
            // One column. Core's Listing silently wraps a full column-width to the RIGHT when content
            // outgrows the rect, outside the group it clips to, and resets CurHeight doing it -- so the
            // page loses its tail AND under-reports its height, which shrinks the rect again.
            listing.maxOneColumn = true;
            listing.Begin(content);
            try
            {
                DrawReview(listing);
            }
            catch (Exception exception)
            {
                // A throw here used to leave the listing open, wedge the GUI group stack, and
                // paint nothing. Saying what broke, on the page, is worth more than a clean
                // stack trace nobody sees -- and the log is written too.
                drawFault = exception.GetType().Name + ": " + exception.Message;
                Log.Error("[Rimrooms] Company setup page failed to draw: " + exception);
            }
            if (drawFault != null) { listing.Label("RR_Setup_DrawFault".Translate(drawFault)); }
            contentHeight = listing.CurHeight + 20f;
            listing.End();
            Widgets.EndScrollView();

            // The gate, drawn last into the space reserved above the buttons. Never inside the
            // scroll view: a player who cannot see why Start refuses has no way to satisfy it.
            var gate = new Listing_Standard();
            // Same flag for the same reason: this rect is sized to one checkbox, so a
            // label that wraps to a second line would push the box off to the right.
            gate.maxOneColumn = true;
            gate.Begin(confirm);
            gate.CheckboxLabeled("RR_Setup_Confirm".Translate(), ref reviewed);
            gate.End();
        }

        private void DrawReview(Listing_Standard listing)
        {
            RimroomsStartDef start = ScenPart_RimroomsStart.Current?.startDef;
            List<Pawn> pawns = null;
            string reason = null;
            if (start == null || start.ConfigErrors().Any() || !StartupReview.TrySelected(out pawns, out reason))
            {
                listing.Label((start == null ? "RR_Start_MissingSetup" : reason ?? "RR_Setup_InvalidConfiguration").Translate());
            }
            else
            {
                SynchronizeRoles(start, pawns);
                // The company name field used to be here. It is pinned above this scroll view
                // now -- see DrawBody. Every start names its own company, so it is offered on
                // every one, and it must be reachable without scrolling to find it.

                // FIRST, because it is the only thing on this page that answers "what can I
                // actually do when the game starts". Owner question, 2026-09-30: *"shouldnt that
                // page list the starting equipment and supplies added from the company to get a
                // gate up quickly"*. The page listed the facility and never connected any of it
                // to the gate.
                DrawGateReadiness(listing, start);
                listing.GapLine();

                // The map size is the player's own choice now, so showing the def's authored number
                // would be telling them something that is not true about their game.
                listing.Label("RR_Setup_Site".Translate(Find.GameInitData.startingTile.ToString(),
                    Find.GameInitData.mapSize));
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

                // WHAT THE COMPANY ADDS, FIRST AND NAMED AS SUCH. Owner, verbatim: *"that pop up
                // should list all the equipemnet for the gate that u get added to ur start on top
                // of what u fill out in edb prepare carfully"*.
                //
                // Read from the authored scenario def, so a setup utility that rewrites the live
                // scenario's starting-thing parts cannot empty this list -- which is exactly what
                // left the section blank.
                listing.Label("RR_Setup_CompanySupplies".Translate());
                List<string> company = StartupReview.CompanySupplies(start);
                if (company.Count == 0) { listing.Label("RR_Setup_None".Translate()); }
                foreach (string supply in company) { listing.Label(supply); }

                listing.GapLine();
                listing.Label("RR_Setup_Supplies".Translate());
                List<string> live = StartupReview.SupplySummary();
                if (live.Count == 0) { listing.Label("RR_Setup_None".Translate()); }
                foreach (string supply in live) { listing.Label(supply); }
                // Said plainly rather than reconciled: something else is managing the equipment,
                // which is a legitimate choice, and the two lists differing is the fact to report.
                if (StartupReview.EquipmentManagedElsewhere(start))
                { listing.Label("RR_Setup_SuppliesDiffer".Translate()); }
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
                // The confirm checkbox used to be here, at the bottom of a list long enough to
                // need scrolling -- so Start refused and its reason was off screen. It is pinned
                // above the buttons now; see DrawBody.
            }
        }

        /// <summary>
        /// What this start arrives able to do about a gate, and what it does not.
        ///
        /// Every figure is read from the gate recipe and from this start's own def, so retuning
        /// either retunes the readout. **A missing prerequisite is stated rather than omitted:**
        /// two of the three shipped starts do not place everything a gate needs, and until this
        /// existed nothing anywhere said so.
        /// </summary>
        private static void DrawGateReadiness(Listing_Standard listing, RimroomsStartDef start)
        {
            listing.Label("RR_Setup_GateHeading".Translate());

            string cost = GateReadinessReview.AssemblyCost();
            listing.Label(cost == null
                ? "RR_Setup_GateNoRecipe".Translate()
                : "RR_Setup_GateCost".Translate(cost));

            var missing = new List<string>();
            foreach (GateReadinessReview.Prerequisite item in GateReadinessReview.Check(start))
            {
                string name = item.Detail == null
                    ? item.LabelKey.Translate().ToString()
                    : item.LabelKey.Translate(item.Detail).ToString();
                listing.Label(item.Present > 0
                    ? "RR_Setup_GatePresent".Translate(name,
                        item.Present.ToString(CultureInfo.CurrentCulture))
                    : "RR_Setup_GateAbsent".Translate(name));
                if (item.Present <= 0) { missing.Add(name); }
            }

            // The conclusion, in one line, because a list of five rows is not an answer.
            //
            // **And the conclusion depends on the start, not only on the list.** Owner, verbatim:
            // *"the store start has a natural portal and to build a machanical one they need to
            // contact the company and resaerch whats needed"*. The defs already say exactly that
            // -- `beginsInCorporationContact` is false and `completedProjects` is empty for both
            // the Store and the solo start, against Async's eight including `RR_GateTelemetry`.
            //
            // So a start that is missing equipment AND out of contact is not deficient, it is
            // **earlier in its own progression**, and the first version of this readout called
            // that *"does not arrive able to raise a gate"* -- describing a designed step as a
            // fault. Three different conclusions, because there are three different situations.
            if (missing.Count == 0)
            {
                listing.Label("RR_Setup_GateReady".Translate());
            }
            else if (!start.beginsInCorporationContact)
            {
                listing.Label("RR_Setup_GateLaterWork".Translate(
                    string.Join(", ", missing.ToArray())));
                listing.Label(start.insideStart
                    ? "RR_Setup_GateInsideRoute".Translate()
                    : "RR_Setup_GateContactRoute".Translate());
            }
            else
            {
                // In contact, with the research, and still missing hardware: that one really is
                // something to build or buy.
                listing.Label("RR_Setup_GateNotReady".Translate(
                    string.Join(", ", missing.ToArray())));
            }
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
                pawns.Select(p => selectedRoles[p]).ToList(), StartupReview.SupplySummary(),
                companyNameBuffer);
            return base.CanDoNext();
        }
    }
}
