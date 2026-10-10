# -*- coding: utf-8 -*-
"""A tell on every family, an ally family, and two animal families.

## Owner direction, 2026-10-04, verbatim

*"remember lsd unnerving feeling with all things ie events random spanwns,
enemies, allies, nuetrals, even all the crazy things ive mentioned in the past
and anything u can find in the many many prep docs on the Backrooms Universe"*

## Every tell is one exact wrong detail, not an adjective

`docs/UNIVERSE_ADAPTATION.md` is explicit about how the feeling is produced:
*"Ordinary industrial interiors become uncanny through exact changes ... a
shifted doorway, impossible adjacency, repeated hall, changed room dimensions, or
a feature that has moved since the last visit."* So no tell below says *eerie*,
*strange* or *unsettling*. Each one states a plain fact that cannot be true:

  * the wanderer has no dust on them in a space nobody has swept;
  * the missing person's clothes are in better repair than the day they vanished;
  * the survivor has been counting the days and the number is wrong;
  * the psychotic is standing exactly where the last crew's recorder failed;
  * the pack are standing in a ring facing outward, and have been for a while;
  * the echo is wearing what the real one put on this morning;
  * the recent dead died of something that has not happened yet on their file;
  * the stripped dead were stripped tidily, and the gear was stacked;
  * the helper knows the branch's name and has never been told it;
  * the animal is well-fed in a space with nothing to eat.

## The helper is the owner's *"allies"*, and it is the most unnerving of the three

Somebody who takes your side against what else is down there, fights for you with
Core's own defend-the-point AI, and **will not leave with you**. The help is
real; the refusal is the tell.

## The animals are the owner's *"wild animals and shit of the gasme"*

Core pawn kinds, unfactioned, no mental state -- the unnerving part is not that
they are dangerous but that they are **in here** and something had to bring them.
Named with a fallback chain so a Core-only install and a 294-mod profile both
resolve one, and the family is skipped rather than substituted if none loads.
"""
import io
import re
import sys

NL = chr(10)
DEFS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsInhabitantDefs/RR_Inhabitants.xml"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Inhabitants.xml"

# (family defName, its tellKey)
TELLS = [
    ("RR_Inhabitant_Wanderer", "RR_Inhabitant_WandererTell"),
    ("RR_Inhabitant_Missing", "RR_Inhabitant_MissingTell"),
    ("RR_Inhabitant_Survivor", "RR_Inhabitant_SurvivorTell"),
    ("RR_Inhabitant_Psychotic", "RR_Inhabitant_PsychoticTell"),
    ("RR_Inhabitant_PsychoticPack", "RR_Inhabitant_PackTell"),
    ("RR_Inhabitant_DeadRecent", "RR_Inhabitant_DeadRecentTell"),
    ("RR_Inhabitant_DeadStripped", "RR_Inhabitant_DeadStrippedTell"),
    ("RR_Inhabitant_Echo", "RR_Inhabitant_EchoTell"),
]

NEW_FAMILIES = '''
  <!-- **THE OWNER'S "allies", AND THE MOST UNNERVING OF THE THREE RELATIONS.** 2026-10-04:
       "they should be nutral, allies, and enemy in all differnt kinds and relations and
       scenrios", under "remember lsd unnerving feeling with all things".

       A thing that attacks you is explicable. Somebody who has been down here long enough to
       be part of the place, who takes your side against what else is in it, and who will not
       come out with you, is not. The help is real and it is Core's: an existing non-hostile
       faction and LordJob_DefendPoint, so they fight the psychotic families with ordinary AI.
       Nothing here goes near a gate - PortalTraversalPolicy is still the only chokepoint and
       an inhabitant still never decides anything about one. -->
  <RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>
    <defName>RR_Inhabitant_Helper</defName>
    <label>caretaker</label>
    <description>Somebody who has been here long enough to know the place. They will stand with a crew against what else is in the space, and they will not leave it.</description>
    <kind>Helper</kind>
    <minDepth>3</minDepth>
    <minBand>Unsettled</minBand>
    <weight>0.5</weight>
    <pawnKindDefNames>
      <li>Villager</li>
      <li>Drifter</li>
      <li>Colonist</li>
    </pawnKindDefNames>
    <count>1~1</count>
    <chance>0.2</chance>
    <friendly>true</friendly>
    <tellKey>RR_Inhabitant_HelperTell</tellKey>
    <letterLabelKey>RR_Inhabitant_HelperLabel</letterLabelKey>
    <letterTextKey>RR_Inhabitant_HelperText</letterTextKey>
  </RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>

  <!-- **THE OWNER'S "wild animals and shit of the gasme".** 2026-10-04. Animals reached the
       player only as a chaser until now, never as something standing in a room.

       Unfactioned and in no mental state, like any wild animal anywhere: the unnerving part is
       not that it is dangerous, it is that it is IN HERE and something had to bring it. Two
       families so the find is not always the same animal - one that belongs on a farm and one
       that does not belong anywhere near people. Named with a fallback chain, and the family
       is skipped rather than substituted when none of the names resolves. -->
  <RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>
    <defName>RR_Inhabitant_FaunaDomestic</defName>
    <label>stray animal</label>
    <description>An animal that was somebody's. It is in good condition, which is the part that does not fit.</description>
    <kind>Fauna</kind>
    <minDepth>2</minDepth>
    <minBand>Unsettled</minBand>
    <weight>0.9</weight>
    <pawnKindDefNames>
      <li>Cat</li>
      <li>LabradorRetriever</li>
      <li>Husky</li>
      <li>Chicken</li>
    </pawnKindDefNames>
    <count>1~1</count>
    <chance>0.3</chance>
    <tellKey>RR_Inhabitant_FaunaDomesticTell</tellKey>
    <letterLabelKey>RR_Inhabitant_FaunaDomesticLabel</letterLabelKey>
    <letterTextKey>RR_Inhabitant_FaunaDomesticText</letterTextKey>
  </RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>

  <RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>
    <defName>RR_Inhabitant_FaunaWild</defName>
    <label>animal</label>
    <description>Something that lives outdoors, indoors, a long way from any outdoors.</description>
    <kind>Fauna</kind>
    <minDepth>4</minDepth>
    <minBand>Unsettled</minBand>
    <weight>0.7</weight>
    <pawnKindDefNames>
      <li>Deer</li>
      <li>Muffalo</li>
      <li>Boomalope</li>
      <li>Hare</li>
    </pawnKindDefNames>
    <count>1~2</count>
    <chance>0.25</chance>
    <tellKey>RR_Inhabitant_FaunaWildTell</tellKey>
    <letterLabelKey>RR_Inhabitant_FaunaWildLabel</letterLabelKey>
    <letterTextKey>RR_Inhabitant_FaunaWildText</letterTextKey>
  </RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>
'''

NEW_KEYS = [
    # ------------------------------------------------- the tells, one exact wrong fact each
    "  <!-- THE TELLS. Owner, 2026-10-04: \"remember lsd unnerving feeling with all things\".",
    "       Read off the pawn forever, not once in a letter. Every one states a plain fact that",
    "       cannot be true, per UNIVERSE_ADAPTATION.md: \"Ordinary industrial interiors become",
    "       uncanny through exact changes\". None of them says eerie, strange or unsettling. -->",
    "  <RR_Inhabitant_WandererTell>There is no dust on them. Nothing in this space has been "
    "swept.</RR_Inhabitant_WandererTell>",
    "  <RR_Inhabitant_MissingTell>Their clothes are in better repair than the day they went "
    "missing.</RR_Inhabitant_MissingTell>",
    "  <RR_Inhabitant_SurvivorTell>They have been counting the days. The number they give is "
    "wrong, and not by a little.</RR_Inhabitant_SurvivorTell>",
    "  <RR_Inhabitant_PsychoticTell>They are standing on the spot where the last crew's recorder "
    "stopped.</RR_Inhabitant_PsychoticTell>",
    "  <RR_Inhabitant_PackTell>They are standing in a ring, facing outward. The floor is worn "
    "where they have been standing.</RR_Inhabitant_PackTell>",
    "  <RR_Inhabitant_EchoTell>Wearing what the real one put on this morning, down to the "
    "repairs.</RR_Inhabitant_EchoTell>",
    "  <RR_Inhabitant_DeadRecentTell>The file gives a cause of death that has not happened to "
    "them yet.</RR_Inhabitant_DeadRecentTell>",
    "  <RR_Inhabitant_DeadStrippedTell>Stripped tidily. Their gear was stacked beside them, not "
    "taken.</RR_Inhabitant_DeadStrippedTell>",
    "  <RR_Inhabitant_HelperTell>They used the branch's name before anybody said it, and they "
    "will not go near the threshold.</RR_Inhabitant_HelperTell>",
    "  <RR_Inhabitant_FaunaDomesticTell>Well fed. There is nothing to eat in this space and "
    "nothing to drink.</RR_Inhabitant_FaunaDomesticTell>",
    "  <RR_Inhabitant_FaunaWildTell>It is not thin, it is not frightened, and there is no way in "
    "here that it could have used.</RR_Inhabitant_FaunaWildTell>",
    # ------------------------------------------------- the new families' letters
    "  <RR_Inhabitant_HelperLabel>Somebody is helping</RR_Inhabitant_HelperLabel>",
    "  <RR_Inhabitant_HelperText>{0} is in this space and has taken the crew's side. They will "
    "stand with the team against what else is down here. They will not leave with them, and they "
    "do not explain why.</RR_Inhabitant_HelperText>",
    "  <RR_Inhabitant_FaunaDomesticLabel>An animal, in here</RR_Inhabitant_FaunaDomesticLabel>",
    "  <RR_Inhabitant_FaunaDomesticText>{0} is in this space. It was somebody's animal and it is "
    "in good condition. Something brought it in here.</RR_Inhabitant_FaunaDomesticText>",
    "  <RR_Inhabitant_FaunaWildLabel>Something that lives outside</RR_Inhabitant_FaunaWildLabel>",
    "  <RR_Inhabitant_FaunaWildText>{0} is in this space, a long way from anywhere it could have "
    "walked in from. It is not thin and it is not frightened."
    "</RR_Inhabitant_FaunaWildText>",
]

problems = 0

# ------------------------------------------------------------------ the tells on the existing eight
defs = io.open(DEFS, encoding="utf-8-sig").read()
for family, tell in TELLS:
    if ("<tellKey>%s</tellKey>" % tell) in defs:
        print("already has a tell: %s" % family)
        continue
    anchor = "<defName>%s</defName>" % family
    if defs.count(anchor) != 1:
        print("FAMILY NOT UNIQUE (%d): %s" % (defs.count(anchor), family))
        problems += 1
        continue
    # inserted immediately before the family's closing tag, so the tell sits with its letters
    start = defs.index(anchor)
    close = defs.index("</RimroomsAsyncIndustries.Threats.RimroomsInhabitantDef>", start)
    defs = defs[:close] + ("  <tellKey>%s</tellKey>" % tell) + NL + "  " + defs[close:]
    print("%-32s tell added" % family)

if "RR_Inhabitant_Helper" in defs:
    print("the new families are already present")
else:
    end = defs.rindex("</Defs>")
    defs = defs[:end] + NEW_FAMILIES + defs[end:]
    print("added 3 families: Helper, FaunaDomestic, FaunaWild")

# ------------------------------------------------------------------------------- the keyed strings
keys = io.open(KEYED, encoding="utf-8-sig").read().split(NL)
if any("RR_Inhabitant_WandererTell" in line for line in keys):
    print("the tells are already in the keyed file")
else:
    closing = [index for index, line in enumerate(keys) if line.strip() == "</LanguageData>"]
    if len(closing) != 1:
        print("EXPECTED ONE </LanguageData>, found %d" % len(closing))
        problems += 1
    else:
        keys = keys[:closing[0]] + NEW_KEYS + keys[closing[0]:]
        print("added %d keyed strings" % len(NEW_KEYS))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

io.open(DEFS, "w", encoding="utf-8-sig", newline=NL).write(defs)
io.open(KEYED, "w", encoding="utf-8-sig", newline=NL).write(NL.join(keys))
print("wrote the defs and the keyed strings")
