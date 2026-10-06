# -*- coding: utf-8 -*-
"""Plant the failures proof-gate-aura-and-loops.py exists to catch, and require it to catch them.

A proof that has never failed is a rumour. Each fault below is the realistic shape of the mistake,
not a token edit: a maintenance type changed to the obvious-looking alternative, a reconcile moved
into the method it looks like it belongs in, a cheap comparison dropped because it reads as
redundant, and a state check reordered so the pleasant answer wins.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

PROOF = [".local/register/proof-gate-aura-and-loops.py"]

SRC = "src/RimroomsAsyncIndustries"
AUDIO = SRC + "/Audio/RimroomsAudio.cs"
LOOPS = SRC + "/Gate/GateLoopAudio.cs"
GATE = SRC + "/Gate/CompRimroomsGate.cs"
AURA = SRC + "/Portals/GateAura.cs"
EMERGENCE = SRC + "/Portals/CompRimroomsEmergence.cs"

_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def read_bytes(path):
    return io.open(path, "rb").read()


def write_verified(path, data):
    """Bytes in, bytes out, verified. A byte-order mark is part of a file and must survive."""
    for _ in range(6):
        try:
            io.open(path, "wb").write(data)
            if read_bytes(path) == data:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND%s" % (path, chr(10)))
    sys.exit(3)


PLANTS = [
    # ---- the loop must die on its own ----------------------------------------------------
    # The single most plausible edit here: PerTick looks fussy beside a type that sounds like it
    # means the same thing, and the symptom only appears when a gate is destroyed mid-ramp.
    # **RE-AIMED: the first version hit the docstring.** `MaintenanceType.PerTick` appears in the
    # explanation above the method as well as in the call, and the proof strips comments before
    # reading -- so the plant changed prose, the code was untouched, and the proof was right to
    # pass. A plant aimed at a comment tests nothing. This one is the call itself.
    ("THE SUSTAINER STOPS BEING SELF-TERMINATING, so a destroyed gate hums until the map unloads",
     AUDIO, "new TargetInfo(cell, map), MaintenanceType.PerTick",
     "new TargetInfo(cell, map), MaintenanceType.PerFrame", 1),

    ("the caller stops maintaining it, which is the other half of the same contract",
     LOOPS, "loopSustainer.Maintain();", "loopCueId = loopCueId;", 1),

    # ---- the reconcile must see the dead states ------------------------------------------
    # Moving it inside TickGate is the tidy-looking change: everything else gate-ticky lives there.
    # It is also what makes a faulted gate keep its loop for ever.
    ("THE RECONCILE MOVES INSIDE TickGate, behind the early returns it exists to survive",
     GATE, "            TickGateLoops();", "            // TickGateLoops();", 1),

    ("a faulted gate stops asking for silence and drones under its own emergency",
     LOOPS, "if (IsEmergency || IsAwaitingRecovery) { return null; }",
     "if (false) { return null; }", 1),

    # ---- the one-shot path must keep refusing a sustainer ---------------------------------
    ("THE ONE-SHOT PATH ADMITS A SUSTAINED DEF, so a loop can start where nothing can stop it",
     AUDIO, "definition.sustain ||", "false ||", 1),

    # ---- the aura must stay cheap --------------------------------------------------------
    # Dropping the comparison reads as removing a redundant guard. It silently turns four glow-grid
    # rebuilds a second per gate into the normal case.
    ("THE AURA WRITES EVERY SAMPLE, rebuilding a map's glow grid four times a second per gate",
     AURA, "if (auraPushed && Mathf.Approximately(radius, auraLastRadius)",
     "if (false && Mathf.Approximately(radius, auraLastRadius)", 1),

    ("the slow pass stops caching the live answer, so the fast path has nothing to read",
     EMERGENCE, "auraLive = live;", "auraLive = auraLive;", 1),

    # ---- a live gate must stay unchanged -------------------------------------------------
    # Reordering so the pleasant state wins is the classic: it reads as an optimisation and it
    # hides a fault behind a working connection.
    ("THE LIVE STATE IS TESTED BEFORE THE FAULTS, hiding an emergency behind an open connection",
     AURA, "            if (gate.IsAwaitingRecovery)",
     "            if (auraLive) { return; }\n            if (gate.IsAwaitingRecovery)", 1),
]

caught = 0
attempted = 0
for label, path, old, new, want in PLANTS:
    attempted += 1
    original = read_bytes(path)
    needle = old.encode("utf-8")
    if original.count(needle) < 1:
        print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:55], label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(needle, new.encode("utf-8"), 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable] + PROOF,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code == 1
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted 1)" % ("CAUGHT " if ok else "MISSED!", label, code))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
