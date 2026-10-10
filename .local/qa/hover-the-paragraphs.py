# -*- coding: utf-8 -*-
"""Move the remaining Operations paragraphs onto the lines and controls they explain.

Owner direction, 2026-10-04, verbatim: *"and all the tabs of operations are well
designed for a tripple A Mod currently it looks like its all just text wall and
shit"*, and *"things can be shortend and more concise and dirrect  with tools
tips would less cluter it making them all concise and accurate"*.

Each replacement below pairs a long explanation with the short line already above
it, so **no new keyed string is written**: the heading was already on screen and
the paragraph under it is now its hover. Where there was no heading, the
paragraph attaches to the control it is the small print for.

Written with the Write tool, not a heredoc -- escapes have been mangled thirteen
times in this repository and three of these replacements carry `\\n` sequences in
C# string literals.
"""
import io
import sys

NL = chr(10)
UI = "src/RimroomsAsyncIndustries/UI/"

REPLACEMENTS = [
    # ---------------------------------------------------------------- procurement
    (UI + "OperationsProcurement.cs",
     '            listing.Label("RR_Procurement_BranchBalance".Translate(Money(campaign.BalanceUsd)));\n'
     '            listing.Label("RR_Procurement_EstimateNotice".Translate());',
     '            // The twenty-two words about catalog prices being provisional estimates are a\n'
     '            // caveat on the balance they are quoted against, so they hang off the balance.\n'
     '            DrawHeading(listing,\n'
     '                heading: "RR_Procurement_BranchBalance".Translate(Money(campaign.BalanceUsd)),\n'
     '                detail: "RR_Procurement_EstimateNotice".Translate());'),

    (UI + "OperationsProcurement.cs",
     '            listing.Label("RR_Procurement_OrderInstructions".Translate());\n'
     '            if (catalog.Count == 0) { listing.Label("RR_Proc_CatalogUnavailable".Translate()); }\n'
     '            else if (listing.ButtonText("RR_Procurement_SelectItem".Translate(selectedCatalog.LabelCap)))\n'
     '            { OpenCatalogMenu(catalog); }',
     '            // **THE THIRTY-NINE WORDS OF METHOD GO ON THE FIRST STEP OF IT.** Choosing the\n'
     '            // item is where the order starts, so the explanation of what the quote snapshots\n'
     '            // and what it does not is the small print on that button. An empty catalog is a\n'
     '            // fault and stays a sentence on screen.\n'
     '            if (catalog.Count == 0) { listing.Label("RR_Proc_CatalogUnavailable".Translate()); }\n'
     '            else if (DrawAction(listing,\n'
     '                    label: "RR_Procurement_SelectItem".Translate(selectedCatalog.LabelCap),\n'
     '                    refusal: TaggedString.Empty,\n'
     '                    detail: "RR_Procurement_OrderInstructions".Translate()))\n'
     '            { OpenCatalogMenu(catalog); }'),

    # ----------------------------------------------------------------- facilities
    (UI + "OperationsFacilities.cs",
     '            listing.Label("RR_Fac_Explanation".Translate());\n'
     '            if (listing.ButtonText("RR_Fac_Refresh".Translate())) { facilityReport.RefreshIfNeeded(campaign, true); }',
     '            // What "headquarters infrastructure" counts as, on the button that recounts it.\n'
     '            if (DrawAction(listing, label: "RR_Fac_Refresh".Translate(),\n'
     '                    refusal: TaggedString.Empty,\n'
     '                    detail: "RR_Fac_Explanation".Translate()))\n'
     '            { facilityReport.RefreshIfNeeded(campaign, true); }'),

    (UI + "OperationsFacilities.cs",
     '            listing.Label("RR_Fac_OtherBeds".Translate(facilityReport.MedicalSlots, facilityReport.OtherBedSlots));\n'
     '            listing.Label("RR_Fac_BedLimit".Translate());',
     '            // **THE CAVEAT BELONGS ON THE COUNT IT QUALIFIES.** Thirty-four words saying an\n'
     '            // empty slot is not a usable bed -- body size, ideology, access, reservations --\n'
     '            // read as a paragraph of its own and as a contradiction of the number above it.\n'
     '            DrawHeading(listing,\n'
     '                heading: "RR_Fac_OtherBeds".Translate(facilityReport.MedicalSlots,\n'
     '                    facilityReport.OtherBedSlots),\n'
     '                detail: "RR_Fac_BedLimit".Translate());'),

    (UI + "OperationsFacilities.cs",
     '            listing.Label("RR_Integration_Heading".Translate(\n'
     '                Core.InstalledIntegrations.ActiveCount(), tracked.Count));\n'
     '            listing.Label("RR_Integration_Caveat".Translate());',
     '            // *"Loaded means present, not proven"* is the definition of the count beside it.\n'
     '            DrawHeading(listing,\n'
     '                heading: "RR_Integration_Heading".Translate(\n'
     '                    Core.InstalledIntegrations.ActiveCount(), tracked.Count),\n'
     '                detail: "RR_Integration_Caveat".Translate());'),

    (UI + "OperationsFacilities.cs",
     '            listing.Label("RR_Debrief_Outstanding".Translate(holds.Count));',
     '            // The count is the readout; that none of them go out again until they report is\n'
     '            // the rule behind it, and the rule does not change between visits.\n'
     '            DrawHeading(listing, heading: "RR_Debrief_Count".Translate(holds.Count),\n'
     '                detail: "RR_Debrief_Outstanding".Translate(holds.Count));'),

    # --------------------------------------------------------------- gate binding
    (UI + "OperationsGateBinding.cs",
     '            listing.Label("RR_NativeGate_Heading".Translate());\n'
     '            listing.Label("RR_NativeGate_Explanation".Translate());',
     '            DrawHeading(listing, heading: "RR_NativeGate_Heading".Translate(),\n'
     '                detail: "RR_NativeGate_Explanation".Translate());'),

    (UI + "OperationsGateBinding.cs",
     '            listing.Label("RR_NativeGate_SharedBatteryWarning".Translate());\n'
     '            listing.Label("RR_NativeGate_DoorStateExplanation".Translate());',
     '            // **FIFTY-FIVE WORDS OF STANDING TRUTH, DRAWN EVERY FRAME.** Neither of these\n'
     '            // changes with state: a shared battery is always shared, and the door\'s own\n'
     '            // Open/Hold state always means something different from the connection window.\n'
     '            // Both are things a player needs once, which is what a hover is for.\n'
     '            DrawHeading(listing, heading: "RR_NativeGate_InfrastructureNotes".Translate(),\n'
     '                detail: "RR_NativeGate_SharedBatteryWarning".Translate()\n'
     '                    + "\\n\\n" + "RR_NativeGate_DoorStateExplanation".Translate());'),

    (UI + "OperationsGateBinding.cs",
     '                listing.Label("RR_NativeGate_DebitFaultExplanation".Translate());\n'
     '                if (listing.ButtonText("RR_NativeGate_AcknowledgeDebit".Translate()))\n'
     '                { ShowResult(gate.AcknowledgeNativeEnergyDebit()); }',
     '                // **WHAT ACKNOWLEDGEMENT DOES AND DOES NOT DO, ON THE ACKNOWLEDGE BUTTON.**\n'
     '                // It does not refill the battery. A player pressing it to fix the fault has\n'
     '                // misread the paragraph that used to sit above it, and the one place they\n'
     '                // cannot misread it is the button itself.\n'
     '                if (DrawAction(listing, label: "RR_NativeGate_AcknowledgeDebit".Translate(),\n'
     '                        refusal: TaggedString.Empty,\n'
     '                        detail: "RR_NativeGate_DebitFaultExplanation".Translate()))\n'
     '                { ShowResult(gate.AcknowledgeNativeEnergyDebit()); }'),
]

USING = "using static RimroomsAsyncIndustries.UI.OperationsControls;" + NL

problems = 0
touched = {}

for path, old, new in REPLACEMENTS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if new.strip().split(NL)[-1] in text and old not in text:
        print("already applied in %s" % path.split("/")[-1])
        continue
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s: %r"
              % (text.count(old), path.split("/")[-1], old.strip()[:84]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-30s rewired %s" % (path.split("/")[-1], old.strip().split(NL)[0][:62]))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    text = touched[path]
    if USING not in text:
        at = text.index(NL + "namespace ")
        text = text[:at] + NL + USING + text[at:]
        print("added the static import to %s" % path.split("/")[-1])
    io.open(path, "w", encoding="utf-8", newline=NL).write(text)
    print("wrote %s" % path.split("/")[-1])
