# -*- coding: utf-8 -*-
"""Extend proof-remote-sites with arc 5's exit plan."""
import ast
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-remote-sites.py')
s = io.open(p, encoding='utf-8').read()

anchor = '''print("")
if failures:'''
assert anchor in s, 'tail anchor missing'

block = '''# --------------------------------------------------------------------------- the exit plan
# Arc 5 names an "exit plan" among what a remote site needs. A gate could only ever be designated
# at the headquarters, because `SameNativeHeadquartersThing` compared `parent.Map` against
# `campaign.Headquarters` -- so the exit plan was unreachable however many sites a branch held.
binding = strip_comments(io.open(os.path.join(SRC, "Gate", "NativeGateBinding.cs"),
                                 encoding="utf-8-sig").read())
emergence = strip_comments(io.open(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs"),
                                   encoding="utf-8-sig").read())

print("")
check("the branch can say where it operates", "public bool OperatesAt" in sites,
      "-- a gate would have nowhere but the headquarters to stand")
check("operating and receiving share one place-set",
      "private bool IsBranchPlace" in sites
      and "public bool CanReceiveDeliveryAt(Map map) { return IsBranchPlace(map); }" in sites
      and "public bool OperatesAt(Map map) { return IsBranchPlace(map); }" in sites,
      "-- two definitions of the branch's own places would drift apart")

# THE change. The gate no longer pins itself to the headquarters map.
check("the gate no longer requires the headquarters map",
      "parent.Map == campaign.Headquarters" not in binding,
      "-- arc 5's exit plan would stay unreachable")
check("the gate asks where the branch operates",
      "campaign.OperatesAt(parent.Map)" in binding,
      "-- any map at all could host a company gate")

# THE consequence, and it is the good one. A gate at a site needs its own equipment AT that site.
check("gate infrastructure must stand on the gate's own map",
      "thing.Map == parent.Map" in binding,
      "-- a remote gate could be run off the equipment back at headquarters, which is the whole "
      "thing arc 5 says a site must not get for free")

# A designated gate must never appear inside a Backrooms coordinate. It is excluded by
# construction -- a coordinate can never be registered -- which is the check nobody can forget.
place = re.search(r"private bool IsBranchPlace\\(Map map\\).*?\\n        \\}", sites, re.S)
place_text = place.group(0) if place else ""
check("the place-set was found", bool(place_text))
check("the place-set admits only the headquarters and registered sites",
      bool(place_text) and "headquarters == map" in place_text and "record.Live" in place_text
      and "RimroomsDestinationMapParent" not in place_text,
      "-- a coordinate admitted here would host a designated gate, against invariant 12")

# A way out may come up at a site too, and that came free from the ownership predicate rather
# than from a second rule. Assert it still routes that way.
check("a way out may come up anywhere the branch owns",
      "campaign.OwnsMap(map)" in emergence,
      "-- emergence anchors would be headquarters-only again")
check("a way out still refuses a coordinate",
      "map.Parent is RimroomsDestinationMapParent" in emergence,
      "-- a way out could come up inside the Backrooms, which is where it leads FROM")

# The refusal a player reads must no longer say "headquarters map" now that it is not true.
check("the binding refusal no longer claims headquarters only",
      "on the active company headquarters map" not in keyed,
      "-- the message would contradict what the code now allows")

''' + anchor

s = s.replace(anchor, block, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('proof extended with the exit plan')
ast.parse(s)
print('proof-remote-sites.py parses clean')
