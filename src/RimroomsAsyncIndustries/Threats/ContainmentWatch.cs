using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// What a branch is holding, and whether it is still holding it — **on every map the
    /// company owns**, not only the one the player happens to be looking at.
    ///
    /// ## Core already warns about containment, and that decided the whole shape of this
    ///
    /// The first design here was a set of alerts for low containment strength, high activity
    /// and an untended entity. **All three already exist in Core** and were found by
    /// enumerating its alert classes rather than assumed absent:
    /// `Alert_InsufficientContainmentStrength`, `Alert_DangerousActivity`,
    /// `Alert_EntityNeedsTend` and `Alert_NeedHoldingPlatform`. Shipping our own would have
    /// been a **second opinion beside a rule the player is already shown** — the exact defect
    /// this project asserts against every time it closes a presentation gap.
    ///
    /// So they were read instead, and every one of them opens the same way:
    ///
    /// <code>
    /// if (Find.CurrentMap == null) { return false; }
    /// ... Find.CurrentMap.listerThings ...
    /// </code>
    ///
    /// **Core's containment warnings are about the map on screen.** That is correct for
    /// RimWorld, where a colony is a map. It is wrong for this mod, whose entire premise is
    /// several live maps at once: a headquarters, the coordinates behind its gates, and any
    /// registered remote site. A player standing in a coordinate watching a crew work gets
    /// **no warning at all** that something is coming off a platform back home.
    ///
    /// That is the gap, it is genuinely ours, and it is the same gap the gate alerts closed at
    /// 0.10.5-dev by walking `Find.Maps` instead of reading one map.
    ///
    /// ## And it never overlaps Core, by construction
    ///
    /// Both alerts below **skip `Find.CurrentMap` entirely**. On the map you are looking at,
    /// Core's four alerts are the only voice; ours speaks only about the maps you are not
    /// looking at. Two alerts for one platform would teach a player to scroll past both, and
    /// the cheapest way to be sure that never happens is to make the two sets disjoint rather
    /// than to try to match Core's conditions exactly and hope they stay matched across a
    /// game update.
    ///
    /// ## Matched by capability, so it is not Anomaly-only by accident
    ///
    /// Holders are found through **`CompEntityHolder`**, an abstract comp in the always-present
    /// base assembly, rather than through `ThingDefOf.HoldingPlatform`. A modded holder
    /// carrying that comp is covered with nothing here naming it, and on an install without
    /// Anomaly the lister group is simply empty — an absent expansion is an empty world, not a
    /// condition, which is the same rule `MachineLoadingProvider` follows.
    ///
    /// ## Profile rows read before writing this
    ///
    /// `register-query.py family security` and `use RR-EVD`. Row **8 Anomaly** is *"optional
    /// native anomaly touchpoints; Rimrooms supplies its own Core threat, evidence, and
    /// containment loops"* — so nothing here may become the route through the campaign, and
    /// nothing does: these are warnings and a company procedure, and both are inert on a
    /// branch holding nothing. Row **140 Name Your Entities** is display naming only, and
    /// because the alerts report **culprits** rather than composing their own names, a renamed
    /// entity reads correctly for free. Row **138 Move Your Monolith** is a layout utility and
    /// touches no holder.
    ///
    /// Nothing is patched, nothing is required, and every mod may be absent.
    /// </summary>
    internal static class ContainmentWatch
    {
        /// <summary>
        /// A holder with an occupant, and what is true about it. Read once per tick into this
        /// shape so two alerts and the breach response cannot disagree about a platform.
        /// </summary>
        internal sealed class HolderState
        {
            internal Thing Holder;
            internal Pawn Occupant;
            internal Map Map;
            internal bool Escaping;
            internal bool Unpowered;
        }

        private static readonly List<HolderState> Cached = new List<HolderState>();
        private static int cachedTick = -1;
        private static Game cachedGame;

        /// <summary>
        /// Every occupied holder on every map the company owns, recomputed at most once per
        /// game tick.
        ///
        /// The cache is keyed on the tick **and the game object**, for the reason
        /// <see cref="Presentation.GateAlertScan"/> records: loading a second save that lands
        /// on the same tick as the first would otherwise hand back the previous game's
        /// despawned things, and a load always produces a new <see cref="Game"/>.
        /// </summary>
        internal static List<HolderState> OccupiedHolders()
        {
            Game game = Current.Game;
            int now = game == null || Find.TickManager == null ? -1 : Find.TickManager.TicksGame;
            if (now == cachedTick && ReferenceEquals(game, cachedGame) && now >= 0)
            { return Cached; }

            cachedTick = now;
            cachedGame = game;
            Cached.Clear();
            if (game == null) { return Cached; }

            RimroomsCampaignComponent campaign = game.GetComponent<RimroomsCampaignComponent>();
            List<Map> maps = Find.Maps;
            if (campaign == null || !campaign.CanOperate || maps == null) { return Cached; }

            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map.listerThings == null || !campaign.OwnsMap(map)) { continue; }
                Collect(map);
            }
            return Cached;
        }

        private static void Collect(Map map)
        {
            List<Thing> holders = map.listerThings.ThingsInGroup(ThingRequestGroup.EntityHolder);
            if (holders == null) { return; }
            for (int index = 0; index < holders.Count; index++)
            {
                Thing holder = holders[index];
                if (holder == null || holder.Destroyed || !holder.Spawned || holder.Map != map)
                { continue; }
                CompEntityHolder comp = holder.TryGetComp<CompEntityHolder>();
                if (comp == null) { continue; }
                Pawn occupant = comp.HeldPawn;
                if (occupant == null) { continue; }

                CompHoldingPlatformTarget target = occupant.TryGetComp<CompHoldingPlatformTarget>();
                CompPowerTrader power = holder.TryGetComp<CompPowerTrader>();
                Cached.Add(new HolderState
                {
                    Holder = holder,
                    Occupant = occupant,
                    Map = map,
                    // Core's own flag, set by the entity's own comp when it starts to get out.
                    // Nothing here decides that a subject is escaping; it reports that Core did.
                    Escaping = target != null && target.isEscaping,
                    // A holder that needs power and has none is not holding anything for long.
                    // `PowerOn` is false while unpowered whether the cause is a cut wire, a
                    // flat battery or a thrown switch, so one test covers all three.
                    Unpowered = power != null && !power.PowerOn
                });
            }
        }

        /// <summary>
        /// Whether anything the company holds anywhere is currently getting out. Used by the
        /// breach response, which is colony-wide by nature: a subject loose on a coordinate is
        /// a reason to cut the connection to that coordinate.
        /// </summary>
        internal static bool AnyBreach()
        {
            List<HolderState> holders = OccupiedHolders();
            for (int index = 0; index < holders.Count; index++)
            {
                if (holders[index].Escaping) { return true; }
            }
            return false;
        }
    }
}
