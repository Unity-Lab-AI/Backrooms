using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Gate;
using RimroomsAsyncIndustries.Portals;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// Something standing on your map walks out through an open gate.
    ///
    /// **Owner direction, 2026-10-06, verbatim:** *"not anyone in base, but anyone on your map.. a
    /// enemy can break in and cross the gate to get valuables and members"*, then *"hold up now
    /// friendlys can too"*.
    ///
    /// ## This is the direction that turns an open window into a security decision
    ///
    /// Until now a connection cost power and attention. It is now **a hole in the base that something
    /// can go through**, which is the strongest idea in the owner's direction: it gives the gate's
    /// duration a second meaning that nothing had to be invented for.
    ///
    /// ## It is `GateIncursion` with the ends swapped, deliberately
    ///
    /// Same six steps — tick on the gate, find a candidate at the doorstep, ask the policy, preflight
    /// the arrival cell, transfer with rollback, announce. Reusing that shape matters for two reasons
    /// beyond economy, and neither is obvious:
    ///
    /// * its `FindAtDoorstep` takes candidates in a **fixed radial order**, so *"the same situation
    ///   resolves the same way on every machine"* — a coordinate is regenerated from a seed and two
    ///   players must see the same thing happen;
    /// * its `Transfer` **puts the pawn back if the spawn fails**, because *"a vanished hostile is a
    ///   save with a hole in it, and the player would never know."*
    ///
    /// ## THE MOTIVE IS THE BOUND, and it came out of the owner's own sentence
    ///
    /// Incursion's five axes do not transfer: coordinate band and gate tier describe how dangerous the
    /// far side has become, which says nothing about whether a raider in your base should walk through
    /// a door. *"to get valuables and members"* is the bound instead — **nothing crosses unless there
    /// is loot or a carryable person over there.**
    ///
    /// That is self-limiting in a way a tuned number is not. It scales with what the player chose to
    /// keep down there, and **it makes the risk legible**: store nothing beyond a gate and you are
    /// never raided through one; build a vault down there and you have built a target, and you can see
    /// that you did.
    ///
    /// ## And the cap is the doorstep, not once per opening
    ///
    /// Inbound is capped at one because the player is being attacked at home and *"closing and
    /// reopening is what resets it"* is the learnable rule. Outbound has a different fairness shape: a
    /// raid is a group, and one raider peeling off through a gate while nineteen ignore it reads as a
    /// bug rather than a rule. **So the player's defence is the cap** — only pawns that actually reach
    /// the threshold cross, and a raid stopped in the killbox never gets near it.
    ///
    /// ## Counterplay, which already existed
    ///
    /// `NativeGateKillSwitch` cuts a connection deliberately, so **close the gate** answers this
    /// exactly as it already answers incursion. And `GateWidth`/`GateOpeningDepth` feed
    /// `FitFailureKey`, so *"a narrow gate is a real defensive choice rather than the starter option"*
    /// gains a second reason to be true.
    /// </summary>
    internal static class GateEgress
    {
        /// <summary>Checked once a game-second. Nothing here is urgent.</summary>
        private const int CheckInterval = 60;

        /// <summary>
        /// How close to the near threshold counts as *at the doorway*. One step, exactly as inbound:
        /// something has to actually reach the doorway, which is what gives the player the chance to
        /// close the gate first.
        /// </summary>
        private const int DoorstepRadius = 1;

        /// <summary>
        /// What the far side has to be worth before anybody breaks into it.
        ///
        /// **A market value, because that is the question a raider asks** and Core already answers it
        /// per thing. Set at a level a bare coordinate never reaches and a stocked one passes easily:
        /// the point is not to tune a difficulty, it is to make *empty* mean *not worth it*.
        /// </summary>
        private const float LootWorthCrossing = 400f;

        internal static void Tick(CompRimroomsGate gate)
        {
            if (gate == null || gate.parent == null || !gate.parent.Spawned) { return; }
            if (Find.TickManager == null || Find.TickManager.TicksGame % CheckInterval != 0) { return; }
            if (string.IsNullOrEmpty(gate.PortalConnectionId) || string.IsNullOrEmpty(gate.PortalOpeningId)) { return; }
            if (gate.IsEmergency || gate.KillSwitchThrown) { return; }

            RimroomsPortalNetwork network = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsPortalNetwork>();
            RimroomsCampaignComponent campaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (network == null || network.HasStateFault || campaign == null || !campaign.CanOperate) { return; }

            PortalConnectionRecord edge = network.Find(gate.PortalConnectionId);
            if (edge == null || edge.First == null || edge.Second == null ||
                edge.First.Anchor != gate.parent) { return; }

            Map homeMap = edge.First.Map;
            Map farMap = edge.Second.Map;
            if (homeMap == null || farMap == null || homeMap == farMap ||
                !Find.Maps.Contains(homeMap) || !Find.Maps.Contains(farMap)) { return; }

            // **The motive, asked once before anybody is considered.** An empty coordinate is not
            // worth breaking into, so this is the cheap gate in front of the pawn scan rather than a
            // condition tested per candidate.
            bool loot = WorthCrossingFor(farMap, out bool people);
            if (!loot && !people) { return; }

            Pawn traveller = FindAtDoorstep(homeMap, edge.First.ApproachCell, gate);
            if (traveller == null) { return; }

            IntVec3 arrival = edge.Second.ApproachCell;
            if (!CanArriveAt(traveller, farMap, arrival)) { return; }
            bool hostile = traveller.Faction != null && traveller.Faction.HostileTo(Faction.OfPlayer);
            if (!Transfer(traveller, farMap, arrival, hostile)) { return; }
            Announce(traveller, farMap, gate, hostile);
        }

        /// <summary>
        /// Whether the far map holds anything worth crossing for.
        ///
        /// **Two separate answers because the owner named two things**, *"valuables and members"*, and
        /// they are not interchangeable: a coordinate holding only people is a kidnap target with
        /// nothing to steal, and one holding only goods is the reverse.
        ///
        /// Counted off `listerThings`, stopping at the first qualifying find, so this is cheap on a
        /// map with anything at all on it and only expensive on a bare one — which is the map where
        /// the answer is no and the scan was the point.
        /// </summary>
        private static bool WorthCrossingFor(Map farMap, out bool people)
        {
            people = false;
            if (farMap == null) { return false; }
            // People first: a colonist standing in a coordinate is the loudest reason to go in.
            if (farMap.mapPawns != null)
            {
                IReadOnlyList<Pawn> present = farMap.mapPawns.FreeColonistsAndPrisonersSpawned;
                for (int index = 0; index < present.Count; index++)
                {
                    if (present[index] != null && !present[index].Dead) { people = true; break; }
                }
            }
            List<Thing> things = farMap.listerThings.AllThings;
            for (int index = 0; index < things.Count; index++)
            {
                Thing thing = things[index];
                if (thing == null || thing.def == null || thing is Pawn) { continue; }
                if (thing.def.category != ThingCategory.Item) { continue; }
                if (thing.MarketValue * thing.stackCount >= LootWorthCrossing) { return true; }
            }
            return false;
        }

        /// <summary>
        /// The first thing at the near doorway the policy will let out.
        ///
        /// Fixed radial order, exactly as inbound, so the same situation resolves the same way on every
        /// machine. **Hostiles are preferred over friendlies when both are standing there**, because a
        /// raider going through is the event the player needs to know about and a visitor wandering
        /// after it is a footnote.
        /// </summary>
        private static Pawn FindAtDoorstep(Map homeMap, IntVec3 approach, CompRimroomsGate gate)
        {
            if (!approach.IsValid || !approach.InBounds(homeMap)) { return null; }
            Pawn friendly = null;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(approach, DoorstepRadius, true))
            {
                if (!cell.InBounds(homeMap)) { continue; }
                List<Thing> things = cell.GetThingList(homeMap);
                for (int index = 0; index < things.Count; index++)
                {
                    Pawn candidate = things[index] as Pawn;
                    if (candidate == null) { continue; }
                    if (PortalTraversalPolicy.OutboundCrossingFailureKey(candidate, gate) != null)
                    { continue; }
                    if (candidate.Faction != null && candidate.Faction.HostileTo(Faction.OfPlayer))
                    { return candidate; }
                    if (friendly == null) { friendly = candidate; }
                }
            }
            return friendly;
        }

        private static bool CanArriveAt(Pawn pawn, Map map, IntVec3 cell)
        {
            if (pawn == null || map == null || !cell.IsValid || !cell.InBounds(map) || !cell.Standable(map))
            { return false; }
            if (!GenSpawn.CanSpawnAt(pawn.def, cell, map, pawn.Rotation, canWipeEdifices: false)) { return false; }
            List<Thing> existing = cell.GetThingList(map);
            for (int index = 0; index < existing.Count; index++)
            {
                if (existing[index] is Pawn || GenSpawn.SpawningWipes(pawn.def, existing[index].def))
                { return false; }
            }
            return true;
        }

        /// <summary>
        /// Move it, and give it something to do when it lands.
        ///
        /// Preflight is complete before anything is despawned, and a spawn that somehow fails puts the
        /// pawn back where it stood — **a vanished raider is a save with a hole in it**, and the player
        /// would never know.
        ///
        /// **The lord is the half that makes this a feature rather than a teleport.** A `Lord` is per
        /// map, so a transferred pawn arrives with no duty at all; this is the same defect
        /// `GateIncursion` shipped with until this batch. A hostile gets an assault lord with
        /// `canSteal` and `canKidnap` — the owner's *"valuables and members"* as parameters — and a
        /// friendly gets `LordJob_DefendPoint`, because a visitor that wandered through a door has not
        /// decided to attack anybody and giving it an assault job would invent a betrayal.
        /// </summary>
        private static bool Transfer(Pawn pawn, Map map, IntVec3 cell, bool hostile)
        {
            Map origin = pawn.Map;
            IntVec3 originCell = pawn.Position;
            Rot4 rotation = pawn.Rotation;
            try
            {
                pawn.DeSpawn();
                Thing spawned = GenSpawn.Spawn(pawn, cell, map, rotation, WipeMode.Vanish);
                if (spawned == pawn && pawn.Spawned && pawn.Map == map)
                {
                    GiveArrivalLord(pawn, map, cell, hostile);
                    return true;
                }
            }
            catch (Exception error)
            {
                Log.Error("[Rimrooms][Threat] Egress transfer failed; returning the traveller to where "
                    + "it stood: " + error);
            }
            if (!pawn.Spawned && origin != null && Find.Maps.Contains(origin))
            { GenSpawn.Spawn(pawn, originCell, origin, rotation, WipeMode.Vanish); }
            return false;
        }

        private static void GiveArrivalLord(Pawn pawn, Map map, IntVec3 cell, bool hostile)
        {
            if (pawn == null || map == null || pawn.Faction == null) { return; }
            if (pawn.GetLord() != null) { return; }
            try
            {
                LordJob job = hostile
                    ? (LordJob)new LordJob_AssaultColony(pawn.Faction, canKidnap: true,
                        canTimeoutOrFlee: true, sappers: false, useAvoidGridSmart: false, canSteal: true)
                    : new LordJob_DefendPoint(cell, 12f);
                LordMaker.MakeNewLord(pawn.Faction, job, map, new List<Pawn> { pawn });
            }
            catch (Exception error)
            {
                Log.Warning("[Rimrooms][Threat] Could not give a crossing traveller a lord; it will "
                    + "fall back to its own think tree: " + error);
            }
        }

        /// <summary>
        /// Say so, every time, and name who went.
        ///
        /// **A friendly crossing is lettered as loudly as a hostile one**, which is the brief's own
        /// decision: a guest who dies in a coordinate is a death the player caused by leaving a hole
        /// open, and **the one thing that must not happen is a faction penalty arriving with no story
        /// the player can connect it to.**
        /// </summary>
        private static void Announce(Pawn traveller, Map map, CompRimroomsGate gate, bool hostile)
        {
            Find.LetterStack.ReceiveLetter(
                (hostile ? "RR_Egress_HostileLabel" : "RR_Egress_FriendlyLabel").Translate(),
                (hostile ? "RR_Egress_HostileText" : "RR_Egress_FriendlyText")
                    .Translate(traveller.LabelShortCap, gate.parent.LabelCap),
                hostile ? LetterDefOf.ThreatBig : LetterDefOf.NeutralEvent,
                new TargetInfo(traveller.Position, map));
            Audio.RimroomsAudio.Play("RR_GateWarning", map, traveller.Position, false);
        }
    }
}
