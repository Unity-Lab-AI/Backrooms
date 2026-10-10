# -*- coding: utf-8 -*-
"""Version bump and changelog for 0.12.83-dev."""
import io

NL = chr(10)

for path in ["Mod/Rimrooms - Async Industries/About/About.xml",
             "src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj",
             "README.md"]:
    text = io.open(path, encoding="utf-8").read()
    count = text.count("0.12.82-dev")
    assert count >= 1, path
    io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace("0.12.82-dev", "0.12.83-dev"))
    print("%s: %d bumped" % (path, count))

ENTRY = '''## 0.12.83-dev - 2026-10-04 - A floor has an architecture, forty-four kinds of room, and the freeze says so first

- **A coordinate has a motif, and its rooms vary from it.** Seven room shapes already existed and
  every room rolled its own independently of every other room, which does not make a pattern, it
  makes noise: one room a wedge, the next bays, the next a cross, reading as damage rather than
  architecture. A coordinate now draws one shape and one theme from its own seed, and how hard
  that grip holds falls with depth. Measured: rooms on the motif shape run at 89.3% at the first
  level, 72.3% at depth 3, 44.5% at depth 6 and 36.5% at depth 8, with all seven shapes present at
  every depth and a random floor sitting at 14.3%. **One number produces both the monotonous
  shallow floors the yellow look depends on and the incoherent deep ones.**
- **Forty-four kinds of room, up from sixteen, and a floor is somewhere rather than a list.**
  Archetypes were drawn against their own weight alone, so a coordinate held a classroom beside a
  weapons locker beside a nursery. Each now declares which kinds of place it belongs to, and a
  coordinate's own theme makes a matching one three times likelier - a bias and never a filter,
  because a market holding nothing but shops is a themed level rather than a Backrooms level.
- **The kinds that were asked for, by name, and twenty-one more besides.** Shop fronts, mall
  concourses, food courts, checkout lanes, stockrooms, barracks, checkpoints, motor pools,
  briefing rooms, apartments, laundries, play rooms, stairwell landings, service tunnels,
  substations, pump houses, roadways, cinemas, waiting rooms, changing rooms, records vaults,
  quiet rooms and infirmaries - plus endless shelving whose aisles meet at the far end, a room
  with its furniture moved to one wall still facing the way it was, a ward symmetrical about an
  axis the door is not on, and a room holding one chair, in the middle, facing a corner.
  Forty-four archetypes against seven shapes is over three hundred distinguishable rooms before a
  single slot is rolled.
- **The generation freeze now says so before it happens.** Carving a 300x300 map runs on the main
  thread inside Core's map generation, and an unexplained freeze reads as a crash. Both of the
  Operations pane's openings now show a full-screen notice first, carrying one of the mod's own
  menu images, and the generation then runs inside a long event whose wait text is ours. There is
  a tone per shipped scenario: the company reads an instrument, the shop reads its own back room,
  and somebody alone in the dark reads neither.
- **The main menu opened on the same picture every single time.** The slide index was pinned to
  zero in the constructor and reset to zero again in the settings handler, so the first thing
  anybody ever saw - and the backdrop behind every load started from the menu - was slide one of
  six, forever. Drawn at random now, from the wall clock rather than from the game's seeded
  randomness, which every generated place depends on.
- Internal: eight archetypes shipped with furniture and nothing worth carrying out, which an
  existing proof caught against a standing owner direction. The layout probe keeps no copy of the
  shape rule and measures it from the planner's own function. A theme tag that nothing can draw is
  now a load-time config error naming the def, because the alternative is completely silent.
  Twenty-three plant suites, 836 anchors; the menu art had no plant coverage at all this morning.

'''

path = "CHANGELOG.md"
text = io.open(path, encoding="utf-8").read()
head = "# Changelog" + NL + NL
assert text.startswith(head)
io.open(path, "w", encoding="utf-8", newline=NL).write(head + ENTRY + text[len(head):])
print("changelog entry prepended")
