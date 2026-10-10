# -*- coding: utf-8 -*-
"""Claims and plants for setting a gate's address and opening it from the door.

Owner direction, 2026-10-04, verbatim: *"and everything that the machine needs to
start up should be able to do in the worlkd from the devices themselfes with
pawns controls and actrions not just in the opetaions tab,, ie setting the
cordinace and all of those things need  to show"*.

Five claims and five plants. The claims are written to assert the **call**, never
the callee -- a source-text claim that asserts a method exists has been the wrong
claim six times in three sessions here, every one found by a plant reporting
MISSED rather than by anybody reading it.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-starts.py"
PLANTS = ".local/register/plant-startplacement.py"

PROOF_ANCHOR = "# ---------------------------------------------- the refusals name their cause"

NEW_CLAIMS = '''# ------------------------------- setting the coordinate, and opening it, FROM THE DOOR
# Owner, 2026-10-04, verbatim: *"and everything that the machine needs to start up should be able
# to do in the worlkd from the devices themselfes with pawns controls and actrions not just in the
# opetaions tab,, ie setting the cordinace and all of those things need  to show"*.
#
# A designated gate already offered eleven commands on the door. **The two it did not offer were
# the two the owner named**: choosing which place it dials, and opening it. Both existed only as
# buttons in the pane the same message calls a text wall, so a player could build, crew and
# calibrate the machine entirely in the world and then had to go and find a tab to aim it.
_address = _file("Gate", "GateAddressControls.cs")

check("SETTING THE GATE'S ADDRESS IS A COMMAND ON THE DOOR",
      "private IEnumerable<Gizmo> AddressGizmos()" in _address
      and "foreach (Gizmo gizmo in AddressGizmos()) { yield return gizmo; }" in _gate
      and '"RR_GateAddress_SetLabel".Translate()' in _address,
      "-- DEFINED AND CALLED. A gizmo method with no caller in `CompGetGizmosExtra` is the defect "
      "class the wiring checker exists for, and it accounts for four of five bond defects")

check("and it calls THE SAME service the pane calls, with the freeze notice in front of it",
      "PortalAddressService.RegisterLaboratoryAddress(this, captured)" in _address
      and "Presentation.RimroomsGenerationNotice.Announce(captured, () =>" in _address,
      "-- a second surface on one authority, not a second derivation of one rule. And the notice "
      "needs a caller that is not waiting on a return value, which a gizmo action is and a tick "
      "is not")

check("AND OPENING IT GOES THROUGH BeginSpinUp, not straight to the opening",
      "ShowOrderResult(BeginSpinUp(captured.Id))" in _address
      and '"RR_GateAddress_OpenLabel".Translate(' in _address,
      "-- opening is *\\"a ramp up process that takes a bit of time\\"*, and there is exactly one "
      "way a laboratory gate opens whichever surface started it")

# **DISABLED, NEVER HIDDEN.** Owner's standing complaint is *"ive done like 50 things in a row and
# its still not opening"*. A command that vanishes when it cannot run teaches a player nothing.
check("and both commands grey out WITH A REASON rather than disappearing",
      'setAddress.Disable("RR_GateAddress_NoneKnown".Translate())' in _address
      and 'open.Disable("RR_GateAddress_NoAddressSet".Translate())' in _address
      and 'open.Disable("RR_GateAddress_AlreadyOpen".Translate())' in _address
      and 'open.Disable("RR_GateAddress_AlreadyRamping".Translate())' in _address
      # The commands are yielded unconditionally; only their enabled state varies.
      and _address.index("yield return setAddress;") > _address.index("setAddress.Disable(")
      and _address.index("yield return open;") > _address.index("open.Disable("),
      "-- a player who cannot find the button cannot tell whether it is blocked or missing, and "
      "the refusal is the answer to the question they are already asking")

check("AND THE FLOAT MENUS SHOW THE ADDRESS CODE, NOT THE RAW ID",
      "captured.AddressCode" in _address
      and "place.AddressCode" in _address
      and '"RR_GateAddress_Option".Translate(captured.AddressCode,' in _address,
      "-- owner: *\\"only like the !A-01 address code is needed to be displayed to thew player\\"*, "
      "and a float menu row has nowhere to put a tooltip carrying the internal identifier")

'''

PLANT_ANCHOR = "    # ------------------- the door says what to do next, in the world"

NEW_PLANTS = '''    # ------------------- setting the coordinate, and opening it, from the door
    ("THE ADDRESS COMMAND VANISHES FROM THE DOOR AGAIN", GATECOMP,
     "            foreach (Gizmo gizmo in AddressGizmos()) { yield return gizmo; }" + CHR_NL,
     "", STARTS_PROOF),

    ("the address registration skips the freeze notice", ADDRESS,
     "                        Presentation.RimroomsGenerationNotice.Announce(captured, () =>"
     + CHR_NL
     + "                            ShowOrderResult("
     + CHR_NL
     + "                                PortalAddressService.RegisterLaboratoryAddress(this, captured)));",
     "                        ShowOrderResult("
     + CHR_NL
     + "                            PortalAddressService.RegisterLaboratoryAddress(this, captured));",
     STARTS_PROOF),

    ("opening from the door bypasses the ramp", ADDRESS,
     "delegate { ShowOrderResult(BeginSpinUp(captured.Id)); }",
     "delegate { }", STARTS_PROOF),

    # **HIDDEN IS THE FAILURE, NOT DISABLED.** This is the exact shape of *"ive done like 50
    # things in a row and its still not opening"*: the control the player is hunting for is not
    # there, and nothing says why.
    ("the open command is HIDDEN instead of disabled when there is no address", ADDRESS,
     '            { open.Disable("RR_GateAddress_NoAddressSet".Translate()); }',
     "            { yield break; }", STARTS_PROOF),

    ("the address menu prints the raw coordinate id at the player again", ADDRESS,
     '                    "RR_GateAddress_Option".Translate(captured.AddressCode,',
     '                    "RR_GateAddress_Option".Translate(captured.Id,', STARTS_PROOF),

'''

ADDRESS_CONST = (
    'GATECOMP = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs"' + NL
    + '# Setting the coordinate and opening the connection, on the door. Owner, 2026-10-04:' + NL
    + '# *"ie setting the cordinace and all of those things need  to show"*.' + NL
    + 'ADDRESS = "src/RimroomsAsyncIndustries/Gate/GateAddressControls.cs"'
)

problems = 0

text = io.open(PROOF, encoding="utf-8").read()
if "_address = _file" in text:
    print("proof claims already present")
elif text.count(PROOF_ANCHOR) != 1:
    print("PROOF ANCHOR NOT UNIQUE (%d)" % text.count(PROOF_ANCHOR))
    problems += 1
else:
    io.open(PROOF, "w", encoding="utf-8", newline=NL).write(
        text.replace(PROOF_ANCHOR, NEW_CLAIMS + PROOF_ANCHOR))
    print("added 5 claims to %s" % PROOF.split("/")[-1])

text = io.open(PLANTS, encoding="utf-8").read()
if "ADDRESS =" in text:
    print("plant constant already present")
else:
    old = 'GATECOMP = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs"'
    if text.count(old) != 1:
        print("GATECOMP CONSTANT NOT UNIQUE (%d)" % text.count(old))
        problems += 1
    else:
        text = text.replace(old, ADDRESS_CONST)
        print("added the ADDRESS constant")

if "THE ADDRESS COMMAND VANISHES FROM THE DOOR AGAIN" in text:
    print("plants already present")
elif text.count(PLANT_ANCHOR) != 1:
    print("PLANT ANCHOR NOT UNIQUE (%d)" % text.count(PLANT_ANCHOR))
    problems += 1
else:
    text = text.replace(PLANT_ANCHOR, NEW_PLANTS + PLANT_ANCHOR)
    io.open(PLANTS, "w", encoding="utf-8", newline=NL).write(text)
    print("added 5 plants to %s" % PLANTS.split("/")[-1])

if problems:
    print("%d problem(s)" % problems)
    sys.exit(1)
