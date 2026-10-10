# -*- coding: utf-8 -*-
"""Record the owner's full-wiki-accuracy direction verbatim and open the nine checkup rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — fix the whole wiki against the code, not against the old wording (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"yes and i want the full wiki fix all the shit that was written ages ago that stall and not accurate to code, making sure the wiki is accurate not the old shit and old wordings that are being copied and pasten from weeks ago\"*",
"",
"**This supersedes nothing and sharpens everything.** The rewrite rows already recorded asked for prose that is not generic. This direction names the actual standard: **every page is rewritten from the code that implements it**, and the failure mode is named too — *\"old wordings that are being copied and pasten from weeks ago\"*. The checkup proved that is literally what happened: `gates.md` carries *\"through depth 3\"* because the **source's own first `<summary>` block** still says it, two years of version bumps later.",
"",
"**So the method is fixed, not optional:** measure the constant, read the keyed string, then write the sentence. Never the reverse, and never from a neighbouring page.",
"",
"- [~] **\"making sure the wiki is accurate not the old shit\"** — every one of the thirteen pages re-derived from source. The nine checkup rows below are the known defects; the standard is that **no number, threshold, count or behaviour appears on a page unless it was read out of the code in the same pass that wrote it**, with the verified-correct table standing as the record of what must not be disturbed.",
"- [ ] **\"old wordings that are being copied and pasten from weeks ago\"** — and the copy-paste has a **source-side root** that has to be cut or the next pass inherits it again: a stale doc comment that still argues the superseded value. `NaturalFrontierService.MaximumNaturalDepth` is the proved case. **Sweep the doc comments on every constant the wiki quotes**, because a page is only ever as accurate as the comment somebody read to write it.",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "fix the whole wiki against the code" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d open, %d in progress" % (SECTION.count("- [ ] "), SECTION.count("- [~] ")))
