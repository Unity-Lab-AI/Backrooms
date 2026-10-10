# -*- coding: utf-8 -*-
"""Retire the sealed evidence case. Custody is a linked archive shelf now."""
import io
import os
import re

MOD = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6')
ARCHIVE = os.path.join('docs', 'implementation', 'historical-content', '0.10.9-dev')

for sub in ('1.6/Defs/ThingDefs_Items', '1.6/Defs/RecipeDefs', '1.6/Textures/Items/Field'):
    os.makedirs(os.path.join(ARCHIVE, *sub.split('/')), exist_ok=True)


def read(path):
    return io.open(path, encoding='utf-8-sig').read()


def write(path, text):
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)


def patch(path, pairs):
    text = read(path)
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:80])
        text = text.replace(old, new, 1)
    write(path, text)
    print('  patched %s (%d)' % (path, len(pairs)))


# --------------------------------------------------------------------------- the ThingDef
p = os.path.join(MOD, 'Defs', 'ThingDefs_Items', 'RR_FieldEquipment.xml')
text = read(p)
start = text.index('  <ThingDef ParentName="RR_FieldItemBase">\n    <defName>RR_SealedEvidenceCase</defName>')
end = text.index('  <ThingDef ParentName="RR_FieldItemBase">\n    <defName>RR_RouteRecording</defName>')
io.open(os.path.join(ARCHIVE, '1.6', 'Defs', 'ThingDefs_Items', 'RR_FieldEquipment.xml'),
        'w', encoding='utf-8', newline='').write(text[start:end])
write(p, text[:start] + text[end:])
print('  retired the RR_SealedEvidenceCase ThingDef (archived)')

# --------------------------------------------------------------------------- the recipe
p = os.path.join(MOD, 'Defs', 'RecipeDefs', 'RR_FieldEquipmentRecipes.xml')
text = read(p)
block = re.search(r'  <RecipeDef ParentName="RR_FieldFabricationBase">\s*\n\s*<defName>RR_MakeEvidenceCase</defName>.*?</RecipeDef>\n',
                  text, re.S)
assert block, 'RR_MakeEvidenceCase not found'
io.open(os.path.join(ARCHIVE, '1.6', 'Defs', 'RecipeDefs', 'RR_FieldEquipmentRecipes.xml'),
        'w', encoding='utf-8', newline='').write(block.group(0))
write(p, text[:block.start()] + text[block.end():])
print('  retired the RR_MakeEvidenceCase recipe (archived)')

# --------------------------------------------------------------------------- the scenario grant
patch(os.path.join(MOD, 'Defs', 'ScenarioDefs', 'RR_Scenarios.xml'), [
    ('        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def>'
     '<thingDef>RR_SealedEvidenceCase</thingDef><count>1</count></li>',
     '        <!-- The sealed evidence case was retired in 0.10.9-dev. Custody is a shelf linked\n'
     '             to a gate as a records archive, so the start grants the shelf instead of a\n'
     '             custom item whose only job was to exist somewhere on the map. -->\n'
     '        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def>'
     '<thingDef>Shelf</thingDef><count>2</count></li>'),
])

# --------------------------------------------------------------------------- the kit and lists
patch('src/RimroomsAsyncIndustries/Expedition/ExpeditionCargo.cs', [
    ('        private static readonly string[] KitDefs = { "RR_FieldRecorder", "RR_SealedEvidenceCase" };\n'
     '        private static readonly int[] KitCounts = { 1, 1 };',
     '        // The sealed evidence case left in 0.10.9-dev with its requirement. Custody is a\n'
     '        // shelf linked to a gate as a records archive, which is a place at headquarters\n'
     '        // rather than an item a crew has to remember to carry out and back.\n'
     '        private static readonly string[] KitDefs = { "RR_FieldRecorder" };\n'
     '        private static readonly int[] KitCounts = { 1 };'),
])

patch('src/RimroomsAsyncIndustries/Generation/FailedSiteRecovery.cs', [
    ('                "RR_SealedEvidenceCase", "TextBook", "RR_QuietPursuer",',
     '                "Shelf", "TextBook", "RR_QuietPursuer",'),
])

# --------------------------------------------------------------------------- keyed string
p = os.path.join(MOD, 'Languages', 'English', 'Keyed', 'RR_Expedition.xml')
text = read(p)
kept = [l for l in text.split('\n') if 'RR_Exp_Missing_RR_SealedEvidenceCase' not in l]
write(p, '\n'.join(kept))
print('  retired the evidence-case kit refusal')
