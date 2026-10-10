import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.8.2-dev - 2026-09-29 - who you find down there

- **There are people in the Backrooms now.** Wanderers who do not explain themselves, survivors who will leave with you, people who went missing, and ones who have been down there far too long.
- **A missing person may be somebody you lost.** The Backrooms remembers people it keeps, and gives you the name back.
- **Bodies are there from the first visit**, carrying what they came in with. Older ones have been picked over.
- **Living things are not there on your first visit.** They arrive as a space gets worse, and a space only gets worse from what you did there.
- **Never more than three hostiles at once**, at any depth, at any wealth.
- **You get told before you meet one.** Hostiles hold their ground rather than hunting you, so backing out is always a real option.
- Nothing you find down there will follow you through a gate on its own.
- Nobody is ever standing between you and the way back.

Full record: [inhabitants](docs/implementation/INHABITANTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.2-dev' not in s
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('- [ ] **"finding random pawns"**',
  '- [x] **"finding random pawns"** — **BUILT 0.8.2-dev** as the wanderer family, placed on **arrival** against the ladder\'s band rather than baked in at generation. Record: [`implementation/INHABITANTS_IMPLEMENTATION.md`](implementation/INHABITANTS_IMPLEMENTATION.md).'),
 ('- [ ] **"of disappering"**',
  '- [x] **"of disappering"** — **BUILT 0.8.2-dev**, and it lands because **the name is one the player knows**. A missing person draws from the branch\'s own register of people it lost inside a coordinate. Bounded at 24, drops the oldest, and **consumes** a name when used, so the same colonist is never found twice — the only honest reading of "missing".'),
 ('- [ ] **"findeding dead ones"**',
  '- [x] **"findeding dead ones"** — **BUILT 0.8.2-dev** as three body families placed at **generation**, because a corpse is discoverable content and finding one should not wait on a danger band. Generated then **killed** rather than spawned dead, so a body has a real cause, a real age and real belongings; **a body with nothing on it is a prop rather than a find.** One family is deliberately stripped — an old one, long picked over.'),
 ('- [ ] **"pasycholitc ones"**',
  '- [x] **"pasycholitc ones"** — **BUILT 0.8.2-dev** as two families, one of them a pack at depth 5+. **Hostility is enforced in code, not trusted in data**: a `ConfigErrors` check rejects any hostile family that is not Psychotic, because a hostile family that does not read as hostile breaks the warning-first rule. They get a **defend-point lord, not an assault lord**, so backing off is a real countermeasure rather than a delayed death.'),
 ('- [ ] **"lost pawns"**',
  '- [~] **"lost pawns"** — **SURVIVORS BUILT 0.8.2-dev**: alive, neutral, and carryable out through a gate by the branch\'s own people. **A dedicated recovery interaction does not exist yet**, so this stays in progress.'),
 ('- [ ] **"all kinds of crazy variations as per the lore"**',
  '- [x] **"all kinds of crazy variations as per the lore"** — **BUILT 0.8.2-dev.** Counts, appearance chances and identities all roll from the coordinate seed combined with its opening count, so a later arrival is not a rerun of the first while a single arrival stays stable. Eight families across the five kinds.'),
 ('- [ ] **Every one of these is held to the frozen threat rules**',
  '- [x] **Every one of these is held to the frozen threat rules** — **ENFORCED 0.8.2-dev.** Readable warning (a letter pointing at the pawn, before contact), learnable rule (hostiles hold ground), countermeasure (withdrawal genuinely works), no unavoidable instant failure (the ladder\'s absolute cap of three, quiet rooms never used for people). Was: '),
 ('- [ ] **And to the traversal invariant:**',
  '- [x] **And to the traversal invariant:** — **HELD 0.8.2-dev.** Nothing in the inhabitant layer touches gates; `PortalTraversalPolicy` remains the single chokepoint. The **threshold room is never used** either, so nothing is ever standing between the player and the way back. Was: '),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

anchor = '- [ ] **"and rooms"**'
extra = ('- [ ] **Recruiting a survivor.** They exist, are neutral, and can be carried out; a dedicated recovery interaction — the thing that turns finding one into gaining one — does not exist yet.\n')
assert anchor in s
s = s.replace(anchor, extra + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated")
