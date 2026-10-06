# -*- coding: utf-8 -*-
"""Assert the gate's aura and its looping cues cannot rot into the failures they were built to avoid.

The properties this exists for
------------------------------
Owner, 2026-10-06: *"maybe have the auro for the gat be gate sensitive change color to the state of
the gate and like strobe on charge up callibation and activation and shit like star trek warp
core"*, and *"ramp up and down and rev"*. Then, when the cheap version was offered: *"not cheap
fucker do it quality"*.

Five things have to stay true, and **no compiler and no checker will say so**:

  * **A LOOP THAT IS NOT MAINTAINED MUST DIE BY ITSELF.** The sustainer is created with
    `MaintenanceType.PerTick`, so RimWorld ends it the moment it stops being maintained. Change that
    to any other maintenance type and a destroyed gate keeps humming until the map unloads -- the
    exact failure the one-shot path refuses sustained defs to avoid.

  * **THE RECONCILE MUST RUN OUTSIDE `TickGate`'s EARLY RETURNS.** `TickGate` returns immediately
    when the gate is unspawned or in a portal-owner fault. Reconciling inside it means a gate that
    faults mid-ramp keeps its loop for ever, which is the leak the whole reconcile shape exists to
    prevent.

  * **THE ONE-SHOT PATH MUST KEEP REFUSING SUSTAINED DEFS.** `Usable` rejecting `sustain` is what
    makes it impossible to start a loop through a code path that has nothing to stop it.

  * **NOTHING ABOUT THE LOOP IS SAVED.** A sound is not part of a save. The reconcile re-derives it
    from state, so a reload mid-ramp restarts the loop with no scribed field -- and a scribed
    sustainer reference would be a null nobody expects.

  * **THE AURA MUST NOT MAKE THE NETWORK WALK FASTER, AND MUST NOT WRITE WHEN NOTHING CHANGED.**
    `IsLiveGate` walks every edge in the portal network, which is why the appearance refresh is
    throttled to 250 ticks. The aura samples sixteen times more often and must read a cached answer
    instead. And `CompGlower.UpdateLit` recomputes a map's glow grid, so it may only be called when
    the resolved value actually differs from the last one pushed.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError("unbalanced body for %r" % signature)


audio = strip_comments(read(os.path.join(SRC, "Audio", "RimroomsAudio.cs")))
loops = strip_comments(read(os.path.join(SRC, "Gate", "GateLoopAudio.cs")))
gate = strip_comments(read(os.path.join(SRC, "Gate", "CompRimroomsGate.cs")))
aura = strip_comments(read(os.path.join(SRC, "Portals", "GateAura.cs")))
emergence = strip_comments(read(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs")))

print("")
print("proof: the gate's aura and its loops cannot rot into the failures they avoid")
print("")

# ------------------------------------------------------------------ 1. the loop dies by itself
print("1. a loop that stops being maintained ends on its own")
starter = body_of(audio, "public static Sustainer TryStartSustainer(")
check("the sustainer is created PerTick",
      "MaintenanceType.PerTick" in starter,
      "-- any other maintenance type and a destroyed gate hums until the map unloads")
check("and the caller maintains it every tick",
      "loopSustainer.Maintain()" in loops,
      "-- PerTick without Maintain is a sound that never starts properly")

# --------------------------------------------------- 2. the reconcile sees the states that matter
print("")
print("2. the reconcile runs where it can decide nothing should play")
comp_tick = body_of(gate, "public override void CompTick()")
check("CompTick calls the loop reconcile",
      "TickGateLoops()" in comp_tick)
check("and TickGate does NOT, so its early returns cannot strand a loop",
      "TickGateLoops" not in body_of(gate, "private void TickGate()"),
      "-- TickGate returns on unspawned and on portal-owner fault; a loop reconciled inside it "
      "would keep running through exactly those states")
desired = body_of(loops, "private string DesiredLoopCue")
check("a faulted gate asks for silence rather than a drone",
      "IsEmergency" in desired and "IsAwaitingRecovery" in desired and "return null" in desired,
      "-- a steady hum under an emergency says the machine is fine")
check("and an unspawned or destroyed gate asks for silence",
      "!parent.Spawned" in desired and "parent.Destroyed" in desired)

# ------------------------------------------------- 3. the one-shot path still refuses a sustainer
print("")
print("3. the one-shot path still refuses a sustained def")
usable = body_of(audio, "private static SoundDef Usable(")
check("Usable rejects sustain",
      "definition.sustain" in usable,
      "-- this is what makes it impossible to start a loop on a path with nothing to stop it")
check("and the sustainer path REQUIRES it, which is the mirror image",
      "!definition.sustain" in starter,
      "-- a one-shot started as a loop would never end")

# ------------------------------------------------------------------ 4. nothing about it is saved
print("")
print("4. no part of the loop is written to a save")
check("the sustainer and its cue id are never scribed",
      "loopSustainer" not in gate.replace("TickGateLoops", "") or "Scribe" not in loops,
      "-- a sound is not part of a save, and a scribed sustainer is a null nobody expects")
check("Scribe appears nowhere in the loop file", "Scribe_" not in loops)

# ------------------------------------------------------------- 5. the aura is cheap and quiet
print("")
print("5. the aura does not make the network walk faster, and does not write when idle")
apply_aura = body_of(aura, "private void ApplyAura()")
# **THE FIRST VERSION OF THIS CLAIM WAS SATISFIED BY THE NAMES BEING PRESENT**, and a plant proved
# it: replacing the guard with `if (false && Mathf.Approximately(radius, auraLastRadius) ...)` left
# every identifier exactly where it was, in the same order, and the claim passed while the guard
# was dead. Testing for a mention rather than for the thing itself is the defect this battery has
# now met more times than any other. The whole guard is matched, whitespace-insensitively, and it
# must be followed by the return it exists to perform.
squeezed = re.sub(r"\s+", "", apply_aura)
check("it compares against the last push and RETURNS, rather than merely naming the fields",
      "if(auraPushed&&Mathf.Approximately(radius,auraLastRadius)"
      "&&SameColor(colour,auraLastColor)){return;}" in squeezed,
      "-- UpdateLit recomputes a map's glow grid; calling it every sample is four rebuilds a "
      "second per gate whether or not anything moved")
check("and the comparison still happens before the write",
      apply_aura.index("auraLastRadius") < apply_aura.index("UpdateLit"))
check("and the radius is quantised, so a hundredth of a cell is not a change",
      "Mathf.Round" in apply_aura)
resolve = body_of(aura, "private void ResolveAura(")
check("the fast path reads the CACHED live answer, never IsLiveGate",
      "auraLive" in resolve and "IsLiveGate" not in resolve,
      "-- IsLiveGate walks every edge in the portal network, which is why the appearance refresh "
      "is throttled to 250 ticks in the first place")
check("the slow pass is what caches it",
      "auraLive = live" in emergence)
check("and the fast tick branch calls only ApplyAura",
      "IsHashIntervalTick(AuraInterval" in emergence and
      "{ ApplyAura(); }" in emergence)

# ------------------------------------------------------- 6. a live gate is deliberately unchanged
print("")
print("6. a gate that is open and well looks exactly as it did")
check("the faulted states are tested FIRST, then live returns untouched",
      resolve.index("IsAwaitingRecovery") < resolve.index("if (auraLive) { return; }") and
      resolve.index("IsEmergency") < resolve.index("if (auraLive) { return; }"),
      "-- checking the pleasant state first would hide a fault behind it")
check("and the live branch sets no new colour or radius of its own",
      "if (auraLive) { return; }" in resolve,
      "-- an existing colony must see no difference in the state it spends most of its time in")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the loops end themselves, the aura stays cheap, and a live gate is unchanged")
