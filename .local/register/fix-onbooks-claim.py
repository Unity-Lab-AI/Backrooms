# -*- coding: utf-8 -*-
"""Key the on-the-books claim off the GUARD, not off the refusal string.

Fault-planting exposed this: replacing `if (!campaign.CanReceiveDeliveryAt(destination))` with
`if (false)` left the refusal string in place, so a claim counting that string still passed. The
guard was gone and the proof said nothing.

Second time today a claim of mine failed open by keying off a token instead of the thing that
actually happens -- invariant 152, which is easy to write and evidently easy to forget while
writing the next claim.
"""
import ast
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-remote-sites.py')
s = io.open(p, encoding='utf-8').read()

old = '''check("a delivery destination must be on the books",
      procurement.count('"RR_Proc_DestinationNotOnTheBooks"') >= 2,
      "-- quoting and redirecting must both refuse an unregistered place")'''

new = '''#    Keyed off the GUARD, not the refusal string. Counting the string passed a planted fault
#    that replaced the condition with `if (false)` and left the string sitting there unused.
check("quoting guards the destination against the books",
      "if (!campaign.CanReceiveDeliveryAt(destination))" in procurement,
      "-- any map at all could be named as a delivery address")
check("redirecting guards the destination against the books",
      "if (!campaign.CanReceiveDeliveryAt(redirectTo))" in procurement,
      "-- an in-flight order could be rerouted anywhere")
check("both guards refuse with a string the player can read",
      procurement.count('"RR_Proc_DestinationNotOnTheBooks"') >= 2,
      "-- a guard that refuses silently teaches nothing")'''

assert old in s, 'claim not found'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('on-the-books claim now asserts the guard')
ast.parse(s)
print('proof-remote-sites.py parses clean')
