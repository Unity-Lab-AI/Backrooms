using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    // These dialogs confirm record changes only. Simulation services recheck live state.
    public sealed class Dialog_ExpeditionClosure : Window
    {
        private readonly ExpeditionRecord run;
        private string reason = "";
        private Vector2 scroll;
        private float contentHeight = 420f;
        public override Vector2 InitialSize { get { return new Vector2(660f, 530f); } }
        public Dialog_ExpeditionClosure(ExpeditionRecord run)
        { this.run = run; forcePause = true; absorbInputAroundWindow = true; doCloseX = true; }
        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawClosure(inRect); }
        }

        private void DrawClosure(Rect inRect)
        {
            Rect content = new Rect(0, 0, inRect.width - 20f, contentHeight);
            Widgets.BeginScrollView(inRect, ref scroll, content);
            var listing = new Listing_Standard(); listing.Begin(content);
            listing.Label("RR_UI_AbandonPreview".Translate(run.ExpeditionId));
            ExpeditionClosureRecord preview = Current.Game.GetComponent<RimroomsExpeditionComponent>().PreviewAbandonment(run.ExpeditionId);
            if (preview != null)
            {
                listing.Label("RR_UI_AbandonCounts".Translate(preview.Crew.Count(p => p.Location == CrewClosureLocation.AtSite),
                    preview.Crew.Count(p => p.KnownDead), preview.Cargo.Count));
                listing.Label("RR_UI_AbandonTransfers".Translate(preview.PendingTransferCount, preview.HeldForRecoveryCount));
                foreach (CrewClosureRecord person in preview.Crew)
                {
                    listing.Label("RR_UI_AbandonPerson".Translate(person.Label, ("RR_CrewClosure_" + person.Location).Translate(),
                        person.KnownDead ? "RR_UI_CrewDead".Translate().ToString() : ""));
                }
            }
            listing.Label("RR_UI_AbandonExplanation".Translate());
            listing.Gap(12f);
            listing.Label("RR_UI_RecordReason".Translate());
            reason = listing.TextEntry(reason);
            if (reason.Length > 240) { reason = reason.Substring(0, 240); }
            listing.Gap(12f);
            if (listing.ButtonText("RR_UI_ConfirmAbandon".Translate()))
            { Finish(Current.Game.GetComponent<RimroomsExpeditionComponent>().AbandonExpedition(run.ExpeditionId, reason)); }
            if (listing.ButtonText("Cancel".Translate())) { Close(); }
            contentHeight = Mathf.Max(420f, listing.CurHeight + 10f);
            listing.End(); Widgets.EndScrollView();
        }
        private void Finish(CompanyActionResult result)
        {
            if (result.Success) { Close(); }
            else { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
        }
    }

    public sealed class Dialog_CargoDeclaration : Window
    {
        private readonly CargoManifestEntry entry;
        private CargoDisposition disposition;
        private string count;
        private string note = "";
        public override Vector2 InitialSize { get { return new Vector2(600f, 400f); } }
        public Dialog_CargoDeclaration(CargoManifestEntry entry)
        {
            this.entry = entry; disposition = entry.Declaration;
            count = (entry.DeclaredCount > 0 ? entry.DeclaredCount : entry.UnresolvedCount).ToString(CultureInfo.InvariantCulture);
            forcePause = true; absorbInputAroundWindow = true; doCloseX = true;
        }
        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawDeclaration(inRect); }
        }

        private void DrawDeclaration(Rect inRect)
        {
            var listing = new Listing_Standard(); listing.Begin(inRect);
            listing.Label("RR_UI_DeclareCargoTitle".Translate(entry.Label));
            listing.Label("RR_UI_DeclareCargoExplanation".Translate(entry.OriginalCount, entry.ObservedCount, entry.UnresolvedCount));
            if (listing.ButtonText(("RR_Cargo_" + disposition).Translate()))
            {
                var options = new List<FloatMenuOption>();
                foreach (CargoDisposition option in Enum.GetValues(typeof(CargoDisposition)))
                {
                    CargoDisposition captured = option;
                    options.Add(new FloatMenuOption(("RR_Cargo_" + option).Translate(), delegate
                    {
                        disposition = captured;
                        int suggested = captured == CargoDisposition.Unspecified ? 0
                            : captured == CargoDisposition.Consumed || captured == CargoDisposition.Lost ? entry.UnresolvedCount : entry.ObservedCount;
                        count = suggested.ToString(CultureInfo.InvariantCulture);
                    }));
                }
                Find.WindowStack.Add(new FloatMenu(options));
            }
            listing.Label("RR_UI_DeclareCount".Translate()); count = listing.TextEntry(count);
            listing.Label("RR_UI_RecordReason".Translate()); note = listing.TextEntry(note);
            if (note.Length > 240) { note = note.Substring(0, 240); }
            if (listing.ButtonText("RR_UI_SaveCargoDeclaration".Translate()))
            {
                int quantity;
                if (!int.TryParse(count, NumberStyles.None, CultureInfo.InvariantCulture, out quantity))
                { Messages.Message("RR_UI_InvalidCargoCount".Translate(), MessageTypeDefOf.RejectInput, false); }
                else
                {
                    CompanyActionResult result = Current.Game.GetComponent<RimroomsExpeditionComponent>()
                        .RecordCargoDisposition(entry.Id, disposition, quantity, note);
                    if (result.Success) { Close(); }
                    else { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
                }
            }
            if (listing.ButtonText("Cancel".Translate())) { Close(); }
            listing.End();
        }
    }
}
