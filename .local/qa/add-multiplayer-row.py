# -*- coding: utf-8 -*-
"""Record the multiplayer-page question verbatim, and close it with the rewrite."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner question — a multiplayer page that never names the multiplayer mod (2026-10-05)",
"",
"**Verbatim owner question (2026-10-05):** *\"and how can we have a multiplayer section to the wiki if we dont explain how to Use Rim Together... i mean thats the multipleyer mod.... u didnt build a whole muliplayer client and server that i dont know about did you?\"*",
"",
"**No. Nothing of the sort exists** — this mod contains no client, no server and no networking of any kind, and the answer to the question as asked is a flat no.",
"",
"**But the point underneath it was right, and it was live.** `docs/wiki/multiplayer.md` was honest about what is not promised and said *\"Each player runs their own company, in their own colony, on their own map\"* — **without ever naming RimWorld Together.** A reader landed on a page titled *Multiplayer*, learned the **shape** of it, and was told nothing about **what software would make any of it happen.** Describing a shape while withholding the thing that provides it is a worse page than having none.",
"",
"- [x] **\"how can we have a multiplayer section to the wiki if we dont explain how to Use Rim Together\"** — **FIXED 0.12.96-dev, and written from the register rather than from memory.** Register row **196, RimWorld Together**, Workshop `3005289691`, family *\"Multiplayer: separate colonies and shared-world exchange\"*, stance **Optional**, disposition *\"Provisional: async co-op layer for separate facilities ... No live shared-map or shared research\"*. The page now **names it, links it, and explains its model**: separate colonies on separate maps, with **offline visits and raids and item and pawn exchange** linking them, which is precisely why a branch office fits it — two players are two companies, not one company with two managers. **It records that RimWorld Together needs Harmony and that we do not**, which is a real distinction a reader will otherwise get backwards. **It states that everyone needs the same mod list**, because the register notes *\"the server does not enforce mod order/settings\"*. **And the denials stay, now correctly attributed:** no shared colony, no shared map, no synchronised research are **RimWorld Together's own model**, not limits this mod added. **Nothing is announced as tested**, per D1 — the untested list is named item by item from the register’s own acceptance evidence: separate starts, an offline visit, a supply or aid exchange, reconnecting after a drop, and whether anything company-specific transfers at all. The page’s own words: *\"A real result is worth more here than anything on this page.\"*",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "a multiplayer page that never names" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded and closed the multiplayer row")
