import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

# 1. The dialling item closes this checkpoint.
old = '- [ ] **Dialling from the history.** The list records and manages; selecting an entry to *re-open* that coordinate is the natural next step, and is a separate interaction with its own permission checks.'
new = ('- [x] **Dialling from the history.** The list records and manages; selecting an entry to *re-open* that coordinate is the natural next step, and is a separate interaction with its own permission checks. '
       '— **BUILT 0.8.9-dev as a spin-up rather than a button**, per the owner direction recorded below. Dialling registers the address (idempotent) and then **ramps**; the ramp is the only way a laboratory gate opens, from any entry point.')
assert old in s
s = s.replace(old, new, 1)

# 2. The depth reading is answered, not flagged.
old = '- [ ] **A reading the owner may want to reversed:**'
new = '- [x] **CONFIRMED BY THE OWNER 2026-09-29 — higher number means deeper.** Asked directly rather than left as a flag; the built reading is correct and nothing changes. Original note retained: **a reading the owner may want to reversed:**'
assert old in s
s = s.replace(old, new, 1)

block = u"""
**Verbatim owner direction (2026-09-29), arriving during the 0.8.9-dev checkpoint:** *"when u establish a backrooms portal connection the specific addresss should be connected and the gate opened but it neededs to be a ramp up process that takes a bit of time like with everything the pawns needs to do/maintaing/ operate to opening the gate process like a item build in a way"*

- [x] **"a ramp up process that takes a bit of time"** — **BUILT 0.8.9-dev.** Opening a laboratory connection is now **work, not a button**. It accumulates at the assigned operator's own working speed, shows a progress bar on the console, and only then opens the gate.
- [x] **"like with everything the pawns needs to do/maintaing/ operate"** — **BUILT 0.8.9-dev.** The ramp climbs **only while the gate is actually held**: operator on station, power and headroom present, cutoff not thrown. Left alone it **bleeds back down** and lapses at zero with a message. **Decay is slower than progress on purpose** — walking away costs real time but never instantly erases a long ramp, which is the same "no unavoidable instant failure" rule every threat in this mod obeys.
- [x] **"like a item build in a way"** — **BUILT 0.8.9-dev.** Taken literally: a work amount, a progress bar, and a readout in the same shape as a build in progress. The existing `RR_OperateGate` station job already sat the operator at the console with a **useless binary progress bar**; it now shows the real ramp, so **no new job def was needed**.
- [x] **The ramp belongs to opening, not to one button.** Three things could start an opening — dialling a remembered address, opening a session from the operations window, and opening straight after registering. All three now route through the same ramp, so **there is exactly one way a gate opens** and it cannot be skipped by choosing a different entry point.
- [x] **The address book now earns its keep.** Required work falls with every previous connection this gate has made to that address, floored so a well-worn route is quick but **never free**. That turns the 0.8.8 history from a convenience list into the gate's **learned routes**, and it is why pinning an entry protects something real: the familiarity count lives on the entry, so evicting it costs the discount too.

**Verbatim owner direction (2026-09-29):** *"yes the gates are just repurosed doors of the game with a bue tint and maybe a blue light glow hue around it like light through a glass wall does"*

- [x] **"just repurosed doors of the game"** — **ALREADY TRUE, and stated rather than rebuilt.** A gate is a Core `Door` or `Autodoor` carrying a dormant component; it becomes a gate only when the player designates it. No gate object is added by this mod.
- [x] **"a bue tint"** — **BUILT 0.8.9-dev, and it needed no new component and no new patch operation.** `ThingWithComps.DrawColor` already consults **`ThingComp.ForceColor()`** on every component a thing carries, and the gate component is already on the door. Overriding that one hook tints a designated gate and leaves **every other door in the game untouched**. Verified by decompiling `Verse.ThingWithComps` and `Verse.ThingComp` rather than assumed.
- [x] **"a blue light glow hue around it like light through a glass wall does"** — **BUILT 0.8.9-dev.** The cosmetic aura already existed but only appeared **while the gate was open**; it is now the gate's permanent identity — a soft steady blue when designated, brighter while a connection is live, and the existing amber when something has gone wrong. Still a native fleck with fixed colour and size: **no new art, no new graphic resource**.
- [x] **A player's own paint still wins.** Core checks a painted colour *before* `ForceColor()`, so somebody who deliberately painted that door keeps their colour. That is the right outcome — an explicit choice beats an automatic tint — and the glow still marks it as a gate.

**Verbatim owner direction (2026-09-29):** *"and rember ther are 1x1 1x2 and 1x3 and 2x3 gate doors that allow differnt capabilities as to the universe and scerios needs fyi all starts have same tech tree just differnt starting researches finished based on scenerio"*

- [ ] **"1x1 1x2 and 1x3 and 2x3 gate doors"** — **OWNER ANSWERED 2026-09-29: BOTH paths.** Core ships only 1x1 `Door` and `Autodoor`, verified against installed game data. So: **(a)** a gate binds across a **run of adjacent Core doors** — two side by side is a 1x2 gate, three is 1x3, a 2x3 block is six doors — which is existing-content-only and works with zero dependencies; **and (b)** when **Doors Expanded** (register row 77) is installed, its multi-cell door defs are **also** accepted as single-thing gates of the matching size. Core path always works; the mod path is a bonus, never a requirement.
- [ ] **"allow differnt capabilities"** — width is the capability. How many people cross abreast, whether bulk cargo, pack animals or a vehicle fits through, and what the opening draws. To be specified per size as part of the multi-cell gate work.
- [ ] **"all starts have same tech tree just differnt starting researches finished based on scenerio"** — **one tech tree, never a per-scenario tree.** A scenario differs only in **which projects are already complete at the start**. This directly shapes the three starting sites and must be built into the versioned start contract rather than bolted onto each scenario.

**Verbatim owner direction (2026-09-29):** *"and at deeper levels i do want monstrosities and npcs to "Chase" pawns/ kill them all the way to the gate, and even at higher techs they can come through the portal into your base and attack, kidnap, steal, do everything npcs can do in game"*

- [ ] **"Chase" pawns/ kill them all the way to the gate"** — pursuit that does not give up at a room boundary. At qualifying depth an inhabitant follows a fleeing pawn to the threshold itself.
- [ ] **"they can come through the portal into your base"** — **OWNER ANSWERED 2026-09-29: depth plus tech, while an opening is live.** It must chase a pawn to the threshold while the gate is open; reaching it before the gate closes is what brings it through. **Closing the gate is the countermeasure** — which makes the emergency cutoff a real tactical decision instead of only a safety feature, at the cost of stranding whoever is still inside.
- [ ] **"attack, kidnap, steal, do everything npcs can do in game"** — once through, it is an ordinary hostile pawn on a player map and every native behaviour applies. Nothing bespoke should be written for behaviour the game already has.
- [ ] **This does not break the traversal chokepoint, and must not.** Invariant #1 says an inhabitant may never decide anything about a gate. That stays true: **`PortalTraversalPolicy` gains a rule permitting hostile crossing under named conditions**, and the inhabitant still decides nothing. The policy is the only thing that may ever say yes.

**Verbatim owner direction (2026-09-29), on ordering the remaining work:** *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*

- [x] **Order chosen and recorded, by dependency direction rather than preference:** **(1) M2 existing-content replacement**, because it *deletes* defs and anything built against content about to be removed gets built twice; **(2) facilities**, because generation must be finished before the scenarios that consume it; **(3) new-game playability** — the world tile and the three starting sites — which consumes the final content set *and* the finished generator; **(4) the player-facing how-to**, because documentation describes a finished thing and writing it earlier means rewriting it. Content set → generator → scenarios → docs, one direction, no backtracking.
"""

anchor = '- [ ] **Facilities** — larger functional spaces, as distinct from rooms and corridors.'
assert anchor in s
s = s.replace(anchor, block + '\n' + anchor, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO.md updated')
