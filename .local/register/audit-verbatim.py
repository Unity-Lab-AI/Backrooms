"""Audit: is every owner direction from this session recorded verbatim in TODO.md?

Distinctive fragments are used rather than whole sentences, because a fragment that is
unique to one direction proves the direction is present without depending on how it was
line-wrapped.
"""
import io

TODO = io.open('docs/TODO.md', encoding='utf-8').read()
NOW = io.open('docs/NOW.md', encoding='utf-8').read()
FINAL = io.open('docs/FINALIZED.md', encoding='utf-8').read()

directions = [
 ('spin-up / ramp',        'neededs to be a ramp up process that takes a bit of time'),
 ('gates are blue doors',  'a bue tint and maybe a blue light glow hue around it'),
 ('gate sizes',            'ther are 1x1 1x2 and 1x3 and 2x3 gate doors'),
 ('same tech tree',        'all starts have same tech tree just differnt starting researches'),
 ('chase to the gate',     'kill them all the way to the gate'),
 ('come through portal',   'they can come through the portal into your base'),
 ('logical order',         'order needs to be logical and your intelkligent educated choise'),
 ('info cards',            'informational informations for everything is properly in the cards'),
 ('glow pods uncapped',    'lets not limit the amount as a backrooms instance can have 100s of rooms'),
 ('glow pod colour',       'maybe lets have the glow pods color setable'),
 ('colour means types',    'color means differnt types of the needs markers'),
 ('doc drift',             'updating old out of date docs, readmes, how tos'),
 ('unified gate naming',   'we need a unified name throught the entire mode'),
 ('ask do not flag',       'dopnt flag shit'),
 ('fallback multi doors',  'the fallback is okay of building mulitple doors 1x1'),
 ('no crossing limits',    'in vinilla any number of pawns can use a door at once'),
 ('cannot expand working', 'gate doors expansions can NOT be done on a working gate'),
]

missing_todo, present = [], []
for label, fragment in directions:
    where = []
    if fragment in TODO:
        where.append('TODO')
    if fragment in NOW:
        where.append('NOW')
    if fragment in FINAL:
        where.append('FINALIZED')
    if 'TODO' in where:
        present.append((label, where))
    else:
        missing_todo.append((label, where, fragment))

print('owner directions checked : %d' % len(directions))
print('verbatim in TODO.md      : %d' % len(present))
print('NOT in TODO.md           : %d' % len(missing_todo))
print('')
for label, where in present:
    print('  OK      %-22s  also in: %s' % (label, ', '.join(w for w in where if w != 'TODO') or '-'))
if missing_todo:
    print('')
    print('  MISSING FROM TODO.md:')
    for label, where, fragment in missing_todo:
        print('  MISSING %-22s  found in: %s' % (label, ', '.join(where) or 'NOWHERE'))
        print('          fragment: %s' % fragment)
