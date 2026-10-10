import io

# (defName, label, desc, kind, minDepth, maxDepth, minBand, weight, kinds, cLo, cHi, chance,
#  hostile, belongings, letterLabel, letterText)
I = [
 ("RR_Inhabitant_Wanderer", "wanderer", "Somebody is here. They were not brought in, and they do not explain themselves.",
  "Wanderer", 2, 0, "Unsettled", 1.2, ["Villager", "Drifter", "Colonist"], 1, 1, 0.45,
  False, True, "RR_Inhabitant_WandererLabel", "RR_Inhabitant_WandererText"),

 ("RR_Inhabitant_Missing", "missing person", "Somebody who went missing. Where the branch has lost people, it is one of them.",
  "Missing", 2, 0, "Unsettled", 1.0, ["Villager", "Drifter", "Colonist"], 1, 1, 0.35,
  False, True, "RR_Inhabitant_MissingLabel", "RR_Inhabitant_MissingText"),

 ("RR_Inhabitant_Survivor", "survivor", "Somebody still alive down here, and willing to leave with anyone who can get them out.",
  "Survivor", 2, 0, "Unsettled", 0.9, ["Villager", "Drifter", "Colonist"], 1, 2, 0.30,
  False, True, "RR_Inhabitant_SurvivorLabel", "RR_Inhabitant_SurvivorText"),

 ("RR_Inhabitant_Psychotic", "unstable inhabitant", "Somebody who has been down here far too long and will not be reasoned with.",
  "Psychotic", 3, 0, "Active", 1.0, ["Pirate", "Drifter", "Villager"], 1, 2, 0.55,
  True, True, "RR_Inhabitant_PsychoticLabel", "RR_Inhabitant_PsychoticText"),

 ("RR_Inhabitant_PsychoticPack", "several unstable inhabitants", "More than one, and they have been together long enough to move together.",
  "Psychotic", 5, 0, "Hostile", 0.6, ["Pirate", "Drifter"], 2, 3, 0.40,
  True, True, "RR_Inhabitant_PackLabel", "RR_Inhabitant_PackText"),

 ("RR_Inhabitant_DeadRecent", "a body", "Somebody who did not get out. Still carrying what they came in with.",
  "Dead", 2, 0, "Quiet", 1.3, ["Villager", "Drifter", "Colonist"], 1, 2, 0.55,
  False, True, "", ""),

 ("RR_Inhabitant_DeadStripped", "an old body", "Somebody who did not get out, a long time ago. Whatever they had is long gone.",
  "Dead", 3, 0, "Quiet", 1.0, ["Villager", "Drifter"], 1, 3, 0.45,
  False, False, "", ""),

 ("RR_Inhabitant_DeadCrew", "what is left of a crew", "Several people who came in together and stayed.",
  "Dead", 4, 0, "Quiet", 0.7, ["Pirate", "Drifter", "Villager"], 2, 4, 0.35,
  False, True, "", ""),
]

def block(d):
    (name, label, desc, kind, lo, hi, band, weight, kinds, clo, chi, chance,
     hostile, belongings, ll, lt) = d
    p = ["  <RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>",
         "    <defName>%s</defName>" % name,
         "    <label>%s</label>" % label,
         "    <description>%s</description>" % desc,
         "    <kind>%s</kind>" % kind,
         "    <minDepth>%d</minDepth>" % lo]
    if hi > 0:
        p.append("    <maxDepth>%d</maxDepth>" % hi)
    p.append("    <minBand>%s</minBand>" % band)
    p.append("    <weight>%s</weight>" % weight)
    p.append("    <pawnKindDefNames>")
    for k in kinds:
        p.append("      <li>%s</li>" % k)
    p.append("    </pawnKindDefNames>")
    p.append("    <count>%d~%d</count>" % (clo, chi))
    p.append("    <chance>%s</chance>" % chance)
    if hostile:
        p.append("    <hostile>true</hostile>")
    if not belongings:
        p.append("    <carriesBelongings>false</carriesBelongings>")
    if ll:
        p.append("    <letterLabelKey>%s</letterLabelKey>" % ll)
        p.append("    <letterTextKey>%s</letterTextKey>" % lt)
    p.append("  </RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>")
    return "\n".join(p)

header = """<?xml version="1.0" encoding="utf-8"?>
<Defs>

  <!-- Owner direction 2026-09-29: "alla trhings are possible finding random pawns of
       disappering, findeding dead ones pasycholitc ones lost pawns all kinds of crazy
       variations as per the lore".

       Every family generates from a PawnKindDef the loaded game already ships. No new pawn
       kind is authored here, because M2 is currently DELETING this mod's five legacy
       RR_*Staff PawnKindDefs under the existing-content policy, and adding new ones would
       reopen the exact category being closed. The preference lists fall back, so a Core-only
       install and a 274-mod profile both work.

       Bodies are Dead and are placed when the space is generated: finding one should not wait
       on a danger band, and a corpse does not act. Everything else acts and is placed on
       ARRIVAL against the coordinate's band at that moment, which is what keeps the ladder's
       promise that a first visit is always quiet.

       Only the Psychotic families are hostile, and that is enforced in code rather than
       trusted here: a hostile family that does not read as hostile would break the
       warning-first threat rule. Hostile counts are additionally clamped by the ladder's
       absolute cap of three simultaneous encounters, whatever these numbers say. -->

"""

io.open('Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsInhabitantDefs/RR_Inhabitants.xml',
        'w', encoding='utf-8', newline='').write(header + "\n\n".join(block(d) for d in I) + "\n\n</Defs>\n")
print("inhabitant families:", len(I))
