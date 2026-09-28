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
            // PrepForMapGen assigned native work priorities before this hook.
            for (int i = 0; i < staff.Count; i++)
            {
                foreach (WorkTypeDef work in startDef.roles[i].workTypes)
                { staff[i].workSettings.SetPriority(work, 2); }
            }
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
            RimroomsCampaignComponent company = Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            CompanyActionResult result = company.InitializeBranch(new BranchStartRequest
            {
                ScenarioId = startDef.scenarioId,
                ScenarioVersion = startDef.scenarioVersion,
                CampaignSeed = Find.World.info.Seed,
                Headquarters = map,
                Staff = new List<Pawn>(receipt.staff),
                StaffRoles = new List<string>(receipt.staffRoles),
                InitialFundingUsd = startDef.initialFundingUsd,
                DailyWageUsd = startDef.dailyWageUsd,
                DailyOverheadUsd = startDef.dailyOverheadUsd,
                SurveyRewardUsd = startDef.surveyRewardUsd,
                SurveyBonusUsd = startDef.surveyBonusUsd
            });
            if (!result.Success)
            {
                receipt.failure = result.MessageKey;
                return result;
            }
            receipt.branchInitialized = true;
            receipt.failure = null;
            SetStartingRelations();
            Find.LetterStack.ReceiveLetter("RR_Start_WelcomeTitle".Translate(), "RR_Start_Welcome".Translate(), LetterDefOf.NeutralEvent);
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
            List<Pawn> selected = candidates == null ? new List<Pawn>() : candidates.Take(5).ToList();
            if (start == null || start.roles == null || start.roles.Count != 5 || selected.Count != 5 || selected.Distinct().Count() != 5)
            { refusal = "RR_Start_RosterCount".Translate(); return false; }
            if (start.roles.Any(r => r == null || r.kind == null || r.skills == null || r.workTypes == null))
            { refusal = "RR_Start_MissingSetup".Translate(); return false; }
            foreach (RimroomsStaffRole role in start.roles)
            {
                Pawn pawn = null;
                foreach (Pawn candidate in selected)
                {
                    if (candidate != null && candidate.kindDef == role.kind && !staff.Contains(candidate))
                    { pawn = candidate; break; }
                }
                if (pawn == null || pawn.Dead || pawn.Downed || pawn.skills == null || pawn.workSettings == null ||
                    !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Moving) ||
                    !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) ||
                    (role.mustFight && pawn.WorkTagIsDisabled(WorkTags.Violent)) ||
                    role.workTypes.Any(w => w == null || pawn.WorkTypeIsDisabled(w)) ||
                    role.skills.Any(s => s == null || s.skill == null || pawn.skills.GetSkill(s.skill).TotallyDisabled || !s.PawnSatisfies(pawn)))
                {
                    refusal = "RR_Start_RosterCapability".Translate(role.kind == null ? role.id : role.kind.LabelCap.ToString());
                    return false;
                }
                staff.Add(pawn);
                roles.Add(role.id);
            }
            return true;
        }
    }

    public sealed class Page_ConfigureRimroomsStaff : Page_ConfigureStartingPawns
    {
        protected override bool CanDoNext()
        {
            if (!base.CanDoNext()) { return false; }
            ScenPart_RimroomsStart part = ScenPart_RimroomsStart.Current;
            List<Pawn> staff;
            List<string> roles;
            string refusal = null;
            if (part == null || !ScenPart_RimroomsStart.TryGetStaff(part.startDef,
                Find.GameInitData.startingAndOptionalPawns, out staff, out roles, out refusal))
            {
                Messages.Message(part == null ? "RR_Start_MissingSetup".Translate().ToString() : refusal,
                    MessageTypeDefOf.RejectInput, false);
                return false;
            }
            return true;
        }
    }
}
