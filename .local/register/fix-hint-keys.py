# -*- coding: utf-8 -*-
"""Explicit hint keys, so the keyed-strings checker can actually verify them.

`"RR_Hint_" + id` built a key at runtime, and `check-keyed-strings.py` refused it: a constructed
key cannot be checked in either direction, so a typo in one would ship silently. The checker is
right, and the fix makes the keys literals.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'SoloGroupHints.cs')
s = io.open(p, encoding='utf-8-sig').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:70]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:70]
    s = s.replace(old, new, 1)


sub(u'''            Say("contact", true);
            Say("surface", AnyoneOnAnOrdinaryMap());
            Say("comms", HasPoweredCommsConsole());
            Say("doorsRunOut", KnowsACoordinateAtNaturalLimit());''',
u'''            // Keys are literals, not built from the id. `check-keyed-strings.py` refused the
            // concatenated version and was right to: a key assembled at runtime cannot be checked
            // in either direction, so a typo in one would have shipped as a raw key on screen.
            Say("contact", "RR_Hint_Contact", true);
            Say("surface", "RR_Hint_Surface", AnyoneOnAnOrdinaryMap());
            Say("comms", "RR_Hint_Comms", HasPoweredCommsConsole());
            Say("doorsRunOut", "RR_Hint_DoorsRunOut", KnowsACoordinateAtNaturalLimit());''')

sub(u'''        private void Say(string id, bool condition)
        {
            if (!condition || hintsSaid.Contains(id)) { return; }
            hintsSaid.Add(id);
            string key = "RR_Hint_" + id;
            Messages.Message(key.Translate(), MessageTypeDefOf.NeutralEvent, false);
            RecordEvent("RR_Event_SoloGroupHint", id);
        }''',
u'''        private void Say(string id, string key, bool condition)
        {
            if (!condition || hintsSaid.Contains(id)) { return; }
            hintsSaid.Add(id);
            Messages.Message(key.Translate(), MessageTypeDefOf.NeutralEvent, false);
            RecordEvent("RR_Event_SoloGroupHint", id);
        }''')

io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('hint keys are now literals')

# Rename the strings to match.
p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_Scenario.xml')
s = io.open(p, encoding='utf-8-sig').read()
for old, new in [('RR_Hint_contact', 'RR_Hint_Contact'), ('RR_Hint_surface', 'RR_Hint_Surface'),
                 ('RR_Hint_comms', 'RR_Hint_Comms'), ('RR_Hint_doorsRunOut', 'RR_Hint_DoorsRunOut')]:
    assert old in s, old
    s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
import xml.etree.ElementTree as ET
ET.parse(p)
print('hint strings renamed and parsed')
