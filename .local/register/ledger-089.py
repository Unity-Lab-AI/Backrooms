import io

# --- CHANGELOG -------------------------------------------------------------
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.8.9-dev - 2026-09-29 - bringing a gate up is work, and a gate looks like one

- **Opening a connection is no longer a button.** The assigned operator brings the gate up at the console over time, and the console shows the progress while they do it.
- **The operator matters.** A skilled technician brings a gate up quickly; a poor one takes a long while. It is their own working speed that decides it.
- **Leave it unattended and it loses charge.** The gate only climbs while somebody is on the console with the power on and the cutoff off. Left alone it slips back and eventually lapses, and the address stays remembered so you can start again.
- **Losing charge is always slower than gaining it**, whoever is operating, so walking away costs you time but never wipes out a long spin-up.
- **A route you have run before comes up faster.** Every previous connection to the same address shortens the next one, down to a floor. Somewhere nobody has been takes the full spin-up, and no route is ever instant.
- **Dial straight from a gate's history** to connect to somewhere it has been and start bringing it up, in one action.
- If the spin-up finishes while the battery is still too low, the gate **waits fully charged and opens itself** the moment there is enough power.
- **A gate you have designated is a blue door with a blue glow around it**, so you can tell one from an ordinary door at a glance. It glows brighter while a connection is live, and amber when something has gone wrong. If you painted that door yourself, your colour is kept.
- A natural portal still has no history, cannot be dialled, and looks like the ordinary doorway it is.

Full record: [bringing a gate up is work](docs/implementation/GATE_SPIN_UP_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.8.9-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG.md updated')

# --- FINALIZED -------------------------------------------------------------
p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.8.9-dev - 2026-09-29 - bringing a gate up is work, and a gate looks like one

### Owner directions, verbatim

> *"when u establish a backrooms portal connection the specific addresss should be connected and the gate opened but it neededs to be a ramp up process that takes a bit of time like with everything the pawns needs to do/maintaing/ operate to opening the gate process like a item build in a way"*

> *"yes the gates are just repurosed doors of the game with a bue tint and maybe a blue light glow hue around it like light through a glass wall does"*

> *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*

### Owner answers recorded this checkpoint, asked rather than assumed

> *"Dial = take me there"* - a dial establishes the address and opens the gate, as one intention.

> Gate sizes: **both** paths - binding across adjacent Core doors, and accepting Doors Expanded multi-cell doors when installed.

> Depth: **higher number means deeper**. The built reading is correct; nothing changes.

> Incursion: **depth plus technology, while an opening is live**. It must chase a pawn to the threshold, and closing the gate is the countermeasure.

### What shipped

Opening a laboratory connection is now work rather than a button, at the operator's own speed, shown on the console as a progress bar. Every entry point routes through the one ramp, so it cannot be skipped. The ramp climbs only while the gate is genuinely held and bleeds otherwise, lapsing at zero with the address kept. Required work falls with familiarity to a floor, turning the gate's address book into its learned routes. A finished ramp waits fully charged rather than being discarded when the battery is momentarily short. A designated gate is a blue door with a blue glow, built on a Core hook the gate component already had, leaving every other door untouched.

### A defect caught before it shipped

Decay was first a flat rate per tick, with a comment claiming it was slower than progress. It was not: at low Intellectual a technician would have lost charge faster than they could build it, making a slow operator's gate impossible rather than slow. The offline proof rejected it on that assertion, and decay is now a fraction of the observed climb rate - true for every operator by construction.

### Build evidence

0.8.9-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **155** C# source files (one new), **92** approved package files (no new file; three existing keyed files extended). Assembly SHA-256 `9E0FA752A9DB00EB801A013FAFBC937D3723CC33D359A54B57A11E42083D8354`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All four checkers pass; 1,214 keyed references all resolving. **No new def of any kind, no asset, no patch operation, no new job def, no new work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Source files modified: 6. Package files created: 0 (three extended). Docs updated: 5 (1 new).
Owner directions captured verbatim: 3. Owner questions asked at the fork rather than flagged for later: 4.
**Requirements met by an existing Core hook rather than by new content: 2** - the blue tint through `ThingComp.ForceColor()`, and the console progress bar through the job that already existed.
**Defects caught by offline proof before shipping: 1** - the flat decay rate.
Still open and named in `TODO.md`: multi-cell gates; pursuit and incursion; facilities; the unknown-def-field checker.
"""
assert '0.8.9-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED.md updated')
