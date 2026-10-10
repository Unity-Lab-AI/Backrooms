# -*- coding: utf-8 -*-
"""The short address code becomes the only identifier a player ever sees.

Owner, 2026-10-04: *"we dont need things like long string corrdinates list in
the operations panel thing like that arnet needed only like the !A-01 address
code is needed to be displayed to thew player and save able and useable"*.

The code already existed -- `CoordinateRecord.label` has been `AI-01`, `AI-02`
since the first version. **What leaked was the raw id**, in four places, and the
worst of them put it on a button and in a list beside the code it duplicates.
"""
import io
import sys

NL = chr(10)

RECORDS = "src/RimroomsAsyncIndustries/Company/CampaignRecords.cs"
PORTALS = "src/RimroomsAsyncIndustries/UI/OperationsPortalNetwork.cs"
RECOVERY = "src/RimroomsAsyncIndustries/UI/OperationsEvidenceRecovery.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"

ADDRESS_PROPERTY = '''
        /// <summary>
        /// **THE ONLY IDENTIFIER A PLAYER EVER SEES.**
        ///
        /// Owner, 2026-10-04: *"we dont need things like long string corrdinates list in the
        /// operations panel thing like that arnet needed only like the !A-01 address code is
        /// needed to be displayed to thew player and save able and useable"*.
        ///
        /// The code itself is not new — `label` has been `AI-01`, `AI-02` and so on since the
        /// first version, assigned in discovery order so it is short, unique within a branch and
        /// stable across a reload. **What was wrong is that the raw `id` leaked out beside it**:
        /// a thirty-character internal string on a button, and in an address list that printed
        /// the connection id, the coordinate id and the code all on one line.
        ///
        /// So this exists to be the thing every readout asks for, rather than each one choosing
        /// between `Label`, `Id` and a fallback. A record with no label falls back to its id
        /// because a row with no identifier at all is worse than an ugly one — and that is a
        /// repair case, not a display choice.
        /// </summary>
        public string AddressCode
        {
            get { return string.IsNullOrEmpty(label) ? id : label; }
        }
'''

EDITS = [
    # ------------------------------------------------------------------- the property itself
    (RECORDS,
     "        public string Id { get { return id; } }" + NL
     + "        public string Label { get { return label; } }",
     "        public string Id { get { return id; } }" + NL
     + "        public string Label { get { return label; } }" + NL
     + ADDRESS_PROPERTY),

    # -------------------------------------------------- the long id on the open-session button
    (PORTALS,
     '                        if (listing.ButtonText("RR_Portals_OpenSession".Translate(captured.CoordinateId)))',
     '                        // **THE CODE, NOT THE RAW ID.** This printed a thirty-character'
     + NL + '                        // internal coordinate string on a button a player presses.'
     + NL + '                        if (listing.ButtonText("RR_Portals_OpenSession".Translate('
     + NL + '                            AddressCodeOf(campaign, captured.CoordinateId))))'),

    (PORTALS,
     "                            step.Source.Anchor.LabelCap, captured.CoordinateId)))",
     "                            step.Source.Anchor.LabelCap,"
     + NL + "                            AddressCodeOf(campaign, captured.CoordinateId))))"),

    # ----------------------------------------------- the address list, which printed three ids
    (PORTALS,
     '                listing.Label("RR_Portals_AddressLine".Translate(address.Id, address.CoordinateId, kind,'
     + NL + '                    AvailabilityLabel(network.Availability(address))));',
     '                // **ONE IDENTIFIER PER ROW.** This printed the connection id AND the raw'
     + NL + '                // coordinate id AND the kind AND the status -- four fields, two of them'
     + NL + '                // internal strings the player can do nothing with. The code is the one'
     + NL + '                // they dial; the connection id moved to the row tooltip for diagnosis.'
     + NL + '                Rect addressRow = listing.GetRect(Text.LineHeight);'
     + NL + '                Widgets.Label(addressRow, "RR_Portals_AddressLine".Translate('
     + NL + '                    AddressCodeOf(campaign, address.CoordinateId), kind,'
     + NL + '                    AvailabilityLabel(network.Availability(address))));'
     + NL + '                TooltipHandler.TipRegion(addressRow,'
     + NL + '                    "RR_Portals_AddressTip".Translate(address.Id, address.CoordinateId));'),

    # --------------------------------------------- the selected-coordinate line, code only
    (PORTALS,
     '            listing.Label("RR_Portals_SelectedCoordinate".Translate(coordinate.Label ?? coordinate.Id, coordinate.Id));',
     '            // The code alone. This showed the code and then the raw id in brackets after it.'
     + NL + '            listing.Label("RR_Portals_SelectedCoordinate".Translate(coordinate.AddressCode));'),

    # ------------------------------------------------------------- the recovery pane fallback
    (RECOVERY,
     '                listing.Label("RR_EvidenceRecovery_Identity".Translate(coordinate?.Label ?? id,',
     '                listing.Label("RR_EvidenceRecovery_Identity".Translate('
     + NL + '                    coordinate == null ? id : coordinate.AddressCode,'),
]

HELPER = '''
        /// <summary>
        /// The player-facing address code for a coordinate id, asked of the record that owns it.
        ///
        /// Owner, 2026-10-04: *"only like the !A-01 address code is needed to be displayed to
        /// thew player"*. A readout holding a coordinate **id** -- a portal connection does, and
        /// so does an expedition record -- has to turn it into something a player recognises, and
        /// doing that inline in each place is how three panes ended up printing three different
        /// things. Falls back to the id when the record is gone, because a row with no identifier
        /// is worse than an ugly one.
        /// </summary>
        private static string AddressCodeOf(RimroomsCampaignComponent campaign, string coordinateId)
        {
            if (campaign == null || string.IsNullOrEmpty(coordinateId)) { return coordinateId; }
            for (int index = 0; index < campaign.Coordinates.Count; index++)
            {
                CoordinateRecord record = campaign.Coordinates[index];
                if (record != null && record.Id == coordinateId) { return record.AddressCode; }
            }
            return coordinateId;
        }
'''

STRINGS = [
    ("RR_Portals_AddressLine", "{0} — {1}, {2}"),
    ("RR_Portals_AddressTip", "Connection {0}\\n\\nCoordinate {1}\\n\\nInternal identifiers, "
                              "for diagnosis. The address code is what you dial."),
    ("RR_Portals_SelectedCoordinate", "Selected: {0}"),
]

problems = 0
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8").read()
    found = text.count(old)
    if found != 1:
        print("NOT UNIQUE (%d) in %s: %s" % (found, path.split("/")[-1], old.strip()[:70]))
        problems += 1
        continue
    io.open(path, "w", encoding="utf-8", newline=NL).write(text.replace(old, new))
    print("ok %s: %s" % (path.split("/")[-1], old.strip()[:66]))

# the helper, once, at the end of the portal pane's class
text = io.open(PORTALS, encoding="utf-8").read()
if "private static string AddressCodeOf(" not in text:
    marker = "        private static string KindLabelKey("
    if text.count(marker) != 1:
        print("cannot place the helper: KindLabelKey anchor is not unique")
        problems += 1
    else:
        at = text.index(marker)
        io.open(PORTALS, "w", encoding="utf-8", newline=NL).write(
            text[:at] + HELPER.lstrip(NL) + NL + text[at:])
        print("ok OperationsPortalNetwork.cs: AddressCodeOf helper added")

# the keyed strings: two rewritten, one new
text = io.open(KEYED, encoding="utf-8-sig").read()
import re
for key, value in STRINGS:
    pattern = re.compile(r"[ \t]*<" + key + r">.*?</" + key + r">")
    line = "  <" + key + ">" + value + "</" + key + ">"
    if pattern.search(text):
        text = pattern.sub(line, text, count=1)
    else:
        close = "</LanguageData>"
        at = text.rindex(close)
        text = text[:at] + line + NL + text[at:]
io.open(KEYED, "w", encoding="utf-8", newline=NL).write(text)
print("keyed strings updated")

if problems:
    sys.exit(1)
