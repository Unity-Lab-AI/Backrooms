# -*- coding: utf-8 -*-
"""Is the Operations panel a utility or a novel? Measure it.

Owner direction, 2026-10-04, verbatim: *"we need to make the whole operations
panel thing alot less of a text wall its like a fucking novel when it doesnt
need to be ... all things should be done to make it more of a utility, not a
text wall"*.

**"Less of a text wall" is a number, and nothing in this battery could see it.**
Sixteen checkers and forty-nine proofs, and not one of them knew how many words
a player reads to use a pane or how many of them are things they can act on.
That is the same blind spot that let the room graph sit at an average degree of
2.2 while every proof passed: a quality nobody measures is a quality nobody can
aim at.

What it reports, per pane:

  words     total words of player-facing text the pane can draw
  reads     Label calls -- things a player reads
  acts      ButtonText / Checkbox / RadioButton calls -- things a player does
  w/act     words per action, which is the text-wall ratio
  longest   the longest single string, in words

The ratio is the headline. A pane with two hundred words and one button is a
page of prose with a button at the bottom; a pane with two hundred words and
twenty controls is a dense utility. **It exits non-zero only on a regression**
against the recorded budget below, so it can be adopted before the panel is
rewritten rather than after.

Run from the repository root.
"""
import io
import os
import re
import sys

NL = chr(10)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "UI")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed")

# The ceiling this panel must not get worse than, recorded the day it was first measured.
# Owner's direction is that these come DOWN; the budget exists so they cannot go UP while
# somebody is working on something else.
WORST_WORDS_PER_ACTION = 60.0
WORST_TOTAL_WORDS = 4200

# How many words a pane may put on screen while offering nothing to click. A heading and a
# sentence of context is a readout; a page is the thing being complained about.
WORDS_WITHOUT_AN_ACTION = 120

# **A RATCHET, PER PANE.** Owner: *"all things should be done to make it more of a utility"* --
# all of them, not the worst one. A single global budget lets one pane get worse while another
# gets better and reports nothing; this records what each pane puts on screen today and refuses
# any increase. Lower a number when the pane improves; it is the only direction the file moves.
#
# Measured 2026-10-04, immediately after the machine tab's status board replaced fourteen wrapped
# paragraphs with two lines and eleven rows (356 on-screen words to 58).
ONSCREEN_CEILING = {
    "MainTabWindow_Operations.cs": 421,
    "OperationsConnectedWork.cs": 48,
    "OperationsContractTerms.cs": 101,
    "OperationsCrewPlanner.cs": 174,
    "OperationsEvidence.cs": 183,
    "OperationsEvidenceRecovery.cs": 62,
    "OperationsExpeditions.cs": 442,
    "OperationsFacilities.cs": 312,
    "OperationsGateBinding.cs": 282,
    "OperationsGateSteps.cs": 58,
    "OperationsHeldPlaces.cs": 187,
    "OperationsHelp.cs": 225,
    "OperationsLaboratoryBinding.cs": 148,
    "OperationsPersonnel.cs": 413,
    "OperationsPortalNetwork.cs": 399,
    "OperationsProcurement.cs": 323,
    "OperationsRemoteSites.cs": 48,
    "OperationsRequests.cs": 157,
}

# The one pane where prose IS the product. Owner's complaint is that readouts read like a novel;
# the help tab is the place a player goes TO read. It is still held to its recorded ceiling.
PROSE_IS_THE_PRODUCT = ("OperationsHelp.cs",)


def keyed_strings():
    """Every keyed string in the package, by key."""
    found = {}
    if not os.path.isdir(KEYED):
        return found
    for name in sorted(os.listdir(KEYED)):
        if not name.lower().endswith(".xml"):
            continue
        text = io.open(os.path.join(KEYED, name), encoding="utf-8-sig").read()
        # **ONE LINE AT A TIME, AND `re.S` IS THE TRAP.** A dot-matches-newline search for
        # `<tag>...</tag>` matches the OUTER `<LanguageData>` wrapper first and swallows the whole
        # file, so the harvest came back with exactly one "key" named LanguageData, every word
        # count read zero, and the tool reported the panel comfortably inside its budget. **A
        # measurement that measures nothing still prints a number** -- which is the defect class
        # this tool exists to find, arriving first in the tool itself.
        for line in text.split(NL):
            match = re.match(r"\s*<([A-Za-z0-9_]+)>(.*)</\1>\s*$", line)
            if match:
                found[match.group(1)] = match.group(2)
    return found


def words_of(value):
    """Words a player actually reads: markup and placeholders are not words."""
    plain = re.sub(r"\\n", " ", value)
    plain = re.sub(r"\{[0-9]+\}", " ", plain)
    plain = re.sub(r"<[^>]+>", " ", plain)
    return len([w for w in plain.split() if any(c.isalnum() for c in w)])


def main():
    if not os.path.isdir(UI):
        print("no UI directory at %s" % UI)
        return 1
    strings = keyed_strings()

    panes = []
    for name in sorted(os.listdir(UI)):
        if not name.endswith(".cs"):
            continue
        if not (name.startswith("Operations") or name.startswith("MainTabWindow_Operations")):
            continue
        source = io.open(os.path.join(UI, name), encoding="utf-8-sig").read()

        # **ON SCREEN AND ON HOVER ARE NOT THE SAME READING, and a first version could not tell
        # them apart.** It counted every keyed string a file referenced, so moving an instruction
        # from a paragraph into a tooltip -- which is the owner's own remedy, *"with tools tips
        # would less cluter it"* -- changed the number not at all. The pane it was aimed at went
        # from fourteen wrapped paragraphs to two lines and eleven rows and still measured 356
        # words. A tool that cannot see the fix is a tool nobody will believe.
        #
        # Classified per statement rather than per line, because a `TipRegion` call routinely
        # wraps onto two or three. Keys are counted once per distinct key per bucket: the same
        # string referenced twice is not twice the reading.
        onscreen_keys = set()
        tooltip_keys = set()
        other_keys = set()
        for statement in source.split(";"):
            found = re.findall(r'"([A-Za-z0-9_]*RR_[A-Za-z0-9_]+)"\.Translate', statement)
            if not found:
                continue
            if "TipRegion" in statement or "tooltip" in statement or "Tooltip" in statement:
                tooltip_keys.update(found)
            elif (".Label(" in statement or ".ButtonText(" in statement
                  or ".CheckboxLabeled(" in statement or "Widgets.Label(" in statement
                  or ".RadioButton(" in statement):
                onscreen_keys.update(found)
            else:
                other_keys.update(found)
        # A key drawn on screen anywhere counts as on screen, whatever else also references it.
        tooltip_keys -= onscreen_keys
        other_keys -= onscreen_keys | tooltip_keys

        words = 0
        longest = 0
        longest_key = ""
        for key in sorted(onscreen_keys):
            count = words_of(strings.get(key, ""))
            words += count
            if count > longest:
                longest = count
                longest_key = key
        hover = sum(words_of(strings.get(key, "")) for key in tooltip_keys)
        elsewhere = sum(words_of(strings.get(key, "")) for key in other_keys)

        reads = len(re.findall(r"\.Label\(", source))
        acts = (len(re.findall(r"\.ButtonText\(", source))
                + len(re.findall(r"\.CheckboxLabeled\(", source))
                + len(re.findall(r"\.RadioButton\(", source))
                + len(re.findall(r"Widgets\.ButtonImage\(", source)))
        panes.append((name, words, hover, elsewhere, reads, acts, longest, longest_key))

    print("operations-density")
    print("  %-30s %6s %6s %6s %5s %5s %7s  %s"
          % ("pane", "onscr", "hover", "other", "reads", "acts", "w/act", "longest"))
    total_words = 0
    total_hover = 0
    total_reads = 0
    total_acts = 0
    worst = []
    for name, words, hover, elsewhere, reads, acts, longest, longest_key in panes:
        total_words += words
        total_hover += hover
        total_reads += reads
        total_acts += acts
        ratio = words / float(acts) if acts else float(words)
        print("  %-30s %6d %6d %6d %5d %5d %7.1f  %d (%s)"
              % (name[:30], words, hover, elsewhere, reads, acts, ratio,
                 longest, longest_key or "-"))
        # **A pane with text and nothing to click is the shape of the complaint.** Only ON-SCREEN
        # words count here: a readout whose detail lives in tooltips is the remedy, not the fault.
        if (acts == 0 and words > WORDS_WITHOUT_AN_ACTION
                and name not in PROSE_IS_THE_PRODUCT
                and name not in ONSCREEN_CEILING):
            worst.append("%s draws %d words on screen and offers nothing to click"
                         % (name, words))
        # The ratchet. A pane may improve and may not get worse.
        ceiling = ONSCREEN_CEILING.get(name)
        if ceiling is None:
            worst.append("%s is a new Operations pane with no recorded ceiling -- measure it and "
                         "add it to ONSCREEN_CEILING, or it can grow unwatched" % name)
        elif words > ceiling:
            worst.append("%s puts %d words on screen, past its recorded ceiling of %d"
                         % (name, words, ceiling))
        elif words < ceiling:
            print("        improved: %d words under the recorded ceiling of %d"
                  % (ceiling - words, ceiling))

    ratio = total_words / float(total_acts) if total_acts else float(total_words)
    print("")
    print("  %-30s %6d %6d %6s %5d %5d %7.1f"
          % ("TOTAL", total_words, total_hover, "", total_reads, total_acts, ratio))
    print("")
    print("  budget: %.1f words per action, %d words total"
          % (WORST_WORDS_PER_ACTION, WORST_TOTAL_WORDS))

    problems = []
    if ratio > WORST_WORDS_PER_ACTION:
        problems.append("words per action is %.1f, past the %.1f budget"
                        % (ratio, WORST_WORDS_PER_ACTION))
    if total_words > WORST_TOTAL_WORDS:
        problems.append("total player-facing words is %d, past the %d budget"
                        % (total_words, WORST_TOTAL_WORDS))
    problems.extend(worst)

    if problems:
        print("")
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("")
    print("OK: the Operations panel is within its reading budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
