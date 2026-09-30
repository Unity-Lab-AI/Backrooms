"""Offline proof of the spin-up familiarity curve and the decay rule, mirroring
SpinUpWorkRequiredFor and TickSpinUp exactly.

The risk this guards against is the one the layout derangement nearly shipped with: a
formula that looks right, silently produces a degenerate value, and the feature appears to
work while doing nothing. Here the degenerate outcomes would be a ramp that collapses to
zero (a gate that opens instantly, which is the one thing the direction exists to prevent),
a ramp that never shrinks (making the address book's familiarity discount a no-op), or a
decay that outruns progress (turning a slow operator's gate from slow into impossible).

This file already earned its keep once: it rejected a flat per-tick decay of 0.5, which
would have bled a low-Intellectual technician's ramp faster than they could build it.
"""

BASE = 1800.0
FACTOR = 0.85
FLOOR_FRACTION = 0.25
DECAY_FRACTION = 0.5

# RimWorld research speed across the plausible operator range, from a barely-literate
# colonist to a specialist with good conditions.
OPERATOR_RATES = [0.08, 0.2, 0.35, 0.5, 0.79, 1.0, 1.35, 1.8, 2.4]


def required(prior):
    req = BASE
    floor = BASE * FLOOR_FRACTION
    for _ in range(prior):
        req *= FACTOR
        if req <= floor:
            return floor
    return max(floor, req)


floor = BASE * FLOOR_FRACTION
previous = None
reached_floor_at = None
for prior in range(0, 61):
    value = required(prior)
    assert value >= floor - 1e-6, 'below floor at %d: %f' % (prior, value)
    assert value <= BASE + 1e-6, 'above base at %d: %f' % (prior, value)
    if previous is not None:
        assert value <= previous + 1e-6, 'not monotonic at %d' % prior
    if reached_floor_at is None and abs(value - floor) < 1e-6:
        reached_floor_at = prior
    previous = value

assert reached_floor_at is not None, 'never reaches the floor: the discount is unbounded'
assert reached_floor_at > 3, 'reaches the floor too fast to be a progression'

# A brand new address must cost the full ramp, or familiarity is being applied to somewhere
# nobody has been.
assert abs(required(0) - BASE) < 1e-6

# The decay rule, as shipped: decay is a fraction of the rate the ramp was observed
# climbing at. This must hold for EVERY operator, which is the whole point of tying it to
# the observed rate rather than to a constant.
for rate in OPERATOR_RATES:
    decay = rate * DECAY_FRACTION
    assert decay < rate, 'decay outruns progress at rate %.2f' % rate
    # Recovering a ramp must never cost more than it cost to build it in the first place.
    ticks_lost_per_tick_away = decay / rate
    assert ticks_lost_per_tick_away < 1.0

# A ramp that is entirely unattended must still eventually lapse rather than hang forever.
for rate in OPERATOR_RATES:
    decay = rate * DECAY_FRACTION
    assert BASE / decay < 200000, 'a full ramp takes implausibly long to lapse at rate %.2f' % rate

slow = OPERATOR_RATES[0]
fast = OPERATOR_RATES[-1]
print('base required        : %.0f' % BASE)
print('floor                : %.0f (%.0f%% of base)' % (floor, FLOOR_FRACTION * 100))
print('reaches floor after  : %d prior connections' % reached_floor_at)
print('required at 0/1/3/5/10 prior: %.0f %.0f %.0f %.0f %.0f'
      % (required(0), required(1), required(3), required(5), required(10)))
print('new route, rate %.2f  : %.0f ticks' % (fast, BASE / fast))
print('new route, rate %.2f  : %.0f ticks' % (slow, BASE / slow))
print('worn route, rate %.2f : %.0f ticks' % (fast, floor / fast))
print('decay checked across %d operator rates from %.2f to %.2f' % (len(OPERATOR_RATES), slow, fast))
print('PASS: monotonic, floored, bounded, lapses, and decay is slower than progress for every operator')
