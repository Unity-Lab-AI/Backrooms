# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | the test phase, and the owner's play brief at the top of it |
| **`docs/PLAYBOOK.md`** | **every play order the owner has given, verbatim, as one checklist. Read before playing** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## ⛔ READ `docs/PLAYBOOK.md` BEFORE TOUCHING THE GAME ⛔

**Owner, 2026-10-07, verbatim:** *"u need to make meals sooner than later and get your shellves organized so like i already told you. so wtf are you not making a guide of everything ive told you becasue im not fucking around you are gonna die if u dont take care of them"*

The guide exists now. **Walk section 1, keeping them alive, every in-game day.** Play in short bursts and read alerts between them.

---

## What this session did

**Shipped, built, staged: the gate's draw is a load on the grid.** The owner watched one battery go flat beside a full one on the same conduit. Two defects, both measured: the draw was a **second line beside the grid**, 3500 W out of storage while generators had 1375 W spare, and the drawing method **emptied batteries one at a time** while claiming to copy Core. An autodoor gate now rides its door's own power comp: generators first, then every battery equally. One-time costs and manual doors split evenly. The closed gate's standby draw, which nothing had ever charged, rides the same load. **Not yet seen in a running game** — that is a `[T]` row at the top of `TEST.md`'s Pending.

**Played: the gate is open.** Eleven of eleven. The two-section stall was a bill at `0x` nobody had priority to work. The company paid **2,000,000 USD** for *Power the gate*.

**Played: food.** Cook bill at 50, butcher table built with *Butcher creature* on Forever, berries and ambrosia marked, fourteen animals marked to hunt, three charge rifles issued.

## The colony

**`rimbridge_save_20261007_before_battery_fix`** — the latest. Async Industries, Gee, Scar, Unity, 9th of Aprimay 5500. **The AI-01 connection is open** with Gee on station. Account **51,721,860 USD**. Research: **Devilstrand**.

**And it carries the open defect below**: an expedition record that blocks dispatch.

## ⛔ OPEN, IN THE ORDER TO TAKE THEM ⛔

1. **Load the save and watch the batteries** — the `[T]` row. Two batteries should fall together, and not at all while the generators have surplus.
2. **A refused dispatch leaves an expedition behind** (TODO). The first press refused with *"carrying an object in their hands"*, crossed nobody, and every press after says *"The gate already has an active expedition"*. The **$5,000,000 AI-01 survey** is waiting behind it. **Hand-carried hauls start again the instant a pawn is undrafted**, so drafting first and dispatching second is the play-side workaround once the defect is gone.
3. **Three plant anchors** no longer find their code since `bcf0701` (TODO). The checkers are **32 of 33**, and the 33 of 33 recorded before was not true.
4. **The DefInjected gate recipe text** still says 100 steel and one bill (TODO).
5. **The play brief**, per `PLAYBOOK.md`: shelves organised, a vault, the prison, guest beds, defences and embrasures, the *Galaxy* sculpture the ideoligion wants, chopping, quests.

## How to drive the game, learned the hard way this session

| | |
|---|---|
| **A bill row's unlabelled icons are plus, minus, DELETE** | `--nth-after "<count>" 3` is plus. #5 deleted the cook bill once |
| **Float menus** — repeat mode, research nodes | pixel clicks with `hands.py`. A plain click on a research node **replaces** the project |
| **`find-things.py Word,Word x0 z0 x1 z1`** | new: finds things by def over the map in one socket session. **It counts cells, not stacks** — "1 survival meal" was a stack of 106 |
| **`designate-cells.py <id> "x,z x,z"`** | new: one designator over a list of cells, then clears it. *Harvest* works per cell; *Harvest fully grown* does not |
| **`dispatch-crew.sh <names>`** | new: waits for empty hands, drafts, dispatches |
| **`open_context_menu` on a pawn's right-click** | says why a bill is not being worked — *"Missing 0.5x raw food"* was the whole food diagnosis |

## State, measured

| | |
|---|---|
| Branch | **`feature/bug-testing`** |
| Version | **0.13.0-dev**, 0 warnings, 0 errors, staged copy hash-checked |
| Checkers | **32 of 33** — the one is the three stale plant anchors, failing before this change |
| RimWorld | **closed by owner direction** to build and stage |

## Is it done?

**No.** The battery fix is built and unseen; the survey is blocked by a defect; the play brief is perhaps a fifth done.
