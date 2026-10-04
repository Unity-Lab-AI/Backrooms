using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Expedition;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    public sealed class CompProperties_RouteEvidence : CompProperties
    {
        public float analysisWorkRequired = 3000f;
        public CompProperties_RouteEvidence() { compClass = typeof(CompRouteEvidence); }
        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string error in base.ConfigErrors(parentDef)) { yield return error; }
            // Native Book independently refuses stacking. Do not override the active stack-limit provider.
            if (parentDef.stackLimit != 1 && (parentDef.thingClass == null || !typeof(Book).IsAssignableFrom(parentDef.thingClass)))
            { yield return "Non-book unique route evidence must have stackLimit 1."; }
            if (analysisWorkRequired <= 0f || float.IsNaN(analysisWorkRequired) || float.IsInfinity(analysisWorkRequired))
            { yield return "analysisWorkRequired must be finite and positive."; }
        }
    }

    public sealed class CompRouteEvidence : ThingComp
    {
        private int bindingSchema = 1;
        private string evidenceId;
        private string carrierLoadId;
        public string EvidenceId { get { return evidenceId; } }
        /// <summary>
        /// Work needed to analyse this record.
        ///
        /// **RR_Cap_Corroboration** (Measurement and evidence, tier 1) takes a quarter off. A
        /// branch that has learned to corroborate one record against another stops re-deriving
        /// everything from first principles each time.
        /// </summary>
        public float WorkRequired
        {
            get
            {
                float work = ((CompProperties_RouteEvidence)props).analysisWorkRequired;
                Company.RimroomsCampaignComponent campaign = Current.Game == null
                    ? null : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
                if (campaign != null && campaign.HasCapability("RR_Cap_Corroboration"))
                { work *= 0.75f; }
                return work;
            }
        }
        public bool HasValidBinding { get { return bindingSchema == 1 && !string.IsNullOrWhiteSpace(evidenceId) &&
            carrierLoadId == parent.GetUniqueLoadID() && IsSupportedCarrier(parent) && WorkRequired > 0f &&
            !float.IsNaN(WorkRequired) && !float.IsInfinity(WorkRequired); } }

        public static ThingDef NativeCarrierDef
        {
            get
            {
                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("TextBook");
                return definition != null && definition.modContentPack != null && definition.modContentPack.IsCoreMod &&
                    definition.thingClass != null && typeof(Book).IsAssignableFrom(definition.thingClass) && definition.comps != null &&
                    definition.comps.OfType<CompProperties_RouteEvidence>().Count() == 1 &&
                    definition.comps.Any(p => p.compClass == typeof(CompBook)) &&
                    definition.comps.Any(p => p.compClass == typeof(CompQuality)) ? definition : null;
            }
        }
        public static bool IsLegacyCarrier(Thing thing)
        {
            return thing != null && thing.def != null && thing.def.defName == "RR_RouteRecording" &&
                thing.def.modContentPack != null && string.Equals(thing.def.modContentPack.PackageId,
                    "unitylabai.rimroomsasyncindustries", StringComparison.OrdinalIgnoreCase);
        }
        public static bool IsSupportedCarrier(Thing thing)
        {
            return thing != null && !thing.Destroyed && thing.stackCount == 1 && thing.TryGetComp<CompRouteEvidence>() != null &&
                ((thing is Book && thing.def == NativeCarrierDef) || IsLegacyCarrier(thing));
        }
        public static bool IsBoundRouteEvidence(Thing thing, string id = null)
        {
            CompRouteEvidence comp = thing == null ? null : thing.TryGetComp<CompRouteEvidence>();
            return comp != null && comp.HasValidBinding && (id == null || comp.evidenceId == id);
        }
        // Conservative recovery scan: legacy loose carriers and suspect bound books both count.
        // An ordinary unrelated textbook never blocks site recovery.
        public static bool IsEvidenceCarrierPresence(Thing thing)
        {
            return IsLegacyCarrier(thing) || (thing is Book && thing.def != null && thing.def.defName == "TextBook" &&
                !string.IsNullOrEmpty(thing.TryGetComp<CompRouteEvidence>()?.EvidenceId));
        }
        public bool Initialize(string id)
        {
            if (bindingSchema != 1 || !IsSupportedCarrier(parent) || string.IsNullOrWhiteSpace(id) ||
                (!string.IsNullOrEmpty(evidenceId) && evidenceId != id) ||
                (!string.IsNullOrEmpty(carrierLoadId) && carrierLoadId != parent.GetUniqueLoadID())) { return false; }
            evidenceId = id;
            carrierLoadId = parent.GetUniqueLoadID();
            return true;
        }
        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref bindingSchema, "rr_evidenceBindingSchema", 1);
            Scribe_Values.Look(ref evidenceId, "rr_evidenceId");
            Scribe_Values.Look(ref carrierLoadId, "rr_carrierLoadId");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && bindingSchema == 1 && IsLegacyCarrier(parent) &&
                !string.IsNullOrEmpty(evidenceId) && string.IsNullOrEmpty(carrierLoadId))
            { carrierLoadId = parent.GetUniqueLoadID(); }
        }
        public override string CompInspectStringExtra()
        {
            RimroomsCampaignComponent campaign = Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            // **A BLANK BOOK SAID NOTHING AT ALL, AND A BLANK BOOK IS THE ONLY KIND THE COMPANY
            // EVER HANDS YOU.** Owner, 2026-10-03, verbatim: *"the company is suppose to supply u
            // with a journal to do tasks in but they only gave me noraml books named wrong things
            // that dont do anything"*.
            //
            // This method opened with `if (string.IsNullOrEmpty(evidenceId)) { return null; }`,
            // which returned **before** `RR_Evidence_Unregistered` could ever be reached. So the
            // one state a player actually starts holding -- an unwritten book granted by the
            // scenario -- was the single state with no guidance, while the *registered* state had
            // had a next step since the same owner's earlier report *"it was confusing at what i
            // was suppose to do with it"*. The fix then was applied to one branch and the branch
            // nobody reaches first was left silent.
            //
            // Said only while the branch can operate and only on a book that could actually
            // serve, so an ordinary Core novel in an ordinary colony is untouched.
            //
            // **And the book is deliberately NOT renamed.** `CompProperties_RouteEvidence` is
            // patched onto EVERY Core `TextBook` (`Patches/RR_ExistingEvidenceBook.xml`), because
            // the design is that any blank book can be carried in and written in the field. A
            // label transform here would therefore retitle every novel in the game, trade stock
            // and mod content included. The company's book is identified by what the card says it
            // is for, not by overwriting Core's own titles.
            if (string.IsNullOrEmpty(evidenceId))
            {
                return campaign == null || !campaign.CanOperate || !IsSupportedCarrier(parent)
                    ? null
                    : "RR_Evidence_Blank".Translate().ToString();
            }
            EvidenceRecord record = campaign == null ? null : campaign.FindEvidence(evidenceId);
            return !HasValidBinding || record == null || record.Item != parent ? "RR_Evidence_Unregistered".Translate().ToString()
                // **THE NEXT THING TO DO, not just the state.** Owner, on finding one on a
                // shelf in the Backrooms: *"it was confusing at what i was suppose to do with
                // it"*. A status readout is only useful to somebody who already knows the
                // procedure exists, and the description that explains it is four sentences long
                // on an item lying in a maze.
                : "RR_Evidence_Inspect".Translate(("RR_EvidenceStatus_" + record.Status).Translate(),
                    (record.AnalysisWork / WorkRequired).ToString("P0"),
                    "RR_Evidence_NextStep".Translate()).ToString();
        }
        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption option in base.CompFloatMenuOptions(selPawn)) { yield return option; }
            if (!HasValidBinding || selPawn == null || selPawn.Faction != Faction.OfPlayer || !parent.Spawned ||
                selPawn.Map != parent.Map || parent.Position.Fogged(parent.Map)) { yield break; }
            RimroomsCampaignComponent campaign = Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null || !campaign.CanOperate || campaign.FindEvidence(evidenceId)?.Item != parent) { yield break; }
            yield return new FloatMenuOption("RR_UI_RecoverEvidence".Translate(selPawn.LabelShortCap), delegate
            {
                if (!HasValidBinding || !campaign.CanOperate || campaign.FindEvidence(evidenceId)?.Item != parent) { return; }
                CompanyActionResult result = ExpeditionCargo.QueuePickup(selPawn, parent, 1);
                if (!result.Success) { Messages.Message(result.MessageKey.Translate(), MessageTypeDefOf.RejectInput, false); }
            });
        }
    }
}
