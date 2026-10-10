# -*- coding: utf-8 -*-
"""CHANGELOG, FINALIZED, NOW and TODO for 0.11.8-dev."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def edit(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor not found' % rel
    write(rel, s.replace(old, new, 1))


# --------------------------------------------------------------------------- CHANGELOG
edit('CHANGELOG.md', u'# Changelog\n\n', u"""# Changelog

## 0.11.8-dev - 2026-09-29 - the storyteller finally knows this mod exists

- **Your storyteller can now pace this mod's events.** Until now every one of them fired on the mod's own schedule, so Cassandra, Randy and Phoebe had never heard of it.
- **Threshold bleed** - the space occasionally comes out the near side. The lights in the room a gate stands in go out, or the room drops several degrees, or dirt appears that was not there. Only in the gate's room, and only if you have actually been through a gate.
- **Unsolicited delivery** - the parent corporation sends a crate nobody ordered. It is not kindness; it has money in you. Only once you are in contact with it.
- **Neither can hurt anybody, destroy anything or block a route**, and each has an answer you already know: flick the switch, wear a coat, sweep the floor.
- **There is no custom storyteller and there never will be.** You would have to give up the one you chose, and there is nothing in one worth taking.
- **The clean-up team is not one of these.** It is a promise, and a promise does not get rolled for.

Full record: [the storyteller finally knows this mod exists](docs/implementation/INCIDENT_SURFACE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

# --------------------------------------------------------------------------- FINALIZED
edit('docs/FINALIZED.md', u'\n## Inherited pre-workflow history', u"""
## Session 2026-09-29 - the storyteller surface (0.11.8-dev)

**Verbatim user quote:** *"lets get to it all making it all correct"*

**The question this closes, verbatim:** *"we may need our own story teller right? or is that way way to much work? with the “AI” like ai thats not an ai that the storytellers use"*

**The decision at that fork, verbatim:** *"Both - guaranteed floor, storyteller flavour"*

### What shipped

The flavour half. The mod's **first two `IncidentDef`s** with our own `IncidentWorker`s, so the player's chosen storyteller paces them: a threshold bleed scoped to the room a designated gate stands in, and an unsolicited corporation delivery gated on contact. **No `StorytellerDef`, now asserted as a never.**

### Files touched

`src/RimroomsAsyncIndustries/Incidents/RimroomsIncidents.cs` (new), `Company/CompanySupplyDrop.cs` (new), `Threats/AnomalyEventService.cs` (re-scoped to cells), `Company/FacilityRelief.cs`, `1.6/Defs/IncidentDefs/RR_Incidents.xml` (new), keyed strings, `tools/package-files.json`, `docs/implementation/INCIDENT_SURFACE_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and a sixth proof.

### Closure notes

- **The mod shipped zero `IncidentDef`s until this checkpoint.** Every event fired from its own component tick, so no storyteller had ever heard of it. That is the real answer to the owner's question, and it cost two defs and a base class rather than a persona.
- **There is no intelligence in a storyteller to borrow** - a `StorytellerComp` rolls a mean-time-between against wealth and population. The part that behaves like a director is `IncidentWorker.CanFireNowSub`, which is ours without owning the exclusive slot.
- **`AnomalyEventService` was re-scoped from `CoordinateRecord` to a plain cell list** so the bleed runs the *same* four effect bodies a coordinate runs. What would drift out of a second copy are the four safety promises in invariant 28.
- **An assertion was wrong and the source was right, for the second time this session.** The incursion claim matched the mod's own doc comment explaining why incursion is excluded. A proof that punishes the explanation teaches people to delete explanations; it now strips comments before asking.
- **The heredoc `\\n` gotcha, hit for the seventh time**, with the fix already written next to it in `NOW.md`.
- Build 0.11.8-dev, 166 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, six proofs hold, the new one fault-planted four ways. Assembly reproduced by two clean recompiles. **No game was launched.**

---
""")

# --------------------------------------------------------------------------- NOW
s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.11.7-dev**.', u'| Published | **0.11.8-dev**.'),
    (u'| Build | **163 C# files, 85 package files**, zero warnings, zero errors |',
     u'| Build | **166 C# files, 86 package files**, zero warnings, zero errors |'),
    (u'`307D02D075BBBF4256FB019BF848E6705400D4F40EF79DA5E26EE11802BB2CCC`',
     u'`3E7B151603CFA38B2066DD5F7DD57EB1DE1EE60317E3A2634D12F452FB05C528`'),
    (u'| Proofs | **five** in `.local/register/proof-*.py`, all holding.',
     u'| Proofs | **six** in `.local/register/proof-*.py`, all holding.'),
    (u'## What shipped this session, 0.7.1 → 0.11.7',
     u'## What shipped this session, 0.7.1 → 0.11.8'),
    (u'| 0.11.7 | **The corporation does not write off a branch** — the clean-up team; five `PawnKindDef`s found authored and read by nothing |',
     u'| 0.11.7 | **The corporation does not write off a branch** — the clean-up team; five `PawnKindDef`s found authored and read by nothing |\n'
     u'| 0.11.8 | **The storyteller finally knows this mod exists** — the first two `IncidentDef`s; no `StorytellerDef`, now asserted |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

# Queue: item 1 done, the Store and Solo/Group starts move up.
start = s.index(u"1. **The storyteller half")
end = s.index(u'2. **Research tiers 3–4**')
s = s[:start] + u"""1. **The Store and Solo/Group starts.** Each *"needs special treatment in theri layout and
   starts"*, a different point of view on the same world, and **neither begins in corporation
   contact** — so neither has the clean-up team, and neither gets the courier, until it earns
   contact. That absence is what makes those two openings frightening, and it is now a real
   difference rather than a note.
""" + s[end:]
s = s.replace(u'3. **The Store and Solo/Group starts.** Each *"needs special treatment in theri layout and\n   starts"*, a different point of view on the same world, and **neither begins in contact**.\n', u'', 1)

# Invariants 141-143.
marker = u'140. **A guarantee must not be an incident.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'141. **Never ship a `StorytellerDef`.** It is an exclusive slot the player would have to '
     u'give up Cassandra or Randy for, and it needs portrait art the no-new-art rule forbids. '
     u'**There is no intelligence in one to borrow** — a `StorytellerComp` rolls a '
     u'mean-time-between against wealth and population. The director is '
     u'`IncidentWorker.CanFireNowSub`, which is ours without the slot. Asserted by '
     u'`proof-incidents.py`.\n'
     u'142. **A proof must not punish an explanation.** The incursion claim failed on this mod’s '
     u'own comment saying why incursion is excluded. Strip comments and ask about code — a rule '
     u'that makes documenting a decision expensive teaches people to stop documenting decisions. '
     u'**Second time this session an assertion was wrong and the code was right** (see 130).\n'
     u'143. **A number displayed and a number dropped must come from one table.** The relief crate '
     u'and the courier crate are one corporation with one warehouse, read at two scales. Two '
     u'tables drift the first time either is tuned, and the letter keeps promising the old one.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# --------------------------------------------------------------------------- TODO
s = read('docs/TODO.md')
old = u'- [ ] **Lighter world-facing events register as `IncidentDef`s with our own `IncidentWorker`s**'
assert old in s
s = s.replace(old, u'- [x] **Lighter world-facing events register as `IncidentDef`s with our own `IncidentWorker`s** - SHIPPED in 0.11.8-dev, the mod\'s first two. Record: `docs/implementation/INCIDENT_SURFACE_IMPLEMENTATION.md`. **No `StorytellerDef`, now asserted as a never.**', 1)
write('docs/TODO.md', s)
