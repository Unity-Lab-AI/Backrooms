#!/usr/bin/env python3
"""Work out WHICH campaign-integrity check a save fails, because the game will not say.

`RimroomsCampaignComponent.ValidateSavedState` tests about a dozen distinct conditions and collapses
every one of them into a single fault key, then logs:

    [Rimrooms][Save] Campaign integrity failed; company actions are disabled. Preserve the original save.

**That message names no cause**, in a mod whose own troubleshooting page promises *"Every refusal in
the game names its own cause. Read it -- the cause is the instruction."* A player meeting this has
their company switched off and nothing to act on; so did I, which is why this exists.

So the same checks are re-run here against the save file's own XML, one at a time, and the ones that
fail are named. Read-only: it opens the save and computes, and writes nothing anywhere.

**The first guess was wrong and is recorded so it is not repeated.** The log line immediately above
the failure is `Could not resolve reference to object with loadID Thing_Human270 of type Verse.Pawn`,
which looks like the cause and is not: that id appears once in the whole file, inside a pawn's
vanilla `<social><directRelations>` as a `Parent`. It is ordinary RimWorld relation data about a
relative who is not in the save. Adjacency in a log is not causation.

Usage:
    python .local/qa/diagnose-campaign-integrity.py "<save name without extension>"
"""
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

SAVES = os.path.expanduser(
    "~/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves")


def campaign_block(text):
    """The RimroomsCampaignComponent element, as XML text, or None.

    **A non-greedy `.*?</li>` CANNOT extract this and the first version tried.** The component is
    hundreds of nested `<li>` elements deep -- staff, ledger, contracts, coordinates -- so the first
    `</li>` it meets belongs to a child, and the captured text is a fragment with mismatched tags.
    It failed with *"mismatched tag: line 21"*, which is the parser being right.

    So the opening tag is found and `<li` / `</li>` are **balanced** forward from it. Depth counting
    rather than a regex, because the structure is recursive and a regex cannot count.
    """
    start = None
    for match in re.finditer(r"<li Class=\"[^\"]*RimroomsCampaignComponent\"\s*>", text):
        start = match.start()
        break
    if start is None:
        return None
    depth = 0
    position = start
    opener = re.compile(r"<li\b[^>]*?(/?)>|</li>")
    while position < len(text):
        found = opener.search(text, position)
        if found is None:
            return None
        token = found.group(0)
        position = found.end()
        if token.startswith("</li"):
            depth -= 1
            if depth == 0:
                return text[start:position]
        elif found.group(1) == "/":
            continue            # `<li />` opens and closes in one token.
        else:
            depth += 1
    return None


def text_of(node, tag, default=""):
    found = node.find(tag)
    return (found.text or default).strip() if found is not None else default


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    name = argv[0]
    path = os.path.join(SAVES, name + ".rws")
    if not os.path.isfile(path):
        print("no such save: %s" % path)
        return 1

    text = io.open(path, encoding="utf-8", errors="replace").read()
    print("save      : %s" % name)
    print("size      : %.1f MB" % (len(text) / 1048576.0))

    block = campaign_block(text)
    if block is None:
        print("RESULT    : no RimroomsCampaignComponent found in this save at all.")
        print("            That is itself the answer: there is no campaign to validate.")
        return 0

    try:
        root = ET.fromstring(block)
    except ET.ParseError as error:
        print("RESULT    : the campaign block does not parse as XML (%s)" % error)
        return 1

    problems = []

    # ---- the ledger, which is the check most likely to fail on a long save -----------------
    entries = root.findall(".//ledger/li")
    print("ledger    : %d entry(s)" % len(entries))
    running = 0
    seen = set()
    for index, entry in enumerate(entries, start=1):
        operation = text_of(entry, "operationId")
        amount_text = text_of(entry, "amountUsd", "0")
        after_text = text_of(entry, "balanceAfterUsd", "0")
        try:
            amount = int(amount_text or 0)
            after = int(after_text or 0)
        except ValueError:
            problems.append("entry %d has a non-integer amount/balance (%r / %r)"
                            % (index, amount_text, after_text))
            continue
        if not operation:
            problems.append("entry %d has an empty operationId" % index)
        elif operation in seen:
            problems.append("entry %d repeats operationId %r -- a duplicate is a double payment "
                            "waiting to happen" % (index, operation))
        seen.add(operation)
        running += amount
        if running < 0:
            problems.append("entry %d drives the running balance negative (%d)" % (index, running))
        if after != running:
            problems.append("entry %d records balanceAfterUsd=%d but the running total is %d"
                            % (index, after, running))

    balance_text = text_of(root, "balanceUsd", "0")
    try:
        balance = int(balance_text or 0)
    except ValueError:
        balance = None
        problems.append("balanceUsd is not an integer (%r)" % balance_text)
    if balance is not None:
        print("balance   : recorded %d, ledger sums to %d" % (balance, running))
        if balance != running:
            problems.append("balanceUsd %d does not equal the ledger total %d" % (balance, running))

    insights = text_of(root, "researchInsights", "0")
    overhead = text_of(root, "dailyOverheadUsd", "0")
    if insights and insights.lstrip("-").isdigit() and int(insights) < 0:
        problems.append("researchInsights is negative (%s)" % insights)
    if overhead and overhead.lstrip("-").isdigit() and int(overhead) < 0:
        problems.append("dailyOverheadUsd is negative (%s)" % overhead)

    complete = text_of(root, "initializationComplete", "False").lower() == "true"
    branch = text_of(root, "branchId")
    receipt = text_of(root, "initializationReceipt")
    if complete and (not branch or not receipt):
        problems.append("initializationComplete is true but branchId/initializationReceipt is empty")

    # ---- the uniqueness checks ------------------------------------------------------------
    for collection in ("staff", "obligations", "contracts", "coordinates",
                       "cases", "evidence", "projects"):
        ids = [text_of(item, "id") for item in root.findall(".//%s/li" % collection)]
        present = [i for i in ids if i]
        duplicates = sorted(set(i for i in present if present.count(i) > 1))
        print("%-10s: %d record(s)%s"
              % (collection, len(ids), ", DUPLICATE ids: %s" % ", ".join(duplicates[:4])
                 if duplicates else ""))
        if duplicates:
            problems.append("%s has duplicate ids: %s" % (collection, ", ".join(duplicates[:6])))
        if len(present) != len(ids):
            problems.append("%s has %d record(s) with an empty id" % (collection, len(ids) - len(present)))

    for member in root.findall(".//staff/li"):
        wage = text_of(member, "dailyWageUsd", "0")
        if wage.lstrip("-").isdigit() and int(wage) < 0:
            problems.append("a staff record has a negative dailyWageUsd (%s)" % wage)
    for obligation in root.findall(".//obligations/li"):
        amount = text_of(obligation, "amountUsd", "1")
        if amount.lstrip("-").isdigit() and int(amount) <= 0:
            problems.append("an obligation has amountUsd <= 0 (%s)" % amount)

    print("")
    if problems:
        print("FAILS %d CHECK(S):" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("EVERY CHECK RE-RUN HERE PASSES.")
    print("So the fault is in a condition this script does not reproduce -- most likely")
    print("ValidateRecordRelationships, which resolves logical owners between collections.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
