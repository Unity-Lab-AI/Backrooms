# The first bug a real launch found — 0.12.43-dev

**The first launch in this project's history, and the first thing it found was ours.**

## The report, verbatim

> *"okay the game is up and running with the bridge and the first thing i see as a bug is in the
> edb prepare carfully on the set up when pressing start game it shows - Comapny Overview" and its
> a blank pop up page... is that noraml? dont seem it"*

> *"review company startup back and start"*

> *"its blank once use set up edb prepare carefully for building game pawns out then pressing start
> opens this async industries pop up"*

So: configure pawns in EdB Prepare Carefully, press Start, and **`Page_RimroomsCompanySetup` opens
with its title and both buttons drawn and its body completely empty.**

## What the evidence said, and what it ruled out

| Checked | Result |
|---|---|
| `Player.log` for an exception | **nothing.** 12,072 bytes, and it did not grow when the page opened |
| our 39 keyed files | parse clean, 1693 keys, zero duplicates — the log's *"2 translation errors"* are not ours |
| all 288 installed mods for the string *"Company Overview"* | **zero matches**, so no keyed string anywhere says it |
| `Page.InitialSize` | `StandardSize`, 1020×764 — the page is large, the geometry was never the problem |
| the scroll-view and listing nesting | correct: `BeginScrollView` → `listing.Begin` → `listing.End` → `EndScrollView` |
| RimBridgeServer for a captured log | none on disk |

**Title and buttons drawn, body not, nothing logged.** That combination is the diagnosis, because
Core draws the title and the buttons — `Page.DrawPageTitle` and `Page.DoBottomButtons` — and Core
sets the state it needs before it draws. Our body drew straight after and set nothing.

## The defect

**Unity's IMGUI state is process-wide.** `GUI.color`, `Text.Font`, `Text.Anchor` and `Text.WordWrap`
are globals, and every mod's `OnGUI` runs against the same globals. A mod that sets `GUI.color` and
returns without restoring it tints **every window drawn after it** — and if the alpha is zero, those
windows paint nothing and log nothing.

**Not one of this package's six window entry points reset any of it.** Measured:

```
grep -rn "override void DoWindowContents" src   ->  6
grep -rn "GUI.color\|Text.Anchor" src/.../UI    ->  0
```

The setup page is simply the first of ours a player ever sees, which is why it was the first to be
reported. The other five had the identical flaw.

## The other half of a claim made at 0.12.40-dev

That checkpoint asserted this package **authors no colour and no font size** in anything a player
reads, so the player's own contrast, scale and colourblind settings apply. **That was true and it is
still true.** What went unexamined is that **authoring nothing is not the same as assuming
nothing**: a window that sets no colour inherits one.

Worse, `check-display-style.py` — written in the same checkpoint to hold that claim — **forbade
`GUI.color =` outright, so my own rule blocked the fix.** That is the interaction worth recording:
a rule stated as a pattern ban rather than as a purpose will eventually forbid the right thing.

The rule's purpose is *do not impose a palette on the player*. Resetting to `Color.white` imposes
nothing — **white is the absence of a tint**, which is exactly what lets the player's settings
decide. So the rule now has one named exception, and the exception has rules of its own.

## What shipped

**`RimroomsWindowState`** — a disposable struct that captures `GUI.color`, `Text.Font`,
`Text.Anchor` and `Text.WordWrap`, resets them to Core's window defaults, and **puts the originals
back on the way out**. Used through `using (RimroomsWindowState.Clean())` so an early return or a
throw cannot skip the restore.

Restoring matters as much as resetting: leaving `GameFont.Small` set would make this package the mod
that breaks the next one, which is the failure being fixed.

**All six entry points now use it** — the setup page, the Operations tab, the expedition-closure and
cargo-declaration dialogs, and the personnel dossier and hire-confirmation dialogs.

**The setup page also stops being able to go blank silently**, independently of the cause:

* the introduction is drawn **outside** the scroll view, so it is the one thing true in every state
  and no failure below can take it down
* the review body is wrapped in `try`/`catch` — a throw is written to the log **and painted on the
  page** as `RR_Setup_DrawFault`, with a note that Back and Start still work and to report the text
* the listing is closed on every path, so a throw can no longer wedge the GUI group stack

**`docs/PLAYING.md` promises that nothing fails silently.** A blank page with an empty log was that
promise broken, and the fix is as much about the page reporting as about the state.

## Honesty about the fix

**The state guard is a diagnosis, not an observation.** The evidence is strong — frame drawn, body
not, nothing logged, and six windows with no state reset in a 288-mod load — but **nobody has seen
the page work.** What is certain is the second half: if the page fails again for any reason, it will
**say so on itself and in the log** instead of being blank. That is the part that cannot be wrong.

## What the same launch also found, not yet fixed

**F12 collides with HugsLib.** HugsLib binds F12 to *Publish log file*. 0.12.40-dev took F12 after
checking it against **Core** and writing *"the only function key Core leaves free"* — true about
Core, and misleading about the profile this mod exists to work with. **Every one of F1–F12 is bound
across Core plus the 288 installed mods**, and register row 85 (EdB Prepare Carefully) says in its
own words *"avoid overriding hotkeys."* Sixteenth time this session a measurement was the defect:
right thing, wrong population. **Open for an owner decision.**

**EdB cannot classify our GlowPod scenario grant.** Twice per setup:
*"Couldn't initialize all scenario equipment. Didn't find an equipment entry for GlowPod (no
material)."* `GlowPod` is a Core **Building** we grant as a starting thing in two scenarios. Vanilla
copes — `ScenPart_StartingThing_Defined` calls `MakeMinified()` on anything minifiable — but EdB's
equipment database has no entry for a building with no stuff. It logs and continues, so it looks
cosmetic. **It is ours and it is noise on every single setup.** Open.

## The proof, and what the plants found

`proof-playing-and-help.py` gained four claims and **caught its own 0.12.40 claim going stale** on
the first run after the fix — *"no readout file authors a colour"* failed against the new guard,
which is the checker working exactly as intended.

`plant-playing-and-help.py` gained **ten plants** and the sweep is **53 of 53**. Two missed first,
both the same shape that has now defeated a claim in **four consecutive batches**: `GUARD_REQUIRED`
survives `for needle, why in []:` completely intact, and `if unguarded:` had no claim on it at all.
**A claim that a rule exists is not a claim that it runs** — definition, loop, and branch are all
asserted now.

Four plants put the regression back deliberately: the guard losing its restore, the guard choosing a
colour instead of resetting, the setup page drawing unguarded again, and the Operations tab drawing
unguarded again. All caught.

## Build

**197 C# files, 89 package files**, zero warnings, zero errors. Assembly SHA-256
`FD9190DACFEF79624B6E4481764169B10D17706902CF711EC369F9C0577446E8`, reproduced by two clean
recompiles. **Thirteen checkers pass, thirty-nine proofs hold.** 53 of 53 planted faults caught.

Staged to the owner's Local Mods folder. No game was launched by this work.
