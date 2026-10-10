# -*- coding: utf-8 -*-
"""The Backrooms were capped at two levels deep by a string length.

Owner: *"anoother door said somthing like you cant doo that, request is not valid for this
branch"*, and *"it must be something about generationg the next world map or deeper backrroms idk
for sure"*. **Their read was exactly right, and the number is checkable:**

    branch id                            42
    coordinate A  = branch + ":coordinate:discovery:opening"           71
    discoveryId   = A + ":frontier:169,178"                            88   <- fits
    coordinate B  = branch + ":coordinate:discovery:" + discoveryId   152
    discoveryId   = B + ":frontier:120,95"                            168   <- REFUSED

`CreateDiscoveredCoordinate` refuses a `discoveryId` longer than 128 with
`RR_Company_InvalidRequest` -- *"That request is not valid for this branch."* And a coordinate's
id **embeds its parent's entire id**, which embeds its parent's, so the id grows by about eighty
characters per level. The first step inward works. **The second one has never been possible**, and
`MaximumNaturalDepth` -- the cap the owner actually designed -- was unreachable from the start.

*"have more natural portals guaranteeed so the backrooms never ends persay"* could not happen, and
the reason was a string.

## The fix, and why it keeps existing saves

The long form is kept **exactly** whenever it fits, so every coordinate already discovered in a
save resolves to the same space it always did -- the id is byte-for-byte what it was. Only when
the composed id would be refused is the parent replaced by a stable hash of itself, which bounds
the length for ever at any depth.

Two independent hashes are used, not one, because a single 31-bit FNV value shared by two
coordinates would merge two different places into one. Both are derived from the coordinate's own
saved id, so a reload resolves identically.

And the limit itself becomes a named constant read by both the enforcer and the composer, because
a validator and its caller carrying separate copies of one number is the defect this project has
now paid for three times in a week.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICES = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "CampaignServices.cs")
FRONTIER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                        "NaturalFrontierService.cs")

# ------------------------------------------- the limit, named, where it is enforced
S_OLD = u"""            if (string.IsNullOrWhiteSpace(discoveryId) || discoveryId.Length > 128 ||
                discoveryId.Any(character => char.IsWhiteSpace(character)))
            { return CompanyActionResult.Refused("RR_Company_InvalidRequest"); }"""

S_NEW = u"""            if (string.IsNullOrWhiteSpace(discoveryId) ||
                discoveryId.Length > MaximumDiscoveryIdLength ||
                discoveryId.Any(character => char.IsWhiteSpace(character)))
            { return CompanyActionResult.Refused("RR_Company_InvalidRequest"); }"""

S_CONST_ANCHOR = u"""        public CompanyActionResult CreateDiscoveredCoordinate(string discoveryId, int depth, out CoordinateRecord coordinate)"""

S_CONST = u"""        /// <summary>
        /// The longest discovery id this branch will accept, and **the number that capped the
        /// Backrooms at two levels deep.**
        ///
        /// A coordinate's id embeds its parent's entire id, so a discovery id grows by about
        /// eighty characters per level: 88 for the first step inward, **168 for the second**,
        /// which was refused with `RR_Company_InvalidRequest` -- *"that request is not valid for
        /// this branch"*. So `MaximumNaturalDepth`, the cap the owner designed, was never
        /// reachable, and *"have more natural portals guaranteeed so the backrooms never ends
        /// persay"* could not happen.
        ///
        /// **It is a named constant because its composer has to read it.** A validator and its
        /// caller carrying separate copies of one number is the defect that stopped every
        /// coordinate generating for thirty-nine checkpoints and refused every candidate layout
        /// two checkpoints ago. `NaturalFrontierService` asks this before composing an id, and
        /// shortens the parent rather than being refused.
        /// </summary>
        public const int MaximumDiscoveryIdLength = 128;

""" + S_CONST_ANCHOR

services = io.open(SERVICES, encoding="utf-8").read()
for old in (S_OLD, S_CONST_ANCHOR):
    if services.count(old) != 1:
        print("ANCHOR PROBLEM in CampaignServices: %d of %r" % (services.count(old), old[:60]))
        raise SystemExit(1)
services = services.replace(S_OLD, S_NEW, 1)
services = services.replace(S_CONST_ANCHOR, S_CONST, 1)
io.open(SERVICES, "w", encoding="utf-8", newline="").write(services)
print("the limit is named where it is enforced")

# --------------------------------------------- the composer keeps itself under it
F_OLD = u"""            string discoveryId = origin.OriginId + ":" + origin.KeyPrefix +
                door.Position.x + "," + door.Position.z;"""

F_NEW = u"""            string discoveryId = DiscoveryIdFor(origin, door);"""

F_METHOD_ANCHOR = u"""        /// <summary>
        /// Whether this doorway leads out of the Backrooms rather than deeper into it, and if"""

F_METHOD = u'''        /// <summary>
        /// The id of the space this doorway leads to, **bounded so that going deeper stays
        /// possible.**
        ///
        /// ## What was wrong
        ///
        /// This was `origin.OriginId + ":" + KeyPrefix + x + "," + z`, and a coordinate's id
        /// embeds its parent's entire id. So the id grew by about eighty characters per level:
        /// 88 for the first step inward, **168 for the second** -- past
        /// <see cref="RimroomsCampaignComponent.MaximumDiscoveryIdLength"/>, refused with
        /// `RR_Company_InvalidRequest`. **The Backrooms could never be more than two levels
        /// deep**, and `MaximumNaturalDepth` was unreachable.
        ///
        /// ## Why the long form is kept whenever it fits
        ///
        /// Byte-for-byte what it always was, so **every coordinate already discovered in a save
        /// resolves to exactly the same space.** Only an id that would be refused is shortened,
        /// and an id that would be refused never existed in a save to begin with.
        ///
        /// ## Why two hashes
        ///
        /// `StableHash` is a 31-bit FNV value. One of them shared by two parents would merge two
        /// different places into one coordinate -- a far worse outcome than a refusal. Two
        /// independent derivations of the same saved id make that vanishingly unlikely, and both
        /// are derived from the id alone, so a reload resolves identically.
        /// </summary>
        private static string DiscoveryIdFor(FrontierOrigin origin, Thing door)
        {
            string position = origin.KeyPrefix + door.Position.x + "," + door.Position.z;
            string full = origin.OriginId + ":" + position;
            if (full.Length <= RimroomsCampaignComponent.MaximumDiscoveryIdLength) { return full; }
            int first = DestinationService.StableHash(0, origin.OriginId, 1);
            int second = DestinationService.StableHash(origin.OriginId.Length, origin.OriginId, 7);
            return "o" + first.ToString("x8") + second.ToString("x8") + ":" + position;
        }

''' + F_METHOD_ANCHOR

frontier = io.open(FRONTIER, encoding="utf-8").read()
for old in (F_OLD, F_METHOD_ANCHOR):
    if frontier.count(old) != 1:
        print("ANCHOR PROBLEM in NaturalFrontierService: %d of %r"
              % (frontier.count(old), old[:60]))
        raise SystemExit(1)
frontier = frontier.replace(F_OLD, F_NEW, 1)
frontier = frontier.replace(F_METHOD_ANCHOR, F_METHOD, 1)
io.open(FRONTIER, "w", encoding="utf-8", newline="").write(frontier)
print("the composer stays under the limit at any depth")
