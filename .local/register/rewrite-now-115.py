# -*- coding: utf-8 -*-
import io

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()

# --------------------------------------------------------------------------- state table
pairs = [
    ('| Published | **0.11.4-dev**.', '| Published | **0.11.5-dev**.'),
    ('| Build | **162 C# files, 85 package files**, zero warnings, zero errors |',
     '| Build | **162 C# files, 85 package files**, zero warnings, zero errors |'),
    ('| Assembly | SHA-256 `D586E665BB10FD6067A3A84241770E6BA8EF454DFC72E7D74FECA3D3E4A4787`, reproduced by two clean recompiles |',
     '| Assembly | SHA-256 `3309AD3036C91C5159C91A7998C4486ECBC04E5B5F187A67B44980028E12A682`, reproduced by two clean recompiles |'),
    ('| Checkers | **eight**, all passing |',
     '| Checkers | **eight**, all passing |\n'
     '| Proofs | **four** in `.local/register/proof-*.py`, all holding. They assert; they do not print. |\n'
     '| Chart | **`docs/CAMPAIGN_CHART.md` is the authority on campaign structure** and beats any prep document |'),
    ('## What shipped this session, 0.7.1 → 0.11.4', '## What shipped this session, 0.7.1 → 0.11.5'),
    ('| 0.11.4 | **The second rung of every branch** — research tier 1; two vestigial power props found and retired |',
     '| 0.11.4 | **The second rung of every branch** — research tier 1; two vestigial power props found and retired |\n'
     '| 0.11.5 | **A designated gate is a machine that is on** — three unused props restored, two wired. **Reversed 0.11.4’s retirements.** |'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

# --------------------------------------------------------------------------- the queue
start = s.index('## What is left, in order')
end = s.index('## Invariants — do not break these')
queue = u"""## What is left, in order

The order is the one `docs/CAMPAIGN_CHART.md` §7 authorises. **Read the chart before starting
anything in this list** — it is the authority, and steps 1–5 of its build order are done.

1. **Research tier 2** — *"Repeatable operations: revisit known coordinates and reduce preventable
   failures."* Seven projects, one per branch, each requiring its tier 1 sibling **and a distortion
   log**, because this band is about things having gone wrong. **Seven live knobs are already
   identified and none of them needs inventing:**
   - Facilities → `stablePowerTicksRequired` (how long power must be stable before opening)
   - Fieldcraft → `dialSpinUpDecayFraction` (progress lost when the operator steps away)
   - Measurement → `calibrationWorkRequired`
   - Spatial → `dialSpinUpFamiliarityFactor` (a known address dials faster)
   - Entities → incursion requires `PortalWindowTier >= 2` instead of `>= 1` — containment
     meaning something, at an existing read site in `PortalTraversalPolicy`
   - Logistics → `MaximumOpenOrders`
   - Commerce → catalogue `maxOrderQuantity`
2. **The clean-up team — *"so that facilities never die"*.** The state it keys on **already
   exists**: `campaign.CorporationContact`, one-way, set from `beginsInCorporationContact`. Async
   Industries begins true; the Store and Solo/Group begin false and must earn it. On collapse the
   corporation sends a team with all-access passes, clears every hostile, requisitions a fresh
   basic team and drops supplies. **A no-fail floor, chosen deliberately by the owner.**
3. **The Store and Solo/Group starts.** Each *"needs special treatment in theri layout and
   starts"*, a different point of view on the same world, and **neither begins in contact**.
4. **Research tiers 3–4** — remote and deep operations.
5. **Generated requests after the hinge**, from branch state, coordinate history and capability.
   Route selection for a generated request is an **open owner question** (chart §6).
6. **Arcs 5–8** — remote sites, the outside world, industrial reach, deeper systems.
7. **Still unbuilt from the prep material** — *"contradictory accounts"* from a returning crew;
   staff **prior exposure**; *"respond to openings in settlements"*.
8. **The adjacent-door-run fallback** — 1×3 and 2×3 by binding one gate across a run of adjacent
   1×1 Core doors, for players without Doors Expanded.
9. **`RR_QuietPursuer` presentation** and the five `RR_*Staff` PawnKinds — the last existing-content
   replacements.
10. **The player-facing how-to.** Written **once**, for both the repo and the site.
11. **Public release** — site, Workshop page, collection. [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md).
    **Correctly last.**
12. **Continue the register retro sweep.** Swept: animals, security, spatial construction,
    expedition logistics, interface, facilities, furniture, storage, power, contracts, faction
    standing, subject casework, evidence, policies. Not yet: medical, world operations, cargo,
    hospitality, materials, visitor economy, staff psychology.
13. Reconcile 0.5.0–0.7.1 into the master backlog; fix the register's `disposition_stance()`
    negation bug; the unknown-def-field checker, **written, proved broken and removed rather than
    shipped**.

### Done since the last handoff, so nobody rebuilds it

Glow-pod markers with colour-as-meaning · evidence custody on a linked archive shelf · the survey
tag, evidence case and their recipes retired · gate equipment links · the log-gated window ladder
with four rungs · the campaign chart · the request shape with success routes · the full tutorial
line and the hinge · research tiers 0 and 1 across seven branches · the alerts readout.

---

"""
s = s[:start] + queue + s[end:]

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md state and queue rewritten')
