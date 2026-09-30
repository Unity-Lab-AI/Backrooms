"""Offline proof that the gate-width body-size ladder actually partitions real animals.

The degenerate outcomes this guards against are the same shape as the layout derangement's:
a threshold so high that every creature passes a 1x1 (the sizes would be decoration), or so
low that nothing passes anything (pack animals become unusable). Both would look like a
working feature.

Mirrors PortalTraversalPolicy.MaxBodySizeForWidth exactly.
"""
import glob
import os
import xml.etree.ElementTree as ET

SINGLE = 1.2
DOUBLE = 2.5
DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"


def max_body_size(width):
    if width <= 1:
        return SINGLE
    if width == 2:
        return DOUBLE
    return None


def fits(size, width):
    limit = max_body_size(width)
    return limit is None or size <= limit


# Every race the installed game ships, with its real body size.
races = {}
for path in glob.glob(os.path.join(DATA, '*', 'Defs', 'ThingDefs_Races', '*.xml')):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root:
        name = node.findtext('defName')
        body = node.findtext('race/baseBodySize')
        if not name or body is None:
            continue
        try:
            races[name.strip()] = float(body)
        except ValueError:
            pass

assert races, 'no races read; the game data path is wrong and this proof would be vacuous'

buckets = {1: [], 2: [], 3: []}
for name, size in races.items():
    for width in (1, 2, 3):
        if fits(size, width):
            buckets[width].append((size, name))

for width in buckets:
    buckets[width].sort()

# The ladder has to actually be a ladder.
assert len(buckets[1]) < len(buckets[2]) < len(buckets[3]), 'widths do not admit strictly more'
assert len(buckets[3]) == len(races), 'three wide must admit everything'
assert len(buckets[1]) > 0, 'one wide admits nothing, so no gate would be usable at the start'

# A person must always fit the narrowest gate there is, or the mod is unplayable.
human = races.get('Human')
assert human is not None and fits(human, 1), 'a person does not fit a one-wide gate'

# The pack animals a branch would actually want must need a wider gate, or width is decoration.
for pack in ('Muffalo', 'Dromedary'):
    if pack in races:
        assert not fits(races[pack], 1), '%s already fits a 1x1, so width buys nothing' % pack
        assert fits(races[pack], 2), '%s does not fit a 1x2, so no gate size is useful for it' % pack

print('races read            : %d' % len(races))
print('fit through 1 wide    : %d  (of %d)' % (len(buckets[1]), len(races)))
print('fit through 2 wide    : %d' % len(buckets[2]))
print('fit through 3 or more : %d' % len(buckets[3]))
print('')
print('largest that fits 1 wide : %s' % ', '.join('%s %.2f' % (n, s) for s, n in buckets[1][-3:]))
blocked_at_one = sorted(set(buckets[2]) - set(buckets[1]))
print('unlocked by going to 2   : %s' % ', '.join('%s %.2f' % (n, s) for s, n in blocked_at_one[:6]))
blocked_at_two = sorted(set(buckets[3]) - set(buckets[2]))
print('unlocked by going to 3   : %s' % ', '.join('%s %.2f' % (n, s) for s, n in blocked_at_two[:6]))
print('')
print('PASS: strictly widening ladder, a person always fits, pack animals genuinely need a wider gate')
