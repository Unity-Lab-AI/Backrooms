# -*- coding: utf-8 -*-
"""The rest of the deadline promises, in three documents the first sweep did not reach.

Two hits are deliberately LEFT ALONE because they argue for the rule rather than against it:

  CONNECTED_COLONY_PORTALS.md - "No ... expiration timer ... may close it. Do not invent a normal
    timed shutdown for it." That is the natural-gate rule and it is on the right side.
  MOD_INTEGRATION_PLAN.md:51 - "Avoid local wall-clock deadlines." A storage convention against
    using the player's real clock. Also on the right side.
"""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:90])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


patch('docs/CAMPAIGN_STATE_DICTIONARY.md', [
    # A storage convention, but it named a thing that no longer exists.
    ("Record durations/deadlines in RimWorld game ticks, not the player's local wall clock.",
     "Record durations in RimWorld game ticks, not the player's local wall clock. **The gate's "
     "connection window is the only duration measured against the player** - see [the campaign "
     "chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate)."),
])


patch('docs/FEATURE_TRACEABILITY.md', [
    ('| Objective, deadline, risk, local response and aftermath appear on Operations and map/world views. |',
     '| Objective, routes to success, risk, local response and aftermath appear on Operations and '
     'map/world views. **No deadline, because a mission has none.** |'),
])


patch('docs/MOD_INTEGRATION_PLAN.md', [
    ('| Countermeasure unknown, breach risk, contract deadline. |',
     '| Countermeasure unknown, breach risk, several routes to success. |'),

    ('Contract cards specify client, advance, deadline, requested deliverables, optional '
     'quality/safety terms, payment, penalty cap, ownership, and cancellation.',
     'Contract cards specify client, advance, requested deliverables, **two or more routes to '
     'success**, optional quality/safety terms, payment, penalty cap, ownership, and cancellation. '
     '**No deadline** - see [the campaign chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate).'),

    ('A town distortion creates timed objectives: locate/secure the entry,',
     'A town distortion creates objectives, none of them timed: locate/secure the entry,'),

    # A wage or rent bill coming due is a cost schedule, not a deadline on a task -- but calling
    # it a deadline on the overview panel reads as pressure the mod does not apply.
    ('| Overview | Gate alarm/state, low stocks, injured/missing staff, payment deadlines, power '
     'reserve, contract and incident priorities. |',
     '| Overview | Gate alarm/state, low stocks, injured/missing staff, payments due, power '
     'reserve, contract and incident priorities. |'),
])
