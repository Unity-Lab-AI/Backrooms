# -*- coding: utf-8 -*-
"""Move every row that needs a launch out of `[ ]`, so open means doable.

**Owner, 2026-10-05, verbatim:** *"clean up the todo properly and tell me straight whats left in
English"*.

Ten rows were marked `[ ]`. **Eight of them say in their own text that they cannot be done without
the game running.** A pending marker on a row nobody can pick up is the same lie as a heading with
no rows under it: it inflates the list and it makes the honest question -- *what can be done now* --
unanswerable from the file.

`[T]` already exists for exactly this and already gates nothing. Each move below is justified by
the row's own words, quoted, not by a judgement of mine.

LAW #0: every original word stays. Only the status letter changes, plus appended evidence.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

MOVES = [
    ("they need to properly spawn in with starting goods",
     "**MOVED TO THE TEST PHASE 0.12.99-dev.** The row says its own next step: it needs a "
     "`Player.log` from an owner launch to see which of the eliminated causes is real. **The "
     "measurement work is done and recorded** -- a 9,216-cell sweep, four candidate causes "
     "eliminated against the installed game -- and no fix was written on a hunch. **What is left "
     "is a launch**, so it does not belong in the pending list where it reads as something "
     "somebody could pick up today."),

    ("my preparecarfully mod food did not appear",
     "**MOVED TO THE TEST PHASE 0.12.99-dev.** The row already names its blocker in its own text: "
     "*it waits on the same `Player.log`* as the starting-goods row. A row that names a launch as "
     "its blocker is a test-phase row."),

    ("idk maybe we will use a playwrite thing so you can click through steam",
     "**CLOSED AS A DECISION WITH A TRIGGER 0.12.99-dev.** Owner, asked directly: *\"Not yet -- "
     "ask again when the mod is ready to publish\"*. **Nothing in this project touches Steam** -- "
     "no Playwright, no account access, no page, no collection. **And the alternative this row "
     "itself named is built:** *\"The alternative is a prepared write-up the owner pastes, which "
     "is far less work for whoever is not doing the clicking\"* -- `docs/WORKSHOP_COPY.md`, both "
     "write-ups, ready to paste. **The question gets asked again at publication readiness.**"),

    ("Resolve duplicate Defs/patch collisions in the exact 294 profile",
     "**MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *\"Structurally requires a "
     "launch with the 294 profile loaded, which only the owner does, through RimSort.\"* A "
     "collision is a thing two mods do to each other at load; it cannot be found by reading."),

    ("Add a user-facing compatibility report with tested order",
     "**MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *\"Cannot honestly state a "
     "tested order before anything has been tested.\"* D1 forbids announcing compatibility before "
     "validation, so writing this report now would be the exact claim the rule exists to stop."),

    ("Slideshow integration review, additional menu images per shipped scenario",
     "**MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *\"Open, and it needs a "
     "launch: the integration review itself -- how the slides read behind the menu buttons, and "
     "whether 30 s dwell and 2 s crossfade feel right -- cannot be judged from here.\"*"),

    ("Validation sweep, invalid-state matrix, balance, release report, packaging.",
     "**MOVED TO THE TEST PHASE 0.12.99-dev. Its two closable halves are closed and the rest is a "
     "launch.** The row's own split says the validation sweep and packaging halves are M6a; **both "
     "closed in this batch as their own rows** -- nine instrumented subjects, and the release "
     "ritual written into `PUBLISHING.md`. What the row still names is the **invalid-state matrix, "
     "balance and release report**, which are M6b, and its own text says why: *\"Balance in "
     "particular cannot be claimed: nothing in this mod has ever been played.\"*"),

    ("to the extent we want normal and really want the creepy insane looks and feel",
     "**MOVED TO THE TEST PHASE 0.12.99-dev, on the row's own words:** *\"Whether it lands is a "
     "play question and belongs to the post-completion test phase.\"* The mechanism is built and "
     "measured -- the look is a function of depth across five bands, and the architecture's "
     "agreement with itself falls from 89.4% to 36.4% by depth. **Whether that feels right is a "
     "judgement only a launch can make.**"),
]

CLOSE = {"idk maybe we will use a playwrite thing so you can click through steam"}


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    missed = []
    done = 0
    for phrase, evidence in MOVES:
        hits = [i for i, line in enumerate(lines)
                if line.lstrip().startswith(("- [ ] ", "- [~] ")) and phrase in line]
        if len(hits) != 1:
            missed.append((phrase, len(hits)))
            continue
        index = hits[0]
        raw = lines[index]
        lead = raw[:len(raw) - len(raw.lstrip())]
        letter = "x" if phrase in CLOSE else "T"
        lines[index] = "%s- [%s] %s -- %s" % (lead, letter, raw.lstrip()[6:].rstrip(), evidence)
        done += 1
    if missed:
        for phrase, count in missed:
            print("NOT MOVED (%d matches): %s" % (count, phrase[:70]))
        print("refusing to write a partial batch")
        return 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("moved %d row(s)" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
