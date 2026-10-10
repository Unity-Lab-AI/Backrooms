# -*- coding: utf-8 -*-
"""The company's own books carry the company's label. Every other novel keeps Core's.

## Owner answer, 2026-10-04, verbatim: *"Mark the company-issued ones"*

Asked because the half of their earlier choice -- *"its own label and an inspect
card"* -- that was **not** built was deliberately not built, and the reason stood
up: `Patches/RR_ExistingEvidenceBook.xml` puts `CompProperties_RouteEvidence` on
**every** Core `TextBook`, because the design is that any blank book can be
carried in and written in the field. A `TransformLabel` on that comp would
retitle every novel in the game -- trade stock, quest rewards, other mods' books.

The owner's answer is the third option, and it is the right one: tag the books
the company hands out, and leave every other blank book alone.

## Two grant paths, and both are covered at the moment of granting

  * `ScenPart_StartingThing_Defined` in `RR_Scenarios.xml` -- Core creates these
    during arrival. `ScenPart_RimroomsArrival` **already enumerates everything
    Core just created**, for its receipt, so the mark goes in that same sweep.
  * Two books placed by `RR_Starts.xml` through `GenStep_Headquarters` -- marked
    where they are spawned.

**A book is marked once, at the moment the company issues it, and the flag is
saved.** Nothing scans for books later, which is what makes it impossible to
retro-tag something a player bought: there is no code path that can.

## The label is the only thing that changes

The card's wording is untouched -- it already opened with *"Company record book,
still blank"* -- and `TransformLabel` on an unmarked book returns Core's label
byte for byte, which is the behaviour every other `TextBook` in the game keeps.
"""
import io
import sys

NL = chr(10)

COMP = "src/RimroomsAsyncIndustries/Investigation/CompRouteEvidence.cs"
ARRIVAL = "src/RimroomsAsyncIndustries/Scenario/ScenPart_RimroomsArrival.cs"
GENSTEP = "src/RimroomsAsyncIndustries/Scenario/GenStep_Headquarters.cs"

EDITS = [
    # ------------------------------------------------- the flag, saved
    (COMP,
     "        private string evidenceId;" + NL
     + "        private string carrierLoadId;",

     "        private string evidenceId;" + NL
     + "        private string carrierLoadId;" + NL
     + "        /// <summary>" + NL
     + "        /// Whether the company issued this book, as opposed to it being any other blank"
     + NL
     + "        /// book in the game." + NL
     + "        ///" + NL
     + "        /// **Set once, at the moment of granting, and saved.** Owner, 2026-10-04:"
     + NL
     + "        /// *\"Mark the company-issued ones\"*. Nothing scans for books later, which is what"
     + NL
     + "        /// makes it impossible to retro-tag something a player bought or looted -- there is"
     + NL
     + "        /// no code path that could. The comp itself is on **every** Core `TextBook` by"
     + NL
     + "        /// patch, because any blank book can be written in the field; this flag is the only"
     + NL
     + "        /// thing that distinguishes the ones the branch handed out." + NL
     + "        /// </summary>" + NL
     + "        private bool companyIssued;"),

    (COMP,
     '            Scribe_Values.Look(ref carrierLoadId, "rr_carrierLoadId");',
     '            Scribe_Values.Look(ref carrierLoadId, "rr_carrierLoadId");' + NL
     + '            Scribe_Values.Look(ref companyIssued, "rr_companyIssued", false);'),

    # ------------------------------------- the mark, and the label it earns
    (COMP,
     "        public override void PostExposeData()",

     "        /// <summary>Whether the branch issued this book.</summary>" + NL
     + "        public bool IsCompanyIssued { get { return companyIssued; } }" + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// Mark this book as one the company handed out." + NL
     + "        ///" + NL
     + "        /// Refuses anything that is not a supported carrier, so a caller cannot brand a"
     + NL
     + "        /// thing that was never a record book. Idempotent: granting is recorded by a"
     + NL
     + "        /// receipt elsewhere and this must not care how many times it is asked." + NL
     + "        /// </summary>" + NL
     + "        public bool MarkCompanyIssued()" + NL
     + "        {" + NL
     + "            if (bindingSchema != 1 || !IsSupportedCarrier(parent)) { return false; }" + NL
     + "            companyIssued = true;" + NL
     + "            return true;" + NL
     + "        }" + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// The company's own label on the company's own book, and Core's on everything else."
     + NL
     + "        ///" + NL
     + "        /// **The guard is the whole point.** This comp is patched onto every Core"
     + NL
     + "        /// `TextBook`, so an unguarded transform here would retitle every novel in the"
     + NL
     + "        /// game: trade stock, quest rewards and other mods' books included. That is why the"
     + NL
     + "        /// label half of *\"its own label and an inspect card\"* was not built until the"
     + NL
     + "        /// owner chose how to tell the two apart." + NL
     + "        /// </summary>" + NL
     + "        public override string TransformLabel(string label)" + NL
     + "        {" + NL
     + "            if (!companyIssued) { return label; }" + NL
     + "            return \"RR_Evidence_CompanyBookLabel\".Translate().ToString();" + NL
     + "        }" + NL
     + NL
     + "        public override void PostExposeData()"),

    # ------------------------------------------- path one: Core's arrival grant
    (ARRIVAL,
     "                    receipt.arrivalRecords.Add(thing.GetUniqueLoadID() + \":\" + thing.def.defName + \":\" + thing.stackCount);"
     + NL
     + "                    if (thing.def.category == ThingCategory.Item) { thing.SetForbidden(false, false); }",

     "                    receipt.arrivalRecords.Add(thing.GetUniqueLoadID() + \":\" + thing.def.defName + \":\" + thing.stackCount);"
     + NL
     + "                    if (thing.def.category == ThingCategory.Item) { thing.SetForbidden(false, false); }"
     + NL
     + "                    // **THE COMPANY'S OWN BOOKS GET THE COMPANY'S LABEL.** Owner,"
     + NL
     + "                    // 2026-10-04: *\"Mark the company-issued ones\"*. This sweep is already"
     + NL
     + "                    // enumerating exactly what Core created for this arrival, which is the"
     + NL
     + "                    // only moment at which a book is known to have been issued rather than"
     + NL
     + "                    // bought. Marking here means no later code has to go looking for books"
     + NL
     + "                    // -- and so no later code can mistake a traded novel for one of ours."
     + NL
     + "                    Investigation.CompRouteEvidence issued ="
     + NL
     + "                        thing.TryGetComp<Investigation.CompRouteEvidence>();"
     + NL
     + "                    if (issued != null) { issued.MarkCompanyIssued(); }"),

    # ------------------------------- path two: the two books the start def places
    (GENSTEP,
     '                receipt.placedRecords.Add("building:" + index++ + ":" + building.GetUniqueLoadID());',

     "                // The start def places two record books among the furniture; they are issued"
     + NL
     + "                // by the company exactly as the scenario grant's are." + NL
     + "                Investigation.CompRouteEvidence placedBook ="
     + NL
     + "                    building.TryGetComp<Investigation.CompRouteEvidence>();" + NL
     + "                if (placedBook != null) { placedBook.MarkCompanyIssued(); }" + NL
     + '                receipt.placedRecords.Add("building:" + index++ + ":" + building.GetUniqueLoadID());'),
]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s: %r"
              % (text.count(old), path.split("/")[-1], old.strip().split(NL)[0][:76]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-28s patched %s" % (path.split("/")[-1], old.strip().split(NL)[0][:54]))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
