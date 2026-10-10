# -*- coding: utf-8 -*-
"""Wire the guarantee into the draw and into the kind, so every level has both portals.

Owner: *"every backrooms instance need a protal to the world map and a deeper in portal"*, after
*"i explored it all ... there were zero portals to be discovered"*.

THREE PLACES, AND EACH ONE IS A WAY THE GUARANTEE COULD HAVE BEEN QUIETLY LOST:

  1. **The rarity draw.** `if (draw % origin.Rarity != 0) return "RR_Frontier_LeadsNowhere";` with
     `FrontierRarity = 12` -- one doorway in twelve. A whole level can roll none, and the owner
     walked one that did. The two chosen doorways skip the draw.

  2. **The cap.** `if (foundHere >= origin.Cap) return "RR_Frontier_NoneLeftHere";` A level that
     has already found its four-to-six ways onward would refuse the guaranteed pair, which makes
     a guarantee conditional. They are exempt, and only they.

  3. **The kind.** A way onward inside the Backrooms leads out one time in three
     (`EmergenceShare`), otherwise deeper. Left to that draw, the guaranteed pair could both come
     up the same way. So the kind is **decided for them**: the out door records a world exit, the
     deeper door is never diverted into one.

Everything else still applies to them -- the threshold obstruction check, the way home never
being a frontier, a door already carrying an edge being refused, and `MaximumNaturalDepth`. **A
guarantee that skipped the safety checks would be a bug with a promise attached.**
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                       "NaturalFrontierService.cs")

EDITS = [
    # ------------------------------------------------- 1 and 2: the cap and the draw
    (u'''            if (foundHere >= origin.Cap) { return "RR_Frontier_NoneLeftHere"; }

            // The draw is over the doorway's position under this place's own stable seed.
            // Position is stable for the life of the map, so the answer never changes on a
            // reload or a revisit.
            int draw = CampaignSeed.Derive(origin.Seed,
                origin.KeyPrefix + door.Position.x + "," + door.Position.z, 1);
            if (draw % origin.Rarity != 0) { return "RR_Frontier_LeadsNowhere"; }
            return null;''',
     u'''            // **THE GUARANTEE.** Owner: *"every backrooms instance need a protal to the world
            // map and a deeper in portal"*. Two doorways per coordinate are chosen once and skip
            // both the cap and the draw below -- everything above still applies to them, because
            // a guarantee that skipped the safety checks would be a bug with a promise attached.
            bool guaranteedLeadsOut;
            bool guaranteed = sourceCoordinate != null
                && GuaranteedFrontiers.IsGuaranteed(door, sourceCoordinate, out guaranteedLeadsOut);

            // Exempt from the cap, and only they. A level that has already found its four-to-six
            // ways onward would otherwise refuse the pair, which makes a guarantee conditional.
            if (!guaranteed && foundHere >= origin.Cap) { return "RR_Frontier_NoneLeftHere"; }

            // The draw is over the doorway's position under this place's own stable seed.
            // Position is stable for the life of the map, so the answer never changes on a
            // reload or a revisit.
            //
            // **One doorway in twelve, and a whole level can roll none.** That is what the owner
            // walked: a Backrooms with no way deeper and no way out, and nothing to tell them the
            // dice simply had not come up.
            if (guaranteed) { return null; }
            int draw = CampaignSeed.Derive(origin.Seed,
                origin.KeyPrefix + door.Position.x + "," + door.Position.z, 1);
            if (draw % origin.Rarity != 0) { return "RR_Frontier_LeadsNowhere"; }
            return null;'''),

    # ----------------------------------------------------------------- 3: the kind
    (u'''            if (door == null || origin == null || campaign == null) { return null; }
            int draw = CampaignSeed.Derive(origin.Seed,
                "wayout:" + door.Position.x + "," + door.Position.z, 1);''',
     u'''            if (door == null || origin == null || campaign == null) { return null; }

            // **THE KIND IS DECIDED FOR THE GUARANTEED PAIR, NOT DRAWN.** A way onward leads out
            // one time in three otherwise, and left to that draw both guaranteed doorways could
            // come up the same way -- which would satisfy "two portals" while delivering one
            // kind, and the owner asked for *"a protal to the world map AND a deeper in portal"*.
            CoordinateRecord guaranteeSource = campaign.Coordinates == null ? null
                : campaign.Coordinates.FirstOrDefault(candidate => candidate != null
                    && candidate.Id == origin.OriginId);
            bool leadsOut;
            if (guaranteeSource != null
                && GuaranteedFrontiers.IsGuaranteed(door, guaranteeSource, out leadsOut))
            {
                // The deeper one is never diverted out; returning null sends the caller on to
                // mint a coordinate, which is exactly what it does for an ordinary deeper find.
                if (!leadsOut) { return null; }
                return campaign.RecordWorldExit(door, origin.OriginId, origin.Seed);
            }

            int draw = CampaignSeed.Derive(origin.Seed,
                "wayout:" + door.Position.x + "," + door.Position.z, 1);'''),
]

text = io.open(SERVICE, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(SERVICE, "w", encoding="utf-8", newline="").write(text)
print("guarantee wired into the cap, the draw and the kind")
