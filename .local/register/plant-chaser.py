# -*- coding: utf-8 -*-
"""Planted faults against `proof-chaser.py`.

## Why this suite exists at all

**The pursuer subsystem had no proof and no plant anywhere.** Twenty-three plant
suites and forty-nine proofs, and a 224-line bespoke threat that teleported
between rooms, never pathfound and landed one scripted two-point blow passed
every gate this project has for twenty-seven versions -- because no instrument
was pointed at it. Owner, 2026-10-04: *"not some blob figure, just normal core
mechanics"*.

A proof written the same day as the code it checks is worth exactly what its
ability to fail is worth, so every claim that guards the owner's direction gets a
plant here.

## The one that matters most

*"the chaser teleports again"*. Every other defect of the old pursuer followed
from that one: because it never pathfound it needed its own advance timer, its
own loudness rule, its own withdrawal counter and its own scripted strike. A
position assignment creeping back is the regression that brings all of it with
it.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

CHASER = "src/RimroomsAsyncIndustries/Threats/FirstSlicePursuer.cs"
SITE = "src/RimroomsAsyncIndustries/Threats/FirstSliceSiteComponent.cs"
OBSERVATIONS = "src/RimroomsAsyncIndustries/Company/EvidenceObservations.cs"
PROOF = ".local/register/proof-chaser.py"
CHR_NL = chr(10)

PLANTS = [
    # ------------------------------------------------- the blob comes back
    ("THE CHASER GOES BACK TO BEING A BESPOKE THING", SITE,
     "        private Pawn pursuer;",
     "        private Thing_QuietPursuer pursuer;", PROOF),

    ("the chaser stops being made by Core's generator", CHASER,
     "PawnGenerator.GeneratePawn(new PawnGenerationRequest(",
     "MakeChaserSomeOtherWay((", PROOF),

    # ------------------- the load-bearing one: everything else followed from the teleport
    ("THE CHASER TELEPORTS AGAIN", CHASER,
     "            RoomRecord here = RoomAt(pursuer.Position);",
     "            RoomRecord here = RoomAt(pursuer.Position);" + CHR_NL
     + "            pursuer.Position = pursuer.Position;", PROOF),

    ("THE SCRIPTED STRIKE COMES BACK", CHASER,
     "            if (closest == null) { return; }",
     "            if (closest == null) { return; }" + CHR_NL
     + "            closest.TakeDamage(new DamageInfo(DamageDefOf.Blunt, 2f));", PROOF),

    # ------------------------------------------------- half the roster disappears
    ("THE WILD ANIMALS DROP OUT OF THE ROSTER", CHASER,
     "                foreach (PawnKindDef animal in map.Biome.AllWildAnimals)",
     "                foreach (PawnKindDef animal in new List<PawnKindDef>())", PROOF),

    ("the humanlike kinds stop matching the vetted inhabitant list", CHASER,
     'HostileHumanlikeKinds = { "Pirate", "Drifter", "Villager" }',
     'HostileHumanlikeKinds = { "Pirate" }', PROOF),

    # ------------------------------------------------- reproducibility
    ("THE DRAW GOES BACK TO Rand, so a reload rerolls what is hunting you", CHASER,
     'int draw = CampaignSeed.Derive(branchSeed, "chaser:kind:" + (openingId ?? ""), 1);',
     "int draw = Rand.Range(0, 9999);", PROOF),

    # **A DERIVED INDEX INTO AN UNORDERED LIST IS REPRODUCIBLE BY LUCK ONLY.** Def database
    # order is not a promise, so the same seed would select different things on different loads
    # -- which looks exactly like working until somebody reloads.
    ("the roster stops being ordered before it is indexed", CHASER,
     "            roster = roster.OrderBy(kind => kind.defName).ToList();" + CHR_NL,
     "", PROOF),

    # ------------------------------------------------- the researched capabilities
    ("THE DETECTION CAPABILITIES STOP BUYING ANYTHING", CHASER,
     '                if (campaign.HasCapability("RR_Cap_Detection")) { return 3; }' + CHR_NL
     + '                return campaign.HasCapability("RR_Cap_EarlyWarning") ? 2 : 1;',
     "                return 1;", PROOF),

    ("and Detection starts stacking with EarlyWarning instead of superseding it", CHASER,
     '                if (campaign.HasCapability("RR_Cap_Detection")) { return 3; }' + CHR_NL
     + '                return campaign.HasCapability("RR_Cap_EarlyWarning") ? 2 : 1;',
     '                return campaign.HasCapability("RR_Cap_EarlyWarning") ? 2 : 1;' + CHR_NL
     + '                + (campaign.HasCapability("RR_Cap_Detection") ? 3 : 0);', PROOF),

    # ------------------------------------------------- the false-positive sighting
    # Scanning the map for hostiles would count any raider as an entity observation, which is a
    # false positive on a contract bonus the player gets paid for.
    ("A SIGHTING COUNTS THE CREW AS STRANGERS", OBSERVATIONS,
     "                if (pawn.Faction == Faction.OfPlayer) { continue; }" + CHR_NL,
     "", PROOF),

    # ------------------------------------------------- the ending
    ("THE WITHDRAWAL VANISHES THE PAWN AGAIN", CHASER,
     "            pursuerWithdrawn = true;" + CHR_NL
     + "            pursuer = null;",
     "            pursuerWithdrawn = true;" + CHR_NL
     + "            if (pursuer != null && !pursuer.Destroyed) { pursuer.Destroy(DestroyMode.Vanish); }"
     + CHR_NL
     + "            pursuer = null;", PROOF),

    ("repelling stops using Core's own fear", CHASER,
     "                    MentalStateDefOf.PanicFlee, null, true);",
     "                    MentalStateDefOf.Berserk, null, true);", PROOF),

    ("a wild animal chaser is given a faction instead of being turned manhunter", CHASER,
     "                    MentalStateDefOf.Manhunter, null, true);",
     "                    MentalStateDefOf.Berserk, null, true);", PROOF),

    # ------------------------------------------------- the placement that was already right
    ("THE ENCOUNTER STARTS ON TOP OF THE CREW", CHASER,
     "distances[r.index] == 2", "distances[r.index] == 0", PROOF),

    ("and an unreachable room stops refusing the encounter", CHASER,
     "            if (distant == null) { return; }" + CHR_NL,
     "", PROOF),

    # ------------------------------------------------- the chaser survives a reload
    # **THE FIRST VERSION OF THIS PLANT TESTED A COMMENT.** It appended
    # `// Thing_QuietPursuer` to the field and reported MISSED -- correctly, because the
    # proof strips comments before reading, and a comment naming a retired class is
    # harmless. Re-aimed at a fault that is real and silent: the encounter flags are saved,
    # so dropping only the reference leaves the site certain something is hunting the crew
    # and unable to say what.
    ("THE CHASER STOPS BEING SAVED, so it vanishes on reload", SITE,
     '            Scribe_References.Look(ref pursuer, "rr_pursuer");' + CHR_NL,
     "", PROOF),
]


# **ONE SENTINEL PER SUITE, named after the suite.** A later suite's unmark once erased an
# earlier suite's failure record when all of them shared a single path.
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


def write_verified(path, text):
    """Write, and do not believe it until it reads back identical.

    Retried on both the plant and the restore, because `OSError: [Errno 22]` on a path this loop
    has already written is a transient this repository has met repeatedly -- and a run that
    aborted on the way *in* while retrying on the way *out* is the asymmetry that killed a
    full-battery sweep on 2026-10-04.
    """
    last = None
    for attempt in range(6):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.4 * (attempt + 1))
    sys.stderr.write("FATAL: could not write %s (%s) -- the sentinel is left in place on "
                     "purpose; run tools/check-plant-residue.py\n" % (path, last))
    sys.exit(3)


ORIGINALS = {path: io.open(path, encoding="utf-8").read()
             for path in sorted({plant[1] for plant in PLANTS})}

print("baseline -- the target must pass before anything is planted")
for command in sorted({plant[4] for plant in PLANTS}):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in ORIGINALS.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every target verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
