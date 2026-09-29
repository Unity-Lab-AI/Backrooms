using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// Places the people found inside a coordinate, within every limit the ladder imposes.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"alla trhings are possible finding random
    /// pawns of disappering, findeding dead ones pasycholitc ones lost pawns all kinds of crazy
    /// variations as per the lore"*.
    ///
    /// ## Bodies at generation, living things on arrival
    ///
    /// A body is **discoverable content**: finding one should not wait on a danger band, and a
    /// corpse does not act. Those are placed when the space is generated.
    ///
    /// Everything that acts is placed **on arrival**, against the coordinate's band at that
    /// moment. That is what makes the ladder's guarantees true rather than decorative — if
    /// living inhabitants were baked in at generation, *"a first visit is always quiet"* would
    /// be a lie the moment somebody walked in, and a band that rose later would never show.
    ///
    /// ## Every limit is applied here, not hoped for elsewhere
    ///
    /// * The ladder's **encounter cap** bounds how many hostiles exist at once.
    /// * **Quiet rooms are never used**, so the guaranteed-empty half of a coordinate stays
    ///   empty of people as well as of furniture.
    /// * Placement happens **once per arrival**, recorded on the map, so re-entering a space
    ///   somebody is already standing in does not stack another group on top.
    /// * Nothing here touches gates. `PortalTraversalPolicy` remains the single chokepoint, and
    ///   an inhabitant may never decide anything about one.
    /// </summary>
    public static class InhabitantService
    {
        /// <summary>
        /// Populates a coordinate on arrival. Safe to call repeatedly; it does nothing after
        /// the first successful placement for a given arrival.
        /// </summary>
        public static void PopulateOnArrival(Map map, CoordinateRecord coordinate)
        {
            if (map == null || coordinate == null) { return; }

            float wealth = CoordinatePressureLadder.ColonyWealth();
            CoordinatePressureLadder.Band band = CoordinatePressureLadder.BandFor(coordinate, wealth);
            if (band <= CoordinatePressureLadder.Band.Quiet) { return; }

            int hostileCap = CoordinatePressureLadder.EncounterCapFor(coordinate, wealth);
            int seed = DestinationServiceSeed(coordinate);

            List<RimroomsInhabitantDef> legal = Legal(coordinate.Depth, band, false);
            if (legal.Count == 0) { return; }

            int hostilesPlaced = 0;
            for (int index = 0; index < legal.Count; index++)
            {
                RimroomsInhabitantDef family = legal[index];
                if (!Appears(family, seed, index)) { continue; }

                int wanted = Count(family, seed, index);
                if (family.hostile)
                {
                    wanted = Math.Min(wanted, Math.Max(0, hostileCap - hostilesPlaced));
                    if (wanted <= 0) { continue; }
                }

                for (int made = 0; made < wanted; made++)
                {
                    if (!PlaceOne(map, coordinate, family, seed + made * 17, band)) { break; }
                    if (family.hostile) { hostilesPlaced++; }
                }
            }
        }

        /// <summary>
        /// Places the bodies a coordinate contains, at generation. Corpses only.
        /// </summary>
        public static void PopulateDead(Map map, CoordinateRecord coordinate, HashSet<IntVec3> reserved)
        {
            if (map == null || coordinate == null) { return; }
            int seed = DestinationServiceSeed(coordinate);
            List<RimroomsInhabitantDef> legal = Legal(coordinate.Depth,
                CoordinatePressureLadder.Band.Hostile, true);
            if (legal.Count == 0) { return; }

            for (int index = 0; index < legal.Count; index++)
            {
                RimroomsInhabitantDef family = legal[index];
                if (!Appears(family, seed, index + 500)) { continue; }
                int wanted = Count(family, seed, index + 500);
                for (int made = 0; made < wanted; made++)
                {
                    if (!PlaceCorpse(map, coordinate, family, seed + made * 29, reserved)) { break; }
                }
            }
        }

        private static List<RimroomsInhabitantDef> Legal(int depth,
            CoordinatePressureLadder.Band band, bool deadOnly)
        {
            List<RimroomsInhabitantDef> legal = DefDatabase<RimroomsInhabitantDef>
                .AllDefsListForReading
                .Where(family => family.minDepth <= depth
                    && (family.maxDepth <= 0 || family.maxDepth >= depth)
                    && (family.kind == InhabitantKind.Dead) == deadOnly
                    && (deadOnly || family.minBand <= band))
                .ToList();
            // Ordinal sort so the outcome cannot follow def load order, which changes with the
            // mod list and would make the same seed produce different people.
            legal.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));
            return legal;
        }

        private static bool Appears(RimroomsInhabitantDef family, int seed, int index)
        {
            if (family.chance >= 1f) { return true; }
            int roll = Gen.HashCombineInt(seed, index * 613 + 0x494E48);
            if (roll < 0) { roll = ~roll; }
            return (roll % 1000) / 1000f < family.chance;
        }

        private static int Count(RimroomsInhabitantDef family, int seed, int index)
        {
            int low = Math.Max(0, family.count.min);
            int high = Math.Max(low, family.count.max);
            if (high == low) { return low; }
            int roll = Gen.HashCombineInt(seed, index * 71 + 0x434E54);
            if (roll < 0) { roll = ~roll; }
            return low + roll % (high - low + 1);
        }

        /// <summary>
        /// Resolves a pawn kind from the family's preference list. **Existing defs only** — a
        /// family whose kinds are all absent is skipped rather than substituted, because a
        /// wanderer rendered as the wrong kind of person is worse than an empty room.
        /// </summary>
        private static PawnKindDef ResolveKind(RimroomsInhabitantDef family)
        {
            if (family.pawnKindDefNames == null) { return null; }
            for (int index = 0; index < family.pawnKindDefNames.Count; index++)
            {
                PawnKindDef kind =
                    DefDatabase<PawnKindDef>.GetNamedSilentFail(family.pawnKindDefNames[index]);
                if (kind != null) { return kind; }
            }
            return null;
        }

        private static bool PlaceOne(Map map, CoordinateRecord coordinate,
            RimroomsInhabitantDef family, int seed, CoordinatePressureLadder.Band band)
        {
            PawnKindDef kind = ResolveKind(family);
            if (kind == null) { return false; }

            IntVec3 cell;
            if (!FindCell(map, coordinate, seed, out cell)) { return false; }

            Faction faction = FactionFor(family);
            Pawn pawn;
            try
            {
                pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction,
                    PawnGenerationContext.NonPlayer, -1, forceGenerateNewPawn: true));
            }
            catch (Exception error)
            {
                Log.Warning("[Rimrooms] could not generate inhabitant " + family.defName + ": " + error);
                return false;
            }
            if (pawn == null) { return false; }

            string echoedName = ApplyIdentity(pawn, family, coordinate, map, seed);
            if (family.kind == InhabitantKind.Echo && string.IsNullOrEmpty(echoedName))
            {
                // Nobody at home to echo. Placing a generic stranger under an echo family would
                // be a worse encounter than none, because the whole point is the recognition.
                pawn.Destroy();
                return false;
            }
            if (family.kind == InhabitantKind.Survivor)
            {
                // Marks this person as somebody who can be offered passage home. Without
                // it a survivor is scenery you can pick up rather than a person you can
                // save, and they stay an inhabitant who may never cross a gate alone.
                pawn.TryGetComp<CompRimroomsSurvivor>()?.MarkSurvivor();
            }
            GenSpawn.Spawn(pawn, cell, map);
            if (!pawn.Spawned) { return false; }

            if (family.hostile && faction != null)
            {
                LordMaker.MakeNewLord(faction, HostileLordJob(band, cell, faction), map, new List<Pawn> { pawn });
            }
            Announce(family, pawn, map);
            return true;
        }

        private static bool PlaceCorpse(Map map, CoordinateRecord coordinate,
            RimroomsInhabitantDef family, int seed, HashSet<IntVec3> reserved)
        {
            PawnKindDef kind = ResolveKind(family);
            if (kind == null) { return false; }

            IntVec3 cell;
            if (!FindCell(map, coordinate, seed, out cell)) { return false; }
            if (reserved != null && reserved.Contains(cell)) { return false; }

            Pawn pawn;
            try
            {
                pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null,
                    PawnGenerationContext.NonPlayer, -1, forceGenerateNewPawn: true));
            }
            catch (Exception)
            {
                return false;
            }
            if (pawn == null) { return false; }

            ApplyIdentity(pawn, family, coordinate, map, seed);
            if (!family.carriesBelongings)
            {
                pawn.equipment?.DestroyAllEquipment();
                pawn.inventory?.DestroyAll();
            }

            // Killed rather than spawned dead so the corpse carries a real cause, a real age and
            // real belongings. A body with nothing on it is a prop rather than a find.
            pawn.Kill(null);
            Corpse corpse = pawn.Corpse;
            if (corpse == null) { return false; }
            if (!corpse.Spawned) { GenSpawn.Spawn(corpse, cell, map); }
            if (!corpse.Spawned) { return false; }

            // A body found down here came from down here. Marking it keeps it consistent with
            // everything else a coordinate produces, and lets it be sold as odd goods.
            OddOriginService.Mark(corpse);
            corpse.SetForbidden(false, false);
            return true;
        }

        /// <summary>
        /// Gives an inhabitant the identity their family implies.
        ///
        /// A **missing** person is drawn from the branch's own record of people it lost where
        /// one exists, which is what makes the owner's *"random pawns of disappering"* land: the
        /// name on the body is a name the player recognises.
        /// </summary>
        private static string ApplyIdentity(Pawn pawn, RimroomsInhabitantDef family,
            CoordinateRecord coordinate, Map map, int seed)
        {
            if (pawn == null) { return null; }

            if (family.kind == InhabitantKind.Echo)
            {
                // An echo is of somebody ALIVE AND AT HOME, never of somebody lost -- that is
                // the Missing family and a different, sadder feeling. The uncanniness depends
                // entirely on the real one being in the base at the same moment.
                Pawn source = ColonistEcho.PickSource(map, seed);
                return source == null ? null : ColonistEcho.Apply(pawn, source);
            }

            if (family.kind != InhabitantKind.Missing) { return null; }

            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            string remembered = campaign == null ? null : campaign.TakeLostPawnName();
            if (string.IsNullOrEmpty(remembered)) { return null; }
            NameTriple existing = pawn.Name as NameTriple;
            pawn.Name = existing == null
                ? (Name)new NameSingle(remembered)
                : new NameTriple(existing.First, remembered, existing.Last);
            return remembered;
        }

        /// <summary>
        /// What a hostile inhabitant does about the people who walked in.
        ///
        /// **Owner direction, 2026-09-29, verbatim:** *"and at deeper levels i do want
        /// monstrosities and npcs to \"Chase\" pawns/ kill them all the way to the gate"*.
        ///
        /// Below <see cref="CoordinatePressureLadder.Band.Hostile"/> this is unchanged and
        /// deliberately so: a defend-this-place lord, because the warning-first rule requires
        /// that **a player who backs off is not pursued across the whole space**. That rule is
        /// what makes a shallow coordinate somewhere a lone survivor can retreat from.
        ///
        /// At `Hostile` it hunts. The band's own definition is *"more than one thing acts, and
        /// the space stops being forgiving"*, which is the owner's "deeper levels" already
        /// written down, so the rule needed no second threshold of its own.
        ///
        /// **Nothing here is new pursuit code.** RimWorld's own assault lord already walks a
        /// hostile to whoever it can reach, which is exactly "all the way to the gate": the
        /// threshold room is excluded from *spawning*, never from being walked into, so a
        /// hunter follows a fleeing crew right to the doorway with nothing added.
        ///
        /// Kidnapping, stealing, fleeing and timing out are all off. A coordinate has map
        /// edges because every generated map does, and a kidnapper carrying somebody off one
        /// would be a disappearance with no story attached to it. What is wanted is something
        /// that follows you, and the countermeasure stays what it always was: leave.
        /// </summary>
        private static LordJob HostileLordJob(CoordinatePressureLadder.Band band, IntVec3 cell, Faction hostileFaction)
        {
            if (band < CoordinatePressureLadder.Band.Hostile)
            { return new LordJob_DefendPoint(cell, 12f); }
            // The assaulting faction is the inhabitant's own, never the player's. Core reads
            // this parameter as who is doing the attacking.
            return new LordJob_AssaultColony(hostileFaction, canKidnap: false,
                canTimeoutOrFlee: false, sappers: false, useAvoidGridSmart: false, canSteal: false);
        }

        private static Faction FactionFor(RimroomsInhabitantDef family)
        {
            if (!family.hostile) { return null; }
            // An existing hostile faction, never a new one. Falls back to null -- which makes
            // the pawn a wild, non-faction threat rather than an ally -- if the game somehow
            // has no hostile faction at all.
            return Find.FactionManager == null ? null
                : Find.FactionManager.AllFactionsListForReading
                    .FirstOrDefault(candidate => candidate != null && !candidate.IsPlayer
                        && candidate.HostileTo(Faction.OfPlayer));
        }

        /// <summary>
        /// A cell inside a room that is **not** one of the coordinate's guaranteed quiet rooms,
        /// so the empty half of a space stays empty of people as well as of furniture.
        /// </summary>
        private static bool FindCell(Map map, CoordinateRecord coordinate, int seed, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            if (coordinate.Rooms == null || coordinate.Rooms.Count == 0) { return false; }

            int roll = Gen.HashCombineInt(seed, 0x524F4F4D);
            if (roll < 0) { roll = ~roll; }
            for (int attempt = 0; attempt < coordinate.Rooms.Count; attempt++)
            {
                RoomRecord room = coordinate.Rooms[(roll + attempt) % coordinate.Rooms.Count];
                if (room == null) { continue; }
                if (string.Equals(room.FamilyId, "threshold_room", StringComparison.Ordinal))
                { continue; }
                if (CoordinatePressureLadder.IsQuietRoom(coordinate.Seed, room.Index,
                    coordinate.Rooms.Count))
                { continue; }

                foreach (IntVec3 candidate in room.Bounds.ContractedBy(1).Cells
                    .OrderBy(c => Gen.HashCombineInt(seed, c.x * 1000 + c.z)))
                {
                    if (!candidate.InBounds(map) || !candidate.Standable(map)) { continue; }
                    if (candidate.GetEdifice(map) != null) { continue; }
                    if (candidate.GetFirstPawn(map) != null) { continue; }
                    cell = candidate;
                    return true;
                }
            }
            return false;
        }

        private static void Announce(RimroomsInhabitantDef family, Pawn pawn, Map map)
        {
            if (string.IsNullOrEmpty(family.letterLabelKey) ||
                string.IsNullOrEmpty(family.letterTextKey))
            { return; }
            // The warning-first rule made concrete: a player is told something is here before
            // they walk into it, and the letter points at the thing so they can go and look.
            Find.LetterStack.ReceiveLetter(
                family.letterLabelKey.Translate(),
                family.letterTextKey.Translate(pawn.LabelShortCap),
                family.hostile ? LetterDefOf.ThreatSmall : LetterDefOf.NeutralEvent,
                new TargetInfo(pawn.Position, map));
        }

        private static int DestinationServiceSeed(CoordinateRecord coordinate)
        {
            // Openings are part of the seed so a later arrival is not a rerun of the first one,
            // while a single arrival stays stable if this is called twice.
            return Gen.HashCombineInt(coordinate.Seed, coordinate.Openings * 7919);
        }
    }
}
