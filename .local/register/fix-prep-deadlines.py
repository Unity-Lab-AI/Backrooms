# -*- coding: utf-8 -*-
"""Remove the deadline promises from the prep documents.

Owner-confirmed at the fork: correct them to match docs/CAMPAIGN_CHART.md. These are living
documents describing the wanted state, and they had promised deadlines, timed investigations and
penalties for delay since Gate 0. No content was ever built from those lines, which is the only
reason nothing is broken.

"Consequence for abandonment" survives everywhere it appears. Abandoning a task is an ACT.
"Consequence for delay" does not: being slow is not an act.
"""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:90])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


patch('docs/CAMPAIGN_CONTENT_CATALOG.md', [
    # arc 4
    ('Every quote and contract states its payment, deadline, deliverable, and consequence before acceptance.',
     'Every quote and contract states its payment, deliverable, **two or more routes to success**, '
     'and consequence before acceptance. **It never states a deadline, because it never has one** '
     '- see [the campaign chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate).'),

    # arc 6 -- the worst offender
    ('Timed distortion investigations, perimeter control, witness and crew cases, rescue operations, '
     'containment decisions, follow-up contracts, and consequences for delay or abandonment.',
     'Distortion investigations, perimeter control, witness and crew cases, rescue operations, '
     'containment decisions, follow-up contracts, and consequences for **abandonment**. '
     '**No investigation is timed and there is no consequence for delay** - abandoning a site is '
     'an act a player chooses, while being slow is not.'),

    # the mission brief
    ('A brief names what counts as success, what may be lost, any deadline, payment, bonus, penalty, '
     'and cancellation rule.',
     'A brief names what counts as success, **the several routes to it**, what may be lost, '
     'payment, bonus and the cancellation rule. **There is no deadline field**, and only the player '
     'may cancel.'),

    # the town distortion mission family
    ('| **Town or settlement distortion** | A timed opening creates a perimeter and public-safety problem:',
     '| **Town or settlement distortion** | An opening creates a perimeter and public-safety problem:'),
])


patch('docs/CAMPAIGN_ECONOMY_MODEL.md', [
    ('Each contract card names requested evidence or cargo, who owns it, base payment, advance, '
     'milestone/partial payments, optional bonus, deadline, penalty cap, and cancellation terms.',
     'Each contract card names requested evidence or cargo, who owns it, base payment, advance, '
     'milestone/partial payments, optional bonus, **two or more routes to success**, penalty cap, '
     'and cancellation terms. **No card carries a deadline** - see [the campaign chart]'
     '(CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate).'),

    ('| Several teams, an extended deadline, high-value cargo, or a secured temporary facility. |',
     '| Several teams, high-value cargo, or a secured temporary facility. |'),

    ('The actual quote is generated from scope, risk, staff time, required equipment and transport, '
     'deadline, buyer demand, deliverable quality, and ownership terms.',
     'The actual quote is generated from scope, risk, staff time, required equipment and transport, '
     'buyer demand, deliverable quality, and ownership terms.'),

    ('- The contract card and order show client/supplier, requested work or goods, amount in USD, '
     'advance, deadline, bonus, capped penalty, cancellation rule, shipment quantity, receiving '
     'site, expected arrival, and item ownership.',
     '- The contract card and order show client/supplier, requested work or goods, amount in USD, '
     'advance, bonus, capped penalty, cancellation rule, shipment quantity, receiving site, '
     'expected arrival, and item ownership. **No deadline.** An expected arrival is the supplier\'s '
     'estimate of when goods turn up, not a clock the player is measured against.'),
])


patch('docs/CAMPAIGN_ECONOMY_PROGRESSION.md', [
    ('It names the buyer, scope, evidence or cargo, ownership, staff time, equipment, risk, deadline, '
     'amount, advance, optional milestone/bonus, partial outcome, penalty cap, cancellation, and '
     'logistics.',
     'It names the buyer, scope, evidence or cargo, ownership, staff time, equipment, risk, amount, '
     'advance, optional milestone/bonus, partial outcome, penalty cap, cancellation, logistics, and '
     '**two or more routes to success**. **It names no deadline** - see [the campaign chart]'
     '(CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate).'),
])


patch('docs/CAMPAIGN_ROSTER_FREEZE.md', [
    ('Deadlines and local trust matter.',
     'Local trust matters. **Deadlines do not exist** - see [the campaign chart]'
     '(CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate).'),

    ('| Saved contract, objective, quote, crew, gear, destination, deadline, and return plan. |',
     '| Saved contract, objective, quote, crew, gear, destination, routes to success, and return plan. |'),

    ('a contract/order shows scope, USD amount, deadline, advance, bonus, penalty cap, ownership, '
     'shipment quantity, receiving site, arrival window and consequence of failure.',
     'a contract/order shows scope, USD amount, advance, bonus, penalty cap, ownership, shipment '
     'quantity, receiving site, arrival window, the several routes to success, and consequence of '
     'failure. **There is no deadline**; an arrival window is when goods are expected, not a limit '
     'on the player.'),
])
