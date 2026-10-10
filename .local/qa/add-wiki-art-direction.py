# -*- coding: utf-8 -*-
"""Record the owner's slide-art banner direction verbatim."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — the slide art becomes the wiki's banner, and must not fight the text (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"and use our slide art as a banner or something  /background to where text writing is not fighting the art to be read ,, in the wiki pages\"*",
"",
"**We ship twelve pieces of art and the published wiki uses none of them.** The menu slides are the **only** art in the package — the approved exception to *no gameplay art* — and they are already ours, already licensed, already the mod's visual identity on the main menu. The site is currently all type.",
"",
"**The direction carries its own acceptance test**, which is the part that matters: *\"to where text writing is not fighting the art to be read\"*. So art behind running prose is refused by the instruction itself. **A banner is a band the text sits beside, never underneath**, and anywhere art and type do share a box, the type gets an opaque enough ground that the art cannot reduce its contrast.",
"",
"- [ ] **\"use our slide art as a banner or something /background\"** — a per-page banner drawn from the twelve menu slides, assigned by subject rather than at random, so the gate page carries the gate slide and the deep-levels page carries a deep-level slide. **One slide may serve more than one page**; twelve pieces against thirteen pages means no page is left blank and nothing is invented to fill a slot.",
"- [ ] **\"to where text writing is not fighting the art to be read\"** — **the readability rule is the deliverable, not a caveat.** No body text over art anywhere. Where a title sits on a banner it gets a solid scrim behind it, and the whole banner is marked as decoration so a screen reader skips it rather than announcing a filename. This has to hold at a narrow window too, which is the case a banner usually breaks in.",
"- [ ] **The art has to actually reach the published site**, which is a second job and a quieter one: the public export is an **allowlist**, so a file nobody added is a file that silently is not there. The pages would render with broken images and every instrument would stay green. **Ship the images in the export, then read the live site back.**",
"",
"**Verbatim owner direction (2026-10-05), on which image leads:** *\"make sure the preview image is prominate becasue thats what mod loaders see\"*",
"",
"- [ ] **\"make sure the preview image is prominate becasue thats what mod loaders see\"** — `About/Preview.png` is **the only image a player sees before they ever install**, and the reason is exactly the one the owner gives: it is what a mod loader renders in its list, so it is already doing the job of a cover. **The front page leads with it, at a size that reads as the cover and not as a thumbnail** — not one of the twelve slides, and not buried below the reading tables. The twelve slides stay the per-page banners; this is the mod's face and it goes first. **Same readability rule: nothing written across it.**",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "the slide art becomes the wiki's banner" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d open rows added" % SECTION.count("- [ ] "))
