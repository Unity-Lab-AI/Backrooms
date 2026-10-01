"""Offline proof that facility planning actually produces facilities.

The failure this guards against is the one the layout derangement nearly shipped with: a
planner whose constraints are each individually reasonable and which, assembled, produces
nothing at all. Half of every coordinate is a required quiet room and one more is the
threshold, so the pool a facility can be built from is small before any roll happens -- it
is entirely possible to write this and have it never once form a group.

Mirrors FacilityPlanner.Plan and Grow, including the quiet-room exclusion.
"""
import math
import re

MIN_ROOMS = 2
MAX_ROOMS = 6
ELIGIBLE_SHARE = 0.6  # mirrors FacilityPlanner.EligibleShare -- CHECKED below, not assumed
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
print('PASS: facilities form, are contiguous, bounded 2-6, never consume a quiet or threshold room,')
print('      leave the quiet guarantee intact, and replan identically from the same seed')

# --------------------------------------------------------------------------- source claims
# **THE MODEL ABOVE HAD NO SOURCE CLAIMS AND DRIFTED.** It carried `MAX_ROOMS = 4` and
# `ELIGIBLE_SHARE = 0.45` with a comment saying they must mirror the C# exactly, and nothing
# checked that they did -- so when the planner moved to 6 and 0.6 this proof kept passing while
# asserting bounds the code no longer used. `proof-coordinate-layout.py` already wrote the rule
# down: the model asserts the property, a source claim asserts the code still computes it, and
# one without the other is the mention-versus-assertion defect.
import io as _io
import os as _os

_REPO = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))


def _read(*parts):
    return _io.open(_os.path.join(_REPO, *parts), encoding="utf-8-sig").read()


facility_source = _read("src", "RimroomsAsyncIndustries", "Generation", "FacilityPlanner.cs")
archetype_source = _read("Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                         "RimroomsRoomArchetypeDefs", "RR_RoomArchetypes.xml")

_failures = []


def _claim(label, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", label, detail if not condition else ""))
    if not condition:
        _failures.append(label)


print("")
print("source claims -- the model above is only worth its agreement with these")

_claim("THE MODELLED BOUNDS ARE THE CODE'S BOUNDS",
       ("private const int MinRooms = %d;" % MIN_ROOMS) in facility_source
       and ("private const int MaxRooms = %d;" % MAX_ROOMS) in facility_source
       and ("private const float EligibleShare = %gf;" % ELIGIBLE_SHARE) in facility_source,
       "-- read out of FacilityPlanner.cs rather than trusted. This proof asserted 2-4 against "
       "its own copy while the code said 2-6, and passed")

# Owner: *"facilitys and buildings and neighboorhoods and complexes and shools and hospitals and
# military and storages need loot inside of them too"*. `Anchors` opened with
# `coordinate.Depth <= 1` and returned null, so a FIRST LEVEL HAD NO INSTITUTIONS AT ALL -- the
# fourth system found gated on the coordinate's own depth rather than on distance from the
# arrival.
_claim("INSTITUTIONS REACH A FIRST LEVEL",
       "if (coordinate == null || coordinate.Rooms == null) { return null; }" in facility_source
       and "coordinate.Depth <= 1) { return null; }" not in facility_source,
       "-- the global depth gate is GONE, not bypassed")

_claim("and the arrival still stays sparse, measured per room",
       "RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth) <= 1"
       in facility_source,
       "-- the property the gate protected is kept and measured per room, by the SAME function "
       "the archetypes, the inhabitants, the events and the wall materials all read. A room the "
       "dressing treats as deep and the facility planner treats as shallow cannot exist")

# Owner: *"...need loot inside of them too"*. Four of the sixteen archetypes carried none.
_blocks = archetype_source.split("<RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>")[1:]
_without = []
for _block in _blocks:
    _name = re.search(r"<defName>(.*?)</defName>", _block)
    if _name is None:
        continue
    if "<category>" not in _block:
        _without.append(_name.group(1))

_claim("EVERY ARCHETYPE HOLDS SOMETHING WORTH CARRYING OUT",
       len(_blocks) >= 16 and not _without,
       "-- %d archetype(s) carry no loot at all: %s. The office, the nursery, the gallery and the "
       "duplicate were the four" % (len(_without), ", ".join(_without) or "none"))

if _failures:
    print("")
    print("PROOF FAILED: %d source claim(s)" % len(_failures))
    raise SystemExit(1)
