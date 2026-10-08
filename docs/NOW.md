# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | the test phase; **"Owner direction — global control"** is the live section |
| **`docs/PLAYBOOK.md`** | **every play order the owner has given, verbatim. §00 order of operations, §01 architecture, §4a global control. Read before playing** |
| **`docs/PLAYSCRIPT.md`** | **the running order of a run, Acts 1-7 -- start to empire** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## The standing order

**Owner, 2026-10-08, verbatim:** *"you are dsoing test items right you keep getting lost in the game play, set fucking goals foo"*

Prompt **"get the tests all completed"**. No timers (owner: *"telling you not to set timers means exactly that NOT itsa okay to set 1m ones!!!!"*). Never build, stage or edit game files while the game runs.

## ⛔ GOALS, IN ORDER — each one closes a TEST row ⛔

Base-building is done only where a goal needs it. When a goal closes, its TEST row gets the evidence and the next goal starts.

| # | Goal | Closes | Done when |
|---|------|--------|-----------|
| **G1** | **Store gate.** Finish the facility (x157-173, z169-176; gate door `(165,172)`, hall door `(161,169)`, both wooden), move the machining table into the control room, console + battery inside, bind, commission `(165,172)`, assemble, calibrate, console to gate control, remember an address, open a connection | TEST *"Furniture and Knickknack Store opening -- a gate built"* | a connection opens through the Store gate |
| **G2** | **Emergency abort in play** on that connection's load notice | TODO abort row (shipped in source, unproved in play) | the notice reads *"Connection aborted. Nothing was opened, sent or charged."* and nothing was charged |
| **G3** | **Repeat request needs a different address** — repeat a request on the Store gate | TODO repeat-address row | the used address is refused and a new one is required |
| **G4** | **Solo or group, inside** — new colony on that start, a gate built | TEST *"Solo or group, inside -- a gate built"* | a gate stands and operates there |
| **G5** | Store-colony rows that ride along: smokeleaf harvested and **sold** (cash crops), the cow pen closed out, shelves for every resource, trade with every trader | TEST cash crops / corral / shelves / trade rows | each with its evidence |
| **G1c** | **The gate complex** -- owner 2026-10-08: *"and your gate need to be not just a side room it needs to be in a massive facility with all it supposrt structures in a windowed off room for security ect ect and security   u can do the research as u need it"*. Grow the facility at x157-173 z169-176 into PLAYSCRIPT Act 5's layout: windowed control room, power room, assembly shop, receiving bay, archive, lab, quarantine, security room, crew quarters | the same Store gate TEST row | every room of the Act 5 table stands and is linked to the gate |
| **G1b** | **Corner towers** -- owner 2026-10-08: *"yopu need towers on all corrner that you can shhot out from with seperate ventalizatyion and added rooms for security stuff and embrassure sally ports"*. Four towers at the perimeter corners with embrasures, own vents, security rooms, embrasure sally ports (PLAYBOOK §01 goal 9). Blueprinted right after G1 so the crew builds them while the gate ramps | TEST *"expand the base ... defences"* row | four towers stand, each vented on its own, sally ports in |
| **G7** | **Guest wing** -- owner 2026-10-08: *"you need to set bed prices and make facilities for guests and use locks so they dont wonder into your vaults only wher u sell stuff and buetify thir rooms and not barracks style rooms"*. Single beautified guest rooms with bed prices, guest facilities, locks keeping guests to the shop | TEST visitors / hospitality rows | guests pay for beds and reach only the shop |
| **G6** | **Save, reload, revisit** a coordinate on the Store colony | TEST *"Save, reload, revisit the same coordinate"* | map state and rewards persist without duplication |

Everything else open in TEST is launch-gated on the owner (RimSort profiles, DLC matrices, RWT server, art review) and is not mine to close by playing.

## Pending on the map, 2026-10-08 (do not drop)

- **Walls after terraform:** `(182,164)`-`(182,170)` (marsh and rain-flooded *MarshFlood*) and `(167,135)`, `(168,135)` are soil blueprints; **steel walls go on all nine the moment the soil lands.** Check with `.local/qa/wall-map.py 118 132 184 198`.
- **Gate complex** blueprinted in steel, x140-174 z176-196 (PLAYSCRIPT Act 5 layout): security door gate at `(169,184)`, reinforced glass wall along z184, 3-wide spine x161-163, main hall z186-188. **Entry wall `(162,176)` designated for deconstruction -- a steel door goes in its place.** Old closet door `(165,172)` decommissioned.
- **Gate needs one live grid** for console, battery and door: conduit to `(169,184)`.
- **Freezer** zone takes foods, plant matter, animal corpses, herbal medicine; nine warehouse shelves refuse them and all medicine.
- **Vault** for silver x178 and the age-reversing serum -- not built yet.
- **Silver ore** on the map, 36 cells at `(44-46,202-204)`, `(80-83,269-271)`, `(257-260,175-178)`, `(263-264,274-275)` -- **all fogged**: walk a pawn there first, then designate mining (never mine into fog). Procurement silver is $1,000 each, so this is the silver supply.
- **Penoxycline x7** bought from IE Solutions for 161 silver; drug policy every 5 days.
- **Research queue:** Drug production -> Penoxycline production (Smokepop packs dropped). Then Psychite refining, Prisoner containment, Vault Wall And Door, the computing line.
- **Multi-analyzer** blueprinted at `(136,156)` beside the hi-tech bench; needs 50 plasteel -- 5 unfogged plasteel ore cells at `(179-181,192-194)` designated for mining.
- **Alfred** (Hospitality quest, bedridden 19 days) for gold x260 + reinforced barrels x2. **Derek** (torturer, crashed) rescued to a sleeping spot `(152,158)` -- recruit him.
- **Gate chamber swap:** z184 glass is now plain **glass wall** (4 glass each, 32 total) and the gate door is an **autodoor** at `(169,184)` (wooden -- Replace to steel later). **Electric smelter** blueprinted at `(145,139)`: add *make glass from chunks* x6.
- **Drug lab** built at `(137-139,145)`: *smokeleaf joint x4* Forever. Penoxycline needs neutroamine -- buy from a trader.
- **THE GATE (2026-10-08):** a steel door **centred in the gate room at `(169,190)`, commissioned** (owner: the gate stands in the centre, not the doorway). `(169,184)` is a plain autodoor, control room <-> chamber. Glass wall z184 built (smelter glass). Machining table on gate control, *Assemble gate x4* active (one assembly). Hidden conduit laid `(158,163)-(158,183)`, `(159-168,183)`, `(168,184-190)` to put the gate on the console/battery grid. Next: operator, calibrate, console to gate control, remember AI-01, open, **Emergency abort**.
- **Barracks machining table `(149-151,157)` is unusable to every pawn** -- powered, bill not suspended, *Anyone*, unlimited radius, recipe listed in Add bill, yet a drafted-free right-click offers only *Clean barracks*, even for a plain *Print company bond* bill. Cause not found yet (reservation or interaction cell suspected). Workaround in progress: a new machining table in the complex assembly shop `(154,182)` to bind as the gate's assembly bench. If the new one works, inspect the old one before writing a TODO.
- Unity is **Pujari of Indra** (role change ritual at the ritual spot `(148,141)`); chess chairs blueprinted.

## State, measured 2026-10-08

| | |
|---|---|
| Colony | **Store**, save **`rimbridge_save_20261008_store_walls`**, tick ~1,266,700 |
| Facility | walls framing; doors `(161,169)` and `(165,172)` wooden frames; north hall wall still blueprints x170-174 |
| Research | Machining, then Multi-analyzer |
| Branch | **`feature/bug-testing`**, last commit e39cb9b |
| Checkers | **32 of 33** — the stale plant anchors, failing before this session |
| Forgejo | **held.** GitHub only |

## Tools, `.local/qa/`

`play_for` takes **`{"durationMs":N,"speed":"Superfast"}`** — `ticks` is rejected and the game does not move. `keys.py --esc` drops a live designator. `terrain-map.py x0 z0 x1 z1` maps walls/doors/frames (`o` there is a frame or plant, not a hole). Right-click an Architect material button for its material menu (no limestone door is offered — wood).
