using System;
using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>What is known about one optional mod this package has a position on.</summary>
    public sealed class IntegrationState
    {
        /// <summary>The register row this came from, so the readout and the register agree.</summary>
        public int RegisterRow;

        /// <summary>The Workshop package id, read from the register and never guessed.</summary>
        public string PackageId;

        /// <summary>
        /// The mod's own package identity as `About.xml` declares it. This is what
        /// `ModsConfig.IsActive` matches; the Workshop number above is the register's source id
        /// and never matches a loaded mod.
        /// </summary>
        public string ModPackageId;

        /// <summary>Key for the mod's name as the register records it.</summary>
        public string NameKey;

        /// <summary>Key for what this package does and does not do with it.</summary>
        public string PositionKey;

        /// <summary>Whether it is loaded right now.</summary>
        public bool Active;
    }

    /// <summary>
    /// **What optional mods are loaded, and what this package's position on each one is.**
    ///
    /// Rows 764, 765, 766 and 784 asked for vehicle and space logistics branches, VGE chapter
    /// hooks, and RWT feature detection with setup diagnostics. Reading the register's own
    /// instructions changed what *hook* had to mean, and it is worth recording why, because the
    /// obvious build would have violated guidance this project has already accepted.
    ///
    /// ## The register forbids patching all four, in its own words
    ///
    /// | Row | The register's integration approach |
    /// |---|---|
    /// | **247** VGE Chapter 1 | *"**No patch or code/assets copied.** Gate and coordinate progression stays Rimrooms-owned; treat VGE as separate optional orbital content behind DLC/mod checks."* |
    /// | **281** VGE Chapter 2 | *"**No patch or code/assets copied.** Keep Backrooms gate/operations independent; a VGE connected mission is only a future optional bridge **after verification**."* |
    /// | **11** Vehicle Framework | *"Keep the machine gate as the Backrooms entry point and preserve native gravship behavior; **do not add vehicles solely because the framework is installed**."* |
    /// | **196** RimWorld Together | *"Keep each company's facility, gate, discoveries, research, and ledger on its own branch. **Do not assume** custom dossier or gear transfers."* |
    ///
    /// So a hook here cannot be a patch, cannot copy anything, and cannot make a Rimrooms route
    /// depend on any of them. What is left — and what the rows actually ask for in their own
    /// words, *"logistics summary/operations links"* and *"feature detection and setup
    /// diagnostics"* — is **a read-only statement of what is installed and what this package
    /// does about it.**
    ///
    /// That is a smaller deliverable than it first looks and a more honest one. The player's
    /// real question about a 294-mod profile is *"does the mod I just installed do anything with
    /// this one, and will it break?"*, and until now the answer lived only in a register HTML
    /// file outside the game.
    ///
    /// ## Detection is by package id, read from the register
    ///
    /// `ModsConfig.IsActive(string id)` is Core's own answer, and the ids below are the
    /// register's `Workshop ID / package` column — **not remembered, and not inferred from a
    /// mod name**. A wrong id produces a silent *"not installed"* forever, which is exactly the
    /// class of defect this project has been caught by five times, so the proof pins every id
    /// against the register's own CSV.
    ///
    /// **Nothing here changes behaviour.** No route, gate, expedition, generation pass or work
    /// giver reads this class, because a detection layer that starts deciding things is how
    /// *"do not add vehicles solely because the framework is installed"* gets broken by
    /// accident. The only readers are the player-pressed adapters —
    /// <see cref="Company.CompanyVehicles"/> and the dossier exchange's provider refusal — and
    /// they read it only to choose which refusal to show or whether to open a provider's own
    /// screen.
    ///
    /// ## The third state row 784 asks for
    ///
    /// Row 784 wants *"unavailable/admin-disabled feature states"*. There are three honest
    /// states and the readout says which:
    ///
    /// * **not installed** — nothing to report;
    /// * **installed** — and this package's position on it, stated;
    /// * **installed, unverified in play** — which is **every one of them**, because no game has
    ///   ever been launched from this repository. Saying *"supported"* would be a claim nobody
    ///   has earned, and row 791 forbids exactly that kind of statement about RWT.
    ///
    /// ## Why this is one class for all four rather than four hooks
    ///
    /// Because the answer to all four is the same sentence with a different subject, and four
    /// copies of it would be four places to drift. `AllInOrder` is the whole surface.
    /// </summary>
    public static class InstalledIntegrations
    {
        /// <summary>
        /// The optional mods this package has a recorded position on, in register row order.
        ///
        /// Package ids are the register's own, from
        /// `docs/research/rimworld-server-mod-inventory.csv`. The proof reads that file and
        /// compares, so an id cannot drift from the row it claims to be.
        /// </summary>
        private static readonly IntegrationState[] Tracked =
        {
            new IntegrationState
            {
                RegisterRow = 11,
                PackageId = "3014915404",
                ModPackageId = "SmashPhil.VehicleFramework",
                NameKey = "RR_Integration_VehicleFrameworkName",
                PositionKey = "RR_Integration_VehicleFrameworkPosition",
            },
            new IntegrationState
            {
                RegisterRow = 196,
                PackageId = "3005289691",
                ModPackageId = "nova.rimworldtogether",
                NameKey = "RR_Integration_RimWorldTogetherName",
                PositionKey = "RR_Integration_RimWorldTogetherPosition",
            },
            new IntegrationState
            {
                RegisterRow = 247,
                PackageId = "3609835606",
                ModPackageId = "vanillaexpanded.gravship",
                NameKey = "RR_Integration_GravshipOneName",
                PositionKey = "RR_Integration_GravshipOnePosition",
            },
            new IntegrationState
            {
                RegisterRow = 249,
                PackageId = "3014906877",
                ModPackageId = "OskarPotocki.VanillaVehiclesExpanded",
                NameKey = "RR_Integration_VehiclesExpandedName",
                PositionKey = "RR_Integration_VehiclesExpandedPosition",
            },
            new IntegrationState
            {
                RegisterRow = 281,
                PackageId = "3799737423",
                ModPackageId = "vanillaexpanded.gravship2",
                NameKey = "RR_Integration_GravshipTwoName",
                PositionKey = "RR_Integration_GravshipTwoPosition",
            },
        };

        private static int cachedHash = int.MinValue;

        /// <summary>
        /// Every tracked mod with its live active state, refreshed when the installed list
        /// changes.
        ///
        /// Keyed on `ModLister.InstalledModsListHash`, which is Core's own answer to *"has the
        /// mod list changed"*. A player can enable a mod and restart into the same save, so a
        /// once-only read would go stale; asking Core every frame would be a string comparison
        /// per mod per frame on a readout nobody is looking at most of the time.
        /// </summary>
        public static IReadOnlyList<IntegrationState> AllInOrder()
        {
            int hash = ModLister.InstalledModsListHash(true);
            if (hash != cachedHash)
            {
                cachedHash = hash;
                for (int index = 0; index < Tracked.Length; index++)
                {
                    IntegrationState state = Tracked[index];
                    state.Active = !string.IsNullOrEmpty(state.ModPackageId) &&
                        ModsConfig.IsActive(state.ModPackageId);
                }
            }
            return Tracked;
        }

        /// <summary>How many of the tracked mods are loaded. Used by the readout's heading.</summary>
        public static int ActiveCount()
        {
            IReadOnlyList<IntegrationState> all = AllInOrder();
            int count = 0;
            for (int index = 0; index < all.Count; index++)
            {
                if (all[index].Active) { count++; }
            }
            return count;
        }

        /// <summary>
        /// Whether one tracked mod is loaded, by register row.
        ///
        /// By **row** rather than by package id, so a caller names the register entry it means
        /// and the register is the single source for the id. Returns false for a row this class
        /// does not track, rather than throwing: a question about an untracked mod has a
        /// truthful answer and it is *"this package has no position on that"*.
        /// </summary>
        public static bool ActiveRow(int registerRow)
        {
            IReadOnlyList<IntegrationState> all = AllInOrder();
            for (int index = 0; index < all.Count; index++)
            {
                if (all[index].RegisterRow == registerRow) { return all[index].Active; }
            }
            return false;
        }
    }
}
