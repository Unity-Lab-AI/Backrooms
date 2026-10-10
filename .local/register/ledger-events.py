import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.8.4-dev - 2026-09-29 - things that happen

- **Things happen in the Backrooms now**, not just things being there. A noise with nothing making it. Every light switching itself off. Cold with no source. The place getting filthier. Loose things not where you left them.
- **Everything that happens has an answer you can actually perform.** The lights come back on with the same switch you already use. Cold is answered by clothing or a heater or leaving. Filth is answered by cleaning, which already works through a gate.
- **Nothing that happens can trap you.** No event hurts anyone, destroys anything, or blocks a route, and the room you arrive in is never touched.
- **Nothing that moves is ever lost** - it is somewhere else in the same space. Your money is never moved at all.
- At most two things happen per visit, and a space does not replay the same trick every time you go back.
- **Deep spaces now also contain things you have owned**, not just things you have built.

Full record: [anomaly events](docs/implementation/ANOMALY_EVENTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.4-dev' not in s
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('- [~] **"even wild waky carzxzy creepy things when u add places and events"**',
  '- [x] **"even wild waky carzxzy creepy things when u add places and events"**'),
 ('**Events remain open** — the rooms exist, things that *happen* do not.',
  '**EVENTS BUILT 0.8.4-dev**: seven of them, every one with an answer the player can actually perform, because the frozen threat rules demand one. The lights case is the best — `CompFlickable.SwitchIsOn` has a public setter, so the countermeasure is **vanilla\'s own switch** rather than a bespoke darkness mechanic. **No effect damages a pawn, destroys a thing, or blocks a route**, and the threshold room is excluded from every one, always. Record: [`implementation/ANOMALY_EVENTS_IMPLEMENTATION.md`](implementation/ANOMALY_EVENTS_IMPLEMENTATION.md).'),
 ('- [ ] **"and rooms"** — **fixtures echo; room shapes do not.** Echoing a layout the player built is a separate and larger piece of work than echoing what stands in it.',
  '- [ ] **"and rooms"** — **fixtures and now items echo; room shapes do not.** Echoing a layout the player built is a separate and larger piece of work than echoing what stands in it, because room dimensions feed the **saved layout fingerprint** and changing them touches generation\'s validation path.\n- [x] **"items and equipment and production benches"** — **BUILT 0.8.4-dev.** Benches were already covered as buildings; items needed a **different test**, and getting it right mattered: faction ownership cannot work for them, because a stack of steel in a colony stockpile has a null faction exactly like one lying in a Backrooms corridor. **Origin is the test instead** — anything stamped `Outside` came into existence somewhere the player was, which excludes the coordinate\'s own contents by the same stroke. Bonds are never echoed.\n- [ ] **"echos of thier inhabitance in weird ways"** — **the place copying your *people*, not just your things.** Its own checkpoint, and a different thing entirely from echoing objects.'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated")
