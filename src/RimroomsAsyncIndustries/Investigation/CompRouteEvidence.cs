using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Core;
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

    public sealed partial class CompRouteEvidence : ThingComp
    {
        private int bindingSchema = 1;
        private string evidenceId;
        private string carrierLoadId;
        /// <summary>
        /// Whether the company issued this book, as opposed to it being any other blank
        /// book in the game.
        ///
        /// **Set once, at the moment of granting, and saved.** Owner, 2026-10-04:
        /// *"Mark the company-issued ones"*. Nothing scans for books later, which is what
        /// makes it impossible to retro-tag something a player bought or looted -- there is
        /// no code path that could. The comp itself is on **every** Core `TextBook` by
        /// patch, because any blank book can be written in the field; this flag is the only
        /// thing that distinguishes the ones the branch handed out.
        /// </summary>
        private bool companyIssued;
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
        /// <summary>
        /// The company's own journal, when one is shipped and fully formed.
        ///
        /// **Owner complaint, 2026-10-03, quoted in full further down this file:** *"the company is
        /// suppose to supply u with a journal to do tasks in but they only gave me noraml books
        /// named wrong things that dont do anything"*. This is that journal. It became possible on
        /// 2026-10-06, when the owner reversed the existing-content-only direction and named it --
        /// *"and the journal"*, *"journal(s)"*.
        ///
        /// Resolved exactly as defensively as Core's: ours by package, a `Book` by type, and
        /// carrying all three components the evidence pipeline reads. Null when any of that is
        /// untrue, and every caller falls back to Core's book rather than losing the kit rule.
        /// </summary>
        public static ThingDef CompanyCarrierDef
        {
            get
            {
                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_RouteRecording");
                return definition != null && definition.modContentPack != null &&
                    string.Equals(definition.modContentPack.PackageId,
                        RimroomsMod.PackageId, StringComparison.OrdinalIgnoreCase) &&
                    definition.thingClass != null && typeof(Book).IsAssignableFrom(definition.thingClass) &&
                    definition.comps != null &&
                    definition.comps.OfType<CompProperties_RouteEvidence>().Count() == 1 &&
                    definition.comps.Any(p => p.compClass == typeof(CompBook)) &&
                    definition.comps.Any(p => p.compClass == typeof(CompQuality)) ? definition : null;
            }
        }

        /// <summary>
        /// A route recording this package itself ships.
        ///
        /// **THIS WAS CALLED `IsLegacyCarrier` AND THE NAME HAS STOPPED BEING TRUE.** It was written
        /// when `RR_RouteRecording` existed only in saves made before 0.9.0-dev retired it, so
        /// *legacy* described every thing it could ever match. The def ships again as of
        /// 0.13.0-dev, so the same test now matches brand new items, and a reader trusting the old
        /// name would conclude this branch is dead code and delete it.
        ///
        /// **The recognition shape is unchanged, deliberately.** It stays looser than `CompanyCarrierDef`
        /// -- def name and package, with no component requirements -- because its other job is to
        /// recognise a carrier in an old save whose def no longer fully resolves. Tightening it
        /// would orphan exactly the items it was written to rescue.
        /// The package check uses the live central identity rather than a retired package name:
        /// a saved carrier resolves its unchanged Def under the package supplying it now.
        /// </summary>
        public static bool IsCompanyCarrier(Thing thing)
        {
            return thing != null && thing.def != null && thing.def.defName == "RR_RouteRecording" &&
                thing.def.modContentPack != null && string.Equals(thing.def.modContentPack.PackageId,
                    RimroomsMod.PackageId, StringComparison.OrdinalIgnoreCase);
        }
        public static bool IsSupportedCarrier(Thing thing)
        {
            return thing != null && !thing.Destroyed && thing.stackCount == 1 && thing.TryGetComp<CompRouteEvidence>() != null &&
                ((thing is Book && thing.def == NativeCarrierDef) || IsCompanyCarrier(thing));
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
            return IsCompanyCarrier(thing) || (thing is Book && thing.def != null && thing.def.defName == "TextBook" &&
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
        /// <summary>Whether the branch issued this book.</summary>
        public bool IsCompanyIssued { get { return companyIssued; } }

        /// <summary>
        /// Which accepted quest this book is the deliverable for, or empty.
        ///
        /// **Owner direction, 2026-10-06:** *"its almost like every book recieved needs to be tuned
        /// to or capable of listing the current quests its needed for that has been acceptred"*.
        /// </summary>
        private string stampedQuestId;

        /// <summary>
        /// How many write-ups the record had filed when this book was last stamped.
        ///
        /// **A count, and it is the agreement test.** The record is the authority and this is the
        /// receipt, so the only question the book has to answer is *am I current*. A book stamped
        /// for the right quest but carrying a smaller count is a book from before the last write-up,
        /// which is the disagreement the owner asked to be visible rather than papered over.
        ///
        /// Counting rather than copying the list is deliberate: a second copy of *which* kinds were
        /// filed would be a second thing to keep in step, and the record already holds that.
        /// </summary>
        private int stampedWriteUpCount;

        public string StampedQuestId { get { return stampedQuestId; } }
        public int StampedWriteUpCount { get { return stampedWriteUpCount; } }

        /// <summary>
        /// Stamp this book for a quest at a tally. Called **only** from
        /// `RimroomsCampaignComponent.FileWriteUpAndStamp`, which writes the record first.
        ///
        /// Refuses a book the company did not issue, because a traded novel is not a deliverable
        /// and branding one would make `BookFor` able to find somebody else's property.
        ///
        /// **The count only ever rises.** A stamp carrying a smaller tally than the book already
        /// holds is stale — a resumed job, a reloaded save — and taking it would make a current book
        /// read as out of date, which shows as amber and tells the player to fix something that is
        /// not broken.
        /// </summary>
        public bool StampForQuest(string questId, int writeUpsFiled)
        {
            if (!companyIssued || string.IsNullOrWhiteSpace(questId) || writeUpsFiled < 0)
            { return false; }
            // **Captured BEFORE the assignment, because the first draft tested it after.** Setting
            // `stampedQuestId` first made the "different quest" branch dead code, so a book
            // re-stamped for a *new* quest with a lower tally would have kept the old quest's count.
            bool differentQuest = stampedQuestId != questId;
            if (!differentQuest && writeUpsFiled <= stampedWriteUpCount) { return false; }
            stampedQuestId = questId;
            // A new quest adopts its tally outright; the same quest only ever counts up.
            if (differentQuest || writeUpsFiled > stampedWriteUpCount)
            { stampedWriteUpCount = writeUpsFiled; }
            return true;
        }

        /// <summary>
        /// Mark this book as one the company handed out.
        ///
        /// Refuses anything that is not a supported carrier, so a caller cannot brand a
        /// thing that was never a record book. Idempotent: granting is recorded by a
        /// receipt elsewhere and this must not care how many times it is asked.
        /// </summary>
        public bool MarkCompanyIssued()
        {
            if (bindingSchema != 1 || !IsSupportedCarrier(parent)) { return false; }
            companyIssued = true;
            return true;
        }

        /// <summary>
        /// The company's own label on the company's own book, and Core's on everything else.
        ///
        /// **The guard is the whole point.** This comp is patched onto every Core
        /// `TextBook`, so an unguarded transform here would retitle every novel in the
        /// game: trade stock, quest rewards and other mods' books included. That is why the
        /// label half of *"its own label and an inspect card"* was not built until the
        /// owner chose how to tell the two apart.
        /// </summary>
        public override string TransformLabel(string label)
        {
            if (!companyIssued) { return label; }
            return "RR_Evidence_CompanyBookLabel".Translate().ToString();
        }

        /// <summary>
        /// What the company book's "i" card says, replacing Core's generated subject.
        ///
        /// **Owner, 2026-10-06, verbatim:** *"both are named wrong and have differ information in
        /// the "i" write up saying incorrectly that one is about nutrition and the othert is about
        /// aiming"*, and on what should be there instead: *"sterp by step instructions how to use
        /// the journal but not wordy keep it very concise asnd to the point"*.
        ///
        /// **Four steps and a stop, because the owner set the ceiling.** The keyed string carries
        /// the whole block; nothing is composed here, so a translator moves one entry rather than
        /// four fragments and the order of the steps cannot be lost in concatenation.
        ///
        /// **This is only ever read for a company-issued book.** `RimroomsRecordBook` guards the
        /// call, and the guard is the same `companyIssued` flag the label uses, so the card and
        /// the name can never disagree about which book this is.
        /// </summary>
        public string CompanyDescription
        {
            get { return "RR_Evidence_CompanyBookDesc".Translate().ToString(); }
        }

        /// <summary>
        /// Forget the quest this book served.
        ///
        /// Called when the corporation collects it, immediately before it stops existing, so nothing
        /// can ever find a half-collected book. **Deliberately not called when a quest is cancelled:**
        /// a book the branch still holds is still the branch's, and un-stamping it would silently
        /// turn a deliverable into an ordinary volume the player then has to re-issue.
        /// </summary>
        public void ClearQuestStamp()
        {
            stampedQuestId = null;
            stampedWriteUpCount = 0;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref bindingSchema, "rr_evidenceBindingSchema", 1);
            Scribe_Values.Look(ref evidenceId, "rr_evidenceId");
            Scribe_Values.Look(ref carrierLoadId, "rr_carrierLoadId");
            Scribe_Values.Look(ref companyIssued, "rr_companyIssued", false);
            // Additive. An unstamped book loads with an empty id and a zero count, which is exactly
            // what a book nobody has written in yet is.
            Scribe_Values.Look(ref stampedQuestId, "rr_stampedQuestId");
            Scribe_Values.Look(ref stampedWriteUpCount, "rr_stampedWriteUpCount", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && bindingSchema == 1 && IsCompanyCarrier(parent) &&
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
            // **THE INSTRUCTIONS COME BEFORE THE BINDING GUARD, AND THAT ORDER IS THE WHOLE POINT.**
            //
            // Owner, 2026-10-06: *"with a pawn click actions with sterp by step instructions how to
            // use the journal"*. The one state a player actually starts holding is a **blank**
            // company book, which has no evidence binding at all -- so an option added below the
            // `HasValidBinding` guard would be invisible on exactly the book that needs explaining.
            // That is the same fault `CompInspectStringExtra` carried until 0.12.9x, where the early
            // return meant the only state with no guidance was the first one anybody meets.
            //
            // Shown on a company-issued book whether bound or not, and never on an ordinary novel.
            if (companyIssued && selPawn != null && selPawn.Faction == Faction.OfPlayer
                && parent.Spawned && selPawn.Map == parent.Map
                && !parent.Position.Fogged(parent.Map))
            {
                yield return new FloatMenuOption("RR_UI_JournalHowTo".Translate(), delegate
                {
                    Find.WindowStack.Add(new Dialog_MessageBox(
                        "RR_Evidence_CompanyBookDesc".Translate(),
                        title: "RR_UI_JournalHowToTitle".Translate().ToString()));
                });
            }
            // **THE QUEST-BOUND ACTIONS, and each one exists only once its underlying action does.**
            // Owner, 2026-10-06: *"with a pawn click actions with sterp by step instructions how to
            // use the journal"*. The instruction block above is always there; these three appear
            // when they can actually be taken, because an option that explains why it is greyed out
            // is a sentence a player reads every time they right-click.
            if (companyIssued && !string.IsNullOrEmpty(stampedQuestId) && selPawn != null
                && selPawn.Faction == Faction.OfPlayer && parent.Spawned
                && selPawn.Map == parent.Map && !parent.Position.Fogged(parent.Map))
            {
                foreach (FloatMenuOption option in QuestBookOptions(selPawn)) { yield return option; }
            }
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
