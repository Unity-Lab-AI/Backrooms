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
