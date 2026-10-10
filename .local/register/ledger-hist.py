import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.8.8-dev - 2026-09-29 - a gate remembers where it has been

- **Every laboratory gate keeps its own list of everywhere it has connected to.**
- **Two gates keep two different lists.** A gate at home and a gate at an outpost are running different operations.
- **Rename an address to something you can actually navigate by.** Clear the name again to get the original back.
- **Pin the ones that matter.** Pinned addresses survive a clear and are never dropped to make room.
- Remove one entry, or clear the noise in one go.
- Connecting somewhere you have been before updates that entry instead of adding another.
- **A natural portal has no list at all.** Its destination is fixed where you found it and it cannot be dialled.

Full record: [gate connection history](docs/implementation/GATE_CONNECTION_HISTORY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.8-dev' not in s
s = s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('- [ ] **"a proper history list that lab gates are connected have connected to"**',
  '- [x] **"a proper history list that lab gates are connected have connected to"** — **BUILT 0.8.8-dev.** Recorded at exactly one point: the success branch of `RegisterLaboratoryAddress`, which is the single moment a laboratory gate dials a coordinate. Repeat connections **update** the entry rather than appending, keeping it an address book rather than a log. Record: [`implementation/GATE_CONNECTION_HISTORY_IMPLEMENTATION.md`](implementation/GATE_CONNECTION_HISTORY_IMPLEMENTATION.md).'),
 ('- [ ] **"easily editable clear able and manage"**',
  '- [x] **"easily editable clear able and manage"** — **BUILT 0.8.8-dev.** Rename, pin, remove, clear. **Clear keeps pinned entries deliberately**: in a long game "clear" means get rid of the noise, and a button that also destroyed the addresses somebody explicitly marked would be a **trap rather than a convenience**. Renaming reuses **the game\'s own rename dialog**, so there is no second rename UI to keep consistent.'),
 ('- [ ] **"connected to the portal gates"**',
  '- [x] **"connected to the portal gates"** — **BUILT 0.8.8-dev**, per gate rather than per branch. **Two gates keep different address books**, which is the right shape rather than a convenience: a gate at headquarters and one at an outpost are running two different operations, and merging them would lose the distinction that makes a second gate worth building.'),
 ('- [ ] **"natural gates dont get to call a seed they are what they are"**',
  '- [x] **"natural gates dont get to call a seed they are what they are"** — **HELD 0.8.8-dev, and it needed no new guard.** Every gate gizmo already sits behind `IsDesignated`, true only of a laboratory gate the player assembled; a natural threshold registers through `RegisterNaturalAddress`, has no gate behind it, and never reaches the code. **Adding a second check would have implied the first was unreliable** — the same reasoning that kept survivor recruitment from special-casing a gate.'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

anchor = '- [ ] **Facilities** — larger functional spaces, as distinct from rooms and corridors.'
extra = '- [ ] **Dialling from the history.** The list records and manages; selecting an entry to *re-open* that coordinate is the natural next step, and is a separate interaction with its own permission checks.\n'
assert anchor in s
s = s.replace(anchor, extra + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated")
