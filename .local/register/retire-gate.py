import io, json, codecs

M = 'Mod/Rimrooms - Async Industries/1.6/'

# --- allowlist ------------------------------------------------------------
p = 'tools/package-files.json'
raw = io.open(p, encoding='utf-8-sig').read()
data = json.loads(raw)
key = 'files' if 'files' in data else None
if key is None:
    for k, v in data.items():
        if isinstance(v, list) and any(isinstance(i, str) and i.endswith('.xml') for i in v):
            key = k
            break
assert key, 'could not find the file list in package-files.json'

removed = [
    '1.6/Defs/ThingDefs_Buildings/RR_GateBuildings.xml',
    '1.6/Defs/ThingDefs_Buildings/RR_BackroomsFixtures.xml',
    '1.6/Defs/ThingDefs_Buildings/RR_InvestigationBuildings.xml',
    '1.6/Defs/TerrainDefs/RR_LiminalFloors.xml',
    '1.6/Languages/English/DefInjected/ThingDef/RR_GateBuildings.xml',
    '1.6/Languages/English/DefInjected/TerrainDef/RR_LiminalFloors.xml',
    '1.6/Textures/Buildings/Gate/RR_EmergencyCutoff.png',
    '1.6/Textures/Buildings/Gate/RR_GateConsole.png',
    '1.6/Textures/Buildings/Gate/RR_MachineGate.png',
    '1.6/Textures/Buildings/Gate/RR_UtilityGenerator.png',
    '1.6/Textures/Buildings/Lab/RR_FieldAnalysisBench.png',
    '1.6/Textures/Buildings/Rooms/RR_SiteFluorescent.png',
    '1.6/Textures/Terrain/RR_FadedInstitutionalCarpet.png',
]
before = len(data[key])
for entry in removed:
    assert entry in data[key], 'not in allowlist: ' + entry
    data[key].remove(entry)
assert len(data[key]) == before - len(removed)
out = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
io.open(p, 'w', encoding='utf-8-sig', newline='').write(out)
print('allowlist: %d -> %d entries' % (before, len(data[key])))


def patch(path, pairs):
    full = M + path
    s = io.open(full, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:60]
        s = s.replace(old, new, 1)
    io.open(full, 'w', encoding='utf-8-sig', newline='').write(s)
    print('patched ' + path)


# The assembly bill lives on the Core machining table now. A comms console cannot host a
# bill at all, so the machining table is the only native bill giver the gate ever had.
patch('Defs/RecipeDefs/RR_GateRecipes.xml', [
    ('<recipeUsers><li>RR_GateConsole</li><li>TableMachining</li></recipeUsers>',
     '<recipeUsers><li>TableMachining</li></recipeUsers>'),
])

patch('Defs/WorkGiverDefs/RR_GateWork.xml', [
    ('<fixedBillGiverDefs><li>RR_GateConsole</li></fixedBillGiverDefs>',
     '<fixedBillGiverDefs><li>TableMachining</li></fixedBillGiverDefs>'),
])

# The facilities overview lists what a branch actually has. The gate and its control are
# Core objects now, so the category names the Core objects a gate is designated onto.
patch('Defs/RimroomsFacilityDefs/RR_FacilityCategories.xml', [
    ('<buildingDefNames><li>RR_MachineGate</li><li>RR_GateConsole</li><li>RR_EmergencyCutoff</li></buildingDefNames>',
     '<buildingDefNames><li>Door</li><li>Autodoor</li><li>CommsConsole</li><li>PowerSwitch</li></buildingDefNames>'),
    ('<buildingDefNames><li>RR_FieldAnalysisBench</li><li>SimpleResearchBench</li><li>HiTechResearchBench</li><li>MultiAnalyzer</li></buildingDefNames>',
     '<buildingDefNames><li>SimpleResearchBench</li><li>HiTechResearchBench</li><li>MultiAnalyzer</li></buildingDefNames>'),
])
print('done')
