using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// What a crossing pawn is carrying **in its pack** rather than in its hands, and why that
    /// never goes through a gate.
    ///
    /// ## The hole this closes, which is ours and not a mod's
    ///
    /// <see cref="PortalTraversalPolicy.CargoFailureKey"/> governs `carryTracker` -- the hands --
    /// and `PortalCrossingService` records exactly that on the receipt via `RecordCarriedThing`.
    /// **Nothing anywhere looked at `pawn.inventory`.** So a pawn whose pack held anything crossed
    /// with it, unrecorded: no cargo policy applied to it, no receipt line mentioned it, and the
    /// branch's own accounting of what went through its gate was wrong by whatever was in the bag.
    ///
    /// **Hands are the cargo route. The pack is not.** That is the rule this file makes true, and
    /// it was already the design everywhere else -- the cargo refusals, the custody transfer and
    /// the receipt are all built around the carried thing.
    ///
    /// ## Where the question came from
    ///
    /// The mod register, row 164 (**Pick Up And Haul**), under *Compatibility Watch*, verbatim:
    /// *"confirm a worker holding a live cross-map commitment that has gathered inventory items
    /// for a near-side stockpile does not carry them through the gate"*. Its disposition records
    /// the forward direction as already safe by design -- the connected families run their own
    /// job driver and work givers, not `WorkGiver_HaulGeneral`, so that mod has no seam to patch
    /// -- and names this as the untested reverse one.
    ///
    /// **It needed no adapter and it is not a compatibility fix.** Pick Up And Haul moves haul
    /// loads into `pawn.inventory`, so it makes this common rather than rare; the hole is ours
    /// either way, and a Core pawn with a spare meal in its pack walks into it too. Nothing here
    /// references that mod, reads its comps or patches it, and the behaviour is identical with it
    /// absent -- which is invariant 42 satisfied by there being nothing to apply.
    ///
    /// ## Core decides what counts, not us
    ///
    /// `Pawn_InventoryTracker.FirstUnloadableThing` is Core's own answer to *what in this pack is
    /// not this pawn's to keep*, read out of the installed game rather than guessed: it keeps the
    /// amounts a drug policy says to carry, every `inventoryStock` entry, and for a colonist as
    /// much packable food as its own hunger justifies. Everything else is freight.
    ///
    /// Using Core's rule rather than our own matters twice over. A pawn never loses its own
    /// medicine, drugs or packed meal at a threshold -- which a naive *"empty the pack"* would
    /// have done, and `DropAllNearPawn` still would. And the definition cannot drift away from
    /// the one the game's own unload job uses.
    /// </summary>
    public static class CrossingInventoryPolicy
    {
        /// <summary>
        /// A bound on the loop, not a design limit.
        ///
        /// `FirstUnloadableThing` is a property that recomputes, so draining it is a loop whose
        /// termination depends on each drop actually removing something. A drop that silently
        /// fails would spin for ever, and a frozen tick is a worse failure than a refused
        /// crossing. Sixty-four distinct stacks in one pack is already far past anything the game
        /// produces, so reaching this bound means something is wrong rather than busy.
        /// </summary>
        public const int MaximumFreightStacks = 64;

        /// <summary>How many stacks of freight this pawn's pack holds, bounded.</summary>
        public static int FreightStacks(Pawn pawn)
        {
            if (pawn == null || pawn.inventory == null || pawn.inventory.innerContainer == null)
            { return 0; }
            int stacks = 0;
            foreach (Thing thing in pawn.inventory.innerContainer)
            {
                if (thing != null) { stacks++; }
                if (stacks >= MaximumFreightStacks) { break; }
            }
            // The pack holding things is not the same question as the pack holding freight, and
            // only Core can answer the second one. A pawn carrying nothing but its own drug-policy
            // allowance has stacks and no freight.
            return HasFreight(pawn) ? stacks : 0;
        }

        /// <summary>
        /// Whether anything in this pawn's pack is freight by Core's own definition.
        ///
        /// Asked through `FirstUnloadableThing` rather than by walking the container, because the
        /// keep-list it applies is Core's and reimplementing it here is how the two would come to
        /// disagree.
        /// </summary>
        public static bool HasFreight(Pawn pawn)
        {
            if (pawn == null || pawn.inventory == null || pawn.inventory.innerContainer == null)
            { return false; }
            if (pawn.inventory.innerContainer.Count == 0) { return false; }
            return pawn.inventory.FirstUnloadableThing.Thing != null;
        }

        /// <summary>
        /// Put the freight down on the side the pawn is standing on, and report how many stacks
        /// went down.
        ///
        /// **Dropped rather than refused outright**, because refusing would strand a hauler at the
        /// threshold with a job it cannot finish and no way for the player to see why. The items
        /// land at the pawn's feet on the **near** side, which is where the near-side haul that
        /// gathered them was taking them anyway: the existing job notices them again, and the
        /// player sees a pile by the gate, which needs no letter to explain.
        ///
        /// **Only ever called while the pawn is still spawned on the source map**, before any
        /// custody change. Dropping after `DeSpawn` would have no map to drop onto, and dropping
        /// during the rollback path would lose goods on a crossing that failed through no fault of
        /// the pawn's -- so `TryRecoverToSource` deliberately does not call this.
        /// </summary>
        public static int DropFreight(Pawn pawn)
        {
            if (!HasFreight(pawn)) { return 0; }
            if (!pawn.Spawned || pawn.Map == null) { return 0; }
            int dropped = 0;
            for (int guard = 0; guard < MaximumFreightStacks; guard++)
            {
                ThingCount freight = pawn.inventory.FirstUnloadableThing;
                if (freight.Thing == null) { break; }
                Thing landed;
                int count = freight.Count < 1 ? 1 : freight.Count;
                if (!pawn.inventory.innerContainer.TryDrop(freight.Thing, pawn.Position, pawn.Map,
                        ThingPlaceMode.Near, count, out landed))
                {
                    // A pack that will not empty is reported by the caller as a refusal rather
                    // than crossed with. Breaking here instead of spinning is the whole reason
                    // the bound above exists.
                    break;
                }
                dropped++;
            }
            return dropped;
        }
    }
}
