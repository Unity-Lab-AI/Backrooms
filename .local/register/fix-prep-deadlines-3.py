# -*- coding: utf-8 -*-
"""The last deadline promises, found by check-campaign-absolutes.py rather than by hand.

Five documents the manual sweep missed. Two of the hits are legitimate discussion of the rule
itself and are handled by widening the checker's negation list rather than by rewording, because
a document explaining why deadlines are banned must be allowed to say the word.
"""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:90])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


patch('AGENTS.md', [
    ('Contracts show quoted scope, payment, deadlines, delivery, risks, and penalties;',
     'Contracts show quoted scope, payment, two or more routes to success, delivery, risks, and '
     'penalties, and never a deadline;'),
])

patch('docs/CAMPAIGN_ECONOMY_MODEL.md', [
    # The second instance carried a "late/lost work" clause the first sweep did not reach.
    ('base payment, advance, milestone/partial payments, optional bonus, **two or more routes to success**, penalty cap, and cancellation terms. **No card carries a deadline**',
     'base payment, advance, milestone/partial payments, optional bonus, **two or more routes to success**, penalty cap, and cancellation terms. **No card carries a deadline, ever**'),
])

patch('docs/OPERATIONS_ACTION_CONTRACTS.md', [
    ('Shows deadline, missing deliverable, or eligibility reason; late/lost work',
     'Shows the missing deliverable or the eligibility reason - never a deadline, because there '
     'is none; lost work'),
])

patch('docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md', [
    ('- [ ] Implement equipment/material procurement, source/price/deadline, shipment manifest, receiving area, delay/loss/damage event',
     '- [ ] Implement equipment/material procurement, source/price/**expected arrival** (a supplier estimate, never a deadline), shipment manifest, receiving area, delay/loss/damage event'),
    ('conceals urgent health, fire, power, missing crew, gate recall, containment, or contract deadlines.',
     'conceals urgent health, fire, power, missing crew, gate recall, containment, or contract priorities.'),
])

patch('docs/SYSTEMS_CATALOG.md', [
    ('1. **Overview:** urgent alerts, active projects, gate state, cash, deadlines.',
     '1. **Overview:** urgent alerts, active projects, gate state, cash, payments due. **No deadlines** - see [the campaign chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate).'),
    ('| Missing civilians, authority pressure, deadline |',
     '| Missing civilians, authority pressure, several routes to success |'),
])

patch('docs/TODO.md', [
    ('- [ ] Implement equipment/material procurement, source/price/deadline, shipment manifest, receiving area, delay/loss/damage event',
     '- [ ] Implement equipment/material procurement, source/price/**expected arrival** (a supplier estimate, never a deadline), shipment manifest, receiving area, delay/loss/damage event'),
    ('conceals urgent health, fire, power, missing crew, gate recall, containment, or contract deadlines. — post-completion test phase',
     'conceals urgent health, fire, power, missing crew, gate recall, containment, or contract priorities. — post-completion test phase'),
])

# The checker must let a document explain the rule. Widening the negation list is the right fix
# for those two rather than rewording text whose whole job is to say deadlines are banned.
p = 'tools/check-campaign-absolutes.py'
text = io.open(p, encoding='utf-8').read()
old = "    r\"none of them timed|no investigation is timed|timed slideshow|timed menu slideshow)\", re.I)"
new = ("    r\"none of them timed|no investigation is timed|timed slideshow|timed menu slideshow|\"\n"
       "    r\"never a deadline|no deadlines|a deadline is the easiest|banned|superseded|\"\n"
       "    r\"carries a deadline, ever|because there is none)\", re.I)")
assert old in text
io.open(p, 'w', encoding='utf-8', newline='').write(text.replace(old, new, 1))
print('  widened the checker negation list so a document may explain the rule')
