using System;
using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Economy;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// Fires the things that *happen* in a coordinate, within the same limits as the things
    /// that are *in* one.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"even wild waky carzxzy creepy things when u
    /// add places and events"*. Places shipped in 0.7.9-dev; this is the events half.
    ///
    /// ## Bounded per opening, and recorded
    ///
    /// At most <see cref="MaxEventsPerOpening"/> fire in a single visit — or
    /// <see cref="QuietProtocolEventsPerOpening"/> for a branch that has earned the quiet
    /// protocol — and a one-shot event
    /// is written to the coordinate so a revisit does not replay it. That is the same
    /// resume-rather-than-reroll rule the escalation ladder follows, applied to events: a space
    /// a player knows should not perform its party trick every single time they walk in.
    ///
    /// ## Nothing here can trap anybody
    ///
    /// **The threshold room is excluded from every effect**, always. No event damages a pawn,
    /// destroys a thing, or blocks a route. That is the frozen "no unavoidable instant failure"
    /// rule made concrete rather than promised: whatever happens, walking back out is still
    /// possible, and every effect has an answer the player can actually perform.
    /// </summary>
    public static class AnomalyEventService
    {
        /// <summary>How many events may fire in one visit.</summary>
        public const int MaxEventsPerOpening = 2;

        /// <summary>
        /// The ceiling once **RR_Cap_QuietProtocol** (Entities, tier 5) is held: one event per
        /// opening rather than two.
        ///
        /// ## This project is the only one in the tree that buys safety by subtracting content,
        /// and the owner was shown that before approving it
        ///
        /// The T5 sweep attached a reservation to this candidate rather than recommending it
        /// outright: *"Every other project on this list adds a capability; this one removes
        /// encounters."* It is still honest — a branch that has written procedure about what lives
        /// down there has earned fewer surprises per visit — but it is the one tier where the
        /// player's reward is less happening, so the subtraction is bounded at one rather than zero.
        /// **An opening where nothing can happen is not a quieter coordinate, it is a different
        /// game**, and the band ladder already guarantees the quiet case: a first visit is always
        /// <see cref="CoordinatePressureLadder.Band.Quiet"/> and a Quiet band fires nothing at all.
        ///
        /// ## And it does NOT touch `QuietRoomFraction`, which the owner confirmed at a second fork
        ///
        /// The sweep offered either constant and recommended this one: *"The first is pacing; the
        /// second is a promise."* `CoordinatePressureLadder.QuietRoomFraction` is half of the
        /// solo-survivability guarantee — *half of every coordinate's rooms bare by count rather
        /// than by chance* — and **a research project that moves a guarantee turns an absolute into
        /// a tech gate.** That is a rule rather than a note:
        /// `check-standalone-guarantee.py` refuses a build where the deciding function reads a
        /// capability at all.
        /// </summary>
        public const int QuietProtocolEventsPerOpening = 1;

        /// <summary>
        /// How many events may fire in this branch's openings, as it currently stands.
        ///
        /// A null campaign answers with the base ceiling rather than the better one: not knowing
        /// what a branch has learned is not the same as knowing it has learned this.
        /// </summary>
        private static int EventCeiling()
        {
            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            return campaign != null && campaign.HasCapability("RR_Cap_QuietProtocol")
                ? QuietProtocolEventsPerOpening
                : MaxEventsPerOpening;
        }

        /// <summary>
        /// Considers firing events for an arrival. Called once when a coordinate becomes
        /// occupied, alongside inhabitant placement.
        /// </summary>
        public static void OnArrival(Map map, CoordinateRecord coordinate)
        {
            if (map == null || coordinate == null) { return; }

            float wealth = CoordinatePressureLadder.ColonyWealth();
            CoordinatePressureLadder.Band band = CoordinatePressureLadder.BandFor(coordinate, wealth);
            if (band <= CoordinatePressureLadder.Band.Quiet) { return; }

            int seed = Gen.HashCombineInt(coordinate.Seed, coordinate.Openings * 104729);
            // **DRAWN AGAINST WHAT THIS LEVEL CAN REACH, NOT AGAINST ITS DOORSTEP.** Owner, after
            // walking a first level end to end: *"i explored it all and there were zero weird
            // events or people"*. Every event def declares minDepth 2 or more and this filtered
            // on `coordinate.Depth`, so a depth-1 coordinate produced an empty list and nothing
            // could ever happen on it. The reach is the coordinate's depth plus the distance a
            // player can walk from the spawn hall -- the same rule the dressing, the inhabitants
            // and the wall material now use.
            int reach = InhabitantService.ReachOf(coordinate);
            List<RimroomsAnomalyEventDef> legal = DefDatabase<RimroomsAnomalyEventDef>
                .AllDefsListForReading
                .Where(candidate => candidate.minDepth <= reach
                    && (candidate.maxDepth <= 0 || candidate.maxDepth >= coordinate.Depth)
                    && candidate.minBand <= band
                    && (candidate.repeatable || !coordinate.HasFiredEvent(candidate.defName)))
                .ToList();
            if (legal.Count == 0) { return; }

            // Ordinal sort so the outcome cannot follow def load order, which changes with the
            // mod list and would make the same seed produce different events.
            legal.Sort((left, right) => string.CompareOrdinal(left.defName, right.defName));

            int ceiling = EventCeiling();
            int fired = 0;
            for (int attempt = 0; attempt < legal.Count && fired < ceiling; attempt++)
            {
                int roll = Gen.HashCombineInt(seed, attempt * 7717);
                if (roll < 0) { roll = ~roll; }
                RimroomsAnomalyEventDef chosen = Pick(legal, roll);
                if (chosen == null) { break; }
                legal.Remove(chosen);

                if (!Fire(map, coordinate, chosen)) { continue; }
                if (!chosen.repeatable) { coordinate.NoteEventFired(chosen.defName); }
                fired++;
            }
        }

        private static RimroomsAnomalyEventDef Pick(List<RimroomsAnomalyEventDef> legal, int roll)
        {
            if (legal.Count == 0) { return null; }
            float total = legal.Sum(candidate => Math.Max(0.0001f, candidate.weight));
            float pick = (roll % 100000) / 100000f * total;
            for (int index = 0; index < legal.Count; index++)
            {
                pick -= Math.Max(0.0001f, legal[index].weight);
                if (pick <= 0f) { return legal[index]; }
            }
            return legal[legal.Count - 1];
        }

        private static bool Fire(Map map, CoordinateRecord coordinate, RimroomsAnomalyEventDef definition)
        {
            if (!FireEffect(map, RoomCells(map, coordinate).ToList(), definition.effect, definition.magnitude))
            { return false; }

            // **WHOSE VOICE IT IS, and it is somebody this branch knows.** A fragment from
            // nobody is atmosphere; a fragment naming a colonist who is standing in the
            // base right now is the owner's *"echos of thier inhabitance in weird ways"*.
            // Null for every other effect, and `Announce` then behaves exactly as before.
            Announce(map, coordinate, definition, VoiceFor(coordinate, definition));
            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign != null)
            { campaign.RecordEvent("RR_Event_AnomalyFired", coordinate.Id, coordinate.Label,
                definition.LabelCap.ToString()); }
            return true;
        }

        /// <summary>
        /// Run one effect over an explicit set of cells.
        ///
        /// **The one implementation of all four effects.** A coordinate passes the cells of its
        /// rooms minus the threshold; the threshold bleed at the headquarters passes the cells of
        /// the room a gate stands in. A second copy of these bodies would drift, and what would
        /// drift out of them are the four promises in invariant 28 -- nothing damages a pawn,
        /// nothing is destroyed, nothing blocks a route, and there is always a countermeasure.
        ///
        /// Returns false when the effect found nothing to do, so a caller can decline to
        /// announce an event that did not happen.
        /// </summary>
        public static bool FireEffect(Map map, List<IntVec3> cells, AnomalyEffect effect, int magnitude)
        {
            if (map == null || cells == null || cells.Count == 0) { return false; }
            switch (effect)
            {
                case AnomalyEffect.LightsFail: return LightsFail(map, cells);
                case AnomalyEffect.ColdSnap: return ColdSnap(map, cells, magnitude);
                case AnomalyEffect.Seepage: return Seepage(map, cells, magnitude);
                case AnomalyEffect.Rearrangement: return Rearrange(map, cells, magnitude);
                // A fragment needs nothing to act on, exactly like `Presence`: it is a
                // transmission, not a change to the space. Returning true unconditionally
                // is the honest answer -- `FireEffect` returns false to mean *the effect
                // found nothing to do*, and this one never can.
                case AnomalyEffect.RadioFragment: return true;
                default: return true;
            }
        }

        /// <summary>
        /// Switches off every light in the space.
        ///
        /// Uses vanilla's own flick switch, which means **the countermeasure is vanilla too**:
        /// a colonist walks over and turns them back on. That is a far better answer than a
        /// bespoke darkness mechanic, because the player already knows how to do it.
        /// </summary>
        private static bool LightsFail(Map map, List<IntVec3> cells)
        {
            bool any = false;
            foreach (Thing thing in ThingsIn(map, cells))
            {
                CompFlickable flick = thing.TryGetComp<CompFlickable>();
                if (flick == null || !flick.SwitchIsOn) { continue; }
                if (thing.TryGetComp<CompGlower>() == null) { continue; }
                flick.SwitchIsOn = false;
                any = true;
            }
            return any;
        }

        private static bool ColdSnap(Map map, List<IntVec3> cells, int degrees)
        {
            bool any = false;
            var seen = new HashSet<Room>();
            foreach (IntVec3 cell in cells)
            {
                Room room = cell.GetRoom(map);
                if (room == null || room.UsesOutdoorTemperature || !seen.Add(room)) { continue; }
                room.TempTracker.Temperature -= Math.Max(1, degrees);
                any = true;
            }
            return any;
        }

        private static bool Seepage(Map map, List<IntVec3> cells, int amount)
        {
            ThingDef filth = ThingDefOf.Filth_Dirt;
            if (filth == null) { return false; }
            int placed = 0;
            foreach (IntVec3 cell in cells)
            {
                if (placed >= Math.Max(1, amount)) { break; }
                if (!cell.Standable(map)) { continue; }
                if (FilthMaker.TryMakeFilth(cell, map, filth)) { placed++; }
            }
            return placed > 0;
        }

        /// <summary>
        /// Moves loose items to other cells in the space.
        ///
        /// **Loose items only.** Fixtures are left alone because the clue system records a
        /// landmark per room and moving one would quietly break a trail the player is following;
        /// nothing is destroyed either, so the worst case is a player hunting for something that
        /// is definitely still here.
        /// </summary>
        private static bool Rearrange(Map map, List<IntVec3> cells, int count)
        {
            if (cells.Count == 0) { return false; }

            var loose = new List<Thing>();
            foreach (IntVec3 cell in cells)
            {
                Thing item = cell.GetFirstItem(map);
                if (item == null || item is Corpse) { continue; }
                if (BondService.FaceValueOf(item) > 0L) { continue; }   // never move somebody's money
                loose.Add(item);
            }
            if (loose.Count == 0) { return false; }

            int moved = 0;
            for (int index = 0; index < loose.Count && moved < Math.Max(1, count); index++)
            {
                Thing item = loose[index];
                IntVec3 target = cells[(index * 37 + item.thingIDNumber) % cells.Count];
                if (!target.InBounds(map) || !target.Standable(map)) { continue; }
                if (target.GetFirstItem(map) != null) { continue; }
                item.DeSpawn();
                if (!GenPlace.TryPlaceThing(item, target, map, ThingPlaceMode.Near))
                {
                    // Put it back rather than leaving it nowhere. An event must never destroy
                    // a player's property, and an unspawned thing is worse than a moved one.
                    GenPlace.TryPlaceThing(item, cells[index % cells.Count], map, ThingPlaceMode.Near);
                    continue;
                }
                moved++;
            }
            return moved > 0;
        }

        /// <summary>
        /// The name a radio fragment carries, or null for every other effect.
        ///
        /// Prefers a **living colonist**, because the uncanny version is a voice whose
        /// owner is in the base at the same moment. Falls back to the lost-pawn register,
        /// which is the sadder reading and still a recognition. With neither -- a branch
        /// with nobody at home and nobody lost -- there is no fragment at all, because a
        /// transmission from a name nobody knows is the thing this is not.
        ///
        /// Derived from the coordinate's seed and its opening count, never `Rand`, so the
        /// same opening always carries the same voice and a reload cannot reroll who is
        /// on the radio.
        /// </summary>
        private static string VoiceFor(CoordinateRecord coordinate,
            RimroomsAnomalyEventDef definition)
        {
            if (definition == null || definition.effect != AnomalyEffect.RadioFragment)
            { return null; }
            RimroomsCampaignComponent campaign = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (campaign == null) { return null; }
            var voices = new List<string>();
            foreach (StaffRecord member in campaign.Staff)
            {
                if (member != null && member.Employed && member.Pawn != null
                    && !member.Pawn.Dead && !string.IsNullOrEmpty(member.Name))
                { voices.Add(member.Name); }
            }
            if (voices.Count == 0)
            {
                foreach (string lost in campaign.LostPawnNames())
                {
                    if (!string.IsNullOrEmpty(lost)) { voices.Add(lost); }
                }
            }
            if (voices.Count == 0) { return null; }
            voices.Sort(System.StringComparer.Ordinal);
            int draw = CampaignSeed.Derive(coordinate.Seed,
                "radio:voice:" + coordinate.Openings, 1);
            if (draw < 0) { draw = ~draw; }
            return voices[draw % voices.Count];
        }

        private static void Announce(Map map, CoordinateRecord coordinate,
            RimroomsAnomalyEventDef definition, string voice = null)
        {
            IntVec3 focus = RoomCells(map, coordinate).FirstOrDefault();

            // **THE TRACE OUTLIVES THE LETTER, and it is recorded before the letter is sent.**
            // Owner, 2026-10-04: the unnerving register applies to *"all things ie events random
            // spanwns"*. A notification scrolls away; `THREAT_DESIGN_SHEETS.md` asks for a
            // *"recorded outcome"* too, and until now an event left nothing at all -- a crew
            // arriving next opening walked through a space that had gone dark or been rearranged
            // and found no sign of it.
            //
            // Written first on purpose: the letter is the thing that can fail (a missing key, a
            // suppressed notification), and the record is the thing a player can still go and
            // read afterwards. Ordering it the other way would make the record the optional half.
            RecordTrace(map, coordinate, definition, focus);

            if (string.IsNullOrEmpty(definition.letterLabelKey)) { return; }
            // A voice is passed only when there is one. `Translate` ignores an extra
            // argument a string has no placeholder for, so the other seven events read
            // exactly as they did.
            Find.LetterStack.ReceiveLetter(
                definition.letterLabelKey.Translate(),
                voice == null ? definition.letterTextKey.Translate()
                    : definition.letterTextKey.Translate(voice),
                LetterDefOf.NeutralEvent,
                focus.IsValid ? new TargetInfo(focus, map) : (LookTargets)null);
        }

        /// <summary>
        /// Leave a readable mark in the coordinate saying this happened here.
        ///
        /// Reuses the clue record an ordinary room's furniture already leaves, so the Atlas
        /// listing, the saved record and the on-map label need no knowledge that this one came
        /// from an event. The room is the one the event focused on, which is where a player
        /// would go looking.
        /// </summary>
        private static void RecordTrace(Map map, CoordinateRecord coordinate,
            RimroomsAnomalyEventDef definition, IntVec3 focus)
        {
            if (map == null || coordinate == null || definition == null) { return; }
            if (string.IsNullOrEmpty(definition.traceKey)) { return; }
            Generation.RoomContentMapComponent content =
                map.GetComponent<Generation.RoomContentMapComponent>();
            if (content == null) { return; }
            RoomRecord room = focus.IsValid
                ? coordinate.Rooms.FirstOrDefault(candidate => candidate.familyId != "threshold_room"
                    && candidate.Bounds.Contains(focus))
                : null;
            // No room under the focus cell is not a reason to lose the record: the coordinate
            // still had the event. The first non-threshold room carries it instead.
            if (room == null)
            {
                room = coordinate.Rooms.FirstOrDefault(candidate => candidate.familyId != "threshold_room");
            }
            if (room == null) { return; }
            content.AddEventClue(coordinate.Id, room.Index, definition.traceKey,
                focus.IsValid ? focus : room.Bounds.CenterCell);
        }

        /// <summary>
        /// Every cell inside the coordinate's rooms **except the threshold**.
        ///
        /// The exclusion is the whole safety guarantee: whatever an event does, it does not do
        /// it where the way back is.
        /// </summary>
        private static IEnumerable<IntVec3> RoomCells(Map map, CoordinateRecord coordinate)
        {
            if (coordinate.Rooms == null) { yield break; }
            for (int index = 0; index < coordinate.Rooms.Count; index++)
            {
                RoomRecord room = coordinate.Rooms[index];
                if (room == null) { continue; }
                if (string.Equals(room.FamilyId, "threshold_room", StringComparison.Ordinal))
                { continue; }
                foreach (IntVec3 cell in room.Bounds.ContractedBy(1).Cells)
                {
                    if (cell.InBounds(map)) { yield return cell; }
                }
            }
        }

        private static IEnumerable<Thing> ThingsIn(Map map, List<IntVec3> cells)
        {
            var seen = new HashSet<Thing>();
            foreach (IntVec3 cell in cells)
            {
                List<Thing> things = cell.GetThingList(map);
                for (int index = 0; index < things.Count; index++)
                {
                    if (things[index] != null && seen.Add(things[index])) { yield return things[index]; }
                }
            }
        }
    }
}
