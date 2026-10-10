import io

# --- TODO ------------------------------------------------------------------
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = u"""
**Verbatim owner direction (2026-09-29):** *"real quick make this html open able : \" file:///C:/Users/gfour/Desktop/Backrooms/Mod/Rimrooms%20-%20Async%20Industries/About/About.xml\" as if i open this with edge to read it its all fucked up"*, *"and its a massive text wall needs style formating and beautiful layout"*, *"check for other shit text walls youve made too after you fix this one"* and *"now the about.xml show a blank screen when i open it with edge and i still dont see the html versions"*

- [x] **The description was a single unbroken line of 6,724 characters** - one sentence appended per checkpoint for twenty-odd checkpoints. Rewritten into four titled sections across 37 lines and **half the length**, which fixes RimWorld's own description panel as well as any text viewer.
- [x] **An XSLT stylesheet was tried first and was the wrong answer.** Chromium blocks XSLT loaded from a `file://` URL, so Edge showed a **blank page** instead of raw XML - worse than the original problem. Reverted completely: the stylesheet link, the file and its allowlist entry are gone.
- [x] **`tools/make-readable-html.py`** generates standalone styled HTML with no external dependencies, into **`outputs/readable/`** - `index.html`, `About.html`, `README.html`, `CHANGELOG.html`, `NOW.html`, `TODO.html`, `ROADMAP.html`. Open any of them from anywhere.
- [x] **Other walls swept.** 42 player-facing strings ran over 220 characters. The scenario description (710 chars, read on the scenario picker) and both welcome letters (430 and 470 chars, the first thing a player ever reads) are reflowed into paragraphs.
- [x] **A wall rule added to `check-info-cards.py`**, proved by planting a 510-character string: any displayed text past 420 characters with no paragraph break now fails the build. RimWorld renders newlines, so a wall is a choice rather than a limitation.
- [x] **A vocabulary leak the earlier rule missed:** *"the machine"* meaning the gate, in three places including a research project description. `"the machine"` is now banned as a phrase, while `machining table` stays because it is real Core content.

"""
anchor = u'\n**Verbatim owner direction (2026-09-29):** *"add a memory and a law to always check the registry'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO')

# --- CHANGELOG -------------------------------------------------------------
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
old = u"""## 0.10.4-dev - 2026-09-29 - the register, checked backwards
"""
new = u"""## 0.10.4-dev - 2026-09-29 - the register checked backwards, and a description you can read
"""
assert old in s
s = s.replace(old, new, 1)
old = u"""Full record: [the register, checked backwards](docs/implementation/REGISTER_RETRO_AUDIT.md). No gameplay, balance, performance or compatibility result is claimed.
"""
new = u"""- **The mod description was one unbroken paragraph of 6,724 characters.** It is now four titled sections and half the length, which fixes how it reads in RimWorld's own mod panel too.
- Both welcome letters and the scenario description were walls as well. All reflowed.
- Readable HTML versions of the description, readme, changelog and working docs are generated into `outputs/readable/`.

Full record: [the register, checked backwards](docs/implementation/REGISTER_RETRO_AUDIT.md) and [a description you can read](docs/implementation/READABLE_TEXT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.
"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG')

# --- FINALIZED -------------------------------------------------------------
p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

### Addendum - a description you can actually read

> *"real quick make this html open able ... as if i open this with edge to read it its all fucked up"*, *"and its a massive text wall needs style formating and beautiful layout"*, *"check for other shit text walls youve made too"*, *"now the about.xml show a blank screen when i open it with edge and i still dont see the html versions"*

The About description had reached **a single unbroken line of 6,724 characters** - one sentence appended per checkpoint for twenty-odd checkpoints. Rewritten into four titled sections across 37 lines and half the length, which fixes RimWorld's own description panel as well as any viewer.

**An XSLT stylesheet was tried first and was the wrong answer.** Chromium blocks XSLT loaded from a `file://` URL, so Edge showed a **blank page** instead of raw XML - worse than the problem it was solving. Reverted completely, and replaced with `tools/make-readable-html.py`, which writes standalone styled HTML into `outputs/readable/` with no external dependencies and no restriction on where it is opened.

Sweeping for other walls found **42 player-facing strings over 220 characters**, including the scenario description a player reads on the picker and both welcome letters, which are the first thing anybody reads. All reflowed. A wall rule now fails the build on any displayed text past 420 characters with no paragraph break, proved by planting one - RimWorld renders newlines, so a wall is a choice rather than a limitation.

The sweep also caught a vocabulary leak the earlier rule missed: *"the machine"* meaning the gate, in three places. It is banned as a phrase now, while `machining table` stays because it is real Core content.
"""
assert '### Addendum - a description you can actually read' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED')

# --- NOW -------------------------------------------------------------------
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
old = u"| 0.10.4 | **The register, checked backwards** — a LAW, a query tool, and a real defect found |"
new = (u"| 0.10.4 | **The register, checked backwards** — a LAW, a query tool, and a real defect found; "
       u"plus a readable description and `outputs/readable/` HTML |")
assert old in s
s = s.replace(old, new, 1)

marker = u'\n\n---\n\n## The warning that matters most right now'
addition = u"""
79. **Chromium blocks XSLT from `file://`.** A stylesheet on About.xml gives a **blank page**, not a styled one. Generate standalone HTML instead: `python tools/make-readable-html.py` writes `outputs/readable/`.
80. **RimWorld renders newlines in descriptions and letters, so a wall of text is a choice.** `check-info-cards.py` fails any displayed string past 420 characters with no paragraph break. The About description had reached 6,724 characters on one line.
81. **`"the machine"` is banned in player-facing text**; `machining table` is real Core content and stays."""
assert marker in s
s = s.replace(marker, addition + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW')
