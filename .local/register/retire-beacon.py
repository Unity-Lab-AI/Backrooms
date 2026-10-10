import io, re

M = 'Mod/Rimrooms - Async Industries/1.6/'

def cut(path, start_marker, encoding='utf-8-sig'):
    """Remove the whole <ThingDef>/<RecipeDef> block containing the marker."""
    full = M + path
    s = io.open(full, encoding=encoding).read()
    idx = s.index(start_marker)
    open_at = s.rindex('  <', 0, idx)
    tag = s[open_at:].split('>', 1)[0].lstrip(' <').split(' ')[0]
    close = '</%s>' % tag
    end = s.index(close, idx) + len(close)
    # Take the trailing newline with it.
    while end < len(s) and s[end] in '\r\n':
        end += 1
    removed = s[open_at:end]
    s = s[:open_at] + s[end:]
    io.open(full, 'w', encoding=encoding, newline='').write(s)
    print('removed %s block (%d chars) from %s' % (tag, len(removed), path))

cut('Defs/ThingDefs_Items/RR_FieldEquipment.xml', '<defName>RR_ReturnBeacon</defName>')
cut('Defs/RecipeDefs/RR_FieldEquipmentRecipes.xml', '<defName>RR_MakeReturnBeacon</defName>')

# The scenario no longer hands one out.
p = M + 'Defs/ScenarioDefs/RR_Scenarios.xml'
s = io.open(p, encoding='utf-8-sig').read()
line = [l for l in s.split('\n') if 'RR_ReturnBeacon' in l]
assert len(line) == 1
s = s.replace(line[0] + '\n', '', 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('scenario grant removed')

# Its refusal string has nothing left to refuse.
p = M + 'Languages/English/Keyed/RR_Expedition.xml'
s = io.open(p, encoding='utf-8-sig').read()
s, n = re.subn(r'[ \t]*<RR_Exp_Missing_RR_ReturnBeacon>.*?</RR_Exp_Missing_RR_ReturnBeacon>\r?\n', '', s, flags=re.S)
assert n == 1
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('keyed string removed')
