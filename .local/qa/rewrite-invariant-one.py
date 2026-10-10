# -*- coding: utf-8 -*-
"""Rewrite every document that asserts the old invariant #1, in the same change as the code.

**DOCS-BEFORE-PUSH, and this is the case the LAW exists for.** Six documents and one class comment
assert that `AutonomousNonPlayerTraversalPermitted` is a constant false and that nothing may ever
cross outward. The owner superseded that on 2026-10-06. A document left denying what the code beside
it now does is the stale-comment failure this repository has a rule about, and it is worse here than
usual: a future reader would take the document as the design and treat the code as the bug.

FINALIZED.md is NOT edited. The archive is append-only, so entry 54's *"must stay false for
everything, forever"* stays exactly as written and the supersession is recorded where the rule now
lives. TODO.md is not edited either -- its rows already carry the owner's words.
"""
import io
import sys

NL = chr(10)

EDITS = [
    # ------------------------------------------------------------------ the architecture statement
    ("docs/ARCHITECTURE.md",
     "`AutonomousNonPlayerTraversalPermitted` is a constant false and `MayApproachThresholdForTraversal` is unconditionally false, so an open gate can never become an objective, lure, spawn target, raid route or attack trigger for a later adapter, scheduler, generator or threat.",
     "**Rewritten 2026-10-06 by owner direction, and only half of it went.** Owner: *\"not anyone in "
     "base, but anyone on your map.. a enemy can break in and cross the gate to get valuables and "
     "members\"*, then *\"hold up now friendlys can too\"*. "
     "`AutonomousNonPlayerTraversalPermitted` is **gone** rather than left at false, because a "
     "constant denying what the code beside it does is a stale comment with authority; "
     "`PortalTraversalPolicy.OutboundCrossingFailureKey` replaces it and is asked there and nowhere "
     "else. **`MayApproachThresholdForTraversal` is still unconditionally false**, which is the "
     "surviving half doing real work: nothing is ever *lured*, so an open gate still cannot become an "
     "objective, a spawn target or a raid route. A hostile or a visitor crosses because it wandered to "
     "a threshold that happens to be open, and the gate notices what is already on its doorstep. "
     "**One chokepoint is kept unchanged, which is the part this clause was always protecting:** no "
     "later adapter, scheduler, generator or threat may decide a crossing for itself."),

    # ------------------------------------------------------------------ the contract statement
    ("docs/CONNECTED_COLONY_PORTALS.md",
     "It also exposes `AutonomousNonPlayerTraversalPermitted` as a constant false and `MayApproachThresholdForTraversal` as an unconditional false, so a later work adapter, scheduler, generator or threat cannot reintroduce the behaviour by accident.",
     "**Changed 2026-10-06 by owner direction; see `CROSS_MAP_TRAVERSAL_BRIEF.md`.** "
     "`AutonomousNonPlayerTraversalPermitted` no longer exists -- the owner's direction is that "
     "anything standing on the branch's map may walk out through an open gate, so a constant denying "
     "it would be a lie with a compiler behind it. `OutboundCrossingFailureKey` is the one place that "
     "may say yes, and `IncursionFailureKey` remains the one place for the other direction. "
     "**`MayApproachThresholdForTraversal` is still an unconditional false**, so no work adapter, "
     "scheduler, generator or threat can make a gate into a destination: a crossing is only ever "
     "offered to something that already walked to the threshold on its own business."),

    # ------------------------------------------------------------------ the travel record
    ("docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md",
     "- `AutonomousNonPlayerTraversalPermitted` is a constant `false` and `MayApproachThresholdForTraversal` returns an unconditional `false`, so a later work adapter, scheduler, generator or threat cannot reintroduce the behaviour by accident. These exist to be read by future code, not configured.",
     "- **Superseded 2026-10-06 by owner direction.** `AutonomousNonPlayerTraversalPermitted` has been "
     "removed: anything standing on the branch's map may now walk out through an open gate, and "
     "`PortalTraversalPolicy.OutboundCrossingFailureKey` is the one place that decides it. "
     "`MayApproachThresholdForTraversal` **still returns an unconditional `false`** -- nothing is ever "
     "given a gate as a destination -- so the guarantee this bullet existed for survives intact: no "
     "later work adapter, scheduler, generator or threat can reintroduce a crossing of its own, "
     "because the policy is still the only thing that may ever say yes."),

    # ------------------------------------------------------------------ the fit record
    ("docs/implementation/GATE_FIT_IMPLEMENTATION.md",
     "`AutonomousNonPlayerTraversalPermitted` is still a constant false and `MayApproachThresholdForTraversal` still returns false for everything.",
     "**`AutonomousNonPlayerTraversalPermitted` was removed 2026-10-06 by owner direction** and "
     "`MayApproachThresholdForTraversal` still returns false for everything. **The ownership test this "
     "record is about is unchanged**: a Backrooms inhabitant is hostile or unfactioned and still fails "
     "`TravellerFailureKey` on `Faction != Faction.OfPlayer` exactly as it always did. What changed is "
     "a separate, named route in the other direction, `OutboundCrossingFailureKey`, which this "
     "record's fit rules bound just as tightly -- a body too large for the opening cannot go out "
     "through it either."),

    # ------------------------------------------------------------------ the incursion record
    ("docs/implementation/GATE_INCURSION_IMPLEMENTATION.md",
     "- `MayApproachThresholdForTraversal` **still returns false for everything.** Nothing on the far side is ever given a threshold as a destination or a reason to converge on one.",
     "- `MayApproachThresholdForTraversal` **still returns false for everything**, including after the "
     "2026-10-06 owner direction that added outbound crossing. Nothing on either side is ever given a "
     "threshold as a destination or a reason to converge on one. **That is why incursion stayed fair "
     "and why its outbound mirror is fair too:** a pawn is at the doorway because of its own business, "
     "and the gate notices what is already there."),

    ("docs/implementation/GATE_INCURSION_IMPLEMENTATION.md",
     "`AutonomousNonPlayerTraversalPermitted` is still a constant `false`.",
     "`AutonomousNonPlayerTraversalPermitted` **was removed 2026-10-06 by owner direction**, because "
     "a constant denying what the code beside it now does is exactly the kind of founding comment this "
     "record already refused to leave standing. **And the lord defect this record did not catch is "
     "fixed in the same change:** `Transfer` despawned an intruder out from under its `Lord` -- which "
     "is per map -- and spawned it with none, so a hostile that followed a crew home arrived with no "
     "assault behaviour at all. It now gets `LordJob_AssaultColony` with `canSteal` and `canKidnap` on "
     "arrival."),
]


def main():
    for path, old, new in EDITS:
        text = io.open(path, encoding="utf-8-sig").read()
        if old not in text:
            print("REFUSED: %s does not contain the expected sentence" % path)
            return 1
        if text.count(old) != 1:
            print("REFUSED: %s contains it %d times" % (path, text.count(old)))
            return 1
        io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new, 1))
        print("rewrote %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
