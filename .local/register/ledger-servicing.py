import io

# --- CHANGELOG
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.7.1-dev - 2026-09-29 - the gate assembly needs looking after

- **A gate now holds a condition that slowly wears down**, and somebody has to recondition it before it runs out. A gate with nothing left will not open until it is seen to.
- **How fast it wears depends on how you keep the room.** A clean, sterile gate chamber wears at half rate; a filthy one wears at triple. Look after the place and the gate mostly looks after itself.
- **An unpowered assembly degrades eight times faster**, so cutting the power has a cost beyond closing the gate.
- Holding a connection open wears it faster too.
- **Nobody is sent to it until it actually needs it.** Above a quarter condition the job is not offered at all, so your people are not forever fiddling with the gate. Reconditioning restores it fully in one visit.
- Running out **never slams a gate shut on people who are already through**. It stops the next opening; it does not end one in progress.

Existing gates load in full condition, so nothing you already built is suddenly out of service.

Full record: [gate servicing](docs/implementation/GATE_SERVICING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
s = s if '0.7.1-dev' in s else s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- TODO
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = '- [ ] **"maintained amounts of maintance ... on equipment but not crazy amounts"** — **GENUINELY NEW. There is no equipment-upkeep concept anywhere in the gate today.**'
new = ('- [x] **"maintained amounts of maintance ... on equipment but not crazy amounts"** — **BUILT 0.7.1-dev**, modelled on the reference the owner gave in a later message (see below). Was: **GENUINELY NEW. There is no equipment-upkeep concept anywhere in the gate today.**')
assert old in s
s = s.replace(old, new, 1)

block = """### Owner direction — model gate upkeep on Questionable Ethics' vats (2026-09-29)

**Verbatim owner requests (2026-09-29, two items):** *"kinda like maintaince for growth vats questionable ethitcs so pawns dont have to always do it but there is a cool down dead zone where its fine"* and, correcting my misreading, *"i said i was refresncing the mod \\"Questional ethics\\" and how maintaince works on cloning vats and organ vats"*.

**I first read "questionable ethics" as flavour and went as far as asking which way to take the ethics angle. That was wrong.** It is a **mod name** — *Questionable Ethics Enhanced*, **profile row 182** — and the owner was pointing at a concrete, proven mechanic. **The register recovered it in one query**, and its review carried the package id and install path that led to the mod's own defs.

Record: [`implementation/GATE_SERVICING_IMPLEMENTATION.md`](implementation/GATE_SERVICING_IMPLEMENTATION.md).

- [x] **"how maintaince works on cloning vats and organ vats"** — read from that mod's own shipped description: *"Requires regular maintenance by a skilled scientist and doctor. A sterile room will significantly decrease the maintenance required. If the vat loses power, it will rapidly lose maintenance."* Three ideas, all better than a service timer: a condition that **decays continuously**; **the room modulating the decay**; and **power loss degrading it fast**.
- [x] **"so pawns dont have to always do it but there is a cool down dead zone where its fine"** — the dead zone **falls out of the model rather than being bolted on**. A well-kept room decays so slowly that nobody is called for a long stretch; a filthy one calls somebody constantly. **The player controls the dead zone by looking after the place.** Reinforced by a hard threshold: the work is offered only below a quarter condition and restores full in one visit, so nobody tops it up continuously — the growth-vat-one-nutrition-short trap.
- [x] **Nothing of that mod is copied, referenced or depended on.** Its defs and assembly are untouched and the feature works with it absent. The idea was read from its public description exactly as every profile row is read, which honours *"we are making a mod that works with the other 274, WE ARE NOT EDITING OTHER PEOPLES MODS!"*
- [x] **It plugs into what already exists** rather than sitting beside it: cleanliness is kept by the cleaning family (which already crosses a gate), power ties to the kill switch built the checkpoint before, and skill reuses the `Research` work type calibration already uses, so **no new work type is added**.
- [x] **Lapsing stops the next opening and never closes one already running** — ending an opening for a bookkeeping reason would strand whoever is on the far side.

"""
old2 = "### Owner direction — the gate must keep meeting its requirements, and a how-to is owed (2026-09-29)"
assert old2 in s
s = s.replace(old2, block + old2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- DEFERRED
p = 'docs/DEFERRED.md'
s = io.open(p, encoding='utf-8').read()
old = '- [ ] **Equipment maintenance on the gate** — requested 2026-09-29 and **genuinely new**: no upkeep concept exists in the gate today. The owner\'s ceiling is explicit — not *"crazy amounts"*. Its own checkpoint.'
new = ('- [x] **Equipment maintenance on the gate** — **BUILT 0.7.1-dev**, modelled on *Questionable Ethics Enhanced* (profile row 182) as the owner intended: a condition that decays continuously, modulated by **room cleanliness**, degrading eight times faster without power. The dead zone falls out of the model, reinforced by a quarter-condition threshold. Nothing of that mod copied or depended on.')
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated for 0.7.1-dev")
