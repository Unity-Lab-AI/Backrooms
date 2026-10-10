# -*- coding: utf-8 -*-
"""Claims and plants for the radio fragment's one distinguishing property.

Every other event is environmental and anonymous. This one is only worth shipping
because of **whose voice it is**: a fragment from nobody is atmosphere, and a
fragment naming a colonist who is standing in the base at the same moment is the
owner's *"echos of thier inhabitance in weird ways"*.

Three ways that could be lost, and all three are silent:

  * the voice is drawn with `Rand`, so a reload reseats who was on the radio;
  * the voice is taken from the lost-pawn register **destructively**, so
    mentioning somebody quietly deletes the record that they are missing;
  * the voice is always null, so the fragment still fires and still announces --
    as anonymous noise, which is the version that is not worth shipping.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-unnerving-register.py"
PLANTS = ".local/register/plant-unnerving-register.py"

PROOF_ANCHOR = 'print("")' + NL + "if failures:"

NEW_CLAIMS = '''# ------------------------------------------------- the one event with a person in it
register = read(SRC, "Company", "LostPawnRegister.cs")

check("THE RADIO FRAGMENT NAMES SOMEBODY THE BRANCH KNOWS",
      "private static string VoiceFor(CoordinateRecord coordinate," in event_service
      and "AnomalyEffect.RadioFragment" in event_service
      and "foreach (StaffRecord member in campaign.Staff)" in event_service,
      "-- a fragment from nobody is atmosphere. The uncanniness is the recognition, which is "
      "the same move the Echo inhabitant family makes")

check("and a branch with nobody at home falls back to somebody it lost",
      "campaign.LostPawnNames()" in event_service,
      "-- the sadder reading, and still a recognition. With neither there is no fragment at "
      "all, because a transmission from a name nobody knows is the thing this is not")

# **MENTIONING SOMEBODY MUST NOT RESOLVE THEM.** `TakeLostPawnName` removes what it returns,
# which is right for a coordinate PLACING a missing person -- they have now been found. It is
# wrong for anything that merely names one.
check("AND NAMING A LOST PERSON DOES NOT DELETE THE RECORD THAT THEY ARE LOST",
      "public List<string> LostPawnNames()" in register
      and "new List<string>(lostPawnNames)" in register
      and "TakeLostPawnName" not in event_service,
      "-- `TakeLostPawnName` removes what it returns; a radio fragment that consumed it would "
      "quietly mark somebody found because their name was mentioned once")

check("THE VOICE IS DERIVED, NEVER Rand",
      'CampaignSeed.Derive(coordinate.Seed,' in event_service
      and '"radio:voice:" + coordinate.Openings' in event_service,
      "-- the same opening always carries the same voice; `Rand` would let a reload reseat who "
      "was on the radio, which is a save-scum on a story beat")

check("and the voices are ordered before the draw indexes them",
      "voices.Sort(System.StringComparer.Ordinal);" in event_service,
      "-- roster order is not a promise, so a derived index into an unordered list is "
      "reproducible by luck only")

check("THE FRAGMENT COSTS NOTHING, like the Presence it is modelled on",
      "case AnomalyEffect.RadioFragment: return true;" in event_service,
      "-- damages nobody, destroys nothing, blocks no route. `FireEffect` returns false to mean "
      "*the effect found nothing to do*, and a transmission never can")

'''

PLANT_ANCHOR = (
    "    # ================================================= the same register, applied to events")

NEW_PLANTS = '''    # ------------------------------------------------- the one event with a person in it
    ("THE RADIO VOICE GOES BACK TO Rand, so a reload reseats who was on the radio", EVENT_SERVICE,
     '            int draw = CampaignSeed.Derive(coordinate.Seed,' + CHR_NL
     + '                "radio:voice:" + coordinate.Openings, 1);',
     "            int draw = Rand.Range(0, 9999);", PROOF),

    ("the voices stop being ordered before the draw", EVENT_SERVICE,
     "            voices.Sort(System.StringComparer.Ordinal);" + CHR_NL, "", PROOF),

    ("NAMING A LOST PERSON DELETES THE RECORD THAT THEY ARE LOST", EVENT_SERVICE,
     "                foreach (string lost in campaign.LostPawnNames())",
     "                foreach (string lost in new[] { campaign.TakeLostPawnName() })", PROOF),

    ("the non-destructive accessor is removed from the register", REGISTER,
     "        public List<string> LostPawnNames()", "        private List<string> Unused()",
     PROOF),

    ("THE FRAGMENT STOPS NAMING ANYBODY and fires as anonymous noise", EVENT_SERVICE,
     "            foreach (StaffRecord member in campaign.Staff)",
     "            foreach (StaffRecord member in new List<StaffRecord>())", PROOF),

    ("the fragment starts claiming it found nothing to do", EVENT_SERVICE,
     "                case AnomalyEffect.RadioFragment: return true;",
     "                case AnomalyEffect.RadioFragment: return false;", PROOF),

'''

PLANT_CONST = (
    'CONTENT = "src/RimroomsAsyncIndustries/Generation/RoomContentMapComponent.cs"' + NL
    + 'REGISTER = "src/RimroomsAsyncIndustries/Company/LostPawnRegister.cs"'
)

problems = 0

text = io.open(PROOF, encoding="utf-8").read()
if "THE RADIO FRAGMENT NAMES SOMEBODY THE BRANCH KNOWS" in text:
    print("the fragment claims are already present")
elif text.count(PROOF_ANCHOR) != 1:
    print("PROOF ANCHOR NOT UNIQUE (%d)" % text.count(PROOF_ANCHOR))
    problems += 1
else:
    io.open(PROOF, "w", encoding="utf-8", newline=NL).write(
        text.replace(PROOF_ANCHOR, NEW_CLAIMS + PROOF_ANCHOR))
    print("added 6 fragment claims")

text = io.open(PLANTS, encoding="utf-8").read()
if "THE RADIO VOICE GOES BACK TO Rand" in text:
    print("the fragment plants are already present")
else:
    old = 'CONTENT = "src/RimroomsAsyncIndustries/Generation/RoomContentMapComponent.cs"'
    if text.count(old) != 1:
        print("PLANT CONSTANT NOT UNIQUE (%d)" % text.count(old))
        problems += 1
    elif text.count(PLANT_ANCHOR) != 1:
        print("PLANT ANCHOR NOT UNIQUE (%d)" % text.count(PLANT_ANCHOR))
        problems += 1
    else:
        text = text.replace(old, PLANT_CONST)
        text = text.replace(PLANT_ANCHOR, NEW_PLANTS + PLANT_ANCHOR)
        io.open(PLANTS, "w", encoding="utf-8", newline=NL).write(text)
        print("added 6 fragment plants")

if problems:
    print("%d problem(s)" % problems)
    sys.exit(1)
