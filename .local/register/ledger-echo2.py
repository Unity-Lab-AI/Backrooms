import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.8.5-dev - 2026-09-29 - the place copies your people

- **Somebody you know can be standing in a deep space**, wearing your colonist's name and the clothes they put on this morning.
- **That colonist is at home right now.** That is the whole point of it.
- It is not them. It has their name and their coat and nothing else - not their skills, not their history, not their mind.
- **It is never hostile**, and you cannot recruit it. It is not a person you can save.
- Your actual colonist is untouched and keeps their own clothes.
- If everyone is down there with you, or hurt, or gone, no echo appears at all.

Full record: [colonist echoes](docs/implementation/COLONIST_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.5-dev' not in s
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = '- [ ] **"echos of thier inhabitance in weird ways"** — **the place copying your *people*, not just your things.** Its own checkpoint, and a different thing entirely from echoing objects.'
new = ('- [x] **"echos of thier inhabitance in weird ways"** — **BUILT 0.8.5-dev.** An echo carries the **name and apparel of a colonist who is alive and at home right now** — deliberately not somebody lost, because that is the Missing family and a different, sadder feeling. **The uncanniness depends entirely on the real one being in the base at the same moment.** Only the surface is copied: no skills, traits, backstory or relationships, because copying the interior would make it a duplicate and hand the player a free second copy of their best worker. **Never hostile, never recruitable.** Apparel is copied rather than taken, or a living colonist would be stripped from across a gate. Record: [`implementation/COLONIST_ECHO_IMPLEMENTATION.md`](implementation/COLONIST_ECHO_IMPLEMENTATION.md).')
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated")
