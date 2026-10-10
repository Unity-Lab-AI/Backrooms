import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.8.6-dev - 2026-09-29 - the shape of the place

- **Deep spaces are not built to a grid any more.** Rooms stretch, shrink and go wrong, and they go wronger the further in you are.
- **Some of them are shaped like rooms you built.** The place took their proportions when it opened - not what you have built since.
- **Lots of hallways.** Long narrow corridors that are corridors on purpose, not by accident.
- **The shallow yellow rooms stay regular.** That monotony is the look, and it is left alone. The wrongness is something you travel toward.
- Spaces you already found are completely unchanged, down to the last cell.
- Building an extension at home does not reshape a space you have already opened.

Full record: [room shape echoes](docs/implementation/ROOM_SHAPE_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.6-dev' not in s
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = '- [ ] **"and rooms"** — **fixtures and now items echo; room shapes do not.** Echoing a layout the player built is a separate and larger piece of work than echoing what stands in it, because room dimensions feed the **saved layout fingerprint** and changing them touches generation\'s validation path.'
new = ('- [x] **"and rooms"** — **BUILT 0.8.6-dev.** The fingerprint problem was the whole difficulty and it is solved by **snapshotting at discovery rather than reading live**: planning is re-run to verify a saved graph, so a planner consulting the colony\'s *current* rooms would replan a coordinate differently once the player built an extension and **fail its own fingerprint check**. Existing coordinates stay on `roomLibraryVersion` 1 and plan byte-identically. Record: [`implementation/ROOM_SHAPE_ECHO_IMPLEMENTATION.md`](implementation/ROOM_SHAPE_ECHO_IMPLEMENTATION.md).\n'
       '\n'
       '**Verbatim owner directions (2026-09-29, three more):** *"remember the back rooms is random on crack and lsd creepy horror flick"*; *"and remebre it not just rooms its weirtd and lots of halways and halway/rooms and facilitys and noraml like rooms all furnished with theri proper room equipement to the extent we want normal and really want the creepy insane looks and feel of the universe"*; *"and items"*.\n'
       '\n'
       '- [x] **"random on crack and lsd creepy horror flick"** — **BUILT 0.8.6-dev** as depth-driven derangement: proportions stretch further the deeper a coordinate sits. **Depth 1 is deliberately exempt** — the yellow rooms read as a place precisely because they are monotonous, and deranging them would throw away the image the setting rests on. The wrongness is something the player travels toward.\n'
       '- [x] **"lots of halways and halway/rooms"** — **BUILT 0.8.6-dev**, and made **deliberately rather than hoped for**: a corridor is one of the two shapes the setting is built on, and leaving it to a symmetric stretch roll would produce one rarely and by accident. Its own branch, long and narrow on one axis.\n'
       '- [x] **"all furnished with theri proper room equipement"** and **"and items"** — **ALREADY COVERED** by the archetype library built in 0.7.9-dev: fourteen archetypes fill rooms by capability, including item slots drawn from thing categories, so a workshop gets benches and material and a ward gets beds and medicine. Said plainly rather than rebuilt.\n'
       '- [ ] **Archetypes are not yet constrained by structural family** — any archetype can currently dress any non-threshold room, so **a hallway can be furnished as a nursery**. Hallways now exist as a shape; teaching the dresser that a corridor is a corridor is the next piece.\n'
       '- [ ] **"facilitys"** — larger functional spaces, as distinct from rooms and corridors.\n'
       '- [ ] **"to the extent we want normal and really want the creepy insane looks and feel"** — the balance between recognisable and wrong is currently fixed by the depth curve. Whether it lands is a play question and belongs to the post-completion test phase.')
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated")
