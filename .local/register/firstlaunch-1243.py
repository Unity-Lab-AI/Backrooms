# -*- coding: utf-8 -*-
"""Record the first launch's three findings in the queue. Owner words verbatim.

Written as a file rather than a bash heredoc because the prose contains apostrophes and escape
sequences, and the heredoc has now mangled both three times in this session.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "TODO.md")

original = io.open(PATH, encoding="utf-8").read()

ANCHOR = u"## TOMBSTONES"

ROWS = u"""## First launch findings — 2026-09-30

**The first launch in this project's history.** Owner words are verbatim.

- [x] **"okay the game is up and running with the bridge and the first thing i see as a bug is in the edb prepare carfully on the set up when pressing start game it shows - Comapny Overview" and its a blank pop up page... is that noraml? dont seem it"** — **FIXED 0.12.43-dev.** `Page_RimroomsCompanySetup` drew its title and both buttons and an entirely empty body, with **nothing in the log**. Cause: **Unity's IMGUI state is process-wide and not one of this package's six window entry points reset any of it**, so each inherited whatever the previously drawn mod left in `GUI.color`, `Text.Font` and `Text.Anchor` — and a leaked zero-alpha colour paints nothing and logs nothing. Core draws the page title and buttons and sets its own state, which is exactly why the frame was visible and only our content was not. **This is the other half of the 0.12.40-dev claim that this package authors no colour:** authoring nothing is not the same as assuming nothing. `RimroomsWindowState` now resets to Core's defaults and **restores what it found**, on all six entry points, and `check-display-style.py` — which forbade `GUI.color =` outright and so blocked its own fix — was taught that resetting to white imposes no palette. The setup page additionally **cannot go blank silently any more regardless of cause**: the introduction draws outside the scroll view, the body is wrapped so a throw is logged **and painted on the page**, and the listing closes on every path. Record `implementation/FIRST_LAUNCH_BLANK_PAGE_IMPLEMENTATION.md`.

- [x] **"its blank once use set up edb prepare carfully for building game pawns out then pressing start opens this async industries pop up"** — same finding as the row above, and this is the sentence that identified it: the page opens **after** EdB hands off, which is where a mod that leaves draw state dirty would sit in the draw order. Closed by the same fix.

- [ ] **F12 collides with HugsLib's "Publish log file", and every function key F1–F12 is bound across Core plus the 288 installed mods.** 0.12.40-dev took F12 after checking it against **Core only** and writing *"the only function key Core leaves free"* — true about Core, and misleading about the profile this mod exists to work with. Register row 85 (EdB Prepare Carefully) says in its own words *"avoid overriding hotkeys."* **Owner decision needed:** ship no default and author our own rebindable `KeyBindingDef`; keep F12 and document the collision; or pick a non-function key. Found 2026-09-30 on the first launch.

- [ ] **EdB Prepare Carefully cannot classify our GlowPod scenario grant** — *"Couldn't initialize all scenario equipment. Didn't find an equipment entry for GlowPod (no material)"*, logged **twice per setup**. `GlowPod` is a Core **Building** granted as a starting thing in two of our scenarios. Vanilla copes, because `ScenPart_StartingThing_Defined` calls `MakeMinified()` on anything minifiable; EdB's equipment database has no entry for a building with no stuff. It logs and continues, so it looks cosmetic — but it is ours and it is noise on every single setup. Found 2026-09-30 on the first launch.

---

"""

if original.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d occurrence(s) of %r" % (original.count(ANCHOR), ANCHOR))
    raise SystemExit(1)

io.open(PATH, "w", encoding="utf-8", newline="").write(
    original.replace(ANCHOR, ROWS + ANCHOR, 1))
print("four first-launch rows recorded, owner words verbatim")
