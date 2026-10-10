"""One-off: give the eleven remaining events the readable values their text names."""
S = "src/RimroomsAsyncIndustries/"


def ed(path, old, new):
    p = S + path
    s = open(p, encoding="utf-8").read()
    assert s.count(old) == 1, (path, old[:60], s.count(old))
    open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))


ed("Company/CampaignServices.cs",
   'RecordEvent("RR_Event_CoordinateDiscovered", id, discoveryId);',
   'RecordEvent("RR_Event_CoordinateDiscovered", id, created.Label, discoveryId);')
ed("Company/EvidenceInterview.cs",
   '''RecordEvent("RR_Event_AccountFiled", record.coordinateId,
                speaker.LabelShortCap.ToString(), interviewer.LabelShortCap.ToString());''',
   '''RecordEvent("RR_Event_AccountFiled", record.coordinateId,
                CoordinateLabelOrId(record.coordinateId),
                speaker.LabelShortCap.ToString(), interviewer.LabelShortCap.ToString());''')
ed("Gate/GateDoorRun.cs",
   '''NativeCampaign?.RecordEvent("RR_Event_GateRunExtended", parent.LabelShortCap,
                RunDoorCount.ToString(), GateWidth.ToString());''',
   '''NativeCampaign?.RecordEvent("RR_Event_GateRunExtended", parent.LabelShortCap,
                parent.LabelShortCap, RunDoorCount.ToString(), GateWidth.ToString());''')
ed("Generation/CoordinateRelease.cs",
   'campaign.RecordEvent("RR_Event_CoordinateReleased", coordinate.Id);',
   'campaign.RecordEvent("RR_Event_CoordinateReleased", coordinate.Id, coordinate.Label);')
ed("Generation/ExplorationMapComponent.cs",
   '{ campaign.RecordEvent("RR_Event_ExplorationComplete", coordinate.Id); }',
   '{ campaign.RecordEvent("RR_Event_ExplorationComplete", coordinate.Id, coordinate.Label); }')
ed("Portals/NaturalFrontierService.cs",
   'campaign.RecordEvent("RR_Event_FrontierDiscovered", discovered.Id, origin.OriginId);',
   'campaign.RecordEvent("RR_Event_FrontierDiscovered", discovered.Id, discovered.Label,\n                    campaign.CoordinateLabelOrId(origin.OriginId));')
p = S + "Portals/PortalAddressService.cs"
s = open(p, encoding="utf-8").read()
assert s.count('campaign.RecordEvent("RR_Event_PortalAddressRegistered", id, coordinate.Id);') == 2
s = s.replace('campaign.RecordEvent("RR_Event_PortalAddressRegistered", id, coordinate.Id);',
              'campaign.RecordEvent("RR_Event_PortalAddressRegistered", id, id, coordinate.Label);')
open(p, "w", encoding="utf-8").write(s)
ed("Portals/PortalAddressService.cs",
   'campaign.RecordEvent("RR_Event_PortalThresholdRepaired", coordinate.Id, operationId);',
   'campaign.RecordEvent("RR_Event_PortalThresholdRepaired", coordinate.Id, coordinate.Label,\n                operationId);')
ed("Procurement/RimroomsProcurementComponent.cs",
   'campaign.RecordEvent("RR_Event_ProcurementRedirected", order.id, receivingZone.label);',
   'campaign.RecordEvent("RR_Event_ProcurementRedirected", order.id, order.id, receivingZone.label);')
ed("Threats/AnomalyEventService.cs",
   '{ campaign.RecordEvent("RR_Event_AnomalyFired", coordinate.Id, definition.LabelCap.ToString()); }',
   '{ campaign.RecordEvent("RR_Event_AnomalyFired", coordinate.Id, coordinate.Label,\n                definition.LabelCap.ToString()); }')
# The helper two of them use: a coordinate's label from its id, or the id when it is not one.
ed("Company/CampaignServices.cs",
   '''        internal void RecordEvent(string messageKey, string relatedId, params string[] arguments)''',
   '''        /// <summary>A coordinate's label for a message, or the id itself when it names no coordinate.</summary>
        internal string CoordinateLabelOrId(string id)
        {
            if (string.IsNullOrEmpty(id)) { return id ?? ""; }
            foreach (CoordinateRecord coordinate in Coordinates)
            {
                if (coordinate != null && coordinate.Id == id) { return coordinate.Label; }
            }
            return id;
        }

        internal void RecordEvent(string messageKey, string relatedId, params string[] arguments)''')
print("patched")
