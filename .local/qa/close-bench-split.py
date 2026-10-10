# -*- coding: utf-8 -*-
"""Close the bench-split row and the partial row whose second half it was."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

# (marker, key, evidence) -- the partial row carries `[~]` and the open row `[ ]`.
ROWS = [
    ("- [ ] ", "**Four machine benches: split the gate's component count across the linked benches.**",
     " -- **BUILT 0.12.99-dev, AND THE NAMED COST IS ANSWERED BY NOT EXISTING.** "
     "**The assembly is four sections**: 25 steel, 2 industrial components and 1500 work each, "
     "against the one bill of 100 steel, 8 components and 6000 work it replaced. "
     "**THE TOTAL IS IDENTICAL AND THAT IS ASSERTED RATHER THAN INTENDED** -- section cost times "
     "section count must equal the historical figures, so a future edit that makes four sections "
     "cost 30 steel each fails a proof instead of quietly taxing the player twenty per cent. "
     "**The cost the fork named was *" + Q + "a destroyed or unlinked bench leaves an unfinishable "
     "remainder" + Q + "*, and the row's own answer was to recompute the split when the set of "
     "benches changes. IT IS BETTER THAN THAT: a section is never allocated to a bench at all.** "
     "The count lives on the gate and any bound bench installs the next one, so there is nothing to "
     "recompute -- destroy a bench mid-build and its unfinished sections are simply still "
     "outstanding, queueable anywhere including on the designated bench alone. **An allocation that "
     "cannot be orphaned beats one that is redistributed correctly, because the redistributing is "
     "the part that would have had the bugs.** The proof asserts the ABSENCE of per-bench state, "
     "which is the only form that claim can take. "
     "**One recipe def, four iterations, not four defs** -- four defs would be four places stating "
     "the section cost and they would disagree the first time one was edited. The repeat count is "
     "the player's: four on one bench, or one on each of four. "
     "**ONE QUESTION DECIDES A BENCH ON BOTH SIDES.** `IsBoundAssemblyBench` is asked by the "
     "recipe's `AvailableOnNow` and by `CompleteAssemblyFromBill`, deliberately: offering a section "
     "at a bench that is then refused the credit is a pawn carrying twenty-five steel across the "
     "base for nothing, and that is exactly the shape a second derivation produces. "
     "**AND THE BILL NO LONGER SUSPENDS ITSELF AFTER ONE SECTION.** The recipe worker called "
     "`MarkAssemblyBillComplete` on any success, which was correct for the whole life of the "
     "single-bill assembly and would have stopped a four-section build dead after the first with "
     "the bill suspended and nothing anywhere saying why. The gate suspends **every** bound bench's "
     "bill itself, once, when the last section lands -- all four, because three repeating bills left "
     "running would spend another seventy-five steel on a gate that is already built. "
     "**A save written before the split loads correctly**: a finished gate reads as four of four "
     "rather than nought of four, and the count is clamped at both ends. "
     "**Instruments: proof 62 `proof-gate-assembly-split.py` and plant suite 39, 22 of 22 caught** "
     "-- and the suite earned its keep immediately. **It found a real hole in my own proof:** three "
     "ordering claims were bare `find(...) < find(...)` comparisons, and Python's `find` returns "
     "**-1** for absent, which is less than every real index. So deleting the guarded line made the "
     "claim pass, and the plant that marked the gate complete on its first section was **MISSED**. "
     "Hardened into an `ordered()` helper that fails on absence as well as inversion. **That is the "
     "fourth time in this repository a rule has been satisfied by the thing it was watching for "
     "simply not being there.** One plant was also wrong before the rule was -- it inserted an XML "
     "comment, and the proof strips comments before reading, correctly."),

    ("- [~] ", "**Up to four consoles, and the same for the machine benches.**",
     " -- **NOW CLOSED 0.12.99-dev: THE BENCH HALF IS BUILT AND THE WIKI GAP THE CONSOLE HALF LEFT "
     "IS FIXED.** `RR_Link_GateAssembly`, `TableMachining`, `maxLinked` **3** -- the designated "
     "bench is the first of the four exactly as the gate's own console is the first station, and "
     "`EquipmentLinkFailureKey` already refuses a provider in any role as `AlreadyAProvider`. "
     "The row's own analysis was right that this was **a bill-distribution question rather than a "
     "link question**, and it was right that *" + Q + "linking a second bench without answering that "
     "would ship a role that changes nothing" + Q + "*. So the role arrives WITH the split, not "
     "before it. "
     "**AND IT NEEDED ONE CHANGE THE ROW DID NOT PREDICT.** `CompRimroomsGateConsole.IsGateControl` "
     "tested `linkedGate != null` -- the **primary** binding, which is exclusive and belongs to the "
     "designated bench. A linked bench has none, so gate control was unreachable on exactly the "
     "three benches the role exists to create, the recipe's own `AvailableOnNow` requires gate "
     "control, and the feature would have shipped **inert**. It asks `Gate` now, which resolves the "
     "primary binding first and falls back to the assembly link. **A link is not the guess this "
     "getter used to make:** the fallback removed in 0.9.0-dev hunted for the nearest machine gate, "
     "and *" + Q + "the guess it made was never the right answer anyway once two gates could "
     "exist" + Q + "*. Reading which gate holds a link the player made on the Machine pane is "
     "reading their decision, not substituting for it. "
     "**THE CONSOLE HALF HAD SHIPPED WITH NO WIKI AT ALL, AND THAT IS FIXED HERE.** Four relief "
     "stations landed in the previous batch and `grep` found the words *relief station* in exactly "
     "one file in the repository: this queue. **A feature no reader-facing page mentions is a "
     "feature nobody will use**, and the owner's standing direction on the crew cap was *" + Q + "and "
     "wiki and other things, all need accounted for" + Q + "*. `wiki/gates.md` gains both sections, "
     "`wiki/first-hour.md` step 5 names the relief stations where a first-hour reader meets the "
     "problem, and every one of the **eight** documents that stated the old single-bill cost now "
     "states the section cost and the unchanged total. "
     "**The cap question the row left open is still open and still honest:** four stations and four "
     "benches sit beside `MaximumOperationalGates = 3`, and whether four is right for three gates is "
     "a thing only play answers. **What is no longer true is the row's own sentence about "
     "`CrewPlanner.MaxCrew = 3`** -- there is no crew cap any more, which is why the comparison is "
     "now to the gate count alone."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for marker, key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith(marker) and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d %r row(s)" % (key[:52], len(hits), marker.strip()))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[len(marker):].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d bench row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
