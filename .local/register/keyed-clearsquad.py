# -*- coding: utf-8 -*-
"""The clear squad's player-facing text.

Written as a file rather than a heredoc: the prose carries apostrophes, and that trap has been
hit thirteen times.

The letter is the only account the player ever gets of what happened while nobody was conscious,
so it reports **numbers rather than adjectives** -- how many of their people the squad resolved,
how many went into the ground, what was repaired, what the paper was worth and what the bill was.
A clearance that said *"the site has been secured"* and left the player to work out that their
whole roster is dead and twenty-five million is gone would be the worst letter in the mod.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Requests.xml")

ANCHOR = u"  <RR_Contact_Call>Call the corporation</RR_Contact_Call>"

ADDITION = u"""  <RR_Event_ClearSquad>The Company cleared the laboratory, took its dead and its paper, and left three people to run it. Nobody was asked.</RR_Event_ClearSquad>
  <RR_Clear_Title>The Company cleared the site</RR_Clear_Title>
  <RR_Clear_Body>Everyone at the laboratory went down. The Company does not lose a facility, and it does not leave anybody behind who was there.

They came in on all-access passes and left no one standing. {1} of your people were resolved on site. {2} of the dead were buried on the property or put in the fire. {3} damaged structures and fixtures were brought back to full repair, and every open connection was shut down at the gate.

The paper is gone. {4} credits of bearer bonds were collected from the site and will not be seen again. A further {5} credits has been drawn from the account, recorded as restocking the petty cash.

{6} replacement staff are on the ground as of today, on the ordinary wage. The gate is still commissioned. {0} is open.</RR_Clear_Body>
  <RR_Clear_RestockingReason>Restocking the petty cash</RR_Clear_RestockingReason>
"""

text = io.open(KEYED, encoding="utf-8-sig").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(
    text.replace(ANCHOR, ADDITION + ANCHOR, 1))

after = io.open(KEYED, encoding="utf-8-sig").read()
failures = []
for key in ("RR_Event_ClearSquad", "RR_Clear_Title", "RR_Clear_Body",
            "RR_Clear_RestockingReason"):
    if (u"<%s>" % key) not in after:
        failures.append("%s is missing" % key)
# The body takes seven arguments and every index must be present, or the letter prints a
# placeholder at the player.
for index in range(7):
    if (u"{%d}" % index) not in after.split(u"<RR_Clear_Body>")[1].split(u"</RR_Clear_Body>")[0]:
        failures.append("RR_Clear_Body never uses {%d}" % index)
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("keyed strings added; the body uses all seven arguments")
