using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Scenario
{
    public sealed class ScenPart_RimroomsStart : ScenPart
    {
        public RimroomsStartDef startDef;

        public static ScenPart_RimroomsStart Current
        {
            get { return Find.Scenario == null ? null : Find.Scenario.AllParts.OfType<ScenPart_RimroomsStart>().FirstOrDefault(); }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref startDef, "rr_startDef");
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (startDef == null) { yield return "Rimrooms scenario has no startDef."; }
        }

        public override IEnumerable<Page> GetConfigPages()
        {
            // XML places this part after the native pawn page. EdB's next-page path also reaches it.
            yield return new Page_RimroomsCompanySetup();
        }

        public override void PreMapGenerate()
        {
            base.PreMapGenerate();
            if (startDef == null || Find.GameInitData == null) { throw new InvalidOperationException("[Rimrooms] Missing scenario start data."); }
            string error = startDef.ConfigErrors().FirstOrDefault();
            if (error != null) { throw new InvalidOperationException("[Rimrooms] " + error); }
            List<Pawn> staff;
            List<string> roles;
            string refusal;
            if (!TryGetStaff(startDef, Find.GameInitData.startingAndOptionalPawns, out staff, out roles, out refusal))
            { throw new InvalidOperationException("[Rimrooms] " + refusal); }
            if (Verse.Current.Game.GetComponent<RimroomsCampaignComponent>().HasBranch)
            { throw new InvalidOperationException("[Rimrooms] Refused duplicate company startup."); }
            // The map size is the PLAYER'S choice, made at world setup, and the tile they
            // pick is where this facility is generated. Forcing it here is what produced the
            // owner's 2026-09-30 report: *"not the map i chose ... a super micro blocked in
            // area"*. The layout is offset onto their map instead; see HeadquartersLayout.
            // **The map generator is not ours.** Owner direction, 2026-09-30, after
            // reporting bare dirt and no vegetation on a tile chosen with Map Preview.
            //
            // This line used to read:
            //     Find.GameInitData.mapGeneratorDef = startDef.mapGenerator;
            // and it replaced Core's `Base_Player` -- elevation, fertility, biome terrain,
            // caves, rocks, plants, animals, ruins, rivers, roads and the DLC steps -- with a
            // four-step generator of ours. The result was flat Soil with a building on it, and
            // **Map Preview simulates the real generator**, so the preview a player rerolled
            // against was a picture of a map this mod then discarded.
            //
            // Core generates the tile now, at the size the player picked, and the facility is
            // added onto it by two gen steps patched into `Base_Player`.
            // Native PrepForMapGen owns initial work priorities. Company role labels do not overwrite them.
        }

        public override void PostGameStart()
        {
            base.PostGameStart();
            // **Said before anything else, because a player with no supplies needs telling and
            // the branch initialising successfully would otherwise bury it.** Owner: *"they need
            // to properly spawn in with starting goods"* / *"my preparecarfully mod food did not
            // appear"*. This reports; it never blocks a start.
            ReportGrantShortfall(Verse.Current.Game.CurrentMap);
            CompanyActionResult result = TryInitializeExistingHeadquarters(Verse.Current.Game.CurrentMap);
            if (!result.Success) { ShowStartFailure(result.MessageKey); }
            else
            {
                LongEventHandler.ExecuteWhenFinished(delegate
                {
                    if (Verse.Current.ProgramState == ProgramState.Playing)
                    { DefDatabase<MainButtonDef>.GetNamedSilentFail("RR_Operations")?.Worker.InterfaceTryActivate(); }
                });
            }
        }

        /// <summary>
        /// Tells the player what the scenario promised and what actually arrived, when the two
        /// do not match.
        ///
        /// ## Why a report rather than a fix
        ///
        /// The queue row is explicit — *"no fix was written on a hunch"* — and four candidate
        /// causes were eliminated against the installed game rather than guessed at. See
        /// <see cref="HeadquartersSetupComponent.promisedGrants"/> for the list and the evidence.
        /// What is left needs a launch, and the owner's own second report names the likely
        /// quarter: *"my preparecarfully mod food did not appear"*, which is the same
        /// `PlayerStartingThings()` enumeration.
        ///
        /// **So this turns the next launch from a repeat of the question into an answer.** A
        /// player who starts with nothing currently has to sweep nine thousand cells to find out;
        /// this says it on the letter stack, with both lists.
        ///
        /// ## It never blocks a start, and it never cries wolf
        ///
        /// Silent unless the promise is non-empty **and** nothing was delivered. A partial
        /// delivery is not reported, because the labels are human text and the deliveries are
        /// defNames: comparing them item by item would need a mapping this deliberately does not
        /// build, and a false alarm on a working start is worse than no report. **Nothing arriving
        /// at all is unambiguous**, and it is the case the owner actually hit.
        /// </summary>
        private static void ReportGrantShortfall(Map map)
        {
            HeadquartersSetupComponent receipt = map == null
                ? null : map.GetComponent<HeadquartersSetupComponent>();
            if (receipt == null) { return; }
            if (receipt.promisedGrants == null || receipt.promisedGrants.Count == 0) { return; }
            if (receipt.deliveredGrants != null && receipt.deliveredGrants.Count > 0) { return; }

            string promised = string.Join(", ", receipt.promisedGrants.ToArray());
            Log.Error("[Rimrooms][Scenario] The scenario promised starting goods and none "
                      + "arrived. Promised: " + promised);
            Find.LetterStack.ReceiveLetter(
                "RR_Start_GrantsMissingLabel".Translate(),
                "RR_Start_GrantsMissingText".Translate(promised),
                LetterDefOf.NegativeEvent);
        }

        // An explicit recovery command may retry only branch registration, never physical grants.
        public CompanyActionResult TryInitializeExistingHeadquarters(Map map)
        {
            HeadquartersSetupComponent receipt = map == null ? null : map.GetComponent<HeadquartersSetupComponent>();
            if (startDef == null || receipt == null || receipt.startDefName != startDef.defName || !receipt.setupComplete)
            {
                return CompanyActionResult.Refused(receipt == null ? "RR_Start_MissingSetup" : receipt.failure ?? "RR_Start_MissingSetup");
            }
            if (receipt.branchInitialized && receipt.openingComplete) { return CompanyActionResult.Existing(); }
            RimroomsCampaignComponent company = Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            // The branch exists and only the opening failed: retry the opening alone.
            if (receipt.branchInitialized) { return FinishOpening(receipt, company, map, CompanyActionResult.Applied()); }
            if (receipt.receiptVersion != 1 && receipt.receiptVersion != 2)
            { return CompanyActionResult.Refused("RR_Setup_UnknownReceipt"); }
            // Schema-1 physical receipts predate the native-arrival journal and remain valid.
            if (receipt.receiptVersion == 2 && !receipt.arrivalComplete)
            { return CompanyActionResult.Refused(receipt.failure ?? "RR_Setup_ArrivalIncomplete"); }
            CompanyActionResult result = company.InitializeBranch(new BranchStartRequest
            {
                ScenarioId = startDef.scenarioId,
                ScenarioVersion = startDef.scenarioVersion,
                CompanyName = Verse.Current.Game.GetComponent<RimroomsStartupComponent>()?.CompanyName,
                CampaignSeed = Find.World.info.Seed,
                Headquarters = map,
                Staff = new List<Pawn>(receipt.staff),
                StaffRoles = new List<string>(receipt.staffRoles),
                InitialFundingUsd = startDef.initialFundingUsd,
                DailyWageUsd = startDef.dailyWageUsd,
                DailyOverheadUsd = startDef.dailyOverheadUsd,
                SurveyRewardUsd = startDef.surveyRewardUsd,
                SurveyBonusUsd = startDef.surveyBonusUsd,
                CompletedProjects = startDef.completedProjects == null
                    ? new List<string>() : new List<string>(startDef.completedProjects),
                BeginsInCorporationContact = startDef.beginsInCorporationContact
            });
            if (!result.Success)
            {
                receipt.failure = result.MessageKey;
                return result;
            }
            receipt.branchInitialized = true;
            receipt.openingComplete = false;
            receipt.failure = null;
            return FinishOpening(receipt, company, map, result);
        }

        /// <summary>
        /// The solo/group opening, after the branch exists and before the welcome letter: it
        /// needs a live campaign to mint a coordinate against, and the player should not be
        /// told they have arrived until they are actually where they start. Recorded as done
        /// only once it succeeds, so a failure leaves it retryable.
        /// </summary>
        private CompanyActionResult FinishOpening(HeadquartersSetupComponent receipt,
            RimroomsCampaignComponent company, Map map, CompanyActionResult result)
        {
            string openingFailure = SoloGroupOpening.Open(startDef, company, map, ref receipt.openingCoordinateId);
            if (openingFailure != null)
            {
                receipt.failure = openingFailure;
                return CompanyActionResult.Refused(openingFailure);
            }
            receipt.openingComplete = true;
            receipt.failure = null;
            SetStartingRelations();
            Find.LetterStack.ReceiveLetter("RR_Start_WelcomeTitle".Translate(), "RR_Setup_Welcome".Translate(), LetterDefOf.NeutralEvent);
            return result;
        }

        private static void ShowStartFailure(string reason)
        {
            Find.LetterStack.ReceiveLetter("RR_Start_FailedTitle".Translate(),
                "RR_Start_Failed".Translate(reason.Translate()), LetterDefOf.NegativeEvent);
        }

        private static void SetStartingRelations()
        {
            Faction player = Faction.OfPlayer;
            foreach (Faction faction in Find.FactionManager.AllFactionsListForReading)
            {
                if (faction == player || faction.Hidden || faction.def.permanentEnemy || faction.defeated ||
                    !faction.def.humanlikeFaction || !faction.HasGoodwill || !player.HasGoodwill) { continue; }
                int delta = -faction.GoodwillWith(player);
                if (delta != 0) { faction.TryAffectGoodwillWith(player, delta, false, false); }
                if (faction.RelationKindWith(player) != FactionRelationKind.Neutral)
                { Log.Warning("[Rimrooms][Scenario] Native faction restrictions preserved for " + faction.GetUniqueLoadID()); }
            }
        }

        internal static bool TryGetStaff(RimroomsStartDef start, IEnumerable<Pawn> candidates,
            out List<Pawn> staff, out List<string> roles, out string refusal)
        {
            staff = new List<Pawn>();
            roles = new List<string>();
            refusal = null;
            RimroomsStartupComponent setup = Verse.Current.Game?.GetComponent<RimroomsStartupComponent>();
            if (setup != null && setup.TryRead(start, out staff, out roles) &&
                candidates != null && staff.SequenceEqual(candidates)) { return true; }
            refusal = "RR_Setup_Unaccepted".Translate();
            return false;
        }
    }

    public sealed class Page_ConfigureRimroomsStaff : Page_ConfigureStartingPawns
    {
        // Kept for legacy ScenPartDef resolution; new starts use the native page plus final review.
    }
}
