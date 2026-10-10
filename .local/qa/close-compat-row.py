# -*- coding: utf-8 -*-
"""Close the row that asked the no-compatibility-claim rule to stop being a formality."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **Consequence: the no-compatibility-claim rule is now the main protection, not a formality.**',
  'CLOSED 0.12.93-dev — **and it is now enforced rather than de-marked, which is the one thing '
  'the row asks for in its own words: *"the main protection, not a formality"*.** A consequence '
  'nobody can run is a formality by definition. '
  'The row names three things the package must not claim until there is a recorded result, and '
  'all three are now refused by `check-doc-conformance.py`: '
  '**no RWT co-op** — already covered by `FORBIDDEN_CLAIMS`, which refuses an un-negated claim '
  'of shared colony, shared map or synchronised research; **no profile row** — covered by '
  '`check_broad_compatibility`, which runs precisely because `About.xml` declares nothing and '
  'silence otherwise reads as a guarantee; **no DLC interaction** — **this was the uncovered '
  'half and is new.** `check_expansion_claims` refuses a reader document telling somebody an '
  'expansion is required, across all five, in both phrasings. '
  '**Every expansion is optional and `About.xml` declares none as a dependency**, so a page '
  'saying one is needed is wrong about what it takes to play — which is worse than a stale '
  'version, because it turns a reader away at the door. '
  '**The control matters more than the refusal here.** `docs/wiki/mods.md` exists to say the '
  'expansions are optional, so it has to be able to name every one of them; the rule pairs a '
  'name with a requirement word and is negation-aware, and a plant that writes *"Biotech is not '
  'required; nothing here needs Anomaly"* must and does **PASS**. Matching the name alone is '
  'recorded in this same file as exactly how the multiplayer rule failed the one document '
  'written to obey it. '
  '`proof-published-site.py` 66 of 66; `plant-published-site.py` 26 of 26, including both '
  'controls. **D1 option B stays binding and 200 of the 294 dispositions are still '
  'provisional** — nothing here announces anything, it only stops us announcing by accident. '
  'The mod-page row still owns the write-up itself.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:80]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
