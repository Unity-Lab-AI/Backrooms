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
            Find.GameInitData.mapSize = startDef.mapSize;
            Find.GameInitData.mapGeneratorDef = startDef.mapGenerator;
            // Native PrepForMapGen owns initial work priorities. Company role labels do not overwrite them.
        }

        public override void PostGameStart()
        {
            base.PostGameStart();
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

        // An explicit recovery command may retry only branch registration, never physical grants.
        public CompanyActionResult TryInitializeExistingHeadquarters(Map map)
        {
            HeadquartersSetupComponent receipt = map == null ? null : map.GetComponent<HeadquartersSetupComponent>();
            if (startDef == null || receipt == null || receipt.startDefName != startDef.defName || !receipt.setupComplete)
            {
                return CompanyActionResult.Refused(receipt == null ? "RR_Start_MissingSetup" : receipt.failure ?? "RR_Start_MissingSetup");
            }
            if (receipt.branchInitialized) { return CompanyActionResult.Existing(); }
            if (receipt.receiptVersion != 1 && receipt.receiptVersion != 2)
            { return CompanyActionResult.Refused("RR_Setup_UnknownReceipt"); }
            // Schema-1 physical receipts predate the native-arrival journal and remain valid.
            if (receipt.receiptVersion == 2 && !receipt.arrivalComplete)
            { return CompanyActionResult.Refused(receipt.failure ?? "RR_Setup_ArrivalIncomplete"); }
            RimroomsCampaignComponent company = Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
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
                    ? new List<string>() : new List<string>(startDef.completedProjects)
            });
            if (!result.Success)
            {
                receipt.failure = result.MessageKey;
                return result;
            }
            receipt.branchInitialized = true;
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
