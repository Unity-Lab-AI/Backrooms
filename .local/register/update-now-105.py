# -*- coding: utf-8 -*-
import io

# README
p = 'README.md'
s = io.open(p, encoding='utf-8-sig').read()
assert '**Current development version: 0.10.4-dev.**' in s
s = s.replace('**Current development version: 0.10.4-dev.**',
              '**Current development version: 0.10.5-dev.**', 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('README version claim updated')

# NOW.md
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()

pairs = [
    ('| Published | **0.10.4-dev**.',
     '| Published | **0.10.5-dev**.'),
    ('| Checkers | **six**, all passing |',
     '| Checkers | **seven**, all passing |'),
    ('## What shipped this session, 0.7.1 → 0.10.4',
     '## What shipped this session, 0.7.1 → 0.10.5'),
    ('7. **All six checkers**: `check-package-integrity.py`, `check-keyed-strings.py`, '
     '`check-dlc-gating.py`, `check-info-cards.py`, `check-doc-conformance.py`, '
     '`research/audit-gate0.py`.',
     '7. **Every checker**: `check-package-integrity.py`, `check-keyed-strings.py`, '
     '`check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, '
     '`check-doc-conformance.py`, `research/audit-gate0.py`. There are seven.'),
    ('| 0.10.4 | **The register checked backwards** — a LAW, a query tool, a real defect; '
     'plus a readable description |',
     '| 0.10.4 | **The register checked backwards** — a LAW, a query tool, a real defect; '
     'plus a readable description |\n'
     '| 0.10.5 | **Every surface the game speaks through** — a seventh checker measured '
     'against Core per display surface, and the alerts readout, which this mod used none of |'),
    ('- **Check the register first** (LAW).',
     '- **Check the register first** (LAW).'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

# New invariants, appended to the method section rather than renumbering anything.
anchor = ('81. **Do not quote a banned string verbatim in a living document**')
assert anchor in s
end = s.index('\n', s.index(anchor))
addition = (
    '\n82. **RimWorld has a different convention per display surface, not one voice.** A float '
    'menu row ends with a full stop 7% of the time in Core; an explanatory tooltip does 93% of '
    'the time. Writing either in the other\'s register is the mistake.'
    '\n83. **Measure a surface, never a file.** The first run of `check-display-style.py` '
    'reported seven faults that were not faults, every one from sampling `Letters.xml` or '
    '`GameplayCommands.xml` alone when the surface spans several files. The baselines were '
    'corrected, not the text.'
    '\n84. **A census counts the zeroes.** *"to include all"* is only actionable if the report '
    'names the surfaces the mod uses **none** of. That is how the alerts readout was found '
    'unused. A zero is a question, not a failure.'
    '\n85. **A count printed with no rule behind it says so.** The inspect pane is counted and '
    'not ruled on, because Core builds inspect lines from strings scattered across its keyed '
    'files and there is no clean population to measure. A stated limit is not a forgotten one.'
    '\n86. **Cache an alert scan on the tick AND the game object.** Core calls `GetReport` on a '
    'rotating one-in-twenty-four schedule. Keying a cache on the tick alone hands a second save '
    'loaded at the same tick the first save\'s despawned components.'
)
s = s[:end] + addition + s[end:]

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md updated for 0.10.5-dev')
