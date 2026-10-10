"""One-off patch: request families remember the gate addresses they were met at."""
p = 'src/RimroomsAsyncIndustries/Company/RequestLine.cs'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new, 1)


rep('''        private List<RequestRecord> requests = new List<RequestRecord>();

        internal void ExposeRequests()
        {
            Scribe_Collections.Look(ref requests, "rr_requestLine", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && requests == null)
            { requests = new List<RequestRecord>(); }
        }''', '''        private List<RequestRecord> requests = new List<RequestRecord>();

        /// <summary>
        /// Every gate address a request family has already been met at, as
        /// <c>family|coordinateId</c>.
        ///
        /// **Owner, 2026-10-07, verbatim:** *"we still want them to be never ending missions but
        /// they should require a differernt address through the gate"*. A family asked for again
        /// counts only evidence from coordinates it has not been met at, so one well-documented
        /// coordinate cannot pay the same job forever. Saved, because it is history.
        /// </summary>
        private List<string> usedRequestAddresses = new List<string>();

        internal void ExposeRequests()
        {
            Scribe_Collections.Look(ref requests, "rr_requestLine", LookMode.Deep);
            Scribe_Collections.Look(ref usedRequestAddresses, "rr_usedRequestAddresses",
                LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && requests == null)
            { requests = new List<RequestRecord>(); }
            if (Scribe.mode == LoadSaveMode.PostLoadInit && usedRequestAddresses == null)
            { usedRequestAddresses = new List<string>(); }
        }

        private bool AddressUsed(string family, string coordinateId)
        {
            if (string.IsNullOrEmpty(family) || string.IsNullOrEmpty(coordinateId)) { return false; }
            return usedRequestAddresses.Contains(family + "|" + coordinateId);
        }

        /// <summary>
        /// Spends the addresses a completed request's evidence routes drew on, so the next request
        /// of the same family needs somewhere new. Every coordinate holding evidence of a kind the
        /// family's Document or Testify routes read is spent, whichever route actually closed it:
        /// the branch was paid for what it knew about those places.
        /// </summary>
        private void SpendRequestAddresses(RimroomsRequestDef definition)
        {
            if (definition == null || definition.successRoutes == null) { return; }
            string family = definition.defName;
            foreach (RimroomsSuccessRoute route in definition.successRoutes)
            {
                if (route == null) { continue; }
                if (route.kind != SuccessRouteKind.Document && route.kind != SuccessRouteKind.Testify)
                { continue; }
                LogKind kind;
                if (!TryLogKind(route.logKind, out kind)) { continue; }
                for (int index = 0; index < evidence.Count; index++)
                {
                    EvidenceRecord record = evidence[index];
                    if (record == null || string.IsNullOrEmpty(record.coordinateId)) { continue; }
                    if (!EvidenceCarries(record, kind, route.kind)) { continue; }
                    string key = family + "|" + record.coordinateId;
                    if (!usedRequestAddresses.Contains(key)) { usedRequestAddresses.Add(key); }
                }
            }
        }

        /// <summary>Whether this record holds evidence of a kind, as the given route reads it.</summary>
        private bool EvidenceCarries(EvidenceRecord record, LogKind kind, SuccessRouteKind routeKind)
        {
            if (routeKind == SuccessRouteKind.Document)
            {
                if (record.analyzedTick < 0) { return false; }
                return kind == LogKind.Route ? record.RouteRecorded
                    : kind == LogKind.Distortion ? record.DistortionRecorded
                    : record.EntityRecorded;
            }
            if (record.Observations == null) { return false; }
            for (int slot = 0; slot < record.Observations.Count; slot++)
            {
                EvidenceObservationRecord observation = record.Observations[slot];
                if (observation != null && ObservationCarries(observation.Kind, kind)) { return true; }
            }
            return false;
        }''')

rep('''                    { labelKey = route.labelKey, value = MeasureRoute(route) });''',
    '''                    { labelKey = route.labelKey, value = MeasureRoute(route, definition.defName) });''')
rep('''                    if (!RouteSatisfied(route, record.BaselineFor(route.labelKey))) { continue; }''',
    '''                    if (!RouteSatisfied(route, record.BaselineFor(route.labelKey), definition.defName))
                    { continue; }''')
rep('''        private bool RouteSatisfied(RimroomsSuccessRoute route, int baseline)
        {
            int required = RequiredProgress(route);
            if (required <= 0) { return false; }
            return MeasureRoute(route) >= baseline + required;''',
    '''        private bool RouteSatisfied(RimroomsSuccessRoute route, int baseline, string family)
        {
            int required = RequiredProgress(route);
            if (required <= 0) { return false; }
            return MeasureRoute(route, family) >= baseline + required;''')
rep('''        private int MeasureRoute(RimroomsSuccessRoute route)
        {''', '''        /// <param name="family">The request family asking; evidence from an address that family
        /// has already been met at does not count. Null counts everything.</param>
        private int MeasureRoute(RimroomsSuccessRoute route, string family = null)
        {''')
rep('''                    return CompletedLogsOfKind(route.logKind);''',
    '''                    return CompletedLogsOfKind(route.logKind, family);''')
rep('''                    return LivingWitnessCount(route.logKind);
''', '''                    return LivingWitnessCount(route.logKind, family);
''')
rep('''        private int CompletedLogsOfKind(string logKind)
        {
            LogKind kind;
            return TryLogKind(logKind, out kind) ? CompletedLogCount(kind) : 0;
        }''', '''        private int CompletedLogsOfKind(string logKind, string family = null)
        {
            LogKind kind;
            if (!TryLogKind(logKind, out kind)) { return 0; }
            if (string.IsNullOrEmpty(family)) { return CompletedLogCount(kind); }
            int count = 0;
            for (int index = 0; index < evidence.Count; index++)
            {
                EvidenceRecord record = evidence[index];
                if (record == null || AddressUsed(family, record.coordinateId)) { continue; }
                if (EvidenceCarries(record, kind, SuccessRouteKind.Document)) { count++; }
            }
            return count;
        }''')
rep('''        private int LivingWitnessCount(string logKind)
        {''', '''        private int LivingWitnessCount(string logKind, string family = null)
        {''')
rep('''                if (record == null || record.Observations == null) { continue; }
                IReadOnlyList<EvidenceObservationRecord> observations = record.Observations;''',
    '''                if (record == null || record.Observations == null) { continue; }
                if (AddressUsed(family, record.coordinateId)) { continue; }
                IReadOnlyList<EvidenceObservationRecord> observations = record.Observations;''')
rep('''            RecordEvent("RR_Event_RequestCompleted", record.id, definition.LabelCap);''',
    '''            RecordEvent("RR_Event_RequestCompleted", record.id, definition.LabelCap);
            SpendRequestAddresses(definition);''')
open(p, 'w', encoding='utf-8').write(s)
print("patched")
