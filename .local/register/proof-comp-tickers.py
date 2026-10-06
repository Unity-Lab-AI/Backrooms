# -*- coding: utf-8 -*-
"""A comp's tick override must match the ticker type of every def that carries it.

Owner, verbatim: *"the back wall door is not correctly blue, is not correctly a stargate portal to
the back rooms and does not cortrectly have the blue light glow. so wtf is going on here? are you
even useing the stargate capabilities to for connections to the backrooms and the map the pawns
start on?"*

READ FROM THE RUNNING GAME. The live session answered the second question on its own:

    mapCount                 2          the Backrooms coordinate GENERATED
    letters                  1          "Branch authorization received" -- only sent when
                                        SoloGroupOpening returns null, so every step succeeded
    cell (160,161)           Door       the emergence door, "Steel door (1x1)"
    its gizmos                          "Stop being a way home"  -> IsDesignated TRUE
                                        "Send somebody through"  -> a LIVE crossing exists
    exceptions                0

**The connection works.** Only the paint was missing.

THE DEFECT WAS ONE WORD WIDE. `RefreshGateAppearance()` -- glow radius, glow colour,
`CompGlower.UpdateLit`, `CompColorable.SetColor` -- had exactly one call site:
`CompTickRare()`. And `Verse.Thing.DoTick` dispatches on the def's ticker type:

    Normal -> Tick() and TickInterval(delta)     Rare -> TickRare()     Long -> TickLong()

**Core's `DoorBase` is `tickerType Normal`**, inherited by `Door` and `Autodoor`. A Normal ticker
never receives `TickRare()`, so `CompTickRare` never ran, so the only method that paints a gate
**has never executed on any door in any session.** Every other line was correct.

WHY THIS PROOF IS SHAPED THE WAY IT IS. The comp and the def live in different files and neither
mentions the other: the C# says "tick me rarely" and the XML says "this def ticks normally", and
nothing in either file is wrong on its own. So this resolves **our comps against the ticker type
of every def that actually carries them**, following `ParentName` through the installed game's own
data -- the same instinct as `proof-class-resolution.py`, which resolves our `Class` names against
the game's own types. **When the truth lives in the engine, ask the engine.**
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

failures = []


def check(claim, held, detail=""):
    print("  %s  %s%s" % ("HOLDS " if held else "FAILS!", claim,
                          "" if held else "\n          " + detail))
    if not held:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8-sig", errors="replace").read()


COMMENT = re.compile(r"<!--.*?-->", re.S)

# --------------------------------------------------------------------------- #
# 1. Every ThingDef the game and this package declare, with its ticker type.
# --------------------------------------------------------------------------- #

declared = {}      # key -> tickerType or None
parent_of = {}     # key -> parent key or None
abstract = {}      # "#Name" -> key


def index(paths):
    for path in paths:
        try:
            text = COMMENT.sub(" ", read(path))
        except Exception:                                      # noqa: BLE001 - unreadable, skipped
            continue
        for match in re.finditer(r"<ThingDef\b([^>]*)>(.*?)</ThingDef>", text, re.S):
            attrs, body = match.group(1), match.group(2)
            # `(?<![A-Za-z])` because `Name="` also matches inside `ParentName="`, which
            # indexed `<ThingDef ParentName="BuildingBase" Name="DoorBase">` under
            # `#BuildingBase` and dead-ended every door's parent chain.
            name = re.search(r'(?<![A-Za-z])Name="([^"]+)"', attrs)
            defname = re.search(r"<defName>([^<]+)</defName>", body)
            key = defname.group(1).strip() if defname else ("#" + name.group(1) if name else None)
            if key is None:
                continue
            ticker = re.search(r"<tickerType>([^<]+)</tickerType>", body)
            declared[key] = ticker.group(1).strip() if ticker else None
            parent = re.search(r'ParentName="([^"]+)"', attrs)
            parent_of[key] = "#" + parent.group(1) if parent else None
            if name:
                abstract["#" + name.group(1)] = key


index(glob.glob(os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml"), recursive=True))
index(glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True))


def ticker_of(key, seen=None):
    """The effective ticker type, following ParentName. Core's default is Never."""
    seen = seen or set()
    if key in seen or key not in declared:
        return None
    seen.add(key)
    if declared[key]:
        return declared[key]
    parent = parent_of.get(key)
    if parent is None:
        return "Never"
    return ticker_of(parent, seen)


print("")
print("A COMP THAT ASKS FOR THE WRONG TICK IS NEVER TICKED AT ALL")
print("=" * 78)
print("")

check("the installed game's ThingDefs were indexed",
      len(declared) > 1000,
      "-- %d found. Without them this proof verifies nothing, so it fails rather than passes"
      % len(declared))

check("and the ticker type resolves through ParentName",
      ticker_of("Door") == "Normal" and ticker_of("GlowPod") == "Rare",
      "-- Door resolved %r (want Normal, inherited from DoorBase) and GlowPod %r (want Rare). "
      "If the chain does not resolve, every claim below is vacuous"
      % (ticker_of("Door"), ticker_of("GlowPod")))

# --------------------------------------------------------------------------- #
# 2. Our comps, their tick overrides, and their CompProperties class.
# --------------------------------------------------------------------------- #

OVERRIDES = ("CompTickInterval", "CompTickRare", "CompTickLong", "CompTick")

comp_ticks = {}            # comp class -> set of overrides
props_to_comp = {}         # CompProperties class -> comp class

for folder, _, names in os.walk(SRC):
    if os.sep + "obj" in folder or os.sep + "bin" in folder:
        continue
    for name in names:
        if not name.endswith(".cs"):
            continue
        body = read(os.path.join(folder, name))
        for match in re.finditer(r"class\s+(\w+)\s*:\s*(?:[\w.]+\s*,\s*)*?ThingComp\b|"
                                 r"class\s+(\w+)\s*:\s*ThingComp\b", body):
            pass
        # CompProperties -> comp class, via the constructor Core requires.
        for match in re.finditer(r"class\s+(CompProperties_\w+)\s*:[^{]*\{(.*?)\n    \}", body, re.S):
            target = re.search(r"compClass\s*=\s*typeof\((\w+)\)", match.group(2))
            if target:
                props_to_comp[match.group(1)] = target.group(1)
        # Which comp classes override which tick.
        for match in re.finditer(r"class\s+(\w+)\s*:[^{]*ThingComp[^{]*\{", body):
            pass
        # **THIS PATTERN ONLY EVER MATCHED `public class X : ThingComp`**, so it was blind to every
        # comp declared `sealed` or `partial` -- which is most of them. It went unnoticed because
        # one comp happened to be declared plainly and that was enough to satisfy the
        # has-subjects claim. Making `CompRimroomsEmergence` partial at 0.13.0-dev removed that
        # one subject and the proof reported it had none at all, which is how the hole surfaced.
        # A proof that silently scans a fraction of its subjects is worse than one that scans none,
        # because it reports green either way.
        declarations = re.findall(
            r"public\s+(?:sealed\s+|partial\s+|abstract\s+)*class\s+(\w+)\s*:\s*ThingComp\b", body)
        for cls in declarations:
            segment = body.split("class " + cls, 1)[1]
            found = set()
            for override in OVERRIDES:
                if re.search(r"public\s+override\s+void\s+%s\s*\(" % override, segment):
                    found.add(override)
            if found:
                # **Unioned, not assigned.** A partial class is declared in more than one file and
                # its overrides may be split across them; assigning would let whichever file was
                # walked last decide what the class overrides.
                comp_ticks.setdefault(cls, set()).update(found)

print("")
print("     comps with a tick override: %s"
      % (", ".join("%s{%s}" % (k, ",".join(sorted(v))) for k, v in sorted(comp_ticks.items()))
         or "none"))

check("at least one of our comps overrides a tick, so this proof has subjects",
      len(comp_ticks) >= 1,
      "-- if nothing ticks, this proof is checking nothing and must say so")

# --------------------------------------------------------------------------- #
# 3. Which defs carry each CompProperties, from our Defs and our Patches.
# --------------------------------------------------------------------------- #

carriers = {}      # CompProperties simple name -> set of defNames

for path in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
    text = COMMENT.sub(" ", read(path))
    for match in re.finditer(r"<ThingDef\b[^>]*>(.*?)</ThingDef>", text, re.S):
        body = match.group(1)
        defname = re.search(r"<defName>([^<]+)</defName>", body)
        if not defname:
            continue
        for value in re.findall(r'Class="([^"]+)"', body):
            carriers.setdefault(value.split(".")[-1], set()).add(defname.group(1).strip())

for path in glob.glob(os.path.join(MOD, "Patches", "*.xml")):
    text = COMMENT.sub(" ", read(path))
    # Each PatchOperationAdd pairs an xpath naming defs with a value naming comp classes.
    for match in re.finditer(r"<xpath>([^<]+)</xpath>\s*<value>(.*?)</value>", text, re.S):
        targets = re.findall(r'defName="([^"]+)"', match.group(1))
        for value in re.findall(r'Class="([^"]+)"', match.group(2)):
            simple = value.split(".")[-1]
            for target in targets:
                carriers.setdefault(simple, set()).add(target)

print("")
print("WHAT EACH TICKING COMP IS ATTACHED TO, AND WHETHER THOSE DEFS ACTUALLY TICK THAT WAY")
print("-" * 78)

# A def name carrying another mod's prefix -- two to five capitals then an underscore, which is what
# `PH_DoorDouble` looks like and what most mods use. Ours are excluded by name: `RR_` is this
# package's and must always resolve.
FOREIGN_DEF = re.compile(r"^(?!RR_)[A-Z]{2,5}_[A-Za-z0-9_]+$")

# What each ticker type actually delivers, from Verse.Thing.DoTick.
DELIVERS = {
    "Normal": set(["CompTick", "CompTickInterval"]),
    "Rare": set(["CompTickRare"]),
    "Long": set(["CompTickLong"]),
    "Never": set(),
}

checked_any = False
for props, comp in sorted(props_to_comp.items()):
    overrides = comp_ticks.get(comp)
    if not overrides:
        continue
    defs = sorted(carriers.get(props, set()))
    check("%s is attached to at least one def" % props, bool(defs),
          "-- a ticking comp nothing carries is dead code, or the attachment was not found by "
          "this proof, and either way it must not pass silently")
    for defname in defs:
        ticker = ticker_of(defname)
        if ticker is None:
            # **ANOTHER MOD'S DEF CANNOT BE READ FROM DISK, AND THAT IS NOT A FAULT OF OURS.**
            # Doors Expanded's `PH_*` doors carry the gate component through a
            # `PatchOperationFindMod`, which is optional by construction and applies nothing when
            # that mod is absent. Its defs live in that mod's folder, not in Core's `Data/` and not
            # in this package, so there is nothing here to resolve.
            #
            # It is reported with its consequence named rather than passed silently: **if such a
            # door were not a `Normal` ticker, `CompTick` would never run on it.** In practice they
            # inherit Core's door bases, which are `Normal` -- but that is an inference about
            # somebody else's content, and an inference is what a note is for. This surfaced only
            # when the class scan stopped being blind to `sealed` and `partial` comps.
            if FOREIGN_DEF.match(defname):
                print("  NOTE  %s carries %s and belongs to another mod; its ticker cannot be read "
                      "from disk. If it is not a Normal ticker, %s never runs on it."
                      % (defname, props, "/".join(sorted(overrides))))
                continue
            check("%s carries %s and its ticker type resolves" % (defname, props), False,
                  "-- the def was not found in the installed game's data or in this package")
            continue
        delivered = DELIVERS.get(ticker, set())
        checked_any = True
        check("%s (%s, tickerType %s) receives %s" % (defname, comp, ticker,
                                                      "/".join(sorted(overrides & delivered))
                                                      or "NOTHING"),
              bool(overrides & delivered),
              "-- %s overrides %s, but a %s ticker only delivers %s. **This is exactly how the "
              "gate was never painted: Door is Normal, the comp overrode CompTickRare, and "
              "Thing.DoTick never calls TickRare on a Normal ticker.**"
              % (comp, "/".join(sorted(overrides)), ticker,
                 "/".join(sorted(delivered)) or "no comp tick at all"))

check("at least one comp/def pairing was actually resolved",
      checked_any,
      "-- if nothing resolved, every claim above was vacuous and this proof proved nothing")

print("")
print("AND THE GATE IS PAINTED FROM SOMEWHERE A DOOR ACTUALLY REACHES")
print("-" * 78)

emergence = read(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs"))

# A bounded window, not `[^}]*?`: the method body contains `{ return; }`, so a character
# class excluding braces cannot reach the call and the claim failed against correct code.
_interval = emergence.find("public override void CompTickInterval(int delta)")
check("the appearance refresh runs on the interval tick a Normal ticker gets",
      _interval >= 0
      and "RefreshGateAppearance();" in emergence[_interval:_interval + 420],
      "-- CompTickRare alone never fires on Door or Autodoor")

check("and it is throttled with Core's interval-safe form",
      "IsHashIntervalTick(AppearanceInterval, delta)" in emergence,
      "-- IsLiveGate walks every portal edge; per-tick on every door in a colony is not "
      "acceptable, and 1.6 varies a thing's update rate so the two-argument form is required")

check("CompTickRare is KEPT as well, for door defs this package does not own",
      "public override void CompTickRare()" in emergence,
      "-- this comp is attached to door DEFS, so another mod's door may legitimately be a Rare "
      "ticker; covering both costs nothing")

check("A SAVED GATE IS BLUE ON THE FIRST FRAME, not an interval later",
      re.search(r"RefreshGateAppearance\(\);\s*\n\s*if \(respawningAfterLoad", emergence)
      is not None,
      "-- painted before the early return, so loading a save does not show an ordinary grey door "
      "for up to 250 ticks")

check("marking and withdrawing repaint on the click",
      emergence.count("RefreshGateAppearance();") >= 5,
      "-- a player who marks a door and sees nothing change assumes the mark failed")

print("")
if failures:
    print("%d CLAIM(S) FAILED" % len(failures))
    for claim in failures:
        print("  - %s" % claim)
    sys.exit(1)
print("ALL COMP-TICKER CLAIMS HOLD")
