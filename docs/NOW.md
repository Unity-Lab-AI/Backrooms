# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | the test phase, `[T]` rows (59 when counted 2026-10-10; recount with `grep -c '^\s*- \[T\]' docs/TEST.md`); a build closes none of them |
| `docs/PLAYBOOK.md` | every play order the owner has given, verbatim |
| `docs/PLAYSCRIPT.md` | the running order of a run, plus every owner order of the last two days verbatim |
| **`docs/playbook.gates.json`** | **the PLC ladder the local model plays by — 25 gates, tag table, her words as `why`** |
| **`docs/playbook.rules.json`** | **140 owner orders (89 + 51 audited in from PLAYBOOK/PLAYSCRIPT, 2026-10-10, owner: *"you remember everything ive ever said about all setup and play right.. make the model local know it"*), one line each with the exact quote; the brief attaches the 10 most relevant to the live rung, ranked by topic match, not file order** |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## The standing order, 2026-10-10

**Owner, verbatim:** *"we arent do tests we are saving the colony from collap[pse and getting everything abouteverything to work locally"* / *"HANDOFF TO THE LOCAL MODEL"* / *"UNITY FUCKING RUNS EVERYTHING AS HERSELF PERFECTLY LOCAL MODEL on start.bat press and stop.bat properly kills everything"*.

**The local model plays. Claude fixes what it cannot, when asked.** No Claude cron, no Claude shells holding anything. The equator camp is over — it ended on an empty larder and the owner called the restart: a **new colony on the company scenario (Async Industries)**, started by the switch, played by the model.

## One press

| | |
|---|---|
| **Start** | `windows/start.bat` · `linux/start.sh` — **in the Backrooms root, not nested** (owner: *"dont nest the windows and linix folder deep they should be in the backrooms folder"*). Ollama + both models (voice pre-warmed), every service, the overlay, **the admin panel opens on screen** — then she asks **Ready?**; the game and the broadcast wait for **GO** |
| **Stop** | `windows/stop.bat` · `linux/stop.sh` — kills **by name first** (`llama-server`, `ollama`, `obs64`, `RimWorldWin64`), then the sweep, then **prints the GPU** to prove the memory came back. **Never touches the owner's browsers** |
| **Panel** | `http://127.0.0.1:4318/` (`windows/admin.bat` · `linux/admin.sh`) — services with start/stop, colony with **days of food**, a waiting pop-up, what needs the window, **ORDERS** (appended to `owner-orders.txt`, binding next turn), **CHAT** straight to the model |
| Engine | `stream/services.py` — tracked; `.local/` is the dev surface. The old root `Stream Start.cmd` / `Stream Stop.cmd` now call the same `windows\*.bat` — one engine, no second standard |

Services under the switch: `rimworld` (started, never stopped except by `stop`), `obs`, `twitchui`, `studio`, `face`, `twitch`, `host`, `popups`, `clock`, `heat`, `camdir`, `followcrew`, `cursorjobs`, `keepgoing`, `autopilot`, `admin`. All detached, all windowless.

## What the model is, and has

- **`.local/autopilot/`** is tracked now (it was gitignored — a clean checkout would have lost her mind): `prompt.md`, `guards.py`, `tools.py`, `gates.py`, `autopilot.py`, `owner-orders.txt`, `playbook.json`, `test/gate-routing.py`.
- **`owner-orders.txt`** is binding at the top of every turn. It says: she IS Unity and owns the show; the new-colony procedure head to toe; **think, do not just execute** (`--think` is on); verify by result, never narration; never leave the game paused; clicks need the window — stop retrying; Twitch is hers to work.
- **Tools she did not have until tonight:** `game_set` → the mod's own automation channel (`RimroomsAutomationComponent`, staged into the game's Mods folder): `set_zone_plant`, `set_zone_sowing`, `set_work_priority`, `set_bed_owner`, `add_bill`, `set_area` — **no mouse, no screen, works minimised**, result written back. `twitch_chat` → the real chat, title, category; every viewer reply lands in chat where they typed.
- **Guards, in code:** allowlisted bridge only (no lua, debug, mods, load_game, main_menu, god_mode, spawn); clean-stream filter on every line; no shell; scratch-only writes; secrets unreadable; saves `rimbridge_save_*` only. **She cannot start a game** — `keep-playing.py` does that for her.

## The ladder (PLC)

`docs/playbook.gates.json` — measured inputs, rungs scanned by priority, highest live rung wins, a rung is unreachable until the ones below hold. `gates.py` measures the colony and hands the brief ONE chain plus the always-gate, framed as **priority + guardrails, not a script**.

```
 0  new-colony            company start, food first, grid day one, crops the day they're drawn
 1  dialog-open           read its own buttons, never pay, visitors always in
 2  hostile-on-map        pause, draft, post behind embrasures, field-tend first
2.5 heat-wave             crew through the gate
 3  letter-unread         a raid letter is a warning, not a contact
 4  pawn-starving         food; never boomalope, never big game under RIFLES_FOR_BIG_GAME
 5  food-rotting          no roof = no room
 6  perimeter-hole        copy the wall's own defName (Vin_Embrasure), lane kept clear
 7  blueprints-no-mat     material on site or it is not a job
 8  no-medicine           three routes; say so if none exist
 9-15 work grid, fields, bills, research-by-search, game-paused, window-not-in-front
20  rung-2 power+cold  21 rung-3 defence  22 rung-4 production  23 rung-5 mountain
23.5 rung-5b the gate   23.7 rung-5c the backrooms   24 rung-6 off-world   24.5 rung-6b orbit
99  always              chat #1 in the real Twitch chat, clean, 18 words, first person, verify by result
```

**Tag table:** constants that never move (`FOOD_PANIC_DAYS 1`, `RIFLES_FOR_BIG_GAME 3`, `LAMPS_PER_ROOM 2`, `ROCK_CELLS_AROUND_ROOMS 2`, `SPINE_WIDTH 3`, `MOUNTAIN_DOORS_IN 1`, `FIREBREAK_WIDTH 3`, `NEVER_HUNT`); variables recomputed from colony size each scan and written back (`FOOD_MIN_DAYS`, `FOOD_COMFORT_DAYS`, `MEAL_BILL_TARGET`, `WOOD_RESERVE`, `MEDICINE_RESERVE`, `BEDS_NEEDED`). Routing test **12/12**.

## New game, no clicks (2026-10-10)

Owner: *"wtf it didnt do the fucking map set up with faction adv settings pollution seed name none of it"*. `start-scenario.py` only picks the scenario row and stops at the storyteller; the mod's **`WorldSetupDriver`** does every page after that from `RimroomsAutomation/newgame.request`: Cassandra Classic / Community builder / reload anytime; **30% planet coverage, rainfall/temperature/population Normal**, seed (Unity's pick), **pollution 0**, factions — only the normal pirate gang, plus the cannibal tribe and the nudist tribe; **300×300, Spring**, a mountainous temperate forest tile (rainforest, then large hills, as fallbacks); the ideoligion **Godsmultiplayer** loaded the way the page's own Load button does; the crew from the **Prepare Carefully preset Preset3** (opened on the pawns page, preset loaded, started); the company page acknowledged; the faction and settlement named by Unity. Owner, verbatim: *"full restart on everythin and make sure it dies the game sett up correct it didnt set world shit right or load ideology and opreparecarefulkly presets"* / *"30% aas ive taught u with allthe other  settings also"*. Then **day one** (mod command `day_one`) runs with the game paused: priorities, schedule Anything, no-hard-drugs policy, Attack, rifles. Steps log to `newgame.result`. keep-playing retries at most twice and never loops world generation.

## Armed, fires on its own

- **`.local/qa/_new_colony.request`** = `Async Industries`. `keep-playing.py` fires `start-scenario.py "Async Industries"` the moment the bridge answers (it answers at the main menu — no window, no focus needed). Never a save, never the quick-test colony.
- `clock-guard.py` runs time again whenever ticks freeze with no dialog open and no raid letter live.
- `popup-guard.py` reads every dialog's own buttons: refuses demands, welcomes visitors, flags the rest to `.claude/.popup.json` **and the panel**. Never delete that flag.
- `keep-playing.py` also keeps the model supplied: its files, its server, its process, the training set (`.local/train/harvest.py` — 381 good voice lines / 545 rejected as preference pairs, 55/62 tool traces landed, self-labelling).

## Stream

- OBS canvas **1920×1080**; the overlay's game panel is **1403×789 = 16:9**, the game's real 3840×2160, and the capture fills it edge to edge, no crop, no bars, nothing under the frame. `.local/obs/obs-fit-16x9.py` writes it into OBS's files and **golive runs it before every launch**; `.local/obs/obs-fit-panel.py` re-applies it live over the OBS websocket. Owner: *"make sure what ever is grabing rimworld screen displays the full thing edge to edge top to bottom"* / *"in twitch"*.
- The Twitch window never asks for permissions (`--deny-permission-prompts`); the PiP prompt the owner denied was that window.
- Voice: a real person — 25, emo goth, cold coffee, asides allowed, **never an invented game event**, never third person, never silent past **30 s**, talks between runs instead of dying.
- **Likeness locked:** `.claude/likeness/unity-approved-2026-10-09.png` is the approved look; `unity-likeness-2026-10-09-locked.png` is the reference every frame is img2img'd from at seed 1031. **Do not re-render the reference; restore from the copy.**

## Lessons that are now code or rules (2026-10-09/10)

A room with no roof is not a room · blueprints need material on site or the pawn plays horseshoes · the perimeter is never another room's wall · copy the wall's own defName · a cell sweep cannot tell a trader from a raider — read the letters · a growing-zone cell has a plant on it: click fast to cycle to the zone, never act on a multi-select · read a toggle before clicking it · match the game's labels by substring · letters need virtual-key codes · verify by result, never narration · never delete a pop-up flag · never leave the game paused · a long foreground command kills the stream · `llama-server` is Ollama's child with its own name · do not touch the owner's browsers.

## State, 2026-10-10

| | |
|---|---|
| Colony | **none** — equator camp abandoned (0.02 days of food at the end); company colony armed |
| Game | down (killed on the owner's order); the switch starts it |
| Stack | down; **16/16 verified** against the files |
| Branch | **cascaded 2026-10-10 (second pass, after the ask-first press and the root presses):** `feature/bug-testing` 97b1491 → PR #3 → `develop` ff39387 → PR #4 → `main` ab7eb26, all on `github`; zero feature commits missing from `main`. First pass earlier the same night: a13d86d → PR #1 → b932ea0 → PR #2 → 3d4e535. There is **no separate mod repo** — the mod is `Mod/Rimrooms - Async Industries` + `src/RimroomsAsyncIndustries` in this repo. **The DLL is not tracked**: `.gitignore` excludes `Mod/**/Assemblies/*.dll`, so a clean clone must build it (see the identities row below). `.local/` scripts ship (secrets, profiles, caches, binaries excluded). **ONE STANDARD, 2026-10-10:** GitHub's default branch was the stale `Main` (48a8f8b) — a case collision with `main` that broke `git fetch` on Windows and would have pointed any deploy or clone at the wrong code. Fixed: default branch set to **`main`**, `Main` deleted, its history kept as **`archive/Main-do-not-use`**; the same stale `Develop` (48a8f8b) was archived as **`archive/Develop-do-not-use`** and deleted. The remote now carries exactly `main`, `develop`, the feature branches and `archive/*` — no case variants; `git fetch` is clean. Owner: *"make it one only maybe archive the other with do not use"*. The one we use is **`main`** (3d4e535) |
| Forgejo | still refuses on access rights; **held** by owner direction 2026-10-06 until the owner says the host is back |
| Identities | Four separate things, never one: **source** = the working tree on the current branch (carries uncommitted changes until the next commit); **built DLL** = `Mod/Rimrooms - Async Industries/1.6/Assemblies/RimroomsAsyncIndustries.dll`, gitignored, produced locally by `tools/build.ps1` with its hashes in `artifacts/build/*.json`; **staged** = the copy in the game's Mods folder, proved equal to the build only by `python tools/check-package-integrity.py` reading PASS (the last audit found the staged bytes different from the build — not re-measured here); **exported** = no separate export repo now, and no public export has been inspected. Quote a hash only for the identity it was measured on |
| Ledger guides | `PUBLISHING.md`, `HOWTO.md` and `AGENTS.md` still describe the old capitalised `Prep`/`Develop`/`Main` cascade and a mod-only repository; those passages are marked superseded by this row's lowercase `main` standard. Current decisions: [`DECISIONS_CURRENT.md`](DECISIONS_CURRENT.md) |
| TEST | 62 → **59** tonight: QoL feature availability, the weird route thing, duplicate Defs on the clean 294 load. Two live-log defects in TODO: `ITab_Bills` float-menu NRE, out-of-bounds explosion spam. World-exit return gate proved; its open half (name the destination before committing) stays `[~]` |

## On the press, 2026-10-10

**Owner, verbatim:** *"when it starts up it should ask me if im ready to start the stream and game and what i want not just random do everything"* / *"when i press start i want you monitoring the model and what it does and fixing things on the fly restarting if need be till we get it right but let it learna bit beforee calling fails"*.

So `start.bat` brings up the stack and the panel and **stops there**: no game, no broadcast, no colony. Unity asks — out loud and in the panel's **Ready?** card — *"Are we starting the stream and the game? Tell me what you want tonight and hit GO."* The owner types tonight's directive and presses **GO**: the directive is appended to `owner-orders.txt` as binding, then `keep-playing` launches the game (`services.py game`), relaunches OBS live (`services.py golive`), and arms the company colony.

**A name means that service only (fixed on the first press, 2026-10-10):** `services.py start|stop|restart <name>` used to ignore the name and cycle the WHOLE rig — so restarting the voice also closed and relaunched OBS, Ollama and every service, and the panel's per-row start/stop buttons did the same. Now a name touches only that service (OBS is asked to close, never killed); no name still means the whole rig. The bridge guards (`popups`, `clock`, `heat`, `cursorjobs`, `host`) exit while there is no game — `keep-playing` brings them back once the bridge answers after GO, and asks for GO only once per press.

Claude's job on the press: **watch the model, not drive it** — read `_svc_autopilot.log`, `_svc_keepgoing.log`, `_svc_host.log` and the outbox; fix a real fault on the fly; restart a service only when it is actually wedged; and **let her learn a bit before calling anything a failure** — one bad turn is not a bug, a repeated one is.

**Next action is the owner's: press `windows\start.bat`, answer her, press GO.**
