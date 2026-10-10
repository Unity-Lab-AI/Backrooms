# -*- coding: utf-8 -*-
"""Retire the survey tag: def, recipe, job, scenario grant, keyed strings."""
import io
import os
import re

MOD = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6')
ARCHIVE = os.path.join('docs', 'implementation', 'historical-content', '0.10.7-dev')

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
start = text.index('  <ThingDef ParentName="RR_FieldItemBase">\n    <defName>RR_SurveyTag</defName>')
end = text.index('  <ThingDef ParentName="RR_FieldItemBase">\n    <defName>RR_SealedEvidenceCase</defName>')
io.open(os.path.join(ARCHIVE, 'RR_SurveyTag.thingdef.xml'), 'w', encoding='utf-8', newline='').write(text[start:end])
write(p, text[:start] + text[end:])
print('  retired the RR_SurveyTag ThingDef (archived)')


# --------------------------------------------------------------------------- the recipe
p = os.path.join(MOD, 'Defs', 'RecipeDefs', 'RR_FieldEquipmentRecipes.xml')
text = read(p)
start = text.index('  <RecipeDef ParentName="RR_FieldFabricationBase">\n    <defName>RR_MakeSurveyTags</defName>')
end = text.index('  <RecipeDef ParentName="RR_FieldFabricationBase">\n    <defName>RR_MakeEvidenceCase</defName>')
io.open(os.path.join(ARCHIVE, 'RR_MakeSurveyTags.recipedef.xml'), 'w', encoding='utf-8', newline='').write(text[start:end])
write(p, text[:start] + text[end:])
print('  retired the RR_MakeSurveyTags recipe (archived)')


# --------------------------------------------------------------------------- the job def
p = os.path.join(MOD, 'Defs', 'JobDefs', 'RR_InvestigationJobs.xml')
text = read(p)
block = re.search(r'  <JobDef>\s*\n\s*<defName>RR_DeployRouteAid</defName>.*?</JobDef>\n', text, re.S)
assert block, 'RR_DeployRouteAid JobDef not found'
io.open(os.path.join(ARCHIVE, 'RR_DeployRouteAid.jobdef.xml'), 'w', encoding='utf-8', newline='').write(block.group(0))
write(p, text[:block.start()] + text[block.end():])
print('  retired the RR_DeployRouteAid JobDef (archived)')


# --------------------------------------------------------------------------- the scenario grant
patch(os.path.join(MOD, 'Defs', 'ScenarioDefs', 'RR_Scenarios.xml'), [
    ('        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def>'
     '<thingDef>RR_SurveyTag</thingDef><count>6</count></li>',
     '        <!-- Six survey tags became eight glow pods. Core content, no cap, and a player\n'
     '             who wants more buys more; the retired tag was six because a kit check said so. -->\n'
     '        <li Class="ScenPart_StartingThing_Defined"><def>StartingThing_Defined</def>'
     '<thingDef>GlowPod</thingDef><count>8</count></li>'),
])


# --------------------------------------------------------------------------- keyed strings
FIELD = os.path.join(MOD, 'Languages', 'English', 'Keyed', 'RR_FieldAndThreats.xml')
text = read(FIELD)
retired = [
    'RR_Field_AidMismatch', 'RR_Field_RepeatedLabel', 'RR_Field_AidLabel', 'RR_Field_AidDeployed',
    'RR_Field_CannotDeploy', 'RR_Field_AidMissing', 'RR_Field_AidAlreadyPlaced',
    'RR_Event_RouteAidPlaced', 'RR_UI_PlaceTag', 'RR_UI_RecoverRouteAid',
]
kept = []
for line in text.split('\n'):
    name = re.match(r'\s*<(RR_[A-Za-z0-9_]+)>', line)
    if name and name.group(1) in retired:
        continue
    kept.append(line)
write(FIELD, '\n'.join(kept))
print('  retired %d keyed strings from RR_FieldAndThreats.xml' % len(retired))

EXP = os.path.join(MOD, 'Languages', 'English', 'Keyed', 'RR_Expedition.xml')
text = read(EXP)
kept = [l for l in text.split('\n') if not re.match(r'\s*<RR_Exp_Missing_RR_SurveyTag>', l)]
write(EXP, '\n'.join(kept))
print('  retired the survey-tag kit refusal')
