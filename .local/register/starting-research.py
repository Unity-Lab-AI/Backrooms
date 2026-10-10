import io

def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:70]
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('patched ' + path.split('/')[-1])

# --- the start def declares only what BEGINS FINISHED ----------------------
patch('src/RimroomsAsyncIndustries/Scenario/RimroomsStartDef.cs', [
 ('        public long surveyBonusUsd = 1000000L;',
  '        public long surveyBonusUsd = 1000000L;\n'
  '\n'
  '        /// <summary>\n'
  '        /// Company projects this start begins with already finished.\n'
  '        ///\n'
  '        /// **Owner direction, 2026-09-29, verbatim:** *"all starts have same tech tree just\n'
  '        /// differnt starting researches finished based on scenerio"*.\n'
  '        ///\n'
  '        /// So a start declares **only this**. It never declares a tree, and it cannot: the\n'
  '        /// branch is seeded from every `RimroomsProjectDef` the game has loaded, so the tree\n'
  '        /// is identical for every start **by construction** rather than by three lists being\n'
  '        /// kept in agreement by hand. Adding a project later reaches every scenario at once,\n'
  '        /// and a scenario that forgot to list it cannot exist.\n'
  '        ///\n'
  '        /// A name here that matches no project is reported and skipped rather than failing a\n'
  '        /// start: a player should not lose a new colony because a scenario named a project\n'
  '        /// that a content update renamed.\n'
  '        /// </summary>\n'
  '        public List<string> completedProjects = new List<string>();'),
])

# --- the request carries them ---------------------------------------------
patch('src/RimroomsAsyncIndustries/Company/CompanyActionResult.cs', [
 ('        public long DailyOverheadUsd;',
  '        public long DailyOverheadUsd;\n'
  '        /// <summary>Company projects this start begins with already finished.</summary>\n'
  '        public List<string> CompletedProjects = new List<string>();'),
])

patch('src/RimroomsAsyncIndustries/Scenario/ScenPart_RimroomsStart.cs', [
 ('                SurveyBonusUsd = startDef.surveyBonusUsd',
  '                SurveyBonusUsd = startDef.surveyBonusUsd,\n'
  '                CompletedProjects = startDef.completedProjects == null\n'
  '                    ? new List<string>() : new List<string>(startDef.completedProjects)'),
])

# --- the branch is seeded from the whole tree ------------------------------
patch('src/RimroomsAsyncIndustries/Company/CampaignServices.cs', [
 ('            var initialProject = new ProjectRecord { id = newId + ":project:gate_telemetry", researchDefName = "RR_GateTelemetry" };',
  '            List<ProjectRecord> initialProjects = BuildProjectTree(newId, request.CompletedProjects);'),
 ('            projects.Add(initialProject);',
  '            for (int index = 0; index < initialProjects.Count; index++) { projects.Add(initialProjects[index]); }'),
])

# The tree builder, placed beside the thing it builds.
p = 'src/RimroomsAsyncIndustries/Company/CampaignServices.cs'
s = io.open(p, encoding='utf-8').read()
helper = '''
        /// <summary>
        /// Every company project the loaded game has, as this branch's research list.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"all starts have same tech tree just
        /// differnt starting researches finished based on scenerio"*. Taken literally: the
        /// tree is built from the def database rather than from the scenario, so **it is the
        /// same tree for every start by construction**, and a scenario chooses only which of
        /// its entries begin finished.
        ///
        /// This replaces a single hardcoded `RR_GateTelemetry` record. That hardcoding meant a
        /// second project would have been invisible to every existing branch until somebody
        /// remembered to add it in three places; now adding one def reaches every start at
        /// once.
        ///
        /// Ordinal sort before anything is built, because def load order varies with the mod
        /// list and two players starting the same scenario must get the same branch.
        /// </summary>
        private static List<ProjectRecord> BuildProjectTree(string branchId, List<string> completed)
        {
            var finished = new HashSet<string>(StringComparer.Ordinal);
            if (completed != null)
            {
                for (int index = 0; index < completed.Count; index++)
                {
                    string name = completed[index];
                    if (string.IsNullOrWhiteSpace(name)) { continue; }
                    if (DefDatabase<Investigation.RimroomsProjectDef>.GetNamedSilentFail(name) == null)
                    {
                        Log.Warning("[Rimrooms][Company] Start names completed project '" + name +
                            "', which no longer exists; it is skipped and the branch begins without it.");
                        continue;
                    }
                    finished.Add(name);
                }
            }

            var definitions = new List<Investigation.RimroomsProjectDef>(
                DefDatabase<Investigation.RimroomsProjectDef>.AllDefsListForReading);
            definitions.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));

            var records = new List<ProjectRecord>();
            for (int index = 0; index < definitions.Count; index++)
            {
                Investigation.RimroomsProjectDef definition = definitions[index];
                if (definition == null || string.IsNullOrEmpty(definition.defName)) { continue; }
                bool done = finished.Contains(definition.defName);
                records.Add(new ProjectRecord
                {
                    id = branchId + ":project:" + definition.defName,
                    researchDefName = definition.defName,
                    completed = done,
                    // A project that begins finished has had its insight paid for by whoever
                    // ran this branch before you. Leaving it uncommitted would offer the player
                    // a "start" button on work that is already done.
                    insightCommitted = done,
                    workDone = done ? definition.workRequired : 0f,
                });
            }
            return records;
        }
'''
anchor = '        public CompanyActionResult InitializeBranch(BranchStartRequest request)'
assert anchor in s
s = s.replace(anchor, helper.lstrip('\n') + '\n' + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('project tree builder added')
