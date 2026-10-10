# -*- coding: utf-8 -*-
"""The remaining call sites the compiler named."""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:80])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


# --------------------------------------------------------------------------- the site
patch('src/RimroomsAsyncIndustries/Threats/FirstSliceSiteComponent.cs', [
    # This branch could never fire. `Beacon` came from a def retired in 0.9.9-dev, so the
    # first clause was permanently false and a marked junction could never counter the
    # distortion. Marker types give the branch a real condition for the first time.
    ("""            bool protectedRoute = DeployedAids().Any(a => a.Beacon && a.RoomIndex == junction.index && RoomAt(a.parent.Position)?.index == junction.index) &&
                DeployedAids().Any(a => !a.Beacon && a.RoomIndex == junction.index);""",

     """            // Marked and still where it was put. Until this checkpoint the first half of
            // this test asked whether a *beacon* was present -- a def retired in 0.9.9-dev --
            // so it was permanently false and a marked junction could never counter anything.
            // A marker type that says it counters distortion is a condition that can be met.
            bool protectedRoute = Markers().Any(a => a.MarkerType != null && a.MarkerType.countersDistortion &&
                a.RoomIndex == junction.index && RoomAt(a.parent.Position)?.index == junction.index);"""),
])


# --------------------------------------------------------------------------- the ledger
patch('src/RimroomsAsyncIndustries/Company/EvidenceObservations.cs', [
    ("""            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_SurveyTag");
            if (definition == null) { return false; }
            foreach (Thing item in map.listerThings.ThingsOfDef(definition))
            {
                CompRouteAid aid = item.TryGetComp<CompRouteAid>();
                if (item.Destroyed || !item.Spawned || item.Map != map || aid == null || !aid.Deployed ||
                    aid.CoordinateId != coordinate.id || aid.RoomIndex != recordedRoom || aid.Number != markerNumber) { continue; }
                if (coordinate.rooms.Any(r => r != null && r.index == observedRoom && r.Bounds.Contains(item.Position))) { return true; }
            }
            return false;""",

     """            foreach (Investigation.CompRimroomsMarker marker in Investigation.CompRimroomsMarker.OnMap(map))
            {
                Thing item = marker.parent;
                if (item.Destroyed || !item.Spawned || item.Map != map ||
                    marker.CoordinateId != coordinate.id || marker.RoomIndex != recordedRoom ||
                    marker.Number != markerNumber) { continue; }
                if (coordinate.rooms.Any(r => r != null && r.index == observedRoom && r.Bounds.Contains(item.Position))) { return true; }
            }
            return false;"""),
])


# --------------------------------------------------------------------------- the kit
patch('src/RimroomsAsyncIndustries/Expedition/ExpeditionCargo.cs', [
    ("""        // The return beacon was retired in 0.9.9-dev: the gate's own address book and the
        // saved return threshold already are the route authority, so the item had no job
        // left to do. Owner decision, asked at the fork.
        private static readonly string[] KitDefs = { "RR_FieldRecorder", "RR_SurveyTag", "RR_SealedEvidenceCase" };
        private static readonly int[] KitCounts = { 1, 6, 1, 1 };""",

     """        // The return beacon was retired in 0.9.9-dev: the gate's own address book and the
        // saved return threshold already are the route authority, so the item had no job
        // left to do. Owner decision, asked at the fork.
        //
        // The survey tag left in 0.10.7-dev, and its six-per-crew requirement left with it.
        // Owner direction was *"lets not limit the amount"*, and a kit check that refuses to
        // dispatch a crew without exactly six of something is the same limit wearing a hat.
        // Markers are glow pods now: a player brings as many or as few as they like.
        //
        // The counts array carried a fourth entry the loop never read, left over from the
        // beacon. Arrays that disagree about their own length are a bug waiting for somebody
        // to add an item to one of them.
        private static readonly string[] KitDefs = { "RR_FieldRecorder", "RR_SealedEvidenceCase" };
        private static readonly int[] KitCounts = { 1, 1 };"""),

    ("""        private static int DeployedCount(string name, Map site, string coordinateId)
        {
            if (site == null || string.IsNullOrEmpty(coordinateId) || name != "RR_SurveyTag") { return 0; }
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
            if (def == null) { return 0; }
            int count = 0;
            foreach (Thing item in site.listerThings.ThingsOfDef(def))
            {
                CompRouteAid aid = item.TryGetComp<CompRouteAid>();
                if (!item.Destroyed && item.Spawned && item.Map == site && aid != null && aid.Deployed && aid.CoordinateId == coordinateId)
                { count += item.stackCount; }
            }
            return count;
        }""",

     """        /// <summary>
        /// Kit already put down at the site counts as kit the crew has.
        ///
        /// Nothing in the kit is deployable any more -- the survey tag was the only one, and
        /// it left in 0.10.7-dev -- so this is zero for every remaining entry. It is kept as
        /// the seam rather than deleted because the rule it expresses is still the right one:
        /// a crew that has already placed something has not lost it.
        /// </summary>
        private static int DeployedCount(string name, Map site, string coordinateId)
        {
            return 0;
        }"""),
])


# --------------------------------------------------------------------------- the UI
patch('src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs', [
    ("""                    if (listing.ButtonText("RR_UI_PlaceTag".Translate(selected.LabelShortCap))) { ShowResult(site.QueueDeployAid(selected)); }
""", ""),
    ("""                    DrawRouteAidRecovery(listing, selected);
""", ""),
])

text = io.open('src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs', encoding='utf-8-sig').read()
start = text.index('        private static void DrawRouteAidRecovery(Listing_Standard listing, Pawn pawn)')
end = text.index('        private static void DrawManifest(Listing_Standard listing, ExpeditionRecord run)')
replacement = """        // Recovering a marker is an ordinary uninstall order on an ordinary Core building
        // now, so the panel that used to list every deployed survey tag and offer to pick it
        // up has nothing left to do. Removed rather than left showing an empty list.
"""
text = text[:start] + replacement + text[end:]
io.open('src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs', 'w', encoding='utf-8-sig', newline='').write(text)
print('  removed the route-aid recovery panel')
