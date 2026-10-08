using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// Where a request stands with this branch.
    ///
    /// **There is no Expired and there never will be.** `docs/CAMPAIGN_CHART.md` §1.1: *"the only
    /// clock is the gate"*. A request that nobody has got round to is still Offered, for as long
    /// as the save lasts.
    /// </summary>
    public enum RequestStatus
    {
        /// <summary>On the table. The branch has not said yes.</summary>
        Offered = 0,

        /// <summary>Taken on. The routes are live and the branch is being watched.</summary>
        Accepted = 1,

        /// <summary>A route came true and the company paid.</summary>
        Completed = 2,

        /// <summary>
        /// The player said no.
        ///
        /// **Chart §4.1: the player may cancel, the corporation may not.** A cancelled request
        /// counts as *resolved* for the purpose of whatever came after it, so cancelling one
        /// never strands the branch behind a prerequisite it can no longer satisfy. It pays
        /// nothing, and that is the whole cost.
        /// </summary>
        Cancelled = 3,
    }

    /// <summary>
    /// Where one route stood when the request was put on the table.
    ///
    /// **A job is measured from when you took it.** Without this, every check in this mod is
    /// absolute state — *"does the branch hold twenty meals"*, *"has it filed a route log"* — and
    /// absolute state is permanently true once true. That is right for a tutorial request asked
    /// **once**: if the branch already has a battery, request 1 completing immediately is correct,
    /// because the lesson is already learned. It is wrong for anything **repeatable**, where it
    /// would pay out the instant the player accepted.
    ///
    /// So a generated request records where each of its routes started, and asks for that much
    /// **more**. A tutorial request records zero and keeps asking absolutely.
    ///
    /// Keyed by label key rather than by list index, so a mod-list change that reorders or
    /// removes a route cannot silently shift every baseline onto the wrong one.
    /// </summary>
    public sealed class RouteBaseline : IExposable
    {
        internal string labelKey;
        internal int value;

        public string LabelKey { get { return labelKey; } }
        public int Value { get { return value; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref labelKey, "rr_labelKey");
            Scribe_Values.Look(ref value, "rr_value", 0);
        }
    }

    /// <summary>
    /// What this branch did about one corporation request.
    ///
    /// The def is the offer; this is the history. Keeping them apart is what lets the seven
    /// authored requests stay pure content while the save carries only what actually happened.
    /// </summary>
    public sealed class RequestRecord : IExposable
    {
        /// <summary>
        /// Where each route stood when this was offered. Empty means measure absolutely.
        ///
        /// **Saved**, unlike the satisfied-route list below, because it is not derivable from the
        /// world: once the branch has moved past the baseline there is nothing left to read it
        /// back from. Losing it would turn a half-finished job into a finished one.
        /// </summary>
        internal List<RouteBaseline> routeBaselines = new List<RouteBaseline>();

        /// <summary>Where one route started, or zero when this request measures absolutely.</summary>
        public int BaselineFor(string labelKey)
        {
            if (routeBaselines == null || string.IsNullOrEmpty(labelKey)) { return 0; }
            for (int index = 0; index < routeBaselines.Count; index++)
            {
                RouteBaseline baseline = routeBaselines[index];
                if (baseline != null && baseline.labelKey == labelKey) { return baseline.value; }
            }
            return 0;
        }

        internal string id;
        internal string requestDefName;
        internal RequestStatus status = RequestStatus.Offered;
        internal int offeredTick = -1;
        internal int acceptedTick = -1;
        internal int completedTick = -1;
        internal string settlementOperationId;
        internal string satisfiedRouteLabelKey;
        internal bool bonusPaid;

        /// <summary>
        /// Who was on the books the moment this was accepted.
        ///
        /// **A snapshot, per invariant 27**, because it decides money. The bonus asks whether
        /// everybody who was employed when the branch took the job is still employed and alive
        /// when it finishes, and reading that live would let a branch earn the bonus by firing
        /// the casualty.
        /// </summary>
        internal List<string> staffAtAcceptance = new List<string>();

        /// <summary>
        /// Which routes were true the last time the line was evaluated, by label key.
        ///
        /// **Deliberately not saved.** It is derived from the world and refreshed on the same
        /// tick that already evaluates every route, so saving it would be a second copy that can
        /// disagree with the first. The field initializer runs before `ExposeData` on load, so a
        /// loaded record starts empty and is correct again within four seconds.
        ///
        /// It exists so the card can show what is already done **without the pane scanning maps
        /// sixty times a second** — the readout and the rule read the same evaluation.
        /// </summary>
        internal List<string> satisfiedRouteLabelKeys = new List<string>();

        public IReadOnlyList<string> SatisfiedRouteLabelKeys { get { return satisfiedRouteLabelKeys; } }

        /// <summary>
        /// The write-up kinds already filed for this quest, by <see cref="RimroomsWriteUpDef"/>
        /// defName.
        ///
        /// **THIS IS THE AUTHORITY, AND THE BOOK CARRIES A COPY.** The owner chose *"Both, and they
        /// must agree"* when asked what the green light reads from, and the cost was named in the
        /// option before it was chosen: two things holding one truth is *"two derivations of one
        /// rule"*, the defect this project keeps meeting.
        ///
        /// So it is spent down to **one writer and two readers.** <see cref="FileWriteUp"/> is the
        /// only thing that ever adds to this list, and the job that calls it stamps the book in the
        /// same operation, record first. **A mismatch therefore cannot be produced by the mod
        /// working normally** — only a book from another branch, a hand-edited save, or damage. Each
        /// of those is something a player should be told about, which is what the amber state is for.
        ///
        /// **Saved**, unlike <see cref="satisfiedRouteLabelKeys"/> above, and the contrast is the
        /// rule rather than an inconsistency: a satisfied route is derived from the world and can be
        /// re-measured, while filed paperwork is a thing a pawn *did* and nothing in the world
        /// remembers it. Losing this would make a finished quest unfinished.
        ///
        /// A list of defNames rather than a count, because *which* paperwork is outstanding is what
        /// a pawn needs to pick its next job and what the ledger has to show. A count answers
        /// neither question.
        /// </summary>
        internal List<string> writeUpsFiled = new List<string>();

        /// <summary>What has been filed. Read-only to everything but <see cref="FileWriteUp"/>.</summary>
        public IReadOnlyList<string> WriteUpsFiled
        {
            get { return writeUpsFiled ?? (writeUpsFiled = new List<string>()); }
        }

        /// <summary>
        /// Record one filed write-up. **Idempotent, and the only writer.**
        ///
        /// Returns false when it was already filed, so a caller cannot double-count and a job
        /// resumed after a save that then finishes twice costs nothing. Same reasoning as
        /// `PostTransaction`'s operation id: a second attempt is not an error, it is a no-op.
        /// </summary>
        internal bool FileWriteUp(string writeUpDefName)
        {
            if (string.IsNullOrWhiteSpace(writeUpDefName)) { return false; }
            if (writeUpsFiled == null) { writeUpsFiled = new List<string>(); }
            if (writeUpsFiled.Contains(writeUpDefName)) { return false; }
            writeUpsFiled.Add(writeUpDefName);
            return true;
        }

        public string Id { get { return id; } }
        public string RequestDefName { get { return requestDefName; } }
        public RequestStatus Status { get { return status; } }
        public int OfferedTick { get { return offeredTick; } }
        public int AcceptedTick { get { return acceptedTick; } }
        public int CompletedTick { get { return completedTick; } }
        public string SatisfiedRouteLabelKey { get { return satisfiedRouteLabelKey; } }
        public bool BonusPaid { get { return bonusPaid; } }

        /// <summary>The offer this record is about, or null if the def is no longer loaded.</summary>
        public RimroomsRequestDef Definition
        {
            get
            {
                return string.IsNullOrEmpty(requestDefName) ? null
                    : DefDatabase<RimroomsRequestDef>.GetNamedSilentFail(requestDefName);
            }
        }

        /// <summary>Resolved either way: nothing downstream is waiting on it any more.</summary>
        public bool Resolved
        {
            get { return status == RequestStatus.Completed || status == RequestStatus.Cancelled; }
        }

        /// <summary>Still on the table or being worked. At most one of these exists at a time.</summary>
        public bool Open
        {
            get { return status == RequestStatus.Offered || status == RequestStatus.Accepted; }
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref requestDefName, "rr_requestDefName");
            Scribe_Values.Look(ref status, "rr_status", RequestStatus.Offered);
            Scribe_Values.Look(ref offeredTick, "rr_offeredTick", -1);
            Scribe_Values.Look(ref acceptedTick, "rr_acceptedTick", -1);
            Scribe_Values.Look(ref completedTick, "rr_completedTick", -1);
            Scribe_Values.Look(ref settlementOperationId, "rr_settlementOperationId");
            Scribe_Values.Look(ref satisfiedRouteLabelKey, "rr_satisfiedRouteLabelKey");
            Scribe_Values.Look(ref bonusPaid, "rr_bonusPaid", false);
            Scribe_Collections.Look(ref staffAtAcceptance, "rr_staffAtAcceptance", LookMode.Value);
            // Additive, and re-made on load rather than trusted. `Scribe_Collections` writes nothing
            // for an empty list, so a save written before this field existed loads it back as
            // **null** — and then every reader would have to remember that. One place remembers.
            Scribe_Collections.Look(ref writeUpsFiled, "rr_writeUpsFiled", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && writeUpsFiled == null)
            { writeUpsFiled = new List<string>(); }
            Scribe_Collections.Look(ref routeBaselines, "rr_routeBaselines", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && staffAtAcceptance == null)
            { staffAtAcceptance = new List<string>(); }
            if (Scribe.mode == LoadSaveMode.PostLoadInit && routeBaselines == null)
            { routeBaselines = new List<RouteBaseline>(); }
        }
    }

    /// <summary>
    /// The mission line: the corporation asking this branch for things, and noticing when it gets
    /// them.
    ///
    /// ## Why this file exists at all
    ///
    /// `RimroomsRequestDef` and `RequestRoutes` shipped in 0.11.1-dev and 0.11.2-dev as
    /// `docs/CAMPAIGN_CHART.md` §7 steps 4 and 5, and the build order recorded both as done.
    /// **They were read by nothing.** Seven requests, the whole tutorial line and the hinge,
    /// validated at def load and checked by two tools, and no player could ever see one. This is
    /// the half that was missing: the offer reaching somebody.
    ///
    /// ## What decides when an offer appears
    ///
    /// **Contact, then order, then prerequisites.** In that sequence, and every one of the three
    /// can refuse:
    ///
    /// * **Contact.** Owner direction for the solo/group start, verbatim: *"option three with
    ///   hints like i need to contact someone about this crazy shit"*. A corporation that has
    ///   never heard of these people does not send them work. Two of the three starts begin in
    ///   silence and the silence is the point.
    /// * **Order.** The tutorial line is *"fixed"* (chart §4.2) and teaches one system each, so
    ///   the next one waits until the open one is resolved. At most one is open at a time.
    /// * **Prerequisites.** Declared on the def, and satisfied by Completed **or Cancelled** — so
    ///   a player who refuses request 4 still gets request 5.
    ///
    /// **The tutorial line is deliberately NOT capability-filtered.** The owner's eligibility
    /// answer — *"filter picks the family, card never shrinks"* — is about **generated** requests
    /// after the hinge. Applying it here would let a fresh branch that cannot yet take two routes
    /// be offered nothing at all, for ever, which is the one failure a tutorial cannot have.
    ///
    /// ## What decides when one completes
    ///
    /// **Any one route coming true.** Not the route the player nominated, because they never
    /// nominate one: a request card shows the ways through and the company only cares that the
    /// work is done. That also means two routes are allowed to come true together, and the one
    /// recorded is the first in ordinal order so a save is reproducible.
    ///
    /// **Every route kind has its own check, and no two of them are the same question.** The pair
    /// most at risk was Document and Testify, which both name a log kind — they are split on the
    /// thing that actually differs: **Document is the paperwork and survives the witness dying;
    /// Testify is the person and survives the book burning.**
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        private List<RequestRecord> requests = new List<RequestRecord>();

        internal void ExposeRequests()
        {
            Scribe_Collections.Look(ref requests, "rr_requestLine", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && requests == null)
            { requests = new List<RequestRecord>(); }
        }

        public IReadOnlyList<RequestRecord> Requests { get { return requests; } }

        /// <summary>
        /// This branch's **most recent** history with one offer, or null if never offered.
        ///
        /// Most recent rather than first, because a **generated** family may be asked for more
        /// than once. A tutorial request is asked exactly once, so for those the distinction does
        /// not arise — and `proof-request-generation.py` asserts it cannot.
        /// </summary>
        public RequestRecord RequestFor(string defName)
        {
            if (string.IsNullOrEmpty(defName)) { return null; }
            for (int index = requests.Count - 1; index >= 0; index--)
            {
                RequestRecord record = requests[index];
                if (record != null && record.requestDefName == defName) { return record; }
            }
            return null;
        }

        /// <summary>
        /// The first request not yet finished — offered or accepted — or null.
        ///
        /// **It is no longer true that there is never more than one, and the change was the owner's
        /// direction.** See <see cref="OfferedRequest"/> and <see cref="AcceptedRequests"/>: a branch
        /// may hold any number of ACCEPTED jobs and is offered at most one at a time. This stays for
        /// the tutorial line, where one-at-a-time means one in either state.
        /// </summary>
        public RequestRecord OpenRequest
        {
            get
            {
                for (int index = 0; index < requests.Count; index++)
                {
                    RequestRecord record = requests[index];
                    if (record != null && record.Open) { return record; }
                }
                return null;
            }
        }

        /// <summary>
        /// The one request on the table awaiting an answer, or null.
        ///
        /// ## THE DEFECT THIS SPLIT REPAIRS, AND IT MADE TWO FEATURES UNREACHABLE
        ///
        /// **Owner direction, 2026-10-06, verbatim:** *"with ability to accept more than one quests
        /// at a time"*, and, about the write-up desks, *"u can have more than one to have more than
        /// one pawn doing it as u can have multiple quests going"*.
        ///
        /// **A branch could hold exactly one job, ever.** Both offer routines refused while
        /// <see cref="OpenRequest"/> was non-null, and `Open` is *offered **or** accepted* — so
        /// accepting a job stopped the company offering anything else until it was finished or
        /// cancelled. Nothing said so; the Requests pane simply never had a second thing in it.
        ///
        /// **So two shipped features were unreachable in play, not merely unused.** The paperwork
        /// ledger lists *every accepted quest* and could never list more than one. The parallel
        /// records desks — built in this same batch, with claims so two writers cannot take the
        /// same page — had nothing to be parallel about. A feature whose precondition is impossible
        /// is a feature nobody can report as broken, which is why this was found by reading the
        /// offer guard rather than by anybody playing.
        ///
        /// ## One OFFER at a time is still right, and that half is kept deliberately
        ///
        /// The tutorial teaches one system per step, and the offer routine's own comment says a
        /// second simultaneous offer *"would turn a tutorial that teaches one system per step into a
        /// list of chores"*. That reasoning is about **offers**, not about obligations: a player who
        /// has taken three jobs chose to. So the company asks for one answer at a time and never
        /// limits how many the branch is carrying.
        /// </summary>
        public RequestRecord OfferedRequest
        {
            get
            {
                for (int index = 0; index < requests.Count; index++)
                {
                    RequestRecord record = requests[index];
                    if (record != null && record.status == RequestStatus.Offered) { return record; }
                }
                return null;
            }
        }

        /// <summary>
        /// Every job the branch has taken on and not yet finished, in acceptance order.
        ///
        /// Acceptance order, because that is the order the paperwork ledger works through and the
        /// order a player remembers saying yes in.
        /// </summary>
        public List<RequestRecord> AcceptedRequests
        {
            get
            {
                var taken = new List<RequestRecord>();
                for (int index = 0; index < requests.Count; index++)
                {
                    RequestRecord record = requests[index];
                    if (record != null && record.status == RequestStatus.Accepted) { taken.Add(record); }
                }
                return taken;
            }
        }

        /// <summary>
        /// True once the branch is past the hinge.
        ///
        /// The hinge is the last thing the company asks for by name, so resolving it is what
        /// turns the line from a script into a campaign. **Cancelled counts**, because the hinge's
        /// own text says every choice is a success and refusing to answer is a choice.
        /// </summary>
        public bool PastTheHinge
        {
            get
            {
                List<RimroomsRequestDef> line = RimroomsRequestDef.TutorialLine();
                if (line.Count == 0) { return false; }
                RequestRecord record = RequestFor(line[line.Count - 1].defName);
                return record != null && record.Resolved;
            }
        }

        internal void TickRequestLine()
        {
            if (!CanOperate) { return; }
            CompleteSatisfiedRequests();
            OfferNextTutorialRequest();
            // The generated half. Refuses until the branch is past the hinge, so before then this
            // is a bool and a list walk. Both offer routines refuse while a request is open, so at
            // most one of them ever puts something on the table.
            OfferNextGeneratedRequest();
        }

        // ------------------------------------------------------------------ offering

        private void OfferNextTutorialRequest()
        {
            // Owner direction: no request line until the corporation knows this branch exists.
            if (!corporationContact) { return; }
            // One at a time. A second offer while the first is open would turn a tutorial that
            // teaches one system per step into a list of chores.
            //
            // **THE TUTORIAL KEEPS THE STRICTER GUARD, deliberately, and it is the only thing that
            // does.** Generated work asks `OfferedRequest` so a branch can carry several jobs; the
            // tutorial is a sequence where each step exists to teach the system the next one needs,
            // so holding an unfinished tutorial step is exactly when the next must not arrive.
            // Pre-hinge the two readings coincide anyway: generation does not run until after it.
            if (OpenRequest != null) { return; }

            List<RimroomsRequestDef> line = RimroomsRequestDef.TutorialLine();
            for (int index = 0; index < line.Count; index++)
            {
                RimroomsRequestDef definition = line[index];
                if (definition == null) { continue; }
                RequestRecord existing = RequestFor(definition.defName);
                // Already dealt with, in either direction. Move down the line.
                if (existing != null) { continue; }
                // The line is ordered, so the first unoffered request whose prerequisites are not
                // resolved stops the whole line rather than being skipped over.
                if (!PrerequisitesResolved(definition)) { return; }

                OfferRequest(definition);
                return;
            }
        }

        /// <summary>
        /// Put one request on the table, and record where its routes started.
        ///
        /// **The baseline is taken at OFFER, not at acceptance**, deliberately. It means the card
        /// reads the same from the moment it appears, and it means a player who starts the work
        /// before formally accepting is not punished for it — which is the same generosity as
        /// letting them order a shipment to a site before the crew arrives.
        ///
        /// A **tutorial** request takes no baseline at all. It is asked once and measures
        /// absolutely: a branch that already holds a battery has already learned request 1's
        /// lesson, and completing it immediately is the honest outcome.
        /// </summary>
        private RequestRecord OfferRequest(RimroomsRequestDef definition)
        {
            // A generated family may be asked for again, so its id carries an instance number.
            // A tutorial request is asked once and keeps the plain id it has always had, which
            // means existing saves keep matching their own records.
            string id = branchId + ":request:" + definition.defName;
            if (!definition.tutorial) { id += ":" + (TimesAsked(definition.defName) + 1); }
            var record = new RequestRecord
            {
                id = id,
                requestDefName = definition.defName,
                status = RequestStatus.Offered,
                offeredTick = Find.TickManager.TicksGame,
            };
            if (!definition.tutorial)
            {
                List<RimroomsSuccessRoute> ordered = OrderedRoutes(definition);
                for (int index = 0; index < ordered.Count; index++)
                {
                    RimroomsSuccessRoute route = ordered[index];
                    if (string.IsNullOrEmpty(route.labelKey)) { continue; }
                    record.routeBaselines.Add(new RouteBaseline
                    { labelKey = route.labelKey, value = MeasureRoute(route) });
                }
            }
            requests.Add(record);
            RecordEvent("RR_Event_RequestOffered", record.id, definition.LabelCap);
            Find.LetterStack.ReceiveLetter(
                "RR_Letter_RequestOfferedTitle".Translate(definition.LabelCap),
                "RR_Letter_RequestOfferedBody".Translate(definition.description, CompanyName),
                LetterDefOf.NeutralEvent);
            return record;
        }

        /// <summary>
        /// Whether everything this request waits on has been dealt with.
        ///
        /// **Cancelled satisfies a prerequisite.** A player who turns down request 4 has still
        /// resolved it, and stranding the rest of the line behind a refusal would make
        /// cancellation a trap rather than the right the chart grants.
        /// </summary>
        private bool PrerequisitesResolved(RimroomsRequestDef definition)
        {
            if (definition.prerequisiteRequests == null) { return true; }
            for (int index = 0; index < definition.prerequisiteRequests.Count; index++)
            {
                RequestRecord required = RequestFor(definition.prerequisiteRequests[index]);
                if (required == null || !required.Resolved) { return false; }
            }
            return true;
        }

        // ------------------------------------------------------------------ the player's two verbs

        /// <summary>Take the job on.</summary>
        public CompanyActionResult AcceptRequest(string defName)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            RequestRecord record = RequestFor(defName);
            if (record == null) { return CompanyActionResult.Refused("RR_Request_NotOffered"); }
            if (record.status == RequestStatus.Accepted) { return CompanyActionResult.Existing(); }
            if (record.status != RequestStatus.Offered)
            { return CompanyActionResult.Refused("RR_Request_AlreadyResolved"); }

            record.status = RequestStatus.Accepted;
            record.acceptedTick = Find.TickManager.TicksGame;
            record.staffAtAcceptance = EmployedStaffLoadIds();
            RecordEvent("RR_Event_RequestAccepted", record.id);
            return CompanyActionResult.Applied();
        }

        /// <summary>
        /// Turn it down, or walk away from it after accepting.
        ///
        /// **Chart §4.1: the player may cancel; the corporation may not.** There is no fee, no
        /// notice and no standing penalty, for the same reason a remote site has none: a cost for
        /// changing your mind is a deadline wearing a different coat.
        /// </summary>
        public CompanyActionResult CancelRequest(string defName)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            RequestRecord record = RequestFor(defName);
            if (record == null) { return CompanyActionResult.Refused("RR_Request_NotOffered"); }
            if (record.status == RequestStatus.Cancelled) { return CompanyActionResult.Existing(); }
            if (!record.Open) { return CompanyActionResult.Refused("RR_Request_AlreadyResolved"); }

            record.status = RequestStatus.Cancelled;
            RecordEvent("RR_Event_RequestCancelled", record.id);
            return CompanyActionResult.Applied();
        }

        private List<string> EmployedStaffLoadIds()
        {
            var ids = new List<string>();
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member == null || !member.employed || string.IsNullOrEmpty(member.pawnLoadId)) { continue; }
                if (!ids.Contains(member.pawnLoadId)) { ids.Add(member.pawnLoadId); }
            }
            ids.Sort(System.StringComparer.Ordinal);
            return ids;
        }

        // ------------------------------------------------------------------ completion

        /// <summary>
        /// Evaluate every open request once, refresh what the card shows, and complete anything
        /// that has come true.
        ///
        /// **One evaluation feeds both the rule and the readout**, which is the same discipline
        /// the gate's idle draw follows: a display that computes its own answer separately is a
        /// display that will eventually disagree with the thing it is describing.
        ///
        /// An **Offered** request is evaluated too, so a player can see what is already done
        /// before deciding. It is never completed while Offered — accepting is the branch saying
        /// yes, and a job nobody took cannot pay.
        /// </summary>
        private void CompleteSatisfiedRequests()
        {
            for (int index = 0; index < requests.Count; index++)
            {
                RequestRecord record = requests[index];
                if (record == null || !record.Open) { continue; }
                RimroomsRequestDef definition = record.Definition;
                if (definition == null) { continue; }

                List<RimroomsSuccessRoute> ordered = OrderedRoutes(definition);
                record.satisfiedRouteLabelKeys.Clear();
                RimroomsSuccessRoute satisfied = null;
                for (int slot = 0; slot < ordered.Count; slot++)
                {
                    RimroomsSuccessRoute route = ordered[slot];
                    if (!RouteSatisfied(route, record.BaselineFor(route.labelKey))) { continue; }
                    record.satisfiedRouteLabelKeys.Add(route.labelKey);
                    if (satisfied == null) { satisfied = route; }
                }

                if (record.status != RequestStatus.Accepted) { continue; }
                // **A request with paperwork is closed by its paperwork, and paid once.** Owner,
                // 2026-10-07, asked which event should close and pay a request whose journal the
                // company collects: *"i think option one"* -- book collection closes it, and the
                // routes only decide when the paperwork can turn green. Before this, collection
                // paid the fee under `:paperwork-return` and left the request open, and a route
                // then paid it again under `:payment` -- found playing *Choose a direction*.
                if (WriteUpsWanted(record).Count > 0)
                {
                    // A save written before this fix may already hold the collection payment for a
                    // request that never closed. It closes now, without paying a second time.
                    string returned = record.id + ":paperwork-return";
                    if (ledgerIndex.ContainsKey(returned))
                    { CompleteRequest(record, definition, satisfied, returned); }
                    continue;
                }
                if (satisfied == null) { continue; }
                CompleteRequest(record, definition, satisfied);
            }
        }

        /// <summary>
        /// A request's authored routes in a fixed order.
        ///
        /// **Ordinal, per invariant 26.** Two routes may go true on the same tick, and which one
        /// gets recorded as the one that did it must not depend on the order a def list happened
        /// to load in — which varies with the player's mod list.
        /// </summary>
        private static List<RimroomsSuccessRoute> OrderedRoutes(RimroomsRequestDef definition)
        {
            if (definition.successRoutes == null) { return new List<RimroomsSuccessRoute>(); }
            return definition.successRoutes
                .Where(route => route != null)
                .OrderBy(route => (int)route.kind)
                .ThenBy(route => route.labelKey, System.StringComparer.Ordinal)
                .ToList();
        }

        /// <summary>
        /// The receipt. `RR_ContractPaid` shipped against `ASSET_REQUESTS.md` -- *"The company pays
        /// out. Should feel like a receipt, not a jackpot"* -- and had **no consumer anywhere** until
        /// 2026-10-06.
        ///
        /// **It plays at the camera rather than at a building, because a ledger entry has no place.**
        /// The def is `MapOnly` with a `distRange` of 8 to 40, so a cue posted at the headquarters'
        /// centre would be inaudible whenever the player happened to be looking somewhere else on
        /// their own base -- a receipt that plays only if you are standing in the right room is worse
        /// than no receipt. Using the camera's own cell makes it audible exactly when the player is
        /// looking at the map it belongs to, and `RimroomsAudio.Play` already refuses any map that is
        /// not the current one, so being away on a coordinate stays silent without a second check.
        ///
        /// **Never the notification.** The letter below is what tells a player they were paid; this
        /// only accompanies it.
        /// </summary>
        private void PlayPaidCue()
        {
            Map map = Find.CurrentMap;
            if (map == null || Find.CameraDriver == null) { return; }
            IntVec3 cell = Find.CameraDriver.MapPosition;
            if (!cell.IsValid || !cell.InBounds(map)) { return; }
            Audio.RimroomsAudio.Play("RR_ContractPaid", map, cell, true);
        }

        /// <param name="paidOperationId">The ledger operation that already paid this request, when
        /// its paperwork was collected; null to pay it here.</param>
        internal void CompleteRequest(RequestRecord record, RimroomsRequestDef definition,
            RimroomsSuccessRoute satisfied, string paidOperationId = null)
        {
            if (!string.IsNullOrEmpty(paidOperationId))
            {
                record.settlementOperationId = paidOperationId;
            }
            // Pay first. If the payment cannot be posted the request stays Accepted and this runs
            // again next tick -- nothing is lost and nothing is completed for free.
            else if (definition.paymentUsd > 0)
            {
                string operationId = record.id + ":payment";
                CompanyActionResult paid = PostTransaction(operationId, definition.paymentUsd,
                    "RR_Ledger_RequestPayment", record.id);
                if (!paid.Success) { return; }
                record.settlementOperationId = operationId;
            }

            record.status = RequestStatus.Completed;
            record.completedTick = Find.TickManager.TicksGame;
            // Null only for a request closed by paperwork no route has yet come true for -- a save
            // from before the paperwork rule. It reads as the paperwork itself.
            string routeKey = satisfied == null ? "RR_Route_PaperworkReturned" : satisfied.labelKey;
            record.satisfiedRouteLabelKey = routeKey;
            RecordEvent("RR_Event_RequestCompleted", record.id, definition.LabelCap);
            PlayPaidCue();

            if (definition.bonusUsd > 0 && EverybodyCameBack(record))
            {
                CompanyActionResult bonus = PostTransaction(record.id + ":bonus", definition.bonusUsd,
                    "RR_Ledger_RequestBonus", record.id);
                if (bonus.Success && !bonus.AlreadyApplied)
                {
                    record.bonusPaid = true;
                    RecordEvent("RR_Event_RequestBonus", record.id, definition.bonusUsd.ToString("N0"));
                }
            }

            Find.LetterStack.ReceiveLetter(
                "RR_Letter_RequestCompletedTitle".Translate(definition.LabelCap),
                "RR_Letter_RequestCompletedBody".Translate(definition.LabelCap,
                    routeKey.Translate(), definition.paymentUsd.ToString("N0")),
                LetterDefOf.PositiveEvent);
        }

        /// <summary>
        /// Whether everybody who was on the books when this was accepted is still on them, alive.
        ///
        /// **This is the only read site for `bonusUsd`**, and it is the reason that field is not
        /// a hollow number — invariant 136. It is also the right beat for the one request that
        /// carries a bonus: *"bring back one record"* is the first time a branch sends people
        /// through a gate, and the company pays extra when they all come back out.
        ///
        /// Measured against the **snapshot**, never the live roster, so firing the casualty does
        /// not earn the bonus. Somebody hired afterwards is not held against the branch.
        /// </summary>
        private bool EverybodyCameBack(RequestRecord record)
        {
            if (record.staffAtAcceptance == null || record.staffAtAcceptance.Count == 0) { return false; }
            for (int index = 0; index < record.staffAtAcceptance.Count; index++)
            {
                string loadId = record.staffAtAcceptance[index];
                bool present = false;
                for (int slot = 0; slot < staff.Count; slot++)
                {
                    StaffRecord member = staff[slot];
                    if (member == null || !member.employed || member.pawnLoadId != loadId) { continue; }
                    Pawn pawn = member.pawn;
                    if (pawn == null || pawn.Dead || pawn.Destroyed) { continue; }
                    present = true;
                    break;
                }
                if (!present) { return false; }
            }
            return true;
        }

        // ------------------------------------------------------------------ what each route asks

        /// <summary>
        /// Whether one route has come true, counted from where the request started.
        ///
        /// `baseline` is zero for the tutorial line, which measures absolutely and asks each
        /// thing once, and is where the route stood when a **generated** request was offered.
        /// See <see cref="RouteBaseline"/> for why the two differ.
        /// </summary>
        private bool RouteSatisfied(RimroomsSuccessRoute route, int baseline)
        {
            int required = RequiredProgress(route);
            if (required <= 0) { return false; }
            return MeasureRoute(route) >= baseline + required;
        }

        /// <summary>
        /// How far along one route this branch is, as a number.
        ///
        /// **Seven kinds, seven different measurements.** Where two kinds could have collapsed
        /// into the same one they are split on what actually differs, because a request whose two
        /// routes are one measurement is the *"one route wearing two hats"* that
        /// `RimroomsRequestDef.ConfigErrors` exists to forbid — and a def that passes that rule
        /// while the runtime ignores it would be the rule passing on text alone.
        ///
        /// A number rather than a bool so that a baseline can be subtracted from it. That is the
        /// only reason this is not simply a predicate, and it is a good enough reason: *"deliver
        /// twenty more"* and *"hold twenty"* are different jobs and only one of them is a job.
        /// </summary>
        private int MeasureRoute(RimroomsSuccessRoute route)
        {
            switch (route.kind)
            {
                // The thing is home. "Home" is a branch place -- the headquarters or a registered
                // site -- never a coordinate, because a record still lying in the Backrooms has
                // not been brought back.
                case SuccessRouteKind.Deliver:
                case SuccessRouteKind.Substitute:
                case SuccessRouteKind.Purchase:
                    return OwnedThingCount(route.thingDefName);

                // The paperwork. An analysed record carries the log, and it keeps carrying it
                // after the book itself is gone.
                case SuccessRouteKind.Document:
                    return CompletedLogsOfKind(route.logKind);

                // The person. Somebody who was there, is still employed, and is still alive --
                // and DISTINCT people, so a route whose label promises two accounts needs two
                // different witnesses rather than one witness counted twice.
                case SuccessRouteKind.Testify:
                    return LivingWitnessCount(route.logKind);

                // Finished it.
                case SuccessRouteKind.Research:
                    return ProjectCompleted(route.projectDefName) ? 1 : 0;

                // Committed to it. Deliberately weaker than Research: the hinge offers both
                // against the same project, and "declare a direction" is saying where you are
                // going while "commit to the ladder" is arriving. If this asked for completion
                // the hinge would have two routes with one answer.
                case SuccessRouteKind.Redirect:
                    return RedirectTaken(route.redirectTo) ? 1 : 0;

                default:
                    return 0;
            }
        }

        /// <summary>
        /// How much progress this route asks for.
        ///
        /// `count` for the kinds that name a quantity; **one** for Research and Redirect, which
        /// are either done or not and whose `count` field means nothing. Returning `count` for
        /// them would let a def ask for a project to be completed three times.
        /// </summary>
        private static int RequiredProgress(RimroomsSuccessRoute route)
        {
            if (route.kind == SuccessRouteKind.Research || route.kind == SuccessRouteKind.Redirect)
            { return 1; }
            return route.count;
        }

        /// <summary>
        /// How many of a thing the branch has at a place it actually runs.
        ///
        /// Uses <see cref="CanReceiveDeliveryAt"/> rather than <see cref="OwnsMap"/> on purpose:
        /// `OwnsMap` includes the branch's own coordinates, and a book still on a shelf in the
        /// Backrooms has not been brought home.
        /// </summary>
        private int OwnedThingCount(string thingDefName)
        {
            if (string.IsNullOrEmpty(thingDefName)) { return 0; }
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(thingDefName);
            if (definition == null) { return 0; }
            int count = 0;
            List<Map> maps = Find.Maps;
            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || !CanReceiveDeliveryAt(map)) { continue; }
                List<Thing> things = map.listerThings.ThingsOfDef(definition);
                for (int slot = 0; slot < things.Count; slot++)
                {
                    Thing thing = things[slot];
                    if (thing == null || thing.Destroyed) { continue; }
                    count += thing.stackCount;
                }
            }
            return count;
        }

        private int CompletedLogsOfKind(string logKind)
        {
            LogKind kind;
            return TryLogKind(logKind, out kind) ? CompletedLogCount(kind) : 0;
        }

        /// <summary>
        /// Distinct living employees who witnessed something of this kind.
        ///
        /// **Distinct, employed and alive, all three.** Distinct because *"two crew accounts"*
        /// means two people. Employed because a testimony is the branch speaking. Alive because
        /// this is the half of the evidence system that a death can take away, which is exactly
        /// what makes it a different route from the paperwork rather than a second name for it.
        /// </summary>
        private int LivingWitnessCount(string logKind)
        {
            LogKind kind;
            if (!TryLogKind(logKind, out kind)) { return 0; }
            var witnesses = new HashSet<string>(System.StringComparer.Ordinal);
            for (int index = 0; index < evidence.Count; index++)
            {
                EvidenceRecord record = evidence[index];
                if (record == null || record.Observations == null) { continue; }
                IReadOnlyList<EvidenceObservationRecord> observations = record.Observations;
                for (int slot = 0; slot < observations.Count; slot++)
                {
                    EvidenceObservationRecord observation = observations[slot];
                    if (observation == null || string.IsNullOrEmpty(observation.WitnessLoadId)) { continue; }
                    if (!ObservationCarries(observation.Kind, kind)) { continue; }
                    Pawn witness = observation.Witness;
                    if (witness != null && !witness.Dead && !witness.Destroyed && IsEmployedPawn(witness))
                    { witnesses.Add(observation.WitnessLoadId); }

                    // Corroborating and disputing accounts are testimony too, and until
                    // 0.12.25-dev there was nowhere to hold them: one fact carried exactly one
                    // witness, so "two crew accounts of the same room" was unreachable and a
                    // request asking for two could only ever be satisfied across two coordinates.
                    //
                    // A DISPUTE COUNTS. Somebody was there and said something. The company files
                    // one version and the disagreement is a fact about the record, not a reason to
                    // pretend the second crew member never spoke.
                    IReadOnlyList<WitnessAccountRecord> accounts = observation.Accounts;
                    if (accounts == null) { continue; }
                    for (int seat = 0; seat < accounts.Count; seat++)
                    {
                        WitnessAccountRecord account = accounts[seat];
                        if (account == null || string.IsNullOrEmpty(account.WitnessLoadId)) { continue; }
                        Pawn speaker = account.Witness;
                        if (speaker == null || speaker.Dead || speaker.Destroyed) { continue; }
                        if (!IsEmployedPawn(speaker)) { continue; }
                        witnesses.Add(account.WitnessLoadId);
                    }
                }
            }
            return witnesses.Count;
        }

        /// <summary>
        /// Which observations speak to which log.
        ///
        /// Taken from `EvidenceObservationKinds`, which the investigation system already writes:
        /// a room survey is how a route gets known, a route mismatch or a recorder gap is the map
        /// and the landmark disagreeing, and a sighting is an entity. Nothing new is recorded for
        /// this feature — testimony reads what crews were already producing.
        /// </summary>
        private static bool ObservationCarries(string observationKind, LogKind logKind)
        {
            switch (logKind)
            {
                case LogKind.Route:
                    return observationKind == EvidenceObservationKinds.RoomSurvey;
                case LogKind.Distortion:
                    return observationKind == EvidenceObservationKinds.RouteMismatch ||
                        observationKind == EvidenceObservationKinds.RecorderGap;
                case LogKind.Entity:
                    return observationKind == EvidenceObservationKinds.EntitySighting;
                default:
                    return false;
            }
        }

        private static bool TryLogKind(string logKind, out LogKind kind)
        {
            switch ((logKind ?? "").ToLowerInvariant())
            {
                case "route": kind = LogKind.Route; return true;
                case "distortion": kind = LogKind.Distortion; return true;
                case "entity": kind = LogKind.Entity; return true;
                default: kind = LogKind.Route; return false;
            }
        }

        private bool IsEmployedPawn(Pawn pawn)
        {
            for (int index = 0; index < staff.Count; index++)
            {
                StaffRecord member = staff[index];
                if (member != null && member.employed && member.pawn == pawn) { return true; }
            }
            return false;
        }

        private bool ProjectCompleted(string projectDefName)
        {
            if (string.IsNullOrEmpty(projectDefName)) { return false; }
            for (int index = 0; index < projects.Count; index++)
            {
                ProjectRecord record = projects[index];
                if (record != null && record.completed && record.researchDefName == projectDefName)
                { return true; }
            }
            return false;
        }

        /// <summary>
        /// Started, rather than finished. Work on the bench, or the insight already committed.
        ///
        /// A project record exists as soon as a branch commits an insight to it, so this is the
        /// earliest honest moment at which a branch has said where it is going.
        /// </summary>
        private bool ProjectStarted(string projectDefName)
        {
            if (string.IsNullOrEmpty(projectDefName)) { return false; }
            for (int index = 0; index < projects.Count; index++)
            {
                ProjectRecord record = projects[index];
                if (record == null || record.researchDefName != projectDefName) { continue; }
                if (record.completed || record.insightCommitted || record.workDone > 0f) { return true; }
            }
            return false;
        }

        /// <summary>
        /// Whether a redirect has been taken: another request finished in its place, or the named
        /// project committed to.
        /// </summary>
        private bool RedirectTaken(string redirectTo)
        {
            if (string.IsNullOrEmpty(redirectTo)) { return false; }
            RequestRecord other = RequestFor(redirectTo);
            if (other != null && other.status == RequestStatus.Completed) { return true; }
            return ProjectStarted(redirectTo);
        }

        // ------------------------------------------------------------------ save integrity

        /// <summary>
        /// Requests, checked the way every other record collection is.
        ///
        /// A duplicate id would double-pay through a second operation id; an undefined status
        /// would fall through every switch silently. Both are save-integrity faults rather than
        /// gameplay recoveries.
        /// </summary>
        internal bool RequestRecordsValid()
        {
            var ids = new HashSet<string>(System.StringComparer.Ordinal);
            var tutorialDefNames = new HashSet<string>(System.StringComparer.Ordinal);
            int open = 0;
            for (int index = 0; index < requests.Count; index++)
            {
                RequestRecord record = requests[index];
                if (record == null || string.IsNullOrWhiteSpace(record.id) || !ids.Add(record.id))
                { return false; }
                if (string.IsNullOrWhiteSpace(record.requestDefName)) { return false; }
                if (!System.Enum.IsDefined(typeof(RequestStatus), record.status)) { return false; }
                if (record.staffAtAcceptance == null || record.routeBaselines == null) { return false; }
                if (record.status == RequestStatus.Offered) { open++; }

                // A GENERATED family may legitimately appear more than once, so def names are not
                // unique any more. A TUTORIAL request is asked exactly once, and a save holding
                // two of one would mean a fixed line had been offered twice and paid twice.
                RimroomsRequestDef definition = record.Definition;
                if (definition != null && definition.tutorial &&
                    !tutorialDefNames.Add(record.requestDefName)) { return false; }
            }
            // **ONE OFFER, EVER. ANY NUMBER ACCEPTED, WHICH THE OWNER ASKED FOR.** This counted
            // `record.Open` -- offered **or** accepted -- which made the whole save invalid the
            // moment a branch held two jobs, and was the save-level half of the same restriction
            // the offer guards imposed. Owner: *"with ability to accept more than one quests at a
            // time"*.
            //
            // The offer count stays bounded at one because both offer routines refuse while
            // something is awaiting an answer, so two offers in a save still means a guard was
            // bypassed and the player is being asked two questions at once.
            return open <= 1;
        }
    }
}
