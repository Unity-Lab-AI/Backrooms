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
#
# **TWO OF THESE WENT UP ON 2026-10-04 AND NEITHER WAS A REGRESSION.** `indirect_groups` was
# added that day and found **367 words of keyed string this tool had been counting as zero** --
# the longest instructions in the panel, picked into a variable and translated later. A ratchet
# whose baseline was measured by a blind instrument is a ratchet holding the wrong line, so the
# affected ceilings were re-measured honestly first and then brought down by the work. The
# recorded number is always what the tool last measured; it is never relaxed to make a change fit.
ONSCREEN_CEILING = {
    # 421 to 195. The longest line left is the unsupported-save warning, which stays whole on
    # screen on purpose: it is the one message a player must not be able to miss by not hovering.
    "MainTabWindow_Operations.cs": 195,
    "OperationsConnectedWork.cs": 48,
    "OperationsContractTerms.cs": 47,
    # The shared primitives themselves author no text: every string they draw arrives from the
    # pane that called them. Recorded at zero so that stays true -- a helper that starts carrying
    # its own player-facing wording is a second place for the panel's voice to live.
    "OperationsControls.cs": 0,
    # Also zero, and for the same reason: `UI/OperationsLinks.cs` is the one place a screen hands
    # the player off to a pawn, a building or the research tree. It draws nothing itself -- it
    # answers *can this link arrive* and then arrives -- so every word it is involved in is
    # charged to the pane that called it, which is where the ceiling should bite.
    "OperationsLinks.cs": 0,
    # 163 -> 164. **One word**, to make a record the branch already keeps readable where the
    # decision is made. A
    # certification the crew planner cannot show is a certification that may as well not exist,
    # and the string is already down to `Trained: {0}`. Recorded rather than absorbed.
    "OperationsCrewPlanner.cs": 164,
    # 78 -> 85. The disposition choice -- contain, release, transfer, destroy -- plus the
    # derived confidence band and the line that replaces all four once one is taken.
    # **First measured at 91 and trimmed to 82 before any raise** -- "Contain it" became
    # "Contain", "Put it back" became "Release", and the transfer button dropped "to the
    # corporation" because its tooltip says so. Seven words for four decisions the player could
    # not make at all before and a score that moves the transfer price, against a global budget
    # of 60 words per action.
    "OperationsEvidence.cs": 85,
    "OperationsEvidenceRecovery.cs": 40,
    # 442 when measured blind, 477 once the objective chain became visible, 215 after the
    # paragraphs moved to hover and the two refusals moved onto the controls they refuse.
    "OperationsExpeditions.cs": 215,
    "OperationsFacilities.cs": 229,
    "OperationsGateBinding.cs": 189,
    "OperationsGateSteps.cs": 58,
    "OperationsHeldPlaces.cs": 86,
    "OperationsHelp.cs": 225,
    "OperationsLaboratoryBinding.cs": 61,
    # 413 to 217. 130 of those words were in `PersonnelView` and `Dialog_ConfirmApplicantHire`,
    # neither of which could reach the primitives until they stopped being private to the window.
    # 217 -> 218. One word, and it buys the pawn deep
    # link: this pane holds the richest readout of a person anywhere in the package and had no
    # way to go and look at them. One word, for a control that replaces closing Operations and
    # hunting the colony by hand. Recorded rather than absorbed, which is what the ratchet is for.
    "OperationsPersonnel.cs": 218,
    "OperationsPortalNetwork.cs": 288,
    "OperationsProcurement.cs": 262,
    "OperationsRemoteSites.cs": 48,
    # **102 -> 123, AND THIS ONE WAS A REAL MISS BEFORE IT WAS A RAISE.** The quest ledger landed
    # in the journal batch at 0.12.99-dev and **this checker was not run on it**, so the tree
    # carried a failing ratchet through two commits. Found on the next run, measured rather than
    # argued about, and the +61 words were entirely the new section.
    #
    # **Trimmed before raised, twice over.** First the shape: the ledger's next-step line was four
    # separate `listing.Label` statements, which this tool correctly charges as the SUM -- 56 words
    # a player can never see together, because exactly one branch draws per frame. Rewritten as an
    # indirect group it is charged at the maximum, which is the worst line a player can actually
    # meet. Then the wording: the three longest lines came down from 22, 14 and 13 words to 16, 6
    # and 10.
    #
    # What is left is **21 words for a complete index of every accepted quest** -- its filing
    # progress, its light, and the one thing it needs next -- which the owner asked for in those
    # terms: *"every book recieved needs to be ... capable of listing the current quests its needed
    # for that has been acceptred, with ability to accept more than one quests at a time"*. Against
    # a global budget of 60 words per action, a section that answers *what have I taken on and what
    # does each one want from me* is the utility this panel is supposed to be.
    "OperationsRequests.cs": 123,
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


def without_comments(source):
    """The C# source with its comments removed, string literals intact.

    ## A COMMENT CHANGED A MEASUREMENT, AND IT WAS THIS FILE'S OWN WORD THAT DID IT

    Classification reads each statement for the words `TipRegion` / `tooltip` /
    `Tooltip` to decide whether a string is drawn or hovered. A comment written
    above `listing.Label("RR_Sites_Heading".Translate())` happened to contain the
    sentence *"a tooltip that reports state is a tooltip that lies"* -- and the
    heading was reclassified as hover text. Seven words, in the right direction,
    for entirely the wrong reason.

    The same hazard runs the other way and is worse: a commented-out `.Label(`
    call counts as a read, so deleting a draw by commenting it out would leave
    the pane measuring exactly as before.

    So the scan reads code only. Written as a scanner rather than a regex because
    `//` inside a string literal is ordinary text and a regex cannot tell the
    difference -- which is the same reason the keyed-string harvest in this file
    reads one line at a time instead of using `re.S`.
    """
    out = []
    index = 0
    length = len(source)
    while index < length:
        character = source[index]
        if character == '"':
            out.append(character)
            index += 1
            while index < length:
                if source[index] == "\\":
                    out.append(source[index:index + 2])
                    index += 2
                    continue
                out.append(source[index])
                if source[index] == '"':
                    index += 1
                    break
                index += 1
            continue
        if source.startswith("//", index):
            while index < length and source[index] != NL:
                index += 1
            continue
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            index = length if end == -1 else end + 2
            continue
        out.append(character)
        index += 1
    return "".join(out)


def indirect_groups(source):
    """Keys the pane picks into a variable and translates later, grouped.

    ## 367 WORDS THIS TOOL COULD NOT SEE, AND THEY WERE THE WORST WORDS IN THE PANEL

    The expedition pane's objective line reads

        if (...) { key = "RR_UI_NextAssembly"; }
        else if (...) { key = "RR_UI_NextCalibration"; }
        ...
        listing.Label(key.Translate());

    Thirteen strings of seventeen to fifty-seven words each. The per-statement
    scan sees `key = "RR_UI_NextAssembly"` with no `.Translate` in it and counts
    nothing, and sees `listing.Label(key.Translate())` with no literal in it and
    counts nothing. **So the longest instructions in the Operations panel measured
    zero**, and the pane that carries them reported 442 words while drawing more
    than that. This is the defect class the header of this file names arriving in
    the file a second time: a measurement that measures nothing still prints a
    number.

    ## Counted at the MAXIMUM of the group, not the sum

    Exactly one branch of that chain draws per frame, so a player never reads the
    sum and charging the pane for it would make the budget unmeetable by
    construction. The honest figure is the **worst line the pane can show**, which
    is what a player meets on their unluckiest visit. Summing a group would also
    punish the right fix -- adding a clearer alternative to a chain -- which is how
    a budget stops being believed.

    Returns a list of key sets, one per identifier that is translated inside an
    on-screen call. An identifier used only in a tooltip is a hover group and is
    returned separately by the caller's own classification, which this does not
    duplicate.
    """
    assignments = {}
    for identifier, key in re.findall(
            r"(\b[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\"(RR_[A-Za-z0-9_]+)\"", source):
        assignments.setdefault(identifier, set()).add(key)
    if not assignments:
        return [], []
    onscreen, hover = [], []
    for identifier in sorted(assignments):
        # Word-bounded, so `key` does not match `monkey` and `stepKey` does not
        # match `key`.
        drawn = re.compile(r"\b%s\s*\.\s*Translate" % re.escape(identifier))
        # The same argument labels the direct scan reads, but with a variable on
        # the right rather than a literal -- `heading: brief.Translate()`. Without
        # this the shared primitives would hide an indirect group completely:
        # the statement carries no `RR_` literal for the direct scan to find and
        # no `.Label(` for the fallback below to recognise.
        labelled = re.compile(
            r"\b(heading|label|detail|refusal)\s*:\s*%s\s*\.\s*Translate" % re.escape(identifier))
        for statement in source.split(";"):
            if not drawn.search(statement):
                continue
            argument = labelled.search(statement)
            if argument:
                if argument.group(1) in ("heading", "label"):
                    onscreen.append(assignments[identifier])
                else:
                    hover.append(assignments[identifier])
                continue
            if "TipRegion" in statement or "ooltip" in statement:
                hover.append(assignments[identifier])
            elif (".Label(" in statement or ".ButtonText(" in statement
                  or ".CheckboxLabeled(" in statement or "Widgets.Label(" in statement
                  or ".RadioButton(" in statement
                  or "DrawHeading(" in statement or "DrawAction(" in statement):
                # **A POSITIONAL CALL TO A PRIMITIVE COUNTS AS ON SCREEN.** The
                # pessimistic bucket on purpose: a call that forgot its argument
                # labels should over-report, never disappear. Disappearing is the
                # failure mode this whole function exists to end.
                onscreen.append(assignments[identifier])
    return onscreen, hover


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
        # **CODE ONLY.** A `///` doc block describing what a pane draws is not a thing a player
        # reads, and leaving it in let one comment's prose move a heading into the hover bucket.
        source = without_comments(io.open(os.path.join(UI, name), encoding="utf-8-sig").read())

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
            # **THE SHARED PRIMITIVES ARE READ BY ARGUMENT LABEL.**
            # `UI/OperationsControls.cs` gives every pane one `DrawHeading` and one `DrawAction`,
            # and each takes a short line that draws and a full text that hovers -- in ONE
            # statement. Classifying that statement as a whole would put both keys in the same
            # bucket and make the panel's own house style unmeasurable, so the call sites name
            # their arguments and this reads the names. `heading:` and `label:` draw; `detail:`
            # and `refusal:` hover.
            #
            # **READ BY SEGMENT, NOT BY ADJACENCY, and the adjacent version got it wrong on its
            # first real call site.** A refusal is routinely conditional --
            # `refusal: gate == null ? "RR_X".Translate() : TaggedString.Empty` -- so the key is
            # not the token after the label. The statement is cut at each argument label and
            # every key inside a segment belongs to that argument. Keys before the first label
            # are counted as on-screen, which is the pessimistic side on purpose.
            labels = [(found.start(), found.group(1)) for found in
                      re.finditer(r"\b(heading|label|detail|refusal)\s*:", statement)]
            if labels:
                for position, (start, argument) in enumerate(labels):
                    end = labels[position + 1][0] if position + 1 < len(labels) else len(statement)
                    segment = statement[start:end]
                    keys = re.findall(r'"([A-Za-z0-9_]*RR_[A-Za-z0-9_]+)"\.Translate', segment)
                    if argument in ("heading", "label"):
                        onscreen_keys.update(keys)
                    else:
                        tooltip_keys.update(keys)
                leading = re.findall(r'"([A-Za-z0-9_]*RR_[A-Za-z0-9_]+)"\.Translate',
                                     statement[:labels[0][0]])
                onscreen_keys.update(leading)
                continue
            if "TipRegion" in statement or "tooltip" in statement or "Tooltip" in statement:
                tooltip_keys.update(found)
            elif (".Label(" in statement or ".ButtonText(" in statement
                  or ".CheckboxLabeled(" in statement or "Widgets.Label(" in statement
                  or ".RadioButton(" in statement
                  or "DrawHeading(" in statement or "DrawAction(" in statement):
                onscreen_keys.update(found)
            else:
                other_keys.update(found)
        # A key drawn on screen anywhere counts as on screen, whatever else also references it.
        tooltip_keys -= onscreen_keys
        other_keys -= onscreen_keys | tooltip_keys

        indirect_onscreen, indirect_hover = indirect_groups(source)
        # A group's keys are alternatives of one line, so they are not also loose keys.
        grouped = {key for group in indirect_onscreen + indirect_hover for key in group}
        onscreen_keys -= grouped
        tooltip_keys -= grouped
        other_keys -= grouped

        words = 0
        longest = 0
        longest_key = ""
        for key in sorted(onscreen_keys):
            count = words_of(strings.get(key, ""))
            words += count
            if count > longest:
                longest = count
                longest_key = key
        for group in indirect_onscreen:
            worst_key = max(group, key=lambda k: words_of(strings.get(k, "")))
            count = words_of(strings.get(worst_key, ""))
            words += count
            if count > longest:
                longest = count
                longest_key = worst_key + " (worst of %d)" % len(group)
        hover = sum(words_of(strings.get(key, "")) for key in tooltip_keys)
        hover += sum(max(words_of(strings.get(key, "")) for key in group)
                     for group in indirect_hover)
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
