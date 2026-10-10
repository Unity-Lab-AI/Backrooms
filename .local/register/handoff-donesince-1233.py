# -*- coding: utf-8 -*-
"""Rewrite "Done since the last handoff" for 0.12.24 -> 0.12.33.

It still described 0.12.11 -> 0.12.22, which was true at the previous handoff and is ten
checkpoints stale. This section exists so nobody rebuilds what shipped, so a stale version is
actively harmful: it under-reports what is done and over-reports what is left.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()

start = s.index(u'### Done since the last handoff, so nobody rebuilds it')
end = s.index(u'## Invariants — do not break these')

s = s[:start] + u"""### Done since the last handoff, so nobody rebuilds it

**Ten checkpoints, 0.12.24 → 0.12.33.** Every one published to all eight refs with a read-back, a
deterministic assembly, and the full checker and proof sweep. Twelve rows closed.

**Two of the three shipped starts had no campaign at all.** `EstablishCorporationContact()` had
**no caller anywhere**, and `corporationContact` gates the tutorial line, generated requests, the
Purchase route **and the clean-up team's rescue**. The Store and Solo/Group starts were a sandbox
with a locked door, permanently, while the chart and `RR_Starts.xml` both said *"reaching contact is
the achievement"*. The owner named the mechanism mid-build — *"once they contact the cvompany in
comms they can start async quest line"* — and it **deleted most of the planned work**: no parallel
solo line was needed, because the existing gate on `corporationContact` was the whole mechanism.
**Starts that can reach the campaign: was 1 of 3, now 3 of 3.**

**The last authored gameplay item is retired, without a save break.** `RR_FieldRecorder`'s job
folded into Core's `TextBook` — the answer had been written down at 0.9.9-dev and sat fourteen
checkpoints because **no proof asserted anything about it.** The def stays loadable so saves open;
it is simply never granted or sold again. A dead end was found on the way: Core gives books
`Flammability 1` and sells them only as random outlander stock, so `RR_Procurement_RecordBooks`
exists.

**Two crew who disagree now produce a real disagreement, and an interview settles it.** The
contradiction was **already being computed and thrown away** as `RR_Company_ReceiptMismatch`, and
chart line 226 asked request 5 for *"two crew accounts of the same room"* — unreachable, because one
evidence record could carry only one witness per fact. And **nobody is lying**: `validFact` runs
against the real map *before* the prior-observation branch, so a disputing account was already
checked and found true. The marker moved. That is 0.10.3-dev's displacement seen from inside an
evidence file, and it is why no reliability statistic was invented.

**The research ladder is complete at six rungs, and two branches deliberately have none.** Tier 4
was surveyed rather than assumed, because 0.12.5-dev deleted four tier 3 projects for being unlocks
with nothing to unlock. **Logistics gets no tier 4** — all four of its knobs are claimed and what
remains are safety bounds no player reaches — and the **gate line cannot have one**, because its
fourth rung already stops the countdown. Both absences are proof claims, since an absence cannot be
read.

**1×3 and 2×3 gates exist with no mods at all.** A run of adjacent Core 1×1 doors binds into one
gate, one width, read the same from both sides. The change is small because **a line of N adjacent
1×1 doors is a 1×N `CellRect`**, which is what every existing size derivation already worked off.

**Fourteen pieces of in-game text told the player to use equipment that does not exist** — a return
beacon, a survey tag, an evidence case, a field recorder. `check-keyed-strings` verifies a key
*resolves*, not that it is *true*. The **tenth checker** derives retired names from the archive, and
repairing the archive came first: `RR_ReturnBeacon` had never been archived, so the derivation
would have been quietly partial and passed.

**Everything this mod authors is now read by something** — the **eleventh checker**, 258 defs and
102 actions audited. One unwired capability got a surface (cutting a connection without disabling
the gate); one duplicate was retired.

**Surgery across a gate cannot be built, and that is now a proof rather than a gap.** `Bill_Medical`'s
patient *is* the bill giver, reserved from the doctor's map, with ingredients searched on the
doctor's map. The patient comes home — which the casualty route has done since 0.5.2-dev.

**Three things the game knew and never said:** the crossing order is on the door with its refusal
named in place, every coordinate reports its pressure band, and selling everything at a beacon asks
first.

**Four rows were already built and just never closed** — 227, 308, 493 and the recorder fold.
**Check a row against the code before building for it.**

""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('done-since rewritten for 0.12.24 -> 0.12.33')
