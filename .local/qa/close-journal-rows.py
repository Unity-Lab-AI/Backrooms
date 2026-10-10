# -*- coding: utf-8 -*-
"""Close the three journal rows this batch finished: the brief, the naming fix, the click actions."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Write the journal and quest brief BEFORE any code.**",
     " -- **WRITTEN 0.12.99-dev: `docs/JOURNAL_AND_QUEST_BRIEF.md`, fourteen sections, and the two "
     "remaining forks were put to the owner before a line of it was designed.** "
     "Owner's answers: **beacon radius pickup** for how a finished book goes back, and **" + Q
     + "Both, and they must agree" + Q + "** for what the green light reads from. "
     "**The return route costs nothing new.** It reuses the contract `ValuablesExchange` already "
     "has and Core's trade beacon established -- *what is in the circle is what is on the table* -- "
     "and the facility now ships **eight beacons** where the owner placed them, so the delivery "
     "surface was already on the map. A courier was declined because arrival timing would be the "
     "company's rather than the player's, and a gate dispatch was declined because paperwork would "
     "then compete with expeditions for the one genuinely scarce resource. "
     "**AND THE GREEN-LIGHT ANSWER WAS THE ONE WITH A RISK, WHICH WAS STATED WHEN IT WAS OFFERED "
     "AND HAS NOW BEEN SPENT DOWN RATHER THAN ACCEPTED.** *" + Q + "Both" + Q + "* means two things "
     "holding one truth, and *" + Q + "two derivations of one rule is the defect this project keeps "
     "meeting" + Q + "*. So the brief specifies **one writer and two readers**: the write-up job "
     "advances the record and stamps the book in a single operation, record first. The record is the "
     "authority, the book is a receipt, and the light reads the record while requiring the book. "
     "**A mismatch therefore cannot be produced by the mod working normally** -- only by a foreign "
     "book, a hand-edited save or damage, each of which the player should be told about. That is "
     "what the third state is for: **amber, unverified**, where the record is complete and no "
     "agreeing book exists. Burn the book and you have lost a deliverable, not a month of work. "
     "**Four write-up kinds are the owner's own list** -- lab notes, research write-up, "
     "investigation, analysis -- and the ellipsis in *" + Q + "what ever the task requires" + Q
     + "* is read as the list being open, so a kind is **declared on the request in XML** rather "
     "than inferred from a quest's name. "
     "**Nothing in the brief needs a new system.** `RecordBookDelivery` already drops books "
     "deterministically, `EvidenceSettlement` already defines custody as the book being on a "
     "gate-linked archive shelf through Core's `StoringThing()`, `ContractRecord` already carries "
     "`requiredSurveyedRooms` for the survey quest exploration will post, and `PostTransaction` is "
     "already idempotent by operation id so a collection cannot pay twice. "
     "**The records desk is the one new buildable and it is recorded as the second approved "
     "exception to `CONTENT_REUSE_POLICY.md`, with the art rule still binding:** Core's own "
     "`Things/Building/Furniture/Table1x2`, verified present in Core's `Buildings_Furniture.xml`. "
     "*" + Q + "The breach was the ART, not the defs" + Q + "* is why that distinction is kept. "
     "**And desks are deliberately uncapped while consoles are capped at four.** A gate's window is "
     "a scarce shared resource and the owner gave it a number; a work station is neither, and "
     "RimWorld has never capped one. "
     "**Register checked before designing:** `use RR-MSN` 23 rows, `trace RR-EVD` 31, `find book` "
     "**zero**. Three applied. [100] Go Explore! says *" + Q + "Do not make it the Backrooms "
     "coordinate, room, or mission generator" + Q + "*, which binds survey completion to **our own "
     "authored room records**. [10] Adaptive Storage Framework says *" + Q + "keep vanilla "
     "stockpiles useful when ASF is absent" + Q + "* -- already satisfied, because custody is "
     "tested through `StoringThing()` and never against a shelf's def name, so a modded shelf "
     "counts and a vanilla one still works. [132] More Faction Interaction says to keep the company "
     "ledger distinct from vanilla silver, which it is."),

    ("**The starting journals are named wrong and describe the wrong subject.**",
     " -- **BUILT 0.12.99-dev, AND THE CAUSE WAS NOT WHAT IT LOOKED LIKE: THE COMPANY LABEL HAD "
     "EXISTED FOR VERSIONS AND WAS NEVER ONCE CALLED.** "
     "`CompRouteEvidence.TransformLabel` has returned `RR_Evidence_CompanyBookLabel` for a "
     "company-issued book since the owner answered *" + Q + "Mark the company-issued ones" + Q
     + "*. **`ThingWithComps.LabelNoCount` is where the comp label chain runs, and `Verse.Book` "
     "overrides it, `LabelNoParenthesis` and `DescriptionFlavor` without ever calling base.** So on "
     "a book no comp can change the label and no comp can reach the description at all. The feature "
     "read as built in every file a reader would open, which is why thirteen launches went past it. "
     "**And the wrong subjects are generated rather than authored.** `Book.GenerateBook` resolves "
     "the title through `GrammarResolver` with `BookComp.Props.nameMaker`, and `AppendDoerRules` "
     "feeds it a topic for every `BookOutcomeDoer` on the def. Core's `TextBook` carries skill "
     "doers, so **" + Q + "nutrition" + Q + " is Cooking and " + Q + "aiming" + Q + " is Shooting "
     "wearing their topic words**. Nothing was mis-authored and nothing was broken: repurposing an "
     "existing item kept its identity as well as its model, the same lesson as the comms console "
     "coming back facing north. "
     "**The fix is `RimroomsRecordBook : Book`, which restores the chains rather than hard-coding "
     "our own string** -- it asks every comp in order exactly as `ThingWithComps` would, so another "
     "mod's comp on a book starts working too and an ordinary novel is untouched. The label is "
     "built from the **transformed name plus `GenLabel.LabelExtras`**, because transforming the "
     "finished string would have thrown the quality suffix away: a second defect shipped while "
     "fixing the first, and a plant was written for exactly it. "
     "**THE BINDING IS IN CODE BECAUSE `check-compliance` RULE 3 REFUSED THE PATCH, AND THE RULE "
     "WAS RIGHT.** Core declares `thingClass` on the **abstract** `BookBase`, so no xpath reaches "
     "TextBook's own element and the only operation that works is a `PatchOperationReplace` -- "
     "which takes ownership of a def where the last mod to load wins. Patching the parent instead "
     "would have handed our class to `Novel`, `Schematic` and `Tome`. So it binds at "
     "`StaticConstructorOnStartup`, the same argument `FixtureTellService` already makes: it reads "
     "the value actually in play, after inheritance and after every mod. **And it can decline** -- "
     "if another mod owns the field it stands down and logs why, because two mods silently fighting "
     "over a single-valued field is worse than one visibly standing down. "
     "**THE OWNER ASKED ABOUT PURCHASED ONES IN THE SAME SENTENCE, AND THAT TURNED UP TWO MORE "
     "GAPS.** Marking was audited on all four routes that mint a book and **two were not marking**: "
     "the corporation's own drop, which is the route a player meets second and the one that "
     "unblocks somebody who lost the first book; and `RR_ProcurementCatalog.xml`, which sells "
     "`TextBook` -- so the catalogue was the *" + Q + "generating ones purchased too" + Q + "* half "
     "of that sentence all along. A book **found in a coordinate** stays unmarked deliberately, "
     "because it is somebody else's, and checker 27 asserts it stays that way. "
     "**WHAT IT CANNOT FIX, MEASURED BEFORE IT WAS DESIGNED RATHER THAN DISCOVERED AFTER.** "
     "`ScribeExtractor.SaveableFromNode` instantiates the `Class` attribute written into the save, "
     "so **a book already in a live save keeps `Verse.Book`** however the def now reads. The fix "
     "covers every book made from this version on. **The remedy needs no migration and already "
     "exists:** `RecordBookDelivery` sends two correct books whenever a branch holds none anywhere, "
     "so destroying a wrong pair returns a right one. Rebuilding a book in place was **rejected** -- "
     "`CompRouteEvidence` binds through `GetUniqueLoadID()`, a new object has a new one, and "
     "re-pointing a bound evidence record quietly is how a case gets lost. "
     "**NO EXISTING INSTRUMENT COULD HAVE CAUGHT THIS**, which is why there is a new one: a checker "
     "reading our source saw a correct transform, one reading the def saw a correctly attached "
     "comp, and the fault lived in a Core class neither reads. `check-record-book-class.py` is "
     "**checker 27** with ten rules, and `plant-record-book-class.py` is **plant suite 35 at 23 of "
     "23** -- which found **two false greens in the checker itself** before it was trusted: "
     "`CLASS_NAME in patch` passed while one of two values was wrong, and `PatchOperationAdd in "
     "patch` passed on a different operation in the same file. Both are scoped to the operation "
     "now, and a third rule that passed on a rename learned that `in` cannot tell a member from a "
     "prefix of one. "
     "**AND `--` WENT INTO AN XML COMMENT FOR THE FOURTH TIME.** The build caught it as an opaque "
     "PowerShell cast error; `check-package-integrity.check_comment_dashes` **already names the "
     "file and the line** and had simply not been run yet. The instrument was not missing -- the "
     "order was wrong, and the standing rule already says to run the one instrument covering the "
     "file just touched."),

    ("**A journal needs pawn click actions with step-by-step instructions, kept short.**",
     " -- **BUILT 0.12.99-dev, AND THE INSTRUCTIONS SIT ABOVE THE BINDING GUARD, WHICH IS THE "
     "WHOLE POINT.** "
     "Right-clicking a company book with a colonist now offers **" + Q + "What is this journal "
     "for?" + Q + "**, which opens the four steps; the same block is the book's information card, "
     "replacing the generated sentence that claimed nutrition. Four steps and a stop, because "
     "*" + Q + "keep it very concise asnd to the point" + Q + "* set the ceiling, and the whole "
     "block is **one keyed string** so a translator moves one entry and the order of the steps "
     "cannot be lost in concatenation. "
     "**The option is added before the `HasValidBinding` guard, deliberately.** The one state a "
     "player actually starts holding is a **blank** company book, which has no evidence binding at "
     "all -- so an option added below that guard would be invisible on exactly the book that needs "
     "explaining. That is the same fault `CompInspectStringExtra` carried until 0.12.9x, where an "
     "early return meant the only state with no guidance was the first one anybody meets. **The "
     "defect was already documented in the file and would have been repeated one method lower.** "
     "**AND IT WENT INTO THE WIKI, which is the second half of the owner's sentence and not "
     "optional.** `docs/wiki/company.md` gains **The record book**: what it is, the four steps a "
     "colonist takes, where the click action is, and a table of **all four ways a book arrives** "
     "with the coordinate one marked as *not yours yet*. `docs/wiki/first-hour.md` gains the line "
     "at the point it matters -- send somebody out **with a book**, because a crew without one "
     "records nothing -- and links to the full account. **Written only after the fix landed**: a "
     "wiki page describing an unbuilt journal is a published lie, and the published wiki is the one "
     "artefact `curl` has caught shipping 404s before. `check-doc-conformance` passes with both "
     "pages inside the 360-character wall."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:48], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d journal row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
