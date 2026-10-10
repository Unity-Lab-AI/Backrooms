# -*- coding: utf-8 -*-
"""NOW.md protocol for 0.12.33-dev: every state claim re-measured, and the queue rewritten.

Measured rather than carried, all of it:

    tip                 7289dbb, tree clean
    C# files            180   (git ls-files src --others --cached --exclude-standard | grep -c '\\.cs$')
    package files        87
    checkers             11   (10 tools/check-*.py + research/audit-gate0.py, the project's own count)
    proofs               30
    assembly            B7EA5785...908C6, read from the live build
    queue                75 open / 50 partial / 457 done, one consistent pattern
    version sites        all three agree on 0.12.33-dev

**The "What is left, in order" section was the stale part**, and badly: items 4 and 5 shipped this
session (contradictory accounts 0.12.25-dev, the door-run fallback 0.12.31-dev) and were still
written as open. A post-compaction session reads that list to decide what to do, so a stale list is
the most expensive thing in the file.

It is replaced with the measured remainder, grouped, with the runtime-gated items separated out --
because *"all build work complete"* has a hard edge and a fresh session needs to know where it is.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:90]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:90]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ the queue count line
sub(u'**The count itself was measured two ways and reported as 90.** Under one consistent pattern '
    u'it is **86 open, 50 partial, 446 done** at 0.12.24-dev.',
    u'**The count itself was measured two ways and reported as 90.** Under one consistent pattern '
    u'it was **86 / 50 / 446** at 0.12.24-dev and is **75 open, 50 partial, 457 done** at '
    u'0.12.33-dev.')

# ------------------------------------------------------------------ replace the stale queue
start = s.index(u'## What is left, in order')
end = s.index(u'### Done since the last handoff, so nobody rebuilds it')
sub(s[start:end], u"""## What is left, in order — rewritten 0.12.33-dev, measured not carried

**~21 genuine build items**, and the previous version of this list had two that shipped this session
still written as open. Anything marked closed below stays as a record so nobody rebuilds it.

### Systems still unbuilt

1. **The eleven DLC container hauling givers.** Named, not guessed at, in
   `HaulingUpkeepProvider`'s own note. **This is the DO THIS FIRST item** — see the top of this
   file for the four things to settle, of which custody is the real one.
2. **Containment rooms, security procedures, staff debrief, quarantine, alarm and escape
   response.** Row 761. Evidence custody and case records already ship; **witness interviews
   shipped 0.12.28-dev.** This is the rest of that row.
3. **Crew composition and cargo planner** with skill, health, weight and window checks, ready and
   unready reasons, and a cost preview. Row 728. *"must not own connection existence"*.
4. **Quests and missions for odd goods**, as distinct from contracts — contracts shipped 0.7.3-dev
   and the owner asked for *"quests and missions and contracts"*. Plus a player-facing surface for
   open odd demands: offers and settlements are recorded events and the Operations pane does not
   list them. Rows 1031, 1032, 1033.
5. **Mining and building behind a gate.** Rows 98 and 99. The cells around a gate are ordinary map;
   the one exception is linked equipment, which has placement requirements **of its own**.
   **Row 113 is closed** (0.12.27-dev) — the approach cell is reserved against blocking, and
   flooring is fine.
6. **Mineable materials and recoverable floors** in a stripped interior. Row 1101. `FillWithRock`
   and `NaturalRockTypesIn` already ship; the floors half is what remains.
7. **The four area types across a gate** — `Area_BuildRoof`, `Area_NoRoof`,
   `Area_SnowOrSandClear`, `Area_PollutionClear`. Rows 1215, 1235, 1239. **Measured: one incidental
   `Area_NoRoof` use and no cross-gate coverage.**
8. **Inhabitant and monstrosity families tiered by depth and wealth**, every variation seeded.
   Row 1011. The bands, archetypes and pressure ladder they sit on all ship.
9. **Material variety per coordinate** — archetype fixtures take their default stuff today.
   Row 1005.
10. **Gate subsystems**: monitoring, cool-down, modules, repair and reliability. Row 725. Power
    reserves, calibration and the cutoff already ship.
11. **Vehicles, space travel and the two VGE chapter hooks.** Rows 764, 765, 766. **Optional by
    construction** — a `PatchOperationFindMod` that does nothing when the mod is absent.
12. **RWT multiplayer feature detection and its documentation.** Rows 784, 791. Requires the mod
    present to detect anything, and **no statement may describe live shared-colony control** unless
    implemented and demonstrated.

### Surfaces and words

13. **The player-facing how-to for gameplay and systems.** Rows 1193, 1220. `docs/HOWTO.md`
    documents the **build**, not play. Written **once**, for both the repo and the site.
14. **The native menu remap** into the company-first layout. Row 821. Twelve panes and reason codes
    ship; this is the Architect/Work/Assign/Research integration.
15. **Tutorial, glossary, keyboard paths, contrast and scale.** Rows 822, 833. Localization
    completeness is already measurable: `check-keyed-strings.py` reports every declared key
    resolving.

### Housekeeping with teeth

16. **The unknown-def-field checker**, written once and **removed rather than shipped** because it
    passed its own planted fault. Row 922.
17. **Fix `disposition_stance()`** in the register generator: it counts a **negated** "required" as
    Required, and **14 of the 17** "Required" rows say the opposite. Row 1055.
18. **Reconcile 0.5.0–0.7.1 into the master backlog.** Row 1054 — the master TODO is granular for
    research and coarse for code.
19. **The register retro sweep's last families.** Swept: animals, security, spatial construction,
    expedition logistics, interface, facilities, furniture, storage, power, contracts, faction
    standing, subject casework, evidence, policies. **Not yet: medical, world operations, cargo,
    hospitality, materials, visitor economy, staff psychology.** Rows 206, 302.
20. **The campaign economy workbook has no generator**, and the register preview PNGs under
    `outputs/` depict a superseded layout. Rows 1268, 1269.
21. **The TOS and official-versions compliance pass** — hold the package against Ludeon's modding
    terms and the Steam agreements, and keep the position current. Rows 1286–1290.

### Cannot close before the game runs once — about 8 rows

Not evasion; it is what they are, in their own words:

- **exchange-rate and catalogue balance** — *"neither has any play behind it"* (rows 890, 891)
- **duplicate def and patch collisions in the exact 294 profile** — a conflict has to be
  reproducible to fix (row 810)
- **performance measurement and profiling** under a long save (rows 212, 742)
- **the user-facing compatibility report** — *"cannot honestly state a tested order before anything
  has been tested"* (row 812)
- **whether the creepy-versus-normal balance lands** — *"a play question"* (row 975)
- **the invalid-state matrix half** of row 835, and the release tag of row 849

### Excluded by the owner — 9 rows

*"lets not count the test items and the steam collection and mod workshop setup and stuff like
that"*. Rows 268–271, 275–278, 572: the site, the Workshop page, the collection, and the Playwright
idea. [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md) holds them, and **it is correctly last.**

---

""")

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md: queue count corrected, remaining-work list rewritten from measurement')
