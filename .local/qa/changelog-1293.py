# -*- coding: utf-8 -*-
"""Prepend the 0.12.93-dev entry. No BOM is added: CHANGELOG.md has none and must keep none."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"
HEADING = "# Changelog"

ENTRY = NL.join([
"## 0.12.93-dev - 2026-10-05 - The ledger guard is a guard, the pack is not a cargo route",
"",
"- **ENABLING PAGES WOULD HAVE PUBLISHED THE ENTIRE WORK LEDGER.** The queue row said *\"a comment",
"  is not a guard\"*, and it was righter than it knew: `docs/_config.yml` claimed everything but the",
"  wiki was *\"deliberately excluded\"* while naming **four directories, two of which do not",
"  exist**. Jekyll publishes every entry in its source directory it is not told to exclude, and",
"  **fifty-four documents sit at `docs/` root** - `TODO.md`, `NOW.md`, `FINALIZED.md` and",
"  `DECOMPOSED.md` among them. None carries front matter, so Jekyll would have copied each one",
"  verbatim and served it as a raw download.",
"- **Two independent instruments now hold it, which is the right shape:** one keeps the list",
"  current and one refuses the bad outcome. `tools/build-site.py` writes the exclude list from the",
"  directory itself; `check-doc-conformance.py` **does not read that list and agree with it** - it",
"  models what Jekyll would publish and fails on the answer, so a broken generator cannot produce",
"  a quiet pass. It refuses fourteen ledger names and any published file outside the declared site",
"  surface.",
"- **Explicit names, never globs.** `*` crossing a path separator is a subtlety of Ruby's",
"  `File.fnmatch` that cannot be verified from here, and a pattern that silently fails to exclude",
"  is the one failure mode a ledger guard must not have. Completeness is guaranteed by `--check`",
"  instead: add a document and the battery fails until it is excluded. It fails **both** ways, so",
"  an exclude naming something that is gone also fails - a dead exclude reads as protection and",
"  gives none.",
"- **A guard that looked at nothing must not report a pass.** Every rule here is an absence rule,",
"  and an absence rule over an empty set is satisfied by construction. The check now refuses",
"  outright if it finds no page under `docs/wiki/`, and two plants blind the model to prove it.",
"- **THE SITE'S NON-MARKDOWN PUBLISHED FILES ARE NOW COVERED**, which is the other row. The wiki",
"  prose never was uncovered - `living_docs()` already globbed every `.md` - but a version in a",
"  layout, a branch in a stylesheet comment or a retired def on the front door would all have",
"  shipped unexamined. **A layout is never fetched by a reader and its text is on every page a",
"  reader fetches**, so a claim there ships exactly as widely as one in prose.",
"- **The wall rule measures `<p>` elements for HTML**, not blank-line blocks: an HTML file has no",
"  blank line between paragraphs, so the markdown splitter would read a whole page as one wall.",
"  Vocabulary applies only where a reader meets words - a stylesheet's selectors are not prose.",
"- **The published site has a root document at last.** Pages serves `docs/`, every page inside the",
"  wiki worked, and **the site's own address answered 404**. `docs/index.html` is the front door:",
"  no front matter so Jekyll copies it verbatim, a **relative** link because a project site is",
"  served from a subpath, a real anchor as well as the refresh, no script and no external request.",
"- **A `CNAME` is checked when one exists** - one bare line, no comment, no placeholder.",
"  `CNAME.example` already warned about this and nothing enforced it; it fails the way the example",
"  describes, quietly, with Pages serving nothing while DNS gets blamed.",
"- **THE CHECKER COUNT IS READ OFF `tools/` INSTEAD OF TYPED.** It said `CHECKER_COUNT = 8` with a",
"  phrase list stopping at *\"seven checkers\"* while nineteen shipped, so the one number the rule",
"  exists to protect was eleven out of date. The derived version immediately caught a real stale",
"  claim the fixed list structurally could not see. It also learns *\"the other N checkers\"*, which",
"  is N+1: a rule that demands wrong prose in order to pass is a rule people scroll past.",
"- **`tools/check-site-generated.py` is new, and it exists because a claim was not true as",
"  written.** `build-site.py --check` is not a `check-*.py`, so a battery globbing those never ran",
"  it - while the config and the closing row both said it *\"fails the battery\"*. The generator",
"  stays a generator and the battery gets an entry point. **Twenty checkers now**, and nothing had",
"  to be edited to say so, because the count is derived.",
"- **THE PACK IS NOT A CARGO ROUTE, AND NOTHING USED TO LOOK AT IT.** From mod register row 164",
"  (Pick Up And Haul): *\"confirm a worker ... that has gathered inventory items for a near-side",
"  stockpile does not carry them through the gate\"*. It did. Every cargo rule and the crossing",
"  receipt govern `carryTracker` - the hands - so anything in `pawn.inventory` crossed",
"  **unrecorded**: the branch's own account of what went through its gate was wrong by whatever",
"  was in the bag. **The hole is ours, not the mod's**; a Core pawn with a spare meal walks into",
"  it too.",
"- **`CrossingInventoryPolicy` puts freight down on the near side** before anything is despawned",
"  and before any custody changes hands - which is where the near-side haul was taking it anyway,",
"  so the job notices it again and the player sees a pile by the door that needs no letter. A pack",
"  that will not empty **refuses the crossing**. The rollback path deliberately does not clear a",
"  pack: a crossing that failed through no fault of the pawn's must not cost it its goods.",
"- **Core decides what a pack may keep, not us.** `Pawn_InventoryTracker.FirstUnloadableThing`,",
"  read out of the installed assembly rather than guessed, keeps drug-policy amounts, every",
"  `inventoryStock` entry and as much packable food as a colonist's own hunger justifies. So a pawn",
"  **never** loses its own medicine or packed meal at a threshold - which `DropAllNearPawn` would",
"  have done, and a plant proves we do not call it.",
"- **NO ADAPTER AND NO PATCH FOR ANY OF THE THREE WORK PROVIDERS**, each for a recorded reason, so",
"  invariant 42 holds by there being nothing to apply. **Haul to Stack** has no cross-map surface,",
"  per the register. **Prison Labor**'s open axis was never a runtime question: **7 of 7 adapters",
"  and 2 of 2 work givers** gate on `TravellerFailureKey`, which demands `Faction.OfPlayer` **and**",
"  `IsColonist`, from **one** function rather than a condition copied nine times. A plant strips",
"  the gate from **a single adapter** and the claim fails, which `in` could never have caught.",
"- **THE LAUNDERING INVARIANT IS HELD BY AN INSTRUMENT INSTEAD OF A SENTENCE.** The row said the",
"  routes *\"must stay closed\"* and feared *\"marking on spawn\"*. The shipped design **does** mark",
"  on spawn, and that is what closes the hole: the stamp is **one-way** and **everything** gets",
"  one, so a crate of colony cotton is proven ordinary at birth and can never become odd whatever",
"  gate it is hauled through. The row's own mechanism was also incomplete - it left rock mined from",
"  a coordinate's walls, cut plants and butchered meat unmarked. **Purpose satisfied, mechanism",
"  recorded as superseded.**",
"- **Three rows closed on measurement rather than on belief.** The research tree: **38 projects, 8",
"  branches, 0 cross-branch prerequisites, 8 entry points**, already guarded per project as *not a",
"  chokepoint between branches*. The five `RR_*Staff` PawnKinds: **a `PawnKindDef` is a generation",
"  recipe, not a pawn class** - all five derive `BasePlayerPawnKind` with `PlayerColony`, so the",
"  pawns always were native colonists, and the retirement half is superseded by invariant 131",
"  because `FacilityRelief` now generates the relief team from exactly those five profiles.",
"- **The DLC half of the no-compatibility-claim rule is enforced**, which is what that row asks",
"  for: *\"the main protection, not a formality\"*. `check_expansion_claims` refuses a reader",
"  document saying an expansion is required, across all five, in both phrasings - and **the",
"  control matters more than the refusal**: `mods.md` exists to say they are optional, so a plant",
"  writing *\"Biotech is not required\"* must and does pass.",
"- **Three new instrument pairs, every claim watched failing.** `proof-published-site.py` 66 of 66",
"  with `plant-published-site.py` 26 of 26; `proof-crossing-pack.py` 25 of 25 with",
"  `plant-crossing-pack.py` 15 of 15; `proof-odd-origin-laundering.py` 28 of 28 with",
"  `plant-odd-origin-laundering.py` 15 of 15. **Totals: 20 checkers, 57 proofs, 31 plant suites.**",
"- **Four of my own claim-writing defects caught by their own plants, all the recorded kinds.** A",
"  claim read its own documentation - twice in one file, once through an HTML comment and once",
"  through a Liquid `{%- comment -%}` block the first stripper did not know. A positional claim",
"  anchored `origin =` to the start of a line and missed an inline assignment, reporting 1 where",
"  there were 2. A claim asserted a refusal's **message** and broke on its own",
"  string-concatenation boundary. And a claim passed on a method **signature**, then on the",
"  **base call** that forwards the same flag, while a plant had deleted the guard entirely.",
"- **And one plant was wrong rather than the claim, twice.** A wall paragraph of 330 characters",
"  against a 360 ceiling planted no wall - the suite now asserts its own fault is big enough. And",
"  a foreign-stamp plant was written as a comment, which the proof correctly strips.",
"- Build 0.12.93-dev, **232 C# files, 103 package files, 0 warnings, 0 errors**. Nine rows closed",
"  and archived with `VERBATIM TRANSFER CONFIRMED`; queue **49 open / 20 partial / 38 test / 0",
"  completed**. **No game was launched, and nothing here has been played.**",
"",
])

raw = io.open(PATH, "rb").read()
if raw.startswith(b"\xef\xbb\xbf"):
    print("CHANGELOG.md has a BOM and should not; refusing to write")
    sys.exit(1)
text = raw.decode("utf-8")
if not text.startswith(HEADING):
    print("CHANGELOG.md does not open with %r; refusing to guess where the entry goes" % HEADING)
    sys.exit(1)
if "0.12.93-dev" in text:
    print("0.12.93-dev is already in the changelog; nothing written")
    sys.exit(1)

rest = text[len(HEADING):].lstrip(NL)
out = HEADING + NL + NL + ENTRY + NL + rest
io.open(PATH, "wb").write(out.encode("utf-8"))

back = io.open(PATH, "rb").read()
if back.startswith(b"\xef\xbb\xbf"):
    print("a BOM was added -- ABORT")
    sys.exit(1)
print("prepended %d lines; no BOM added" % ENTRY.count(NL))
