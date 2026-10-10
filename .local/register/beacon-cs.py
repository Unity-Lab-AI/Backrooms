import io

def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:70]
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('patched ' + path.split('/')[-1])

S = 'src/RimroomsAsyncIndustries/'

patch(S + 'Expedition/ExpeditionCargo.cs', [
 ('        private static readonly string[] KitDefs = { "RR_FieldRecorder", "RR_SurveyTag", "RR_ReturnBeacon", "RR_SealedEvidenceCase" };',
  '        // The return beacon was retired in 0.9.9-dev: the gate\'s own address book and the\n'
  '        // saved return threshold already are the route authority, so the item had no job\n'
  '        // left to do. Owner decision, asked at the fork.\n'
  '        private static readonly string[] KitDefs = { "RR_FieldRecorder", "RR_SurveyTag", "RR_SealedEvidenceCase" };'),
 ('            if (site == null || string.IsNullOrEmpty(coordinateId) || (name != "RR_SurveyTag" && name != "RR_ReturnBeacon")) { return 0; }',
  '            if (site == null || string.IsNullOrEmpty(coordinateId) || name != "RR_SurveyTag") { return 0; }'),
])

patch(S + 'Generation/FailedSiteRecovery.cs', [
 ('                "SimpleResearchBench", "RR_FieldRecorder", "RR_SurveyTag", "RR_ReturnBeacon",',
  '                "SimpleResearchBench", "RR_FieldRecorder", "RR_SurveyTag",'),
])

patch(S + 'Threats/FirstSliceSiteComponent.cs', [
 ('            foreach (string name in new[] { "RR_SurveyTag", "RR_ReturnBeacon" })\n'
  '            {\n'
  '                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(name);\n'
  '                if (definition == null) { continue; }\n'
  '                foreach (Thing item in map.listerThings.ThingsOfDef(definition))\n'
  '                {\n'
  '                    CompRouteAid aid = item.TryGetComp<CompRouteAid>();\n'
  '                    if (aid != null && aid.Deployed && aid.CoordinateId == Coordinate?.Id) { yield return aid; }\n'
  '                }\n'
  '            }',
  '            // One kind of route aid since the beacon was retired in 0.9.9-dev.\n'
  '            ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail("RR_SurveyTag");\n'
  '            if (definition == null) { yield break; }\n'
  '            foreach (Thing item in map.listerThings.ThingsOfDef(definition))\n'
  '            {\n'
  '                CompRouteAid aid = item.TryGetComp<CompRouteAid>();\n'
  '                if (aid != null && aid.Deployed && aid.CoordinateId == Coordinate?.Id) { yield return aid; }\n'
  '            }'),
 ('        public CompanyActionResult QueueDeployAid(Pawn pawn, bool beacon)',
  '        public CompanyActionResult QueueDeployAid(Pawn pawn)'),
 ('            Thing item = pawn.inventory?.innerContainer.FirstOrDefault(t => t.def.defName == (beacon ? "RR_ReturnBeacon" : "RR_SurveyTag"));',
  '            Thing item = pawn.inventory?.innerContainer.FirstOrDefault(t => t.def.defName == "RR_SurveyTag");'),
])

patch(S + 'UI/OperationsExpeditions.cs', [
 ('            foreach (string defName in new[] { "RR_SurveyTag", "RR_ReturnBeacon" })\n'
  '            {\n'
  '                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);\n'
  '                if (definition == null) { continue; }',
  '            // One kind of route aid since the beacon was retired in 0.9.9-dev.\n'
  '            foreach (string defName in new[] { "RR_SurveyTag" })\n'
  '            {\n'
  '                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(defName);\n'
  '                if (definition == null) { continue; }'),
])
