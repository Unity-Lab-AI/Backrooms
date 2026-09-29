using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimroomsAsyncIndustries.Threats
{
    /// <summary>
    /// The place copying your **people**, not your things.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"not just room shape echoes but echos of
    /// thier inhabitance in weird ways and items and equipment and production benches"*.
    ///
    /// Items and benches shipped in 0.8.4-dev. This is *"echos of thier inhabitance"*, and it
    /// is a different thing entirely from echoing objects.
    ///
    /// ## The echo is of somebody who is alive right now
    ///
    /// **Deliberately not somebody you lost.** That is the Missing family, and it is a
    /// different and sadder feeling — a body with a familiar name is grief. An echo is
    /// *uncanny*, and it is uncanny precisely because the real one is standing in your base at
    /// the same moment you are looking at this one.
    ///
    /// That constraint is enforced, not assumed: a colonist must be **alive, not downed, and
    /// on a player home map** to be echoed. Somebody who is currently inside the coordinate is
    /// also excluded, because meeting your own echo while you are standing there is a different
    /// and much sillier effect than meeting it while you know they are at home.
    ///
    /// ## What is copied, and what deliberately is not
    ///
    /// **Copied:** the name, and the apparel. Those are the two things a player recognises at a
    /// glance, and together they are enough to land.
    ///
    /// **Not copied:** skills, traits, backstory, health, relationships. An echo is a *surface*
    /// — something that has seen your colonist rather than something that is them. Copying the
    /// interior would make it a duplicate, which is a weaker and much more confusing idea, and
    /// would also hand the player a free second copy of their best worker if they ever recruited
    /// it. Echoes therefore cannot be recruited at all.
    ///
    /// ## Never hostile
    ///
    /// An echo is unsettling, not dangerous. Hostility would also break the warning-first rule,
    /// because a thing wearing a friendly name that attacks is the definition of an unreadable
    /// threat.
    /// </summary>
    public static class ColonistEcho
    {
        /// <summary>
        /// A colonist worth echoing, chosen deterministically, or null when there is nobody
        /// suitable — a branch whose people are all inside the coordinate, or downed, or dead.
        /// </summary>
        public static Pawn PickSource(Map coordinateMap, int seed)
        {
            var candidates = new List<Pawn>();
            List<Map> maps = Find.Maps;
            if (maps == null) { return null; }

            for (int index = 0; index < maps.Count; index++)
            {
                Map map = maps[index];
                if (map == null || map == coordinateMap) { continue; }
                // Only somewhere the player actually lives. A colonist standing in another
                // coordinate is not "at home", and echoing them would lose the whole point.
                if (!map.IsPlayerHome) { continue; }
                if (Economy.OddOriginService.IsBackroomsMap(map)) { continue; }

                IReadOnlyList<Pawn> free = map.mapPawns == null ? null : map.mapPawns.FreeColonists;
                if (free == null) { continue; }
                for (int person = 0; person < free.Count; person++)
                {
                    Pawn pawn = free[person];
                    if (pawn == null || pawn.Dead || pawn.Downed) { continue; }
                    if (pawn.RaceProps == null || !pawn.RaceProps.Humanlike) { continue; }
                    candidates.Add(pawn);
                }
            }
            if (candidates.Count == 0) { return null; }

            // Sorted by a stable identity rather than by list order, which varies with spawn
            // and load order. Without this the same seed would echo a different colonist on a
            // reload, and the whole effect depends on it being the same person every time.
            candidates.Sort((left, right) => left.thingIDNumber.CompareTo(right.thingIDNumber));
            int roll = Gen.HashCombineInt(seed, 0x45434F50);
            if (roll < 0) { roll = ~roll; }
            return candidates[roll % candidates.Count];
        }

        /// <summary>
        /// Makes a generated pawn read as an echo of a colonist: their name, and their clothes.
        /// Returns the name used, or null if nothing could be echoed.
        /// </summary>
        public static string Apply(Pawn echo, Pawn source)
        {
            if (echo == null || source == null) { return null; }

            CopyName(echo, source);
            CopyApparel(echo, source);
            return source.LabelShortCap;
        }

        private static void CopyName(Pawn echo, Pawn source)
        {
            NameTriple sourceName = source.Name as NameTriple;
            if (sourceName != null)
            {
                echo.Name = new NameTriple(sourceName.First, sourceName.Nick, sourceName.Last);
                return;
            }
            if (source.Name != null)
            { echo.Name = new NameSingle(source.LabelShortCap); }
        }

        /// <summary>
        /// Dresses the echo in copies of what the source is wearing.
        ///
        /// **Copies, never the originals.** Taking the real apparel would strip a living
        /// colonist from across a gate, which would be a bug wearing a feature's clothes. Each
        /// piece is made fresh from the same def and stuff, so quality and damage differ — which
        /// is fitting, since an echo is a likeness rather than a duplicate.
        /// </summary>
        private static void CopyApparel(Pawn echo, Pawn source)
        {
            if (echo.apparel == null || source.apparel == null) { return; }
            List<Apparel> worn = source.apparel.WornApparel;
            if (worn == null) { return; }

            // Whatever the generator already dressed it in comes off first, or the echo ends up
            // wearing two shirts and reads as a mess rather than as a copy.
            echo.apparel.DestroyAll();

            for (int index = 0; index < worn.Count; index++)
            {
                Apparel piece = worn[index];
                if (piece == null || piece.def == null) { continue; }
                try
                {
                    ThingDef stuff = piece.Stuff;
                    if (stuff != null && !piece.def.MadeFromStuff) { stuff = null; }
                    if (stuff == null && piece.def.MadeFromStuff)
                    { stuff = GenStuff.DefaultStuffFor(piece.def); }
                    var copy = ThingMaker.MakeThing(piece.def, stuff) as Apparel;
                    if (copy == null) { continue; }
                    if (!ApparelUtility.HasPartsToWear(echo, copy.def)) { copy.Destroy(); continue; }
                    echo.apparel.Wear(copy, false);
                }
                catch (Exception)
                {
                    // Apparel from an unknown mod can refuse to be made or worn for reasons this
                    // mod cannot anticipate. A missing coat is a worse echo, not a broken one.
                }
            }
        }
    }
}
