# -*- coding: utf-8 -*-
"""Close the provider-adapter row and the two site rows the work actually finished."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **Optional work/storage provider adapters**',
  'CLOSED 0.12.93-dev. **NO ADAPTER AND NO PATCH FOR ANY OF THE THREE, each for a recorded '
  'reason — and invariant 42 holds by there being nothing to apply, which is a stronger result '
  'than a correctly-gated patch rather than a weaker one.** The register was checked first, per '
  'the LAW, and it already held two of the three answers. '
  '**Haul to Stack (107):** the register says it outright — *"Connected-work check added '
  '2026-09-29: none needed — this mod has no cross-map surface."* Nothing to build. '
  '**Prison Labor (288):** the register had settled one axis from Core source — a prisoner keeps '
  'its own faction and is held by `HostFaction`, so `PortalTraversalPolicy` never admits one — '
  'and left open whether a prisoner is ever *offered* a connected work giver. **That was never a '
  'runtime question.** It is a property of our own entry points, and it is now asserted by '
  '**count**: **7 of 7 adapters and 2 of 2 work givers** gate on `TravellerFailureKey`, which '
  'demands `Faction.OfPlayer` **and** `IsColonist`, from **one** function rather than a condition '
  'copied nine times. A plant strips the gate from **a single adapter** and the claim fails — '
  'which `in` could never have caught. '
  '**Pick Up And Haul (164): the one real finding, and it is OURS, not the mod’s.** The row '
  'asked to confirm *"a worker ... that has gathered inventory items for a near-side stockpile '
  'does not carry them through the gate"*. It did. **Every cargo rule and the receipt itself '
  'govern `carryTracker` — the hands — and nothing anywhere looked at `pawn.inventory`**, so '
  'anything in a pack crossed **unrecorded**: no cargo policy applied to it and no receipt line '
  'mentioned it, which means the branch’s own account of what went through its gate was wrong '
  'by whatever was in the bag. A Core pawn with a spare meal walks into that too; the mod only '
  'makes it routine. **`CrossingInventoryPolicy` makes the rule true: hands are the cargo route, '
  'the pack is not.** Freight is put down on the near side before anything is despawned and '
  'before any custody changes hands — which is where the near-side haul was taking it anyway, so '
  'the job notices it again and the player sees a pile by the door that needs no letter. A pack '
  'that will not empty **refuses the crossing** rather than crossing with it. '
  '**Core decides what counts, not us.** `Pawn_InventoryTracker.FirstUnloadableThing`, read out '
  'of the installed assembly rather than guessed, keeps drug-policy amounts, every '
  '`inventoryStock` entry and as much packable food as a colonist’s own hunger justifies. So a '
  'pawn **never** loses its own medicine, drugs or packed meal at a threshold — which '
  '`DropAllNearPawn` would have done, and a plant proves we do not call it. Two definitions of '
  '*not theirs to keep* is how they come to disagree. '
  '**Nothing references any of the three mods**, no comp is read, no assembly is referenced and '
  'the behaviour is byte-identical with all of them absent. **No new saved state** — the drop '
  'count is not needed after the crossing, and derived beats stored. '
  '`proof-crossing-pack.py` 25 of 25; `plant-crossing-pack.py` 15 of 15; build 0 warnings / 0 '
  'errors.'),

 ('- [ ] **A GitHub Pages build that catalogues the whole mod**',
  'CLOSED 0.12.93-dev ON MEASUREMENT — the site is built, and the row asked for a shape rather '
  'than a page count. **Thirteen pages, 966 lines, in the three-group order a newcomer needs:** '
  'Start (index, install, first hour, the three starts), The game (gates, beyond the gate, the '
  'company, the interface), Reference (mods and expansions, multiplayer, troubleshooting, links, '
  'credits) — *"capabilities, how-to, and the public-facing documentation"*, with its own layout, '
  'stylesheet, generated index, per-page summaries and now a root front door. '
  '**One thing is deliberately NOT the public shape:** an exhaustive feature-by-feature catalogue. '
  'That exists as `docs/SYSTEMS_CATALOG.md` and is internal, because a reader arriving at a wiki '
  'wants to know how to play rather than to read an inventory — and the row itself asks for the '
  'shape *"other rimworld mods make theri third party sites"*, which is thematic pages, not a '
  'manifest. Recorded rather than quietly omitted.'),

 ('- [ ] **`check-doc-conformance.py` should cover the generated site**',
  'CLOSED 0.12.93-dev, and **this row and the one in the Pending section were the same work '
  'written twice** — *"must cover the published site"* there, *"should cover the generated site"* '
  'here, in two different sections. Both are now done and both say so, because a duplicate closed '
  'in one place and left open in the other is how a finished thing gets built again. The site’s '
  'five non-markdown published files are held to the version, branch, retired-def and claims '
  'rules; the checker count is read off `tools/` instead of typed; and a published page cannot '
  'claim a version or a branch the build does not have, which is this row’s own wording.'),
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
