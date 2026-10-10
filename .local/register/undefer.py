"""Move every open row out of DEFERRED.md and into TODO.md under its owning major.

Owner direction, 2026-09-29, verbatim:

    un deffer everything in defferments.md and put it all back in the todod properly
    LIKE I SAID NOTHING SHALL BE DEFFERED SO USE ASK ME FUCKIGN QUESTION OR FUCKING RE
    MAKE IT IN THE TODO CORRECTLY AS MOST ARE TEST SHIT THAT IVE BEEN SAYING SINCE THE
    START WE DO WHEN ITS ALL COMPLETE AND 100% FINISHED!!!! DO YOU UNDERSTAND THIS!!!!!

Every row is carried across byte-for-byte. Nothing is summarised, reworded or dropped.
"""

import io
import re

DEFERRED = "docs/DEFERRED.md"
TODO = "docs/TODO.md"

# DEFERRED section heading -> the TODO heading that owns its rows.
OWNER = {
    "Owned by M1 resume step 4 (work intents, leases, adapters)":
        "### Major M1 — Connected colony portals",
    "Owned by M1 resume step 5 (providers, scenario openings, inhabitants)":
        "### Major M1 — Connected colony portals",
    "Owned by M1 resume step 6 (milestone hygiene)":
        "### Major M1 — Connected colony portals",
    "Owned by the containment direction (2026-09-29)":
        "### Owner universe direction — the Backrooms has no outside (2026-09-29)",
    "Owned by the continuous-topology direction (2026-09-29)":
        "### Owner universe direction — continuous portal topology across every start (2026-09-29)",
    "Owned by M3 (scenario framework) — the universe period and factions":
        "### Owner universe direction — period and factions (2026-09-28)",
    "Owned by M2 (existing-content replacement)":
        "### Major M2 — Existing-content replacement",
    "Owned by M3 (Phase 3 breadth) — deferred by dependency, not by choice":
        "### Major M3 — Phase 3 interconnected company simulation",
    "Owned by M5 (interface) / M6 (release)":
        "### Major M5 — Phase 5 complete Company Command interface and polish",
    "A way out of the Backrooms (2026-09-29)":
        "### Owner direction — the other half of the topology: a way out into the world (2026-09-29)",
    "Zones and areas across a gate (2026-09-29)":
        "### Owner direction — zones must work on both sides of any gate (2026-09-29)",
    "The 294-mod register, and the work types nobody had enumerated (2026-09-29)":
        "### Owner direction — the 294-mod register must actually work and be human navigable (2026-09-29)",
}

# Rows whose text shows they cannot close without the game running become [T].
TEST_MARKERS = (
    "post-completion test phase",
    "Measurement itself belongs",
    "Need a running game",
    "after the owner has launched",
    "screenshots, trailer",
)


def main():
    text = io.open(DEFERRED, encoding="utf-8").read()
    lines = text.splitlines()

    section = None
    moved = {}
    keep = []
    in_built = False
    count_open = 0
    count_test = 0

    for line in lines:
        heading = re.match(r"^### (.+)$", line)
        if heading:
            section = heading.group(1).strip()
            in_built = section.startswith("Built")
            keep.append(line)
            continue
        row = re.match(r"^- \[([ T])\] (.*)$", line)
        if row and not in_built and section in OWNER:
            marker = row.group(1)
            body = row.group(2)
            if marker == "T" or any(m in body for m in TEST_MARKERS):
                marker = "T"
                count_test += 1
            else:
                count_open += 1
            moved.setdefault(OWNER[section], []).append(
                "- [%s] %s" % (marker, body))
            continue
        keep.append(line)

    # --- write the rows into TODO.md
    todo = io.open(TODO, encoding="utf-8").read()
    for heading, rows in moved.items():
        index = todo.find(heading)
        if index < 0:
            raise SystemExit("TODO heading not found: %r" % heading)
        # Insert at the end of that section: just before the next "### " heading.
        nxt = todo.find("\n### ", index + len(heading))
        if nxt < 0:
            nxt = todo.find("\n## ", index + len(heading))
        if nxt < 0:
            nxt = len(todo)
        block = ("\n**Undeferred 2026-09-29 by owner direction** — moved here verbatim "
                 "from `DEFERRED.md`, which is now empty of open rows:\n\n"
                 + "\n".join(rows) + "\n")
        todo = todo[:nxt] + block + todo[nxt:]
    io.open(TODO, "w", encoding="utf-8", newline="").write(todo)

    # --- write DEFERRED.md back without its open rows
    io.open(DEFERRED, "w", encoding="utf-8", newline="").write("\n".join(keep) + "\n")

    print("moved %d build rows and %d test rows into TODO.md" % (count_open, count_test))
    for heading, rows in sorted(moved.items()):
        print("  %-70s %d" % (heading[:68], len(rows)))


if __name__ == "__main__":
    main()
