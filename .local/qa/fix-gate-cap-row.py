# -*- coding: utf-8 -*-
"""Correct the row I misread, and log the owner's clarification verbatim.

LAW #0: the owner's words were kept intact, but **my reading under them was
wrong** -- I wrote "three addresses held per gate" and started building a cap on
addresses. The owner corrected it in the same breath. The wrong reading is kept
and struck rather than deleted, because a correction nobody can see is a
correction that gets made again.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

OLD = ('- [ ] **"and gates need to be able to set up a max of three of them  so u can have three '
       'addrerss called at once wich would give 4 of 5 open maps"** — **three addresses held per '
       'gate**, concurrently. The owner has done the arithmetic against the standing open-map '
       'budget: three called coordinates plus the colony is **four of five**, leaving one spare. '
       'That ties directly to `Portals/OpenMapBudget`.')

NEW = ('- [ ] **"and gates need to be able to set up a max of three of them  so u can have three '
       'addrerss called at once wich would give 4 of 5 open maps"** — ~~three addresses held per '
       'gate~~ **CORRECTED BY THE OWNER, 2026-10-04, verbatim:** *"not three address per '
       'gate!!! up to three differnt operational gates that can call any address and we need a '
       'Random address option not just company requested task and quests at specific '
       'xcorrdinates"*.'
       + NL + NL +
       '  So: **up to three operational gates**, and **each one can call any address.** The cap '
       'is on gates, not on addresses, and there is no pairing between a gate and a place. The '
       'arithmetic the owner did is exactly that: three gates each holding one open coordinate, '
       'plus the colony, is **four of five** against `Portals/OpenMapBudget`, leaving one spare.'
       + NL + NL +
       '  **The wrong reading is struck rather than deleted.** I had started building a per-gate '
       'address cap off it; a correction nobody can see is a correction that gets made again.')

CLARIFICATION = '''
### Owner clarification and new direction — three operational gates, any address, and a random one (2026-10-04)

**Verbatim owner correction (2026-10-04):** *"not three address per gate!!! up to three differnt operational gates that can call any address and we need a Random address option not just company requested task and quests at specific xcorrdinates"*

- [ ] **"not three address per gate!!!"** — recorded as the correction it is. The cap is on **gates**, not on addresses held by one.
- [ ] **"up to three differnt operational gates"** — **three** gates may be operational at once. Enforced where a door becomes a gate, so the player meets the limit at the moment they would exceed it rather than at the moment they try to open one.
- [ ] **"that can call any address"** — **no pairing.** A gate is not bound to a place; any operational gate can dial any address the branch knows. This is also what makes three gates worth having rather than three copies of the same route.
- [ ] **"and we need a Random address option not just company requested task and quests at specific xcorrdinates"** — **dial somewhere nobody asked for.** Every coordinate today arrives because something named it: a request, a quest, a contract. A random dial is the player choosing to go *looking*, and it is the thing that makes the gate an instrument of exploration rather than a delivery chute. It needs its own address, discovered on the dial rather than granted.

'''

text = io.open(TODO, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("cannot find the row to correct exactly once (%d)" % text.count(OLD))
    sys.exit(1)
text = text.replace(OLD, NEW)

anchor = "## Pending" + NL
if text.count(anchor) != 1:
    print("cannot find the single Pending heading")
    sys.exit(1)
at = text.index(anchor) + len(anchor)
text = text[:at] + NL + CLARIFICATION + text[at:]

io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("row corrected and clarification logged, %d new rows" % CLARIFICATION.count("- [ ] "))
