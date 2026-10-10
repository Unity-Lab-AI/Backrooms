# -*- coding: utf-8 -*-
"""Replace a claim that could not fail.

The ordering claim was written with a conditional fallback:

    "CanUnloadAt" not in procurement.split("private int TryDeliver")[0]
    if "private int TryDeliver" in procurement else "CanUnloadAt" in procurement

`private int TryDeliver` does not exist in that file, so the whole thing collapsed to
`"CanUnloadAt" in procurement` -- trivially true, always. THIRD fail-open claim in one day.

**A claim with a conditional fallback is a claim that can be trivially true.** The property I
actually wanted is simple and cannot degenerate: `CanUnloadAt` has exactly one call site, and it
is in the delivery path. If anybody adds it to quoting, accepting or redirecting, the count moves.
"""
import ast
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-remote-sites.py')
s = io.open(p, encoding='utf-8').read()

old = '''check("ordering is NOT gated on staffing",
      "CanUnloadAt" not in procurement.split("private int TryDeliver")[0]
      if "private int TryDeliver" in procurement else "CanUnloadAt" in procurement,
      "-- a player could not order ahead while the crew was still walking there")'''

new = '''#    No conditional fallback. The first version of this claim had one, keyed off a method name
#    that does not exist in the file, so it collapsed to a trivially-true expression and could
#    never fail. One call site is the whole intent and cannot degenerate.
check("staffing is consulted at exactly one place, the arrival",
      procurement.count("CanUnloadAt") == 1,
      "-- a second call site would almost certainly be gating the ORDER, which punishes planning")
check("quoting and redirecting still use the address check only",
      procurement.count("CanReceiveDeliveryAt") == 2,
      "-- ordering ahead while the crew walks there must stay possible")'''

assert old in s, 'claim not found'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ordering claim replaced with one that cannot be trivially true')
ast.parse(s)
print('proof-remote-sites.py parses clean')
