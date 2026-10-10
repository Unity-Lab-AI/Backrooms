# -*- coding: utf-8 -*-
"""Extend the cleaning family with snow/sand and pollution, and wire the roof family.

The cleaning family takes the two weather routes rather than getting a new family, because its
continuation giver already sits at 22 -- above `CleanClearSnow` (10) and `CleanClearPollution` (0)
-- so the rule that continuation must outrank every local giver it travels for already holds. The
roof routes could not do the same: the finishing family's continuation is 82, below `BuildRoofs`
(100) and `RemoveRoofs` (90), so they needed their own family at 101.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


UPKEEP = "src/RimroomsAsyncIndustries/ConnectedWork/Providers/UpkeepProviders.cs"

# ------------------------------------------------------------------ cleaning: two new routes
sub(UPKEEP,
    u"""        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            List<Thing> filth = FilthOn(map);
            if (filth == null || filth.Count == 0) { return false; }""",
    u"""        public override bool HasCandidateWork(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map == null || pawn == null || work == null || !WorkerEligible(pawn)) { return false; }
            // Weather work first: both are a TrueCount comparison on an area, so a map with no
            // snow area and no pollution area leaves in two integer reads.
            if (AnyWeatherToClear(map, pawn, work)) { return true; }
            List<Thing> filth = FilthOn(map);
            if (filth == null || filth.Count == 0) { return false; }""")

sub(UPKEEP,
    u"""        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            List<Thing> filth = FilthOn(pawn.Map);
            if (filth == null) { return false; }""",
    u"""        public override bool HasWorkHere(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Map == null || !WorkerEligible(pawn))
            { return false; }
            if (AnyWeatherToClear(pawn.Map, pawn, null)) { return true; }
            List<Thing> filth = FilthOn(pawn.Map);
            if (filth == null) { return false; }""")

sub(UPKEEP,
    u"""        private static List<Thing> FilthOn(Map map)
        {
            return map.listerFilthInHomeArea == null ? null : map.listerFilthInHomeArea.FilthInHomeArea;
        }""",
    u'''        /// <summary>
        /// How many marked cells one remote pass may look at. Areas are cell sets and a player
        /// can paint a large one.
        /// </summary>
        private const int MaximumWeatherCellsPerMap = 24;

        /// <summary>
        /// Snow, sand or pollution the player marked for clearing on that map.
        ///
        /// **Live only since the ordinary-map endpoint landed at 0.6.9-dev.**
        /// `research/ZONES_AND_AREAS_ACROSS_A_GATE.md` recorded `Area_SnowOrSandClear` and
        /// `Area_PollutionClear` as not covered *and correctly so*, with the reason written down:
        /// a Backrooms coordinate **has no outside and therefore no weather**, so nothing
        /// accumulates there and the areas have nothing in them. A registered remote site is an
        /// ordinary world map, which does get snow and can be polluted, so the reason expired.
        ///
        /// On a coordinate this still finds nothing, because there is still nothing to find.
        ///
        /// Both halves are facts about the map asked about, taken from Core's own givers:
        /// `WorkGiver_ClearSnowOrSand` refuses below `0.2f` of snow **or** sand depth, and
        /// `WorkGiver_ClearPollution` asks `map.pollutionGrid.IsPolluted(cell)`. Neither takes a
        /// pawn, so Core's real question is asked here rather than substituted for. The
        /// reservation is all that is left to arrival.
        ///
        /// `map.pollutionGrid` is null without Biotech, which is the only gate either route
        /// needs: an absent expansion is an empty world, not a condition.
        /// </summary>
        private static bool AnyWeatherToClear(Map map, Pawn pawn, RimroomsConnectedWorkComponent work)
        {
            if (map.areaManager == null) { return false; }
            return AnyMarked(map, pawn, work, map.areaManager.SnowOrSandClear, true) ||
                AnyMarked(map, pawn, work, map.areaManager.PollutionClear, false);
        }

        private static bool AnyMarked(Map map, Pawn pawn, RimroomsConnectedWorkComponent work,
            Area area, bool snow)
        {
            if (area == null || area.TrueCount == 0) { return false; }
            if (!snow && map.pollutionGrid == null) { return false; }
            int examined = 0;
            foreach (IntVec3 cell in area.ActiveCells)
            {
                if (work != null && examined >= MaximumWeatherCellsPerMap) { break; }
                examined++;
                if (!cell.IsValid || !cell.InBounds(map) || cell.Fogged(map)) { continue; }
                if (snow)
                {
                    // Core's own threshold, and it is an OR: either depth alone is enough.
                    if (map.snowGrid == null) { continue; }
                    if (map.snowGrid.GetDepth(cell) < 0.2f && cell.GetSandDepth(map) < 0.2f)
                    { continue; }
                }
                else if (!map.pollutionGrid.IsPolluted(cell)) { continue; }
                if (work != null && !work.ObservedAreaAllows(pawn, map, cell)) { continue; }
                if (work == null && !pawn.CanReserve(cell, 1, -1, null)) { continue; }
                return true;
            }
            return false;
        }

        private static List<Thing> FilthOn(Map map)
        {
            return map.listerFilthInHomeArea == null ? null : map.listerFilthInHomeArea.FilthInHomeArea;
        }''')

# ------------------------------------------------------------------ the roof family id
REG = "src/RimroomsAsyncIndustries/ConnectedWork/ConnectedDeploymentProvider.cs"
sub(REG, u'        /// <summary>Designation-driven: flick, open, eject fuel.</summary>',
    u"""        /// <summary>
        /// Roof building and roof removal on the far map, driven by `Area_BuildRoof` and
        /// `Area_NoRoof`. A third `Construction` family rather than two routes on the finishing
        /// one, because the finishing family's continuation giver sits at 82 -- **below** Core's
        /// `BuildRoofs` (100) and `RemoveRoofs` (90) -- and a continuation giver that does not
        /// outrank the local givers it travels for turns a committed worker around.
        /// </summary>
        public const string RoofWork = "roof-work";

        /// <summary>Designation-driven: flick, open, eject fuel.</summary>""")

sub(REG, u"        private static readonly PaintingProvider painting = new PaintingProvider();",
    u"        private static readonly PaintingProvider painting = new PaintingProvider();\n"
    u"        private static readonly RoofWorkProvider roofWork = new RoofWorkProvider();")

sub(REG, u"                { Painting, painting },",
    u"                { Painting, painting },\n                { RoofWork, roofWork },")

# ------------------------------------------------------------------ giver classes
sub("src/RimroomsAsyncIndustries/ConnectedWork/WorkGiver_ConnectedDeployment.cs",
    u"    public sealed class WorkGiver_ConnectedBasicWorker : WorkGiver_ConnectedDeployment",
    u"    public sealed class WorkGiver_ConnectedRoofWork : WorkGiver_ConnectedDeployment\n"
    u"    {\n"
    u"        protected override string ProviderId\n"
    u"        { get { return ConnectedDeploymentProviders.RoofWork; } }\n"
    u"        protected override bool ContinueOnly { get { return false; } }\n"
    u"    }\n\n"
    u"    public sealed class WorkGiver_ConnectedRoofWorkContinue : WorkGiver_ConnectedDeployment\n"
    u"    {\n"
    u"        protected override string ProviderId\n"
    u"        { get { return ConnectedDeploymentProviders.RoofWork; } }\n"
    u"        protected override bool ContinueOnly { get { return true; } }\n"
    u"    }\n\n"
    u"    public sealed class WorkGiver_ConnectedBasicWorker : WorkGiver_ConnectedDeployment")

# ------------------------------------------------------------------ the two defs
sub("Mod/Rimrooms - Async Industries/1.6/Defs/WorkGiverDefs/RR_ConnectedWork.xml",
    u"  <!-- BasicWorker: flick a switch, open a container, eject fuel on the far side.",
    u"""  <!-- RoofWork: put a roof up or take one down on the far side, driven by the player's own
       BuildRoof and NoRoof areas. Continue sits at 101, one above Core's BuildRoofs (100) and
       therefore above RemoveRoofs (90) as well, which are the two givers this family travels
       for. It is NOT hung on the finishing family because that family's continue is 82, below
       both, and a continue giver below the work it travels for turns a committed worker around.
       Plan sits at 1, below ConstructSmoothWalls (10) which is the lowest local giver in the
       type, and below the finishing (5) and repair (3) plans because a frame somebody is waiting
       on beats a roof area. -->

  <WorkGiverDef>
    <defName>RR_ConnectedRoofWorkContinue</defName>
    <label>travel on to work a roof through a gate</label>
    <giverClass>RimroomsAsyncIndustries.ConnectedWork.WorkGiver_ConnectedRoofWorkContinue</giverClass>
    <workType>Construction</workType>
    <verb>roof</verb>
    <gerund>working a roof</gerund>
    <priorityInType>101</priorityInType>
    <requiredCapacities><li>Manipulation</li><li>Moving</li></requiredCapacities>
    <canBeDoneByMechs>false</canBeDoneByMechs>
    <prioritizeSustains>true</prioritizeSustains>
  </WorkGiverDef>

  <WorkGiverDef>
    <defName>RR_ConnectedRoofWork</defName>
    <label>cross a gate to work a roof</label>
    <giverClass>RimroomsAsyncIndustries.ConnectedWork.WorkGiver_ConnectedRoofWork</giverClass>
    <workType>Construction</workType>
    <verb>roof</verb>
    <gerund>working a roof</gerund>
    <priorityInType>1</priorityInType>
    <requiredCapacities><li>Manipulation</li><li>Moving</li></requiredCapacities>
    <canBeDoneByMechs>false</canBeDoneByMechs>
  </WorkGiverDef>

  <!-- BasicWorker: flick a switch, open a container, eject fuel on the far side.""")

# ------------------------------------------------------------------ strings and settings row
sub("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_ConnectedWork.xml",
    u"  <RR_ConnectedWork_BasicWorkerLabel>",
    u"  <RR_ConnectedWork_RoofWorkLabel>working a roof through a gate</RR_ConnectedWork_RoofWorkLabel>\n"
    u"  <RR_ConnectedWork_BasicWorkerLabel>")

sub("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Audio.xml",
    u"  <RR_Settings_FamilyPainting>Travelling to paint</RR_Settings_FamilyPainting>",
    u"  <RR_Settings_FamilyPainting>Travelling to paint</RR_Settings_FamilyPainting>\n"
    u"  <RR_Settings_FamilyRoofWork>Travelling to work a roof</RR_Settings_FamilyRoofWork>")

sub("src/RimroomsAsyncIndustries/Core/ConnectedWorkPriorities.cs",
    u'            new ConnectedWorkPriorityPair("RR_Settings_FamilyDarkStudy",',
    u'            new ConnectedWorkPriorityPair("RR_Settings_FamilyRoofWork",\n'
    u'                "RR_ConnectedRoofWorkContinue", "RR_ConnectedRoofWork"),\n'
    u'            new ConnectedWorkPriorityPair("RR_Settings_FamilyDarkStudy",')

print("areas and roof family wired")
