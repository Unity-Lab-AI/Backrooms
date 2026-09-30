"""Offline proof that revisit displacement actually displaces something.

Three independent ways this could quietly do nothing, each individually plausible:

  1. the candidate filter excludes every fixture,
  2. the `roll % 3` gate never opens for any candidate,
  3. the count for a given visit works out to zero.

Any of them would leave a feature that looks implemented and never fires. Mirrors
RevisitDisplacement.OnArrival exactly.
"""

MAX_MOVED = 3
OPENINGS_PER_EXTRA = 3


def roll(seed, openings, index):
    value = seed
    value = (value * 31 + openings * 7919) & 0xFFFFFFFF
    value = (value * 31 + index * 104729) & 0xFFFFFFFF
    if value >= 0x80000000:
        value -= 0x100000000
    return abs(value)


def wanted(openings):
    if openings <= 1:
        return 0
    return min(MAX_MOVED, 1 + (openings - 2) // OPENINGS_PER_EXTRA)


VISIT_SALT = 6151


def moved_count(seed, openings, candidates):
    want = wanted(openings)
    if want <= 0:
        return 0
    # Roughly a third of returns are left exactly as they were, so a player cannot learn
    # that coming back always moves something.
    if roll(seed, openings, VISIT_SALT) % 3 == 0:
        return 0
    moved = 0
    for index in range(candidates):
        if moved >= want:
            break
        if roll(seed, openings, index) % 3 == 0:
            moved += 1
    return moved


# A first visit must never change anything.
for seed in range(500):
    assert moved_count(seed, 1, 12) == 0, 'a first visit displaced something'

# The ladder has to actually be a ladder.
assert wanted(2) == 1
assert wanted(5) == 2
assert wanted(8) == 3
assert wanted(40) == 3, 'the cap does not hold on a long game'

# With a realistic number of dressed fixtures, a return must usually change something.
CANDIDATES = 12
returns = 0
changed = 0
totals = {}
for seed in range(400):
    for openings in range(2, 12):
        returns += 1
        n = moved_count(seed, openings, CANDIDATES)
        totals[n] = totals.get(n, 0) + 1
        if n:
            changed += 1

rate = 100.0 * changed / returns
print('returns simulated      : %d' % returns)
print('changed something      : %d (%.1f%%)' % (changed, rate))
print('distribution           : %s' % ', '.join(
    '%d moved x%d' % (k, totals[k]) for k in sorted(totals)))

assert changed > 0, 'NOTHING ever moved: the feature is a no-op'
assert 45.0 < rate < 85.0, ('returns change something %.1f%% of the time; it must be common '
                            'enough to be real and uncertain enough to be unnerving') % rate
assert totals.get(0, 0) >= 0

# A sparse room must not be assumed away: even with few candidates it should still fire often.
sparse = sum(1 for seed in range(400) if moved_count(seed, 3, 3) > 0)
print('sparse room, 3 fixtures: %d of 400 returns changed something' % sparse)
assert sparse > 120, 'a lightly dressed coordinate almost never changes'

# Deterministic: the same return is the same return.
for seed in (7, 99, 12345):
    for openings in (2, 4, 9):
        assert moved_count(seed, openings, CANDIDATES) == moved_count(seed, openings, CANDIDATES)

print('')
print('PASS: first visits never change, the count ladders 1-2-3 and caps, most but NOT all')
print('      returns change something, sparse rooms still fire, and a return replays identically')
