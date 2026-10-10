# -*- coding: utf-8 -*-
"""Close six rows. Status changes and appended closure notes only -- never a rewritten
description, so anyone reading the queue sees what was done and where."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "TODO.md")

s = io.open(PATH, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, "anchor missing: %r" % old[:90]
    assert s.count(old) == 1, "anchor not unique: %r" % old[:90]
    s = s.replace(old, new, 1)


ROOF = (u"**BUILT 0.12.36-dev.** `Area_BuildRoof` and `Area_NoRoof` as `RoofWorkProvider`, a "
        u"**third `Construction` family** rather than routes on the finishing one: that family's "
        u"continue giver is **82**, below Core's `BuildRoofs` (100) and `RemoveRoofs` (90), and a "
        u"continue giver below the work it travels for turns a committed worker around. So roof "
        u"work sits at 101/1 and the tuned numbers are untouched. `Area_SnowOrSandClear` and "
        u"`Area_PollutionClear` became routes on the **existing cleaning family**, whose continue "
        u"is already 22, above `CleanClearSnow` (10) and `CleanClearPollution` (0). Almost nothing "
        u"needed a presence substitute -- every condition takes the map explicitly and takes no "
        u"pawn. **The Backrooms rule still keeps itself**: `BackroomsContainment` empties "
        u"`Area_NoRoof` on a coordinate, so the family finds nothing there, and the proof asserts "
        u"the provider holds no Backrooms exception of its own. Record "
        u"`implementation/AREAS_AND_DEBRIEF_IMPLEMENTATION.md`, proof "
        u"`proof-areas-and-debrief.py`. Was: ")

# ------------------------------------------------------------------ 1215 / 1235 / 1239
sub(u"- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` "
    u"across a gate** — `research/ZONES_AND_AREAS_ACROSS_A_GATE.md`",
    u"- [x] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` "
    u"across a gate** — " + ROOF + u"`research/ZONES_AND_AREAS_ACROSS_A_GATE.md`")

sub(u"- [ ] **Three area types are not covered, and that is correct only until the far side of a "
    u"gate can be an ordinary world map.**",
    u"- [x] **Three area types are not covered, and that is correct only until the far side of a "
    u"gate can be an ordinary world map.** — **THE CONDITION EXPIRED AND THE WORK IS DONE, "
    u"0.12.36-dev.** The ordinary-map endpoint landed at 0.6.9-dev, so a registered site is a "
    u"world map that wants roofs, gets snow and can be polluted. **This row is the reason the "
    u"work was findable at all**: it recorded *why* the areas were uncovered rather than just "
    u"that they were. Was: ")

sub(u"- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear` "
    u"across a gate** — **now genuinely live as of 0.6.9-dev**",
    u"- [x] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear` "
    u"across a gate** — **BUILT 0.12.36-dev**, and the row's own instruction to *\"build it in "
    u"that checkpoint\"* was followed one checkpoint late rather than never. Was: **now genuinely "
    u"live as of 0.6.9-dev**")

# ------------------------------------------------------------------ 98 and 99
sub(u'- [ ] **"in the real world you can mine and build and explore directly behind the gates '
    u'with out actually effecting the gate"**',
    u'- [x] **"in the real world you can mine and build and explore directly behind the gates '
    u'with out actually effecting the gate"** — **PROVED 0.12.36-dev rather than built, because '
    u'it was already true.** Every reason a gate can stop working was enumerated — **six**: the '
    u'kill switch, power, the operator, two clocks, and the deliberate cutoff — and **not one '
    u'reads an adjacent cell**. Nothing in the gate calls `CellsAdjacent`. The proof asserts the '
    u'whole **set**, so a seventh reason cannot appear without this being reconsidered. The one '
    u'placement constraint is the approach cell (row 113, closed 0.12.27-dev): reserved against '
    u'**blocking** placement, flooring fine, every uncertainty accepted. Roofing behind a gate '
    u'became real work in the same checkpoint. Was: ')

sub(u'- [ ] **"unless there is connected need requipremd equipemnet directly required placemnets '
    u'behind the pgate doors"**',
    u'- [x] **"unless there is connected need requipremd equipemnet directly required placemnets '
    u'behind the pgate doors"** — **CLOSED 0.12.36-dev, and the row\'s premise turned out to be '
    u'wrong about this mod.** It says linked equipment constrains placement *"because a link has '
    u'a reach"*. `GateEquipmentLinks` deliberately has **no distance check and no line-of-sight '
    u'check** — owner direction was *"reach fare and through walls"*, and Core\'s own '
    u'`CompProperties_Facility` defaults (`maxDistance = 8f`, `requiresLOS = true`) are the '
    u'opposite of that, so the reach was removed rather than reused. **Same map and same branch '
    u'is the whole spatial rule.** The real constraints are power-net membership for anything '
    u'with a power component, and single ownership across gates. Was: ')

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("six rows closed in docs/TODO.md")

# ------------------------------------------------------------------ the research doc
RESEARCH = os.path.join(REPO, "docs", "research", "ZONES_AND_AREAS_ACROSS_A_GATE.md")
r = io.open(RESEARCH, encoding="utf-8").read()


def rsub(old, new):
    global r
    assert old in r, "research anchor missing: %r" % old[:80]
    assert r.count(old) == 1, "research anchor not unique: %r" % old[:80]
    r = r.replace(old, new, 1)


rsub(u"| `Area_BuildRoof` | `WorkGiver_BuildRoof` | **Not covered — and correctly so today.** "
     u"See below |",
     u"| `Area_BuildRoof` | `WorkGiver_BuildRoof` | **Covered 0.12.36-dev** by `roof-work`. Was "
     u"correctly uncovered while the far side was always a coordinate |")
rsub(u"| `Area_SnowOrSandClear` | `CleanClearSnowOrSand` | **Not covered — and correctly so "
     u"today.** See below |",
     u"| `Area_SnowOrSandClear` | `CleanClearSnowOrSand` | **Covered 0.12.36-dev** by a route on "
     u"`cleaning` |")
rsub(u"| `Area_PollutionClear` | `CleanClearPollution` (Biotech) | **Not covered — and correctly "
     u"so today.** See below |",
     u"| `Area_PollutionClear` | `CleanClearPollution` (Biotech) | **Covered 0.12.36-dev** by a "
     u"route on `cleaning`; null pollution grid without Biotech is the only gate |")
rsub(u"| `Area_NoRoof` | containment | **Deliberately emptied** on a Backrooms map every "
     u"interval. That is the containment rule, not a defect. Untouched on ordinary maps |",
     u"| `Area_NoRoof` | containment | **Still deliberately emptied** on a Backrooms map every "
     u"interval — that is the containment rule, not a defect. **Covered 0.12.36-dev** by "
     u"`roof-work` on ordinary maps, where the area is not emptied and roof removal is ordinary "
     u"work |")

rsub(u"- **`Area_BuildRoof`.** The construction deployment looks for `BuildingFrame`s, not roof "
     u"areas.",
     u"**All four were covered at 0.12.36-dev.** The condition each of these paragraphs attached "
     u"— *revisit when the ordinary-map endpoint lands* — was met at 0.6.9-dev, and the reasons "
     u"below are kept because they are why the work was findable: they record **why** the areas "
     u"were uncovered rather than only that they were.\n\n"
     u"- **`Area_BuildRoof`.** The construction deployment looks for `BuildingFrame`s, not roof "
     u"areas.")

io.open(RESEARCH, "w", encoding="utf-8", newline="").write(r)
print("research doc brought current")
