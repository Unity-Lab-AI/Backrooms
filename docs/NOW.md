# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | **the test phase, and the owner's play brief lives at the top of it** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## ⛔ READ `docs/TEST.md` FIRST — THE OWNER'S PLAY BRIEF IS AT THE TOP OF IT ⛔

Six verbatim directions from 2026-10-07 are recorded there in full. **The standing order is to PLAY the colony, not to tinker with tooling.** The owner's own words on how the last hour went:

> *"so wtf? how many fucking test items have you completed? youve been playing for an hour and did nothing in the game but plant rice and neever finished completing the gate steps and never expanded what i told you to do ... its like 90% of everything ive told you you just fucking ignore!"*

**That judgement is correct and the cause was method.** The hour went on fighting the UI: float menus that draw at the mouse, a zone designator that stayed live so forty clicks painted three stray stockpiles that then had to be deleted, and a faction-naming dialog that silently froze the game for two in-game days.

**⛔ DRIVE THE GAME THROUGH THE BRIDGE'S SEMANTIC CLICKS. Pixels are the last resort.** `.local/qa/click-label.py` (`--list`, `--after`, `--nth-after N`, `--labelled-after`) hits real UI elements and cannot drift. `hands.py` pixel clicks are only for surfaces the bridge cannot enumerate — the main menu, the landing-tile page, float menus.

**And before ANY pixel click: `click_cell x z button=right`, then confirm `get_designator_state` reports `selectedDesignatorId: null`.** `press_cancel` does **not** clear a live designator. That one omission made the mess above.

---

## THE COLONY, LIVE AND SAVED

**`rimbridge_save_20261007_122501.rws`** — Async Industries on a 300×300 **Temperate forest / Mountainous** tile, Spring, rolled the owner's way with `.local/qa/pick-site.py` reading the Terrain pane. Three staff: Gee, Scar, Unity, from Preset3 through Prepare Carefully with the Godsmultiplayer ideoligion.

| Done | State |
|---|---|
| Gate | **6 of 11.** Console, battery and bench bound; table and console in gate control; **2 of 4 sections installed**; Gee assigned operator |
| Freezer (`Stockpile zone 2`) | Foods + Medicine + Wort + **Corpses**; `*Allow rotten` **off**, `*Allow fresh` on |
| Trash | `Dumping stockpile zone 1`, 64 cells, west of the compound |
| Resources | **140 mine cells on unfogged rock only**, 89 chop designations |
| Food | 189-cell rice field, blight cut, cook bill running |
| Pawns | All three **Attack**, schedules all **Anything** |
| Research | Prisoner containment done, more queued |

## ⛔ WHAT THE OWNER ASKED FOR AND DID NOT GET ⛔

**Not started:** prison · guest beds (alert standing, five visitors) · defences and embrasures (alert standing) · hunting · a vault for silver, gold, gems and ivory · shelves organised · meds to the hospital · cook bill maintained at **50** rather than 10 · expanding the base · quests and missions · prisoners working under layered security.

**And the gate is stalled at 2 of 4 sections.** The *assemble gate section* bill counts down to `0x` without consuming the 100 steel and 8 components, and step 5 stays red. **Not yet attributed — do not guess.** The gate's own card is the thing to read: it says *"Assembly: 2 of 4 sections installed"* and names its next step in plain words. `.local/qa/inspect.py` prints that card.

---

## What this session actually bought: the board could not see a gate the player had built

**Fixed and verified, `57959dd`.** `MainTabWindow_Operations.CurrentGate` read only `selectedGate`, a field assigned nowhere but the pane's own *Select a door* menu. Designate the door from **the door's own button** — the one-click path this mod advertises — and the window never learned the gate existed.

**The board read `0 of 11 complete` on a gate that was commissioned and already paying out its start-up goals**, and the objective line told the player to assemble a gate they had built. It reset to zero every time Operations was reopened.

**This is the owner's old report** — *"ive done like 50 things in a row and its still not opening"* — wearing a different hat.

**Proved, not reasoned:** pressing *Select a door* moved the board **0 → 2** on an unchanged gate. After the fix, a fresh load reads **2 of 11 with nothing selected**, and the chain then ran to 6 in play. The fallback asks the branch for its designated gate through the same door enumeration the menu offers, so the two cannot disagree; an explicit selection still wins.

---

## Tools built this session, all in `.local/qa/`

| Tool | What it is for |
|---|---|
| `click-label.py` | **The main way to drive the game.** Semantic clicks on enumerable UI |
| `inspect.py` | Prints the selection's inspect card — the game saying what it thinks |
| `designators.py` | Architect designator ids by category and keyword |
| `pick-site.py` | Rolls *Select random site* until the Terrain pane reads mountains in forest or jungle |
| `eyes.py` | Bridge capture (`--os` for a desktop grab when the game's thread is busy) |
| `hands.py` | Pixel click, drag, hover, unicode typing. **Refuses unless the game holds the foreground** |

**⛔ In any Core file list the unlabelled button beside a row's name is DELETE.** It came one click from the owner's `Godsmultiplayer.rid`. Use `--labelled-after "<name>" "Load"`.

---

## State, measured

| | |
|---|---|
| Branch | **`feature/bug-testing`**, `57959dd` on five GitHub refs, tree clean |
| Version | **0.13.0-dev**, 0 warnings, 0 errors, staged copy matches |
| Checkers | **33 of 33** |
| Forgejo | **held.** GitHub only |
| Client | Updating from 2.1.270 to reach `claude-opus-5-5`, which needs 2.1.280+ |

## Is it done?

**No.** The generator reads right and the gate chain runs, but the owner's play brief is roughly a tenth done. **Next session opens `TEST.md`, takes the list in order, and uses semantic clicks.**
