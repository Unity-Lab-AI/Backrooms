using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    /// <summary>
    /// The register of what this branch has actually built, and the reason deep coordinates
    /// start looking like it.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"we need a dynamic procederually gernation of
    /// BAckrroms so that new equipement and rooms and shit going into the backrooms and build
    /// there or in the real world can start appearing in lower levels of back rooms seeds"*.
    ///
    /// ## Why this is the best idea the generator has had
    ///
    /// Until now a deep coordinate drew its furniture from the whole def database — everything
    /// the loaded game could offer, which is broad but impersonal. This makes the place draw
    /// from **the player instead**. Push far enough in and the rooms start containing the
    /// things *you* build: your benches, your beds, your machines, laid out by something that
    /// has clearly seen them.
    ///
    /// That is exactly the feeling the setting is built on. A Backrooms space reads as wrong
    /// because it is *almost* somewhere real, and nothing is more almost-real to a player than
    /// a copy of their own colony. It also means the generator gets more interesting the longer
    /// a save runs, with no new content authored for it.
    ///
    /// ## Sampled, never hooked
    ///
    /// Nothing here intercepts construction. A rotating window of one map's buildings is
    /// sampled on an interval, which is the same bounded-scan rule the work layer uses
    /// everywhere else: **fixed cost regardless of how large the colony grows, and no region
    /// of any map can be starved**, because the window advances every time.
    ///
    /// That also means it costs nothing to be correct about *where* something was built. A
    /// bench in the colony and a bench a colonist assembled inside a coordinate are both
    /// simply things the branch built, which is what the owner asked for — *"build there or in
    /// the real world"*.
    ///
    /// ## Bounded, and it forgets
    ///
    /// The register is capped. When it is full, the **least recently seen** entry is dropped,
    /// so a branch that stops building a thing eventually stops seeing it echoed back. A
    /// register that only ever grew would turn a long save into an ever-lengthening list that
    /// is saved, loaded and scanned forever.
    /// </summary>
    public sealed class ConstructionEchoComponent : GameComponent
    {
        /// <summary>How often a sample runs. Roughly every ten seconds at normal speed.</summary>
        private const int Interval = 600;

        /// <summary>Cells examined per sample. A rotating window, so cost is fixed.</summary>
        private const int WindowCells = 900;

        /// <summary>Most definitions the register will hold before it starts forgetting.</summary>
        public const int Capacity = 96;

        /// <summary>
        /// The shallowest depth at which the echo appears at all.
        ///
        /// Deliberately not depth 2. The first couple of spaces should still feel like
        /// somewhere that existed before the player did; the place copying you is a thing you
        /// discover by pushing in, not a thing that greets you.
        /// </summary>
        public const int EchoFromDepth = 3;

        /// <summary>Saved, in parallel: definition names and the tick each was last seen.</summary>
        private List<string> defNames = new List<string>();
        private List<int> lastSeenTicks = new List<int>();

        /// <summary>Where the rotating window currently sits, per map. Not saved; cheap to rebuild.</summary>
        private readonly Dictionary<int, int> cursors = new Dictionary<int, int>();
        private int mapCursor;

        public ConstructionEchoComponent(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref defNames, "rr_echoDefNames", LookMode.Value);
            Scribe_Collections.Look(ref lastSeenTicks, "rr_echoLastSeen", LookMode.Value);
            if (Scribe.mode != LoadSaveMode.PostLoadInit) { return; }
            defNames = defNames ?? new List<string>();
            lastSeenTicks = lastSeenTicks ?? new List<int>();
            // Parallel lists must agree or one definition inherits another's age and the
            // eviction order silently becomes arbitrary.
            while (lastSeenTicks.Count < defNames.Count) { lastSeenTicks.Add(0); }
            while (lastSeenTicks.Count > defNames.Count) { lastSeenTicks.RemoveAt(lastSeenTicks.Count - 1); }
        }

        public override void GameComponentTick()
        {
            int now = Find.TickManager == null ? 0 : Find.TickManager.TicksGame;
            if (now % Interval != 0) { return; }

            List<Map> maps = Find.Maps;
            if (maps == null || maps.Count == 0) { return; }
            mapCursor = (mapCursor + 1) % maps.Count;
            Map map = maps[mapCursor];
            if (map == null) { return; }

            Sample(map, now);
        }

        /// <summary>
        /// Walks the next window of one map and records every player-built thing it finds.
        ///
        /// The window advances whether or not anything was found, which is what stops a large
        /// empty region from parking the cursor and starving the rest of the map.
        /// </summary>
        private void Sample(Map map, int now)
        {
            int cells = map.Size.x * map.Size.z;
            if (cells <= 0) { return; }
            int cursor;
            cursors.TryGetValue(map.uniqueID, out cursor);

            int examined = 0;
            while (examined < WindowCells)
            {
                if (cursor >= cells) { cursor = 0; }
                IntVec3 cell = map.cellIndices.IndexToCell(cursor);
                cursor++;
                examined++;
                if (!cell.InBounds(map)) { continue; }

                List<Thing> things = cell.GetThingList(map);
                for (int index = 0; index < things.Count; index++)
                {
                    Thing thing = things[index];
                    if (!Echoable(thing)) { continue; }
                    Note(thing.def.defName, now);
                }
            }
            cursors[map.uniqueID] = cursor;
        }

        /// <summary>
        /// Whether a thing counts as something the branch built.
        ///
        /// Faction ownership is the test, so a bench a colonist assembled inside a coordinate
        /// counts exactly as much as one in the colony — *"build there or in the real world"*.
        /// Generated Backrooms fixtures are **not** player-faction, so the place cannot echo
        /// its own furniture back at itself and slowly converge on a single room.
        /// </summary>
        private static bool Echoable(Thing thing)
        {
            if (thing == null || thing.def == null || !thing.Spawned) { return false; }
            if (thing is Pawn) { return false; }
            if (thing.Faction == null || !thing.Faction.IsPlayer) { return false; }
            if (thing.def.category != ThingCategory.Building) { return false; }
            if (thing.def.building == null) { return false; }
            if (thing.def.building.isNaturalRock) { return false; }
            // Walls, doors and conduits are structure rather than contents. Echoing them would
            // put a wall in the middle of a generated room, which changes the layout instead of
            // dressing it -- the same rule the archetype placer already holds.
            if (thing.def.building.isEdifice && !thing.def.Minifiable) { return false; }
            if (thing.def.size.x > 2 || thing.def.size.z > 2) { return false; }
            return true;
        }

        /// <summary>Records a definition, or refreshes how recently it was seen.</summary>
        private void Note(string defName, int now)
        {
            if (string.IsNullOrEmpty(defName)) { return; }
            int existing = defNames.IndexOf(defName);
            if (existing >= 0)
            {
                lastSeenTicks[existing] = now;
                return;
            }
            if (defNames.Count >= Capacity) { EvictOldest(); }
            defNames.Add(defName);
            lastSeenTicks.Add(now);
        }

        private void EvictOldest()
        {
            int oldest = 0;
            for (int index = 1; index < lastSeenTicks.Count; index++)
            {
                if (lastSeenTicks[index] < lastSeenTicks[oldest]) { oldest = index; }
            }
            defNames.RemoveAt(oldest);
            lastSeenTicks.RemoveAt(oldest);
        }

        /// <summary>
        /// The register, sorted ordinally.
        ///
        /// Sorted for the same reason the archetype candidate lists are: unsorted it would
        /// follow the order things happened to be sampled in, which differs between machines,
        /// and **the same seed would then produce different rooms**.
        /// </summary>
        public List<string> Register()
        {
            var copy = new List<string>(defNames);
            copy.Sort(StringComparer.Ordinal);
            return copy;
        }

        /// <summary>
        /// A definition from the register that satisfies a slot, or null when the register
        /// holds nothing suitable. Deterministic from the seed given.
        /// </summary>
        public ThingDef Draw(Predicate<ThingDef> acceptable, int seed)
        {
            List<string> register = Register();
            var candidates = new List<ThingDef>();
            for (int index = 0; index < register.Count; index++)
            {
                ThingDef definition = DefDatabase<ThingDef>.GetNamedSilentFail(register[index]);
                if (definition == null) { continue; }
                if (acceptable != null && !acceptable(definition)) { continue; }
                candidates.Add(definition);
            }
            if (candidates.Count == 0) { return null; }
            int roll = Gen.HashCombineInt(seed, 0x4543484F);
            if (roll < 0) { roll = ~roll; }
            return candidates[roll % candidates.Count];
        }

        /// <summary>The live component, or null outside a game.</summary>
        public static ConstructionEchoComponent Current
        {
            get
            {
                return Verse.Current.Game == null
                    ? null : Verse.Current.Game.GetComponent<ConstructionEchoComponent>();
            }
        }
    }
}
