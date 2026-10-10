"""Record the connected-work findings for the three hauling profile rows.

TODO item: the three hauling providers -- Pick Up And Haul (164), Haul To Stack (107),
Prison Labor (288) -- read each review, record the disposition, done.

All three already carried a profile disposition. What none of them carried was the
question that matters now that twenty-two cross-map work families exist: does this
mod interact with them. That is what these edits record, and one of the three answers
turned out to be a verified Core fact rather than a pending test.
"""
import csv
import os

ROOT = r"C:\Users\gfour\Desktop\Backrooms"
INVENTORY = os.path.join(ROOT, "docs", "research", "rimworld-server-mod-inventory.csv")
FIELDS = os.path.join(ROOT, "docs", "research", "mod-register-integration-fields-2026-09-29.csv")

DISPOSITION = {
    "164": (
        "Provisional: optional hauling QoL; Rimrooms cargo records and vanilla hauling remain "
        "independent. Cross-map work is unaffected by design: the connected families run their own "
        "job driver and work givers, not WorkGiver_HaulGeneral, so this mod has no seam to patch. "
        "The untested direction is the reverse one -- a worker carrying inventory items it gathered "
        "for a near-side stockpile when its crossing begins."),
    "107": (
        "Optional hauling QoL; do not build supply loops around it. No interaction with the "
        "connected cross-map families. The publisher states this mod does nothing on newer game "
        "versions while Pick Up And Haul is active, and Pick Up And Haul is selected at row 164; "
        "that is a page claim, not a reproduced result, so treat it as inert pending the test phase. "
        "Steam also shows an item-removed notice with no stated reason."),
    "288": (
        "Provisional: no Rimrooms dependency or adapter; preserve this mod and vanilla prisoner "
        "controls; custody/UI interactions need testing. Settled on one axis: a prisoner given work "
        "by this mod can never cross a gate. PortalTraversalPolicy admits only Faction.OfPlayer "
        "colonists, and Pawn.IsColonist requires Faction.IsPlayer, which a prisoner of the colony "
        "never has -- prisoners keep their own faction and are held by HostFaction. Verified in "
        "Core source, not inferred."),
}

WATCH = {
    "164": (
        "Medium: verify stack, weight, ownership, caravan, and RWT transfer behavior for mission "
        "cargo. Connected-work check added 2026-09-29: confirm a worker holding a live cross-map "
        "commitment that has gathered inventory items for a near-side stockpile does not carry them "
        "through the gate, and that the one-commitment-per-worker chokepoint survives this mod's "
        "inventory hauling. The publisher's own page calls unloading imperfect and lists guest and "
        "prisoner limitations."),
    "107": (
        "Medium: confirm stack rules still distinguish quarantined samples, ordinary stock, and "
        "mission cargo. Connected-work check added 2026-09-29: none needed -- this mod has no cross-"
        "map surface. Verify the publisher's inert-alongside-Pick-Up-And-Haul claim on the pinned "
        "profile rather than trusting it, and resolve the Steam removal notice before relying on "
        "the mod being present at all."),
    "288": (
        "Missing 1.6/Biotech conditional path; prisoner UI/work assignments may conflict with other "
        "prisoner and UI mods. Exact interaction and RWT transfer untested. Connected-work check "
        "added 2026-09-29: a prisoner can never be sent through a gate, verified from Pawn."
        "IsColonist. Still worth confirming at runtime that a prisoner working under this mod is "
        "never offered a connected work giver at all, and that the warden deployment still finds "
        "prisoners on a far map while this mod owns their work assignments."),
}


def patch(path, key_field, updates):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    touched = 0
    for row in rows:
        order = row["LoadOrder"]
        if order in updates:
            if key_field not in row:
                raise SystemExit("%s has no %s column" % (path, key_field))
            row[key_field] = updates[order]
            touched += 1
    if touched != len(updates):
        raise SystemExit("expected %d rows in %s, touched %d" % (len(updates), path, touched))
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("patched %s rows of %s (%s)" % (touched, os.path.basename(path), key_field))


patch(INVENTORY, "FinalDisposition", DISPOSITION)
patch(FIELDS, "CompatibilityWatch", WATCH)
