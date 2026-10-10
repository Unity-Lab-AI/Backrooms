import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = '''### Owner direction — the place copies you, and who you find in it (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and we need a dynamic procederually gernation of BAckrroms so that new equipement and rooms and shit going into the backrooms and build there or in the real world can start appearing in lower levels of back rooms seeds"*

**And immediately after:** *"alla trhings are possible finding random pawns of disappering, findeding dead ones pasycholitc ones lost pawns all kinds of crazy variations as per the lore"*

- [x] **"new equipement ... going into the backrooms and build there or in the real world can start appearing in lower levels"** — **BUILT 0.8.1-dev** as a saved, bounded register of what the branch has actually built, sampled on a rotating window rather than hooked into construction. Deep coordinates answer 40% of their furniture slots from it. Record: [`implementation/CONSTRUCTION_ECHO_IMPLEMENTATION.md`](implementation/CONSTRUCTION_ECHO_IMPLEMENTATION.md).
- [x] **"build there or in the real world"** — faction ownership is the test, so a bench assembled inside a coordinate counts exactly as much as one in the colony. **Generated Backrooms furniture is excluded**, or the place would echo its own furniture back at itself and every deep coordinate would converge on the same room.
- [ ] **"and rooms"** — **fixtures echo; room shapes do not.** Echoing a layout the player built is a separate and larger piece of work than echoing what stands in it.
- [ ] **A reading the owner may want to reversed:** *"lower levels"* is implemented as **deeper** coordinates. In Backrooms lore a lower *number* is usually shallower, so this is genuinely ambiguous. It is read as deeper because the owner has consistently said *"further in"* for depth and the mechanic is far stronger as a progression reveal than as something present at the entrance. **Flipping it is a one-constant change.**

**The pawn direction, which is what the escalation ladder was built to pace:**

- [ ] **"finding random pawns"** — people present in a coordinate who were not put there by the player, found rather than spawned at them.
- [ ] **"of disappering"** — pawns who have gone missing, including, where the lore supports it, ones the branch itself lost.
- [ ] **"findeding dead ones"** — corpses and what they were carrying, as discoverable content rather than as a threat.
- [ ] **"pasycholitc ones"** — hostile or unstable people, which is where the ladder's encounter cap and its warning-first rule actually bind.
- [ ] **"lost pawns"** — survivors who can be recovered, which is the counterweight that makes a coordinate worth entering rather than only worth surviving.
- [ ] **"all kinds of crazy variations as per the lore"** — variations generated from depth and seed rather than authored one by one, the same shape the room archetypes use.
- [ ] **Every one of these is held to the frozen threat rules** already recorded: readable warning, learnable rule, at least one countermeasure, and no unavoidable instant failure. The ladder built in 0.8.0-dev already caps how many may act at once and guarantees half of every coordinate is quiet.
- [ ] **And to the traversal invariant:** an inhabitant may never decide anything about a gate. Anything found in a coordinate leaves only carried out by the branch's own people.

'''

anchor = '### Owner direction — the look, and the seed generator that has to carry the universe (2026-09-29)'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("todo section added")
