# Shared menu and generation-notice art brief

**Living document.** This is the hand-off spec for whoever produces the main-menu images —
another tool, another person, or the owner. Current rendering details are read from
`Presentation/RimroomsSlideArt.cs`, `RimroomsMenuBackground.cs` and `RimroomsGenerationNotice.cs`
under `src/RimroomsAsyncIndustries/`; package dimensions are measured from the PNGs.

**Original main-menu images are the single declared exception to this project's no-new-art rule**
(invariant 10). Nothing else in this mod may add art. That exception exists specifically so the
menu can look like the game.

---

## The one thing that makes this drop-in

**Any PNG named `RR_Menu_*.png` in the folder below becomes a slide. No code change, ever.**

```
Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu/
```

`RimroomsSlideArt` scans that folder once with `ContentFinder<Texture2D>.GetAllInFolder` and owns
the shared ordering, cosmetic random selection and full-screen crop calculation. The menu and
pre-generation notice read that one list; adding art does not require another C# list. The `RR_Menu_` prefix
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
script, which the checker also catches. Add the file, add the line, run the checker. Also append
the asset's entry to `docs/research/provenance-register.csv` and retain its prompt, input-reference,
actual-dimension, edit and hash record outside the loadable package.

---

## Hard specs

| | |
|---|---|
| **Format** | PNG. Alpha is permitted but unnecessary; these are full-bleed backgrounds |
| **Size** | Aim for 1920 × 1080 composition; preserve and report the actual delivered resolution. Before the October 4 additions, five PNGs are 1672 × 941 and LaboratoryOperations is 1672 × 940. Do not describe an upscale as a native master. |
| **Aspect** | Approximately 16:9. `RimroomsSlideArt.FullScreenRect` reads each image's own aspect and fills the screen by cropping; it does not letterbox. Check subjects at other display aspects. |
| **Naming** | `RR_Menu_<SceneName>.png`. For a deliberate running order use `RR_Menu_NN_<SceneName>.png` — slides are sorted **ordinally by filename** so the order is identical on every machine |
| **Count** | Twelve local package slides after the October 4 addition: six preserved and six new. Use the package folder/allowlist for the current total. A slide dwells **30 s** and crossfades over **2 s**, starting at a cosmetic random index. |

### Keep these regions clear of critical detail

Read from the code, in screen pixels:

| Region | Rect | What is drawn there |
|---|---|---|
| **Top-left band** | `x 350 → ~770`, `y 10 → 74` | the mod's version label |
| **Bottom-left corner** | `x 8 → ~8 + 32 + 64n + 16(n-1)`, bottom 104 px | RimWorld's own DLC/expansion icon strip |
| **Centre-left** | roughly the left third, vertically centred | RimWorld's own main-menu buttons |
| **Centre** | centered 560 px-wide panel; height follows localized text | the mod's pre-generation notice and continue button |

Nothing is forbidden in those areas — just do not put the subject of the image there.

The shared art is already used by the main menu and the notice shown before Operations-origin
coordinate generation. Core owns the subsequent long-event wait box. Adding PNGs does not extend
coverage to the still-open tick/job-driven generation announcement paths.

### Style rules

- **Painterly, not photographic.** RimWorld's own menu art is illustrated: soft brushwork, strong
  silhouettes, muted desaturated palette, one clear light source.
- **Match the existing set's small, simply painted figures.** The owner rejected overly realistic
  characters and a later pilot too similar to FieldSurvey. New images need new compositions and
  **unsettling situations**, with distress, grief, fear or disorientation visible in body language.
  Strange architecture supports the situation; it is not the only subject.
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
- **Deeper coordinates grow wrong** through palette bands and **coherence decay**. Furniture in
  a corridor is *content*, not a mistake (owner direction, 0.8.7-dev). The October 4 direction also
  permits small blood splashes/trails and disturbing recoveries; preserve the painted style and
  situational unease without turning every image into a gore tableau.
- **A gate is an ordinary door, tinted blue.** Not a portal ring, not a swirling vortex. A door
  you could walk past, that is faintly the wrong colour.
- **The company is 1990s industrial.** CRT monitors, beige plastic, paper, fluorescent strip
  lighting, cable runs, clipboards. No holograms and no glowing interfaces.

---

## Existing inventory and October 4 direction

Preserve `RR_Menu_CorridorEncounter.png`, `RR_Menu_FacilityThreshold_v2.png`,
`RR_Menu_FieldSurvey_v2.png`, `RR_Menu_IndustrialGateLogistics.png`,
`RR_Menu_LaboratoryOperations.png` and `RR_Menu_SilentRecovery.png`.

The October 4 addition is **six** distinct scenes: PanicJunction, LightsOut, EmptyCinema,
FamiliarStranger, BreachedVault and RedTrail, all **1672 × 941 native PNGs**, copied unchanged.
They were generated from text with no input images. The initial realistic batch and the duplicative
reference-based pilot are rejected and unshipped. MirroredWard and BreakingPoint were initial
ideas withdrawn from this batch. [Task and evidence](implementation/evidence/menu-art-2026-10-04/TASK.md)
record package evidence and [exact prompts/hashes](../outputs/menu-art-2026-10-04-revised/prompts-and-provenance.json).
These additions are in the local copyable package; this task does not stage or publish them.

Ground the pictures in existing blackout, echo, survivor/dead-crew, pressure and room-generation
systems. Pawns' emotional reactions are artistic depictions of normal RimWorld consequences,
not promises of new scripted mental states or hallucination mechanics. Echoes remain neutral.

## Earlier scene pitches — historical concepts, not a shipped inventory

Twelve, covering the owner's request: *"content scenrio art like and ecounter and like lab
opertions or gate industrial usage and scary creepy backrrom univers sill art … in dramatic and
tragic and creepy moments of differnt scense and possible run ins"*.

These are preserved earlier pitches, not twelve installed slides or blanket feature verification.
Re-check any selected pitch against current source and the connected-portal rules before producing
it. The latest situation-focused direction above governs this batch.

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

The earlier pitch priority was **1, 3, 6, 7, 9**. It is historical and does not override the
October 4 request for new unsettling situations deeper in the Backrooms.

---

## Checking the result

```sh
python tools/check-package-integrity.py     # allowlist, and it reports the folder's slide count
python .local/register/proof-menu-slides.py  # existing source/package slideshow verifier
```

`check-package-integrity.py` prints a note naming the scanned folder and how many textures it
covers, so the count is verifiable without launching anything.

An art-only addition does not require changing or rebuilding the C# assembly. Package/source
checks and static previews do not establish actual menu/notice readability, supported display
crops, transitions, reduced motion, fallback or profile compatibility. Those acceptance cases
remain open for an owner-launched RimSort session; do not infer a result from an older launch.
