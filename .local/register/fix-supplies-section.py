# -*- coding: utf-8 -*-
"""The supplies section says what the company adds, and the gate line stops asserting a falsehood.

Owner: *"that pop up should list all the equipemnet for the gate that u get added to ur start on
top of what u fill out in edb prepare carfully"*.

Two changes on the page, and one of them is a content bug the owner's screenshot exposed by
accident.

1. **The supplies section lists the company's own contribution first**, read from the authored
   scenario def rather than from the live one, then whatever the live scenario is carrying under
   its own heading -- *"on top of what u fill out"*, both visible, neither guessed at. When the
   two disagree, the page says so instead of leaving the player to notice.

2. **`RR_Setup_GateCost` claimed the assembly materials were in the supplies below. For the
   Furniture Store start that is false.** The bill wants 100 steel and 8 components; the Store
   arrives with 80 steel and no components at all. The line was written against the Async start
   and asserted for all three. It now names the cost and points at the list without promising
   what is in it -- and the list beneath it is the evidence, which is the whole point of showing
   it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Scenario",
                    "Page_RimroomsCompanySetup.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed", "RR_StartupSetup.xml")

PAGE_OLD = u'''                listing.GapLine();
                listing.Label("RR_Setup_Supplies".Translate());
                foreach (string supply in StartupReview.SupplySummary()) { listing.Label(supply); }'''

PAGE_NEW = u'''                listing.GapLine();

                // WHAT THE COMPANY ADDS, FIRST AND NAMED AS SUCH. Owner, verbatim: *"that pop up
                // should list all the equipemnet for the gate that u get added to ur start on top
                // of what u fill out in edb prepare carfully"*.
                //
                // Read from the authored scenario def, so a setup utility that rewrites the live
                // scenario's starting-thing parts cannot empty this list -- which is exactly what
                // left the section blank.
                listing.Label("RR_Setup_CompanySupplies".Translate());
                List<string> company = StartupReview.CompanySupplies(start);
                if (company.Count == 0) { listing.Label("RR_Setup_None".Translate()); }
                foreach (string supply in company) { listing.Label(supply); }

                listing.GapLine();
                listing.Label("RR_Setup_Supplies".Translate());
                List<string> live = StartupReview.SupplySummary();
                if (live.Count == 0) { listing.Label("RR_Setup_None".Translate()); }
                foreach (string supply in live) { listing.Label(supply); }
                // Said plainly rather than reconciled: something else is managing the equipment,
                // which is a legitimate choice, and the two lists differing is the fact to report.
                if (StartupReview.EquipmentManagedElsewhere(start))
                { listing.Label("RR_Setup_SuppliesDiffer".Translate()); }'''

text = io.open(PAGE, encoding="utf-8").read()
if text.count(PAGE_OLD) != 1:
    print("PAGE ANCHOR PROBLEM: %d" % text.count(PAGE_OLD))
    raise SystemExit(1)
text = text.replace(PAGE_OLD, PAGE_NEW, 1)
io.open(PAGE, "w", encoding="utf-8", newline="").write(text)
print("supplies section rewritten")

KEY_OLD = (u"  <RR_Setup_GateCost>The assembly bill wants {0}, carried to the bench and worked by "
           u"a crafter. Those are in the supplies below.</RR_Setup_GateCost>")
KEY_NEW = (u"  <RR_Setup_GateCost>The assembly bill wants {0}, carried to the bench and worked by "
           u"a crafter. Check the starting supplies below for them.</RR_Setup_GateCost>\n"
           u"  <RR_Setup_CompanySupplies>Starting supplies the company adds to this start</RR_Setup_CompanySupplies>\n"
           u"  <RR_Setup_SuppliesDiffer>The starting equipment in play differs from the company's "
           u"own list above, so another setup mod is managing it. What arrives is the list "
           u"directly above this line; edit it there if the gate materials are missing."
           u"</RR_Setup_SuppliesDiffer>")

keyed = io.open(KEYED, encoding="utf-8").read()
if keyed.count(KEY_OLD) != 1:
    print("KEYED ANCHOR PROBLEM: %d" % keyed.count(KEY_OLD))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8", newline="").write(keyed.replace(KEY_OLD, KEY_NEW, 1))
print("keyed strings updated: gate cost no longer promises, two new keys")
