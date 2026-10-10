# -*- coding: utf-8 -*-
"""Replace MY OWN positional annotations with the subject they were standing in for.

**Why this is not a LAW #0 problem, which is worth stating because it looks like one.** LAW #0
protects the owner's words. Every phrase replaced below is a status annotation *I* appended in an
earlier batch -- `**PARTLY BUILT**; ... **Open:** the individual routes listed below` and the like.
The verbatim master-TODO text each row carries is untouched, and so is every owner quotation.

The first attempt at this appended the correction and left the pointer standing, which is exactly
the *"second opinion"* failure recorded about stacked doc comments: two statements about the same
thing, one of them dead. Checker 25 kept failing and it was right to.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

REPLACEMENTS = [
    ("**PARTLY BUILT**; what shipped is archived. **Open:** the individual routes listed below.",
     "**PARTLY BUILT**; what shipped is archived. **Open:** runtime acceptance of the built "
     "routes, and nothing in code."),

    ("Four genuine gaps remain, recorded below as new rows because this is new information "
     "rather than a restatement.",
     "Four genuine gaps remain, recorded as new rows at the time because this was new "
     "information rather than a restatement."),

    ("**Open:** optional provider adapters, on their own row below.",
     "**Open:** the T5 and T6 research bands, which carry their own row under the research "
     "tiers heading."),

    ("**Open:** the optional provider interfaces, on their own row below.",
     "**Open:** nothing. The optional profile interfaces are `InstalledIntegrations`."),

    ("**Open:** containment, vehicles and the VGE hooks, each listed individually above.",
     "**Open:** containment, vehicles and the VGE hooks, each named here rather than pointed at."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    for old, new in REPLACEMENTS:
        count = text.count(old)
        if count != 1:
            print("NOT REPLACED (%d matches): %s" % (count, old[:70]))
            return 1
        text = text.replace(old, new, 1)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
    print("replaced %d annotation(s) of my own with the subject they stood in for"
          % len(REPLACEMENTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
