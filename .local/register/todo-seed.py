import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = '''### Owner direction — the look, and the seed generator that has to carry the universe (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and we can use the floor lights i guess for the yellow carpet and yellow wood walls for the main backrooms look as we dont have over head florrecent lights unless we could repurpose floor lights correctly, and remmeber when building the seed genrator for the back rooms everything ive said and how the backrooms universe works to be lots of furnature and equipment and different types of rooms and materials of all types from labs, to workshops, to nursaries, to everything imanginable and every variation of them and even wild waky carzxzy creepy things when u add places and events to proper balance levels of colony wealth and the like so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"*

**And immediately after:** *"andf remmeber thats just the main backrooms looks further in it gets very varied and weird"*

That second message is what shaped the palette: a single global look could only ever deliver half the direction, so the look is a **function of depth**. Record: [`implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md`](implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md).

- [x] **"the yellow carpet and yellow wood walls for the main backrooms look"** — **BUILT 0.7.8-dev.** Core `Carpet` tinted `Structure_Mustard` through the public `TerrainGrid.colorGrid`, and Core `Wall` from `WoodLog` tinted through `CompColorable`. **No new texture, no new terrain, no new building** — the look is Core content wearing a colour.
- [x] **"we dont have over head florrecent lights unless we could repurpose floor lights correctly"** — **the game already had one.** Core ships **`WallLamp`**, wall-mounted rather than standing, which is closer to the intended look *and* frees the floor: an endless corridor reads as endless precisely because nothing is standing in it. Generation had been using `StandingLamp`, which put furniture in the middle of every room.
- [x] **"thats just the main backrooms looks further in it gets very varied and weird"** — **BUILT 0.7.8-dev** as `CoordinateRecord.depth`, counted in portals from the ordinary world. **Depth 1 is fixed and never rolls**, because the first space a player ever sees must be the yellow rooms on every seed; deeper bands roll from the coordinate's own seed and stay stable across reloads.
- [ ] **"lots of furnature and equipment and different types of rooms"** — a room archetype library with per-archetype furniture and equipment density. Today generation has six or seven room families and places a handful of fixtures.
- [ ] **"from labs, to workshops, to nursaries, to everything imanginable and every variation of them"** — the archetype set itself, and **variations within each archetype** so two labs are not the same lab. Built from existing Core and profile defs by capability, never by a hand-listed item.
- [ ] **"materials of all types"** — material variety drawn from what the loaded game actually offers rather than a fixed list, so a profile that adds materials shows them here.
- [ ] **"even wild waky carzxzy creepy things when u add places and events"** — anomalous places and events as **saved, bounded** content rather than random noise, so a revisit resumes rather than rerolls. Inherits the frozen threat rules: readable warning, learnable rule, at least one countermeasure, no unavoidable instant failure.
- [ ] **"to proper balance levels of colony wealth and the like"** — the escalation ladder scales against **colony wealth**, not wall-clock time. This is a concrete answer to a question the ladder spec previously left open, and it should be read as the owner choosing the pacing input.
- [ ] **"so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying"** — **an acceptance condition on the whole generator, not a nice-to-have.** A high-tier coordinate that cannot be survived solo by building, supplying and finding a way out has failed this direction regardless of how good it looks.
- [ ] **"from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"** — the inhabitant and monstrosity families, tiered by depth and wealth, with every variation seeded rather than authored one by one.

'''

anchor = '### Owner direction — nothing is deferred, and what the Backrooms is *for* (2026-09-29)'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("todo section added")
