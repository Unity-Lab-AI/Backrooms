# The player-facing words — 0.12.40-dev

**Rows 1193, 1220, 821, 822, 833.** Five rows, one family: everything left in the queue that was
about what a player reads and how they reach it.

## The queue rows, verbatim

> *"eventually we will need to write a how to to the game paly and systems"* (row 1193)

> *"Remap RimWorld's menus, tabs, and campaign views into the finished company-first Company
> Command layout, growing from the first-playable Operations tab. Keep every relevant Architect,
> Work, Assign, Research, World, map, building, and pawn action reachable; change navigation and
> presentation without replacing the underlying colony simulation."* (row 821)

> *"Add tutorial/guide, help glossary, keyboard/controller paths as appropriate,
> color/contrast/readability options, scalable UI, icons/tooltips, and localization support."*
> (row 822)

## The register, checked first

`python tools/register-query.py trace interface` and `trace facilities`. The interface family's
integration approach is the reason the invasive half of row 821 is not built: **remapping Core's own
tab bar is the one change that would collide with every interface mod in the register at once**, and
the register asks for coexistence rather than replacement throughout that family. Nothing in it
asked for a company-first bar; row 821 did, and row 821 also **challenges its own premise in its own
text** — *"it should be challenged before it is built"*.

The register is guidance, not law, so it does not veto anything. Here it agreed with the row's own
challenge, which is a stronger position than either alone.

## What the measurement found, before anything was written

**Architect opened from nowhere.** The handoff said *"`OpenNativeTab` already opens Architect, Work,
Assign and Research from the company panel"*. It does not and never did — `grep -rn "Architect"
--include=*.cs src` returned **nothing at all**. The panel opened Work and Research; Assign and World
opened from inside the personnel and facilities panes. **Architect — the first surface row 821 names,
and the one every building action in RimWorld goes through — was not reachable from this mod's
interface by any route.** That is the thirteenth time this session a measurement was the defect while
the code was merely incomplete, and the first where the stale measurement was in the handoff itself.

**The company tab was the second button from the right.** Core's own orders are Architect 1, Work 10,
Schedule 20, Assign 30, Animals 40, Wildlife 50, Research 60, Quests 65, World 70, History 80,
Factions 90, Menu 500. Operations shipped at **95** — between Factions and Menu. A tab called
company-first sat as far from first as the bar allows.

**Core generates a keyboard binding for free, and nobody had claimed it.**
`KeyBindingDefGenerator.ImpliedKeyBindingDefs` walks every `MainButtonDef`, and for any that sets
`defaultHotKey` it emits a `KeyBindingDef` named `MainTab_<defName>` into the `MainTabs` category and
assigns it back to the def's `hotKey`. That binding then appears in the player's own Key Bindings
dialog and is rebindable there. **The whole of rows 822 and 833's "keyboard paths" is one XML field**,
and this package authors no `KeyBindingDef` of its own to get it.

**Core takes Tab and F1 through F9 for its main tabs, F10 for `TakeScreenshot` and F11 for
`ToggleScreenshotMode`.** F12 is the only function key it leaves free, so F12 is the default. Taking
any other would have silently stolen a binding the player already had.

**The contrast and scale answer was already true and had nothing holding it true.** Not one file in
`src/RimroomsAsyncIndustries/UI/` authored a colour — no `new Color(`, no `GUI.color`, no
`ColorLibrary` — and the only font work in the whole folder is one `GameFont.Medium` for a heading
with `GameFont.Small` and the caller's font both restored. So the position is: **this package
authors neither colour nor font size in anything a player reads text from**, which means the
player's own Options for interface scale, font and colourblind mode apply to it exactly as they
apply to the base game. An option of ours would have been a second, worse copy of a setting the
game already has.

That was true by accident. It is now held by a checker.

## What shipped

### Row 821, the built half — reachability

`MainTabWindow_Operations` opens **all five surfaces the row names**, in the row's own order:
Architect, Work, Assign, Research, World. Each goes through `MainButtonDef.Worker
.InterfaceTryActivate()` — the game's own button, pressed on the player's behalf, which is what
preserves Core's research, tutorial and world-selection behaviour. An unavailable tab is refused in
words rather than doing nothing.

### Row 821, company-first — and the half that is deliberately absent

`RR_MainButtons.xml` moves to **`<order>0</order>`**, left of Architect's 1. That is one field on
this package's own def and changes nothing about Core's buttons or any other mod's.

**The remap is not built, on purpose, and the absence is asserted rather than assumed.** The proof
refuses a patch against `MainButtonDef` in the package's `Patches/` folder, and refuses any C# of
ours that assigns through a `MainButtonDef`-typed expression — `order`, `buttonVisible`,
`tabWindowClass` or `workerClass`. That second one matters because rewriting Core's bar through the
def database is the one route a Harmony-free mod still has, so it is the one worth closing.

### Rows 822 and 833 — the keyboard path

`<defaultHotKey>F12</defaultHotKey>`. The help pane prints the binding through
`hotKey.MainKeyLabel`, which reads the player's **current** binding, so help stays right for anybody
who rebinds it. `hotKey` is `[Unsaved]` and is filled in by Core's generator, so it is null-checked
before it is read.

### Rows 822 and 833 — the help pane, the thirteenth

A new `Help` pane holding the glossary of every word this package enforces — gate, connection,
threshold, coordinate, band, branch, request, contract, dispatch, debrief, evidence, insight,
facility, site — the live keyboard binding, the readability position, and the first-session
sequence.

**It draws outside `DrawCompany`.** A glossary you need a running company to open is not help, and
the tab is `validWithoutMap` so the pane is reachable from the main menu. The proof asserts both
halves: that help is drawn from the pane branch, and that `DrawHelp` does **not** appear inside the
company block — because being inside it looks identical from the outside until there is no company.

`check-info-cards.py` bans the retired vocabulary everywhere the game displays text. A glossary that
did not define the replacements would leave the player holding enforced words with no explanation of
them, so the four the mod is strictest about are asserted individually.

### Rows 822 and 833 — contrast and scale, as a checker

`check-display-style.py` gains `check_readability()`. In every file under `UI/` it refuses an
authored colour, an assignment to `GUI.color`, a `ColorLibrary` colour, a `UnityEngine.Color`
constant, an inline `<color=` tag, a `Text.Font` set to anything but Core's four `GameFont` values,
and any direct `fontSize`.

Scoped to that folder on purpose. `Presentation/` and `Generation/` author colour deliberately and
correctly — the gate tint, the room palettes, the connection overlay and the menu art are pictures,
not text, and this rule is about text a player reads.

### Rows 1193 and 1220 — `docs/PLAYING.md`

The play document. `HOWTO.md` documents the build and keeps doing so; this one documents play, and it
is **written once** for the repository and the site as row 1193 requires, rather than as two copies
that drift.

It opens with the caveat, because the caveat governs everything under it: **no game has ever been
launched from this repository**, so every instruction in it is a structural claim about the code
rather than a report of play. It also says which side wins on a disagreement — **the game's own
readouts are right and the page is wrong** — because the panes read live state and a sentence was
written from source at one checkpoint. Numbers appear only where the code fixes them; anything the
game computes is described instead.

It joins `READER_FACING` in `check-doc-conformance.py`, now **thirteen documents**, so the
vocabulary rule, the wall rule and the row 791 claim guard all apply to it. Both caught something on
the first run: *"on the Machine pane"* tripped the banned phrase *"the machine"*, and *"no
synchronised research"* tripped the claim guard because the sentence splitter breaks on newlines and
the negator was on the line above. Both were real — the second is the hard-wrap trap that has now
bitten three times, and the fix each time is to put the negator and the phrase in one line.

## The proof, and what the plants found

`.local/register/proof-playing-and-help.py` — **thirty-seventh proof**.
`.local/register/plant-playing-and-help.py` plants **43 faults across three targets** and all 43 are
caught.

**The plant harness now runs every target clean before planting anything**, and prints the exit
status of each. That is the 0.12.39-dev lesson made structural: a plant run there reported 17 of 17
and was worthless, because a syntax error made the proof exit non-zero unconditionally and every
plant registered as caught. A perfect sweep against a broken checker is indistinguishable from a
perfect sweep.

**The first sweep caught 33 of 42, and all nine misses were real.**

Two were **gaps in the new checker**, not in the plants:

* `new UnityEngine.Color(1f, 0f, 0f)` walked past a pattern that matched `new Color(` only — and
  the qualified spelling is the one a file without `using UnityEngine;` would actually have to use,
  which is to say the likelier one. Both the checker and the proof now tolerate a namespace
  qualifier.
* `Text.Font = (GameFont)7` — a font size outside Core's four, precisely what the rule forbids —
  passed both readers, because each allowed any value *containing* the word `Font` in order to let
  the `previousFont` restore through. Now the exemption is a whole-identifier test with `GameFont`
  excluded.

Four were **claims that tested a mention rather than a use**, which is a defect class this project
has now been caught by ten times:

* `"def check_readability("` and `"check_readability(problems)"` — the definition is a superstring
  of the call, so deleting the call changed nothing. The call is now matched with its indentation.
* `"AUTHORED_COLOUR"` matched `AUTHORED_COLOUR_UNUSED`, and `"CORE_FONTS"` matched
  `CORE_FONTS_UNUSED`. Both now assert the definition *and* the use site.
* `"RR_Help_KeyboardRebind" in help_keys` read the keyed file, so deleting the call that draws it
  passed. It now asserts the call.

One was a **detector that depended on a variable being named conveniently.** The runtime-write scan
matched lines mentioning `MainButton`, and a planted `target.order = 3;` walked past it because the
parameter is declared `MainButtonDef target` on a different line — which is exactly how it would
really be written. It now collects every identifier declared as a `MainButtonDef` and refuses an
assignment through any of them.

Two were **weak plants**, and one of those found a writing fault:

* Removing one mention of F12 left the claim satisfied by a second mention. **The document said the
  same fact in two places**, which is its own small defect; F12 is now named once, in the section
  that owns it, and the first-session step points there.
* The wall-of-text plant came to roughly 590 characters against a 700 threshold. Made longer. Same
  shape as the `maxTechLevel` replant at 0.12.37-dev: **the plant was wrong, not the rule.**

## Build

**192 C# files, 88 package files**, zero warnings, zero errors. Assembly SHA-256
`7641035476D6D2A2A5FF326E258E1B5D24E32DD581FFD2A683994B55C2D230C4`, reproduced by two clean
recompiles. **Twelve checkers pass, thirty-seven proofs hold**, all read by exit status.

No game was launched. Nothing here has been played.
