import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.8.7-dev - 2026-09-29 - the deeper it is, the less it pretends

- **Hallways can hold anything.** A production bench in a corridor is not a mistake down there.
- **Shallow spaces still make sense.** Deep ones stop bothering, and the change is gradual rather than a switch.
- **Some rooms in a deep space still read as ordinary**, on purpose. If everything is wrong, nothing is unsettling.
- **The strange kinds of room get commoner the further in you go**, until the ordinary ones are the surprise.
- **What you find scales with what you have researched and how deep you have pushed.** A young colony finds crude things; an advanced one starts turning up spacer equipment.
- **A deep space is worth going back to.** The same coordinate after a hundred hours of research is a different place.

Full record: [coherence and tech scaling](docs/implementation/COHERENCE_AND_TECH_SCALING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.7-dev' not in s
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

old = '- [ ] **Archetypes are not yet constrained by structural family** — any archetype can currently dress any non-threshold room, so **a hallway can be furnished as a nursery**. Hallways now exist as a shape; teaching the dresser that a corridor is a corridor is the next piece.'
new = '''- [x] **Archetypes are not constrained by structural family, and the owner confirmed that is correct** — **RESOLVED 0.8.7-dev.** The gap named in the previous checkpoint was **not a bug**: *"hallways can have furniture and produiction benches too"*. A bench in a corridor is exactly right for the setting, because **the wrongness is the content**. So nothing was constrained; instead **coherence decays** with depth and branch advancement. Record: [`implementation/COHERENCE_AND_TECH_SCALING_IMPLEMENTATION.md`](implementation/COHERENCE_AND_TECH_SCALING_IMPLEMENTATION.md).

**Verbatim owner direction (2026-09-29):** *"hallways can have furniture and produiction benches too remember things are almost completely fucking werid and crazy odd and scary looking the deeping in the backrooms and higher the gete quality and rtesarch levels and tech and stuff ec t ect"*

- [x] **"things are almost completely fucking werid ... the deeping in the backrooms"** — **BUILT 0.8.7-dev.** Rolled **per room**, so some rooms in a deep space still read as ordinary: **a space where everything is wrong stops being unsettling and starts being noise. The contrast is what works.** Anomalous archetypes also grow heavier until the ordinary ones are the surprise.
- [x] **"higher the gete quality and rtesarch levels and tech and stuff"** — **BUILT 0.8.7-dev.** What a coordinate produces rises with research finished and depth reached, never above the archetype's own declared ceiling. **Also means a deep space is worth revisiting**: the same coordinate after a hundred hours of research is a different place, with nothing authored twice.
- [x] **Depth and advancement are capped separately** so neither alone can max the place out — depth is what the player chose to risk, advancement is what they earned, and the worst of it wants both.
- [x] **A real defect fixed:** `maxTechLevel` was emitted in the archetype XML for fourteen defs while the C# class had no such field, so it had been **failing silently at load since 0.7.9-dev**. RimWorld logs an unknown field and carries on; nothing in the build or any checker noticed.
- [ ] **An unknown-def-field checker, written and then removed rather than shipped.** It would have caught the defect above. Every part was verified correct in isolation — the field parser reads all seven fields, the XML walk reaches the right node, the comparison flags a planted bad child — but **the assembled function reported nothing**. It was removed because **a checker that silently passes everything is worse than no checker: it manufactures confidence**, and that is the same failure mode designed out of the layout derangement one checkpoint earlier. The next attempt should start from the verified parts rather than from scratch.

**Verbatim owner direction (2026-09-29), arriving during this checkpoint:** *"and we need a proper history list that lab gates are connected have connected to in a easily editable clear able and manage bench connected to the portal gates natural gates dont get to call a seed they are what they are"*

- [ ] **"a proper history list that lab gates are connected have connected to"** — an address book of every coordinate a laboratory gate has dialled, held against the gate.
- [ ] **"easily editable clear able and manage"** — the player can rename, reorder, remove and clear entries. A history nobody can prune becomes unusable in a long game.
- [ ] **"connected to the portal gates"** — the list belongs to the gate rather than to the branch, so two gates can keep different address books.
- [ ] **"natural gates dont get to call a seed they are what they are"** — **a natural gate has no address book and may not dial.** Its destination is fixed at discovery and permanent. This is already true of the traversal layer and must stay true: the history feature is a *laboratory gate* capability and must not be offered on a natural one.
- [ ] **Facilities** — larger functional spaces, as distinct from rooms and corridors.'''
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated")
