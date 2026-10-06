using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using RimroomsAsyncIndustries.Threats;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    /// <summary>
    /// What a marker means. The colour is the meaning, not a decoration.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"tyhe glow pods can be used and lets not
    /// limit the amount as a backrooms instance can have 100s of rooms if the player is using
    /// 300x300 maps for instance and maybe lets have the glow pods color setable"*, clarified
    /// immediately after with *"color means differnt types of the needs markers"*.
    ///
    /// The second sentence decides how the first is built. The colour **is** settable, and the
    /// way you set it is by choosing what the marker is for — so RimWorld's own free colour
    /// picker is deliberately **not** enabled on these. A picker would let a player paint a
    /// danger marker the same green as a cleared one, and the whole point of a colour is that
    /// it can be read from across a dark room without selecting anything.
    ///
    /// Presentation data, not a capability. Nothing about a marker changes what a pawn may do.
    /// </summary>
    public sealed class RimroomsMarkerTypeDef : Def
    {
        /// <summary>The glow this marker casts. Core writes glow colours with alpha 0.</summary>
        public ColorInt glowColor = new ColorInt(255, 255, 255, 0);

        /// <summary>Order in the picker. Sorted ordinally after this, never by hash order.</summary>
        public int displayOrder;

        /// <summary>
        /// Whether a marker of this type, left in a junction and still where it was put,
        /// counters a corridor distortion.
        ///
        /// A type field rather than a hardcoded def name, so that what a colour *means*
        /// mechanically is data a reader can see beside the colour itself.
        /// </summary>
        public bool countersDistortion;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors()) { yield return error; }
            if (string.IsNullOrEmpty(label)) { yield return "A marker type must have a label; a player picks it by name."; }
            if (string.IsNullOrEmpty(description)) { yield return "A marker type must have a description; it is shown in the picker."; }
        }

        /// <summary>
        /// Every marker type in display order. Sorted ordinally, because a list that is rolled
        /// over or shown to a player must not depend on def load order.
        /// </summary>
        public static List<RimroomsMarkerTypeDef> AllInOrder()
        {
            return DefDatabase<RimroomsMarkerTypeDef>.AllDefsListForReading
                .OrderBy(definition => definition.displayOrder)
                .ThenBy(definition => definition.defName, System.StringComparer.Ordinal)
                .ToList();
        }
    }

    public sealed class CompProperties_RimroomsMarker : CompProperties
    {
        public CompProperties_RimroomsMarker() { compClass = typeof(CompRimroomsMarker); }
    }

    /// <summary>
    /// Turns an ordinary glow pod into a route marker, and does nothing at all until somebody
    /// designates it.
    ///
    /// This replaces the custom survey tag retired in this checkpoint, and it is the same
    /// pattern the gate already uses on doors: **the component sits on every one of them and
    /// is dormant until designated**, so a glow pod dropped by an insect hive on a normal map
    /// is completely untouched — it still glows its own green, and it still dies on schedule.
    ///
    /// Three things happen the moment it becomes a marker, and all three are reversible:
    ///
    /// 1. **The glow turns the colour of its meaning**, through `CompGlower.GlowColor`, which
    ///    has a public setter that re-registers the glower with the map's glow grid itself.
    /// 2. **Its lifespan stops running.** Core's glow pod carries `CompProperties_Lifespan` at
    ///    1,200,000 ticks — **twenty days** — after which it dies. A route home that evaporates
    ///    on day twenty is not a route home. `CompLifespan.age` is a public field, so a
    ///    designated pod is simply held at zero and an undesignated one is not touched.
    /// 3. **It remembers where it is**, so the site can tell you when a marker you left in one
    ///    room turns up in another.
    ///
    /// **There is no cap of any kind**, by direction. Not per room, not per coordinate, not per
    /// map. The retired survey tag allowed exactly one deployed aid per room, which is a cap,
    /// and the owner's words were *"lets not limit the amount"*.
    /// </summary>
    public sealed class CompRimroomsMarker : ThingComp
    {
        private RimroomsMarkerTypeDef markerType;
        private string coordinateId;
        private int roomIndex = -1;
        private int markerNumber;
        private bool mismatch;

        /// <summary>
        /// True only for the instant the space itself moves a marker. Set so that the respawn
        /// does not re-read the room the marker has just been moved into and quietly agree with
        /// it, which would erase the discrepancy the move exists to create.
        /// </summary>
        private bool relocating;

        public bool IsMarker { get { return markerType != null; } }
        public RimroomsMarkerTypeDef MarkerType { get { return markerType; } }
        public string CoordinateId { get { return coordinateId; } }
        public int RoomIndex { get { return roomIndex; } }
        public int Number { get { return markerNumber; } }

        private CompGlower Glower { get { return parent.TryGetComp<CompGlower>(); } }
        private CompLifespan Lifespan { get { return parent.TryGetComp<CompLifespan>(); } }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            // Re-applied from our own saved marker type rather than relying on the glower's
            // saved override. One source of truth for the colour, and it survives a pod being
            // minified, hauled across a gate and put back down.
            ApplyGlow();

            // A marker a player uninstalled and set down somewhere else is a marker in a new
            // room, and saying otherwise would read exactly like the space having moved it.
            // A load restores what was saved, and a relocation is the space's own doing.
            if (!respawningAfterLoad && !relocating && IsMarker) { BindToPlace(); }
            relocating = false;
        }

        /// <summary>
        /// Move a placed marker to another cell, keeping everything it knows.
        ///
        /// Writing <c>parent.Position</c> directly would have been shorter and would have been
        /// a bug: a glow pod is a <see cref="Building"/>, and a building's cells are registered
        /// in the map's thing grid at spawn. Moving one without despawning leaves the grid
        /// pointing at where it used to be.
        /// </summary>
        internal bool RelocateTo(IntVec3 cell, Map destination)
        {
            if (!parent.Spawned || destination == null || !cell.InBounds(destination) || !cell.Standable(destination))
            { return false; }
            relocating = true;
            Thing moved = parent;
            moved.DeSpawn();
            GenSpawn.Spawn(moved, cell, destination);
            relocating = false;
            return moved.Spawned;
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            // Order against CompLifespan's own rare tick does not matter: whether it adds 250
            // before or after this runs, the age stays five orders of magnitude below expiry.
            if (IsMarker && Lifespan != null) { Lifespan.age = 0; }
        }

        internal void Designate(RimroomsMarkerTypeDef type)
        {
            markerType = type;
            BindToPlace();
            ApplyGlow();
        }

        internal void ClearDesignation()
        {
            markerType = null;
            coordinateId = null;
            roomIndex = -1;
            markerNumber = 0;
            mismatch = false;
            ApplyGlow();
        }

        internal void MarkMismatch() { mismatch = true; }

        /// <summary>
        /// Records the coordinate and room a marker was set down in, when there is one. A
        /// marker on a home map is perfectly legal and simply has nowhere to record.
        /// </summary>
        private void BindToPlace()
        {
            coordinateId = null;
            roomIndex = -1;
            mismatch = false;
            if (markerType == null || !parent.Spawned || parent.Map == null) { return; }
            FirstSliceSiteComponent site = parent.Map.GetComponent<FirstSliceSiteComponent>();
            if (site == null || site.Coordinate == null) { return; }
            RoomRecord room = site.RoomAt(parent.Position);
            if (room == null) { return; }
            coordinateId = site.Coordinate.Id;
            roomIndex = room.index;
            if (markerNumber == 0) { markerNumber = site.NextMarkerNumber(); }
        }

        /// <summary>
        /// Sets the glow to the marker's meaning, or back to the pod's own colour.
        ///
        /// The undesignated case writes the def's own value rather than clearing the override,
        /// because Core's clear path is protected. The visible result is identical.
        /// </summary>
        private void ApplyGlow()
        {
            CompGlower glower = Glower;
            if (glower == null) { return; }
            glower.GlowColor = markerType != null ? markerType.glowColor : glower.Props.glowColor;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo gizmo in base.CompGetGizmosExtra()) { yield return gizmo; }
            if (!parent.Spawned) { yield break; }

            yield return new Command_Action
            {
                defaultLabel = IsMarker
                    ? "RR_Marker_Change".Translate().ToString()
                    : "RR_Marker_Designate".Translate().ToString(),
                defaultDesc = "RR_Marker_DesignateDesc".Translate().ToString(),
                action = OpenTypePicker,
            };

            if (!IsMarker) { yield break; }
            yield return new Command_Action
            {
                defaultLabel = "RR_Marker_Clear".Translate().ToString(),
                defaultDesc = "RR_Marker_ClearDesc".Translate().ToString(),
                action = ClearDesignation,
            };
        }

        private void OpenTypePicker()
        {
            List<FloatMenuOption> options = new List<FloatMenuOption>();
            foreach (RimroomsMarkerTypeDef type in RimroomsMarkerTypeDef.AllInOrder())
            {
                RimroomsMarkerTypeDef chosen = type;
                options.Add(new FloatMenuOption(chosen.LabelCap, delegate { Designate(chosen); }));
            }
            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("RR_Marker_NoTypes".Translate(), null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        public override string TransformLabel(string label)
        {
            return IsMarker ? "RR_Marker_Label".Translate(label, markerType.LabelCap).ToString() : label;
        }

        public override string CompInspectStringExtra()
        {
            if (!IsMarker) { return null; }
            string text = "RR_Marker_Inspect".Translate(markerType.LabelCap).ToString();
            if (roomIndex >= 0)
            {
                text += "\n" + "RR_Marker_InspectRoom".Translate((roomIndex + 1).ToString()).ToString();
            }
            if (mismatch)
            {
                text += "\n" + "RR_Marker_Mismatch".Translate((roomIndex + 1).ToString()).ToString();
            }
            return text;
        }

        public override void DrawGUIOverlay()
        {
            base.DrawGUIOverlay();
            if (!mismatch || !parent.Spawned || parent.Map != Find.CurrentMap || parent.Position.Fogged(parent.Map))
            { return; }
            GenMapUI.DrawThingLabel(parent, "RR_Marker_RepeatedLabel".Translate((roomIndex + 1).ToString()));
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Defs.Look(ref markerType, "rr_markerType");
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref roomIndex, "rr_roomIndex", -1);
            Scribe_Values.Look(ref markerNumber, "rr_markerNumber");
            Scribe_Values.Look(ref mismatch, "rr_mismatch");
        }

        /// <summary>
        /// Every designated marker on a map. Used by the site and by the evidence ledger, and
        /// deliberately a scan rather than a registry: markers are uncapped, a player may move
        /// one at any time with the ordinary uninstall order, and a registry that can drift out
        /// of step with the map is worse than a scan that cannot.
        /// </summary>
        public static IEnumerable<CompRimroomsMarker> OnMap(Map map)
        {
            if (map == null) { yield break; }
            foreach (ThingDef definition in MarkerCarrierDefs)
            {
                foreach (Thing thing in map.listerThings.ThingsOfDef(definition))
                {
                    CompRimroomsMarker marker = thing.TryGetComp<CompRimroomsMarker>();
                    if (marker != null && marker.IsMarker) { yield return marker; }
                }
            }
        }

        /// <summary>
        /// Every def that can carry a marker: the company's own survey tag, and Core's glow pod.
        ///
        /// **THIS SCAN NAMED ONE DEF AND THAT WAS THE THIRD INSTANCE OF THE SAME DEFECT IN A DAY.**
        /// The gate's providers and the crew's record book both resolved a single def name while
        /// the component was the real marker, so new content carrying the component was invisible
        /// to the system built to read it. A survey tag with `CompRimroomsMarker` would have been
        /// designatable from its own button and then missing from every route, every ledger entry
        /// and every distortion count that `OnMap` feeds.
        ///
        /// **The scan still has to name defs rather than walk every thing on the map**, because
        /// `ThingsOfDef` is indexed and `AllThings` is not, and this runs on a site tick. So the
        /// list is short, ordered ours-first, and both entries resolve silently to null when
        /// absent -- a profile without Core's glow pod simply has one fewer carrier.
        /// </summary>
        private static IEnumerable<ThingDef> MarkerCarrierDefs
        {
            get
            {
                ThingDef tag = DefDatabase<ThingDef>.GetNamedSilentFail("RR_SurveyTag");
                if (tag != null) { yield return tag; }
                ThingDef pod = DefDatabase<ThingDef>.GetNamedSilentFail("GlowPod");
                if (pod != null) { yield return pod; }
            }
        }
    }
}
