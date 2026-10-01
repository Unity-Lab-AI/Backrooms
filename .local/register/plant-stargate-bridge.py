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
PLANTS = [
    # ------------------------------------------------- the integration stops being one
    ("THE FAR END IS NEVER WIRED, so a route has a gate on one side only", EMERGENCE,
     "StargateBridge.Attach(far);", "// StargateBridge.Attach(far);"),

    ("WE STOP DIALLING, so the player is back to doing it by hand", EMERGENCE,
     "StargateBridge.Dial(near, far.Map, 0);", "// StargateBridge.Dial(near, far.Map, 0);"),

    ("the near end is never wired", EMERGENCE,
     "StargateBridge.Attach(near);", "// StargateBridge.Attach(near);"),

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
     "if (StargateBridge.IsHibernating(near)) { return; }", ""),

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
     "gate.Initialize(SizedProps(door.def));", "gate.Initialize(donorProps);"),

    ("the puddle stops being read off the door's footprint", BRIDGE,
     "int width = Math.Max(1, Math.Max(door.size.x, door.size.z));", "int width = 5;"),

    ("THE RATIO LEAVES THE BAND THEIR OWN GATES SIT IN", BRIDGE,
     "float puddle = width * 1.6f;", "float puddle = width * 4f;"),

    ("the vortex gets deeper than a doorway", BRIDGE,
     '.Append(",0,1)</li>");', '.Append(",0,1)</li>").Append("<li>(0,0,2)</li>");'),

    ("the vortex stops spanning the door's width", BRIDGE,
     "for (int offset = -half; offset <= width - 1 - half; offset++)",
     "for (int offset = -half; offset <= -half; offset++)"),

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
     "if (sizedProps.TryGetValue(door, out cached)) { return cached; }", ""),

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
                           stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)


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
    write_verified(path, original.replace(old, new, 1))
    code = run(PROOF)
    write_verified(path, original)
    if io.open(path, encoding="utf-8").read() != original:
        sys.stderr.write("FATAL: %s not restored -- CHECK BY HAND\n" % path)
        sys.exit(3)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s (exit %d)" % ("CAUGHT " if ok else "MISSED!", label, code))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
