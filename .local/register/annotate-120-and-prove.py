# -*- coding: utf-8 -*-
"""Annotate the 0.12.0 record as corrected, and prove the natural depth cap."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


# ------------------------------------------------------------------ annotate, never rewrite
p = os.path.join(REPO, 'docs', 'implementation', 'SOLO_GROUP_START_IMPLEMENTATION.md')
sub(p, u"""**Dated record.** Describes the checkpoint as it was built. Never rewritten.""",
u"""**Dated record.** Describes the checkpoint as it was built. Never rewritten.

> ## ONE CLAIM IN THIS RECORD WAS CORRECTED THE SAME DAY
>
> Below, under *"Three things it deliberately does not do"*, this record says: **"There is no way
> home and finding one is the whole opening."**
>
> **That is wrong.** Owner direction, 2026-09-29, verbatim: *"and remember the solo/group start in
> a backroom needs to 100% have a exit to map natural portal on their first backrroms level with
> natural portals deeper to an extent till they would need to buidl theri own gate"*.
>
> The first level must hold a **guaranteed** natural portal out - not a discovered one, not a
> rarity draw. The body below is **left exactly as written**, because it is what the checkpoint
> shipped and the evidence trail depends on that. The correction is in `TODO.md`, in
> `FINALIZED.md`, and in the record for the checkpoint that fixes it.
>
> **Half of it was fixed immediately**, in the same session: natural portals now reach through
> depth 3 and no further, which is the *"to an extent"* half. The guaranteed exit itself is its
> own piece, because its destination is a world tile that does not exist yet.""")
print('0.12.0 record annotated')

# ------------------------------------------------------------------ prove the cap
p = os.path.join(REPO, '.local', 'register', 'proof-starts.py')
sub(p, u'''print("")
if failures:''',
u'''# --------------------------------------------------------------------------- the natural chain
# Owner direction: "with natural portals deeper to an extent till they would need to buidl theri
# own gate", and the extent chosen at the fork was through depth 3.
FRONTIER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                        "NaturalFrontierService.cs")
frontier = io.open(FRONTIER, encoding="utf-8-sig").read()

print("")
cap = re.search(r"MaximumNaturalDepth\\s*=\\s*(\\d+)", frontier)
check("the natural chain has a declared depth limit", cap is not None,
      "-- without one the Backrooms hands out free doorways forever and no gate is ever needed")
if cap:
    check("the natural depth limit is 3 (%s)" % cap.group(1), cap.group(1) == "3",
          "-- the owner chose through depth 3 at the fork")

# THE one that matters. The cap must be applied AFTER the way-out attempt, or a crew standing at
# the deepest natural band can never find a door home and the band becomes a trap. Invariant 28
# forbids an unavoidable failure, and this is exactly the shape one would take.
wayout = frontier.find("TryRecordWayOut(door, origin, campaign)")
capcheck = frontier.find("depth > MaximumNaturalDepth")
check("the way-out attempt runs before the depth cap",
      wayout != -1 and capcheck != -1 and wayout < capcheck,
      "-- the deepest natural band would become a trap with no door home")

# A refusal a player reads must be a real string, or they see the raw key.
KEYED = os.path.join(MOD, "Languages", "English", "Keyed")
keyed_text = ""
for path in glob.glob(os.path.join(KEYED, "*.xml")):
    keyed_text += io.open(path, encoding="utf-8-sig").read()
for key in sorted(set(re.findall(r'Refused\\("(RR_Frontier_\\w+)"\\)', frontier))):
    check("%s has a keyed string" % key, ("<" + key + ">") in keyed_text,
          "-- the player would be shown the raw key")

print("")
if failures:''')
print('proof extended with the natural chain')

import ast
ast.parse(io.open(p, encoding='utf-8').read())
print('proof-starts.py parses clean')
