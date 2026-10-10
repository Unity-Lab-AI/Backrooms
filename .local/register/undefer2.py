"""Second pass: the three `##`-level sections the first pass did not match, plus the
post-completion phase row. Same rule -- every row carried across byte-for-byte."""

import io
import re

DEFERRED = "docs/DEFERRED.md"
TODO = "docs/TODO.md"

OWNER = {
    "A way out of the Backrooms (2026-09-29)":
        "### Owner direction — the other half of the topology: a way out into the world (2026-09-29)",
    "Zones and areas across a gate (2026-09-29)":
        "### Owner direction — zones must work on both sides of any gate (2026-09-29)",
    "The 294-mod register, and the work types nobody had enumerated (2026-09-29)":
        "### Owner direction — the 294-mod register must actually work and be human navigable (2026-09-29)",
    "The post-completion test phase — `[T]`":
        "### Post-completion test phase — `[T]`, gates nothing",
}

TEST_MARKERS = (
    "post-completion test phase",
    "runtime acceptance",
    "whatever the owner actually uses",
)


def main():
    lines = io.open(DEFERRED, encoding="utf-8").read().splitlines()
    section = None
    moved = {}
    keep = []
    opened = tested = 0

    for line in lines:
        heading = re.match(r"^#{2,3} (.+)$", line)
        if heading:
            section = heading.group(1).strip()
            keep.append(line)
            continue
        row = re.match(r"^- \[([ T])\] (.*)$", line)
        if row and section in OWNER:
            marker, body = row.group(1), row.group(2)
            if marker == "T" or any(m in body for m in TEST_MARKERS):
                marker = "T"
                tested += 1
            else:
                opened += 1
            moved.setdefault(OWNER[section], []).append("- [%s] %s" % (marker, body))
            continue
        keep.append(line)

    todo = io.open(TODO, encoding="utf-8").read()
    for heading, rows in moved.items():
        index = todo.find(heading)
        if index < 0:
            raise SystemExit("TODO heading not found: %r" % heading)
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
    io.open(DEFERRED, "w", encoding="utf-8", newline="").write("\n".join(keep) + "\n")

    print("second pass: moved %d build rows and %d test rows" % (opened, tested))
    for heading, rows in sorted(moved.items()):
        print("  %-70s %d" % (heading[:68], len(rows)))


if __name__ == "__main__":
    main()
