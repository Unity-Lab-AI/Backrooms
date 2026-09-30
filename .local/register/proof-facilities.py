"""Offline proof that facility planning actually produces facilities.

The failure this guards against is the one the layout derangement nearly shipped with: a
planner whose constraints are each individually reasonable and which, assembled, produces
nothing at all. Half of every coordinate is a required quiet room and one more is the
threshold, so the pool a facility can be built from is small before any roll happens -- it
is entirely possible to write this and have it never once form a group.

Mirrors FacilityPlanner.Plan and Grow, including the quiet-room exclusion.
"""
import math

MIN_ROOMS = 2
MAX_ROOMS = 4
ELIGIBLE_SHARE = 0.45  # must mirror FacilityPlanner.EligibleShare exactly
QUIET_FRACTION = 0.5


def roll(seed, room_index, salt):
    value = seed
    value = (value * 31 + room_index) & 0xFFFFFFFF
    value = (value * 31 + salt) & 0xFFFFFFFF
    if value >= 0x80000000:
        value -= 0x100000000
    return abs(value)


def room_rank(seed, room_index):
    r = (seed * 2654435761 + (room_index * 7919 + 0x5155) * 2246822519) & 0xFFFFFFFF
    return r


def quiet_rooms(seed, count):
    required = max(1, math.ceil(count * QUIET_FRACTION))
    if required >= count:
        return set(range(count))
    ranked = sorted(range(count), key=lambda i: (room_rank(seed, i), i))
    return set(ranked[:required])


def plan(seed, count, links):
    """links: index -> list of adjacent indices. Room 0 is the threshold."""
    if count < MIN_ROOMS + 1:
        return {}
    quiet = quiet_rooms(seed, count)
    eligible = {i for i in range(count) if i != 0 and i not in quiet}
    if len(eligible) < MIN_ROOMS:
        return {}
    budget = int(len(eligible) * ELIGIBLE_SHARE)
    if budget < MIN_ROOMS:
        return {}

    anchors, taken, spent = {}, set(), 0
    for start in sorted(eligible):
        if spent + MIN_ROOMS > budget:
            break
        if start in taken:
            continue
        if roll(seed, start, 7919) % 2 == 0:
            continue
        wanted = MIN_ROOMS + (roll(seed, start, 104729) % (MAX_ROOMS - MIN_ROOMS + 1))
        wanted = min(wanted, budget - spent)
        if wanted < MIN_ROOMS:
            break
        group = grow(links, eligible, taken, start, wanted)
        if len(group) < MIN_ROOMS:
            continue
        group.sort()
        anchor = group[0]
        for member in group:
            anchors[member] = anchor
            taken.add(member)
        spent += len(group)
    return anchors


def grow(links, eligible, taken, start, wanted):
    group, frontier, seen = [start], [start], {start}
    while len(group) < wanted and frontier:
        nxt = []
        for node in frontier:
            for candidate in sorted(links.get(node, [])):
                if candidate in seen:
                    continue
                seen.add(candidate)
                if candidate not in eligible or candidate in taken:
                    continue
                group.append(candidate)
                nxt.append(candidate)
                if len(group) >= wanted:
                    return group
        frontier = nxt
    return group


def chain_with_branches(count):
    """A plausible coordinate: a spine with occasional branches, like the planner builds."""
    links = {i: [] for i in range(count)}
    for i in range(1, count):
        parent = i - 1 if i % 3 else max(0, i - 2)
        links[i].append(parent)
        links[parent].append(i)
    return links


sizes = [8, 10, 12, 14, 16, 20, 24]
total_coords = 0
with_facility = 0
group_sizes = []
for count in sizes:
    links = chain_with_branches(count)
    quiet_guard = max(1, math.ceil(count * QUIET_FRACTION))
    for seed in range(400):
        total_coords += 1
        anchors = plan(seed, count, links)
        if not anchors:
            continue
        with_facility += 1

        groups = {}
        for room, anchor in anchors.items():
            groups.setdefault(anchor, []).append(room)
        quiet = quiet_rooms(seed, count)
        for anchor, members in groups.items():
            assert MIN_ROOMS <= len(members) <= MAX_ROOMS, 'group out of bounds: %d' % len(members)
            assert anchor == min(members), 'anchor is not the lowest index'
            for m in members:
                assert m not in quiet, 'a quiet room was consumed by a facility'
                assert m != 0, 'the threshold room was consumed by a facility'
            # Every member must be reachable from the anchor through other members.
            reach, frontier = {anchor}, [anchor]
            while frontier:
                node = frontier.pop()
                for nb in links.get(node, []):
                    if nb in members and nb not in reach:
                        reach.add(nb)
                        frontier.append(nb)
            assert reach == set(members), 'a facility is not contiguous'
        # The quiet guarantee is untouched.
        assert len(quiet) >= quiet_guard

        # Determinism: the same seed must produce the same plan.
        assert plan(seed, count, links) == anchors

rate = 100.0 * with_facility / total_coords
print('coordinates simulated : %d across sizes %s' % (total_coords, sizes))
print('with a facility       : %d (%.1f%%)' % (with_facility, rate))

assert with_facility > 0, 'NO coordinate ever formed a facility: the planner is a no-op'
assert rate > 40.0, 'facilities are too rare to be a feature (%.1f%%)' % rate
assert rate < 100.0, 'every coordinate has one, so a plain coordinate never exists'
print('')
print('PASS: facilities form, are contiguous, bounded 2-4, never consume a quiet or threshold room,')
print('      leave the quiet guarantee intact, and replan identically from the same seed')
