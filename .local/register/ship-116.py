# -*- coding: utf-8 -*-
"""Ledger, changelog and README updates for 0.11.6-dev."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def edit(rel, old, new, count=1):
    p = os.path.join(REPO, rel)
    s = io.open(p, encoding='utf-8-sig' if rel.endswith('.xml') else 'utf-8').read()
    assert old in s, '%s: anchor not found' % rel
    s = s.replace(old, new, count)
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


# --------------------------------------------------------------------------- README
edit('README.md',
     u'**Current development version: 0.11.5-dev.**',
     u'**Current development version: 0.11.6-dev.**')

# --------------------------------------------------------------------------- CHANGELOG
entry = u"""# Changelog

## 0.11.6-dev - 2026-09-29 - the second time you do a thing should be cheaper

- **Seven more research projects**, the third step in each branch. Each needs its own second project and a completed distortion log, because this band is about having been through often enough for something to have gone wrong.
- **Standby Discipline** - a designated gate costs half as much to keep while it is closed.
- **Relief Watch** - a gate ramp left unattended loses a quarter as much progress. It still lapses if nobody comes back.
- **Reference Standards** - calibrating a gate assembly takes two fifths less work.
- **Known Address** - every previous connection to an address makes the next one to it markedly faster. A first visit is exactly as slow as it ever was.
- **Containment Protocol** - nothing follows a crew out through a connection until the aperture is opened wider than Field Stability allows.
- **Forward Dispatch** - a shipment leaves in half the time, which is what finally lets your own relays move an arrival.
- **Specialist Recruitment** - you may ask for applicants again in half the time.
- **None of these replaces an earlier project.** Every one moves a setting no other project touches, so two cards never have to explain each other.
- **Three planned unlocks were dropped before they were built**, because checking them showed they would have changed a number nobody could ever notice - a one-second wait, a cap of a hundred orders, and a quantity limit already set to a million.

Full record: [the second time you do a thing should be cheaper](docs/implementation/RESEARCH_TIER2_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
edit('CHANGELOG.md', u'# Changelog\n\n', entry)
