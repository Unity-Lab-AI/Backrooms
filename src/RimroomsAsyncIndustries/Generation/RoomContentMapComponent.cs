using System.Collections.Generic;
using System.Linq;
using RimroomsAsyncIndustries.Company;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Generation
{
    public sealed class RoomContentMapComponent : MapComponent
    {
        private string coordinateId;
        private int contentVersion;
        private bool populationStarted;
        private bool populationComplete;
        private List<RoomClueRecord> clues = new List<RoomClueRecord>();
        public RoomContentMapComponent(Map map) : base(map) { }
        public IReadOnlyList<RoomClueRecord> Clues { get { return clues; } }
        public bool PopulationComplete { get { return populationComplete; } }
        internal bool BeginPopulation(string id, int version)
        {
            if (populationStarted || populationComplete) { return false; }
            coordinateId = id; contentVersion = version; populationStarted = true;
            return true;
        }
        internal void AddClue(string id, RoomRecord room, Thing landmark, int variant, bool salvage)
        {
            clues.Add(new RoomClueRecord { id = id + ":room:" + room.Index + ":clue", roomIndex = room.Index,
                family = room.FamilyId, variant = variant, landmark = landmark, originCell = landmark.Position, salvage = salvage });
        }
        /// <summary>
        /// A clue left by something that **happened** rather than something that is here.
        ///
        /// **Owner direction, 2026-10-04:** *"remember lsd unnerving feeling with all
        /// things ie events random spanwns"*, restating *"even wild waky carzxzy creepy
        /// things when u add places and events"*. An anomaly event used to fire one
        /// letter and leave nothing: the notification scrolled away, the coordinate
        /// recorded no trace, and a crew arriving next opening walked through a space
        /// that had gone dark or been rearranged with no sign of it.
        ///
        /// Two things differ from an ordinary clue and both are the reason this overload
        /// exists at all:
        ///
        /// * **No landmark thing.** `AddClue` reads `landmark.Position`; an event has
        ///   nothing to point at, so the cell is passed instead. The map label and the
        ///   locate button already skip a clue whose landmark is null, so it degrades to
        ///   a listed trace rather than breaking either surface.
        /// * **Observed on arrival.** The crew lived through it. `MapComponentTick` marks
        ///   an ordinary clue observed only once its landmark is unfogged in a surveyed
        ///   room, so it would never mark this one and the trace would be invisible
        ///   forever.
        /// </summary>
        internal void AddEventClue(string id, int roomIndex, string effectKey, IntVec3 cell)
        {
            if (string.IsNullOrEmpty(effectKey)) { return; }
            string key = id + ":room:" + roomIndex + ":event:" + effectKey;
            // One trace per event per room. A repeatable event that fires twice in the
            // same room has left the same mark, and two identical lines in the Atlas read
            // as a bug rather than as emphasis.
            if (clues.Exists(existing => existing.id == key)) { return; }
            clues.Add(new RoomClueRecord
            {
                id = key,
                roomIndex = roomIndex,
                family = effectKey,
                variant = 0,
                landmark = null,
                originCell = cell,
                salvage = false,
                observed = true,
            });
        }

        internal void CompletePopulation() { populationComplete = true; }
        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref contentVersion, "rr_contentVersion");
            Scribe_Values.Look(ref populationStarted, "rr_populationStarted");
            Scribe_Values.Look(ref populationComplete, "rr_populationComplete");
            Scribe_Collections.Look(ref clues, "rr_clues", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) { clues = clues ?? new List<RoomClueRecord>(); }
        }
        public override void MapComponentTick()
        {
            if (!populationComplete || Find.TickManager.TicksGame % 60 != 0) { return; }
            RimroomsCampaignComponent campaign = Current.Game?.GetComponent<RimroomsCampaignComponent>();
            CoordinateRecord coordinate = campaign == null ? null : campaign.Coordinates.FirstOrDefault(c => c.Id == coordinateId);
            if (coordinate == null) { return; }
            foreach (RoomClueRecord clue in clues)
            {
                if (!clue.observed && clue.landmark != null && clue.landmark.Spawned && clue.landmark.Map == map &&
                    !clue.landmark.Position.Fogged(map) && coordinate.Rooms.Any(r => r.Index == clue.roomIndex && r.Surveyed))
                { clue.observed = true; }
            }
        }
        public override void MapComponentOnGUI()
        {
            if (Find.CurrentMap != map || !populationComplete || Find.CameraDriver.CurrentZoom == CameraZoomRange.Furthest) { return; }
            foreach (RoomClueRecord clue in clues)
            {
                Thing landmark = clue.landmark;
                if (landmark == null || !landmark.Spawned || landmark.Map != map || landmark.Position.Fogged(map)) { continue; }
                Vector2 pos = GenMapUI.LabelDrawPosFor(landmark, -0.4f);
                string label = clue.Label;
                GenMapUI.DrawThingLabel(pos, label, Color.white);
                TooltipHandler.TipRegion(new Rect(pos.x - 110f, pos.y - 5f, 220f, 25f), () => clue.Description, landmark.thingIDNumber);
            }
        }
    }

    public sealed class RoomClueRecord : IExposable
    {
        internal string id;
        internal int roomIndex;
        internal string family;
        internal int variant;
        internal Thing landmark;
        internal IntVec3 originCell;
        internal bool salvage;
        internal bool observed;
        public string Id { get { return id; } }
        public int RoomIndex { get { return roomIndex; } }
        public Thing Landmark { get { return landmark; } }
        public bool Salvage { get { return salvage; } }
        public bool Observed { get { return observed; } }
        public string Label { get { return ("RR_Clue_Label_" + family).Translate(roomIndex + 1).ToString(); } }
        public string Description { get { return ("RR_Clue_Text_" + family).Translate(roomIndex + 1, variant + 1).ToString(); } }
        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "rr_id");
            Scribe_Values.Look(ref roomIndex, "rr_roomIndex");
            Scribe_Values.Look(ref family, "rr_family");
            Scribe_Values.Look(ref variant, "rr_variant");
            Scribe_References.Look(ref landmark, "rr_landmark");
            Scribe_Values.Look(ref originCell, "rr_originCell", IntVec3.Invalid);
            Scribe_Values.Look(ref salvage, "rr_salvage");
            Scribe_Values.Look(ref observed, "rr_observed");
        }
    }
}
