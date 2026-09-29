# Main-menu slideshow art brief

**Living document.** This is the hand-off spec for whoever produces the main-menu images —
another tool, another person, or the owner. Every number in it was read out of
`src/RimroomsAsyncIndustries/Presentation/RimroomsMenuBackground.cs`, not estimated.

**Original main-menu images are the single declared exception to this project's no-new-art rule**
(invariant 10). Nothing else in this mod may add art. That exception exists specifically so the
menu can look like the game.

---

## The one thing that makes this drop-in

**Any PNG named `RR_Menu_*.png` in the folder below becomes a slide. No code change, ever.**

```
Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu/
```

The code scans that folder with `ContentFinder<Texture2D>.GetAllInFolder`. The `RR_Menu_` prefix
is **required, not cosmetic**: `UI/Menu` is a generic content path and `ContentFinder` resolves
across every loaded mod, so without the prefix another mod's menu art would appear in this
slideshow. In a 294-mod install that is a certainty rather than a risk.

### The one manual step

`tools/check-package-integrity.py` refuses to let a file ship that is not on the package
allowlist, so each new PNG needs one line added to `tools/package-files.json`:

```json
"1.6/Textures/UI/Menu/RR_Menu_YourSceneName.png",
```

**Do not add a line before the file exists** — a listed file that is missing breaks the staging
script, which the checker also catches. Add the file, add the line, run the checker.

---

## Hard specs

| | |
|---|---|
| **Format** | PNG. Alpha is permitted but unnecessary; these are full-bleed backgrounds |
| **Size** | **1920 × 1080**. The two existing slides are 1672 × 941, which is the same 16:9 |
| **Aspect** | 16:9. `BackgroundRect` reads each image's **own** aspect and scales to fit, so a different aspect will not break — but it will letterbox or crop differently from its neighbours, and the crossfade between two aspects looks like a mistake |
| **Naming** | `RR_Menu_<SceneName>.png`. For a deliberate running order use `RR_Menu_NN_<SceneName>.png` — slides are sorted **ordinally by filename** so the order is identical on every machine |
| **Count** | Any. Two ship today. A slide dwells **30 s** and crossfades over **2 s** |

### Keep these regions clear of critical detail

Read from the code, in screen pixels:

| Region | Rect | What is drawn there |
|---|---|---|
| **Top-left band** | `x 350 → ~770`, `y 10 → 74` | the mod's version label |
| **Bottom-left corner** | `x 8 → ~8 + 32 + 64n + 16(n-1)`, bottom 104 px | RimWorld's own DLC/expansion icon strip |
| **Centre-left** | roughly the left third, vertically centred | RimWorld's own main-menu buttons |

Nothing is forbidden in those areas — just do not put the subject of the image there.

### Style rules

- **Painterly, not photographic.** RimWorld's own menu art is illustrated: soft brushwork, strong
  silhouettes, muted desaturated palette, one clear light source.
- **No text, no logos, no watermarks, no UI.** The version label is the only text on screen.
- **No visible faces in close-up.** RimWorld's art keeps figures small and read-by-silhouette.
- **Wide, cinematic, one readable subject.** These are seen behind a menu, at a glance.
- **Never redistribute vanilla or DLC art.** This is original work, which is why the exception
  exists at all.

---

## The palette this mod actually ships

Do not invent a look. `Generation/BackroomsPalette.cs` already defines what the Backrooms looks
like here, and the art should match the game:

- **Depth 1 is sacred** (invariant 25): the yellow rooms. Fixed, sparse, never deranged. Damp
  mono-yellow wallpaper, worn carpet, buzzing fluorescent ceiling, no windows, no outside.
- **Deeper coordinates grow wrong** through palette bands and **coherence decay** — not through
  gore. Furniture in a corridor is *content*, not a mistake (owner direction, 0.8.7-dev).
- **A gate is an ordinary door, tinted blue.** Not a portal ring, not a swirling vortex. A door
  you could walk past, that is faintly the wrong colour.
- **The company is 1990s industrial.** CRT monitors, beige plastic, paper, fluorescent strip
  lighting, cable runs, clipboards. No holograms and no glowing interfaces.

---

## Scene list

Twelve, covering the owner's request: *"content scenrio art like and ecounter and like lab
opertions or gate industrial usage and scary creepy backrrom univers sill art … in dramatic and
tragic and creepy moments of differnt scense and possible run ins"*.

**Every scene below depicts something the mod actually ships.** None of it is invented lore, which
is the point — the menu should show the game.

| # | Filename | Scene |
|---|---|---|
| 1 | `RR_Menu_01_Threshold.png` | A designated door standing open in a plain company corridor. Blue tint on the frame. Beyond it: damp yellow wallpaper and worn carpet that belong to no building. Nobody in shot. **The quietest image in the set, and it should be the most wrong.** |
| 2 | `RR_Menu_02_GateAssembly.png` | Lab operations. Two staff working on a door: one at a beige console with a CRT, one kneeling at a bound battery, cable runs taped across the floor. Clipboards. Ordinary industrial work, done to a door. |
| 3 | `RR_Menu_03_SpinUp.png` | **Dramatic.** The moment a gate comes up. Light bleeding around every edge of a closed door frame, hard shadows thrown back down the corridor, two silhouettes stepping away from it rather than toward it. |
| 4 | `RR_Menu_04_FieldSurvey.png` | A three-person crew in a yellow room, one writing in a book, one holding a glow pod, one watching the corridor they came from. Torchlight against fluorescent. *(A slide of this name already ships — treat this as its replacement or keep both.)* |
| 5 | `RR_Menu_05_RouteMarked.png` | A junction of identical yellow corridors with glow pods set down at the mouth of one of them. Coloured light on the carpet. **The colour is the meaning** — this is the image that teaches what markers are for. |
| 6 | `RR_Menu_06_Coherence.png` | **Creepy.** A deep coordinate where the space has stopped agreeing with itself: a door in a ceiling, a corridor that returns to the room it left, a production bench standing in a hallway with the wallpaper continuing straight through where a wall should be. No creature. |
| 7 | `RR_Menu_07_AtTheThreshold.png` | **A possible run-in.** Something holding ground just inside the dark on the far side of an open gate, read entirely by silhouette and eye-shine. It is not coming through. It is waiting to see whether you do. |
| 8 | `RR_Menu_08_DidNotComeBack.png` | **Tragic.** An empty threshold room on the company side. A dropped glow pod still lit, a book face-down on the carpet, one boot print in dust that is not from this building. The door is closed. |
| 9 | `RR_Menu_09_CleanUpTeam.png` | **Tragic and corporate.** Drop pods open in a wrecked facility courtyard at dawn. Uniformed relief staff unloading crates with complete indifference, walking past damage nobody has cleared. Nobody asked for them and no invoice came. |
| 10 | `RR_Menu_10_StoreBasement.png` | The Furniture & Knickknack Store start. A closed shop floor at night — sofas under dust sheets, price tags, a till — and a stockroom door at the back standing slightly open onto yellow light. |
| 11 | `RR_Menu_11_AlreadyInside.png` | The solo/group start. One to five ordinary people in street clothes in a yellow corridor, no equipment, no company, looking at a single unremarkable door. **They have no idea what they are looking at.** |
| 12 | `RR_Menu_12_TownOpening.png` | Arc 6. An ordinary residential street at night, and between two houses a door frame standing free of any wall, with yellow light coming out of it. Neighbours at a distance, watching, not approaching. |

Priority if the set has to be cut: **1, 3, 6, 7, 9** — those five carry the threshold, the
drama, the wrongness, the encounter and the corporation, which is the whole mod in five images.

---

## Checking the result

```sh
python tools/check-package-integrity.py     # allowlist, and it reports the folder's slide count
python tools/check-display-style.py         # no string surface regressed
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
```

`check-package-integrity.py` prints a note naming the scanned folder and how many textures it
covers, so the count is verifiable without launching anything.

**Nobody has seen any of this in motion.** No game has ever been launched from this repository, so
dwell timing, crossfade and legibility behind the menu buttons are all **unverified by play** and
only the owner can confirm them.
