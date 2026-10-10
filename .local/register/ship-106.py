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
      [('<Version>0.10.5-dev</Version>', '<Version>0.10.6-dev</Version>')])
patch('Mod/Rimrooms - Async Industries/About/About.xml',
      [('0.10.5-dev', '0.10.6-dev')])
patch('README.md', [('**Current development version: 0.10.5-dev.**',
                     '**Current development version: 0.10.6-dev.**')])

# --------------------------------------------------------------------------- CHANGELOG
entry = u"""## 0.10.6-dev - 2026-09-29 - the documents use the mod's own words

- **The documents you read now call things what the game calls them.** The gate is the gate, the connection is the link it holds open, the threshold is where you arrive. The readme, the how-to, the design and scenario documents, the compatibility notes and the research notes were still using the words the game stopped using two versions ago.
- **Eleven walls of text broken up.** The readme opened with a 1,275-character paragraph; the design document had a 1,274-character one. They are lists and short paragraphs now, because that is what they always were underneath.
- **One of those walls was also out of date.** The readme's status paragraph still cited the 0.2.0 build record and sprites that were retired in 0.9.0-dev.
- **Two rules that were superseded and still written down as current.** The design and scenario documents both said gate and portal were one word, and both said nothing ever crosses a gate on its own - which stopped being true when pursuit and incursion were added.
- **Words quoted from somewhere else are never rewritten.** The A24 synopsis calls what appears in the basement a doorway; that is the synopsis's word and it stays, marked as a quotation.

Full record: [the documents use the mod's own words](docs/implementation/READER_FACING_DOCS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
patch('CHANGELOG.md', [(u'## 0.10.5-dev - 2026-09-29', entry + u'## 0.10.5-dev - 2026-09-29')],
      enc='utf-8')

# --------------------------------------------------------------------------- TODO
patch('docs/TODO.md', [
    (u'- [ ] **"did we finish up that doc regress work"** - **partly.',
     u'- [x] **"did we finish up that doc regress work"** - **answered with a measurement, and '
     u'the gap it named closed for the reader-facing set in 0.10.6-dev. Was: partly.'),
    (u'- [ ] **"the later stuff i said about cleaning up text walls for everything making them '
     u'a pleasure to read"** - **partly.',
     u'- [x] **"the later stuff i said about cleaning up text walls for everything making them '
     u'a pleasure to read"** - **eleven walls broken up in the reader-facing set in 0.10.6-dev, '
     u'and the rule now fails the build. Was: partly.'),
    (u'- [ ] **"lets make sure the docs ... are proper to backrrooms universe and rimworld '
     u'gameplay style"** - the document half of the direction above: the gate vocabulary and '
     u'the readability rule leave the game and reach the living documents, enforced rather than '
     u'swept once.',
     u'- [x] **"lets make sure the docs ... are proper to backrrooms universe and rimworld '
     u'gameplay style"** - **BUILT 0.10.6-dev.** The gate vocabulary and the readability rule '
     u'leave the game and reach the living documents, enforced rather than swept once.\n'
     u'  - `check-doc-conformance.py` gained two rules over a named **reader-facing set** of '
     u'eleven documents: the banned vocabulary, and a paragraph-wall rule at 700 characters '
     u'grounded in the documents already rewritten for readability, which top out at 542.\n'
     u'  - **The boundary is a real distinction, not a convenience.** These eleven describe the '
     u'mod to a person. An internal design document describes the code, whose own identifiers '
     u'are `Portals/` and `PortalCrossingService`; rewriting the prose around them would make '
     u'the documents disagree with the source, which is worse than an old word.\n'
     u'  - **Still open, counted rather than rediscovered:** the retired word appears **262 '
     u'more times in prose across the internal design documents**, excluding code spans, file '
     u'names, the branch name and owner quotations. That sweep needs the code-identifier '
     u'exemption written into the rule before it can run.\n'
     u'  - Two superseded rules were found still written as current: gate and portal as one '
     u'word, and nothing-ever-crosses-on-its-own. Both corrected.\n'
     u'  - Record: `implementation/READER_FACING_DOCS_IMPLEMENTATION.md`.'),
], enc='utf-8')
print('ledgers updated')
