# -*- coding: utf-8 -*-
"""Three plants still planted faults into a feature that no longer exists.

`plant-coordinate-layout.py` carried three plants that broke the shape of a re-open. With
re-opening removed by owner direction they have nothing to mutate, and the suite refuses to run
rather than scoring them -- the harness working, and the same refusal that caught ambiguous
anchors twice before.

They are **replaced, not deleted.** The property worth guarding has inverted: it used to be *a
re-open must go through the one registration path*, and it is now *nothing may re-open a released
place at all*. So each plant RESTORES a way to re-open and requires the proof to refuse it.
Deleting them would have quietly reduced what is proved while the total still looked like it went
up.

(Written with the file's own `NL` constant rather than `\\n`: the first attempt put real newlines
inside quoted strings and the file would not parse. That file avoids backslash escapes on
purpose, and the fix is to follow its convention rather than fight it.)
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

text = io.open(PLANT, encoding="utf-8").read()

start = text.find('    ("re-opening stops using the path that created it", EMERGENCE,')
end = text.find('    ("THE HELD-PLACES PANE IS NEVER DISPATCHED TO", OPTABS,')
if start < 0 or end <= start:
    print("ANCHOR PROBLEM: could not bound the three re-open plants")
    raise SystemExit(1)

removed = text[start:end]
if "RegisterNaturalAddress" not in removed or removed.count('    ("') != 3:
    print("ANCHOR PROBLEM: that block is not the three re-open plants (%d found)"
          % removed.count('    ("'))
    raise SystemExit(1)

NEW = (
    u'    # **RE-OPENING IS GONE, SO THESE PLANTS INVERTED.** Owner: *"we do need to be able to\n'
    u'    # close natural portals u just can not re open them"*, *"thats the whole 5 limit\n'
    u'    # issue"*. They used to break the SHAPE of a re-open; each one now RESTORES a way to\n'
    u'    # re-open and requires the proof to refuse it. Replaced rather than deleted, so the\n'
    u'    # count stays honest.\n'
    u'    ("THE REOPEN METHOD COMES BACK", EMERGENCE,\n'
    u'     "        // `Reopen` lived here until 0.12.59-dev.",\n'
    u'     "        private CompanyActionResult Reopen(CoordinateRecord shelved)" + NL\n'
    u'     + "        { return PortalAddressService.RegisterNaturalAddress("\n'
    u'     + "parent, ApproachCell, shelved); }" + NL + NL\n'
    u'     + "        // `Reopen` lived here until 0.12.59-dev."),\n'
    u'\n'
    u'    ("THE REOPEN GIZMO COMES BACK", EMERGENCE,\n'
    u'     "            bool marked = IsDesignated;",\n'
    u'     "            bool marked = IsDesignated;" + NL\n'
    u'     + "            yield return new Command_Action { defaultLabel = "\n'
    u'     + chr(34) + "RR_Release_ReopenLabel" + chr(34) + ".Translate() };"),\n'
    u'\n'
    u'    ("the door stops remembering where it led, so a spent gate looks like any door",\n'
    u'     EMERGENCE,\n'
    u'     "internal string ShelvedCoordinateId { get { return shelvedCoordinateId; } }",\n'
    u'     "internal string ShelvedCoordinateIdUnused { get { return shelvedCoordinateId; } }"),\n'
    u'\n')

io.open(PLANT, "w", encoding="utf-8", newline="").write(text.replace(removed, NEW, 1))

import ast
try:
    ast.parse(io.open(PLANT, encoding="utf-8").read())
    print("three re-open plants inverted, and the file parses")
except SyntaxError as problem:
    print("STILL BROKEN: %s" % problem)
    raise SystemExit(1)
