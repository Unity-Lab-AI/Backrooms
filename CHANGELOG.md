# Changelog

## 0.12.93-dev - 2026-10-05 - The ledger guard is a guard, the pack is not a cargo route

- **ENABLING PAGES WOULD HAVE PUBLISHED THE ENTIRE WORK LEDGER.** The queue row said *"a comment
  is not a guard"*, and it was righter than it knew: `docs/_config.yml` claimed everything but the
  wiki was *"deliberately excluded"* while naming **four directories, two of which do not
  exist**. Jekyll publishes every entry in its source directory it is not told to exclude, and
  **fifty-four documents sit at `docs/` root** - `TODO.md`, `NOW.md`, `FINALIZED.md` and
  `DECOMPOSED.md` among them. None carries front matter, so Jekyll would have copied each one
  verbatim and served it as a raw download.
- **Two independent instruments now hold it, which is the right shape:** one keeps the list
  current and one refuses the bad outcome. `tools/build-site.py` writes the exclude list from the
  directory itself; `check-doc-conformance.py` **does not read that list and agree with it** - it
  models what Jekyll would publish and fails on the answer, so a broken generator cannot produce
  a quiet pass. It refuses fourteen ledger names and any published file outside the declared site
  surface.
- **Explicit names, never globs.** `*` crossing a path separator is a subtlety of Ruby's
  `File.fnmatch` that cannot be verified from here, and a pattern that silently fails to exclude
  is the one failure mode a ledger guard must not have. Completeness is guaranteed by `--check`
  instead: add a document and the battery fails until it is excluded. It fails **both** ways, so
  an exclude naming something that is gone also fails - a dead exclude reads as protection and
  gives none.
- **A guard that looked at nothing must not report a pass.** Every rule here is an absence rule,
  and an absence rule over an empty set is satisfied by construction. The check now refuses
  outright if it finds no page under `docs/wiki/`, and two plants blind the model to prove it.
- **THE SITE'S NON-MARKDOWN PUBLISHED FILES ARE NOW COVERED**, which is the other row. The wiki
  prose never was uncovered - `living_docs()` already globbed every `.md` - but a version in a
  layout, a branch in a stylesheet comment or a retired def on the front door would all have
  shipped unexamined. **A layout is never fetched by a reader and its text is on every page a
  reader fetches**, so a claim there ships exactly as widely as one in prose.
- **The wall rule measures `<p>` elements for HTML**, not blank-line blocks: an HTML file has no
  blank line between paragraphs, so the markdown splitter would read a whole page as one wall.
  Vocabulary applies only where a reader meets words - a stylesheet's selectors are not prose.
- **The published site has a root document at last.** Pages serves `docs/`, every page inside the
  wiki worked, and **the site's own address answered 404**. `docs/index.html` is the front door:
  no front matter so Jekyll copies it verbatim, a **relative** link because a project site is
  served from a subpath, a real anchor as well as the refresh, no script and no external request.
- **A `CNAME` is checked when one exists** - one bare line, no comment, no placeholder.
  `CNAME.example` already warned about this and nothing enforced it; it fails the way the example
  describes, quietly, with Pages serving nothing while DNS gets blamed.
- **THE CHECKER COUNT IS READ OFF `tools/` INSTEAD OF TYPED.** It said `CHECKER_COUNT = 8` with a
  phrase list stopping at *"seven checkers"* while nineteen shipped, so the one number the rule
  exists to protect was eleven out of date. The derived version immediately caught a real stale
  claim the fixed list structurally could not see. It also learns *"the other N checkers"*, which
  is N+1: a rule that demands wrong prose in order to pass is a rule people scroll past.
- **`tools/check-site-generated.py` is new, and it exists because a claim was not true as
  written.** `build-site.py --check` is not a `check-*.py`, so a battery globbing those never ran
  it - while the config and the closing row both said it *"fails the battery"*. The generator
  stays a generator and the battery gets an entry point. **Twenty checkers now**, and nothing had
  to be edited to say so, because the count is derived.
- **THE PACK IS NOT A CARGO ROUTE, AND NOTHING USED TO LOOK AT IT.** From mod register row 164
  (Pick Up And Haul): *"confirm a worker ... that has gathered inventory items for a near-side
  stockpile does not carry them through the gate"*. It did. Every cargo rule and the crossing
  receipt govern `carryTracker` - the hands - so anything in `pawn.inventory` crossed
  **unrecorded**: the branch's own account of what went through its gate was wrong by whatever
  was in the bag. **The hole is ours, not the mod's**; a Core pawn with a spare meal walks into
  it too.
- **`CrossingInventoryPolicy` puts freight down on the near side** before anything is despawned
  and before any custody changes hands - which is where the near-side haul was taking it anyway,
  so the job notices it again and the player sees a pile by the door that needs no letter. A pack
  that will not empty **refuses the crossing**. The rollback path deliberately does not clear a
  pack: a crossing that failed through no fault of the pawn's must not cost it its goods.
- **Core decides what a pack may keep, not us.** `Pawn_InventoryTracker.FirstUnloadableThing`,
  read out of the installed assembly rather than guessed, keeps drug-policy amounts, every
  `inventoryStock` entry and as much packable food as a colonist's own hunger justifies. So a pawn
  **never** loses its own medicine or packed meal at a threshold - which `DropAllNearPawn` would
  have done, and a plant proves we do not call it.
- **NO ADAPTER AND NO PATCH FOR ANY OF THE THREE WORK PROVIDERS**, each for a recorded reason, so
  invariant 42 holds by there being nothing to apply. **Haul to Stack** has no cross-map surface,
  per the register. **Prison Labor**'s open axis was never a runtime question: **7 of 7 adapters
  and 2 of 2 work givers** gate on `TravellerFailureKey`, which demands `Faction.OfPlayer` **and**
  `IsColonist`, from **one** function rather than a condition copied nine times. A plant strips
  the gate from **a single adapter** and the claim fails, which `in` could never have caught.
- **THE LAUNDERING INVARIANT IS HELD BY AN INSTRUMENT INSTEAD OF A SENTENCE.** The row said the
  routes *"must stay closed"* and feared *"marking on spawn"*. The shipped design **does** mark
  on spawn, and that is what closes the hole: the stamp is **one-way** and **everything** gets
  one, so a crate of colony cotton is proven ordinary at birth and can never become odd whatever
  gate it is hauled through. The row's own mechanism was also incomplete - it left rock mined from
  a coordinate's walls, cut plants and butchered meat unmarked. **Purpose satisfied, mechanism
  recorded as superseded.**
- **Three rows closed on measurement rather than on belief.** The research tree: **38 projects, 8
  branches, 0 cross-branch prerequisites, 8 entry points**, already guarded per project as *not a
  chokepoint between branches*. The five `RR_*Staff` PawnKinds: **a `PawnKindDef` is a generation
  recipe, not a pawn class** - all five derive `BasePlayerPawnKind` with `PlayerColony`, so the
  pawns always were native colonists, and the retirement half is superseded by invariant 131
  because `FacilityRelief` now generates the relief team from exactly those five profiles.
- **The DLC half of the no-compatibility-claim rule is enforced**, which is what that row asks
  for: *"the main protection, not a formality"*. `check_expansion_claims` refuses a reader
  document saying an expansion is required, across all five, in both phrasings - and **the
  control matters more than the refusal**: `mods.md` exists to say they are optional, so a plant
  writing *"Biotech is not required"* must and does pass.
- **Three new instrument pairs, every claim watched failing.** `proof-published-site.py` 66 of 66
  with `plant-published-site.py` 26 of 26; `proof-crossing-pack.py` 25 of 25 with
  `plant-crossing-pack.py` 15 of 15; `proof-odd-origin-laundering.py` 28 of 28 with
  `plant-odd-origin-laundering.py` 15 of 15. **Totals: 20 checkers, 57 proofs, 31 plant suites.**
- **Four of my own claim-writing defects caught by their own plants, all the recorded kinds.** A
  claim read its own documentation - twice in one file, once through an HTML comment and once
  through a Liquid `{%- comment -%}` block the first stripper did not know. A positional claim
  anchored `origin =` to the start of a line and missed an inline assignment, reporting 1 where
  there were 2. A claim asserted a refusal's **message** and broke on its own
  string-concatenation boundary. And a claim passed on a method **signature**, then on the
  **base call** that forwards the same flag, while a plant had deleted the guard entirely.
- **And one plant was wrong rather than the claim, twice.** A wall paragraph of 330 characters
  against a 360 ceiling planted no wall - the suite now asserts its own fault is big enough. And
  a foreign-stamp plant was written as a comment, which the proof correctly strips.
- Build 0.12.93-dev, **232 C# files, 103 package files, 0 warnings, 0 errors**. Nine rows closed
  and archived with `VERBATIM TRANSFER CONFIRMED`; queue **49 open / 20 partial / 38 test / 0
  completed**. **No game was launched, and nothing here has been played.**

## 0.12.92-dev - 2026-10-05 - The wiki is a site you can scan, and its index writes itself

- **THE THEME IS GONE AND THE LAYOUT IS OURS.** Owner: *"the beautiful and masterfully way
  paossible so the thing needs to NOT pop like a text wall"*. The queue row's reading of
  `jekyll-theme-primer` was blunt and right - a text wall with a margin: one column, one type
  size, and no way into a page except reading it from the top. `docs/_layouts/default.html` and
  `docs/assets/css/rimrooms.css` replace it.
- **Four devices do the scannability**, because the row says it is *"a layout answer as much as a
  prose one"*: a persistent index of every page on every page; a **summary line** at the top of
  each; a prose column capped near 68 characters, since a full-width paragraph *is* the text wall;
  and headings that read as dividers with a rule and real space above them, with tables and
  blockquotes styled so a skimming eye lands on them.
- **No webfont, no script, no external request and no remote theme gem.** The site is a handful of
  static files, which is the same instinct as the package depending on nothing but Core. Dark mode,
  a keyboard skip link, and the current page marked by weight and an inset rule rather than by
  colour alone.
- **THE INDEX WRITES ITSELF.** Owner: *"Generated, never hand-maintained."* `tools/build-site.py`
  writes `docs/_includes/nav.html` from whatever is actually in `docs/wiki/` - the title from each
  page's own first heading, the hover text from its `summary` front matter. **A hand-written list
  of pages is a second place the truth lives:** add a page and the list is wrong, rename one and
  the list is a broken link. `--check` fails when the include and the directory disagree, so the
  battery catches a stale index rather than a reader finding it. A page not in the declared reading
  order is still published and still indexed, under *More*.
- **And it found a bug in itself before shipping:** the first version marked the current page with
  `page.url contains '/wiki/'`, which is true of **every** page in the wiki - so the index would
  have been highlighted as current everywhere. The layout now derives a slug once and the generated
  index compares against that.
- **All thirteen pages say what they are before they say anything else**, through `title` and
  `summary` front matter rendered as a callout at the top and as the hover text on the index entry.
  No stylesheet can invent a one-line answer to *what is this page for*.
- **CNAME SUPPORT AUTHORED, DOMAIN DELIBERATELY NOT NAMED.** `docs/CNAME.example` carries the
  shape, the four apex A records, the subdomain alternative, the Settings step and the `curl -sI`
  verification - and it is **inert on purpose**. No file in this repository names a hostname the
  deploy does not serve, because a live `CNAME` naming a domain nobody owns yet does not fail
  loudly: Pages stops answering on `github.io` and waits for DNS that never arrives. And no page
  hard-codes the site's own address, so the real domain needs no page edits at all.
- **`_config.yml` now records in the file why the work ledger can never be published.**
  `outputs/readable/` renders `TODO.html` and `NOW.html` as an internal reading convenience, and
  the row is explicit that it stays internal. **Written down and NOT yet enforced** - a comment is
  not a guard, so that row stays open alongside the published-site coverage it belongs with.
- **Two gaps measured rather than claimed.** `check-doc-conformance.py` already globs every `.md`
  in the repository, so the thirteen wiki pages were **always** covered for version and branch
  claims - that half was never missing. What is uncovered is the site's **non-markdown** published
  files: the layout, the generated include, the stylesheet, `_config.yml` and a future `CNAME`. A
  version claimed in a layout would ship unchecked today.
- **THE RESEARCH ROW WAS WRONG ABOUT T3, and the measurement says so.** It read *"tiers 0-2
  complete; T3 is the next checkpoint"*. **T3 is fully built** - seven projects, one per branch,
  each gated on its tier-2 sibling plus three route, two distortion and one entity log, with its
  own header and a record in `BUILD_ORDER_CORRECTION.md`. **T4 is built too**, six of seven, and
  both absences are reasoned in the file. **34 capabilities granted, 34 read - a perfect
  bijection**, so no hollow unlock and no dead read. What is actually open is T5 and T6, and the
  file's own rule makes that a knob sweep rather than an authoring job.
- Instruments: **19 checkers, 54 proofs, 28 plant suites.** 19 checkers and 54 proofs run green.
  **The plant sweep was not re-run and did not need to be:** this batch changed no C# and no mod
  Def or Keyed file - only two version lines, the docs tree and the new site tool - so every plant
  target is byte-identical to the 1035-of-1035 sweep at 0.12.91-dev, and `check-plant-residue.py`
  confirms nothing is planted. Queue: 58 open, 20 partial, 38 post-completion test, 0
  completed-and-unarchived.

## 0.12.91-dev - 2026-10-05 - The package needs nothing, expansions only add, and a missing start reports itself

- **THE STAND-ALONE GUARANTEE IS A CHECKER NOW, which is what the row said it would take.** Owner:
  *"we will completely make the mod 100% functional and stand alone not needing any other mods"*.
  The queue row named the obstacle exactly - *"A declaration cannot establish it"* - and nothing in
  the battery could, because `check-dlc-gating.py` asks *is every expansion reference gated* and
  **can never see a reference to one of the 294 profile mods**: such a def is not DLC-only, it is
  not in the game's data at all. That is the hole a stand-alone claim actually rests on. One
  `thingDefName` naming another mod's building would quietly make the package require that mod,
  with no error anywhere until a player without it reached the feature.
- **The measurement, first run: 214 def-name field values across the package and ZERO resolve
  outside Core and our own defs.** The 14 that resolve only in an expansion are all gated. 64
  literal def lookups in C# and **zero hard `GetNamed`** on anything we do not ship; the 5
  expansion lookups all degrade through `GetNamedSilentFail`. Four assembly references, all the
  game's own and Unity's.
- **Its reference fields are enumerated from our own source rather than listed by hand** - the
  lesson `check-register-compliance.py` paid for when a hand-kept tag list missed `<thing>` and
  read 114 of 171 references as nothing. **And it SKIPS rather than passes when the game data is
  absent**, because a checker that reports green against nothing is the defect that once gave
  eight claims a false pass.
- **FOUR EXPANSION ROLES, AND THEY ARE OPTIONAL BY CONSTRUCTION RATHER THAN BY A GATE.** Owner:
  *"DLCs only add content"*. A containment wing (Anomaly), a biological laboratory (Biotech), an
  assembly room (Ideology) and off-world logistics (Odyssey).
  `RimroomsGateEquipmentDef.thingDefNames` is a `List<string>`, so naming `HoldingPlatform`
  creates **no cross-reference at load at all** - `Fillable` resolves it through
  `GetNamedSilentFail` and `AllInOrder` hides a role nothing can fill from the picker, the readout
  and `RoleFor` alike. Not merely gated: unable to exist.
- **`MayRequire` is on every expansion entry anyway, per entry rather than per role.** Gating the
  whole role would delete a role that also accepts Core buildings, and Core gates string lists the
  same way in `CommonMapGenerator.xml`. **`check-dlc-gating.py` could not see a per-entry gate**
  and reported all fourteen as ungated; it read the attribute off the def alone and now accumulates
  it down the element tree, which is how RimWorld reads it. **Taught the mechanism rather than
  worked around** - demanding the attribute on the def would have pushed the worse shape, which is
  how a checker ends up making the code wrong. Verified still strict three ways.
- **None of the four carries a stock need or a risk**, so an expansion cannot even put a
  *shortfall* line in front of a player. The gate opens, the crews cross, the records are kept and
  the company pays identically without any of them.
- **AND ROYALTY GETS NOTHING, WHICH IS RECORDED RATHER THAN PADDED.** It ships almost no buildings
  - thrones are Core - and what it adds is titles, permits, psycasts and the Empire. None is
  equipment a facility links to, and the row's own condition is *"only as optional company
  routes"*: a route must be a thing, a log or a project, and a title is none of the three. An
  honest hook needs a new route kind, which is a design decision rather than a def edit. Stated the
  way the project tree states that transport and orbital support has no tier 0, deliberately.
- **THE STARTING-GOODS DEFECT: FOUR CANDIDATE CAUSES ELIMINATED AND NO FIX WRITTEN ON A HUNCH.**
  Owner: *"they need to properly spawn in with starting goods"* and *"my preparecarfully mod food
  did not appear"*. Eliminated against the installed game rather than guessed: the arrival part is
  not missing - `ScenPart_RimroomsArrival` **subclasses** `ScenPart_PlayerPawnsArriveMethod`, which
  is the one place in the game that collects `PlayerStartingThings()`; the start spot is not wrong,
  Core's `FindPlayerStartSpot` is order 850 and only picks when none is valid; the gen steps are not
  out of order, `ScenParts` is order **875** after both; and the pawns do not arrive by pod,
  `Standing` is enum zero **and** set explicitly.
- **The report's own evidence rules out the next obvious one:** the pawns' `MealSurvivalPack`
  possessions *did* arrive, and possessions travel in the same list as the grants through the same
  `DropThingGroupsNear` call. So the placement ran and the grants were not in the list it placed.
- **So what shipped is the thing that makes the next launch answer it.** The receipt records what
  the scenario **promised** and what actually **arrived**, and the start reports the gap on the
  letter stack naming Prepare Carefully as the likely quarter. **The promise is read through
  `GetSummaryListEntries`, which creates nothing** - enumerating `PlayerStartingThings()` again
  would manufacture a second set of goods, the exact double-grant the receipt exists to prevent and
  which that class's own header forbids. It never blocks a start, and it is silent unless a promise
  was recorded and nothing at all arrived.
- **Two rows closed on measurement.** Staff prior exposure was listed as unbuilt on a second row
  while being built and wired - **a fact recorded as missing in two places was missing in neither**.
  And the battery-reserve row was a recorded *finding* rather than a task: its own words are
  *"checked and ruled out rather than assumed"*, and a ruled-out cause belongs in the archive where
  the next reader finds it.
- **Two instruments added, and five claims in them were wrong before they were right.**
  `proof-standalone-and-grants.py` is 20 claims and `plant-standalone-and-grants.py` reports **23
  of 23 caught**. One claim tested a refusal's *message* instead of its condition - the
  message-is-not-a-rule mistake, made again. One asserted a name that appears at its definition
  **and** its use, so `in` was satisfied by the use alone. One asserted a `catch` existed rather
  than that it swallows, and a planted `throw;` walked past. **One had a slicing bug**: it cut a
  method at its first `}`, which was an inline `{ return; }` guard, so it examined four lines and a
  planted failure sat safely below. **And one plant was wrong rather than the claim** - it rewrote a
  checker's message, which does not stop the checker refusing anything.
- Instruments: **19 checkers, 54 proofs, 28 plant suites, 1035 plant anchors.** Queue: 62 open, 20
  partial, 38 post-completion test, 0 completed-and-unarchived.

## 0.12.90-dev - 2026-10-05 - Training is work, a decision costs something, and the only clock is still the gate

- **CERTIFICATIONS AND TRAINING JOBS, and the training is a real bill rather than a button.**
  Owner: *"Add configurable company roles, staff schedules, certifications, training jobs, field
  history, trust/stress/exposure and equipment familiarity; preserve pawn autonomy and vanilla
  skill/trait systems"*. A certification is the **person-level twin of a company project**: a
  project spends insight and work to give the branch a capability, a certification spends one
  person's work to give that person a qualification, and it stays with them. Each one names a
  `RecipeDef` the player adds to a bench, modelled on `RR_AssembleMachineGate` - a pawn walks
  over, works, and the recipe worker records it against whoever did it. **No new work giver, no
  new job driver and no new building**, because Core's bill system already is this mechanism.
- **And Core enforces the skill floor, not this mod.** The recipes carry `skillRequirements`, so
  RimWorld refuses the bill to an unqualified pawn up front. A floor checked after the work was
  finished would mean spending thousands of ticks of somebody's day and being told no at the end.
- **Three certifications ship and every one is read by named code**, which is the project tree's
  rule: *an unlock a player is told about that changes nothing is worse than no unlock*. A trained
  operator takes work off the spin-up dial, a trained analyst may sign off a report whatever their
  Intellectual, a trained technician reconditions a gate for less work. **Security and medical
  logistics have none, deliberately** - no existing surface would act on one, and a fourth card
  promising nothing is what the project tree already refuses by leaving transport without a tier 0.
- **The row's last clause is honoured literally.** *"Preserve pawn autonomy and vanilla
  skill/trait systems"*: nothing grants a skill, a trait, a hediff or a passion. A certification is
  a record the **company** keeps, and the ordinary learning comes from the recipe's `workSkill`.
- **One of the three things that row listed as missing was already built.** Staff prior exposure
  ships and is wired - recorded where *came back from there* is already known, read by the
  spin-up dial and by the crew planner. Measured against the source rather than taken from the row.
- **CONTAIN, RELEASE, TRANSFER AND DETAIN, each with a consequence a player can feel.** Owner:
  *"Make sale/study/use/contain/release/recruit/detain/transfer choices visible with financial,
  staff, faction, legal-in-world, trust, and security consequences"*. Sale, study and recruit
  already had surfaces; these four did not exist. **Contain charges the branch every day on its
  own ledger line** - modelled on the remote-site share down to not being folded into overhead,
  for the same stated reason: a branch that contains everything should watch itself going broke
  and know which line did it. **Transfer pays less than the exchange would**, because if it paid
  the same it would be sale with extra words - taking less *is* the decision, and that is the
  legal-in-world consequence expressed as a price rather than a paragraph.
- **Detain is the one that belongs to a person**, so it sits beside the passage offer: take them
  home as one of yours, or hold them. The consequence is **Core's entire prisoner system** -
  needs, recruitment, escape risk, the warden job, the faction reading - which is why it is a few
  lines rather than a subsystem. Refused **by name** when there is nowhere to hold anybody.
- **CONFIDENCE IS DERIVED AND NEVER STORED**, and that is the design. It is a function of the
  record's own observations, disputes, analysis and sign-off, all already saved; a stored score
  would be a second copy that could disagree with its own inputs - settle a dispute and it would
  still read *contradicted* until something remembered to recompute. Four bands rather than a
  percentage, because a percentage invites precision that is not there. **An unsettled dispute
  caps it at Weak whatever else is true**, which is exactly why review refuses to sign off while
  one is open: the two rules agree by construction.
- **And it is load-bearing rather than a readout:** confidence moves what the corporation pays for
  a transfer, which is the honest reading of the row pairing *confidence* with *value* on one
  line. It never pays **less** than an unverified record, because a penalty for handing over
  something thin would push a player to sit on findings - and sitting on findings is what the
  containment charge already costs them for.
- **Destruction is its own choice and deliberately not folded into release.** Releasing puts a
  thing **back**, where it still exists; destroying means it exists nowhere. It is also **the only
  option that needs nothing** - no buyer, no contact, nowhere to put it - which is why a branch
  out of options still has it, and it is the one way out of a containment charge. **It pays
  nothing**, so contain-then-cash can never beat selling.
- **The generator can see four things about the branch it is generating for.** Owner: *"Generate
  bounded story variations from client/faction, coordinate, staffing, discovered rules, company
  tier, previous outcomes, opening duration, and available equipment"*. Four of those arrived at
  0.12.12-dev; **company tier, previous outcome, opening duration and the world's faction
  pressure did not.** Tier against what a family pays, so a tier-five branch is not asked for a
  two-hundred-credit errand. A family the branch keeps turning down is one the company stops
  leading with. Deep work needs a window that stays open.
- **It is a bias and never a filter, and the distinction is load-bearing.** `FamilyEligible` still
  decides what is *answerable*; a fifth hard condition is how a branch ends up with nothing on the
  table at all, which is the trap `CoordinateMotif` names for room themes. Every factor is clamped
  in both directions - the owner's word is *bounded*, and a weight that can reach zero is a filter
  wearing a weight's clothes. **Least-asked-first is untouched**; the weighting applies inside the
  tie, where the code was choosing at random. **And no `faction` field was added to the def**,
  because there is no authored content behind one and it would have been the hollow unlock this
  package keeps refusing.
- **EVICTION AND RENEWAL - AND "TERM" IS REFUSED RATHER THAN BUILT.** `CAMPAIGN_CHART.md` 1.1 is
  absolute and checker-enforced: *a gate's connection has a duration, nothing else in this mod
  has a duration*. **A lease term is a countdown on a thing the player is asked to maintain**, so
  the row is answered by saying so - the same way the chart records four prep documents' timed
  investigations as superseded. A row asking for something a LAW forbids is answered, not built
  smaller.
- **Eviction is allowed because it is a consequence, not a clock**, built to 1.1's own test: a
  place goes **only** because the branch stopped paying for it, the unpaid bill is on the ledger,
  and paying clears it. **No time passing ever evicts anybody.** One place per operating day and
  the newest first, so a cash-flow problem never becomes a campaign-ending event with no step in
  between - and it is recorded as an **eviction**, not a release, because the branch did not
  choose it. **Renewal costs nothing**: a branch that lost a place and still owes for it has
  already paid twice.
- **Three rows closed on measurement rather than work.** The company book's label was waiting on a
  problem the `companyIssued` flag solved at 0.12.87-dev - the label applies only to a
  company-issued book and every novel in the game is untouched, so the objection that kept the row
  open no longer applies. Gate size and what it lets through: widths for people, herd animals and
  vehicles, depth as well as width, hostiles at the same single chokepoint, and the blue glow -
  all built. Equipment versus seed reproducibility: held absolutely on one half, superseded on the
  other, with nothing left open on either.
- **Two instruments added, and four claims in them were wrong before they were right.**
  `proof-tenure-and-disposition.py` is 40 claims and `plant-tenure-and-disposition.py` reports
  **46 of 46 caught**. One claim read its own XML comment - the third time this session a claim
  has read the documentation explaining the thing it was asserting the absence of, so a comment
  stripper now exists for both languages. One asserted a needle that appears **three** times and
  was satisfied by the two the plant left behind. One checked a clock-name pattern on one file and
  a narrower one on the other, so an `expiryTick` walked past it. **And one was positional again**
  - comparing call indices, which a plant satisfied by moving the call out of its block entirely;
  the property was containment, not order, and `NOW.md` already recorded that exact class.
- Instruments: **18 checkers, 53 proofs, 27 plant suites.** Queue: 67 open, 21 partial, 38
  post-completion test, 0 completed-and-unarchived.

## 0.12.89-dev - 2026-10-05 - The thing says what it is, the link goes there, and the company pays for the goal

- **THE UNNERVING REGISTER REACHED OBJECTS, which the owner had named specifically and the last
  version had missed.** Owner: *"not just room shape echoes but echos of thier inhabitance in weird
  ways and items and equipment and production benches"*. 0.12.88-dev took the register to people
  and events; a coordinate's objects were materially varied, correctly placed, and said nothing at
  all about who had been using them. Twenty object tells now ship across nine classes - bench,
  seat, table, bed, storage, light, item, equipment and anything - each one exact wrong fact read
  off the thing for as long as the thing exists. *"The bills are still queued on it. The last one
  is for a meal, and there is nothing in this space to cook."*
- **The classes ask the definition a question rather than naming defs**, so a bench from a mod
  installed tomorrow is a bench today - the same discipline the room archetypes already use. And
  the comp is attached in code at `StaticConstructorOnStartup` rather than by XML, because that is
  the only moment the question can be asked *after def inheritance resolves*. The patch file's own
  note records why that matters: an xpath runs on raw XML and `BuildingBase` is the only parent
  broad enough to catch the furniture, which would have put this comp on every wall, door and
  turret in every colony in the game to reach the few that can be dressed into a Backrooms room.
- **The same no-mood-adjective gate the people and events are held to.** The rule is
  `UNIVERSE_ADAPTATION.md`'s, not invented here: the uncanny is *one exact change to something
  ordinary*. A bench that is *eerie* tells the player nothing. And **most objects carry no tell**,
  which is the design rather than a shortfall - *quiet stretches are required content*, and a
  coordinate with a placard on every stool buries the sharper people and event beats.
- **Hauling can no longer silently destroy a tell.** `Thing.CanStackWith` compares def, stuff and
  hit points and never looks at comp data, so a marked stack dropped onto an ordinary one would
  merge and the fact would survive or vanish depending on which absorbed which. A readable warning
  that disappears because somebody tidied up is not a readable warning.
- **THE STATION HAD NO INSPECT CARD AT ALL.** Owner: *"we also need to be making sure all mod
  ingame decriptions and informational informations for everything is properly in the cards like
  the game does currently"*. The gate had one and the beacon had one; the thing a player clicks on
  to *run* a gate had nothing, so a station bound to no gate looked exactly like one bound to a
  gate. The sharpest edge was gate control - it holds every unrelated bill on the machining bench
  suspended, which is correct and was asked for, and a player who left it that way and could not
  work out why nothing was being crafted had no way to find out from the bench.
- **And the beacon was silent in exactly the state where a player needed telling.** It read
  `if (!designated) return null` and stopped, so bonds piled up inside its radius with nothing
  banking them and nothing on the thing saying one toggle was the answer. **A card that explains
  itself only once it is already working explains itself only to people who did not need it.** It
  speaks now only when there are company bonds in range, which keeps the dormant-until-designated
  rule intact: this comp sits on Core's own trade beacon in every colony in the game.
- **The locked supply tier row printed a raw `defName` straight at the player.** An internal
  identifier like `MicroelectronicsBasics`, which the game displays nowhere else, behind a **null
  action**. So the one screen that told somebody they needed a research project named it
  unrecognisably and gave them no way to go and look at it. It now shows the project's own label
  and opens the research tree at it through Core's public `MainTabWindow_Research.Select` -
  confirmed by decompiling the installed assembly rather than remembered - and deliberately does
  **not** set the player's current project, because a link shows somebody where a thing is and
  choosing to research it is still theirs.
- **Deep links out to a pawn and a building, through one helper.** The Personnel detail view holds
  the richest readout of a person anywhere in the package and had no way to go and look at them; it
  refuses **by name** for an off-site applicant, because somebody not standing anywhere yet is
  worth saying out loud. A link that cannot arrive is never offered - *a button that can only
  refuse is worse than no button*.
- **The scheduling surface, and it adds no clock.** Owner's row: *"Add schedule, warning, recall,
  evacuation, emergency close, lost-connection, failed return, and rescue workflows"* - schedule
  was the one left. A standing recall calls the crew home at a point in the opening's window the
  player picked. `CAMPAIGN_CHART.md` 1.1 is absolute and checker-enforced - *a gate's connection
  has a duration, nothing else in this mod has a duration* - so this reads the gate's existing
  window, is off by default, and only ever tells people to walk home: it cannot close the gate,
  cannot strand anybody and cannot end the trip. **Its thresholds are the three warning
  thresholds**, not new ones, because a schedule that could sit between two warnings would be a
  second opinion about when a window is nearly over.
- **Why it is worth having:** the way a player loses a crew is not misunderstanding the rules, it
  is being busy elsewhere on the map when the five-minute warning scrolls past. A warning needs
  somebody watching. A standing order does not.
- **THE COMPANY PAYS FOR EACH START-UP GOAL REACHED.** Owner: *"and once u follow the quests to get
  the gate up and running(full totorieal quest line payouts on each successful step(the company
  rewards getting to the goals)"*. Eleven goals, eleven payouts, scaled so the early ones are a
  nudge and a connection actually open is worth more than the other ten together. The spine is
  `GateStartupChecklist.Steps` - **the same list the machine tab's status board and the door's own
  inspect card read**, so a payout and a tick can never disagree about whether something is done.
- **And it added no saved state at all, because the ledger is already the record.**
  `PostTransaction` is idempotent on its operation id, so *has step six been paid* is answered
  permanently by the branch's own books; a second bookkeeping field could only ever drift from
  them. The id names the step and not the gate, so the chain pays **once per branch** - paying per
  door would turn eleven payouts into an income stream, and a plant proves that version fails.
- **The five named room functions that were never built:** quarantine, armory, radio, receiving and
  canteen, as gate equipment link roles. The row's own analysis decided the shape and was right -
  *RimWorld already builds rooms; what this mod adds is what a gate is linked to*. **Every defName
  was read out of the installed game data**: `TableLong` was the first choice for the canteen and
  does not exist. So a role nothing in the loaded game can fill is now **hidden rather than offered
  and unfillable**, which is the stand-alone guarantee applied to a role.
- **A role knows what should be kept on it, and what goes wrong when it is not.** A role that only
  *accepts* equipment is a label; one that knows what belongs on it is a function - an armory with
  no weapons in it is not an armory, and nothing anywhere could say so before. Counted on the
  role's **own linked things and never map-wide**, because a branch with five rifles in a bedroom
  does not have an armory. Each risk names the consequence - *"a crew that meets something hostile
  down there has nothing to meet it with"* - and never scores it.
- **`RecordsAwaitingReview()` had no caller for a whole checkpoint**, which is exactly what its own
  file warns about: *"Four of five bond defects, and seven before them, were built, correct and
  unreachable."* It is wired now and the awaiting-sign-off heading carries the branch-wide count.
  **The fix for an unreachable surface is to reach it, not to remove it** - that correction came
  from the owner mid-batch, and it cost no screen words at all because the count rides a string
  that already existed.
- **Two instruments added, and four claims in them were wrong before they were right.**
  `proof-operations-reach.py` is 38 claims and `plant-operations-reach.py` reports **38 of 38
  caught**; `plant-unnerving-register.py` is now **50 of 50**. Two claims failed on their first run
  because an absence assertion read the documentation too - good documentation explains the thing
  it avoids **by naming it** - and two more passed a plant they should have caught: one asserted a
  `for` line that appears twice in the file and matched the wrong one, and one asserted that an
  error *message* existed rather than the condition that fires it. **A message is not a rule.**
- **Two rows closed on measurement rather than work.** Non-rectangular rooms and corridors: built,
  seven shape forms banded by distance from the arrival hall. Material variation across items,
  equipment, walls, floors, lights, furniture and benches: built, and reaching both placement paths.
  The clause that was genuinely missing was the one about objects saying something, above.
- Instruments: **18 checkers, 52 proofs, 26 plant suites, 957 plant anchors.** Queue: 67 open, 30
  partial, 38 post-completion test, 0 completed-and-unarchived.

## 0.12.88-dev - 2026-10-04 - Everything down there has one exact thing wrong with it, and you can read it off the thing

- **The unnerving register reached people and events, which it never had.** Owner: *"remember
  lsd unnerving feeling with all things ie events random spanwns, enemies, allies, nuetrals,
  even all the crazy things ive mentioned in the past and anything u can find in the many many
  prep docs on the Backrooms Universe"*. The LSD direction had been read as an *architecture*
  direction for eight versions - bent corridors, seven room shapes, roads, neighbourhoods, a
  per-coordinate motif, all built - and none of it reached a single encounter, spawn or event.
  The owner's four-word version of that was *"zero weird events or people"*.
- **AND THE PREP DOCUMENTS HELD THE MECHANISM, not just atmosphere.**
  `docs/UNIVERSE_ADAPTATION.md`, written before any of this code existed: *"Ordinary industrial
  interiors become uncanny through exact changes ... a shifted doorway, impossible adjacency,
  repeated hall, changed room dimensions, or a feature that has moved since the last visit."*
  The uncanny is **one exact change to something ordinary** - a testable property, not a mood,
  and the reason the generator's floors already read while no encounter did.
- **So it is a gate now.** No inhabitant tell and no event trace may contain a mood adjective:
  eerie, creepy, unsettling, strange, weird, sinister, ominous, uncanny, disturbing, horrifying,
  terrifying. The lights going out is not uncanny; the switches being found already off is. That
  claim could not have been written without reading that file and it is the most useful thing in
  this batch.
- **A letter is not a tell, and that was the shared defect.** The announcements this package
  writes are good - the echo's reads *"{0} is standing in this space, wearing what they were
  wearing this morning. {0} is also at home right now"* - but they fire once and scroll away,
  and then the pawn was just a pawn and the event had never happened. All twelve inhabitant
  families carry a `tellKey` and all eight events a `traceKey`, both refused at load if absent,
  both read off the thing rather than out of a notification. The event trace is written **above**
  the letter's early return, so a letterless event still leaves a record.
- **Ally existed nowhere and now does.** `RR_Inhabitant_Helper` takes the crew's side against
  what else is in the space and **will not leave with them**. The help is Core's: an existing
  non-hostile faction and `LordJob_DefendPoint`, so they fight the psychotic families with
  ordinary AI. A new faction would have been the *"new type of np0c"* the owner forbade. An ally
  is the most unnerving of the three relations, not the friendliest - an attack is explicable.
- **Animals are something you find, not only something that chases you.** Two families from Core
  kinds, unfactioned and in no mental state. The tell-carrying comp had to be patched onto Core's
  `AnimalThingBase` for an animal to say anything at all, and the limit is recorded in the patch
  rather than hidden: a mod animal that does not inherit it reads its tell in the letter.
- **Radio fragments: the one event with a person in it.** The last open item in *"Add repeated
  missing-person mysteries with radio fragments ..."*. All seven events before it were
  environmental. What makes it worth shipping is whose voice it is - a colonist standing in the
  base right now, falling back to the lost-pawn register, and with neither there is no fragment
  at all. **And mentioning somebody must not resolve them**: `TakeLostPawnName` *removes* what it
  returns, so a non-destructive `LostPawnNames()` was added and a plant proves the destructive
  version fails.
- **Two coverage suites where there were none.** `proof-unnerving-register.py` is 35 claims and
  `plant-unnerving-register.py` reports **32 of 32 caught**. Three plants came back MISSED across
  this batch and **all three were claims being wrong rather than code**: one compared call
  positions when the property was *a missing letter key must not lose the record*, one matched the
  old code's exact line layout, one tested a comment.
- **Two stale rows closed by measurement rather than work.** *"fourteen historical gameplay PNGs
  still in the package allowlist"* - audited: the tree holds **thirteen** images and every one is
  accounted for, twelve menu slides and `About/Preview.png`. There is no gameplay art and no
  audio at all; the `Sounds` tree held one empty folder and zero files and has been removed, so
  the absence reads off the tree rather than off a document.

## 0.12.87-dev - 2026-10-04 - The thing chasing you is a person or an animal, a gate's width means something, and the start names no other mod

- **What chases a crew is an ordinary RimWorld pawn now.** Owner: *"things that chase you are
  just npc pawns and wild animals and shit of the gasme spawned in procedurally and dynamically
  for randomness encounters, not somew new type of np0c in the backrooms ... not some blob
  figure, just normal core mechanics"*. It was `RR_QuietPursuer`, a `ThingDef` drawn as a
  1.4-tile black mote and driven by a bespoke `Thing_QuietPursuer` whose own comment read *"No
  native pawn AI or unbounded melee attacks."* Concretely it **teleported** -
  `pursuer.Position = cell` - so it never walked, never pathfound and never opened a door; it
  **struck once, scripted**, two points of blunt to a named arm only above 80% health; and it
  **withdrew after three advances by a counter**. All three are Core's now: a real `Pawn` from
  Core's own `PawnGenerator`, hunting with the same AI, pathing, doors, weapons and wounds as any
  hostile in the game. The def is retired, the class is deleted, and five saved fields that
  existed only to pace a scripted walk went with them.
- **The roster is Core pawn kinds and the map biome's own wild animals**, because the direction
  names two things. An animal is turned **manhunter** rather than given a faction, which is
  Core's way of saying *this one is coming for you* and is why an animal chaser needs nothing
  authored. The humanlike kinds are the three the inhabitant families already vetted, so the
  package has one list of *people down here who will hurt you* rather than two.
- **Procedural, and not a save-scum.** The kind is derived from the branch seed salted with the
  opening id, never `Rand`, so one opening always meets the same chaser and a reload cannot
  reroll what is hunting you. The roster is ordered before it is indexed: a derived index into an
  unordered list is reproducible by luck only, since def database order is not a promise.
- **AND THIS SUBSYSTEM HAD NO COVERAGE AT ALL.** No proof and no plant anywhere mentioned the
  pursuer - twenty-three plant suites, forty-nine proofs, and a 224-line bespoke threat passed
  every gate this project has for twenty-seven versions, because no instrument was pointed at it.
  `proof-chaser.py` is 21 claims and `plant-chaser.py` reports **17 of 17 caught**. Two plants
  reported MISSED on the first run and **both were the claims being wrong, not the code**: one
  matched the old code's exact three-line layout, and one tested a comment.
- **A gate's width decides what fits, including vehicles.** Owner: *"people through 1x1 cdoor
  gates, herd animals through 2x1 and vehicals through 3.1 and 3x2 depending size"*. The first
  two rungs already held from Core's own body sizes. **The vehicle rung did not exist**: width
  three returned *no limit*, so a three-wide gate admitted anything of any footprint and nothing
  anywhere could tell a 1x3 gate from a 2x3 one - two of the four legal footprints were the same
  gate as far as the game was concerned. `GateOpeningDepth` is new and *"depending size"*
  resolves to the vehicle's narrower dimension against the aperture's depth: a 1x2 runabout takes
  the 1x3, a 2x3 truck needs the 2x3, a 3x5 tank fits through neither. Recognised by footprint,
  never by type, so it works with the vehicle mods in the profile and identically with none.
- **The company's own books carry the company's label.** Owner: *"Mark the company-issued
  ones"*. Set once at the moment of granting and saved, by the arrival sweep that was already
  enumerating what Core created and by the genstep that places the start's two. Nothing scans for
  books later, so nothing can retro-tag one a player bought - and every other `TextBook` in the
  game keeps Core's own label byte for byte.
- **The starting scenario names no other mod's defs.** Owner: *"issues like the ballistic glass
  we used needs to be taken out of the starting scenerio to acturatley make sure it isnt needed
  to play the mod"*. `RB_ReinforcedGlassWall` and `RB_GlassWall` were the only two non-Core def
  references in any shipped start. Nothing changes for a Core-only player - the genstep already
  left a plain wall when ReBuild was absent - but the claim is checkable now, which is what *"to
  acturatley make sure"* asks for: `check-register-compliance.py` refuses a non-Core def
  reference in a shipped start or scenario.
- **And the first version of that rule read almost nothing.** It listed `thingDef` and missed
  `<thing>`, which is **114 of the 171 def references** in the file; a hand-planted foreign def
  sailed through and it reported PASS. The tag list is enumerated from the files now, and the
  same plant fails it.

## 0.12.86-dev - 2026-10-04 - Every tab is a utility, the door says what to do next, and the package asks for nothing

- **The queue was holding fragments of finished work, and the gate that guards it could not see
  them.** `tools/archive-finished-todo.py` ended an `[x]` item at the next blank line, so every
  row whose closure carried its own evidence archived its **bullet line only** and left the rest
  behind - **twelve stranded lines across 0.12.82-dev, 0.12.83-dev, 0.12.84-dev and
  0.12.85-dev**. Both halves of the owner's direction broke at once: `FINALIZED.md` was missing
  the record and `TODO.md` was holding finished text. The mover's proof is a reassembly identity,
  `kept + moved == original`, which is a real proof of the thing it proves and **says nothing
  about where a row ends**. Fixed at the source; the mover now refuses outright when unindented
  prose sits after a closed row rather than guessing which side it belongs to; every stranded
  line is recovered into `FINALIZED.md` with the row it came from, read from the pre-move
  snapshot the mover itself wrote. `tools/check-queue-integrity.py` is checker 18 and fails on a
  stranded continuation, on closure evidence that is not on a row, and on any `[x]` left in a
  queue.
- **The Operations panel is a utility, measured.** 4,015 on-screen words to **2,551**, with
  **1,583** moved onto hovers and words-per-action from 32.9 to 22.6. All eighteen pane files
  measured and named. `UI/OperationsControls.cs` holds the two primitives the whole panel now
  shares: a short line with its explanation on hover, and a control that stays visible and says
  why it will not work instead of being replaced by a sentence about its own absence.
- **And the instrument measuring it was blind twice.** It counted keys picked into a variable and
  translated later as **zero** - 367 words, the longest instructions in the panel, including the
  entire eleven-branch objective chain - so indirect groups are now resolved and charged at their
  **worst** branch, because exactly one draws per frame. And it read comments as code: a comment
  containing the word *tooltip* reclassified a heading into the hover bucket. Two ceilings went
  **up** when the blindness was removed and then came down by the work.
- **The door says what to do next.** The eleven start-up checks left a private method on the
  Operations window for `Gate/GateStartupChecklist.cs`, and the gate's own inspect card names the
  first unfinished one, first on the card - above ten readouts that all answered *what is the
  state* and none of which answered *what do I do*. The extraction normalises byte-for-byte
  identical to the original. One list, read by both surfaces, so they cannot disagree.
- **Setting the coordinate and opening the connection are commands on the door.**
  `Gate/GateAddressControls.cs`. They were the last two start-up actions that existed only as
  panel buttons, so a player could build, crew and calibrate the machine in the world and then
  had to find a tab to aim it. Both call the same services the pane calls, with the same freeze
  notice in front of the one that builds a map, and both grey out with a reason rather than
  disappearing.
- **The package declares no hard dependencies.** `About.xml` declared **293**; every one was
  already in `loadAfter`, so 1,462 lines of requirement wall came out and the load order changed
  by nothing at all. Verified as an identity before the deletion, not after.
- **A plant found the gap that deletion created.** With nothing declared, *every declared
  dependency must also be ordered* has nothing to iterate, so `loadAfter` became the only thing
  carrying the weight and the only thing unchecked - and the suite reported **MISSED** when a
  former dependency was removed from the order. `check-register-compliance.py` now requires
  `loadAfter` to match the 294-row profile register exactly. This package sat at position **197
  of 296** in the owner's live load order with 99 mods loading after it.
- **The claim rule inverted rather than relaxing.** The dangerous sentence used to be *"this
  needs nothing"*; it is now *"this works with everything"*, which nobody has shown.
  `check_broad_compatibility` refuses ten such phrasings while the declared count is zero. D1 is
  unmoved: do not announce compatibility until validation is complete. `ROADMAP.md` already
  listed promising blanket compatibility as a non-goal and nothing enforced it until now.
- **A plant suite had been crashing rather than running.** Two entries in
  `plant-startplacement.py` carried four elements where the baseline generator reads a fifth, so
  it raised `IndexError` on the line that prints `baseline` - which reads like the start of a
  run. Ninety-six plants had not been set since the day it was added. Fixed; the suite reports
  **105 of 105 caught**, and **853** plant anchors across twenty-three suites are findable in
  their targets.
- **Decision records amended in the same commit**, with every superseded owner quote struck in
  place rather than deleted: `GATE_0_DECISIONS.md` D3/D4, `ROADMAP.md`'s decision log,
  `ARCHITECTURE.md` B8, and the compliance row whose evidence line claimed `loadAfter` held Core
  alone when it holds 294 entries.

## 0.12.85-dev - 2026-10-04 - The machine tab is a status board, the gate dials blind, and a door can be boarded up

- **The machine tab stopped being a novel.** The same eleven start-up checks were drawn as
  fourteen wrapped paragraphs: a heading, a progress line, a next-up line carrying its full
  instruction, then eleven lines each carrying its own instruction again. It is a status board
  now - one row per system with a coloured light and Core's own checkbox glyph, one next-step
  line for the whole tab, and every instruction in full on the row's tooltip. Measured 356
  on-screen words to 58.
- **"Less of a text wall" is a number now.** `tools/check-operations-density.py` reports, per
  pane, the words a player reads on screen, the words on hover, how many things they can read and
  how many they can do, and the ratio between them. It is a per-pane ratchet: every pane's
  current figure is recorded and may only come down. The panel measures 3,980 on-screen words
  against 121 controls.
- **The status lights are never the only channel.** Colour alone fails the accessibility brief
  and a player's colourblind setting cannot help a dot that means something by hue, so the
  display-style rule permits exactly two named indicator colours in exactly that file and
  requires the glyph beside them. Both the checker and its proof police the pair.
- **Internal identifiers came off the player's screen.** The short address code was never
  missing - it has been AI-01, AI-02 since the first version - but the raw coordinate id leaked
  out beside it in four places, one of them putting a thirty-character internal string on a
  button. One property is now the thing every readout asks for.
- **A natural door can be boarded up, by a colonist, for 25 wood.** It fetches the wood, carries
  it there, nails it shut, and the place behind it closes - freeing one of the five open-map
  slots. Closing a place already existed in a panel; what was missing is that it happens in the
  world. The release conditions are re-checked at the end as well as the start, because a crew
  can walk in while the boards are being carried, and the wood is spent only after the place
  actually closes.
- **Three operational gates, refused at designation.** A player who had built a fourth door,
  wired it and crewed it before being told would have spent all of that for nothing. Three
  called addresses plus the colony is four of the five maps the game holds open; the fifth is the
  margin for a door somebody walks through without planning to.
- **A gate can dial somewhere nobody asked for.** Every coordinate until now arrived because
  something named it - a request, a quest, a contract. The dial is unpredictable and the place is
  not: the address derives from a monotonic index, never from `Rand`, so the same slot is always
  the same place and a reload does not move it. It creates an address, not a map.

## 0.12.84-dev - 2026-10-04 - Roads are wide, neighbourhoods are blocks, and twelve slides are all disclosed

- **A road is now an arrangement rather than a room with lane markings in it.** A straight run of
  linked rooms that carries on past either of its ends has every corridor along it cut at the wide
  half-width, whatever that pair's own roll said. A run already existed; it looked like a chain of
  ordinary hallways. Derived from the saved graph and stored nowhere, so the carver, the
  reachability proof and the layout probe cannot disagree about where a road is.
- **A road braid was written and then deleted, on the measurement.** A pass that picked a row and
  linked every slot along it moved the longest straight run not at all: 6 to 8 either way, which at
  depth 3 and deeper is the entire slot row. At an average of five links per room the braids
  already join almost every adjacent collinear pair. A pass whose effect nobody can measure is a
  pass nobody can defend.
- **A neighbourhood is a block of rooms pressed wall to wall off one hub**, and two findings were
  needed to make it happen at all. It has to run before the diagonal and reach braids, because a
  room holding five or six links cannot slide - any move carrying one past its stated reach is
  undone - and placed after them the whole pass measured as a no-op. And the hub's neighbours are
  offered least-connected first, so the mobile ones are tried before the hopeless ones have shifted
  the geometry. Back-to-back pairs rose from 248 to 376 at the first level and 366 to 488 at depth
  3, in blocks of four. Nothing was relaxed: every move still satisfies all four conditions or is
  put back.
- **The link prune stopped guessing which edges the spanning tree owns.** It refused to touch
  anything whose room centres shared an axis, which was true of the tree and too coarse for the
  reach braid - that makes links two slots apart along an axis, and the neighbourhood push could
  leave one with no route. It now removes the edge and keeps the removal only if every room still
  claiming a route can still be reached from the threshold.
- **Six new menu slides, twelve in total**, all 1672x941, all discovered by the existing folder
  scan with no code change - and they are loading-screen backgrounds as well as menu backgrounds.
- **Four shipped images had no provenance row at all, and nothing could see it.** The disclosure
  claim was satisfied by one provenance file existing anywhere, so when the slide count went from
  six to twelve the 2026-09-29 batch was shipping undisclosed. Steam's AI-content requirement is
  per asset. All four are registered retroactively and the claim now refuses any slide without its
  own row.

## 0.12.83-dev - 2026-10-04 - A floor has an architecture, forty-four kinds of room, and the freeze says so first

- **A coordinate has a motif, and its rooms vary from it.** Seven room shapes already existed and
  every room rolled its own independently of every other room, which does not make a pattern, it
  makes noise: one room a wedge, the next bays, the next a cross, reading as damage rather than
  architecture. A coordinate now draws one shape and one theme from its own seed, and how hard
  that grip holds falls with depth. Measured: rooms on the motif shape run at 89.3% at the first
  level, 72.3% at depth 3, 44.5% at depth 6 and 36.5% at depth 8, with all seven shapes present at
  every depth and a random floor sitting at 14.3%. **One number produces both the monotonous
  shallow floors the yellow look depends on and the incoherent deep ones.**
- **Forty-four kinds of room, up from sixteen, and a floor is somewhere rather than a list.**
  Archetypes were drawn against their own weight alone, so a coordinate held a classroom beside a
  weapons locker beside a nursery. Each now declares which kinds of place it belongs to, and a
  coordinate's own theme makes a matching one three times likelier - a bias and never a filter,
  because a market holding nothing but shops is a themed level rather than a Backrooms level.
- **The kinds that were asked for, by name, and twenty-one more besides.** Shop fronts, mall
  concourses, food courts, checkout lanes, stockrooms, barracks, checkpoints, motor pools,
  briefing rooms, apartments, laundries, play rooms, stairwell landings, service tunnels,
  substations, pump houses, roadways, cinemas, waiting rooms, changing rooms, records vaults,
  quiet rooms and infirmaries - plus endless shelving whose aisles meet at the far end, a room
  with its furniture moved to one wall still facing the way it was, a ward symmetrical about an
  axis the door is not on, and a room holding one chair, in the middle, facing a corner.
  Forty-four archetypes against seven shapes is over three hundred distinguishable rooms before a
  single slot is rolled.
- **The generation freeze now says so before it happens.** Carving a 300x300 map runs on the main
  thread inside Core's map generation, and an unexplained freeze reads as a crash. Both of the
  Operations pane's openings now show a full-screen notice first, carrying one of the mod's own
  menu images, and the generation then runs inside a long event whose wait text is ours. There is
  a tone per shipped scenario: the company reads an instrument, the shop reads its own back room,
  and somebody alone in the dark reads neither.
- **The main menu opened on the same picture every single time.** The slide index was pinned to
  zero in the constructor and reset to zero again in the settings handler, so the first thing
  anybody ever saw - and the backdrop behind every load started from the menu - was slide one of
  six, forever. Drawn at random now, from the wall clock rather than from the game's seeded
  randomness, which every generated place depends on.
- Internal: eight archetypes shipped with furniture and nothing worth carrying out, which an
  existing proof caught against a standing owner direction. The layout probe keeps no copy of the
  shape rule and measures it from the planner's own function. A theme tag that nothing can draw is
  now a load-time config error naming the def, because the alternative is completely silent.
  Twenty-three plant suites, 836 anchors; the menu art had no plant coverage at all this morning.

## 0.12.82-dev - 2026-10-04 - The corridors bend, a room has five ways out, and the rock is worth digging

- **Corridors are not all straight any more, and there are seven shapes of bend rather than one.**
  A corridor could only run along one axis, which is *why* a link had to join grid-adjacent slots:
  four neighbours, so a measured maximum degree of 4 at every depth and an average of 2.2 to 2.4 —
  one way in and one way out, which is a line with rooms on it. Routes now run through the rock
  lanes between rooms as elbows, as five-leg routes that reach a slot two away, and as a u-turn
  that leaves through the wall facing away from where it is going. A lane is defined by a room's
  own wall rather than by the slot grid, so a route needs nothing but the two rooms' rectangles.
- **A room now has 0 to 16 ways out, averaging 5.** Three mechanisms: a diagonal braid, a reach
  braid to slots two away, and one slot in eight being a junction that takes every link it can —
  which gives a spread rather than moving every room to the same new number. Rooms with only one
  link fell from 6.5% to under 1%.
- **Some rooms have no way in at all, and you find them by mining.** A sealed vault's slot is
  reserved before the maze walk, so nothing can link to it, and a seam of ore runs from it to the
  nearest room that does have a door. The reachability proof now asks its question of rooms that
  *claim* a route; a room with none is reached with a pick.
- **The rock is worth digging.** Ore veins run from every door-onto-nothing, between near rooms a
  corridor does not join, and out of every sealed vault — plus scattered deposits at three times
  Core's own density, read off Core's own scatter step rather than copied. Deep-drillable
  resources including chemfuel are written under the whole coordinate. Nothing is named: the ore
  list is read out of the loaded game, so other mods' ores are included without an adapter.
- **A deep level is no longer 83% bare rock.** Room fill rose from 17.1% to 44.9% at depth, and
  from 46.0% to 57.2% at the first level. The cause was arithmetic — a finer slot grid fills
  *less* space, because the rock between rooms is fixed per boundary — so the grid stops at
  eight slots per axis and the map margin came down from fourteen cells to six. The room cap is
  unchanged.
- **Doors are no longer all at the exact middle of a wall.** That was never a door rule: a
  corridor could only run along a line both room centres shared, so the midpoint was the only cell
  one could arrive at. One function now decides where a straight corridor meets two rooms, and the
  door is wherever that line lands. It also unsealed the grand hall, whose centre sits between its
  two slots and which could previously only lead out along its own row.
- **Rooms stand back to back far more often, and that had quietly regressed.** Only dead ends were
  ever pushed together, and the better-connected maze left few dead ends: measured pairs fell from
  131 to 23 as a side effect of a different feature. Any room may be pushed now, because the push
  proves the move itself — on the map, nothing overlapped, no existing corridor broken, and the
  two rooms really share a wall, or it is undone.
- **The main menu opened on the same picture every single time.** The slide index was pinned to
  zero in two places, so the first thing anyone ever saw — and the backdrop behind every load
  started from the menu — was slide one of six. It is drawn at random now, and the slide list
  moved to one place so the menu and every other surface take the same images from the same source.
- Internal: the validator stopped keeping its own copy of the room-adjacency rule and asks the
  planner, which was a live defect — the planner's half had to grow and the copy would have
  refused every graph it had just learned to build, on load, for every saved coordinate. The
  layout probe stopped keeping a third copy for its own diagnostics, which had begun reporting the
  wrong reason for every refusal.

## 0.12.81-dev - 2026-10-03 - A way back out of the world, a door you can commission first, and the grand hall stops hiding in one corner

- **A crew that walks out of the Backrooms onto a world tile can now walk back in.** Emerging was
  a one-way trip: the exit existed, the way home did not. Claiming the tile now also puts a gate
  on it, marked and connected back to the level you came from. It is built **before** anybody
  steps through, so if it cannot be built nobody moves and the door you came to is still there.
  At five maps held the crew still forms a caravan and walks home overland, as before.
- **Any door can be commissioned as the gate before its circuit exists.** Picking the door used to
  demand a single comms console, a single battery and a single machining table all at once, so on
  a company start with no battery bound the button simply refused. Now the door becomes the gate
  first; if the headquarters already has exactly one of each they are wired at the same time,
  otherwise you finish the circuit on the Operations gate pane and the gate tells you what it is
  still missing.
- **An open gate no longer asks for power to send people through it.** Passing somebody through an
  aperture that is already held was being charged the cost of *opening* one, and refusing with a
  message about reserve power in the batteries. Opening and recovering a connection still cost what
  they cost.
- **The company's record book says what it is.** A blank one was indistinguishable from any other
  book on the shelf and its card said nothing at all. It now reads as the journal the company
  issues you, with what to do with it.
- **The grand hall is no longer always in the same corner of the map.** Every level ever generated
  opened in the bottom-left; the hall's position and its orientation are now part of the level's
  own seed, so revisiting is the same place but two different levels are not. Roughly half of
  levels now open in a hall that runs the other way.

## 0.12.80-dev - 2026-10-02 - Architect gets its corner back, and the shop stocks a meal that keeps

- **The Architect tab is at the far left again.** The Operations tab had taken that slot, so
  reaching for Architect out of habit opened Operations instead. The two have swapped: Architect
  sits where it always did and Operations is immediately to its right. **Nothing about Core's own
  buttons or any other mod's was changed to do it** - only this mod's own button moved.
- **The Furniture & Knickknack Store starts with 100 packaged survival meals instead of 24 simple
  meals.** A simple meal spoils, so a shop start was handing you two dozen meals and then quietly
  taking them away. It was also the only start granting a simple meal at all; the other two
  already used survival packs.

Nothing else in the game changed. No gameplay, balance, performance or compatibility result is
claimed.

## 0.12.79-dev - 2026-10-01 - you do not need a debug server to play this

- **The mod no longer tells you it requires a debug server.** A QA instrument that only its author
  attaches to a running game was declared as a hard requirement, so a mod manager would have asked
  you to install one. It is gone from the requirement list and from the load order. **293
  requirements, not 294.**
- Nothing else about the requirement list changed, and it was checked rather than assumed: every
  requirement declared is still installed and active, and nothing active is undeclared.

Nothing in the game changed. No gameplay, balance, performance or compatibility result is claimed.

## 0.12.78-dev - 2026-10-01 - a locked door said nothing, and no start shipped the book

- **A locked gate refused every crossing in silence.** Ordering somebody through checked that the
  cell on the near side was standable and reachable, and never asked whether the door would open.
  It now says so: *"That gate's door is locked, so nobody can walk through it."*
- **No start shipped the record book every expedition requires.** The laboratory spawned 112
  fixtures and not one book, so the first dispatch always refused. It carries two now - one to
  take, one in reserve.
- **And for the starts that begin with nothing, the corporation sends them.** Build and calibrate
  a gate with no book anywhere and blank record books arrive. It will send again if you lose
  them, and never while you still have one.
- **The quest to go through your own gate already reached every start** and is now asserted rather
  than assumed - the request line has no scenario check anywhere in it, and its first two requests
  are power the gate and assemble and calibrate it.
- **One door the facility was missing.** The east-west service corridor was walled off at its east
  end, with no way out of the compound on that side.

Full record: [a locked door said nothing](docs/implementation/CROSSING_AND_BOOK_IMPLEMENTATION.md).
No gameplay, balance, performance or compatibility result is claimed.

## 0.12.77-dev - 2026-10-01 - every battery counts, and the refusal tells you the truth

- **A gate now runs off its whole circuit.** It used to read charge from the single battery you
  bound to it and ignore every other battery on the same power net, so adding batteries did
  nothing. Bind one as the anchor, then put **as many on the circuit as you like** — there is no
  limit, and the readout shows the circuit's total.
- **And it spends from the whole circuit too.** Worse than the reading: a drained anchor battery
  refused to open or hold a connection *while ten full batteries sat beside it on the same net*.
- **A refusal now names the real cause.** Seven different problems used to produce one message:
  *"The laboratory connection for that address is not open."* So a flat battery reported an
  address fault. There are now separate reasons for no stored charge, an expedition holding the
  connection, an emergency in progress, an expired window, and an operator off station.
- **The wiki.** How to install it, how to set up your mod manager, how to play, what is through
  the gate, and what to do when something refuses — written as short pages instead of one long
  document, and linked from the mod description in game.
- **Reports get signed off, and your people remember where they have been** — carried over from
  the previous build and now documented.

Full record: [every battery counts](docs/implementation/GATE_CIRCUIT_IMPLEMENTATION.md). No
gameplay, balance, performance or compatibility result is claimed.

## 0.12.76-dev - 2026-10-01 - the company clears the site, and the mod finally admits what it needs

- **If everyone at the laboratory goes down, The Company comes.** Not when they die - when they are
  all *down*. A squad arrives on all-access passes, and it does not leave anybody standing who was
  there. The dead are buried on the property where there is ground that will take a grave, and put
  in the fire where there is not. Damaged walls and fixtures come back to full repair. Every open
  connection is shut at the gate, and the gate is left commissioned. Three replacement staff land
  with supplies, on the ordinary wage, and **you never lose the game.**
- **It costs you everything on paper.** Every bearer bond anywhere on your maps is collected and
  credited nowhere, and up to 25,000,000 credits is drawn from the account as restocking the petty
  cash - whatever is there, and never below zero. The letter tells you the figures rather than
  saying the site has been secured.
- **This happens at the laboratory only.** The furniture store and the solo start keep the clean-up
  team they already had: five staff, and a trigger that waits for actual death.
- **The mod now declares what it needs, so your mod manager can tell you what is missing.** All five
  expansions and the 289 mods this build is authored against, each with a name and a link, and every
  one of them also declared as a load-order constraint - so a sorting manager puts this mod where it
  belongs on its own. It was previously declaring nothing at all and loading **197th of 296, with 99
  mods coming after it.**
- **Nothing from another mod is assumed.** Content is looked up by name and a missing one degrades
  what depends on it rather than throwing.
- **Reports get signed off now.** A second person reads a finished analysis and either stands behind
  it or returns it - the fourth of the four workflows, after analyse, compare and interview. The
  analyst cannot review their own work, and nothing can be signed off while two of your crew are
  still contradicting each other on the record.
- **Your people remember where they have been.** Field history is kept per person, and an operator
  who has personally walked an address brings the gate up faster on it. The crew panel says who is a
  novice, who is a veteran, and who knows this particular route.

Full record: [the company clears the site](docs/implementation/CLEAR_SQUAD_IMPLEMENTATION.md). No
gameplay, balance, performance or compatibility result is claimed.

## 0.12.39-dev - 2026-09-29 - the game now tells you what it does with your other mods

- **The company panel lists the optional mods this mod has a position on, and what that position is.** Five of them, with the register row each came from, whether it is loaded, and in plain words what this mod will and will not do with it. That answer used to live only in a spreadsheet outside the game.
- **Nothing changes because a mod is installed.** No route, contract, gate or expedition will ever ask you for a vehicle or a gravship. Nothing another mod owns is patched, read or copied.
- **Nothing from orbit will ever turn up in a Backrooms space.** What lives in there comes only from this mod's own list, and that is checked on every build.
- **There is a page about playing together now**, with the server setup and what the experience actually is. It says plainly that each player runs their own company - no shared colony, no shared map, no shared research - and that none of it has been tested in play.
- **Every line of that says "loaded", never "supported".** No game has been launched from this project yet, and the build now refuses any document that claims otherwise.

Full record: [the register said don't patch, so the hook is a sentence](docs/implementation/INTEGRATIONS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.38-dev - 2026-09-29 - a shot-up gate will not hold a connection

- **Damage to a gate now matters.** A gate could be shot to twelve per cent and still open a connection and hold it perfectly. Below half condition it loses its calibration, refuses to open, and says why - repair it with ordinary construction work and calibrate it again, exactly as you did the first time. If a connection is live when it goes, the crews get their return window rather than being cut off.
- **Every address you have dialled now records how the trips went.** How many came back clean, how many ended in an emergency, and the rate - shown when you pick that address out of the gate's history, which is where it helps. An address nobody has come back from yet says so rather than showing a made-up figure.
- **Nothing about this is random.** A gate fails for a reason you can read, every time.

Full record: [a gate read no damage at all](docs/implementation/GATE_SUBSYSTEMS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.37-dev - 2026-09-29 - every coordinate in the game was made of wood

- **Spaces are furnished out of different materials now.** Every table, chair, shelf and lamp in every room of every coordinate was wooden - one hardcoded material, not the item's own default. A space now has a short palette of its own drawn from whatever materials your game has, so two spaces look different and each looks like somewhere that was fitted out.
- **The same space always looks the same**, on any machine and whatever else you have installed. That was not free and it is the fiddliest part of the change.
- **Confirmed rather than changed: you can strip a coordinate's floors and get the material back.** They were always ordinary floors; nothing about them was special. The same goes for the rock - it comes from the world's own stone types.
- **Confirmed rather than changed: what lives in a space already scales with how deep it is and how rich you are.**
- **A new build check refuses a setting the game would silently ignore.** A mistyped field name in mod data is not an error in RimWorld - it is logged and skipped - and one had been quietly doing nothing for fourteen definitions until it was caught by hand.

Full record: [every coordinate in the game was made of wood](docs/implementation/GENERATION_MATERIALS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.36-dev - 2026-09-29 - roofs, snow, and reporting in

- **Colonists will cross a gate to build a roof or take one down**, wherever you paint the area. On a Backrooms coordinate there is nothing to do, because it is already solid rock overhead and taking a roof off in there was never allowed.
- **They will also cross to clear snow, sand and pollution**, which only matters at a registered site: a coordinate has no outside and never gets weather.
- **Crew who come back from a trip now owe the company a report**, and the company will not send anybody out again until they have given it. Take the report from the facilities pane; somebody else has to take it, and they have to be a decent enough talker.
- **Confirmed rather than changed: the ground around a gate is ordinary ground.** Mine it, wall it, roof it, put a bedroom there. Nothing about a gate looks at its neighbours, and the only reserved square is the one people stand on to walk through.

Full record: [four area types, a debrief that gates the next trip, and two rows that were already true](docs/implementation/AREAS_AND_DEBRIEF_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.35-dev - 2026-09-29 - containment you can see from the other side of a gate

- **You are now told when containment fails somewhere you are not looking.** The base game warns you about the map you have open; this warns you about every other place the company holds something, which is the warning that actually matters when you are standing in a coordinate watching a crew work.
- **A holding platform that has lost power with something on it now says so.** The base game has no warning for that at all.
- **The branch has a standing order for a containment failure: cut every open connection and bring the crews home.** It is on by default, the facilities pane says which way it is set, and you can turn it off if you would rather decide each time.
- **You can sound the alarm yourself** from the comms console, which does the same thing on demand.
- **The facilities report has a containment section** listing what the company is holding across every site, and a containment category that finds any holding platform or prisoner bed without naming a single one.

Full record: [containment you can see from the other side of a gate](docs/implementation/CONTAINMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.34-dev - 2026-09-29 - fifteen more reasons to walk through a gate

- **Colonists will now cross a gate to load and empty machines on the other side** - gene banks, growth vats, gene extractors, subcore scanners, mech chargers, waste containers, biosculpter pods, bioferrite harvesters and entity holding platforms. Everything the worker handles is already on the far side; nobody and nothing is ever carried through the gate into a machine.
- **Colonists will cross a gate to paint, and to strip paint.** Mark a floor or a wall on a coordinate and somebody will come and do it, provided there is dye over there. Marking nothing means nobody comes.
- **A travel priority you set is the priority that gets used.** Six of the mod's own shipped travel priorities were being quietly replaced with a lower number every time a game loaded, which could turn a worker around part way to a gate. Each family's slider now reaches its own shipped value.
- No expansion is required for any of this. With Biotech, Ideology or Anomaly missing, the machines simply are not there and nothing is offered.

Full record: [fifteen work givers, and a clamp that was overwriting the mod's own numbers](docs/implementation/MACHINE_LOADING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.33-dev - 2026-09-29 - three things you could not see

- **You can send somebody through a gate from the gate itself now.** Select who you mean, click the door, pick them off the list. Anyone who cannot cross is listed with the reason instead of being left out.
- **Every coordinate now tells you how hostile it is** - quiet, unsettled, active or hostile. The game has always known; it never said.
- **Selling everything at a credit beacon asks first.** It is a large, irreversible action and the only warning used to be text you read after clicking.
- **Surgery on a crew member always happens at home, and now that is written down as a rule rather than a gap.** The base game needs the patient, the doctor and the medicine in one place, so a casualty is carried back through the gate to a bed - which the rescue work has always done.
- **Patient feeding and prisoner care across a gate were already working.** Checked rather than assumed.

Full record: [surgery cannot cross, and three things were invisible](docs/implementation/MEDICAL_AND_SURFACES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.32-dev - 2026-09-29 - everything is read by something

- **You can cut a connection now without disabling the gate.** A new button on a working gate ends the opening immediately and starts the emergency return window, so anyone on the far side comes home - and the gate is still there for next time. That is different from the kill switch, which stays thrown until you clear it.
- **The whole mod was audited for things that were built and then never hooked up.** 258 definitions and 102 actions checked. The cutoff above was one of two that had no way to reach them; the other turned out to be a duplicate of something that already worked, and was removed.
- **A check now refuses to ship anything this mod adds that nothing reads.** Four times in this project's history something was written and left unreachable - once it was the entire contract line.

Full record: [everything is read by something](docs/implementation/WIRING_AUDIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.31-dev - 2026-09-29 - a wide gate out of plain doors

- **You can build a wide gate out of ordinary doors now.** Put two or three plain doors side by side in the same wall, designate one as a gate, and bind the others into it. The whole run becomes one gate.
- **No mod needed for any gate size.** One-cell and two-cell were already free - the base game's ornate door is two wide - and a bound run covers three-wide and the big two-by-three shape. If you do run a door mod, its real wide doors still work exactly as before.
- **It is one gate, not several.** One opening, one spin-up, one address, and the same width read from both sides. The extra doors are part of the gate rather than gates of their own.
- **A bigger opening costs more.** More power to hold open and more work to bring up, in proportion, exactly as a real wide door does.
- **The run has to be a filled rectangle** and no bigger than the largest gate size. A ring of doors around a gap is not an opening.
- **Neither binding nor releasing can be done while the gate is working.** Release turns the extra doors back into ordinary doors.

Full record: [a wide gate out of plain doors](docs/implementation/GATE_DOOR_RUN_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.30-dev - 2026-09-29 - you can call the company

- **Two of the three starts could never reach the campaign at all.** The shop opening and the solo/group opening both begin with no corporation watching, and there was no way to change that - which meant no contracts, no company catalogue, and no clean-up team coming for a stranded crew, for the whole game.
- **You can now call them, from a communications console.** Once they have you on the books the Async Industries request line starts, exactly as it does for the company start.
- **You have to have something to tell them.** A powered console, somebody awake who can speak, a coordinate you have actually been into, and a record book you brought home and had analysed. You are not calling for help; you are calling to say you found something.
- **The button always shows why it is not ready yet** rather than hiding until it is.
- **There is no way to take the call back.**

Full record: [two of three starts had no campaign](docs/implementation/CORPORATE_CONTACT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.29-dev - 2026-09-29 - the top of the research ladder

- **Six new company projects, one for each branch that had somewhere left to go.**
  - **Practised Dialling** - bringing any gate up takes a fifth less work, on every route rather than only familiar ones.
  - **Decompression** - a crew shakes the place off twice as fast once they are out of it.
  - **Open Market** - the company stops underpaying you for ordinary salvage.
  - **Statement Discipline** - most of the branch can take a statement, not just your two most sociable staff.
  - **Surface Reading** - ways into the Backrooms turn up on your own maps noticeably more often.
  - **Steady Nerve** - the worst the place can weigh on somebody drops from severe to noticeable.
- **Two branches get nothing, on purpose.** Company logistics has already learned everything there is to learn about delivery, and the gate line's top project already stops the countdown entirely - there is nothing above a connection that does not end.
- **Nothing was invented to fill a gap.** Every one of the six moves a number that was already in the game and that nothing else was touching.

Full record: [six rungs, and two that could not exist](docs/implementation/RESEARCH_TIER_4_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.28-dev - 2026-09-29 - nobody is lying

- **You can now settle a disagreement between two crew.** A staff member takes both statements and the company files one of them as its version of events.
- **Neither crew member is wrong, and the game does not pretend otherwise.** Both accounts were checked against the coordinate when they were given. They disagree because the marker moved between the two visits - which is a thing that happens down there.
- **The account you do not file stays on the record**, with the name of the person who gave it. Nothing is erased.
- **An interviewer needs Social 4**, has to be awake and able to talk, and cannot be one of the crew who gave an account. If nobody on staff qualifies, the readout says so and says what is needed.
- **A finished analysis cannot be reopened.** Once a report is written, the disagreement stays on the record exactly as it was.

Full record: [nobody is lying](docs/implementation/INTERVIEW_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.27-dev - 2026-09-29 - you cannot brick your own gate

- **Nothing can be built on the cell your crew has to stand on to use a gate.** The game refuses the placement and says which gate it is protecting, instead of letting you wall your own way in and find out later.
- **Laying a floor there is fine.** Carpet it, tile it, do what you like with the ground.
- **A power conduit or anything else you can walk over is fine too.** The rule is only about things that would stop somebody standing there.
- **It works with buildings from other mods** without any of those mods being changed.
- **Your existing gates already could not break this way** - that was fixed earlier. This stops you doing it by accident in the first place.

Full record: [you cannot brick your own gate](docs/implementation/GATE_APPROACH_CELL_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.26-dev - 2026-09-29 - the in-game text stops naming things that do not exist

- **Fourteen pieces of in-game text told you to use equipment this mod no longer has.** The objectives panel, the contract terms, three room clues and the what-to-do-next readouts were all naming a return beacon, a survey tag, a sealed evidence case or a field recorder - gear retired between four and fifteen checkpoints ago.
- **They now name what the game actually gives you:** the record book you carry, glow pods designated as numbered route markers, and the shelf designated as your records archive.
- **Two of those are different instructions, not different words.** Custody is a place now, so a crew brings the book home to a shelf rather than returning it inside a case. And a marker is still numbered - the numbering survived the tag.
- **Three dead labels were removed** - text describing two fixtures that stopped existing long ago.
- **A check now refuses to ship text that names retired equipment**, so this cannot come back.

Full record: [the in-game text stops naming things that do not exist](docs/implementation/RETIRED_VOCABULARY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.25-dev - 2026-09-29 - two crew who disagree

- **A second crew member's account of the same thing is now kept.** Before, whoever spoke first was the only one on the record: an identical account was folded into theirs and a **different** account was thrown away silently.
- **Two crew who disagree about one room now produce a real disagreement.** The company files the first account, keeps the second, and the evidence readout names both, who gave them, when, and where each of them puts the marker.
- **You are told when it happens**, once, at the coordinate.
- **A disagreement still counts as testimony.** The company does not pretend the second person never spoke, so the contract that asks you to report a disagreement is now satisfied by an actual disagreement instead of only by visiting two different coordinates.
- **One person counts once**, however long they stand there.
- **Nothing in your save breaks.** A save with no accounts on record simply has none, which is true of it.

**Not yet:** nothing resolves a disagreement. The accounts sit on the record and the analysis reports them; deciding which one the company files is the next piece of work.

Full record: [two crew who disagree](docs/implementation/CONTRADICTORY_ACCOUNTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.24-dev - 2026-09-29 - the recorder became the book

- **Field crews now write straight into the record book they carry.** The separate field recorder is gone from every start and can no longer be built or bought. One item does both jobs, so the record and the thing that made it can no longer get separated.
- **Nothing in your save breaks.** A recorder you already own still loads, still weighs the same, and can still be recovered from a coordinate. It is simply never issued again.
- **The company now sells blank record books.** Books burn, and the base game only sells them to you by chance, so a branch that loses its book can order more instead of being unable to send anyone out.
- **Surveying and recording now follow the same rule:** somebody on the crew has to be carrying the book. Before, a book left on the floor still counted for one of the two.
- **Losing the book is now the thing that stops a survey**, rather than losing a second piece of equipment nobody could see the point of.

Full record: [the recorder became the book](docs/implementation/RECORD_BOOK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.23-dev - 2026-09-29 - the handoff, audited again

- **Nothing in the game changed.** This is the session handoff, and writing it properly turned up six things in it that were no longer true.
- **The count of how the mod's own internal checks report themselves was stale**, and measuring it found two that do not announce themselves at all - which is a better argument for the way they are run, not a worse one.
- **Three finished pieces of work were still listed as pending**, including all seven third-tier research projects.
- **A question was asked instead of written down.** It had been parked in the document as something for the owner to decide later; the owner asked for it immediately, answered it, and the handoff now records the decision.

Full record: [the handoff, audited again](docs/implementation/HANDOFF_AUDIT_2_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.22-dev - 2026-09-29 - the last new art is gone

- **This mod no longer adds a single piece of gameplay art.** The four custom images it still shipped - the field recorder, the route recording, the return anchor and the Quiet Pursuer - now use pictures the base game already has.
- **The Quiet Pursuer is a shape you cannot resolve.** It uses the base game's plain black mote, which suits it better than a drawing did: you are not meant to get a good look at it.
- **Nothing about how any of them behaves changed.** Every rule you can learn about the Pursuer, every route recording, every return anchor works exactly as before.
- **The rule is now checked rather than remembered.** The only images this mod ships are the main-menu slides, and a check refuses any other.

Full record: [the last new art is gone](docs/implementation/NO_NEW_ART_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.21-dev - 2026-09-29 - a way out into the world

- **You can now get out of the Backrooms without having marked a door first.** Before this, a way out could only ever arrive at a door you had already marked back home - and if you had not marked one, the survey quietly turned the way out into a way *deeper*. A branch with nothing marked could never get out at all.
- **A way out now leads somewhere on the world map you do not own.** Walk through, and if the company can take on another place, that tile becomes yours and your crew is standing in it. If you are already running as many places as you can, they come out as a caravan and make their own way from there.
- **Five places is the limit**, counting the Backrooms level you are standing in and every tile you have claimed this way - and if you have set your own colony limit lower than that, yours wins.
- **Nobody can be taken from you by any of this.** A gate closing on a crew, a window running out, and crossing a gate all still leave your people yours. Walking out is something you click, and the crew stays yours on the other side.

Full record: [a way out into the world](docs/implementation/WORLD_EXIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.20-dev - 2026-09-29 - the register, by the column that matters

- **The mod register can now be asked the question it exists to answer.** Every one of its 295 rows carries a trace code saying which part of this mod it bears on, and there was no way to search by it. Now there is, so "what applies to the thing I am about to build" is one command.
- **A new check verifies this mod still uses other people's mods the way the register says to.** It confirms no hard dependency on any mod, that the one mod we patch at all is a reviewed row, that the patch does nothing when that mod is absent, and that none of another mod's content has been copied in here.
- **We patch exactly one mod, optionally**, and depend on none.

Full record: [the register, by the column that matters](docs/implementation/REGISTER_COMPLIANCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.19-dev - 2026-09-29 - the yellow rooms were never carpeted

- **A real, visible bug, fixed.** The first Backrooms level you ever walk into is supposed to be worn yellow carpet. It has been **wood plank flooring** since the look shipped, in every game, on every seed. Nothing ever reported it.
- **The cause:** RimWorld has no floor called "Carpet". It has a *template* that makes one carpet per colour, so asking for "Carpet" quietly returned nothing and the code fell back to wood. The fix uses the colour each level already names, so mustard carpet downstairs, faded green in the office levels, burnt umber where the place stops making sense.
- **Three things I had reported as missing are already in the game.** The rock between rooms is mineable in whatever stone that world tile actually has, and lifting a floor gives you back half of what it cost - carpet included. I was wrong about all three and the record says so.
- **All of that is now checked**, including the specific way it could silently break again: swapping in one of the floors RimWorld gives nothing back for.

Full record: [the yellow rooms were never carpeted](docs/implementation/INTERIOR_RESOURCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.18-dev - 2026-09-29 - the third rung of every branch

- **Seven new research projects, one for each branch**, and every one of them changes a number you can watch change. Hold twelve remote sites instead of eight. Pay a sixth of your overhead per site instead of a quarter. Have a shipment left at a site with nobody there. Find a way onward sooner. Find the way *out* more often. Finish a survey faster. Build a room that holds the place back better.
- **This tier was deleted rather than written four versions ago**, because there was genuinely nothing for four of the branches to move. Building remote sites gave them all something real.
- **Two things deliberately did not change.** A coordinate still never yields more than two ways onward - that limit is what keeps the whole chain of spaces finite. And a sheltered room never stops the place wearing on you entirely; nothing will make the Backrooms somewhere to live.
- **Every unlock is checked against the code that honours it**, so no card can promise something that does nothing.

Full record: [the third rung of every branch](docs/implementation/RESEARCH_TIER_3_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.17-dev - 2026-09-29 - four more menu slides

- **Six main-menu images now cycle instead of two.** Laboratory operations, industrial gate logistics, a corridor encounter and a silent recovery join the two that were already there.
- **A slide that would never have appeared is now caught before it ships.** The slideshow only shows files whose name starts with `RR_Menu_`, so a correctly-drawn image with the wrong filename used to be invisible with nothing anywhere saying so.
- **A truncated or half-copied image is caught too**, which matters because the game would only fail when it tried to load it, long after the build said everything was fine.
- **How the images were made is recorded and ships with the mod**, including the exact instructions used for each one.

Full record: [four more menu slides](docs/implementation/MENU_SLIDES_LANDED_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.16-dev - 2026-09-29 - the menu takes any number of slides

- **New main-menu art is now a drop-in.** Any image named `RR_Menu_*.png` placed in the menu texture folder becomes a slide, in filename order, with no code change at all.
- **Another mod's menu art can never leak into the slideshow.** The folder is a shared content path, so the name prefix is what keeps the slideshow ours.
- **A full art brief ships with the mod**, naming twelve scenes drawn from things the mod actually contains, with the exact image size, the screen regions to keep clear, and the palette the game already uses.
- **Two integrity notes that had been wrong since the art was added are fixed.** Both existing slides were reported as unused every single run; the checker could not see how they were loaded.

Full record: [the menu takes any number of slides](docs/implementation/MENU_SLIDESHOW_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.15-dev - 2026-09-29 - the universe has factions in it

- **Seven organisations now exist in the world.** A federal oversight office that wants your paperwork, competing interests that want your figures, former staff who know where everything is, an acquisition crew that will just take it, industrial intelligence you may never see arrive, concerned citizens who noticed the trucks, and an independent press that wants to publish all of it.
- **All seven start neutral.** None of them is an enemy until your branch makes one. Hostility is earned by what you actually do.
- **None of them changes your world map.** They have people and intentions, not towns, so generating a world is exactly as it was before. This matters when you are running 294 other mods.
- **Nothing new was added to the game to build them.** Every person they can send is one RimWorld already ships, and every icon is one the base game already uses.

Full record: [the universe has factions in it](docs/implementation/UNIVERSE_FACTIONS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.14-dev - 2026-09-29 - the queue could not answer the question

- **Nothing in the game changed.** The owner asked how close the mod was to finished, and the working queue could not say, because 178 of its 254 open rows had never been re-checked against the code.
- **155 rows re-measured.** 114 of them turned out to be built or deliberately superseded; 41 were rewritten to name exactly what exists and what does not. Open rows went from **254 to 107**.
- **Nothing was ticked off on a guess.** Every flip names the file, symbol, def or version that proves it, so anybody can re-check it instead of trusting it.
- **It found a real hole:** the seven universe factions the owner asked for are completely unbuilt, and so is mining and floor recovery inside the Backrooms, which a code comment had been claiming for months.

Full record: [the queue could not answer the question](docs/implementation/BACKLOG_AUDIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.13-dev - 2026-09-29 - arcs 5 to 8 have work in them

- **Thirteen more kinds of job**, one for every item the campaign plan names across the last four arcs: relay stations, caches, field shelters, guarded leases, resupply, evacuation, a town that saw something, residents who are missing, something loose where people live, cargo that does not fit through a door, people who know what they are looking at, a place that is two places at once, and one rule nobody has seen before.
- **Eighteen kinds of job in total** once you are past the tutorial, and the company works through the range of them rather than repeating the cheapest.
- **Every job offers the capability or the shortcut.** Do the work and own it, or pay to make the problem somebody else's. The company genuinely does not mind which, and would quietly rather you did the first.
- **Nothing new was added to the game to make this work** - no new items, no new art, no new sounds. It is written entirely out of things already there.

Full record: [arcs 5 to 8 have work in them](docs/implementation/ARCS_5_TO_8_REQUESTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.12-dev - 2026-09-29 - the company stops naming things

- **Work keeps coming after the tutorial.** Once you have answered the seventh request, clients start asking: a coordinate written up, material by the crate, instruments left running, somebody recovered, a door they can rely on. Five kinds of job, straight from the campaign plan's own list.
- **You are never offered a job you cannot do.** A request only appears if your branch has at least two genuinely different ways to finish it. What it then shows you is still every route, including ones you have not earned yet.
- **Progress on a generated job is counted from when it appeared.** "Deliver two hundred and fifty steel" means two hundred and fifty more, not "happen to have some in a stockpile".
- **Still no clock anywhere.** The next job turns up when you have finished or turned down the last one, and the company works through the range of what it wants rather than repeating the cheapest thing.
- **A job you already finished cannot be offered back to you as free money.** A request whose only route is research you have already completed is never put on the table.

Full record: [the company stops naming things](docs/implementation/REQUEST_GENERATION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.11-dev - 2026-09-29 - the corporation starts asking

- **The company now actually asks you for things.** Six requests in order, each teaching one part of the job, and then a seventh where it stops naming things and asks where you intend to take this.
- **Every request offers more than one way through**, and the card shows all of them - including the ones you cannot do yet, so you can see what to work toward. A tick appears beside the ones you have already done.
- **Nothing ever expires.** There is no date on any of it. The company waits as long as it takes, and you can turn any request down without penalty.
- **Two ways through that used to mean the same thing now mean different things.** Filing the analysed paperwork and having a crew member who was there and can speak to it are separate routes: one survives the witness dying, the other survives the book burning.
- **"Two crew accounts" now really means two people.** It was accepting one.
- **The bonus on bringing back your first record is paid when everybody you had on the books comes back.** It previously had no condition at all.

Honest note: all of this was authored two versions ago and **no part of the game ever showed it to you**. This is the version where it reaches the screen.

Full record: [the mission line reaches a player](docs/implementation/REQUEST_LINE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.10-dev - 2026-09-29 - the handoff, audited

- **Nothing in the game changed.** This is the session handoff, and writing it properly turned up four problems in the project's own checks.
- **Four of the mod's fifteen internal proofs had not been running.** They pass, but they were being skipped, so nobody knew.
- **The build fingerprint recorded in the handoff had been wrong for five versions.** It is now read from the build itself.
- **Two questions the owner had already answered were still listed as open.** Both closed with their answers.

Full record: [writing the handoff found four unrun proofs](docs/implementation/HANDOFF_AUDIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.9-dev - 2026-09-29 - the exit plan

- **You can build a gate at a site, not only at headquarters.** A second gate has stopped being theoretical.
- **A remote gate needs its own facility.** Its own comms console, its own bound battery and its own assembly bench, standing at that site. You cannot run a gate at the far end of the world off the equipment back home.
- **A way out of the Backrooms can already come up at a site too**, which came free from how ownership works rather than from a separate rule.
- **A Backrooms coordinate still cannot hold a company gate.** What is down there is a natural gate: no operator, no power, no address book, and not yours to build.
- **The refusal message stopped lying.** It used to say infrastructure had to be on the headquarters map, which is no longer true.

Full record: [the exit plan](docs/implementation/GATE_AT_A_SITE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.8-dev - 2026-09-29 - remote sites need people

- **A shipment to a site with nobody at it waits.** The supplier will not unload with no one to receive it. Nothing is lost - the cargo is held and the payment stands - and it lands as soon as somebody is there.
- **You can still order ahead.** Staffing is checked when the shipment arrives, not when you place it, so you can send supplies while the crew is still walking there.
- **The Sites pane tells you which sites are empty**, because that is the state quietly holding your deliveries.
- **Somebody unconscious on the floor does not count as staffing a site.** Neither do prisoners.
- **Closing a gate on your people does not take them away from you.** They stay yours, on a map that is never unloaded, and they have to survive until you reopen a connection. There is no time limit on getting them back, and an alert tells you they are waiting. This was already how the mod worked; it is now guaranteed against a future change breaking it.

Full record: [remote sites need people](docs/implementation/SITE_STAFFING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.7-dev - 2026-09-29 - shipments can go to your sites

- **The corporation will now deliver to a site you have put on the books**, not only to headquarters. Pick any stockpile at any place the branch holds.
- **Stockpiles say where they are** once you hold more than one place, so two stockpiles both called "Stockpile" are never confusable.
- **You can reroute a shipment in flight to a different place**, and it arrives there.
- **A bug was fixed that would have swallowed shipments.** Rerouting an order updated which stockpile it was bound for but not which map, so the moment deliveries to sites became possible a cross-map reroute would have left the shipment paid for, held, and never arriving.
- **A shipment bound for a place that is not loaded now says so honestly** instead of blaming headquarters.
- **The supplier will not unload anywhere you have not accepted responsibility for** - headquarters or a registered site, and never a Backrooms coordinate.

Full record: [company-to-site logistics](docs/implementation/SITE_DELIVERIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.6-dev - 2026-09-29 - a remote base is a costly responsibility

- **A new Sites pane.** Put a place your branch holds on the books, and it becomes the branch's responsibility - your people and supplies reach it, a gate can be built there, and a way out of the Backrooms can come up on it.
- **It costs every day, and you can see exactly how much.** A quarter of your branch's overhead per site, billed as its own line so you can decide whether a place is worth keeping.
- **The cost scales with your operation.** A site costs a research branch on fifty million rather more in absolute terms than it costs a furniture shop with two hundred silver in the till, and proportionally the same.
- **Taking a place off the books is free.** No fee and no notice. The colony there is still yours; it just stops being the branch's account.
- **A Backrooms coordinate can never be a site** - somewhere you go, not somewhere you keep.
- **Nothing here settles anything for you.** RimWorld already lets you found a second colony, and the mod's own portals already let a crew come out somewhere else. This is the paperwork, not the shovel.
- **A site you can no longer reach stops being billed**, and says so on its row rather than vanishing.

Full record: [a remote base is a costly responsibility](docs/implementation/REMOTE_SITES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.5-dev - 2026-09-29 - the queue was in the wrong order

- **Nothing in the game changed, on purpose.** This checkpoint is a correction to what gets built next, and shipping it is cheaper than building the wrong thing.
- **Four research projects were NOT written**, because the things they would have unlocked do not exist yet. The research band after the current one is about running remote sites, and remote sites are not built.
- **The build order now matches the design chart**, which said all along that the remaining research stops at the current band and the campaign arcs come next.

Full record: [the queue was in the wrong order](docs/implementation/BUILD_ORDER_CORRECTION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.4-dev - 2026-09-29 - four answers, and a research unlock that did nothing

- **A gate now needs real generators running before it will open**, not just a charged battery. You are told which is missing: the circuit cannot deliver enough, or there is no margin left above what the gate already draws.
- **A research unlock that changed nothing now works.** Reserve Discipline, the first Facilities project, promised the gate would need less spare power before opening. Nothing read that number. It does now.
- **The gate tells you how much of its reserve is held back for getting people home.** You used to see only the total.
- **A warning before you remove a natural way into the Backrooms.** Take it out and the access is gone; the space does not close and does not move, you just have no way back to it. Confirm and it goes; cancel and the order is dropped.
- **Machine gates you built get no such warning** - it is your machine, you can rebuild it.
- **The solo or group start has no mission list, on purpose.** Nobody is helping you because nobody knows you exist. Instead your people occasionally say what they are thinking - and none of it is an objective, nothing tracks whether you listened.
- **A designated gate still costs 250 W while closed.** Confirmed as intended rather than left as an open question.

Full record: [four answers, and a dead capability they uncovered](docs/implementation/FOUR_ANSWERS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.3-dev - 2026-09-29 - a portal is its own door cell

- **You can build, mine and explore right behind a gate without affecting it.** A portal takes up its own doorway and nothing else: no reserved space, no protected circle, no invisible claim on your map.
- **A real bug is fixed.** Walling one particular cell beside a gate used to break that gate permanently, silently, for the rest of the save - even with three other perfectly walkable cells around the same door. Build your airlock; the gate keeps working.
- **Seal a door in on all four sides and it stops working**, exactly like any other door you wall off. That much has always been fair.
- **A crossing in progress is never disturbed.** If somebody is mid-transfer the gate waits before adjusting anything, because losing a colonist in a doorway is not a risk worth taking.
- **The only placement rules near a gate are the equipment's own** - a console or a bound battery has to be within reach. That is the equipment needing to be close, not the gate claiming ground.

Full record: [a portal is its own door cell](docs/implementation/PORTAL_FOOTPRINT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.2-dev - 2026-09-29 - the way out was already there

- **The solo or group start now has a guaranteed way out, from the first tick.** A door on the surface, connected to the level you wake up in. Nobody built it and nobody knows who did.
- **You still start inside.** Your people and everything they were carrying are in the Backrooms before you see anything; the surface is a bare tile with one small concrete shell on it, and that shell is where you will come out.
- **Nothing is prepared for you up there.** No power, no furniture, no stockpile. Everything a facility needs, you build.
- **Using the way out is entirely your choice.** It is permanently open and it does not ask anything of you. A group that would rather stay down there and dig is playing correctly.

Full record: [the way out was already there](docs/implementation/SOLO_GROUP_EXIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.1-dev - 2026-09-29 - the free doors run out

- **Found doors stop leading deeper after the third level.** The Backrooms gives you the yellow rooms and two steps in, and then no more doors turn up. Past that, going deeper needs a gate you built.
- **Doors that lead OUT are never limited.** You can always find your way home from the deepest level the free doors reach. Being stuck down there with nothing to find would not be a challenge, it would be a bug.
- **A built gate is unaffected** and reaches anywhere it has earned, exactly as before. The limit is on the free doors, not on you.
- **When a door goes deeper than anything you can walk through, you are told so plainly** rather than quietly sent somewhere else.

Full record: [the free doors run out](docs/implementation/NATURAL_DEPTH_LIMIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.0-dev - 2026-09-29 - you are already in

- **The third start: solo or group, inside.** You begin in the Backrooms with what you were carrying. No gate, no company, no research, and nobody looking for you.
- **One to five people, your choice.** Groups have been known to end up in together. Set it up natively or with Prepare Carefully or Character Editor, the same as the other two starts.
- **The whole map is the Backrooms**, wall to wall. Solid rock between the rooms, and a roof that does not come off however far you dig.
- **There is no power and there are no lights.** Nobody wired the place. You have three glow pods and whatever else you brought.
- **No money, no wages, no overhead** - there is no company here to run an account.
- **All three starts are now in**, and only Async Industries begins in contact with the corporation. The other two have no clean-up team and no deliveries until they earn one.

Full record: [you are already in](docs/implementation/SOLO_GROUP_START_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.9-dev - 2026-09-29 - a shop with a door in the back

- **A second start: the Furniture and Knickknack Store.** Three ordinary people, a sales floor, a stockroom, two hundred silver in the till, and a door in the back room that should not be there.
- **No corporation, no research, and no rescue.** Nobody is watching this place. There is no clean-up team and no unsolicited delivery until you reach Async Industries, and reaching them at all is the achievement.
- **Async Industries now starts with the research an authorised branch would already have** - the first rung of the gate ladder and the entry project of all seven branches. It also means something can follow a crew out from the very first opening.
- **The threshold in the shop's back room is an ordinary door**, because that is what every gate in this mod is until somebody designates it. What it becomes is up to you.
- **Both starts stay fully editable** with native setup, Prepare Carefully or Character Editor.

Full record: [a shop with a door in the back](docs/implementation/STORE_START_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.8-dev - 2026-09-29 - the storyteller finally knows this mod exists

- **Your storyteller can now pace this mod's events.** Until now every one of them fired on the mod's own schedule, so Cassandra, Randy and Phoebe had never heard of it.
- **Threshold bleed** - the space occasionally comes out the near side. The lights in the room a gate stands in go out, or the room drops several degrees, or dirt appears that was not there. Only in the gate's room, and only if you have actually been through a gate.
- **Unsolicited delivery** - the parent corporation sends a crate nobody ordered. It is not kindness; it has money in you. Only once you are in contact with it.
- **Neither can hurt anybody, destroy anything or block a route**, and each has an answer you already know: flick the switch, wear a coat, sweep the floor.
- **There is no custom storyteller and there never will be.** You would have to give up the one you chose, and there is nothing in one worth taking.
- **The clean-up team is not one of these.** It is a promise, and a promise does not get rolled for.

Full record: [the storyteller finally knows this mod exists](docs/implementation/INCIDENT_SURFACE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.7-dev - 2026-09-29 - the corporation does not write off a branch

- **A clean-up team now arrives if your facility is wiped out.** Once you are in contact with the parent corporation, losing every last member of staff is no longer the end of the run.
- **They come in on all-access passes and clear the site of hostiles.** Removed, not killed - there is nobody left to haul forty corpses.
- **They bring a replacement crew of five**, one for each company role, and leave food, medicine, steel, components and wood. Enough to start again.
- **There is no limit on this and it never gets stingier.** The corporation is greedy, it is invested in you, and it will wait.
- **It will not fire while anybody is still alive** - including a crew that is standing inside the Backrooms when it happens. Staff who are merely unconscious are not replaced.
- **The Store and Solo/Group starts do not have this until they earn contact.** That absence is the point of those openings.
- **Five staff types that shipped with the mod but were used by nothing are now the replacement crew.** They were written for exactly this.

Full record: [the corporation does not write off a branch](docs/implementation/FACILITY_RELIEF_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.6-dev - 2026-09-29 - the second time you do a thing should be cheaper

- **Seven more research projects**, the third step in each branch. Each needs its own second project and a completed distortion log, because this band is about having been through often enough for something to have gone wrong.
- **Standby Discipline** - a designated gate costs half as much to keep while it is closed.
- **Relief Watch** - a gate ramp left unattended loses a quarter as much progress. It still lapses if nobody comes back.
- **Reference Standards** - calibrating a gate assembly takes two fifths less work.
- **Known Address** - every previous connection to an address makes the next one to it markedly faster. A first visit is exactly as slow as it ever was.
- **Containment Protocol** - nothing follows a crew out through a connection until the aperture is opened wider than Field Stability allows.
- **Forward Dispatch** - a shipment leaves in half the time, which is what finally lets your own relays move an arrival.
- **Specialist Recruitment** - you may ask for applicants again in half the time.
- **None of these replaces an earlier project.** Every one moves a setting no other project touches, so two cards never have to explain each other.
- **Three planned unlocks were dropped before they were built**, because checking them showed they would have changed a number nobody could ever notice - a one-second wait, a cap of a hundred orders, and a quantity limit already set to a million.

Full record: [the second time you do a thing should be cheaper](docs/implementation/RESEARCH_TIER2_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.5-dev - 2026-09-29 - a designated gate is a machine that is on

- **A designated gate now costs power to keep.** Not much, and only while it is closed - while a connection is open the opening draw is charged instead. Until now a finished gate sitting idle cost you exactly nothing.
- **It will never drain the reserve below what an emergency return needs.** A flat battery is a cost. A crew that cannot be recovered is a trap, and the gate stops short of it.
- **A gate now refuses a battery too small to come home on.** You are told when you choose the battery, rather than finding out at the threshold.
- **Three settings that did nothing now do what their names always said.** Two were removed one version ago as dead weight; that was wrong, and they are back and working.

Full record: [a designated gate is a machine that is on](docs/implementation/WIRED_UNUSED_PROPS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.4-dev - 2026-09-29 - the second rung of every branch

- **Seven more research projects**, one deeper step in each branch of the company's work. Each needs its own first project and one completed route log, so the band is about having been through once and read what came back.
- **Efficient Aperture** - holding a connection open costs about a seventh less power, and a wider gate saves proportionally more.
- **Rescue Training** - the emergency return window runs twice as long.
- **Corroboration** - analysing a record takes a quarter less work.
- **Alternate Exits** - fewer things are out of place when you return, because you are no longer relying on the one path that would have shown it.
- **Detection** - three times as long between recognising something and it reaching you.
- **Relays** - deliveries arrive about a quarter sooner.
- **Leases** - everything bought through the catalogue costs a fifth less.
- **Three of these replace their earlier version rather than adding to it**, so a deeper study is a bigger number and not a compounding one.
- **Two settings that did nothing have been removed.** They looked like they governed how fast the gate's reserve refills and how large it is. Neither was read by anything; the reserve is whichever battery you bind, and your colony's power charges it.

Full record: [the second rung of every branch](docs/implementation/RESEARCH_TIER1_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.3-dev - 2026-09-29 - seven ways into the tree, and every one of them does something

- **The research tree has seven new starting points**, one for each branch of the company's work, and you can take them in any order. None requires anything but insight, so a branch is never locked out by which record it happened to bring home first.
- **Reserve Discipline** - the gate needs less spare power above its draw before it will open.
- **Return Drill** - the emergency return window runs half again as long.
- **Second Reading** - every analysed record yields twice the insight.
- **Coordinate Atlas** - coming back to a coordinate finds it as you left it more often. The space has not stopped moving things; you have got better at knowing when it did.
- **Early Warning** - twice as long between recognising something and it reaching you.
- **Standing Orders** - twice as much cargo may be in flight at once.
- **Negotiated Terms** - everything bought through the company catalogue costs a tenth less.
- **Every one of those is real.** A check refuses to ship a project whose card promises an unlock that no code honours.

Full record: [seven ways into the tree](docs/implementation/RESEARCH_BRANCHES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.2-dev - 2026-09-29 - the company asks for six things, then stops asking

- **The tutorial line is in.** Power the gate, assemble and calibrate it, bring back one record, mark a route home, report a disagreement, hold a connection open - then the hinge, where the company stops naming things and the campaign opens up.
- **Each one teaches one system by being played**, in the order the systems depend on each other, and each requires the one before it.
- **Every request offers at least two genuinely different ways through.** Build the battery or re-purpose one you already have. Survey a coordinate yourself or recover a record somebody else left down there. Mark the junctions or let a crew who already walked it account for it.
- **The hinge has three answers and no wrong one.** Tell the company where you are taking this, say nothing and go do something and let the work speak, or push the gate itself further.
- **Nothing here expires.** The company waits for all of it, for as long as it takes.

Full record: [the company asks for six things](docs/implementation/TUTORIAL_LINE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.1-dev - 2026-09-29 - an offer with more than one way through

- **A corporation request now has to offer at least two ways to succeed**, of two genuinely different kinds. Two ways of delivering the same object to the same shelf is one route wearing two hats, and the game refuses to load a request that tries it.
- **A request has nowhere to put a deadline.** Not "we chose not to set one" - the shape has no field for it.
- **Routes you have earned are added on top.** If the company catalogue carries what a request wants, you can simply order it. If your crew has already been there and the log proves it, they can account for it instead of going again. Neither is available to a branch that has not built toward it.
- **A branch with nothing still sees two ways through**, because the written-in routes are counted before any of that is consulted.
- **Async Industries now starts in contact with the parent corporation**, with the basic gate research already done, and can take company work from the first minute. The other two starts will begin without contact and have to reach it.
- The first request of the tutorial line - power the gate - is in, as the worked proof that the shape holds.

Full record: [an offer with more than one way through](docs/implementation/REQUEST_SHAPE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.11.0-dev - 2026-09-29 - the only clock is the gate

- **Nothing in this mod has a deadline except the gate.** No mission, quest, offer, contract or trade ever expires. The company waits.
- **A job applicant used to withdraw after seven days.** It does not any more. Offers stay open until you accept or decline them.
- **A purchase quote used to expire after about ten hours.** It does not any more. A quote stays until you take it or cancel it.
- **The gate still has its window**, and that window is still what power, tech, maintenance and your operator decide - it was never a timer set against you, and it stays.
- Delivery still takes time, cooldowns still exist. A supplier being slow is not you being late.
- **The campaign chart is written**: the mission line, the research tree, the tutorial that turns into an open campaign, and the rule that every offer must have more than one way to succeed. No quest or request content is written until the chart says where it sits.

Full record: [the only clock is the gate](docs/implementation/CAMPAIGN_ABSOLUTES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.9-dev - 2026-09-29 - what you have learned is what you can build

- **A company project now needs completed logs, not just insight.** Route logs, distortion logs, entity logs. Insight is the price; the logs are the qualification, and unlike insight a completed log is never spent.
- **You are told which log you are short of before anything is charged**, and told what to do about it.
- **The ladder has four rungs instead of one.** Gate Telemetry, Field Stability, Sustained Aperture, Standing Connection. Each one needs the one below it.
- **A connection that never counts down was previously impossible.** The indefinite tier was set at four and only one rung existed, so the top of the gate's own capability ladder could not be reached however you played. It can now.
- **Sustained Aperture is the rung where what lives down there can follow a crew out** - and it requires an entity log, so nothing can come through before you have written down that something is there.
- **Evidence custody is a shelf now.** Link a shelf to a gate as its records archive, store a recovered book there, and it is in custody. The sealed evidence case is retired: it was an item whose only job was to exist somewhere on the map, and it did not care where the book actually went.
- Starts grant two shelves instead of a case. Dispatch no longer refuses a crew over one.

Full record: [what you have learned is what you can build](docs/implementation/LOG_GATED_LADDER_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.8-dev - 2026-09-29 - a gate's facility is the equipment linked into it

- **Link shelves, analysers, benches and tool cabinets to a gate**, the way furniture connects to a bed. Select the gate and you see lines to everything connected to it, drawn in the game's own colours - solid when a link is working, faded when it is not.
- **Three differences a large installation needs.** The links reach as far as the branch, they pass through walls, and nothing is ever connected automatically. You connect each one yourself.
- **Multiples, not one of each.** Up to eight shelves, six analysers or benches, six tool cabinets per gate.
- **Powered equipment must be on the gate's own power network.** Unpowered equipment - a shelf, a tool cabinet, a simple research bench - has no network to be on and can sit anywhere on the branch.
- **Equipment belongs to one gate at a time**, so several gates can share one building without quietly sharing each other's facilities.
- **A multi-analyzer linked to a gate still boosts a research bench** in the ordinary way. Nothing about vanilla facility linking changed, for you or for any other mod.
- The gate's inspect pane now lists each role, how many are linked, and how many of those are actually working.

Full record: [a gate's facility is the equipment linked into it](docs/implementation/GATE_EQUIPMENT_LINKS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.7-dev - 2026-09-29 - the survey tag becomes a glow pod

- **Route markers are glow pods now.** The custom survey tag is gone. You set down an ordinary Core glow pod and mark it, the same way you designate a door as a gate.
- **The colour is what it means.** Route home, cleared, danger, supply cache, unexplored lead - five markers, five colours, readable from the far end of a corridor without selecting anything.
- **No limit on how many.** Not per room, not per coordinate, not per map. The old tag allowed exactly one per room and made dispatch refuse a crew carrying fewer than six.
- **A marked pod stops ageing.** A plain glow pod dies after about twenty days. A way home that expires is not a way home, so marking one holds it. Unmark it and it starts ageing again.
- **A glow pod you find in the wild is untouched.** Same green light, same lifespan. It just gains a button.
- **A marked junction can now actually counter a corridor distortion.** That outcome existed in the code and could never happen: it tested for a return beacon, which was retired two versions ago, so the condition was permanently false.
- Dispatch no longer refuses a crew over survey tags, the deploy order and its job are gone, and the company catalogue sells glow pods by the crate.

Full record: [the survey tag becomes a glow pod](docs/implementation/GLOW_POD_MARKERS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.6-dev - 2026-09-29 - the documents use the mod's own words

- **The documents you read now call things what the game calls them.** The gate is the gate, the connection is the link it holds open, the threshold is where you arrive. The readme, the how-to, the design and scenario documents, the compatibility notes and the research notes were still using the words the game stopped using two versions ago.
- **Eleven walls of text broken up.** The readme opened with a 1,275-character paragraph; the design document had a 1,274-character one. They are lists and short paragraphs now, because that is what they always were underneath.
- **One of those walls was also out of date.** The readme's status paragraph still cited the 0.2.0 build record and sprites that were retired in 0.9.0-dev.
- **Two rules that were superseded and still written down as current.** The design and scenario documents both said gate and portal were one word, and both said nothing ever crosses a gate on its own - which stopped being true when pursuit and incursion were added.
- **Words quoted from somewhere else are never rewritten.** The A24 synopsis calls what appears in the basement a doorway; that is the synopsis's word and it stays, marked as a quotation.

Full record: [the documents use the mod's own words](docs/implementation/READER_FACING_DOCS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.5-dev - 2026-09-29 - every surface the game speaks through

- **New warnings in the alerts readout, down the right-hand edge.** Until now every warning this mod gave you was either a letter you can dismiss and lose, or a line in an inspect pane you had to already be looking at. RimWorld keeps the alerts readout for things that are still wrong *right now*, and the mod used it for nothing.
- **"Recovery overdue"** - the return window ran out and your people are still on the far side. Click it to jump to the gate.
- **"Return window closing"** - a connection failed while it was open and the window is still running. This is the one you can still act on.
- **"No gate operator"** - there is a finished gate and nobody assigned to run one, so no connection can be brought up at all. It stays quiet if any gate has an operator, so keeping a spare door designated does not nag you.
- **Right-click rows that were paragraphs are now rows.** "This gate has not connected anywhere yet." became "No connections yet", and four more like it. A right-click option is a thing you pick, not a sentence read to you - which is how the base game writes them, measured rather than assumed.
- The one that was carrying an instruction now says only the condition, and the instruction moved to the button's own tooltip where there is room for it.

Full record: [every surface the game speaks through](docs/implementation/DISPLAY_SURFACE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.4-dev - 2026-09-29 - the register checked backwards, and a description you can read

- **A drafted animal could walk through a gate while a drafted colonist could not.** Fixed. A pawn under direct combat control does not wander off through a gate, whatever it is.
- That was only reachable if you run **Draftable Animals**, which vanilla cannot do - so it was found by checking the mod register against work already shipped, not by re-reading the code.
- Two other systems were checked against the profile and needed no change: what chases you works the same with or without **Search and Destroy**, and a coordinate still cannot be stripped of its roof with a roof-removal mod installed.

- **The mod description was one unbroken paragraph of 6,724 characters.** It is now four titled sections and half the length, which fixes how it reads in RimWorld's own mod panel too.
- Both welcome letters and the scenario description were walls as well. All reflowed.
- Readable HTML versions of the description, readme, changelog and working docs are generated into `outputs/readable/`.

Full record: [the register, checked backwards](docs/implementation/REGISTER_RETRO_AUDIT.md) and [a description you can read](docs/implementation/READABLE_TEXT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.3-dev - 2026-09-29 - something is not where you left it

- **Go back to a space you have been to before and something is sometimes not where you left it.** A bench, a lamp, a shelf - in the same room, a few cells away.
- **Nothing tells you.** No letter, no alert. If you never notice, you have lost nothing. If you do notice, you found it yourself.
- **Not every time.** Roughly a third of returns are exactly as you left them, so you can never be sure whether the room changed or you misremembered.
- Never anything you built, never the way out, and never anything that could block a door.
- A first visit never changes, because there is nothing yet to remember.

Full record: [something is not where you left it](docs/implementation/REVISIT_DISPLACEMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.2-dev - 2026-09-29 - one set of words

- **Everything the mod shows you now uses one set of words.** The **gate** is the machine in your wall. The **connection** is the live link it holds open. The **threshold** is the doorway you arrive at on the far side.
- That means the game can finally tell you *which* part failed. "The gate is fine, the connection dropped" is a sentence it could not say before.
- The biggest offender was **"machine gate"**, the name of an object retired two versions ago and still used in twenty-five places the game spoke to you.
- Eighty-four lines of screen text, tooltips, job reports and item cards brought into line.

Full record: [one set of words](docs/implementation/VOCABULARY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.1-dev - 2026-09-29 - LAW #0, made checkable

- Internal only; nothing in the game changes.
- The owner asked whether their instructions were always being written down properly. **They were not.** Ten of them had been acted on and archived without ever being written into the working queue.
- All ten are now recorded word for word, and a check refuses from here on to let an instruction reach the archive without appearing in the queue first.

Full record: [LAW #0, made checkable](docs/implementation/VERBATIM_QUEUE_RULE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.10.0-dev - 2026-09-29 - the documents say what is true

- **The readme said this was version 0.4.1-dev.** It is 0.10.0-dev. That and twenty-seven other stale claims across ten documents are corrected.
- The publishing procedure named a branch that has not been the working branch for the whole of this development run.
- Documents no longer describe retired objects as things you can build, or point at a deferral list that was closed.
- A sixth check now refuses to ship documentation that describes a mod this is not. **Dated records are deliberately exempt**: an old build record saying "all four checkers pass" was true when it was written, and rewriting history would be worse than leaving it.

Full record: [the documents say what is true](docs/implementation/DOC_CONFORMANCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.9-dev - 2026-09-29 - the beacon had nothing left to do

- **The return beacon is gone.** Your gate remembers every address it has dialled and the way back is saved with the space itself, so carrying a beacon to find your own door stopped being a job some time ago.
- Nothing was lost with it. Finding your way home is done by the gate's own address book and the saved return threshold, both of which are better at it than an item you could drop.
- Survey tags are untouched and still mark your route.

Full record: [the field kit, part one](docs/implementation/FIELD_KIT_RETIREMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.8-dev - 2026-09-29 - one tech tree, different starting points

- **Every start uses the same company research tree.** A scenario chooses only which projects it begins with already finished, never what the tree contains.
- Adding a research project in future reaches every scenario at once, instead of needing each one updated by hand.
- No change to the Async Industries start: it still begins with gate telemetry available and unresearched.

Full record: [one tech tree, different starting points](docs/implementation/STARTING_RESEARCH_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.7-dev - 2026-09-29 - some places are bigger than a room

- **Runs of two to four connected rooms are now furnished as one thing.** You find a laboratory wing rather than a room with a bench in it, a dormitory block rather than a stray bed.
- **Deeper in they are still wrong in all the usual ways**, which is worse than a jumble rather than tidier: there is finally something recognisable for the wrongness to happen to.
- Quiet rooms are never part of one, so a coordinate still has its empty stretches. The room you arrive in is never part of one either.
- The shallow yellow rooms are untouched and stay sparse.

Full record: [some places are bigger than a room](docs/implementation/FACILITIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.6-dev - 2026-09-29 - it came through with them

- **Something can follow your crew home.** In the worst coordinates, with an advanced gate and a connection actually open, a thing that reaches the doorway behind your people steps through it into the facility.
- **Once it is inside it is an ordinary hostile**, and does everything a hostile in your base does.
- **Only one per opening.** Closing the connection and opening it again is what resets that, which makes the emergency cutoff a decision rather than a formality.
- **Only if it fits through the gate.** A narrow gate is genuinely safer, so the small one is a defensive choice and not just the one you started with.
- **Never from a quiet space, and never on an unresearched machine.** A new branch with a fresh gate is not a way in.
- Closing the connection before it reaches the doorway stops it completely.

Full record: [it came through with them](docs/implementation/GATE_INCURSION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.5-dev - 2026-09-29 - they follow you

- **In the worst coordinates, what lives there no longer holds its ground.** It follows your crew, room after room, all the way to the doorway you came in by.
- **Everywhere quieter it still gives you a warning and lets you back away.** That has not changed, and it is what makes the deep ones mean something.
- Nothing kidnaps anyone or carries anything off the map. What follows you follows you; it does not disappear with one of your people.
- The limits that keep a lone survivor alive are untouched: never more than three things acting at once, quiet rooms still guaranteed, and nothing ever waiting in the room you arrive in.

Full record: [they follow you](docs/implementation/PURSUIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.4-dev - 2026-09-29 - what a gate's size lets through

- **Your animals can walk through a gate.** They could not before at all, which meant gate size had nothing to stop.
- **How big a creature fits depends on how wide the gate is.** A one-cell doorway passes people, dogs and deer. A two-cell doorway passes pack animals - muffalo, dromedaries, donkeys. Three cells or more passes anything, up to and including a thrumbo.
- **A gate has one width in both directions**, so an animal that walked in can always walk back out again.
- **Nothing from the other side gained anything.** A Backrooms creature still cannot cross under any circumstances; the rule that changed is about what is *yours*.
- Cross-gate **work** is still colonists only. An animal crosses because you told it to, never because a job was scheduled for it.

Full record: [what a gate's size lets through](docs/implementation/GATE_FIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.3-dev - 2026-09-29 - everything you can look at says what it is

- **The facilities overview now explains each kind of room** - what it is for, and what goes wrong for a branch without it.
- **The procurement list now says what each thing is actually for**, not just what it costs and how long it takes to arrive.
- Sixteen descriptions written for things that previously showed you a bare name.
- Where the game itself does not describe something, neither do we. A work giver, a pawn kind, a trader and a category get a name and no more, because **that is exactly what RimWorld does** - it was counted rather than guessed.

Full record: [everything you can look at says what it is](docs/implementation/INFO_CARDS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.2-dev - 2026-09-29 - a gate has a size

- **A gate can be wider than one cell.** An ordinary door gives you a one-wide gate; **the game's own ornate door gives you a two-wide one with no other mods at all**, and so does Anomaly's security door.
- If you run **Doors Expanded**, its double and triple doors and its big blast door work as gates too, giving you three-wide and two-by-three. If you do not run it, nothing changes and nothing is touched.
- **A wider gate is more machine.** It draws more power while open and takes longer to bring up, in proportion to its whole footprint, so a big gate is something you work toward and plan power for.
- **A wide gate never limits how many people cross at once.** It simply has a wider opening, and your colonists spread across it the way they do at any wide door.
- **A gate cannot be resized while it is working** - not while it is open, and not while it is being brought up.
- The gate now tells you its size when you select it.

Full record: [a gate has a size](docs/implementation/GATE_FOOTPRINT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.1-dev - 2026-09-29 - one kind of gate

- Internal cleanup with **no change to anything you can see or do**. Now that the custom gate machine is gone, there is only one kind of gate, and the code no longer carries a second one alongside it.
- The gate's leftover private power reserve is gone with it. A gate has always run off the battery you bind to it; the unused second system underneath is simply removed.
- One hundred and twelve lines lighter, and seven pieces of dead on-screen text pruned.

Full record: [one kind of gate](docs/implementation/NATIVE_PROVIDER_COLLAPSE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.9.0-dev - 2026-09-29 - a gate is a door and nothing else

- **The custom gate machine, control console, cutoff switch and generator are gone.** A gate is an ordinary door you designate, its controls are an ordinary comms console and machining table, and its power comes off your own grid like everything else.
- The unused site lamp, climate unit, analysis bench and floor carpet went with them. **Four of those had no code behind them at all** and had been shipping artwork nobody could see.
- The gate's control station no longer guesses which gate belongs to it. You choose, and only your choice counts.
- Nothing you can do in the game was removed. Every one of these had already been replaced by an ordinary object you designate.

Full record: [a gate is a door and nothing else](docs/implementation/LEGACY_GATE_RETIREMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.9-dev - 2026-09-29 - bringing a gate up is work, and a gate looks like one

- **Opening a connection is no longer a button.** The assigned operator brings the gate up at the console over time, and the console shows the progress while they do it.
- **The operator matters.** A skilled technician brings a gate up quickly; a poor one takes a long while. It is their own working speed that decides it.
- **Leave it unattended and it loses charge.** The gate only climbs while somebody is on the console with the power on and the cutoff off. Left alone it slips back and eventually lapses, and the address stays remembered so you can start again.
- **Losing charge is always slower than gaining it**, whoever is operating, so walking away costs you time but never wipes out a long spin-up.
- **A route you have run before comes up faster.** Every previous connection to the same address shortens the next one, down to a floor. Somewhere nobody has been takes the full spin-up, and no route is ever instant.
- **Dial straight from a gate's history** to connect to somewhere it has been and start bringing it up, in one action.
- If the spin-up finishes while the battery is still too low, the gate **waits fully charged and opens itself** the moment there is enough power.
- **A gate you have designated is a blue door with a blue glow around it**, so you can tell one from an ordinary door at a glance. It glows brighter while a connection is live, and amber when something has gone wrong. If you painted that door yourself, your colour is kept.
- A natural portal still has no history, cannot be dialled, and looks like the ordinary doorway it is.

Full record: [bringing a gate up is work](docs/implementation/GATE_SPIN_UP_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.8-dev - 2026-09-29 - a gate remembers where it has been

- **Every laboratory gate keeps its own list of everywhere it has connected to.**
- **Two gates keep two different lists.** A gate at home and a gate at an outpost are running different operations.
- **Rename an address to something you can actually navigate by.** Clear the name again to get the original back.
- **Pin the ones that matter.** Pinned addresses survive a clear and are never dropped to make room.
- Remove one entry, or clear the noise in one go.
- Connecting somewhere you have been before updates that entry instead of adding another.
- **A natural portal has no list at all.** Its destination is fixed where you found it and it cannot be dialled.

Full record: [gate connection history](docs/implementation/GATE_CONNECTION_HISTORY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.7-dev - 2026-09-29 - the deeper it is, the less it pretends

- **Hallways can hold anything.** A production bench in a corridor is not a mistake down there.
- **Shallow spaces still make sense.** Deep ones stop bothering, and the change is gradual rather than a switch.
- **Some rooms in a deep space still read as ordinary**, on purpose. If everything is wrong, nothing is unsettling.
- **The strange kinds of room get commoner the further in you go**, until the ordinary ones are the surprise.
- **What you find scales with what you have researched and how deep you have pushed.** A young colony finds crude things; an advanced one starts turning up spacer equipment.
- **A deep space is worth going back to.** The same coordinate after a hundred hours of research is a different place.

Full record: [coherence and tech scaling](docs/implementation/COHERENCE_AND_TECH_SCALING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.6-dev - 2026-09-29 - the shape of the place

- **Deep spaces are not built to a grid any more.** Rooms stretch, shrink and go wrong, and they go wronger the further in you are.
- **Some of them are shaped like rooms you built.** The place took their proportions when it opened - not what you have built since.
- **Lots of hallways.** Long narrow corridors that are corridors on purpose, not by accident.
- **The shallow yellow rooms stay regular.** That monotony is the look, and it is left alone. The wrongness is something you travel toward.
- Spaces you already found are completely unchanged, down to the last cell.
- Building an extension at home does not reshape a space you have already opened.

Full record: [room shape echoes](docs/implementation/ROOM_SHAPE_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.5-dev - 2026-09-29 - the place copies your people

- **Somebody you know can be standing in a deep space**, wearing your colonist's name and the clothes they put on this morning.
- **That colonist is at home right now.** That is the whole point of it.
- It is not them. It has their name and their coat and nothing else - not their skills, not their history, not their mind.
- **It is never hostile**, and you cannot recruit it. It is not a person you can save.
- Your actual colonist is untouched and keeps their own clothes.
- If everyone is down there with you, or hurt, or gone, no echo appears at all.
- **Nothing you have not found yet can die of neglect.** People and bodies in rooms you have not reached are held exactly as they were - nobody starves, freezes or rots behind a door you have not opened.
- **Finding them is what starts their clock.** Once you have seen a room, everything in it lives and suffers normally.

Full record: [colonist echoes](docs/implementation/COLONIST_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.4-dev - 2026-09-29 - things that happen

- **Things happen in the Backrooms now**, not just things being there. A noise with nothing making it. Every light switching itself off. Cold with no source. The place getting filthier. Loose things not where you left them.
- **Everything that happens has an answer you can actually perform.** The lights come back on with the same switch you already use. Cold is answered by clothing or a heater or leaving. Filth is answered by cleaning, which already works through a gate.
- **Nothing that happens can trap you.** No event hurts anyone, destroys anything, or blocks a route, and the room you arrive in is never touched.
- **Nothing that moves is ever lost** - it is somewhere else in the same space. Your money is never moved at all.
- At most two things happen per visit, and a space does not replay the same trick every time you go back.
- **Deep spaces now also contain things you have owned**, not just things you have built.

Full record: [anomaly events](docs/implementation/ANOMALY_EVENTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.3-dev - 2026-09-29 - getting somebody out, and earning what comes against you

- **You can offer a survivor passage home.** They accept - there is no negotiation and no recruitment roll. Somebody lost down there who meets a team with a way out wants to leave.
- **Joining is what lets them walk out.** Until they accept they are an inhabitant, and an inhabitant cannot use a gate at all - the only way out for them is to be carried, like anything else you find.
- One of your people has to actually be standing there to make the offer.
- **The Backrooms now starts by sending one thing at a time**, not three.
- **It only sends more once you have gone deeper than you ever have**, and when that happens it is written into your branch history so you can see the moment the rules changed.
- Stay shallow and it stays at one, however rich or advanced you get.
- It never goes past three.

Full record: [survivors and cap progression](docs/implementation/SURVIVORS_AND_CAP_PROGRESSION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.2-dev - 2026-09-29 - who you find down there

- **There are people in the Backrooms now.** Wanderers who do not explain themselves, survivors who will leave with you, people who went missing, and ones who have been down there far too long.
- **A missing person may be somebody you lost.** The Backrooms remembers people it keeps, and gives you the name back.
- **Bodies are there from the first visit**, carrying what they came in with. Older ones have been picked over.
- **Living things are not there on your first visit.** They arrive as a space gets worse, and a space only gets worse from what you did there.
- **Never more than three hostiles at once**, at any depth, at any wealth.
- **You get told before you meet one.** Hostiles hold their ground rather than hunting you, so backing out is always a real option.
- Nothing you find down there will follow you through a gate on its own.
- Nobody is ever standing between you and the way back.

Full record: [inhabitants](docs/implementation/INHABITANTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.1-dev - 2026-09-29 - the place starts copying you

- **Push far enough into the Backrooms and the rooms start containing things you built.** Your benches, your beds, your machines - arranged by something that has clearly seen them.
- It counts what you build anywhere: in the colony, or inside a coordinate.
- **It does not copy its own furniture**, so deep spaces do not slowly all turn into the same room.
- **It only copies some of it.** The rest of the room stays strange, which is the whole point.
- Only spaces three or more portals in do this. The first couple still feel like somewhere that existed before you did.
- It forgets. Stop building something and it eventually stops appearing down there.
- A brand-new colony that has built almost nothing still gets fully furnished deep rooms.

Full record: [the construction echo](docs/implementation/CONSTRUCTION_ECHO_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.8.0-dev - 2026-09-29 - the Backrooms paces against what you have built

- **How dangerous a space becomes is now paced against your colony's wealth**, the same measure the game's own storyteller uses.
- **A space only gets worse from things you actually did** - how often you went in, and how long you stayed. Never from the clock, never from a reroll when you reload, never from simply having a gate open.
- **Going back to a space you know resumes where it was.** It does not get worse for revisiting, and it does not get safer either.
- **Walking in is never the dangerous part.** A first visit is always quiet, however rich you are and however deep the space.
- **Half of every space is quiet, always.** Not by luck - by count. You will never open a coordinate with something in every room.
- **No more than three things can ever act at once**, at any depth, at any wealth. That is a hard number, not a curve.
- Several open gates never add up into one bigger threat.
- Shallow spaces stay survivable no matter how rich you get.

Nothing acts yet - this is the pacing the inhabitants will be held to.

Full record: [the escalation ladder](docs/implementation/ESCALATION_LADDER_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.9-dev - 2026-09-29 - rooms that are a kind of place

- **Deeper coordinates now contain recognisable rooms** - laboratories, workshops, dormitories, canteens, storerooms, offices, wards, machine halls, nurseries and salvage caches.
- **Further in, some of them are wrong.** A gallery. A room you have already been in, laid out exactly the same. An assembly of things that belong in different rooms. A hoard.
- **Two rooms of the same kind are not the same room**, and the same room is the same every time you go back to it.
- **The shallow yellow rooms stay empty.** That emptiness is the look, and nothing will be put in them.
- The room you arrive in is never dressed, so the way back is never buried.
- **Furniture comes from whatever you have installed.** A mod that adds a workbench puts it in Backrooms workshops without either mod knowing about the other.

Full record: [room archetypes](docs/implementation/ROOM_ARCHETYPES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.8-dev - 2026-09-29 - the yellow rooms

- **The first Backrooms space now looks like the Backrooms.** Yellow carpet, yellow wood walls, and lights on the walls instead of lamps standing in the middle of the floor.
- **The first one always looks like that**, on every seed. It is the image the whole thing rests on.
- **Deeper spaces do not.** Coordinates now know how far in they are, and the look changes with depth: poolrooms, machinery, abandoned offices, cold storage, and one band where the place stops agreeing with itself.
- The same deep space looks the same every time you go back to it.
- Spaces in an existing save read as shallow, so nothing you have already found changes.

Full record: [the palette](docs/implementation/BACKROOMS_PALETTE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.7-dev - 2026-09-29 - the company will buy, and pay you in paper

- **Sell to the company at a credit beacon.** Everything tradeable in the beacon's range goes at once, and you see the total before you commit.
- **Odd goods fetch half again over market**, because nobody else can get them. Ordinary valuables go slightly under, because the company is instant and a trader is not.
- **Traders are still the better price for ordinary goods if you can wait for one.** That is on purpose.
- Your gold and silver finally have somewhere to go that is not a passing caravan.
- **Company bonds in range are never sold** - banking one is a different thing, and selling your own money by accident is not a feature.
- **Withdraw credits as paper at the gate console.** Pick a denomination off the ladder, get one bond of that size.

Full record: [the exchange](docs/implementation/VALUABLES_EXCHANGE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.6-dev - 2026-09-29 - the corporation will sell you things, eventually

- **The parent corporation is now a trader you can call in** from the gate console. It arrives in orbit like any other trade ship, and trading works exactly as it always does, beacon and all.
- **Its catalogue is tiered, and each tier has three locks**: research you have to finish, company work you have to have completed, and an access fee in credits.
- **That access fee is what your bonds are for.** A vault of paper now buys capability, not just goods.
- **A locked tier sells nothing and buys nothing** - it will not quietly take your goods off you for a catalogue you have not opened.
- **A locked tier tells you which lock is holding it**, rather than just refusing.
- The first tier is open from the start, because a supplier who sells you nothing until you have already made it is not a supplier.
- Each tier sells whatever the loaded game puts in its category, so mods that add materials show up in the catalogue without this mod knowing they exist.

Full record: [corporate supply](docs/implementation/CORPORATE_SUPPLY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.5-dev - 2026-09-29 - company bonds, from ten credits to a quadrillion

- **Company credits can now be held as physical bearer bonds.** Print them at a machining table, haul them, stack them in a vault, hand them around.
- **Fifteen denominations**, every power of ten from 10 credits up to a quadrillion. Ten of any size is worth one of the next size up.
- **You are always paid in the fewest, largest bonds.** Withdraw a trillion and you get one piece of paper, not a warehouse.
- **A trade beacon can be designated as a credit beacon.** It shows the face value of every bond in its range, and banks them into the company account on command.
- **Banking a bond destroys it.** No spent certificate left lying around.
- **Bonds are physical, and that means physical.** They burn. They can be carried off. That is the price of holding your money where you can reach it, and it is why the company account still exists.
- Silver, gold, jade and ivory are untouched. Your vault works exactly as it always did.

Full record: [company bonds](docs/implementation/COMPANY_BONDS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.4-dev - 2026-09-29 - the place gets into people, and everything from it is marked

- **Everything that comes out of a coordinate is odd now, not just what was lying there.** Rock you mined from its walls, material from a partition you pulled down, plants you cut in its rooms - all of it.
- **Things you carry in stay ordinary, permanently.** Haul your own cotton down there and back and it is still your own cotton.
- **Being in the Backrooms wears on people.** Minus one the moment they step through, sliding toward minus ten over about an hour of real time down there.
- **It follows them home.** The feeling fades after they leave rather than switching off at the door, so rotating shifts works and living down there does not.
- **You can build against it.** A lit, properly enclosed room made of material you hauled in slows it right down. Fixtures you found in place do nothing - it has to be real material from outside.
- Nothing you build makes the place ordinary. The first point never goes away.

Full record: [origin and pressure](docs/implementation/BACKROOMS_PRESSURE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.3-dev - 2026-09-29 - somebody wants the odd goods

- **Buyers now turn up wanting goods recovered from the Backrooms**, and they will not take the ordinary equivalent. Your own cotton is no substitute for cotton that came out of a coordinate.
- **They only ask for things a space you have actually opened really held.** No contract will ever send you looking for something that was never down there.
- **They pay well over the ordinary rate** - these are goods nobody else can source.
- Up to three demands stand open at a time, and a new one arrives about once a day.
- Delivery is automatic once the goods are home: the contract settles and pays, and it pays once even if you reload in the middle of it.
- Uninstalled buildings count. Haul a machine home from down there and it is still the thing the buyer wanted.

Full record: [odd supply contracts](docs/implementation/ODD_SUPPLY_CONTRACTS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.2-dev - 2026-09-29 - what comes out of the Backrooms is marked

- **Anything you carry out of a Backrooms coordinate is marked odd.** A stove you found down there, a stack of cotton off a shelf, a door you uninstalled: it comes home labelled `(odd)`.
- **Odd goods never stack with ordinary ones.** Odd cotton and your own cotton sit in the same stockpile as two separate stacks, and neither one absorbs the other. Split an odd stack and both halves stay odd.
- **Uninstalled buildings keep the mark.** Uninstalling a machine you found and hauling it home does not launder it back into an ordinary one.
- **Bringing your own goods in does not make them odd.** Only what was already down there counts.

Nothing asks for odd goods yet. This is the marker the contracts will be written against.

Full record: [odd origin](docs/implementation/ODD_ORIGIN_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.1-dev - 2026-09-29 - the gate assembly needs looking after

- **A gate now holds a condition that slowly wears down**, and somebody has to recondition it before it runs out. A gate with nothing left will not open until it is seen to.
- **How fast it wears depends on how you keep the room.** A clean, sterile gate chamber wears at half rate; a filthy one wears at triple. Look after the place and the gate mostly looks after itself.
- **An unpowered assembly degrades eight times faster**, so cutting the power has a cost beyond closing the gate.
- Holding a connection open wears it faster too.
- **Nobody is sent to it until it actually needs it.** Above a quarter condition the job is not offered at all, so your people are not forever fiddling with the gate. Reconditioning restores it fully in one visit.
- Running out **never slams a gate shut on people who are already through**. It stops the next opening; it does not end one in progress.

Existing gates load in full condition, so nothing you already built is suddenly out of service.

Full record: [gate servicing](docs/implementation/GATE_SERVICING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.7.0-dev - 2026-09-29 - a cutoff you can throw

- **A gate can now be given an emergency cutoff**: a power switch on its own circuit that somebody can throw to shut an open gate at once.
- **The switch has to actually carry the gate's power.** One that is not wired into the line feeding the gate cannot be chosen at all, and says why. No believing in a cutoff that would not work.
- Throwing it ends the opening immediately and says so plainly — *the cutoff was thrown*, not *the power failed*. Those were the same message before, and they are not the same event.
- **Anyone still on the other side keeps their emergency return window.** That window is the whole reason the gate holds its own power reserve, and one flick should not strand people for good.
- Throwing a switch is ordinary work, so you can order somebody at home to do it while a team is still inside. That is what it is for.
- Gates without a cutoff work exactly as before. Nothing needs rebuilding or rebinding.

Worth knowing: cutting a gate's power already closed it. What was missing was the gate knowing *which* switch was its own, checking that the switch really powers it, and telling you apart a deliberate shutdown from a broken wire.

Full record: [the kill switch](docs/implementation/GATE_KILL_SWITCH_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.9-dev - 2026-09-29 - a way out, and it comes up where you said

- **A doorway in the Backrooms can now lead back out into the world**, instead of only ever leading deeper. Roughly one in three ways onward does, once you have somewhere for it to come up.
- **You choose where it comes up.** Any door on a map you hold can be marked as a way home, with one command on the door itself. Nothing is ever marked for you — a way out only ever arrives at a door you picked.
- A door inside the Backrooms cannot be marked, because a way out cannot come up in the place it leads away from.
- With nothing marked, doorways simply lead deeper as before. Nothing is refused and nothing is lost.
- The same doorway always leads to the same place. Saving, reloading and revisiting never change it.
- Unmarking a door stops new ways out coming up there, and deliberately leaves any that already exists alone.

Two unrelated fixes found while working: one message on the gate was sharing a name with another, so one of the two was always wrong — the operator-away refusal and the operator readout now have separate names. And there is now a check that no two messages can share a name again.

Full record: [a way out](docs/implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.8-dev - 2026-09-29 - zones work on both sides of a gate

- **A growing zone inside the Backrooms no longer traps the person you sent to it.** Backrooms floors are concrete, and nothing can be planted in concrete — but somebody was being sent to sow there anyway, and once they arrived the game correctly refused while the mod still believed there was work, so they stood there doing nothing and never came back. Nobody is sent now unless the ground can actually take the crop.
- Everything else about zones on both sides of a gate was checked rather than assumed. Stockpiles on the far side pull goods across and honour their own filters and priority. Fishing zones, home areas and per-colonist allowed areas all read the far side's own settings.
- Zones you paint in a Backrooms space survive leaving and coming back, along with their settings.

One honest note on what "continuous" can mean: the game does not allow a single zone to cover two maps, so two zones either side of a gate stay two zones. They already behave as one in the way that matters — put something in one and a hauler will move it to the other when that is a better home for it.

Full record: [zones and areas across a gate](docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.7-dev - 2026-09-29 - every kind of work in the game now crosses a gate

- **Containers on the other side get tended.** A fermenting barrel that wants wort or has beer ready, an egg box with eggs in it, and a pack animal you marked to unload will all now pull somebody across a gate.
- Nobody crosses for a barrel with no wort on that side, or one sitting at a temperature that would ruin it.
- **Somebody will cross a gate to flick a switch, open a container, or eject fuel** — but only where you marked it. Nothing is guessed.
- **With the Odyssey expansion, somebody will cross to fish** a zone you painted on the other side. Water you never zoned attracts nobody.
- All of it is tunable while the game runs, like the rest.

That closes the last of the gaps found when every kind of work in the game was listed out and checked. Every one is now either handled or deliberately left alone with the reason written down.

Full record: [the last work type gaps](docs/implementation/WORK_TYPE_GAPS_CLOSED_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.6-dev - 2026-09-29 - study what you contain, through a gate

- **A researcher now crosses a gate to study a contained entity on the other side.** A containment facility reached through a portal is the whole idea of this mod, and until now nobody would walk to one.
- An empty holding platform attracts nobody. Neither does an entity still on its study cooldown, or one whose study you switched off.
- The game's own study work does the studying once your researcher is standing there, exactly as it does at home.
- This needs the Anomaly expansion. Without it the work simply does not exist, rather than misbehaving.

**A load error fixed, present since 0.6.4-dev.** The two cross-gate childcare work entries referred to a work type that only the Biotech expansion adds, with nothing marking them as needing it. On a copy of the game without Biotech that produced an error at startup — in a mod that is supposed to need nothing but the base game. Both are now marked correctly, and a new check reads the game's own data to make sure no future entry can slip through the same way.

Full record: [dark study](docs/implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.5-dev - 2026-09-29 - somebody actually runs the bill on the other side

- **A bench on the other side of a gate now gets worked.** Until now ingredients were carried through to a bill and then nobody came to make anything, so a workshop in the Backrooms just accumulated material. A cook, crafter, smith, tailor or sculptor will now cross a gate to run the bill itself.
- **The game's own crafting does the work, exactly as it does at home.** Nothing about recipes, quality, skill gain or part-finished items is reimplemented here — your colonist walks over and the game takes it from there.
- **A bill you restricted to one person still only pulls that person**, and a bill with a skill minimum only pulls somebody who meets it. Neither ever drags the wrong colonist through a gate.
- **Nobody crosses for a bench that has no materials.** A workshop over there with nothing to work with attracts nobody, rather than sending someone on a pointless walk over and over.
- **Nobody crosses for a bench that has simply run out of fuel** either — fuel gets carried to it instead, which already worked.
- Local work always wins. Somebody only crosses when there is nothing of that kind to do on this side at all, and somebody already on their way is never turned around.
- All of it is tunable while the game runs, like the rest.

One fix to something already shipped: bills belonging to the automatic production and mech systems were being supplied with ingredients even though the mod's own notes said they were left alone. They are now genuinely left alone until they get a proper look.

Full record: [bill work](docs/implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## Repository tooling - 2026-09-29 - the 294-mod register actually opens now

**No change to the mod itself.** The mod build is byte-for-byte identical to 0.6.4-dev and the version was deliberately not bumped. This entry covers the project's own research register, which lives beside the mod rather than inside it.

- **The register now opens.** The spreadsheet never could on this machine: there is no spreadsheet program installed and Windows has no idea what a `.xlsx` is, so it was being handed to an unrelated application. There is now an **HTML register beside it** that opens straight in a browser with no install and no internet — same four views, plus a search box that filters all 294 mods across every column as you type, and dropdowns for how each mod is treated and whether that decision is settled yet.
- The 294-mod integration register workbook also had four real faults, now fixed for anyone who does have a spreadsheet program. Every text cell in it claimed to be a formula result when nothing in the file was a formula; all 294 rows were pinned to a fixed height that the spreadsheet was then forbidden to expand, so five columns — including every evidence field — were cut off on screen; its summary page counted 45 categories where the rows hold 66, with eleven wrong numbers; and there was no way to rebuild it, while six columns of work existed in that one file and nowhere else.
- Both versions are now four views instead of two: a summary, an **index** that fits on one screen with a link to each mod, the **full grid** for filtering, and a **card per mod** where no field is ever cut off.
- The counts on the summary page are now worked out from the rows each time it is built, so they cannot quietly go stale again.
- It can be rebuilt from plain text files that live in the repository, and a second tool reads every cell back out and checks it against them.
- A broken link in the task list that had been failing the project's own audit was found and fixed along the way.

Full record: [the register rebuild](docs/implementation/MOD_REGISTER_REBUILD.md) and [the work type coverage audit](docs/research/WORK_TYPE_COVERAGE_AUDIT.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.4-dev - 2026-09-29 - the Backrooms has no sky, and the last three kinds of work

- **A Backrooms space now has no outside anywhere in it.** Every cell of it sits under thick mountain rock, and the space between its rooms is solid stone rather than open ground. Previously most of a generated space was open to the sky, which was wrong.
- **That ceiling can never be opened.** Marking a no-roof area inside the Backrooms does nothing, and if anything else removes a piece of roof it is put straight back. There is no way to make a hole in the world from the inside.
- **You can still take the place apart completely.** Walls and doors deconstruct, the stone is mineable in several materials, and floors can be lifted. Mine a whole space out if you like — the ceiling collapses into rubble the way a mountain does, and it still never leaves a gap.
- **Your own colony is untouched by all of this.** Building roof, removing mountain roof and building mountain wall all work exactly as they always did anywhere outside the Backrooms.
- Wardens now cross a gate to prisoners held on the other side, and food already reaches them, so the two work together without anything extra.
- Carers cross to a baby on the far side, where the expansion that adds babies is present.
- Animal handlers cross for animals you marked for slaughter, taming or release — but not merely because an animal over there could be sheared some day.

One thing named rather than assumed: lifting a floor does not return materials in the base game, so carpet and tile being reused or sold is its own piece of work still to come.

Full record: [containment and care](docs/implementation/CONTAINMENT_AND_CARE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.3-dev - 2026-09-29 - a way onward can turn up out in the world

- Doorways that lead somewhere else can now be found out in the ordinary world, not only deep in the Backrooms. Much rarer out there, and at most one per map, because it should be a notable thing rather than a fixture.
- **A door your own people built is never one of them.** A way onward is found in something that was already standing there, so installing this mod never quietly turns part of your base into a permanent hole in the world.
- A doorway that already has a gate machine on it is left alone too.
- The same doorway always leads to the same place. Reloading or revisiting never rerolls it, and every space already found in an older save still leads exactly where it did.

Two things worth knowing about what was already true, because they did not need building: a portal found inside a space reached by a portal already works to any depth, and a way onward has always led to a genuinely new place with its own seed rather than linking two you already knew. What is still to come is a portal that opens out onto the ordinary world rather than into another Backrooms space; the groundwork for it is named in the register.

Full record: [continuous topology](docs/implementation/CONTINUOUS_TOPOLOGY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.2-dev - 2026-09-29 - eight more kinds of work cross a gate

- Cleaning, repair and firefighting now happen across a gate — but only inside a Home area you set on that side. A Backrooms corridor nobody called home attracts nobody, exactly as it already did for the game's own colonists.
- Mining, hunting, cutting plants and working a growing zone all cross a gate too, and every one of them only where **you** marked it wanted. Nothing is guessed: no designation, no zone, nobody goes.
- Fuel and shells are carried through a gate to anything of yours that has run dry — a generator, a smithy, a mortar, an autocannon. Each takes whatever it actually accepts, so a modded machine with its own odd fuel is handled without anything special.
- A machine you told not to auto-refuel is left alone, and nothing crosses if fuel it can use is already sitting on that side.
- A colonist will not cross toward a fire if the route to the gate breaks the danger rules you set. A fire on the other side does not override what you allowed.
- A local emergency, and local work of the same kind, always come first for every one of these.
- All of it is tunable while the game runs, like the rest.

Full record: [eight more families](docs/implementation/CONNECTED_WORK_FAMILIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.1-dev - 2026-09-29 - a casualty gets a bed where they lie

- Somebody will now cross a gate to put a downed colonist into a bed on that side, instead of carrying them all the way home first. Taking an injured person through a gate is one more trip for somebody who cannot walk, so if there is a bed over there, the help goes to them.
- If there is no bed on that side, nothing changes: they are carried home to one, exactly as before.
- Babies are never picked up this way, and a prisoner bed is never used for one of your own people.
- A casualty at home still comes first, and a rescuer already on their way to a gate is not turned around by one somebody else can reach.

Two things deliberately **not** added. A tired colonist will not walk through a gate to go to bed, and this one is not a judgement call: the game itself refuses to let anyone use a bed that is not on the same map they are, so the walk could never have worked even if it were safe. The same goes for owning or being assigned a bed on the other side of a gate. What does work is building beds over there, and that already works through the existing cross-gate construction: material is carried to the site and a builder crosses to finish it.

Full record: [rest and beds](docs/implementation/CONNECTED_REST_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.6.0-dev - 2026-09-29 - food crosses a gate, and nobody starves for want of a delivery

- Food is now carried through a gate to your people on the other side when there is nothing there they will eat. Ordinary hauling only ever moves things to better storage, so without this a colonist could starve beside an empty larder while the pantry at home was full.
- The last food never leaves a side that still has hungry people of its own. Moving starvation from one side of a gate to the other is not work.
- Only your own people and your guests are fed. A hungry animal or hostile on the far side attracts nothing.
- What anybody will actually eat stays entirely the game's decision, so ideology restrictions, royal titles, teetotalling and race diets are all respected without this mod having an opinion.
- Someone will also cross a gate to feed a patient who cannot feed themselves, but only once there is food on that side to feed them with. Sending a carer to an empty larder helps nobody.
- Treatment still beats meals: a patient who needs a doctor outranks a patient who needs feeding, and an urgent local patient outranks both.
- Food that arrives after the hunger has passed is simply put away rather than treated as a wasted trip, because food keeps.

One thing deliberately **not** added, and worth saying plainly: a hungry colonist will not walk through a gate to go and eat. Hunger is handled by the game at a level this mod does not reach into, and more importantly a gate can close while somebody is still on the far side. Sending a starving person on that walk risks stranding them with no food and no way back, which is worse than being hungry at home. Food goes to people instead. Full record: [food across a gate](docs/implementation/CONNECTED_FOOD_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.9-dev - 2026-09-28 - a doctor crosses a gate, and so does the medicine

- A doctor will now walk through a gate to treat a patient lying in a bed on the other side, instead of the patient being carried home first. Somebody already settled in a bed is better off treated where they are.
- Medicine is carried through a gate to a patient whose own side has none. The treating is the game's own; all this does is make sure there is something to treat them with.
- Medicine never decides whether somebody gets treated, only how well. The game treats patients with or without it, so a delivery that arrives late costs nothing.
- Your medical care settings are respected exactly. A patient set to no medicine has none carried for them, a patient set to herbal or worse never has glitterworld medicine hauled across a gate, and the amount carried is the amount the game says will heal them.
- Nothing crosses if the patient already has enough medicine they are allowed to use nearby, counting every kind they allow rather than just one.
- A local emergency always wins. A doctor only partway to a gate turns back for an urgent patient at home, and a doctor only ever crosses when there is no doctoring left to do on this side at all.
- An injured colonist wandering around does not pull a doctor through a gate; only somebody actually in a bed does.
- Works alongside your medical mods with nothing special needed for any of them, including the one that lets doctors carry medicine in their own inventory.

Surgery, patient feeding and prisoner or guest care are each a separate piece of work and are named as such rather than quietly assumed. Full record: [tending across a gate](docs/implementation/CONNECTED_TENDING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.8-dev - 2026-09-28 - a researcher crosses a gate to work

- A researcher will now walk through a gate to use a research bench on the other side, when there is nothing to research on this side.
- The research itself is the game's own, on that side, at its normal speed. Nothing about how research works is changed or replaced.
- A researcher partway to a gate is not turned around by a bench freeing up at home, and nobody is ever dragged back. When the far bench stops being usable, or there is no project left to research, the colonist is simply free where it stands.
- A bench that is unpowered, or missing a facility it needs, is not treated as somewhere worth walking to.
- This works alongside your research mods without needing anything special for any of them. Because the mod only decides that the walk is worth it and then gets out of the way, whatever handles research on that side does the work — including mods that pick projects for you, reprioritise them, redraw the tree, or run a completely separate research system of their own.
- How eagerly researchers cross a gate is a setting like the rest, adjustable while the game runs.

Full record: [research across a gate](docs/implementation/CONNECTED_RESEARCH_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.7-dev - 2026-09-28 - ingredients reach a bill through a gate

- A workbench whose bill is short of leather can now be supplied from the other side of a gate. A colonist picks up the real leather, carries it through, and puts it where the bill can reach it.
- The crafting itself is untouched. Your colonist on that side finds the ingredients and runs the recipe with the game's own bill work, exactly as if the leather had always been there.
- Deliveries land inside the bill's own ingredient radius, measured the same way the game measures it. So if you have deliberately kept a bill's radius small, the goods arrive near that bench rather than in some far-off stockpile.
- Nothing crosses a gate if the ingredient is already within reach of the bench. A recipe that will accept two different materials also will not trigger a trip when one of them is already plentiful there.
- Half-finished work is never picked up or carried. The game binds a part-made item to the one colonist who started it, so nobody else can finish it; carrying one anywhere would strand it.
- The bill a delivery is for is remembered properly, so reordering your bill list mid-delivery does not redirect the goods to a different bill.
- Medical, mechanitor and autonomous bills are not supplied yet, and each is named as its own future piece of work rather than quietly skipped.

- The loaded mod version no longer has a long build identifier stuck on the end of it internally, which also means a given release of the mod now builds to a byte-identical file every time.

Full record: [bill ingredients](docs/implementation/CONNECTED_BILLS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.6-dev - 2026-09-28 - tune how eagerly colonists cross a gate, while the game runs

- You can now set how eagerly colonists cross a gate to work, for all four kinds of cross-gate errand, in the mod settings. Changes take effect the moment you close the window: no restart, no reload.
- Starting a trip is always kept below finishing one, and the settings screen tells you when it has done that. Otherwise a colonist standing on the far side holding something could be sent on a fresh errand instead of finishing the delivery.
- The shipped numbers stay the shipped numbers. Only values you actually change are saved, and there is a reset button.
- Checked the whole package against RimWorld and Steam requirements and wrote the position down with the evidence behind it: no game or expansion file is included, nothing of the base game is overwritten or deleted, no expansion is required, no third-party mod is required, and the mod targets official RimWorld and official expansions only. Those checks now run automatically on every build, so the position cannot quietly rot.
- Nothing in this project is waiting on anybody. Every item that can only be confirmed by playing is now marked as belonging to the single test pass that happens once the mod is finished, and none of them holds up any work.

Full record: [tunable priorities and the test phase](docs/implementation/TUNABLE_PRIORITIES_AND_TEST_PHASE.md) and the [compliance position](docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.5-dev - 2026-09-28 - a builder crosses a gate to finish the job

- A frame on the other side of a gate that already has all its material can now be finished. A builder walks through and builds it. Nothing is carried, because nothing needs carrying — this is the other half of last build's material delivery.
- The building itself is entirely the game's own. Your colonist finishes the frame with the game's normal construction job, its normal reservation and its normal speed. All this mod does is decide that walking over there is worth it.
- A builder will not cross a gate while there is any construction work left on this side — not even smoothing a wall. Local work always comes first.
- A builder already on the way is not turned around by a frame that appears at home while it walks, so it does not get stuck oscillating at a doorway.
- Nobody is ever dragged home. When the work over there runs out, the colonist is simply free where it stands, with its own needs and whatever local work it finds, exactly like anyone else who walked through a gate.
- A colonist can only ever owe one cross-gate errand at a time. It cannot be promised a haul and a building job at once and then abandon one of them.
- Respects your work assignments as always: a colonist with construction switched off is never sent, and nothing here is ever a forced order.
- Operations lists people working across a gate separately from people carrying things across one, because reading the first as hauling would be misleading.

Also captured this build: the campaign opens in the 1990s, and the world's factions are the universe's own — the US government, rival corporations after proprietary technology, disgruntled ex-employees, high-tech thieves, corporate espionage and sabotage, and concerned citizens — default-set per scenario and tailored to each. They begin neutral and earn their hostility from what your company actually does. That layer is authored after the remaining cross-gate work families. Source and compiler evidence: [travel-to-work record](docs/implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.4-dev - 2026-09-28 - a gate you can actually work through, and a company you name

- A laboratory gate's first opening now lasts about thirty real minutes instead of about fourteen real seconds. The old value could not support a single round trip, which would have made every cross-gate work family unusable on a laboratory gate. Each research advance multiplies the duration, and at the top of the ladder a supported opening has no countdown at all.
- "No countdown" still means "while supported". Power, the operator on station and the energy supply are all checked every tick exactly as before, so running the supply dry ends the opening the same way cutting power does. A sustained draw needs real sustained generation behind it, not just batteries.
- Duration advances on *completed* research, never on spendable insight. Gating it on the currency would have meant spending research to advance shrank your gate.
- Natural gates are untouched and still permanently open, with no timer, operator, power or close command of any kind. Confirmed in the source rather than assumed.
- Every scenario researches the same tree and can build a full company, so nothing about duration or research is tied to which start you chose.
- You name your own company. A field at setup on every start, the name shown throughout Operations, and renaming any time through the game's own rename dialog. The old fixed identity survives only as a suggested default.

Two questions open since the earliest planning are now answered: the inside start has a configurable party, and its first exit lets the player choose the destination settlement rather than revealing a fixed one. Note one honest gap: only one company project exists so far, so the top of the duration ladder cannot be reached until the research tree lands. Source and compiler evidence: [gate duration and naming record](docs/implementation/GATE_DURATION_AND_COMPANY_NAMING.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.3-dev - 2026-09-28 - material reaches a build site through a gate, and the dependency position is audited

- A half-built structure stalled for want of steel can now be supplied from the other side of a gate. A colonist picks up the real material, carries it through, and puts it into the build site. Blueprints work as well as part-built frames, because the game's own delivery step turns a blueprint into a frame on the first material that arrives.
- Nothing about building is reimplemented. The site's own material requirement, the frame's own resource store and the work of building all stay the game's; only the carrying is ours.
- Audited what this mod actually requires and confirmed it needs nothing but the base game. Every game definition it uses was traced to base Core: no DLC, no Harmony, no other mod. The mod description now says so precisely instead of just claiming it.
- Fixed four places where a missing definition would have thrown an error at you instead of quietly reporting the action as unavailable. A definition can go missing because of another mod or a load-order clash, and that should never be a crash. There are now none of those left.
- Confirmed two compatibility claims are real rather than intended: stack-size mods are respected automatically because no stack size is ever hardcoded, and modded doors work as gate thresholds because doors are recognised by what they are rather than by name.
- Corrected a recorded blocker that was simply wrong: the gate's power draw was said to exceed every single generator in the game, while the same sentence named one that exceeds it. A draw is supplied by a power network in any case.

Recorded the method behind the above as binding: decide what to build a feature on by the capability it needs, never by a name. Because this mod adds behaviour to existing game objects rather than inventing objects, every piece of custom gear still awaiting replacement now has an existing-content answer, which unblocks that work on content grounds. See the [dependency and capability record](docs/implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md) and the [construction record](docs/implementation/CONNECTED_CONSTRUCTION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.2-dev - 2026-09-28 - our own people and our dead come home

- A colonist who goes down on the far side of a gate can now be fetched. Another of our people crosses, picks them up, carries them back and puts them in a bed. If no bed is free on arrival they are set down on this side and ordinary rescue takes over from there, because being home is what the trip was for.
- Our dead come back too, to a grave or to storage. This needed no new machinery: the game already treats carrying a corpse as ordinary hauling, and a grave is reached the same way any other container is.
- Fixed a real gap that would have made that silently not work: the planner only looked for open floor space, and a grave is not floor space. A corpse whose only home was a grave would never have been planned for, and the container delivery route added last build would have sat unreachable for exactly the case it was built for.
- Capture stays a player order, not automatic work, which is both how the game does it and what the gate rule says: people and monstrosities come back because you directed it.

This is the casualties-and-remains work family, built ahead of construction because carrying people back through an opening is something the gate rule names explicitly and no route reached it at all. Tending someone across a gate is a different capability and is not implemented. Source and compiler evidence: [casualties record](docs/implementation/CONNECTED_CASUALTIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.1-dev - 2026-09-28 - nine deferments closed, and doorways that lead onward

- Doorways deeper in can now be found. One of our own people walks up to a doorway in the Backrooms, studies it, and records that it leads somewhere else: a permanently open way through to a further space. A doorway's answer comes from its own position under that space's saved seed, so it is always the same answer and revisiting never rerolls it. At most two ways onward per space, so a chain of spaces stays finite.
- Storage containers are now valid delivery destinations for cross-gate hauling, not just open stockpile cells. This follows the game's own rule for which destinations take which route, which is also what makes the storage-framework mods work here without special handling for each one.
- A worker no longer plans a trip whose arrival its allowed area forbids. The game offers no way to ask about a zone on a map a pawn is not standing on, so instead we write down what we saw while we were standing there, and an unseen map is treated as unrestricted exactly as the game itself treats it. A destination that turns someone away is left alone for a while afterwards.
- Finished crossing records are now bounded. Automatic hauling made these an everyday event rather than a rare order, so they would otherwise have grown in the save forever. Unresolved records are never touched, because those hold real people and real cargo.
- Fixed four pieces of missing text that would have shown the player a raw internal name, including the Procurement tab label.
- Internal: one implementation each for branch map ownership and for choosing a threshold's approach cell, instead of two and three.

Nine deferred items closed, seven of which turned out to be blocked on nothing and three of which had already shipped and were still listed as outstanding. The deferment register now carries the four audit questions that caught them, so it gets checked rather than only added to. Source and compiler evidence: [audit and closures record](docs/implementation/DEFERMENT_AUDIT_AND_CLOSURES.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.0-dev - 2026-09-28 - colonists work across a gate

- Added cross-gate work as ordinary work. A colonist can now haul an actual object from the map that holds it, carry it through a gate in real hands under native mass and stack limits, and put it into storage the other side's own settings accept. Both directions. No dispatch, no crew list, no cargo manifest.
- Added the saved work intent that makes a trip survive its job boundaries, a save and a reload: it remembers the worker, the one real object, the destination, and the gate the plan was made against. The next physical step is always worked out from the worker's actual current position, so an interruption or an unexpected location resolves by itself.
- Added the planning lease, which stops two of our own planners promising the same stack and does nothing else. It is not a reservation, it excludes nobody, and it expires.
- Work reaches people through ordinary work priorities, within-type order, schedules, disabled work types and required capacities, because it is an ordinary work giver rather than something that pushes errands. Hunger, sleep, danger, drafting and mental states keep winning. Nothing is ever marked as a forced player order.
- Nothing is counted, cloned, teleported or consumed at a distance. The object that arrives is the object that left, or the honest split of a stack that a partial pickup produced. A delivery that merges into an existing stack is a finished delivery, not a lost item.
- Added a list of the work trips currently crossing a gate, because saved state that moves people and goods must never be invisible.

Storage hauling is the first of the work families and the only one in this version. Construction, bills, research, medical care, food and rest are specified with named owner steps in the [deferment register](docs/DEFERRED.md) and are not claimed here. Also recorded permanently in the [pinned Core API reference](docs/implementation/CONNECTED_WORK_CORE_API.md): RimWorld 1.6 does ship its own map-portal system, and it cannot serve this design, because its hauling does nothing without a player-filled loading manifest and its crossing drops carried cargo on arrival. Source and compiler evidence: [connected-work record](docs/implementation/CONNECTED_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.4.3-dev — 2026-09-28 — inhabitants stay in the Backrooms

- Added the rule that people and monstrosities on the far side do not cross a gate. Nothing but this company's own people walks through, an open gate is never an objective, lure, spawn target, raid route or attack trigger, and no setting, research or upgrade changes that.
- Everything else comes back because one of our own people carried it: materials, tools, equipment, resources, minified furniture and production benches, corpses, and people or monstrosities that are genuinely downed, dead or held prisoner. Anyone still on their own feet cannot be taken through.
- One chokepoint enforces it for every gate at once, so no future work adapter, scheduler, generator or threat can reintroduce the behaviour by accident.
- Added player-facing text for each refusal.

Gate, machine door and portal mean the same thing; every start can eventually run several gates, and nothing assumes one gate per branch, map or coordinate. The gradual-escalation half of the same rule — how much pressure a space presents and how it grows — is specified but not yet implemented; it is owned by the procedural-inhabitants work in the [deferment register](docs/DEFERRED.md). Source and compiler evidence: [connected-travel record](docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md). No gameplay result is claimed.

## 0.4.2-dev — 2026-09-28 — remembered portal addresses and ordinary crossing

- Added explicit portal addresses: a designated native gate can remember a laboratory connection to a saved coordinate, and any actual doorway can hold a permanently open natural connection. Addresses are derived from the branch, coordinate and threshold object, so remembering the same address twice changes nothing.
- Added an explicit repair for sites generated before their return threshold was an actual door. It replaces that one object with a Core door under a saved receipt and keeps the site's map, room graph, construction, recovered items and discoveries.
- Added a deterministic record for newly discovered coordinates so an address can never invent a coordinate identity or seed. Visited coordinates are never removed to make room.
- Added ordinary crossing: order one colonist and they walk to the saved threshold and cross carrying what they already carry. No crew list, manifest or dispatch. Opening a doorway normally still moves nobody.
- Added laboratory session controls, a reconcile action for every unresolved crossing, and an emergency-return route that pays the physical recovery cost once and teleports nobody.
- Added player-facing text for every portal address, travel and crossing result.

Source and compiler evidence is in the [connected-travel record](docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md). Cross-map work, materials, hauling, bills, research and needs are not implemented by this version; they remain the next steps in the [deferment register](docs/DEFERRED.md). No gameplay, save-migration or compatibility result is claimed.

## 0.3.0-dev — 2026-09-28 — company operations and content reuse

- Added voluntary native-pawn applicants, inspection, hiring, recovery, staff role assignments and payroll registration. Offers retain the original pawn through interrupted arrivals; unavailable offers have an explicit safe dismissal route.
- Added quoted procurement of existing Core goods, saved physical cargo, ledger-backed payment/refund records, receiving stockpiles, partial deliveries, redirection and bounded history.
- Added an HQ Facilities pane for actual buildings, rooms, power, bed ownership and staff care needs, with native inspection and assignment routes.
- Moved company laboratory work to an explicitly designated native research bench. New field evidence uses a real Core TextBook, with saved creation/custody records and retry of the same original object.
- Replaced the four custom gameplay audio files with references to existing Core sounds. Preserved old files outside the loadable package as historical evidence.
- Added two original painted Backrooms menu images, a quiet slideshow, reduced-motion/disable settings and the exact mod title/current build version beside native top-left version information.
- Recorded the owner's existing-content-only rule throughout the build documents and mapped the remaining older custom content for replacement.

This is an implementation checkpoint toward the full mod TODO. The [company build record](docs/implementation/PHASE_3_BUILD_RECORD.md) owns compiler/package evidence and limitations. Custom gameplay content from 0.2.0 still awaits replacement; gameplay, balance, save migration, optional integrations and release acceptance remain open.

## 0.2.0 — 2026-09-28 — first-expedition development slice

- Added the Async Industries facility start, five staff, physical supplies and one-time branch funding.
- Added the USD ledger, wages/overhead, arrears, initial survey contract, case/evidence records and company projects.
- Added physical machine assembly, staffed calibration/operation, power reserve, warnings and recovery openings.
- Added a saved finite first destination, real inventory/crew transfer, recall, relief/casualty recovery, abandonment history and auditable cargo declarations.
- Added deployable numbered tags/beacon, corridor mismatch, bounded Quiet Pursuer, physical evidence analysis, once-only settlement and insight-gated Gate Telemetry.
- Added actionable Operations panes, next objectives and original equipment/encounter sprites with provenance and source masters.
- Added bounded layout candidates/fallback, furnished room families, fog-preserving native doors, observed clues, physical salvage, original carpet and native wall paint.
- Added frozen evidence reports, explicit AI-01 resurvey preparation, persistent gate warnings and development identity/performance logging.
- Added four original quiet audio cues with native game/master volume, independent gate/field mute and a mod volume control.

The [build record](docs/implementation/PHASE_2_BUILD_RECORD.md) records exact implementation, source and evidence boundaries. Gate 2, runtime/presentation acceptance, full campaign systems, optional integrations, co-op and release remain in progress. This is a private development checkpoint.

## 0.1.0 — 2026-09-28 — private foundation

- Added the Core-referenced C# library, logging entry point and inactive save-local campaign component with explicit schema version.
- Added the localized Operations main tab, with foundation status and guarded links to native Work and Research tabs.
- Added exact mod identity, original package preview and the separate copyable 1.6 package.
- Added pinned build references, locked dependency restore, package manifests and scoped RimSort Local Mods staging with backups.
- Added contributor/build/migration guidance, production asset specifications and implementation evidence linked to the existing design contracts.

The company scenario, economy, machine gate, expeditions, generation, analysis, threats, main-menu slideshow and optional integrations are not implemented in this version. Compilation and package/staging evidence do not establish in-game behavior or profile compatibility. No public release or save-support promise is made.

## Preparation — 2026-09-28

Gate 0 documentation/source preparation completed, including owner decisions, 294-mod source review, design contracts, feature traceability, source registers and future acceptance plans. See the [closure audit](docs/research/GATE_0_COMPLETION_AUDIT.md).
