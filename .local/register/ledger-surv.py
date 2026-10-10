import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.8.3-dev - 2026-09-29 - getting somebody out, and earning what comes against you

- **You can offer a survivor passage home.** They accept - there is no negotiation and no recruitment roll. Somebody lost down there who meets a team with a way out wants to leave.
- **Joining is what lets them walk out.** Until they accept they are an inhabitant, and an inhabitant cannot use a gate at all - the only way out for them is to be carried, like anything else you find.
- One of your people has to actually be standing there to make the offer.
- **The Backrooms now starts by sending one thing at a time**, not three.
- **It only sends more once you have gone deeper than you ever have**, and when that happens it is written into your branch history so you can see the moment the rules changed.
- Stay shallow and it stays at one, however rich or advanced you get.
- It never goes past three.

Full record: [survivors and cap progression](docs/implementation/SURVIVORS_AND_CAP_PROGRESSION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.3-dev' not in s
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('- [~] **"lost pawns"**',
  '- [x] **"lost pawns"**'),
 ('**A dedicated recovery interaction does not exist yet**, so this stays in progress.',
  '**RECOVERY BUILT 0.8.3-dev.** Offering passage, not recruiting: no negotiation and no roll, because somebody lost down there who meets a team with a way out wants to leave. **Joining is also what lets them walk out** — until they accept they are an inhabitant and cannot use a gate at all, so the only way out for them is to be carried. Nothing special-cases a gate; `PortalTraversalPolicy` stays the one chokepoint and this is one more caller obeying it. Record: [`implementation/SURVIVORS_AND_CAP_PROGRESSION_IMPLEMENTATION.md`](implementation/SURVIVORS_AND_CAP_PROGRESSION_IMPLEMENTATION.md).'),
 ('- [ ] **Recruiting a survivor.** They exist, are neutral, and can be carried out; a dedicated recovery interaction — the thing that turns finding one into gaining one — does not exist yet.',
  '- [x] **Recruiting a survivor** — **BUILT 0.8.3-dev.** The comp is dormant on every pawn and does nothing unless a coordinate marked that person as a survivor it produced, the same dormant-until-designated pattern the gate and beacon comps use. One of the branch\'s own people must be **present** to make the offer.'),
 ('- [ ] **Raising an encounter cap as a recorded progression step**, which the 2026-09-28 ladder direction requires and 0.8.0-dev does not yet do.',
  '- [x] **Raising an encounter cap as a recorded progression step** — **BUILT 0.8.3-dev**, closing the **last unmet clause of the 2026-09-28 ladder direction**. The cap opens at **1**, not at the ceiling, and rises only when the branch reaches a depth it has never reached. Deliberately not research and not wealth: wealth already feeds the ladder\'s ceiling so reusing it would **double-count one input**, and research is not an act of exploration. **A branch that stays shallow stays at one forever**, however rich it becomes. Idempotent, so a cap cannot be walked up by re-entering one space, and a step that hits the ceiling is still recorded because the history should show the branch went deeper.'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated")
