"""Prepend the 0.12.80-dev entry to CHANGELOG.md.

Written to a file rather than a heredoc: a heredoc has mangled an escape or an
apostrophe eleven times in this repository and `docs/NOW.md` records each one.
"""

import io
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PATH = os.path.join(REPO, "CHANGELOG.md")

ENTRY = u"""## 0.12.80-dev - 2026-10-02 - Architect gets its corner back, and the shop stocks a meal that keeps

- **The Architect tab is at the far left again.** The Operations tab had taken that slot, so
  reaching for Architect out of habit opened Operations instead. The two have swapped: Architect
  sits where it always did and Operations is immediately to its right. **Nothing about Core's own
  buttons or any other mod's was changed to do it** - only this mod's own button moved.
- **The Furniture & Knickknack Store starts with 100 packaged survival meals instead of 24 simple
  meals.** A simple meal spoils, so a shop start was handing you two dozen meals and then quietly
  taking them away. It was also the only start granting a simple meal at all; the other two
  already used survival packs.

Nothing else in the game changed. No gameplay, balance, performance or compatibility result is
claimed.

"""

text = io.open(PATH, encoding="utf-8").read()
marker = u"# Changelog\n\n"
if u"## 0.12.80-dev" in text:
    raise SystemExit("0.12.80-dev entry already present")
if not text.startswith(marker):
    raise SystemExit("CHANGELOG.md does not start with the expected header")
io.open(PATH, "w", encoding="utf-8", newline="").write(
    marker + ENTRY + text[len(marker):]
)
print("prepended 0.12.80-dev entry")
