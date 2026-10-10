# -*- coding: utf-8 -*-
"""Close the research-mirror row against what was built."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ROW = "**Mirror every company project into the vanilla Research tab.**"

EVIDENCE = (
    " -- **BUILT 0.12.99-dev. 38 mirrors, their own tab, nine columns by band, and checker 26 "
    "holding the pairing.** "
    "Owner's answers: *" + Q + "Two genuine routes, either works" + Q + "* and *" + Q + "Own tab, "
    "nine columns by band" + Q + "*, then *" + Q + "as far as the research layout wit has to work "
    "bvanillia and with the research mods" + Q + "*. "
    "**That last one turned out to be a single requirement rather than two.** Vanilla lays a tree "
    "out from `researchViewX`/`researchViewY`; every research mod derives its own layout from the "
    "**prerequisite graph**. So both are emitted -- coordinates for vanilla, and a correct graph so "
    "ResearchTree and Research Whatever each draw the same shape their own way. "
    "**THE REGISTER REVERSED A STEER THIS REPOSITORY HAD CARRIED SINCE 0.5.x.** "
    "`check-register-compliance` forbade shipping a `ResearchProjectDef` at all, reasoning that rows "
    "191 and 279 operate on that type and we stayed clear. Reading the cards shows they ask for the "
    "opposite: row 191's planned use is that *" + Q + "The Backrooms tree should own gate, mapping, "
    "containment, and spatial-analysis milestones and should not overwrite other research "
    "trees" + Q + "*, with *" + Q + "stable definitions and an independent route" + Q + "*. **Being "
    "seen by those mods was the goal all along**, and the prohibition became **four assertions**, "
    "which is strictly stronger: our own tab, a self-contained graph, one mirror per project with "
    "label, description and prerequisites agreeing, and the sync still running both ways so the "
    "Operations insight route remains the independent one. "
    "**Both directions, because one direction is two different lies.** A mirror finished in the "
    "Research tab must grant the capability or the tab is a lie; a project finished in Operations "
    "must show as done or the tab offers work already completed and a research mod draws an "
    "unfinished node for finished work. The sync is idempotent and asks *are these two "
    "disagreeing*, never *has something just happened* -- so it also catches a project finished by a "
    "dev command, a quest reward or another mod. **And it never un-completes anything:** taking a "
    "capability back from a player who has it is worse than granting one twice, and twice is already "
    "impossible because the record is a boolean. "
    "**AND THE COST MODEL WAS A UNIT ERROR THAT MEASURING CAUGHT.** The first generator used "
    "`workRequired * (1 + insightCost)` on the reasoning that both are bench work. Our "
    "`workRequired` runs 4,000 to 18,000; vanilla's **113** research projects run **200 to 8,000, "
    "median 1,000**. It produced **8,000 to 108,000** -- the *cheapest* mirror equalling vanilla's "
    "single dearest project and the dearest thirteen times it. **" + Q + "Either route works" + Q
    + " would have been false while looking true**, and nothing in the build would have said so. "
    "Bands now map onto vanilla's own distribution at **800 to 7,000**, with the insight premium "
    "additive rather than multiplicative, and **checker 26 asserts the range** so the next version "
    "cannot drift out of it. "
    "**Three smaller faults, each caught by a tool rather than by me.** `--` inside an XML comment "
    "for the **third** time, so the generator now sanitises comment bodies at the point of writing "
    "-- and the first sanitiser rewrote the `--` of `<!--` itself, which is why it is scoped to "
    "bodies and never delimiters. A new package file is refused until `package-files.json` declares "
    "it, which is the allowlist working. And `check-keyed-strings` read the `RR_Mirror_` prefix as a "
    "whole defName, **correct behaviour on an incomplete rule rather than a false alarm**: it "
    "classifies prefixes by call site, and this one is concatenated into a def lookup rather than "
    "passed to `StartsWith`, so the rule learned the second call site.")


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines)
            if l.lstrip().startswith(("- [ ] ", "- [~] ")) and ROW in l]
    if len(hits) != 1:
        print("row matched %d time(s); refusing" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), EVIDENCE)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("research mirror row closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
