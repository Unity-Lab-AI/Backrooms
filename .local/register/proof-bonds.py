# -*- coding: utf-8 -*-
"""The bonds: a name that is their value, a correct value, a way back in, and a way to combine.

Why this proof exists
---------------------
**Nothing in this battery had ever made a single claim about bonds.** Forty-five proofs, sixteen
plant suites, seventeen checkers, and `grep -l Bond` over all of them returned nothing. That is
why five separate defects shipped in one feature and the owner found all of them in one sitting:

  * `CompRimroomsBond.TransformLabel` **had never run.** `Verse.Book` overrides `LabelNoCount` as
    `title + GenLabel.LabelExtras(...)` and never walks `comps`, so every bond ever issued showed
    a randomly generated novel title and a quality suffix. Owner: *"now the books as bonds just
    say noprmal the quality which is normal"*.
  * The value was a `Novel`'s `MarketValue 160`. A million-credit bond was a hundred and sixty
    silver of paper. Owner: *"value is not correct"*.
  * `RedeemBondsInRadius` worked and had **exactly one caller**, a credit beacon, so a player
    without one had no route to put paper back at all. Owner: *"the bonds i pull out i dont sdeem
    to be able to put them back in"*.
  * Combining did not exist. Owner: *"and and to combine them"*.
  * The description was a sentence about banking at a beacon. Owner: *"and better description"*.

Four of those five are the same shape: **built, correct, and unreachable.** It is this project's
most repeated defect and the only thing that catches it is a claim that asserts something is
*called*, not merely that it exists.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(*parts):
    return io.open(os.path.join(*parts), encoding="utf-8-sig").read()


def no_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


paper = no_comments(read(SRC, "Economy", "BondPaper.cs"))
comp = no_comments(read(SRC, "Economy", "CompRimroomsBond.cs"))
service = no_comments(read(SRC, "Economy", "BondService.cs"))
handling = no_comments(read(SRC, "Economy", "BondHandling.cs"))
treasury = no_comments(read(SRC, "Company", "BondTreasury.cs"))
text = read(KEYED, "RR_Bonds.xml")

print("")

# --------------------------------------------------------------- the name is the value
check("THE LABEL IS OVERRIDDEN ON THE CARRIER, NOT RETURNED FROM A COMP HOOK",
      "public class Book_RimroomsBond : Book" in paper
      and "public override string LabelNoCount" in paper
      # **BOTH OVERRIDES, COUNTED.** The label expression appears in `LabelNoCount` and in
      # `LabelNoParenthesis`, so a plant that gutted the first one left the second standing and
      # this claim held while no bond was named. Duplicate-string trap; counted rather than found.
      and paper.count(
          '"RR_Bond_Label".Translate(CreditDenominations.ShortName(bond.FaceValue))') == 2
      # The dead hook is GONE, not merely bypassed. Keeping it reads like the bug is fixed.
      and "TransformLabel" not in comp,
      "-- `Verse.Book.LabelNoCount` is `title + GenLabel.LabelExtras(...)` and never walks "
      "`comps`, so the comp hook could not name a bond and never did. A method that cannot be "
      "called is worse than the bug it was meant to fix")

check("and the carrier's thingClass is actually assigned",
      "bond.thingClass = typeof(Book_RimroomsBond);" in service
      and "if (bond.thingClass == typeof(Book) || bond.thingClass == null)" in service,
      "-- **DEFINED AND CALLED.** A Def field, which is the boundary `check-compliance.py` "
      "states. The first attempt wrote Book's private `title` by reflection and that checker "
      "refused it: *a SetValue into a game type is a game-assembly modification no dependency "
      "list would show*")

check("and an ordinary novel keeps its own name",
      "return base.LabelNoCount;" in paper
      and "return bond != null && bond.IsBond ? bond : null;" in paper,
      "-- the repurposing has to cost the player nothing. Every member defers to base unless the "
      "thing carries a stamped face value")

check("AND THE LABEL IS THE VALUE SAID IN WORDS",
      "<RR_Bond_Label>{0} credit bearer bond</RR_Bond_Label>" in text,
      "-- *\"they need a name that is theri value\"*. The exact figure is on the inspect line and "
      "in the description; the name is how a person would say it")

# --------------------------------------------------------------- the value is correct
check("A BOND IS WORTH ITS FACE VALUE",
      "public sealed class StatPart_RimroomsBondValue : StatPart" in paper
      and "if (face > 0L) { value = face; }" in paper
      and "market.parts.Add(valuePart);" in service
      and "!market.parts.Any(part => part is StatPart_RimroomsBondValue)" in service,
      "-- **DEFINED AND ADDED TO THE STAT.** A `Novel` is `MarketValue 160`, so a million-credit "
      "bond was a hundred and sixty silver of paper. The face value lives per instance, so no "
      "entry on a def can express it and a StatPart is the only mechanism that reads the thing")

check("and it is additive: every other object answers as before",
      "if (!request.HasThing) { return 0L; }" in paper
      and "return bond == null || !bond.IsBond ? 0L : bond.FaceValue;" in paper,
      "-- `MarketValue`'s own parts are untouched. An ordinary novel, and everything in every "
      "other mod, gets the same number it got before")

# --------------------------------------------------------------- back in, and combined
check("A BOND CAN BE PUT BACK IN FROM THE PAPER ITSELF",
      "public static CompanyActionResult Deposit(Thing bond)" in handling
      and "campaign.DepositBondPaper(" in handling
      and "internal CompanyActionResult DepositBondPaper(" in treasury
      and "BondHandling.Deposit(parent)" in comp,
      "-- **DEFINED AND CALLED, from a gizmo on the bond.** `RedeemBondsInRadius` worked and had "
      "exactly one caller -- a credit beacon -- so a player who had not built one had no route "
      "anywhere. Same shape as `Discover` having no callers")

check("AND SEVERAL CAN BE COMBINED INTO FEWER",
      "public static CompanyActionResult Combine(Thing anchor)" in handling
      and "campaign.CombineBondPaper(" in handling
      and "internal CompanyActionResult CombineBondPaper(" in treasury
      and "BondHandling.Combine(parent)" in comp,
      "-- **DEFINED AND CALLED.** *\"and and to combine them\"*")

check("and combining conserves value through the ledger, in two halves of one operation",
      'PostTransaction(operationId + ".in", destroyed,' in treasury
      and 'PostTransaction(operationId + ".out", -payable,' in treasury
      and 'PostTransaction(operationId + ".unplaced", unplaced,' in treasury,
      "-- the paper is credited, the replacement is debited, and anything that could not be "
      "placed stays credited. The ledger is the only thing in this mod that cannot lose a "
      "credit, which is why this does not simply swap objects")

check("and it uses the one decomposition every other payout uses",
      "CreditDenominations.Decompose(destroyed, out remainder)" in treasury
      and "CreditDenominations.Decompose(total, out remainder)" in handling,
      "-- fewest bonds, largest first. A second arithmetic for the same question is the defect "
      "this project keeps meeting")

check("and it refuses rather than shredding a pile it cannot improve",
      '"RR_Bond_NothingToCombine"' in handling
      and '"RR_Bond_AlreadyCombined"' in handling
      and "if (wanted >= paper.Count && remainder <= 0L)" in handling,
      "-- destroying and recreating the same pile is not work, and a silent no-op is how a "
      "player concludes a button is broken")

check("AND EVERY REFUSAL IS SAID OUT LOUD",
      "private void Show(CompanyActionResult result)" in comp
      # **THE CALL REACHED, not the call written.** A plant prefixing `if (false) ` left every
      # asserted character in place and the refusal went silent. Pinned to the line above it, in
      # order, so the guard cannot be slipped in between.
      and ("            if (result.Success) { return; }" + chr(10)
           + '            Messages.Message((result.MessageKey ?? "RR_Bond_NoneInRange").Translate(),')
      in comp,
      "-- a gizmo that refuses in silence is the thing that cost the owner an afternoon on the "
      "gate")

# --------------------------------------------------------------- the description
check("THE DESCRIPTION IS THE INSTRUMENT, AND IT NAMES BOTH NEW ACTIONS",
      "COMPANY BEARER BOND" in text
      and "Face value: {0} credits." in text
      and "press Deposit" in text
      and "combined into the fewest" in text
      and "<RR_Bond_Flavour>" in text,
      "-- *\"and better description\"*. It previously told the player to bank it at a credit "
      "beacon and nothing else, which was the only route that existed and the one they did not "
      "have")

check("and the comp still supplies the description and the inspect line",
      "public override string CompInspectStringExtra()" in comp
      and "public override string GetDescriptionPart()" in comp,
      "-- those two hooks ARE consulted on a `Book`, which is why they always worked and the "
      "label never did")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a bond is named for its value, worth its value, can be put back in, and can "
      "be combined")
