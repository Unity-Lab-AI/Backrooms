"""Survey: which defs this package ships have a label and a description, and which do not."""
import glob, io, os, re
import xml.etree.ElementTree as ET
from collections import defaultdict

MOD = 'Mod/Rimrooms - Async Industries/1.6'

# Def types RimWorld shows an info card or tooltip for, where a description is player-facing.
WANT_DESCRIPTION = {
    'ThingDef', 'TerrainDef', 'ResearchProjectDef', 'ThoughtDef', 'TraderKindDef',
    'WorldObjectDef', 'ScenarioDef', 'PawnKindDef', 'RecipeDef', 'ThingCategoryDef',
    'MainButtonDef', 'JobDef', 'WorkGiverDef', 'SoundDef', 'ScenPartDef', 'MapGeneratorDef',
}
# Types where a label is expected but a description is not a thing the game shows.
LABEL_ONLY = {'JobDef', 'WorkGiverDef', 'SoundDef', 'ScenPartDef', 'MapGeneratorDef', 'ThingCategoryDef'}

defs = {}          # defName -> (type, file, has_label, has_desc)
for path in sorted(glob.glob(os.path.join(MOD, 'Defs', '**', '*.xml'), recursive=True)):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print('PARSE FAIL', path, e)
        continue
    for node in root:
        name_node = node.find('defName')
        if name_node is None or not name_node.text:
            continue
        defs[name_node.text.strip()] = [
            node.tag,
            os.path.relpath(path, MOD).replace(os.sep, '/'),
            node.find('label') is not None and bool((node.findtext('label') or '').strip()),
            node.find('description') is not None and bool((node.findtext('description') or '').strip()),
        ]

# DefInjected can supply either.
inj_label, inj_desc = set(), set()
for path in glob.glob(os.path.join(MOD, 'Languages', '**', 'DefInjected', '**', '*.xml'), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root:
        key = node.tag
        if key.endswith('.label'):
            inj_label.add(key[: -len('.label')])
        elif key.endswith('.description'):
            inj_desc.add(key[: -len('.description')])

missing_label, missing_desc = [], []
by_type = defaultdict(int)
for name, (kind, path, has_label, has_desc) in sorted(defs.items()):
    by_type[kind] += 1
    label = has_label or name in inj_label
    desc = has_desc or name in inj_desc
    if not label:
        missing_label.append((kind, name, path))
    if not desc and kind in WANT_DESCRIPTION and kind not in LABEL_ONLY:
        missing_desc.append((kind, name, path))

print('defs declared: %d across %d types' % (len(defs), len(by_type)))
for kind in sorted(by_type):
    print('  %-34s %d' % (kind, by_type[kind]))
print('')
print('MISSING LABEL: %d' % len(missing_label))
for kind, name, path in missing_label[:40]:
    print('  %-34s %-36s %s' % (kind, name, path))
print('')
print('MISSING DESCRIPTION: %d' % len(missing_desc))
for kind, name, path in missing_desc[:60]:
    print('  %-34s %-36s %s' % (kind, name, path))
