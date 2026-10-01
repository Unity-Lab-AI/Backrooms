# -*- coding: utf-8 -*-
"""Plant every way this integration could quietly stop being an integration.

Plant a fault, run the proof, require failure, restore. Verified writes. Clean run first.

The plants that matter most are not the obvious ones. They are the three that would leave the
package **compiling, passing every checker, and silently doing nothing**: a bridge that reports
available when their mod is absent, an attach that goes on the def instead of the instance, and a
dial that is never called because only one end of the route was wired.
"""
import io
import os
import subprocess
import sys
import time

PROOF = ".local/register/proof-stargate-bridge.py"
SRC = "src/RimroomsAsyncIndustries"
BRIDGE = SRC + "/Portals/StargateBridge.cs"
EMERGENCE = SRC + "/Portals/CompRimroomsEmergence.cs"
CSPROJ = SRC + "/RimroomsAsyncIndustries.csproj"

# (label, path, old, new)

# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
_RR_SENTINEL = os.path.join(".local", "register", ".plant-in-progress")


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


PLANTS = [
    # ------------------------------------------------- the integration stops being one
    ("THE FAR END IS NEVER WIRED, so a route has a gate on one side only", EMERGENCE,
     "StargateBridge.Attach(far, true);", "// StargateBridge.Attach(far, true);"),

    ("WE STOP DIALLING, so the player is back to doing it by hand", EMERGENCE,
     "if (!StargateBridge.Dial(near, far.Map, 0))",
     "if (false && !StargateBridge.Dial(near, far.Map, 0))"),

    ("the near end is never wired", EMERGENCE,
     "StargateBridge.Attach(near, true);", "// StargateBridge.Attach(near, true);"),

    ("the far anchor is searched for instead of read off the edge", EMERGENCE,
     "private ThingWithComps FarAnchor(PortalConnectionRecord edge)",
     "private ThingWithComps FarAnchorUnused(PortalConnectionRecord edge)"),

    ("a merely MARKED door becomes a stargate, registering a place that does not exist",
     EMERGENCE, "if (edge == null || !IsLiveGate) { return; }", "if (edge == null) { return; }"),

    ("the wormhole is refreshed somewhere other than where the glow is", EMERGENCE,
     "            RefreshGateAppearance();\n            // Same tick, same question. If the "
     "appearance and the wormhole were refreshed from\n            // different places they "
     "could disagree about whether this is a gate.\n            RefreshStargate();",
     "            RefreshGateAppearance();"),

    ("a receiving end is dialled, fighting their one-way rule", EMERGENCE,
     "StargateBridge.IsReceiving(near)", "false"),

    ("a hibernating gate is dialled, fighting their one-gate-per-map rule", EMERGENCE,
     "if (StargateBridge.IsHibernating(near))", "if (false)"),

    # EVERY SILENT REFUSAL MUST NAME ITSELF. The wormhole took a whole launch to diagnose
    # because these paths returned without a word and the owner's log held nothing at all.
    ("A REFUSAL GOES SILENT AGAIN, so the next launch cannot say why", EMERGENCE,
     "private void ReportGateState(string reason)",
     "private void ReportGateStateUnused(string reason)"),

    ("the far end being a non-door stops being reported", EMERGENCE,
     "the far end of this route is not a door",
     "the far end of this route is not a doorway"),

    # ------------------------------------------------------- the line around their mod
    ("THE BRIDGE REPORTS AVAILABLE WITH THEIR MOD ABSENT, which crashes a Core-only colony",
     BRIDGE, "return compType != null && donorProps != null && openMethod != null;",
     "return true;"),

    ("Attach stops refusing when the mod is absent", BRIDGE,
     "if (!Available || door == null) { return false; }\n            if (On(door) != null)",
     "if (door == null) { return false; }\n            if (On(door) != null)"),

    # Retargeted when the gate started taking SIZED properties: the "constructed, not borrowed"
    # risk moved to the fallback, which is now the only place their own instance is used.
    ("their properties are CONSTRUCTED instead of borrowed, so our copy goes stale", BRIDGE,
     "cached = built ?? donorProps;",
     "cached = built ?? new CompProperties_Stargate();"),

    ("the component is added to the DEF, so every door in every colony becomes a gate", BRIDGE,
     "door.AllComps.Add(gate);", "door.def.comps.Add(donorProps);"),

    ("a reflection WRITE appears in the one file most tempted to use one", BRIDGE,
     "            openMethod = compType.GetMethod(\"OpenStargateDelayed\");",
     "            compType.GetField(\"IsHibernating\").SetValue(null, false);\n"
     "            openMethod = compType.GetMethod(\"OpenStargateDelayed\");"),

    ("a PRIVATE field of theirs is read", BRIDGE,
     "activeField = compType.GetField(\"StargateIsActive\");",
     "activeField = compType.GetField(\"_sendBuffer\", BindingFlags.NonPublic);"),

    ("Harmony appears", BRIDGE,
     "using System.Reflection;", "using System.Reflection;\nusing HarmonyLib;"),

    ("THE DOC COMMENT EXPLAINING THE RULE IS DELETED to satisfy a grep", BRIDGE,
     "No Harmony, no detour, no `SetValue`, no `BindingFlags.NonPublic`.", ""),

    ("the build grows a hard reference to their assembly", CSPROJ,
     "</Project>",
     "  <ItemGroup><Reference Include=\"Stargates\" /></ItemGroup>\n</Project>"),

    ("their type is looked up with a bare Type.GetType that cannot see mod assemblies", BRIDGE,
     "compType = GenTypes.GetTypeInAnyAssembly(CompTypeName);",
     "compType = Type.GetType(CompTypeName);"),

    # -------------------------------------------------------- the effects stop being sized
    ("THE GATE GOES BACK TO THEIR UNSIZED PROPERTIES, so a 1x1 door gets a 7x7 kawoosh", BRIDGE,
     "gate.Initialize(SizedProps(door.def, naturalGate));", "gate.Initialize(donorProps);"),

    ("the puddle stops being read off the door's footprint", BRIDGE,
     "int width = Math.Max(1, Math.Max(door.size.x, door.size.z));", "int width = 5;"),

    ("THE RATIO LEAVES THE BAND THEIR OWN GATES SIT IN", BRIDGE,
     "float puddle = width * 1.6f;", "float puddle = width * 4f;"),

    ("the vortex gets deeper than a doorway", BRIDGE,
     '.Append(",0,1)</li>");', '.Append(",0,1)</li>").Append("<li>(0,0,2)</li>");'),

    ("the vortex stops spanning the door's width", BRIDGE,
     "for (int offset = -half; naturalGate ? false : offset <= width - 1 - half; offset++)",
     "for (int offset = -half; naturalGate ? false : offset <= -half; offset++)"),

    ("an iris is offered on a door with no opening to cover", BRIDGE,
     'Append(width >= 2 ? "true" : "false")', 'Append("true")'),

    ("the properties stop being built by Core's loader", BRIDGE,
     "return DirectXmlToObject.ObjectFromXml<CompProperties>(document.DocumentElement, false);",
     "return donorProps;"),

    ("the texture paths stop following their gate", BRIDGE,
     "FieldInfo field = donorProps.GetType().GetField(fieldName);",
     "FieldInfo field = null;"),

    ("A SIZING FAILURE BREAKS THE ROUTE instead of just looking wrong", BRIDGE,
     "cached = built ?? donorProps;", "cached = built;"),

    ("the properties are rebuilt for every door instead of cached per def", BRIDGE,
     "if (sizedProps.TryGetValue(key, out cached)) { return cached; }", ""),

    # ------------------------------------------- a natural gate must never carry a vortex
    ("A NATURAL GATE GETS A VORTEX, detonating its own doorway every re-dial", BRIDGE,
     "for (int offset = -half; naturalGate ? false : offset <= width - 1 - half; offset++)",
     "for (int offset = -half; offset <= width - 1 - half; offset++)"),

    ("the natural and machine kinds share one cached result", BRIDGE,
     'string key = door.defName + (naturalGate ? "|natural" : "|machine");',
     "string key = door.defName;"),

    ("a natural route is attached as a machine gate", EMERGENCE,
     "StargateBridge.Attach(near, true);", "StargateBridge.Attach(near, false);"),

    ("the pocket-map half of the address conversion is dropped", BRIDGE,
     "destination.IsPocketMap\n                    ? new PlanetTile(destination.Index) : destination.Tile",
     "destination.Tile"),
]


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


def run(target):
    return subprocess.call([sys.executable, target],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


print("clean run first, so a plant that 'fails' cannot be a pre-existing fault")
code = run(PROOF)
print("  %-46s exit %d" % (PROOF, code))
if code != 0:
    print("ABORTED: the proof does not pass clean")
    sys.exit(2)
print("")

caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    hits = original.count(old)
    if hits != 1:
        print("PLANT SETUP BROKEN (%d matches, need exactly 1): %s" % (hits, label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = run(PROOF)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    if io.open(path, encoding="utf-8").read() != original:
        sys.stderr.write("FATAL: %s not restored -- CHECK BY HAND\n" % path)
        sys.exit(3)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s (exit %d)" % ("CAUGHT " if ok else "MISSED!", label, code))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
