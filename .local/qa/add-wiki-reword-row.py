# -*- coding: utf-8 -*-
"""Record the wiki-rewrite direction verbatim, with the gap measured rather than described."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — the wiki write-ups are stale and generic (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"and add totodo to reword the write ups on the wiki, alot of that shit was written agges ago and is generic horshit stalle as fuck even how it we all explained is all generalized and has nothing weve done written up in it over the last few days\"*",
"",
"### Measured before it was written down, so the row names what is missing rather than repeating the complaint",
"",
"Every one of the thirteen pages was last touched **2026-10-04** — but that was the front-matter and layout pass, not the prose. Swept the pages against what has actually shipped, and **nine player-facing systems appear nowhere in the wiki at all**:",
"",
"| Shipped and a player can see it | Anywhere in the wiki? |",
"|---|---|",
"| **Three operational gates** — the cap, and that a gate dials any address | **no** |",
"| **The random address dial** — going to look rather than being sent | **no** |",
"| **The open-map budget** — five maps, and *\"this gate is blocked\"* | **no** |",
"| **Boarding a natural doorway up** — 25 wood, a real job a pawn walks to | **no** |",
"| **The held-places list and Release** — giving a place back, and what is left behind | **no** |",
"| **Grand pillared halls** — shallow levels are few huge rooms, not small boxes | **no** |",
"| **Staff certification and training** — training is work that completes state | **no** |",
"| **A stranded crew** — a closed gate does not take your people; they survive and you get them out | **no** |",
"| **Material variation by depth** — what a room is built from is part of the loot | **no** |",
"| Odd goods and origin | **yes** — `backrooms.md`, and it is good |",
"",
"**Two apparent hits were false and are worth naming so nobody trusts the grep:** `install.md` matched *Release* on *\"Download the release\"*, and `interface.md` matched *board* on *\"Keyboard\"*. So the real coverage is thinner than a search suggests.",
"",
"- [ ] **\"reword the write ups on the wiki\"** — rewrite the prose on all thirteen pages so each one describes **what this mod actually does now**. The nine systems above are the content that is missing; the row is not a style pass. **Written from the source and the register, never from memory** — that is the method that found five documents lying about dependencies and a multiplayer page that never named the multiplayer mod.",
"- [ ] **\"is generic horshit stalle as fuck\"** — the specific failure is **generality**: pages describe the *shape* of a feature and not the feature. The multiplayer page is the worked example of the fix — it described *\"each player runs their own company\"* and never named **RimWorld Together**, and rewriting it meant naming the thing, its model, its requirement and what is untested. **Every page gets that treatment: name the thing, say what it does, say what is not claimed.**",
"- [ ] **\"nothing weve done written up in it over the last few days\"** — and the gap is one-directional: the **mod** moved and the **wiki** did not. Nine systems shipped with instruments and claims and keyed strings and nobody wrote a sentence a player could read about any of them. **A feature nobody can find out about is a feature nobody uses.**",
"- [ ] **The rules the rewrite still has to obey**, so none of this is traded away for liveliness: the **vocabulary** (`gate`/`connection`/`threshold`, never *portal* or *doorway*, and *the machine* is reserved), the **360-character paragraph ceiling** — owner: *\"public facing documnets ARE NOT to be text walls\"* — **no in-house dev names, no task numbers, no work information**, **no dependency claims** because the mod declares none, **nothing announced as compatible or tested** per D1, and **no reference to the build repositories**. All six are enforced by `check-doc-conformance.py` and the export audit, so a rewrite that breaks one fails the battery rather than shipping.",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "the wiki write-ups are stale and generic" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d open rows added" % SECTION.count("- [ ] "))
