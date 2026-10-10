import io

# (defName, label, desc, effect, minDepth, minBand, weight, duration, magnitude, repeatable, ll, lt)
E = [
 ("RR_Anomaly_Presence", "a presence", "Something was heard. Nothing was found.",
  "Presence", 2, "Unsettled", 1.4, 0, 0, True,
  "RR_Anomaly_PresenceLabel", "RR_Anomaly_PresenceText"),

 ("RR_Anomaly_LightsFail", "the lights go", "Every light in the space switches itself off.",
  "LightsFail", 2, "Unsettled", 1.2, 0, 0, True,
  "RR_Anomaly_LightsLabel", "RR_Anomaly_LightsText"),

 ("RR_Anomaly_ColdSnap", "the cold comes in", "The space drops several degrees for no reason anyone can find.",
  "ColdSnap", 3, "Unsettled", 1.0, 0, 12, True,
  "RR_Anomaly_ColdLabel", "RR_Anomaly_ColdText"),

 ("RR_Anomaly_Seepage", "seepage", "The place is filthier than it was an hour ago.",
  "Seepage", 2, "Unsettled", 1.1, 0, 24, True,
  "RR_Anomaly_SeepageLabel", "RR_Anomaly_SeepageText"),

 ("RR_Anomaly_Rearrangement", "things move", "Loose things are not where they were left.",
  "Rearrangement", 4, "Active", 0.8, 0, 6, True,
  "RR_Anomaly_MovedLabel", "RR_Anomaly_MovedText"),

 ("RR_Anomaly_DeepCold", "the cold that stays", "A deeper, longer cold. It does not lift on its own.",
  "ColdSnap", 5, "Active", 0.6, 0, 25, False,
  "RR_Anomaly_DeepColdLabel", "RR_Anomaly_DeepColdText"),

 ("RR_Anomaly_Blackout", "total blackout", "Everything goes dark at once, and stays dark until somebody walks over and fixes it.",
  "LightsFail", 5, "Hostile", 0.7, 0, 0, False,
  "RR_Anomaly_BlackoutLabel", "RR_Anomaly_BlackoutText"),
]

def block(d):
    (name, label, desc, effect, lo, band, weight, dur, mag, rep, ll, lt) = d
    p = ["  <RimroomsAsyncIndustries.Threats.RimroomsAnomalyEventDef>",
         "    <defName>%s</defName>" % name,
         "    <label>%s</label>" % label,
         "    <description>%s</description>" % desc,
         "    <effect>%s</effect>" % effect,
         "    <minDepth>%d</minDepth>" % lo,
         "    <minBand>%s</minBand>" % band,
         "    <weight>%s</weight>" % weight]
    if mag:
        p.append("    <magnitude>%d</magnitude>" % mag)
    if rep:
        p.append("    <repeatable>true</repeatable>")
    p.append("    <letterLabelKey>%s</letterLabelKey>" % ll)
    p.append("    <letterTextKey>%s</letterTextKey>" % lt)
    p.append("  </RimroomsAsyncIndustries.Threats.RimroomsAnomalyEventDef>")
    return "\n".join(p)

header = """<?xml version="1.0" encoding="utf-8"?>
<Defs>

  <!-- Owner direction 2026-09-29: "even wild waky carzxzy creepy things when u add places and
       events". The places shipped earlier; these are the events.

       Every effect has an answer, because the frozen threat rules require one: readable
       warning, learnable rule, at least one countermeasure, no unavoidable instant failure.
       Lights are switched off with vanilla's own flick switch, so the countermeasure is
       vanilla too and the player already knows how to do it. Cold is answered by clothing, a
       heater, or leaving. Seepage is answered by the cleaning family, which already crosses a
       gate. Rearranged things are moved, never destroyed. Presence does nothing at all.

       Nothing here damages a pawn, destroys a thing, or blocks a route, and the threshold room
       is excluded from every effect, always -- whatever happens, walking back out is still
       possible.

       Non-repeatable events are recorded against the coordinate so a revisit resumes rather
       than replaying: a space a player knows should not perform its party trick every single
       time they walk in. -->

"""

io.open('Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsAnomalyEventDefs/RR_AnomalyEvents.xml',
        'w', encoding='utf-8', newline='').write(header + "\n\n".join(block(d) for d in E) + "\n\n</Defs>\n")
print("events:", len(E))
