# -*- coding: utf-8 -*-
"""Five budget claims were loose enough for a plant to walk through. Tighten all five.

Each miss is the same family this project keeps meeting:

  * `Prefs.MaxNumberOfPlayerSettlements` survived being deleted from the CODE because the name is
    also in the doc comment above it -- a comment satisfied a claim.
  * `RR_Frontier_TooManyGatesHeld` is a PREFIX of `RR_Frontier_TooManyGatesHeldUnused`, so
    renaming the tag left the claim satisfied. Sixth time a prefix has done this.
  * three claims read the whole FILE where they meant one method BODY, so deleting the use while
    leaving the declaration, or changing a line with a common shape like `return false;`, was
    invisible.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

text = io.open(PROOF, encoding="utf-8").read()

EDITS = [
    # 1. Read the property BODY, with comments stripped, not the whole file.
    ('''check("THE BUDGET IS READ FROM THE GAME'S OWN COLONY LIMIT, NOT HARD-CODED",
      "Prefs.MaxNumberOfPlayerSettlements" in budget
      and "= 5;" not in budget,''',
     '''# The BODY of the Budget property, comments stripped. The first version of this claim read the
# whole file and passed a plant that replaced the pref with a literal 5 in the code -- because the
# pref's NAME is also in the doc comment directly above it. A comment satisfied a claim about code.
budget_code = re.sub(r"///.*", "", budget)
budget_code = re.sub(r"//.*", "", budget_code)
budget_at = budget_code.find("internal static int Budget")
budget_body = budget_code[budget_at:budget_code.find(chr(10) + "        }", budget_at)] \\
    if budget_at >= 0 else ""
check("THE BUDGET IS READ FROM THE GAME'S OWN COLONY LIMIT, NOT HARD-CODED",
      budget_at >= 0
      and "Prefs.MaxNumberOfPlayerSettlements" in budget_body
      and not re.search(r":\\s*\\d+\\s*;", budget_body),'''),

    # 2. The exact tag, not a prefix of it.
    ('''check("the refusal says what the owner said",
      "RR_Frontier_TooManyGatesHeld" in keyed
      and "holding open too many gates" in keyed
      and "RR_Frontier_TooManyGatesHeld" in budget,''',
     '''check("the refusal says what the owner said",
      "<RR_Frontier_TooManyGatesHeld>" in keyed
      and "</RR_Frontier_TooManyGatesHeld>" in keyed
      and "holding open too many gates" in keyed
      and 'BlockedKey = "RR_Frontier_TooManyGatesHeld"' in budget,'''),

    # 3 and 4. The deciding function's own body, so a deleted USE is visible.
    ('''check("WAYS ONWARD SCALE WITH THE SIZE OF THE PLACE",
      "MinimumFrontiersPerCoordinate = 4" in frontier
      and "MaximumFrontiersPerCoordinate = 6" in frontier
      and "Cap = FrontiersFor(record)" in frontier,''',
     '''frontiers_at = frontier.find("internal static int FrontiersFor(CoordinateRecord coordinate)")
frontiers_body = frontier[frontiers_at:frontier.find(chr(10) + "        }", frontiers_at)] \\
    if frontiers_at >= 0 else ""
check("WAYS ONWARD SCALE WITH THE SIZE OF THE PLACE",
      "MinimumFrontiersPerCoordinate = 4" in frontier
      and "MaximumFrontiersPerCoordinate = 6" in frontier
      and "Cap = FrontiersFor(record)" in frontier
      and "coordinate.Rooms.Count" in frontiers_body
      and "Depth" not in frontiers_body,'''),

    ('''depth_reach = re.search(r"MaximumNaturalDepth\\s*=\\s*(\\d+)", frontier)''',
     '''check("THE CEILING ON WAYS ONWARD IS ACTUALLY APPLIED, NOT MERELY DECLARED",
      frontiers_at >= 0 and "MaximumFrontiersPerCoordinate" in frontiers_body,
      "-- a plant that deleted the clamp while leaving the constant walked past the first "
      "version of this, which only asked whether the constant existed. A chain of spaces still "
      "has to be finite")

depth_reach = re.search(r"MaximumNaturalDepth\\s*=\\s*(\\d+)", frontier)'''),

    # 5. The method body, because `return false;` is a shape the file uses several times.
    ('''check("A COORDINATE MAP IS STILL NEVER UNLOADED, WHICH IS WHY A CAP IS NEEDED AT ALL",
      "public override bool ShouldRemoveMapNow(out bool alsoRemoveWorldObject)" in parent
      and "return false;" in parent,''',
     '''# The method body alone. `return false;` appears several times in this file -- CanBeSettled,
# GravShipCanLandOn, InitializeCoordinate -- so a plant that flipped THIS one to true left the
# string present elsewhere and the claim satisfied.
remove_at = parent.find("public override bool ShouldRemoveMapNow(out bool alsoRemoveWorldObject)")
remove_body = parent[remove_at:parent.find(chr(10) + "        }", remove_at)] \\
    if remove_at >= 0 else ""
check("A COORDINATE MAP IS STILL NEVER UNLOADED, WHICH IS WHY A CAP IS NEEDED AT ALL",
      remove_at >= 0 and "return false;" in remove_body and "return true;" not in remove_body,'''),
]

problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("five loose claims tightened")
