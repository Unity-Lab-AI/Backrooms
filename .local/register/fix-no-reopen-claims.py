# -*- coding: utf-8 -*-
"""Closing a natural portal is one-way, so the proofs must assert its ABSENCE, not its shape.

Owner: *"we do need to be able to close natural portals u just can not re open them"* and
*"thats the whole 5 limit issue"*.

Removing the re-open gizmo left two things behind, and running every proof found both:

  * **`Reopen()` survived as dead code.** The gizmo that called it was gone, so nothing reached
    it -- which is exactly the shape of defect that a `…Unused` rename usually hides. It is
    deleted, not orphaned.
  * **Four claims still described re-opening**, and three of them still HELD, because the method
    they inspected was the dead one. A proof that passes by reading unreachable code is worse
    than no proof: it reports a feature that cannot happen.

Inverted rather than deleted. The claims now require that **no path re-opens a released place**,
because that is the rule the five-map limit depends on: a slot is freed by a decision that cannot
be undone, and a decision that can be undone is not a decision.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                    "CompRimroomsEmergence.cs")
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

# --------------------------------------------------------------------------- #
# 1. The dead method goes.
# --------------------------------------------------------------------------- #
comp = io.open(COMP, encoding="utf-8").read()
start = comp.find("        /// <summary>\n        /// Open the shelved place again")
if start < 0:
    print("ANCHOR PROBLEM: the Reopen summary was not found")
    raise SystemExit(1)
end = comp.find("\n        }\n", comp.find("private CompanyActionResult Reopen(", start))
if end < 0:
    print("ANCHOR PROBLEM: the Reopen body did not close")
    raise SystemExit(1)
removed = comp[start:end + len("\n        }\n")]
if "RegisterNaturalAddress" not in removed:
    print("ANCHOR PROBLEM: that is not the Reopen method -- refusing to cut it")
    raise SystemExit(1)
comp = comp.replace(removed,
                    "        // `Reopen` lived here until 0.12.59-dev. **Closing a natural portal\n"
                    "        // is one-way now** -- owner: *\"we do need to be able to close\n"
                    "        // natural portals u just can not re open them\"*, *\"thats the whole\n"
                    "        // 5 limit issue\"*. A slot is freed by a decision that cannot be\n"
                    "        // undone, because one that can be undone is not a decision.\n", 1)
io.open(COMP, "w", encoding="utf-8", newline="").write(comp)
print("the dead Reopen method is gone (%d chars)" % len(removed))

# --------------------------------------------------------------------------- #
# 2. The claims invert.
# --------------------------------------------------------------------------- #
proof = io.open(PROOF, encoding="utf-8").read()

OLD = u'''reopen_at = emergence.find("private CompanyActionResult Reopen(")
reopen_body = emergence[reopen_at:emergence.find(chr(10) + "        }", reopen_at)] \\
    if reopen_at >= 0 else ""
check("re-opening goes through the same path that first created it",
      reopen_at >= 0 and "PortalAddressService.RegisterNaturalAddress(" in reopen_body,
      "-- nothing bespoke, so there is no second implementation to drift")

check("A FAILED RE-OPEN LEAVES THE DOOR STILL OFFERING TO TRY",
      reopen_at >= 0 and "if (registered.Success) { ForgetShelvedPlace(); }" in reopen_body,
      "-- forgetting on failure would strand the place for ever over a transient refusal")

check("re-opening is refused, and visibly, when the budget is full",
      "Disabled = !room," in emergence and "RR_Release_ReopenNoRoomDesc" in emergence,
      "-- disabled rather than hidden: a player at their limit needs to see what they are at the "
      "limit of")'''

NEW = u'''# **CLOSING A NATURAL PORTAL IS ONE-WAY, AND THAT IS WHAT THE FIVE-MAP LIMIT IS FOR.**
# Owner: *"we do need to be able to close natural portals u just can not re open them"* and
# *"thats the whole 5 limit issue"*.
#
# These claims used to describe the SHAPE of a re-open. Three of them still held after the gizmo
# was removed, because the method they inspected had been left behind as dead code -- a proof
# passing by reading something unreachable, which reports a feature that cannot happen.
check("NOTHING RE-OPENS A RELEASED PLACE",
      "private CompanyActionResult Reopen(" not in emergence
      and "RR_Release_ReopenLabel" not in emergence,
      "-- a slot is freed by a decision that cannot be undone. A decision that can be undone is "
      "not a decision, and the limit would not bite")

check("and the method is deleted rather than orphaned",
      "Reopen(" not in emergence,
      "-- dead code that no gizmo reaches is exactly what a `...Unused` rename hides. If it is "
      "not reachable it should not be here")

check("THE DOOR STILL REMEMBERS WHERE IT LED, as a record and not an offer",
      "shelvedCoordinateId" in emergence and "RememberShelvedPlace" in emergence,
      "-- a player standing in front of a spent door needs to know it was a way through. Losing "
      "the memory would make a released place indistinguishable from a door that never led "
      "anywhere")'''

if proof.count(OLD) != 1:
    print("PROOF ANCHOR PROBLEM: %d" % proof.count(OLD))
    raise SystemExit(1)
proof = proof.replace(OLD, NEW, 1)

# The retired keys leave the required-strings list with them.
OLD_KEYS = u'''                "RR_Release_CrossingInFlight", "RR_Release_ReopenLabel",
                "RR_Release_ReopenNoRoomDesc", "RR_Event_CoordinateReleased", "RR_UI_Places"]'''
NEW_KEYS = u'''                "RR_Release_CrossingInFlight",
                "RR_Event_CoordinateReleased", "RR_UI_Places"]'''
if proof.count(OLD_KEYS) != 1:
    print("KEY LIST ANCHOR PROBLEM: %d" % proof.count(OLD_KEYS))
    raise SystemExit(1)
proof = proof.replace(OLD_KEYS, NEW_KEYS, 1)

OLD_SAME = u'check("the place itself is kept, so re-opening returns to the SAME place",'
NEW_SAME = u'check("the record and its rooms survive the release, so the history is not rewritten",'
if proof.count(OLD_SAME) != 1:
    print("SAME-PLACE ANCHOR PROBLEM: %d" % proof.count(OLD_SAME))
    raise SystemExit(1)
proof = proof.replace(OLD_SAME, NEW_SAME, 1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(proof)
print("four re-open claims inverted; two retired keys dropped from the required list")
