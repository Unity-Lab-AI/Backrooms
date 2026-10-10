# -*- coding: utf-8 -*-
"""Wire boarding up: the gizmo on the door, the JobDef, and the strings."""
import io
import re
import sys

NL = chr(10)

EMERGENCE = "src/RimroomsAsyncIndustries/Portals/CompRimroomsEmergence.cs"
JOBDEFS = "Mod/Rimrooms - Async Industries/1.6/Defs/JobDefs/RR_PortalJobs.xml"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"

GIZMO = '''
            // **BOARDING IT UP, ON THE DOOR, BY A PAWN, FOR WOOD.** Owner, 2026-10-04: *"the
            // closing of natural portals needs to be an option on the gate itself so pawns can
            // close it with like 25 wood to board it up which makes it close its map freeing up a
            // map from being open so others can be explored"*.
            //
            // Closing a place already existed in the Operations held-places pane. What the owner
            // objected to is where it lived -- the same direction says *"everything that the
            // machine needs to start up should be able to do in the worlkd from the devices
            // themselfes with pawns controls and actrions not just in the opetaions tab"*.
            //
            // Offered only when there is something behind the door to close, and **disabled with
            // its reason showing** rather than hidden when there is not: a command that vanishes
            // teaches nothing, and the reasons here are the interesting part -- somebody is still
            // inside, a crossing is in flight, there is no wood.
            RimroomsCampaignComponent boardCampaign = Campaign();
            if (boardCampaign != null
                && PortalBoardUp.PlaceBehind(boardCampaign, parent) != null)
            {
                string boardRefusal = PortalBoardUp.RefusalFor(boardCampaign, parent);
                var boardUp = new Command_Action
                {
                    defaultLabel = "RR_BoardUp_Label".Translate(PortalBoardUp.WoodCost),
                    defaultDesc = "RR_BoardUp_Desc".Translate(PortalBoardUp.WoodCost),
                    icon = parent.def.uiIcon,
                    action = delegate { Show(PortalBoardUp.Order(boardCampaign, parent)); }
                };
                if (boardRefusal != null)
                { boardUp.Disable(boardRefusal.Translate()); }
                yield return boardUp;
            }
'''

JOB = '''
  <!-- Boarding up a natural portal. Owner 2026-10-04: "so pawns can close it with like 25 wood
       to board it up which makes it close its map freeing up a map from being open". The wood is
       carried to the doorway, so the job is visible on the map rather than a number changing. -->
  <JobDef>
    <defName>RR_BoardUpPortal</defName>
    <driverClass>RimroomsAsyncIndustries.Portals.JobDriver_BoardUpPortal</driverClass>
    <reportString>boarding up TargetA.</reportString>
    <casualInterruptible>false</casualInterruptible>
  </JobDef>
'''

STRINGS = [
    ("RR_BoardUp_Label", "Board it up ({0} wood)"),
    ("RR_BoardUp_Desc",
     "Send a colonist to nail {0} wood across this doorway.\\n\\nThe place behind it closes and "
     "its map is let go, which frees one of the open-map slots so somewhere else can be opened. "
     "Anything left lying in there is left in there.\\n\\nThis cannot be undone. A doorway that "
     "has been boarded up still says where it used to lead, but it does not lead there any more."),
    ("RR_BoardUp_LeadsNowhere", "This doorway does not lead anywhere that is being held open."),
    ("RR_BoardUp_NoWood", "There is not enough wood on this map to board it up."),
    ("RR_BoardUp_NobodyAvailable",
     "Nobody is free who can reach both the wood and this doorway."),
    ("RR_BoardUp_NoJobDef",
     "The boarding-up job is missing from the package. This is a packaging fault, not a "
     "situation in the game."),
    ("RR_BoardUp_Done", "{0} boarded up the doorway. The place behind it is closed and a map slot "
                        "is free."),
]

problems = 0

# ---------------------------------------------------------------------------- the gizmo
text = io.open(EMERGENCE, encoding="utf-8").read()
if "PortalBoardUp.PlaceBehind(" in text:
    print("gizmo already present")
else:
    anchor = "            bool marked = IsDesignated;"
    if text.count(anchor) != 1:
        print("cannot find the designation gizmo anchor")
        problems += 1
    else:
        at = text.index(anchor)
        io.open(EMERGENCE, "w", encoding="utf-8", newline=NL).write(
            text[:at] + GIZMO.lstrip(NL) + NL + text[at:])
        print("gizmo added to CompRimroomsEmergence")

# ---------------------------------------------------------------------------- the JobDef
text = io.open(JOBDEFS, encoding="utf-8-sig").read()
if "RR_BoardUpPortal" in text:
    print("JobDef already present")
else:
    close = "</Defs>"
    if text.count(close) != 1:
        print("cannot find the single </Defs>")
        problems += 1
    else:
        at = text.rindex(close)
        io.open(JOBDEFS, "w", encoding="utf-8", newline=NL).write(text[:at] + JOB + text[at:])
        print("JobDef added")

# --------------------------------------------------------------------------- the strings
text = io.open(KEYED, encoding="utf-8-sig").read()
added = 0
for key, value in STRINGS:
    if ("<" + key + ">") in text:
        continue
    close = "</LanguageData>"
    at = text.rindex(close)
    text = text[:at] + "  <" + key + ">" + value + "</" + key + ">" + NL + text[at:]
    added += 1
io.open(KEYED, "w", encoding="utf-8", newline=NL).write(text)
print("added %d keyed string(s)" % added)

if problems:
    sys.exit(1)
