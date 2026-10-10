# -*- coding: utf-8 -*-
"""Close the runtime-integration note left for this agent by the asset author."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

KEY = "**Note to Claude — runtime integration:**"
EVIDENCE = (
    " -- **BUILT 0.13.0-dev, and the one detail this note adds is the rate.** The live sequence was "
    "already drawn after the burst and already shared one set across every footprint; what it did "
    "**not** do was run slower. It does now: the charge cycle is six ticks a frame and the live "
    "cycle is ten, so a ramp looks busy and an open connection looks settled. Running both at one "
    "rate made a finished gate look like it was still straining. "
    "**The burst cannot overlap the live cycle**, because the overlay resolves worst-state-first: "
    "while the burst is inside its own six-frame window it wins, and the instant it passes its last "
    "frame it answers null and clears itself rather than restarting. **And it is transient on "
    "purpose** -- nothing about it is scribed, so a save reloaded mid-cycle shows no burst, which is "
    "correct: a one-off flash replaying on every load would announce an event that is not happening."
)


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [ ] ") and KEY in l]
    if len(hits) != 1:
        print("REFUSED: matched %d open row(s)" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), EVIDENCE)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed the runtime-integration note")
    return 0


if __name__ == "__main__":
    sys.exit(main())
