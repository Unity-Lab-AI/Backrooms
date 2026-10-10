# -*- coding: utf-8 -*-
import io

def patch(path, pairs, enc='utf-8-sig'):
    text = io.open(path, encoding=enc).read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:70])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding=enc, newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


patch('src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj',
      [('<Version>0.10.6-dev</Version>', '<Version>0.10.7-dev</Version>')])

text = io.open('Mod/Rimrooms - Async Industries/About/About.xml', encoding='utf-8-sig').read()
assert '0.10.6-dev' in text
io.open('Mod/Rimrooms - Async Industries/About/About.xml', 'w', encoding='utf-8-sig',
        newline='').write(text.replace('0.10.6-dev', '0.10.7-dev'))
print('  bumped About.xml')

patch('README.md', [('**Current development version: 0.10.6-dev.**',
                     '**Current development version: 0.10.7-dev.**')])

entry = u"""## 0.10.7-dev - 2026-09-29 - the survey tag becomes a glow pod

- **Route markers are glow pods now.** The custom survey tag is gone. You set down an ordinary Core glow pod and mark it, the same way you designate a door as a gate.
- **The colour is what it means.** Route home, cleared, danger, supply cache, unexplored lead - five markers, five colours, readable from the far end of a corridor without selecting anything.
- **No limit on how many.** Not per room, not per coordinate, not per map. The old tag allowed exactly one per room and made dispatch refuse a crew carrying fewer than six.
- **A marked pod stops ageing.** A plain glow pod dies after about twenty days. A way home that expires is not a way home, so marking one holds it. Unmark it and it starts ageing again.
- **A glow pod you find in the wild is untouched.** Same green light, same lifespan. It just gains a button.
- **A marked junction can now actually counter a corridor distortion.** That outcome existed in the code and could never happen: it tested for a return beacon, which was retired two versions ago, so the condition was permanently false.
- Dispatch no longer refuses a crew over survey tags, the deploy order and its job are gone, and the company catalogue sells glow pods by the crate.

Full record: [the survey tag becomes a glow pod](docs/implementation/GLOW_POD_MARKERS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
patch('CHANGELOG.md', [(u'## 0.10.6-dev - 2026-09-29', entry + u'## 0.10.6-dev - 2026-09-29')],
      enc='utf-8')

patch('docs/TODO.md', [
    (u'- [ ] **Survey tag → Core `GlowPod`.**', u'- [x] **Survey tag → Core `GlowPod`.**'),
], enc='utf-8')
