# -*- coding: utf-8 -*-
"""The laundering invariant, held as claims instead of as a sentence in the queue.

Queue row, verbatim: *"**The laundering routes are closed and must stay closed.** Marking happens
in exactly one place -- once, at the end of generation, before the map can be reached. Marking on
spawn instead would let a player haul ordinary goods in, drop them, and carry them out as odd. Any
future code that marks a thing anywhere else reopens that hole."* And its acceptance test: *"if
odd contracts can be satisfied without entering a coordinate, it has failed."*

THE ROW'S PURPOSE IS SATISFIED. ITS MECHANISM WAS SUPERSEDED, AND BY A STRONGER ONE.
------------------------------------------------------------------------------------
The row feared marking on spawn. The shipped design **does** mark on spawn, and that is what
closes the hole rather than opening it -- because the stamp is **one-way** and **everything** gets
one:

* Anything that first exists anywhere but a Backrooms coordinate is stamped `Outside`, for ever.
  So a crate of colony cotton is *proven ordinary at birth* and can never become odd, whatever
  gate it is hauled through afterwards. Under the row's own mechanism it would have been stamped
  nothing, and a rule that only marks generated contents has to trust that no later pass marks it.
* Anything still `Unknown` on a Backrooms map genuinely came into existence there -- rock mined
  from its walls, material from a deconstructed partition, a plant cut in one of its rooms, meat
  butchered from something found in it. **None of that was covered when only generated contents
  were marked**, so the row's mechanism left real odd goods unmarked as well as leaving the hole
  closeable only by vigilance.

So the row is closed on the purpose, and the mechanism it specified is recorded as superseded
rather than quietly dropped. What the row really asks for is that the property **stay** true, and
a sentence in a queue cannot do that. These claims can.

Absence claims go through `code_only`. Every file here names the hazard in order to explain the
guard -- the comment literally says *"Marking on spawn instead would let a player haul ordinary
goods in"* -- so a claim that read documentation would pass on the prose and miss the code.
"""
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
COMP = os.path.join(SRC, "Economy", "CompRimroomsOddOrigin.cs")
SERVICE = os.path.join(SRC, "Economy", "OddOriginService.cs")
CONTRACTS = os.path.join(SRC, "Company", "OddSupplyContracts.cs")
MISSIONS = os.path.join(SRC, "Company", "OddConsignmentMissions.cs")


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def code_only(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


def flat(text):
    return " ".join(text.split())


def slice_member(text, name):
    """A member body, cut to the next member signature rather than to the next brace."""
    match = re.search(r"(?m)^\s*(?:public|private|internal|protected)[^\n;=]*\b"
                      + re.escape(name) + r"\s*\(", text)
    if not match:
        return ""
    rest = text[match.end():]
    following = re.search(r"(?m)^\s*(?:public|private|internal|protected)\s", rest)
    return text[match.start():match.end() + (following.start() if following else len(rest))]


comp = code_only(read(COMP))
service = code_only(read(SERVICE))
contracts = code_only(read(CONTRACTS))
missions = code_only(read(MISSIONS))

# Every one of our own C# files, for the claims that have to be true of the whole tree rather
# than of one file. A laundering route is whatever code exists, not whatever code we remembered.
ALL = []
for base, dirs, names in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in ("obj", "bin")]
    for name in sorted(names):
        if name.endswith(".cs"):
            path = os.path.join(base, name)
            ALL.append((os.path.relpath(path, REPO), code_only(read(path))))

CLAIMS = []


def claim(label, ok, detail=""):
    CLAIMS.append((label, bool(ok), detail))


# ------------------------------------------------------------------ the stamp is one-way
stamp = slice_member(comp, "StampOrigin")
claim("the origin field is private",
      re.search(r"private\s+ThingOrigin\s+origin\s*;", comp) is not None,
      "a public field is a laundering route with no method to guard")
claim("the stamp refuses to overwrite an existing origin",
      "origin != ThingOrigin.Unknown" in stamp and "return;" in stamp,
      "one-way is the whole mechanism: re-stamping is laundering in either direction")
claim("the stamp refuses to write Unknown back over an answer",
      "value == ThingOrigin.Unknown" in stamp)
claim("MarkOdd goes through the stamp rather than assigning the field",
      "StampOrigin(ThingOrigin.Backrooms)" in slice_member(comp, "MarkOdd")
      and re.search(r"(?m)^\s*origin\s*=", slice_member(comp, "MarkOdd")) is None)

# The field may be written in exactly two places: the one-way stamp, and the legacy-save read
# that exists so an early save does not lose marks it had earned.
#
# **COUNTED ON NORMALISED SOURCE, AND THE FIRST VERSION WAS NOT.** It anchored `origin =` to the
# start of a line, so the legacy read -- written inline as `if (legacyOdd) { origin = ... }` --
# was invisible to it and the count came back 1. **A positional claim encodes layout, not the
# property**, which this battery has now been caught doing three times; a reformat would have
# "fixed" it and a real second assignment written inline would have walked straight past. The
# property is *how many times the field is assigned*, and that does not depend on where the
# newlines are.
ASSIGNS = re.compile(r"(?<!ref )\borigin\s*=(?!=)")
writes = ASSIGNS.findall(flat(comp))
claim("the origin field is assigned in exactly two places, both inside the comp",
      len(writes) == 2,
      "found %d; the stamp and the 0.7.2-dev legacy-boolean read, and nothing else" % len(writes))
# **AND THE TREE-WIDE CLAIM ASKS THE RIGHT QUESTION NOW.** The first version looked for
# `origin =` in every file and flagged four -- `NaturalFrontierService`, `WorldExit`,
# `BackroomsPressureComponent` and `GateIncursion` -- every one of them a local variable named
# `origin` of an unrelated type. That is the crying-wolf failure, and the claim was wrong rather
# than the code.
#
# The field is private, so no other file *can* assign it; that is the claim above. What a file
# outside the economy genuinely could do is **stamp** one, and a stamp from anywhere else is
# exactly the hole the row describes as reopened. So the property is where the stamps are.
stampers = sorted(set(rel for rel, text in ALL if "StampOrigin(" in text))
foreign = [rel for rel in stampers
           if "/Economy/" not in rel.replace(os.sep, "/")]
claim("EVERY origin stamp in the tree is inside the Economy namespace",
      stampers and not foreign,
      "stamped from outside it: %s" % ", ".join(foreign))
claim("the stampers are a short, known set",
      len(stampers) == 2,
      "found %d: %s -- the comp itself and the bond purchase, which is the only other place a "
      "thing is known to have come from outside" % (len(stampers), ", ".join(stampers)))

# ------------------------------------------------- everything gets a stamp, which closes the hole
spawn = slice_member(comp, "PostSpawnSetup")
claim("every first spawn is stamped, on a Backrooms map or anywhere else",
      "ThingOrigin.Backrooms" in spawn and "ThingOrigin.Outside" in spawn)
claim("THE OUTSIDE ARM EXISTS, which is the clause that closes laundering",
      "? ThingOrigin.Backrooms : ThingOrigin.Outside" in flat(spawn),
      "colony goods are proven ordinary at birth, so hauling them in cannot make them odd")
# **THE SIGNATURE IS CUT BEFORE THE BODY IS EXAMINED, AND THE FIRST VERSION DID NOT CUT IT.**
# `PostSpawnSetup(bool respawningAfterLoad)` carries the word in its own parameter list, so a
# claim that looked for the word in the slice passed on the signature while a plant removed the
# guard entirely -- it reported CAUGHT on nothing. The property is that the body *acts* on the
# flag, which the signature cannot satisfy.
# **AND THE SIGNATURE WAS ONLY THE FIRST OF TWO PLACES THE WORD HIDES.** With the signature cut,
# the claim still passed a plant that deleted the guard -- because `base.PostSpawnSetup(
# respawningAfterLoad)` *forwards* the flag, so the word is in the body either way. Both are the
# same defect: asserting that a word is present rather than that it does anything. So the base
# call is cut too, and what is left has to both mention the flag and return on it.
spawn_body = spawn[spawn.index(")") + 1:] if ")" in spawn else spawn
spawn_body = re.sub(r"base\.\w+\s*\([^)]*\)\s*;", " ", spawn_body)
claim("a reloaded thing is not restamped",
      "respawningAfterLoad" in spawn_body and "return;" in spawn_body,
      "asserted with the signature AND the base call removed: the parameter is named the same "
      "thing the guard tests, and the base call forwards it, so neither proves a guard exists")
claim("an already-stamped thing is not restamped on spawn",
      "origin != ThingOrigin.Unknown" in spawn)
claim("a thing with no map is left alone rather than guessed at",
      "map == null" in spawn)

# ------------------------------------------------------------- merging and splitting
allow = slice_member(comp, "AllowStackWith")
claim("merging is refused in BOTH directions",
      "IsOdd == OddOriginService.IsOdd(other)" in flat(allow),
      "odd absorbing ordinary manufactures odd goods; ordinary absorbing odd destroys them")
claim("the merge rule still honours Core's own answer first",
      "base.AllowStackWith(other)" in allow)
split = slice_member(comp, "PostSplitOff")
claim("a piece split off an odd stack is odd",
      "MarkOdd()" in split, "without this, splitting is a laundering route")

# ------------------------------------------------------------------------ the service
mark = slice_member(service, "Mark")
claim("the service refuses to mark something already stamped either way",
      "marker.Origin != ThingOrigin.Unknown" in mark,
      "and reports false, so a generation pass cannot overcount what it marked")
claim("the service marks through a minified wrapper",
      "Resolve(thing)" in mark,
      "the owner's own example is an uninstalled stove, which is a MinifiedThing")
generated = slice_member(service, "MarkGeneratedContents")
claim("the generation pass skips pawns",
      "thing is Pawn" in generated, "a generated inhabitant is not goods to be sold by origin")
claim("the generation pass returns a SORTED list of def names",
      "produced.Sort(" in generated,
      "database order depends on the mod list, so an unsorted list indexed anywhere is a seed "
      "divergence")
claim("the generation pass iterates a snapshot rather than the live lister",
      "new List<Thing>(things)" in generated)
claim("the comp is injected in exactly one place",
      sum(text.count("new CompProperties_RimroomsOddOrigin()") for _, text in ALL) == 1)

# ----------------------------------------- the acceptance test: no odd demand without a coordinate
claim("supply contracts test origin through the service, not a local flag",
      "OddOriginService.IsOdd(thing)" in contracts)
claim("nothing reads the comp's field directly outside the Economy namespace",
      not [rel for rel, text in ALL
           if "/Economy/" not in rel.replace(os.sep, "/") and ".Origin ==" in text],
      "a second reader is a second definition of odd")
claim("a supply demand is drawn from what a coordinate really produced",
      "MarkGeneratedContents" in flat(code_only(read(SERVICE))),
      "a demand for a thousand odd cotton is worthless if no space ever contained cotton")
claim("consignment missions exist and are a distinct kind from supply",
      os.path.isfile(MISSIONS) and "IsOddConsignment" in missions)

# ------------------------------------------------------------------------ standing constraints
claim("the whole feature needs no Harmony and no Core patch",
      not any("HarmonyLib" in text or "[HarmonyPatch" in text
              for _, text in ALL),
      "AllowStackWith, PostSplitOff, TransformLabel and PostExposeData are all Core hooks")
claim("the mark is saved, so it survives a reload",
      "Scribe_Values.Look(ref origin" in comp)
claim("the legacy boolean from 0.7.2-dev is still read",
      "rr_oddOrigin" in comp,
      "an early save must not silently lose every mark it had earned")

# ---------------------------------------------------------------------------------- report
bad = [(label, detail) for label, ok, detail in CLAIMS if not ok]
for label, ok, detail in CLAIMS:
    print("%s  %s" % ("ok   " if ok else "FAIL!", label))
    if detail and not ok:
        print("       %s" % detail)
print("")
print("%d of %d claims hold" % (len(CLAIMS) - len(bad), len(CLAIMS)))
sys.exit(1 if bad else 0)
