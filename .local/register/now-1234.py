# -*- coding: utf-8 -*-
"""NOW.md for 0.12.34-dev.

Every number re-measured rather than carried:

    C# files            182   (git ls-files src --others --cached --exclude-standard | grep -c '\\.cs$')
    package files        87
    assembly            read from the live build after the determinism run
    queue                74 open / 50 partial / 458 done, one consistent pattern
    proofs               31
    version sites        all three agree on 0.12.34-dev

The DO THIS FIRST section is replaced rather than edited: the eleven container givers are built,
and the next task is a different question. The remaining-work list loses its first item and gains
the two closures as records, because the standing rule is that nobody rebuilds what shipped.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

s = io.open(PATH, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, "anchor missing: %r" % old[:90]
    assert s.count(old) == 1, "anchor not unique: %r" % old[:90]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ state table
sub(u"| Published | **0.12.33-dev**. This handoff is the tip; `git log --oneline -1` is "
    u"authoritative and the eight refs below match it. |",
    u"| Published | **0.12.34-dev**. `git log --oneline -1` is authoritative and the eight refs "
    u"below match it. |")

sub(u"| Build | **180 C# files, 87 package files**, zero warnings, zero errors.",
    u"| Build | **182 C# files, 87 package files**, zero warnings, zero errors.")

sub(u"| Assembly | SHA-256 `B7EA5785E49DD0B8F123A560C3752AC86F7D213FA74476A0FF720E9E389908C6`, "
    u"reproduced by two clean recompiles.",
    u"| Assembly | SHA-256 `C5493C37AF131E005FBC77E64A514C7B97D950F4BB1BC0187433F8117B2576AD`, "
    u"reproduced by two clean recompiles.")

sub(u"| Proofs | **THIRTY** in `.local/register/proof-*.py`.",
    u"| Proofs | **THIRTY-ONE** in `.local/register/proof-*.py`.")

# ------------------------------------------------------------------ the queue figures
sub(u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 75 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 50 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 457 done
```""",
    u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 74 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 50 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 458 done
```""")

sub(u"**~21 genuine build items**, measured at 0.12.33-dev, listed in full under **What is left** "
    u"below.",
    u"**~19 genuine build items**, measured at 0.12.34-dev, listed in full under **What is left** "
    u"below.")

# ------------------------------------------------------------------ the staging note
sub(u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.33-dev**.",
    u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is **0.12.34-dev**.")

# ------------------------------------------------------------------ replace DO THIS FIRST
start = s.index(u"## DO THIS FIRST — the eleven DLC container hauling givers")
end = s.index(u"## What shipped this session, 0.7.1 →")
sub(s[start:end], u"""## DO THIS FIRST — containment, quarantine and the alarm

Row 761, and it is the largest unbuilt system left rather than the easiest. Its own words:

> *"Containment rooms, security procedures, staff debrief, quarantine, alarm and escape
> response."*

**Two of the six are already shipped and must not be rebuilt.** Evidence custody and case records
have shipped since 0.7.x, and **witness interviews shipped 0.12.28-dev** — `EvidenceInterview.cs`,
with nine refusals and an interviewer chosen on Social. Check each of the six against the code
before writing a line of it: **four separate rows in this session turned out to be already built**,
and a fifth (1266) turned out to be answered by Core rather than needing anything.

Four things to settle first:

1. **What a containment room *is* in this mod has a precedent, and it is not a new building.**
   0.10.8-dev established that *"a gate's facility is the equipment linked into it"* — shelves,
   analysers and cabinets link like furniture to a bed, through walls and by hand — and
   0.9.7-dev established that a facility is a **contiguous run** of cells. A containment room is
   almost certainly a room role read off equipment already linked, not a `ThingDef`. **No new
   gameplay ThingDefs** is a standing constraint, so if the design needs one, ask.
2. **An alarm has exactly one honest surface and 0.10.5-dev already measured it.** The seventh
   checker calibrated every display surface against Core per surface, and found this mod used
   **none** of the alerts readout. An escape or a breach is what `Alert` exists for. Anything
   drawn instead of an `Alert` is a second opinion beside the one the player already watches.
3. **Quarantine is an area question, and three area rows are still open** — 1215, 1235 and 1239
   cover `Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` across
   a gate. Quarantine may be the fifth of those rather than its own machinery, and if it is, build
   it with them.
4. **`python tools/register-query.py use RR-EVD` and `family security`** before designing. The
   security family is swept; **subject casework and evidence are swept too**, so this one has
   register guidance already read rather than owing a sweep.

**The escape half has a hard constraint from 0.9.6-dev.** *"It came through with them"* is a
**bounded, named exception** to the founding rule that nothing crosses but people. An escaping
contained subject is the same class of event and must be the same kind of exception — named,
bounded and refusable — rather than a new general capability. Read `CompRimroomsEmergence` and the
0.9.6-dev record first.

---

""")

# ------------------------------------------------------------------ session table row
sub(u"## What shipped this session, 0.7.1 → 0.12.33",
    u"## What shipped this session, 0.7.1 → 0.12.34")

# ------------------------------------------------------------------ the remaining-work list
sub(u"""## What is left, in order — rewritten 0.12.33-dev, measured not carried

**~21 genuine build items**, and the previous version of this list had two that shipped this session
still written as open. Anything marked closed below stays as a record so nobody rebuilds it.

### Systems still unbuilt

1. **The eleven DLC container hauling givers.** Named, not guessed at, in
   `HaulingUpkeepProvider`'s own note. **This is the DO THIS FIRST item** — see the top of this
   file for the four things to settle, of which custody is the real one.
2. **Containment rooms, security procedures, staff debrief, quarantine, alarm and escape
   response.** Row 761. Evidence custody and case records already ship; **witness interviews
   shipped 0.12.28-dev.** This is the rest of that row.
3. **Crew composition and cargo planner**""",
    u"""## What is left, in order — rewritten 0.12.34-dev, measured not carried

**~19 genuine build items.** Anything marked closed below stays as a record so nobody rebuilds it.

### Systems still unbuilt

1. **Containment rooms, security procedures, staff debrief, quarantine, alarm and escape
   response.** Row 761. Evidence custody and case records already ship; **witness interviews
   shipped 0.12.28-dev.** This is the rest of that row, and **it is the DO THIS FIRST item** —
   see the top of this file for the four things to settle.
   **Row 1266 is closed** (0.12.34-dev): the eleven DLC container hauling givers are built as
   `machine-loading`, and the custody review they were waiting on found that **Core forbids every
   one of them from moving anything between maps**, so invariant 55 was never engaged. **The four
   painting givers in `Art` are closed with them** — `Art` had a bill family and no designation
   family, so nobody would ever have crossed to paint anything.
2. **Crew composition and cargo planner**""")

sub(u"""4. **Quests and missions for odd goods**""", u"""3. **Quests and missions for odd goods**""")
sub(u"""5. **Mining and building behind a gate.**""", u"""4. **Mining and building behind a gate.**""")
sub(u"""6. **Mineable materials and recoverable floors**""",
    u"""5. **Mineable materials and recoverable floors**""")
sub(u"""7. **The four area types across a gate**""", u"""6. **The four area types across a gate**""")
sub(u"""8. **Inhabitant and monstrosity families tiered by depth and wealth**,""",
    u"""7. **Inhabitant and monstrosity families tiered by depth and wealth**,""")
sub(u"""9. **Material variety per coordinate**""", u"""8. **Material variety per coordinate**""")
sub(u"""10. **Gate subsystems**:""", u"""9. **Gate subsystems**:""")
sub(u"""11. **Vehicles, space travel and the two VGE chapter hooks.**""",
    u"""10. **Vehicles, space travel and the two VGE chapter hooks.**""")
sub(u"""12. **RWT multiplayer feature detection and its documentation.**""",
    u"""11. **RWT multiplayer feature detection and its documentation.**""")
sub(u"""13. **The player-facing how-to for gameplay and systems.**""",
    u"""12. **The player-facing how-to for gameplay and systems.**""")
sub(u"""14. **The native menu remap**""", u"""13. **The native menu remap**""")
sub(u"""15. **Tutorial, glossary, keyboard paths, contrast and scale.**""",
    u"""14. **Tutorial, glossary, keyboard paths, contrast and scale.**""")
sub(u"""16. **The unknown-def-field checker**""", u"""15. **The unknown-def-field checker**""")
sub(u"""17. **Fix `disposition_stance()`**""", u"""16. **Fix `disposition_stance()`**""")
sub(u"""18. **Reconcile 0.5.0–0.7.1 into the master backlog.**""",
    u"""17. **Reconcile 0.5.0–0.7.1 into the master backlog.**""")
sub(u"""19. **The register retro sweep's last families.**""",
    u"""18. **The register retro sweep's last families.**""")
sub(u"""20. **The campaign economy workbook has no generator**""",
    u"""19. **The campaign economy workbook has no generator**""")
sub(u"""21. **The TOS and official-versions compliance pass**""",
    u"""20. **The TOS and official-versions compliance pass**""")

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("NOW.md updated for 0.12.34-dev")
