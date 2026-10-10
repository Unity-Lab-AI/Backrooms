# -*- coding: utf-8 -*-
"""Move the two deferred decisions to ROADMAP.md as majors, and clear their TODO rows.

Owner, on the expansion content: *"option 1,2,3 but all deffered thats massive"*. On the entity
sheets: *"option 1 but also deffered as this is deep"*.

`DEFERRED.md` is closed and never takes a row, so deferral here means **grain escalation**: these
are milestones rather than tasks, and `ROADMAP.md` is the ledger for major grain. The decision
travels with them, so the next person does not have to re-ask what was already settled.
"""
import io
import sys

NL = chr(10)
ROADMAP = "docs/ROADMAP.md"
TODO = "docs/TODO.md"

ANCHOR = "- [~] **M2 — Existing-content replacement**"

MAJORS = NL.join([
"- [ ] **M9 — Expansion content, thick and optional** (RR-DLC; decided by owner answer 2026-10-05).",
"  **Owner decision, verbatim:** *\"option 2 and 3 not thin but thick\"*, then on scope and timing: *\"option 1,2,3 but all deffered thats massive\"*.",
"  **Scope:** real content for all five expansions this profile knows, each **absent-safe and never required** — Royalty titles and psycasts as optional company routes, Ideology beliefs, rituals and staff policy, Biotech genes and mechanitors, and the headline: **an Odyssey gravship that carries a branch** — relocating its tile with the gate left commissioned and the account, coordinates and records following it.",
"  **Sequence the owner chose, and it matters:** **a brief for each of the four comes before any code**, because this is the largest remaining piece of work and building it on a guess is how it gets built twice. The gravship is the one that changes play, so it leads.",
"  **Standing constraints it may not break:** zero declared dependencies, nothing announced as required, every lookup degrading when a provider is absent, and no first objective of any start gated on a provider. The stand-alone guarantee is not negotiable against this.",
"  **Exit condition:** four briefs approved by the owner, then content per brief with each unlock asserted to be read by real behaviour, `check-dlc-gating.py` green, and the package still declaring no dependencies.",
"",
"- [ ] **M10 — Entity and anomaly design sheets for what ships** (RR-THREAT; decided by owner answer 2026-10-05).",
"  **Owner decision, verbatim:** *\"option 1 but also deffered as this is deep\"* — option 1 being sheets for the twelve inhabitants that actually ship, and explicitly **not** designing entities that do not exist.",
"  **Scope:** one sheet per shipped inhabitant — wanderers, the missing, survivors, the psychotic and its pack, the recent and stripped dead, the dead crew, and the rest of the twelve — each carrying its **readable tell**, its appearance and readability, its AI rules and triggers, its **limits**, its counter, what evidence it yields, the risk of studying it, and capture or containment where either applies.",
"  **Why it is a milestone rather than a task:** the owner called it deep, and it is — a sheet that invents a limit the code does not keep is worse than no sheet, so each one has to be read out of the inhabitant's own behaviour and then asserted.",
"  **Standing constraint:** *\"remember lsd unnerving feeling with all things\"*. Every sheet has to name the one exact wrong detail that makes its subject uncanny, **readable as text and never as atmosphere alone**.",
"  **Exit condition:** twelve sheets, each with its tell and limit traceable to source, and nothing in them describing an entity that does not exist.",
"",
])

CLEAR = [
    "Royalty conditional content:",
    "Ideology conditional content:",
    "Biotech conditional content:",
    "Odyssey conditional content:",
    "Author entity/anomaly design sheets first:",
]

EVIDENCE = (" — **MOVED TO `ROADMAP.md` 0.12.98-dev as part of %s, on the owner's own word "
            "*\"deffered\"*.** The decision is made and travels with it; what is deferred is the "
            "work, not the question. **It leaves the working queue because it is a milestone "
            "rather than a task** — a row somebody could not pick up today reads as one they "
            "should have.")


def main():
    roadmap = io.open(ROADMAP, encoding="utf-8").read()
    if "M9 — Expansion content" in roadmap:
        print("the majors are already recorded; nothing written")
        return 1
    if roadmap.count(ANCHOR) != 1:
        print("ROADMAP anchor matched %d time(s); refusing" % roadmap.count(ANCHOR))
        return 1
    at = roadmap.index(ANCHOR)
    io.open(ROADMAP, "w", encoding="utf-8", newline=NL).write(
        roadmap[:at] + MAJORS + roadmap[at:])
    print("ROADMAP: two majors recorded")

    text = io.open(TODO, encoding="utf-8").read()
    lines = text.split(NL)
    done = 0
    missed = []
    for phrase in CLEAR:
        which = "M10" if "entity" in phrase else "M9"
        hits = [i for i, l in enumerate(lines)
                if l.startswith(("- [ ] ", "- [~] ")) and phrase in l]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        lines[hits[0]] = "- [x] " + lines[hits[0]][6:].rstrip() + (EVIDENCE % which)
        done += 1
    if missed:
        for phrase, count in missed:
            print("NOT CLEARED (%d matches): %s" % (count, phrase[:60]))
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("TODO: %d row(s) cleared into the roadmap" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
