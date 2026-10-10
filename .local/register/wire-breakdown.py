# -*- coding: utf-8 -*-
"""Show the reserve breakdown, consuming two accessors nothing read."""
import io
import os
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(path, old, new, enc='utf-8-sig'):
    s = io.open(path, encoding=enc).read()
    assert old in s, '%s: anchor missing %r' % (os.path.basename(path), old[:70])
    assert s.count(old) == 1, '%s: anchor not unique' % os.path.basename(path)
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new, 1))


p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Gate', 'CompRimroomsGate.cs')
sub(p, u"""            if (NativeBindingFailureKey != null) { powerText += "\\n" + NativeBindingFailureKey.Translate(); }""",
u"""            // The breakdown, found by the live-effects sweep: `EmergencyReturnCostWattDays` and
            // `RecoveryOpeningCostWattDays` were public accessors read by NOTHING. The totals above
            // include them, so the player saw "this much to open and come home" without ever being
            // told how much of it was the coming home. That is the number that decides whether it
            // is safe to send anybody, so it is worth its own line.
            powerText += "\\n" + "RR_NativeGate_ReserveBreakdown".Translate(
                EmergencyReturnCostWattDays.ToString("F2"),
                RecoveryOpeningCostWattDays.ToString("F2"));
            if (NativeBindingFailureKey != null) { powerText += "\\n" + NativeBindingFailureKey.Translate(); }""")
print('breakdown wired into the gate readout')

p = os.path.join(REPO, 'Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English',
                 'Keyed', 'RR_NativeGate.xml')
s = io.open(p, encoding='utf-8-sig').read()
assert 'RR_NativeGate_ReserveBreakdown' not in s
key = (u'  <RR_NativeGate_ReserveBreakdown>Of that, {0} watt-days is held back for an emergency '
       u'return, and a recovery opening costs {1} watt-days.</RR_NativeGate_ReserveBreakdown>\n')
i = s.rindex(u'</LanguageData>')
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s[:i] + key + s[i:])
ET.parse(p)
print('keyed string added and parsed')
