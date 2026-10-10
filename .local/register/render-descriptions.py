import io

def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:70]
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('patched ' + path.split('/')[-1])

U = 'src/RimroomsAsyncIndustries/UI/'

# The facilities overview: say what the selected category is for, not just its name.
patch(U + 'OperationsFacilities.cs', [
 ('            List<FacilityBuildingObservation> rows = facilityReport.Buildings.Where(b => facilityCategory == null ||\n'
  '                (b.CategoryId ?? "") == facilityCategory).ToList();',
  '            // What the chosen category is actually for. Owner direction 2026-09-29: "all mod\n'
  '            // ingame decriptions and informational informations for everything is properly in\n'
  '            // the cards like the game does currently". A row of bare nouns tells a player\n'
  '            // nothing the word did not already tell them.\n'
  '            RimroomsFacilityCategoryDef chosen = string.IsNullOrEmpty(facilityCategory) ? null\n'
  '                : DefDatabase<RimroomsFacilityCategoryDef>.GetNamedSilentFail(facilityCategory);\n'
  '            if (chosen != null && !string.IsNullOrEmpty(chosen.description))\n'
  '            { listing.Label(chosen.description); }\n'
  '            List<FacilityBuildingObservation> rows = facilityReport.Buildings.Where(b => facilityCategory == null ||\n'
  '                (b.CategoryId ?? "") == facilityCategory).ToList();'),
])

# Procurement: the row already carries price and lead time. The description says what the
# thing is FOR, which is the part no number can tell you.
patch(U + 'OperationsProcurement.cs', [
 ('            if (zones.Count == 0) { listing.Label("RR_Proc_NoStockpiles".Translate()); }',
  '            if (selectedCatalog != null && !string.IsNullOrEmpty(selectedCatalog.description))\n'
  '            { listing.Label(selectedCatalog.description); }\n'
  '\n'
  '            if (zones.Count == 0) { listing.Label("RR_Proc_NoStockpiles".Translate()); }'),
])
