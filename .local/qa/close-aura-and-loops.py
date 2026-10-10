# -*- coding: utf-8 -*-
"""Close the five gate presentation rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ('**"and maybe have the auro for the gat be gate sensitive change color to the state of the gate"**',
     " -- **BUILT 0.13.0-dev, AND IT COST NO ART AT ALL.** Five states, each with its own colour "
     "and its own radius: **designated idle** a dim blue at 2.5 cells, **spinning up** climbing "
     "from that blue toward near-white as the work completes, **live** the existing blue at the "
     "existing radius, **emergency** amber, **awaiting recovery** red. "
     "**THE HARD PART WAS NOT THE COLOUR, IT WAS THE COST.** `RefreshGateAppearance` is throttled "
     "to 250 ticks because `IsLiveGate` **walks every edge in the portal network**, and an aura "
     "needs roughly four samples a second -- so running the existing refresh that fast would have "
     "performed that walk **sixteen times more often, on every door in the colony**, to animate at "
     "most three gates. The expensive answer is cached by the slow pass; only *what colour is this "
     "right now* runs fast. **And it writes to the glow grid only when the value changed**: "
     "`CompGlower.UpdateLit` recomputes a map's glow contribution, the radius is quantised so a "
     "hundredth of a cell is not a change, and in the steady states the aura settles and stops "
     "writing entirely. "
     "**A LIVE GATE LOOKS EXACTLY AS IT DID** -- the faulted states are tested first and the live "
     "branch returns untouched, so the state a colony spends most of its life in is unchanged and "
     "this cannot read as a regression to somebody who liked it. **A natural gate gets no state "
     "behaviour either**, which is the same distinction the owner drew about the frame."),

    ('**"like strobe on charge up callibation and activation and shit like star trek warp core"**',
     " -- **BUILT 0.13.0-dev, AND THE RATE IS WHAT CARRIES IT.** The pulse is a **triangle wave, "
     "not a square one**: a hard on/off reads as a hazard light, which is the opposite meaning. "
     "Through spin-up its **period falls from 96 ticks to 20** as the work completes, so the gate "
     "visibly winds up rather than blinking at a fixed rate -- that rising rate is the warp-core "
     "feel the owner asked for. Emergency pulses slowly at 80 ticks; awaiting recovery pulses at "
     "36, faster and red, because it is the one state nobody is coming back from on their own. "
     "**The activation flash is deliberately NOT a third copy**: the moment already has the "
     "six-frame burst and `RR_GateActivate`, and the spin-up pulse reaches its maximum at "
     "completion and settles into live, which reads as the flash resolving."),

    ('**"and things like the gates activating animations and charge up and stuff"**',
     " -- **BUILT 0.13.0-dev. All three sequences are drawn**: eight charge frames looping through "
     "spin-up, a six-frame activation burst that plays **once**, and eight live frames looping "
     "while a connection is open. Six ticks a frame, ten frames a second. "
     "**The burst is transient and deliberately not saved** -- a one-off flash replaying every "
     "time somebody loads a game would announce an event that is not happening. It is triggered "
     "from the same event as the activation cue, so a flash with no sound or a sound with no flash "
     "is not reachable. **One square sheet per sequence**, stretched over whatever run it is drawn "
     "on: four footprints times three facings times eight frames would have been ninety-six files "
     "for one animation, and every future footprint multiplies it."),

    ('**"ramp up and down and rev"**',
     " -- **BUILT 0.13.0-dev, INCLUDING THE TWO LOOPS, AND THE LOOPS ARE THE PART THAT COULD HAVE "
     "GONE WRONG.** The five one-shots fire on real events: ramp-up on spin-up starting, calibrate "
     "on the three interior quarter crossings, activate on the ramp completing, ramp-down on a "
     "connection closing or a ramp stopped on purpose, emergency on a gate fault. "
     "**THE LOOPS ARE RECONCILED EVERY TICK, NEVER STARTED AND STOPPED BY EVENT.** The obvious "
     "shape leaks: completion, abort, lapse, power loss, the operator walking away, a fault and a "
     "reload would each have to remember to stop the sound, and the first one anybody forgets is "
     "**a hum that plays until the map unloads**. Nothing starts or stops on an event -- every "
     "tick asks what should be playing and makes reality match, which is self-healing in both "
     "directions and restarts the loop after a reload with **nothing scribed at all**. "
     "**And the sustainer ends itself.** `MaintenanceType.PerTick` means RimWorld stops it the "
     "moment it stops being maintained, so a destroyed gate goes quiet on its own -- *forgetting to "
     "stop one is not a failure mode here*. **The reconcile is called from `CompTick` outside "
     "`TickGate`'s early returns**, because `TickGate` returns on unspawned and on portal-owner "
     "fault and a loop reconciled inside it would run through exactly those states. A faulted gate "
     "asks for silence rather than droning under its own emergency. "
     "**`proof-gate-aura-and-loops` is proof 64 and `plant-gate-aura-and-loops` is suite 43, 8 of "
     "8 caught** -- and the plants found two weak claims before they found anything else: one plant "
     "was aimed at a docstring and tested nothing, and one claim of mine was satisfied by the field "
     "names merely being present while the guard was dead."),

    ("**The one thing the cues have to get right, recorded so it is not lost between the brief and "
     "the build:**",
     " -- **DELIVERED AND VERIFIED 0.13.0-dev.** Every one of the seventeen cues was measured "
     "rather than trusted: **48 kHz, mono, 16-bit**, every duration inside the range the brief "
     "asked for. The contrast the row names is in the delivered audio -- the ramp-up climbs and "
     "holds without resolving, the ramp-down descends into a latch and silence -- so a player can "
     "tell whether a gate is becoming dangerous or becoming safe without reading a word."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if (l.lstrip().startswith("- [ ] ") or l.lstrip().startswith("- [~] ")) and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:58], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
