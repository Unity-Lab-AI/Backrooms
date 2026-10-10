# -*- coding: utf-8 -*-
"""Append the 0.12.40-dev entry to FINALIZED.md. Appends only; nothing existing is touched."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "FINALIZED.md")

ENTRY = u"""

---

## 0.12.40-dev — the words a player reads

**Rows 1193, 1220, 821, 822, 833.** Five rows, one family. Owner direction for the run, verbatim:

> *"okay we are getting close so go ahead and read the NOW.md to finish wrapping up what we need to
> do to finish the build"*

Row 1193, verbatim: *"eventually we will need to write a how to to the game paly and systems"*.

**`docs/PLAYING.md` written, once, for the repository and the site**, as row 1193 requires.
`docs/HOWTO.md` documents the build and keeps doing so. The play document opens with the caveat that
governs everything under it — **no game has ever been launched from this repository**, so every
instruction in it is a structural claim about the code rather than a report of play — and it says
which side wins on a disagreement: **the game's own readouts are right and the page is wrong.** It
joins the reader-facing set, now **thirteen documents**, and **both rules caught something on the
first run**: *"on the Machine pane"* tripped the banned phrase *"the machine"*, and a denial of
synchronised research tripped the row 791 claim guard because the sentence splitter breaks on
newlines and the negator was hard-wrapped onto the line above. The second is the hard-wrap trap for
the third time; the fix each time is to put the negator and the phrase on one line.

**The first surface row 821 names opened from nowhere in this package.** `grep -rn "Architect"
--include=*.cs src` returned **nothing at all** across 191 files — and `docs/NOW.md` said it was
already reachable, which is the worst place for a stale measurement because a fresh session trusts
it instead of checking. Architect is the surface every building action in RimWorld goes through. All
five surfaces the row names now open from the company panel, in the row's own order, each through
`MainButtonDef.Worker.InterfaceTryActivate()` — the game's own button pressed on the player's
behalf, which is what preserves Core's research, tutorial and world-selection behaviour.

**A tab called company-first was second from the right.** Core's own orders run Architect 1 through
Factions 90 and Menu 500; Operations shipped at **95**, between the last two. Order 0 now.

**The remap itself is deliberately not built, exactly as row 821 says to consider** — the row
challenges its own premise in its own text. Rewriting Core's tab bar would fight every interface mod
in the register at once, and **reachability was the requirement the row actually states.** The
absence is asserted rather than assumed: the proof refuses a patch against `MainButtonDef` and
refuses any C# of ours that assigns through a `MainButtonDef`-typed expression, because the def
database is the one route to Core's bar a Harmony-free mod still has.

**The whole keyboard requirement was one XML field.**
`KeyBindingDefGenerator.ImpliedKeyBindingDefs` emits a rebindable `MainTab_<defName>` into the
`MainTabs` category for any `MainButtonDef` that sets `defaultHotKey`, so the binding lands in the
player's own Key Bindings dialog and **this package authors no `KeyBindingDef` at all**. The default
is **F12, the only function key Core leaves free** — it takes Tab and F1–F9 for its main tabs, F10
for `TakeScreenshot` and F11 for `ToggleScreenshotMode`. The help pane prints the player's **live**
binding, not the shipped one, so help stays right for anybody who rebinds it.

**A thirteenth Operations pane, `Help`**, holding the first-session sequence and a definition for
every word this package enforces — gate, connection, threshold, coordinate, band, branch, request,
contract, dispatch, debrief, evidence, insight, facility, site. It draws **outside** the company
block and the tab is `validWithoutMap`, because **a glossary you need a running company to open is
not help.** The proof asserts both that it is drawn and that it is *not* drawn from inside the
company block, since that failure looks identical from the outside until there is no company.

**Contrast and scale were already right and had nothing holding them right.** Not one file under
`UI/` authored a colour, and the only font work in the folder is one `GameFont.Medium` heading with
the caller's font restored. So the position is that this package authors **neither colour nor font
size in anything a player reads text from**, and the player's own Options for interface scale, font
and colourblind mode apply exactly as they do to the base game. **An option of ours would have been
a second, worse copy of a setting the game already has.** `check-display-style.py` gained
`check_readability()` to hold it, because an absolute with no check behind it is a promise.

**The plant harness now runs every target clean before it plants anything**, and prints each exit
status. That is the 0.12.39-dev lesson made structural, and this batch justified it immediately:
**33 of 42 on the first sweep, and all nine misses were real.** Two were gaps in the new checker —
`new UnityEngine.Color(...)` walked past a pattern matching `new Color(` only, which is the spelling
a file without the `using` would have to write; and `Text.Font = (GameFont)7`, a font size outside
Core's four, walked past an exemption meant for the `previousFont` restore. Four were claims that
tested a **mention** rather than a **use** — `def check_readability(` satisfies a probe for
`check_readability(problems)`, `AUTHORED_COLOUR` matches `AUTHORED_COLOUR_UNUSED`, and a keyed-file
check passed while the call that draws it was deleted. One was a detector that depended on a
variable being named conveniently: a planted `target.order = 3;` walked past a scan for lines
mentioning `MainButton`, because the parameter is declared on a different line, which is exactly how
it would really be written. Two were weak plants, and one of those found a writing fault — the
document stated the same key in two places, so removing one left the claim satisfied.

**192 C# files, 88 package files**, zero warnings, zero errors. Assembly SHA-256
`7641035476D6D2A2A5FF326E258E1B5D24E32DD581FFD2A683994B55C2D230C4`, reproduced by two clean
recompiles. **Twelve checkers pass, thirty-seven proofs hold**, all read by exit status. **43 of 43
planted faults caught**, against a baseline verified first. Record:
`implementation/PLAYER_FACING_IMPLEMENTATION.md`.

No game was launched. Nothing in this batch has been played.
"""

text = io.open(PATH, encoding="utf-8").read()
assert u"0.12.40-dev — the words a player reads" not in text, "entry already present"
io.open(PATH, "a", encoding="utf-8", newline="").write(ENTRY)
print("FINALIZED.md appended: 0.12.40-dev")
