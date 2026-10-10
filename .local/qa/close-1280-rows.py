"""Close the 0.12.80-dev rows in docs/TODO.md.

FINALIZED was written first; this flips the rows, after which the archiver moves
them out so the queue ends the checkpoint with no completed item in it.
"""

import io
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PATH = os.path.join(REPO, "docs", "TODO.md")

SUBS = [
 # ---- the meal def -------------------------------------------------------
 ('- [~] **"should start scenerio with survival meals not simple meals and should be like 100 to start"**',
  '- [x] **"should start scenerio with survival meals not simple meals and should be like 100 to start"** — **DONE 0.12.80-dev.**'),

 # ---- Prepare Carefully half, same path ----------------------------------
 ('- [~] **"my preparecarfully mod food did not appear"**',
  '- [ ] **"my preparecarfully mod food did not appear"** — **STILL OPEN with the row below.**'),

 # ---- the tab swap -------------------------------------------------------
 ('- [~] **"it should not replace the architects default possition"**',
  '- [x] **"it should not replace the architects default possition"** — **DONE 0.12.80-dev.**'),
 ('- [~] **"so we are swapping theri positions ... so archetect tab is back in its default far left position"**',
  '- [x] **"so we are swapping theri positions ... so archetect tab is back in its default far left position"** — **DONE 0.12.80-dev.**'),
]

# The spawn row keeps its open status and gains what the measurement actually showed.
SPAWN_OLD = '- [~] **"they need to properly spawn in with starting goods"**'
SPAWN_NEW = '- [ ] **"they need to properly spawn in with starting goods"** — **STILL OPEN, and no fix was written on a hunch.**'

text = io.open(PATH, encoding="utf-8").read()
for old, new in SUBS:
    if old not in text:
        raise SystemExit("not found: %r" % old[:70])
    text = text.replace(old, new, 1)
if SPAWN_OLD in text:
    text = text.replace(SPAWN_OLD, SPAWN_NEW, 1)

# The live-read row closes: the read was done and its instrument is recorded.
LIVE_OLD = '- [ ] **"check the current game and whats on the map versus what they were suppose to start with verses how to fix it properly now"**'
LIVE_NEW = '- [x] **"check the current game and whats on the map versus what they were suppose to start with verses how to fix it properly now"** — **DONE 0.12.80-dev: 9,216 cells swept through the bridge against the owner\'s own live process, read-only.**'
if LIVE_OLD in text:
    text = text.replace(LIVE_OLD, LIVE_NEW, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("closed the 0.12.80-dev rows; the spawn row and the Prepare Carefully row stay open")
