using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The clean-up team. The parent corporation will not let a branch it has on its books die.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"the mega mother corp is greedy and will basic
    /// do anything and put up with anything to make sure you succssed to the point of sending
    /// clean up teams to your base with all access passses to wipe the facitly of all hostals and
    /// requisition a new basic team supplies drops like a fresh start of sorts so that facilities
    /// never die, this is liken the store and solo/group scenerios once they reach contact with
    /// the corporation"*.
    ///
    /// And the scoping direction that followed: *"clena up tema is only once u are in
    /// communication and working with the corporation"*.
    ///
    /// ## Why this is deterministic and not an incident
    ///
    /// Owner decision at the storyteller fork, verbatim: ***"Both - guaranteed floor, storyteller
    /// flavour"***. This is the floor half, and it lives here rather than in an `IncidentDef`
    /// **because a promise must not be at the mercy of a dice roll**. A storyteller decides
    /// whether and when to fire an incident. *"Facilities never die"* admits neither question.
    ///
    /// The other half — lighter, world-facing events the player's own storyteller paces — is a
    /// separate surface and does not belong in the same code path as a guarantee.
    ///
    /// ## Greed is the mechanism, not a contradiction
    ///
    /// An investor protecting an investment does not walk away from it for being slow, or for
    /// failing. `docs/CAMPAIGN_CHART.md` §4.3. There is deliberately **no cap** on how many times
    /// this fires and **no escalating penalty**: the corporation *"will put up with anything"*,
    /// and a rescue that gets stingier is a rescue with a deadline on it wearing a different hat.
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>How many times the corporation has stepped in. A record, never a limit.</summary>
        private int reliefCount;

        /// <summary>
        /// When the last relief landed. **A timestamp, which is history rather than a countdown**
        /// (`docs/CAMPAIGN_CHART.md` §1.1). Nothing compares it against a limit, and nothing
        /// becomes unavailable as it ages.
        /// </summary>
        private int lastReliefTick = -1;

        /// <summary>Roles the relief team arrives with, one each. The order is the order they land in.</summary>
        private static readonly string[] ReliefRoles =
        { "operations", "engineering", "medical_logistics", "security", "research" };

        /// <summary>
        /// The kind each relief role is generated from.
        ///
        /// **These five `PawnKindDef`s already existed and were read by nothing.** They were
        /// authored with exactly these five role profiles, loaded and validated every run, and no
        /// source file mentioned one. Invariant 131, owner verbatim: *"make sure shit isnt unused
        /// it was put there for a reason"* — **a def nobody wired is a job nobody finished.**
        /// This is the job they were written for.
        /// </summary>
        private static string ReliefKindFor(string role)
        {
            switch (role)
            {
                case "research": return "RR_ResearchStaff";
                case "engineering": return "RR_EngineeringStaff";
                case "security": return "RR_SecurityStaff";
                case "medical_logistics": return "RR_MedicalLogisticsStaff";
                default: return "RR_OperationsStaff";
            }
        }

        /// <summary>
        /// The clean-up team drops the corporation's crate at **full scale**.
        ///
        /// The table itself lives in <see cref="CompanySupplyDrop"/> because the unsolicited
        /// courier drops the same crate smaller. Same corporation, same warehouse, one table.
        /// </summary>
        private const float ReliefSupplyScale = 1f;

        internal void ExposeFacilityRelief()
        {
            Scribe_Values.Look(ref reliefCount, "rr_reliefCount", 0);
            Scribe_Values.Look(ref lastReliefTick, "rr_lastReliefTick", -1);
        }

        /// <summary>How many times the corporation has had to step in.</summary>
        public int FacilityReliefCount { get { return reliefCount; } }

        /// <summary>
        /// Whether a single employed staff member is still alive **anywhere**.
        ///
        /// **Anywhere matters.** A crew standing in a Backrooms coordinate is alive and the
        /// facility is not dead, so a player who has taken everybody through a gate must never
        /// come home to a relief team and a duplicate payroll. This deliberately does not ask
        /// where the pawn is, only whether it exists.
        ///
        /// Downed is also not dead. A branch whose staff are all unconscious is in trouble, not
        /// gone, and replacing people who are going to stand back up would be the corporation
        /// paying twice for the same jobs.
        ///
        /// **That reasoning holds for the Store and the Solo/Group branches and the owner has
        /// overruled it for the laboratory.** Owner, 2026-10-01: *"a the company clear squad when
        /// all pawns incompacitated"*, and on the people it lands on: *"the downed: No
        /// Witnesses"*. The laboratory's trigger is <c>AnyCapableStaff</c> in
        /// <c>CompanyClearSquad.cs</c>, which counts downed as lost; this one is unchanged and is
        /// still what the other two scenarios use. The comment is scoped rather than deleted
        /// because it is still a true statement about the path it guards.
        /// </summary>
        private bool AnyLivingStaff()
        {
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed) { continue; }
                Pawn pawn = member.pawn;
                if (pawn != null && !pawn.Dead && !pawn.Destroyed && !pawn.Discarded) { return true; }
            }
            return false;
        }

        /// <summary>
        /// Checked on the company's own cadence. Cheap in the overwhelming majority of calls: the
        /// contact flag is a bool and the staff scan stops at the first living employee.
        /// </summary>
        internal void TickFacilityRelief()
        {
            if (!corporationContact) { return; }
            Map map = headquarters;
            if (map == null || !Find.Maps.Contains(map)) { return; }
            // **The laboratory takes a different path entirely and never reaches the relief.**
            // Owner: *"this only happens for the lab secnerio for now we will figure out how to
            // impliment it in other scenreios later"*. Returning here is what keeps that scoping
            // real: the squad handles the dead as well as the downed, so running both would land
            // eight people and charge twenty-five million for three of them.
            if (IsLaboratoryBranch) { TickClearSquad(map); return; }
            if (AnyLivingStaff()) { return; }
            try { RunFacilityRelief(map); }
            catch (Exception error)
            {
                // A rescue that throws must not take the save with it. The condition stays true,
                // so the next company tick tries again rather than leaving the branch dead with
                // a guarantee that silently stopped applying.
                Log.Warning("[Rimrooms] facility relief could not complete: " + error);
            }
        }

        private void RunFacilityRelief(Map map)
        {
            int now = Find.TickManager.TicksGame;
            int cleared = ClearHostiles(map);

            IntVec3 center = ReliefDropCell(map);
            List<Thing> payload = new List<Thing>();
            List<string> arrived = new List<string>();

            for (int index = 0; index < ReliefRoles.Length; index++)
            {
                string role = ReliefRoles[index];
                Pawn pawn = GenerateReliefStaff(role);
                if (pawn == null) { continue; }
                payload.Add(pawn);
                arrived.Add(role);
            }

            // Nobody arrived, so nothing is recorded and nothing is spent. The branch is still
            // collapsed and the next tick tries again. Claiming a rescue that put no one on the
            // map would be worse than the failure.
            if (payload.Count == 0) { return; }

            CompanySupplyDrop.Fill(payload, ReliefSupplyScale);

            reliefCount++;
            lastReliefTick = now;

            DropPodUtility.DropThingsNear(center, map, payload, 110, false, false, true,
                forbid: false);

            for (int index = 0; index < arrived.Count; index++)
            {
                Pawn pawn = payload[index] as Pawn;
                if (pawn == null) { continue; }
                RegisterReliefStaff(pawn, arrived[index], now);
            }

            // Core sets this the moment the last free colonist dies and posts a game-over letter
            // 400 ticks later. `CheckOrUpdateGameOver` clears it again as soon as any map holds a
            // free colonist, so landing a team is usually enough on its own — but the field is
            // public, the relief is a guarantee, and relying on Core to notice in time is not
            // the same thing as making sure.
            if (Find.GameEnder != null) { Find.GameEnder.gameEnding = false; }

            RecordEvent("RR_Event_FacilityRelief", BranchId);
            Find.LetterStack.ReceiveLetter(
                "RR_Relief_Title".Translate(),
                "RR_Relief_Body".Translate(arrived.Count, cleared, CompanyName),
                LetterDefOf.PositiveEvent, new TargetInfo(center, map));
        }

        /// <summary>
        /// *"all access passses to wipe the facitly of all hostals"*.
        ///
        /// Removed rather than killed. A clean-up team that left forty corpses on the floor of a
        /// facility with nobody in it to haul them has not cleaned anything up, and the rot, the
        /// filth and the mood hit would land on the replacement crew who were not there for it.
        ///
        /// **Only things actually hostile to the player**, and never the player's own — a
        /// colonist, a player animal or a downed friendly is not swept up by this.
        /// </summary>
        private static int ClearHostiles(Map map)
        {
            if (map == null || map.mapPawns == null) { return 0; }
            List<Pawn> doomed = new List<Pawn>();
            IReadOnlyList<Pawn> spawned = map.mapPawns.AllPawnsSpawned;
            for (int index = 0; index < spawned.Count; index++)
            {
                Pawn pawn = spawned[index];
                if (pawn == null || pawn.Destroyed || pawn.Dead) { continue; }
                if (pawn.Faction == Faction.OfPlayer) { continue; }
                if (!pawn.HostileTo(Faction.OfPlayer)) { continue; }
                doomed.Add(pawn);
            }
            for (int index = 0; index < doomed.Count; index++)
            {
                Pawn pawn = doomed[index];
                if (pawn.Destroyed) { continue; }
                pawn.Destroy(DestroyMode.Vanish);
            }
            return doomed.Count;
        }

        private static IntVec3 ReliefDropCell(Map map)
        {
            try
            {
                IntVec3 spot = DropCellFinder.TradeDropSpot(map);
                if (spot.IsValid && spot.InBounds(map)) { return spot; }
            }
            catch (Exception)
            {
                // A map with no trade spot is still a map the relief has to reach.
            }
            return map.Center;
        }

        private static Pawn GenerateReliefStaff(string role)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(ReliefKindFor(role));
            // Never a throwing lookup, and never a silent substitution either: if the branch's own
            // staff kind is missing, Core's ordinary colonist is a person who can do the job.
            if (kind == null) { kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Colonist"); }
            if (kind == null) { return null; }
            try
            {
                return PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, Faction.OfPlayer,
                    PawnGenerationContext.NonPlayer, -1, forceGenerateNewPawn: true, allowDead: false,
                    allowDowned: false, canGeneratePawnRelations: false, mustBeCapableOfViolence: false,
                    forceAddFreeWarmLayerIfNeeded: true, allowGay: true, allowFood: true,
                    developmentalStages: DevelopmentalStage.Adult));
            }
            catch (Exception error)
            {
                Log.Warning("[Rimrooms] could not generate relief staff for " + role + ": " + error);
                return null;
            }
        }

        /// <summary>
        /// Puts a relief arrival on the books.
        ///
        /// **Deliberately not routed through the hiring pipeline.** That path exists to reconcile
        /// an onboarding charge against a saved quote, and there is no charge here: the parent
        /// corporation is paying for its own rescue. Sending a free arrival through a function
        /// whose whole job is matching receipts would mean inventing a receipt to satisfy it.
        ///
        /// They are ordinary employees from the moment they land, on the ordinary wage, and the
        /// next payroll bills for them like anybody else. The rescue is free; keeping the people
        /// afterwards is not.
        /// </summary>
        private void RegisterReliefStaff(Pawn pawn, string role, int now)
        {
            if (pawn == null || pawn.Dead || pawn.Destroyed) { return; }
            string id = branchId + ":relief:" + reliefCount + ":" + role;
            for (int index = 0; index < staff.Count; index++)
            {
                if (staff[index] != null && staff[index].id == id) { return; }
            }
            staff.Add(new StaffRecord
            {
                id = id,
                pawn = pawn,
                pawnLoadId = pawn.GetUniqueLoadID(),
                nameAtHire = pawn.LabelShortCap.ToString(),
                role = Personnel.PersonnelRoles.Valid(role) ? role : "operations",
                dailyWageUsd = ReliefDailyWageUsd(),
                hiredTick = now,
                employed = true,
            });
        }

        /// <summary>The ordinary company wage, read from the hiring policy rather than restated.</summary>
        private static long ReliefDailyWageUsd()
        {
            List<Personnel.HiringPolicyDef> policies =
                DefDatabase<Personnel.HiringPolicyDef>.AllDefsListForReading;
            for (int index = 0; index < policies.Count; index++)
            {
                if (policies[index] != null && policies[index].Valid) { return policies[index].dailyWageUsd; }
            }
            return 5000L;
        }
    }
}
