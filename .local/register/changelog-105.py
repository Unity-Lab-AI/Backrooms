# -*- coding: utf-8 -*-
import io

p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()

entry = u"""## 0.10.5-dev - 2026-09-29 - every surface the game speaks through

- **New warnings in the alerts readout, down the right-hand edge.** Until now every warning this mod gave you was either a letter you can dismiss and lose, or a line in an inspect pane you had to already be looking at. RimWorld keeps the alerts readout for things that are still wrong *right now*, and the mod used it for nothing.
- **"Recovery overdue"** - the return window ran out and your people are still on the far side. Click it to jump to the gate.
- **"Return window closing"** - a connection failed while it was open and the window is still running. This is the one you can still act on.
- **"No gate operator"** - there is a finished gate and nobody assigned to run one, so no connection can be brought up at all. It stays quiet if any gate has an operator, so keeping a spare door designated does not nag you.
- **Right-click rows that were paragraphs are now rows.** "This gate has not connected anywhere yet." became "No connections yet", and four more like it. A right-click option is a thing you pick, not a sentence read to you - which is how the base game writes them, measured rather than assumed.
- The one that was carrying an instruction now says only the condition, and the instruction moved to the button's own tooltip where there is room for it.

Full record: [every surface the game speaks through](docs/implementation/DISPLAY_SURFACE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""

anchor = u'## 0.10.4-dev - 2026-09-29'
assert anchor in s
s = s.replace(anchor, entry + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG 0.10.5-dev written')
