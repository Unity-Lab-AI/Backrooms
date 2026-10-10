"""Record the bill-work-deployment findings against the profile rows they came from.

Five rows were read before writing the family, per the owner's standing rule that the
prep work is where mod facts live. Each one answered a real question, and the answers
belong back in the register rather than only in an implementation record.

Nothing here edits another mod. These are our notes about how our own code behaves
alongside theirs.
"""
import csv
import os

ROOT = r"C:\Users\gfour\Desktop\Backrooms"
FIELDS = os.path.join(ROOT, "docs", "research", "mod-register-integration-fields-2026-09-29.csv")

WATCH = {
    # 260 While You Are Nearby
    "260": (
        "Check priority ties, restricted work types, expedition maps and performance in the "
        "complete profile. Connected-work check added 2026-09-29 for the bill work family: "
        "this mod reorders which target a scanning work giver picks by distance, and the "
        "connected givers are NonScanJob givers with a single candidate, so there is nothing "
        "for it to reorder. Its stated effect -- prefer near work over distant -- already "
        "matches this family's own rule, because the planning giver sits below every local "
        "giver in its work type. Confirm at runtime that it never raises a cross-gate job "
        "above local work of the same type."),
    # 67 Compact Work Tab
    "67": (
        "Optional UI-only coexistence; show Rimrooms work types without changing work logic. "
        "Connected-work check added 2026-09-29: the bill work family adds ten work giver defs "
        "across Cooking, Crafting, Smithing, Tailoring and Art, bringing the mod's total to "
        "fifty-seven givers. The publisher states added work types work; these are added "
        "givers within existing types, which is a weaker change. Confirm header readability "
        "and wheel priority behaviour with all of them present, and with Numbers (row 197) "
        "active. Fluffy's Work Tab is not in the profile."),
    # 53 Big Little Mod Patch
    "53": (
        "In an isolated 1.6 profile, verify listed Jewelry/Sparkling Worlds linkables and "
        "representative Rimrooms benches, compare with the patch absent, and record load "
        "order and errors. Connected-work note added 2026-09-29: the bill work family reads "
        "its bench set from every loaded WorkGiverDef's fixedBillGiverDefs, so any bench this "
        "patch bundle links is covered with no code naming it and nothing of its copied or "
        "patched."),
    # 246 Vanilla Furniture Expanded - Factory
    "246": (
        "Check recipes, quantities, fuel/power/heat, belts/spoilage, storage handoff, "
        "performance, save/load, and VGE cargo before/after launch. Connected-work check "
        "added 2026-09-29: its bill-driven benches are picked up automatically by the bill "
        "work family IF their work type is one of Cooking, Crafting, Smithing, Tailoring or "
        "Art. A bench under a wholly new modded work type is NOT covered -- a named limit, "
        "not a claim. Confirm which work types its benches use before relying on either."),
    # 96 Fueled Crematoriums
    "96": (
        "Connected-work check added 2026-09-29: a fuelled bill giver matters because Core "
        "hands out a refuel job instead of the bill when CompRefuelable.HasFuel is false. The "
        "bill work family requires UsableForBillsAfterFueling(), so nobody crosses a gate for "
        "a bench that only needs fuel; the fuel carry family already owns that route. Confirm "
        "a far-side crematorium that is out of fuel pulls fuel rather than a worker, and that "
        "a refuelled one then pulls the worker."),
}


def patch(path, key_field, updates):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    touched = 0
    for row in rows:
        if row["LoadOrder"] in updates:
            row[key_field] = updates[row["LoadOrder"]]
            touched += 1
    if touched != len(updates):
        raise SystemExit("expected %d rows, touched %d" % (len(updates), touched))
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("patched %d rows of %s (%s)" % (touched, os.path.basename(path), key_field))


patch(FIELDS, "CompatibilityWatch", WATCH)
