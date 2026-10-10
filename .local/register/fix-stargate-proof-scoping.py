# -*- coding: utf-8 -*-
"""Eight plants walked past the proof, and all eight are the same trap in the same batch.

The claim-scoping trap, instances twenty-two through twenty-nine. Every one of them is a
substring test that survives the thing it is supposed to forbid:

  1-3. **Commenting a call out leaves the call's text in the file.** `StargateBridge.Attach(far)`
       is still "in" the source after `// StargateBridge.Attach(far);`. The emergence file is
       read through a comment strip now, the same way `check-compliance.py` reads C#, and the
       same way the compliance claim in this proof already had to be fixed an hour ago. **It was
       fixed in one place and not the other.**

  4.   **A pattern that matches somewhere else.** The claim that the wormhole and the glow are
       refreshed together matched the pair inside `CompTickRare` as well, so deleting the pair
       inside `CompTickInterval` passed. Anchored to the interval tick specifically now, which is
       the one a door actually receives.

  5.   **Counting guard clauses is not checking the guard.** `if (!Available` appearing four
       times says nothing about whether `Available` is honest; the plant made it `return true;`
       and every count still held. The getter's own body is asserted now.

  6.   **A second, legitimate call satisfied the claim.** `AllComps.Add(` appears twice -- once
       for the gate and once for the transporter -- so moving the gate onto the def still left a
       match. Both are required by name now.

  7.   **Two of three lookups still matched.** One `GenTypes.GetTypeInAnyAssembly` swapped for a
       bare `Type.GetType` left the other two, and a presence test cannot see that. All three are
       required.

  8.   **The strings appeared twice for different reasons.** `destination.IsPocketMap` is in both
       the address ternary and the dial-mode ternary, so deleting the address half passed. The
       address branch is asserted by its own expression.

**One family, eight instances, caught because every suite is run rather than the ones that were
touched.** That is now twice in two checkpoints that running everything found something reading
nothing.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

EDITS = []

# --------------------------------------------------------------------------- 1-3. comment strip
EDITS.append((
    u'''bridge = read(BRIDGE)
emergence = read(EMERGENCE)''',
    u'''bridge = read(BRIDGE)
emergence_raw = read(EMERGENCE)
# COMMENTED-OUT CODE IS NOT CODE. Three plants commented a call out and every presence test still
# matched, because the text was still in the file. Read the way `check-compliance.py` reads C#.
emergence = re.sub(r"/\\*.*?\\*/", " ",
                   re.sub(r"//[^\\n]*", " ", emergence_raw or ""), flags=re.S)'''))

# ------------------------------------------------------------------- 4. anchored to the interval
EDITS.append((
    u'''check("and it is driven from the same tick that paints the gate",
      re.search(r"RefreshGateAppearance\\(\\);\\s*\\n(?:\\s*//[^\\n]*\\n)*\\s*RefreshStargate\\(\\);",
                emergence) is not None,
      "-- one place asks *is this a gate yet*, so the glow and the wormhole can never disagree "
      "about the answer")''',
    u'''# ANCHORED TO THE INTERVAL TICK, which is the one a Normal-ticker door actually receives.
# The first draft matched the identical pair inside CompTickRare, so deleting the pair that runs
# on a door still passed.
_interval = emergence.find("public override void CompTickInterval(int delta)")
_window = emergence[_interval:_interval + 600] if _interval >= 0 else ""
check("and it is driven from the same tick that paints the gate",
      "RefreshGateAppearance();" in _window and "RefreshStargate();" in _window,
      "-- one place asks *is this a gate yet*, so the glow and the wormhole can never disagree "
      "about the answer -- and it must be the tick a door really gets")'''))

# ------------------------------------------------------------- 5. the guard itself, not the count
EDITS.append((
    u'''check("every entry point answers false when the mod is absent",
      bridge.count("if (!Available") >= 4,''',
    u'''check("AVAILABLE IS HONEST ABOUT WHETHER THEIR MOD IS THERE",
      "return compType != null && donorProps != null && openMethod != null;" in bridge,
      "-- counting guard clauses says nothing about whether the guard tells the truth. A plant "
      "made this `return true;` and every count still held, which would crash a Core-only colony")

check("every entry point answers false when the mod is absent",
      bridge.count("if (!Available") >= 4,'''))

# ------------------------------------------------------- 6. both adds, by what they add
EDITS.append((
    u'''check("the component is added to the instance, not to the def",
      "AllComps.Add(" in bridge,''',
    u'''check("the component is added to the instance, not to the def",
      "door.AllComps.Add(gate);" in bridge and "door.AllComps.Add(transporter);" in bridge
      and "def.comps.Add" not in bridge,
      "-- `AllComps.Add(` appears twice for two different components, so a bare presence test "
      "stayed satisfied when the gate was moved onto the def. Adding to the DEF would make every "
      "door in every colony a stargate, which is the one thing this must never do") if True else check(
      "placeholder", True,'''))

# --------------------------------------------------------------- 7. all three lookups
EDITS.append((
    u'''check("their type is found by Core's own name lookup",
      "GenTypes.GetTypeInAnyAssembly" in bridge,
      "-- the same lookup def loading uses, so a missing mod is a null rather than an exception")''',
    u'''check("EVERY type of theirs is found by Core's own name lookup",
      bridge.count("GenTypes.GetTypeInAnyAssembly") >= 3 and "Type.GetType(" not in bridge,
      "-- three types are resolved, and a plant swapped one for a bare `Type.GetType` that cannot "
      "see mod assemblies while the other two kept the presence test satisfied. "
      "GenTypes is the lookup def loading itself uses")'''))

# ------------------------------------------------------- 8. the address branch by its expression
EDITS.append((
    u'''check("the address conversion handles a pocket map as well as a world tile",
      "destination.IsPocketMap" in bridge and "PocketMap" in bridge,
      "-- their InitGate registers whichever applies, so the dial has to speak both")''',
    u'''check("the address conversion handles a pocket map as well as a world tile",
      "new PlanetTile(destination.Index)" in bridge and "destination.Tile" in bridge
      and '"PocketMap" : "Map"' in bridge,
      "-- their InitGate registers a map index for a pocket map and a tile otherwise, so the dial "
      "has to speak both. `destination.IsPocketMap` appears in two ternaries, so naming the "
      "string was not enough to prove the ADDRESS half survived")'''))

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("eight claims tightened: %d edits" % len(EDITS))
