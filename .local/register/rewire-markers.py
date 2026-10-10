# -*- coding: utf-8 -*-
"""Move the site, the cargo kit, the ledger and the UI off the retired survey tag."""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:80])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


SITE = 'src/RimroomsAsyncIndustries/Threats/FirstSliceSiteComponent.cs'

patch(SITE, [
    # ---- the scan replaces the registry of deployed aids ---------------------------------
    ("""        private IEnumerable<CompRouteAid> DeployedAids()
        {
            // One kind of route aid since the beacon was retired in 0.9.9-dev.
            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_SurveyTag");
            if (definition == null) { yield break; }
            foreach (Thing item in map.listerThings.ThingsOfDef(definition))
            {
                CompRouteAid aid = item.TryGetComp<CompRouteAid>();
                if (aid != null && aid.Deployed && aid.CoordinateId == Coordinate?.Id) { yield return aid; }
            }
        }""",

     """        /// <summary>
        /// Every marker this coordinate has, placed by the player designating a glow pod.
        ///
        /// The custom survey tag this replaced was a mod item with its own deploy job, its own
        /// recipe and a limit of one per room. Owner direction was <i>"lets not limit the
        /// amount"</i>, so there is no limit here of any kind, and the pods are Core's own.
        /// </summary>
        private IEnumerable<CompRimroomsMarker> Markers()
        {
            string id = Coordinate?.Id;
            if (string.IsNullOrEmpty(id)) { yield break; }
            foreach (CompRimroomsMarker marker in CompRimroomsMarker.OnMap(map))
            {
                if (marker.CoordinateId == id) { yield return marker; }
            }
        }

        /// <summary>Hands out the next marker number for this coordinate. Never reused.</summary>
        internal int NextMarkerNumber()
        {
            return nextMarkerNumber == int.MaxValue ? nextMarkerNumber : nextMarkerNumber++;
        }"""),

    # ---- the corridor mismatch moves a marker rather than an item -------------------------
    ("""                    CompRouteAid tag = DeployedAids().FirstOrDefault(a => !a.Beacon && a.RoomIndex == junction.index &&
                        RoomAt(a.parent.Position)?.index == junction.index && !a.parent.def.AffectsRegions);
                    if (tag != null && TryRoomCell(currentRoom, out IntVec3 tagCell) && tagCell.GetFirstItem(map) == null)
                    {
                        tag.parent.Position = tagCell;
                        tag.MarkMismatch();""",

     """                    CompRimroomsMarker tag = Markers().FirstOrDefault(a => a.RoomIndex == junction.index &&
                        RoomAt(a.parent.Position)?.index == junction.index);
                    if (tag != null && TryRoomCell(currentRoom, out IntVec3 tagCell) && tagCell.GetFirstItem(map) == null &&
                        tag.RelocateTo(tagCell, map))
                    {
                        tag.MarkMismatch();"""),

    # ---- the evidence observation reads the same scan -------------------------------------
    ("""                CompRouteAid displaced = DeployedAids().FirstOrDefault(a => !a.Beacon &&
                    a.RoomIndex != room.Index && RoomAt(a.parent.Position)?.Index == room.Index);""",

     """                CompRimroomsMarker displaced = Markers().FirstOrDefault(a =>
                    a.RoomIndex != room.Index && RoomAt(a.parent.Position)?.Index == room.Index);"""),
])

# ---- the whole deploy order is gone: a marker is a designation, not a job ------------------
text = io.open(SITE, encoding='utf-8-sig').read()
start = text.index('        public CompanyActionResult QueueDeployAid(Pawn pawn)')
end = text.index('        private void ReturnDeploymentRecovery')
replacement = """        /// <summary>
        /// Nothing queues a marker any more, by design.
        ///
        /// The retired survey tag needed an order, a job driver, a reserved cell, a free
        /// inventory slot and a per-room limit before a pawn could put one down. A glow pod is
        /// a Core building a colonist installs with the ordinary install order, and marking it
        /// is a designation on the thing itself -- the same shape as designating a door as a
        /// gate. Three moving parts became none.
        /// </summary>
"""
text = text[:start] + replacement + text[end:]
io.open(SITE, 'w', encoding='utf-8-sig', newline='').write(text)
print('  removed the deploy order from %s' % SITE)
