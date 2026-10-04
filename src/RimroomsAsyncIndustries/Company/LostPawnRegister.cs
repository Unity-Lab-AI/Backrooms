using System;
using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>
    /// The branch's record of people it lost inside a coordinate.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"finding random pawns of disappering"*.
    ///
    /// This is what makes that land rather than being a label. When a coordinate produces a
    /// *missing* person, the name it carries is drawn from here where there is one — so the
    /// name on the body, or the face in the corridor, is **a name the player recognises**.
    /// A stranger called nothing in particular is atmosphere; somebody you lost is a story.
    ///
    /// Bounded and consuming: the register holds a short list, drops the oldest when full, and
    /// a name is **taken** when it is used rather than copied. The same colonist is therefore
    /// never found twice, which is both better and the only honest reading of "missing".
    /// </summary>
    public sealed partial class RimroomsCampaignComponent
    {
        /// <summary>How many lost names are remembered. Small on purpose.</summary>
        private const int LostPawnCapacity = 24;

        /// <summary>Saved. Names of people lost inside coordinates, oldest first.</summary>
        private List<string> lostPawnNames = new List<string>();

        internal void ExposeLostPawns()
        {
            Scribe_Collections.Look(ref lostPawnNames, "rr_lostPawnNames", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && lostPawnNames == null)
            { lostPawnNames = new List<string>(); }
        }

        /// <summary>
        /// Records that somebody was lost inside a coordinate. Ignores duplicates so a body
        /// left in place across several visits is remembered once.
        /// </summary>
        public void NoteLostPawn(string name)
        {
            if (string.IsNullOrWhiteSpace(name)) { return; }
            lostPawnNames = lostPawnNames ?? new List<string>();
            if (lostPawnNames.Contains(name)) { return; }
            if (lostPawnNames.Count >= LostPawnCapacity) { lostPawnNames.RemoveAt(0); }
            lostPawnNames.Add(name);
            RecordEvent("RR_Event_PawnLostInside", name, name);
        }

        /// <summary>
        /// Takes a remembered name, removing it. Returns null when the branch has not lost
        /// anybody, which is the common case early and is why every caller must cope with it.
        /// </summary>
        public string TakeLostPawnName()
        {
            if (lostPawnNames == null || lostPawnNames.Count == 0) { return null; }
            string name = lostPawnNames[0];
            lostPawnNames.RemoveAt(0);
            return name;
        }

        /// <summary>How many lost names are currently remembered.</summary>
        public int LostPawnCount
        {
            get { return lostPawnNames == null ? 0 : lostPawnNames.Count; }
        }

        /// <summary>
        /// The remembered names, read without taking any of them.
        ///
        /// **`TakeLostPawnName` removes what it returns**, which is right for the thing it was
        /// written for -- a coordinate placing a missing person consumes the record, because
        /// that person has now been found. It is wrong for anything that merely *mentions*
        /// somebody: a radio fragment naming a lost colonist must not quietly delete the fact
        /// that they are lost.
        ///
        /// Returns a copy, so a caller iterating it cannot be broken by a note arriving
        /// mid-loop, and cannot reach in and edit the register through the accessor.
        /// </summary>
        public List<string> LostPawnNames()
        {
            return lostPawnNames == null ? new List<string>() : new List<string>(lostPawnNames);
        }
    }
}
