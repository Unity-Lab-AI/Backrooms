# -*- coding: utf-8 -*-
"""Ledger for 0.12.18-dev: research tier 3, all seven branches."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def insert_before(rel, anchor, block):
    s = read(rel)
    assert anchor in s, '%s: anchor not found' % rel
    write(rel, s.replace(anchor, block + anchor, 1))


insert_before('CHANGELOG.md', u'## 0.12.17-dev', u"""## 0.12.18-dev - 2026-09-29 - the third rung of every branch

- **Seven new research projects, one for each branch**, and every one of them changes a number you can watch change. Hold twelve remote sites instead of eight. Pay a sixth of your overhead per site instead of a quarter. Have a shipment left at a site with nobody there. Find a way onward sooner. Find the way *out* more often. Finish a survey faster. Build a room that holds the place back better.
- **This tier was deleted rather than written four versions ago**, because there was genuinely nothing for four of the branches to move. Building remote sites gave them all something real.
- **Two things deliberately did not change.** A coordinate still never yields more than two ways onward - that limit is what keeps the whole chain of spaces finite. And a sheltered room never stops the place wearing on you entirely; nothing will make the Backrooms somewhere to live.
- **Every unlock is checked against the code that honours it**, so no card can promise something that does nothing.

Full record: [the third rung of every branch](docs/implementation/RESEARCH_TIER_3_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the third rung of every branch (0.12.18-dev)

**Verbatim user quotes:** *"come on lets start gettin these last 100 or so finished up"* and *"make sure you are use the prep docs and mod register as a guide in all you build"*

### What shipped

**Research tier 3: seven projects, one per branch**, each moving a real observable knob, with two design restraints asserted.

### Files touched

`1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml`, `Company/RemoteSites.cs`, `UI/OperationsRemoteSites.cs`, `Portals/NaturalFrontierService.cs`, `Threats/BackroomsPressure.cs`, `docs/implementation/RESEARCH_TIER_3_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and two proofs.

### Closure notes

- **The register check was skipped on the first pass and the owner caught it.** *"make sure you are use the prep docs and mod register as a guide in all you build"* - correct, and the LAW says check **before** designing. Done properly: **row 191 ResearchTree (Settled)** and **row 279 Research Whatever** both operate on `ResearchProjectDef`; our company projects are `RimroomsProjectDef`, a separate type, so neither can see them. **Row 76 Do Your F****** Research** gates research by skill, which these already do through `minimumIntellectual` 6. **Rows 123 Mad Skills and 129 Misc. Training** make that threshold easier to reach, so the requirement is not a wall for players running them. Same reasoning that kept this mod clear of the native quest system.
- **THE 0.12.5-dev DELETION WAS RIGHT, AND THE RE-SURVEY IS WHAT MADE THIS WRITEABLE.** Four of seven branches had nothing to move then, because the systems an unlock would modify did not exist. Arc 5 wrote them. The knob sweep was run again and found a real read site for **all seven** - up from three - and the two that looked empty an hour ago turned out to have the best knobs: **Fieldcraft owns `EmergenceShare`**, because how often a survey finds a way *out to the world* is about coming back, not about reading a space; and **Entities owns `BestShelterRate`**, because knowing what is in a space changes how a room is built against it.
- **TWO RESTRAINTS KEPT, AND BOTH ARE ASSERTED.** `MaximumFrontiersPerCoordinate` is **not** touched: its own summary says raising it is *a design decision, not a tuning knob*, because the cap is what keeps a chain of spaces finite. Spatial makes the two arrive **sooner**, never three. And `DisciplinedShelterRate` is 0.12, **never zero** - a coordinate is always wearing and no player may build a room that makes the place ordinary. Both restraints were fault-planted and both fail when broken.
- **My own first version of the cap restraint was keyed off proximity and was wrong.** It searched for the capability name within 400 characters of the cap assignment, and broke the instant the capability-aware **rarity** line was written directly above it. **Proximity is not the thing that happens** - the same mistake this project has now caught five times. Rewritten to key off the assignment itself, and it also refuses any second per-coordinate cap constant to switch to.
- **The site cap now has exactly one source.** Both the service refusal and the Sites pane readout go through `RemoteSiteCap`, so the number a player is **shown** and the number that **refuses** them cannot disagree - the same discipline as the gate's idle draw. `proof-remote-sites.py` asserts the pane no longer reads the raw constant.
- **`proof-remote-sites.py` failed on the divisor change and was retargeted**, which is the proof working: the literal moved into `OverheadDivisorInForce` while the property - a ratio of the branch's own overhead, never an absolute - is unchanged. Two claims were **added**, including that a tier-3 unlock may not swap in a flat discount.
- **The vocabulary checker caught *"doorway"* twice in my own descriptions.** This mod says **door**; the far-side arrival point is a **threshold**. My text was corrected, not the rule.
- **The heredoc backslash trap was hit for the TENTH time**, mangling a regex into a syntax error. The gotcha line exists for exactly this and I ignored it again. Count corrected rather than rounded down.
- **Four planted faults, four catches, clean on restore.**
- Build 0.12.18-dev, 173 C# files, 91 package files, **0 warnings, 0 errors**. **32 project defs**, tiers 0-3 complete across seven branches. Eight checkers pass, **nineteen** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.17-dev**.', u'| Published | **0.12.18-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.17',
     u'## What shipped this session, 0.7.1 → 0.12.18'),
    (u'| 0.12.17 | **Four more menu slides** — six now cycle. A slide that would never have appeared is caught before it ships; provenance ships for the Steam disclosure |',
     u'| 0.12.17 | **Four more menu slides** — six now cycle. A slide that would never have appeared is caught before it ships; provenance ships for the Steam disclosure |\n'
     u'| 0.12.18 | **The third rung of every branch** — research tier 3, **all seven**, every one moving an observable knob. Two design restraints asserted |'),
]
for old, new in pairs:
    assert old in s, 'anchor missing: %r' % old[:60]
    s = s.replace(old, new, 1)

old = (u'- **Bash heredocs mangle `\\n` and break on apostrophes.** Hit **NINE times**')
new = (u'- **Bash heredocs mangle `\\n` and break on apostrophes.** Hit **TEN times**')
assert old in s, 'heredoc gotcha line not found'
s = s.replace(old, new, 1)

marker = u'199. **Provenance for generated art is a release obligation, not a nicety.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'200. **A tier deleted for having no knobs is worth re-surveying once the systems land.** '
     u'Tier 3 had nothing to move for four of seven branches at 0.12.5-dev and a real read site for '
     u'**all seven** at 0.12.18-dev, because arc 5 wrote the systems in between. **Re-run the '
     u'sweep; do not carry the old verdict.**\n'
     u'201. **A restraint is only a restraint if breaking it fails.** The per-coordinate frontier '
     u'cap must never become a research knob, and shelter must never reach zero. Both are asserted '
     u'and both were fault-planted — otherwise they are comments.\n'
     u'202. **Proximity is not the thing that happens.** A claim that looked for a capability name '
     u'within 400 characters of a constant broke the moment a legitimate line was written above it. '
     u'**Key off the assignment, the guard, the exit status — never off what sits nearby.** Fifth '
     u'time.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# Close the research tier-3 queue item.
t = read('docs/TODO.md')
old_row = u'- [~] Complete research branches for facility/power, engineering, field safety, equipment'
assert old_row in t, 'research branches row not found'
start = t.index(old_row)
end = t.index(u'\n', start)
body = t[start:end].split(u'] ', 1)[1].split(u' — **')[0]
t = (t[:start] + u'- [~] ' + body + u' — **TIERS 0–3 COMPLETE across seven branches, 0.12.18-dev.** '
     u'Tier 3 was deleted rather than written at 0.12.5-dev because four of seven branches had '
     u'nothing observable to move; arc 5 wrote those systems and the re-run sweep found a real read '
     u'site for **all seven**. Two restraints kept and asserted: the per-coordinate frontier cap is '
     u'**not** a research knob, and shelter never reaches zero. **Tier 4 remains**, and should be '
     u'surveyed the same way rather than assumed to have knobs.' + t[end:])
write('docs/TODO.md', t)
