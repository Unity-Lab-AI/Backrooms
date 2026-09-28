using Verse;

namespace RimroomsAsyncIndustries.Personnel
{
    // Append new values; never reorder saved enum values.
    public enum ApplicantStatus { Queued = 0, Offered = 1, GenerationFailed = 2, Hiring = 3, Hired = 4,
        Releasing = 5, Declined = 6, Expired = 7, Cancelled = 8, Unavailable = 9, Dismissed = 10 }
    public enum ApplicantRelease { None = 0, Declined = 1, Expired = 2, Cancelled = 3, InvalidCandidate = 4 }

    public sealed class ApplicantRecord : IExposable
    {
        internal string id;
        internal Pawn pawn;
        internal string pawnId;
        internal string name = "";
        internal string kindDefName;
        internal string suggestedRole;
        internal string selectedRole;
        internal string policyDefName;
        internal long onboardingUsd;
        internal long dailyWageUsd;
        internal int createdTick;
        internal int expiresTick;
        internal ApplicantStatus status;
        internal string failureKey;
        internal Map hiringMap;
        internal IntVec3 arrivalCell = IntVec3.Invalid;
        internal int acceptedTick;
        internal bool charged;
        internal bool arrivalAttempted;
        internal bool arrivalFailedOffsite;
        internal bool everArrived;
        internal bool recruitStarted;
        internal bool recruited;
        internal bool registered;
        internal bool refunded;
        internal ApplicantRelease release;
        internal bool worldReleaseStarted;

        public string Id { get { return id; } }
        public Pawn Pawn { get { return pawn; } }
        public string Name { get { return pawn == null ? (string.IsNullOrEmpty(name) ? "RR_Personnel_Unnamed".Translate().ToString() : name) : pawn.LabelShortCap.ToString(); } }
        public string PawnId { get { return pawnId; } }
        public string SuggestedRole { get { return suggestedRole; } }
        public string SelectedRole { get { return selectedRole; } }
        public long OnboardingUsd { get { return onboardingUsd; } }
        public long DailyWageUsd { get { return dailyWageUsd; } }
        public int ExpiresTick { get { return expiresTick; } }
        public ApplicantStatus Status { get { return status; } }
        public string FailureKey { get { return failureKey; } }
        public bool Charged { get { return charged; } }
        public bool ArrivalAttempted { get { return arrivalAttempted; } }
        public bool CanCancelBeforeArrival { get { return status == ApplicantStatus.Hiring && !everArrived && !recruitStarted &&
            !registered && (!arrivalAttempted || arrivalFailedOffsite); } }
        public bool Registered { get { return registered; } }
        public bool Refunded { get { return refunded; } }
        public bool IsOpen { get { return status == ApplicantStatus.Queued || status == ApplicantStatus.Offered ||
            status == ApplicantStatus.Hiring || status == ApplicantStatus.Releasing || status == ApplicantStatus.Unavailable; } }
        internal string HireId { get { return id + ":hire:1"; } }
        internal string ChargeId { get { return HireId + ":onboarding"; } }
        internal string RefundId { get { return HireId + ":refund"; } }
        internal string StaffId { get { return HireId + ":staff"; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "id");
            Scribe_References.Look(ref pawn, "pawn");
            Scribe_Values.Look(ref pawnId, "pawnId");
            Scribe_Values.Look(ref name, "name", "");
            Scribe_Values.Look(ref kindDefName, "kindDefName");
            Scribe_Values.Look(ref suggestedRole, "suggestedRole");
            Scribe_Values.Look(ref selectedRole, "selectedRole");
            Scribe_Values.Look(ref policyDefName, "policyDefName");
            Scribe_Values.Look(ref onboardingUsd, "onboardingUsd");
            Scribe_Values.Look(ref dailyWageUsd, "dailyWageUsd");
            Scribe_Values.Look(ref createdTick, "createdTick");
            Scribe_Values.Look(ref expiresTick, "expiresTick");
            Scribe_Values.Look(ref status, "status");
            Scribe_Values.Look(ref failureKey, "failureKey");
            Scribe_References.Look(ref hiringMap, "hiringMap");
            Scribe_Values.Look(ref arrivalCell, "arrivalCell", IntVec3.Invalid);
            Scribe_Values.Look(ref acceptedTick, "acceptedTick");
            Scribe_Values.Look(ref charged, "charged");
            Scribe_Values.Look(ref arrivalAttempted, "arrivalAttempted");
            Scribe_Values.Look(ref arrivalFailedOffsite, "arrivalFailedOffsite");
            Scribe_Values.Look(ref everArrived, "everArrived");
            Scribe_Values.Look(ref recruitStarted, "recruitStarted");
            Scribe_Values.Look(ref recruited, "recruited");
            Scribe_Values.Look(ref registered, "registered");
            Scribe_Values.Look(ref refunded, "refunded");
            Scribe_Values.Look(ref release, "release");
            Scribe_Values.Look(ref worldReleaseStarted, "worldReleaseStarted");
        }
    }
}
