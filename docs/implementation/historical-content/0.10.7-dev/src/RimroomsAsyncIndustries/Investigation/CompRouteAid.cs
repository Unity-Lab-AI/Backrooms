using Verse;

namespace RimroomsAsyncIndustries.Investigation
{
    public sealed class CompProperties_RouteAid : CompProperties
    {
        public bool beacon;
        public CompProperties_RouteAid() { compClass = typeof(CompRouteAid); }
    }
    public sealed class CompRouteAid : ThingComp
    {
        private string coordinateId;
        private int roomIndex = -1;
        private int markerNumber;
        private bool mismatch;
        public bool Deployed { get { return !string.IsNullOrEmpty(coordinateId); } }
        public bool Beacon { get { return ((CompProperties_RouteAid)props).beacon; } }
        public string CoordinateId { get { return coordinateId; } }
        public int RoomIndex { get { return roomIndex; } }
        public int Number { get { return markerNumber; } }
        internal void Deploy(string coordinate, int room, int number)
        { coordinateId = coordinate; roomIndex = room; markerNumber = number; }
        internal void MarkMismatch() { mismatch = true; }
        public override bool AllowStackWith(Thing other)
        { return !Deployed && other.TryGetComp<CompRouteAid>()?.Deployed == false; }
        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            // Picking the physical aid up removes its deployed route function.
            coordinateId = null; roomIndex = -1; markerNumber = 0; mismatch = false;
        }
        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref coordinateId, "rr_coordinateId");
            Scribe_Values.Look(ref roomIndex, "rr_roomIndex", -1);
            Scribe_Values.Look(ref markerNumber, "rr_markerNumber");
            Scribe_Values.Look(ref mismatch, "rr_mismatch");
        }
        public override string TransformLabel(string label)
        { return Deployed ? "RR_Field_AidLabel".Translate(label, markerNumber).ToString() : label; }
        public override string CompInspectStringExtra()
        {
            if (!Deployed) { return null; }
            string text = "RR_Field_AidDeployed".Translate(markerNumber, roomIndex + 1).ToString();
            return mismatch ? text + "\n" + "RR_Field_AidMismatch".Translate(roomIndex + 1).ToString() : text;
        }
        public override void DrawGUIOverlay()
        {
            base.DrawGUIOverlay();
            if (mismatch && parent.Spawned && parent.Map == Find.CurrentMap && !parent.Position.Fogged(parent.Map))
            { GenMapUI.DrawThingLabel(parent, "RR_Field_RepeatedLabel".Translate(roomIndex + 1, markerNumber)); }
        }
    }
}
