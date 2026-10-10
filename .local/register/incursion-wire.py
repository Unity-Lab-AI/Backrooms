import io

def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:70]
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('patched ' + path.split('/')[-1])

G = 'src/RimroomsAsyncIndustries/Gate/'

# The per-opening latch lives with the portal session, because that is what resets it.
patch(G + 'PortalGateOpening.cs', [
 ('        private bool portalOwnerFault;',
  '        private bool portalOwnerFault;\n'
  '\n'
  '        /// <summary>\n'
  '        /// Whether something has already come through on this opening.\n'
  '        ///\n'
  '        /// One per opening, so **closing the gate is a countermeasure that works** and is\n'
  '        /// learnable from a single incident. It is cleared when the session ends rather than\n'
  '        /// on a timer, which is what makes "close it and reopen" the deliberate cost.\n'
  '        /// </summary>\n'
  '        private bool incursionSpent;\n'
  '        public bool IncursionSpentThisOpening { get { return incursionSpent; } }\n'
  '        internal void NoteIncursionSpent() { incursionSpent = true; }'),
 ('            Scribe_Values.Look(ref portalOpeningSequence, "rr_gatePortalOpeningSequence", 0);',
  '            Scribe_Values.Look(ref portalOpeningSequence, "rr_gatePortalOpeningSequence", 0);\n'
  '            Scribe_Values.Look(ref incursionSpent, "rr_gateIncursionSpent", false);'),
 ('            portalOpeningSequence++;\n'
  '            portalConnectionId = connectionId;\n'
  '            portalOpeningId = nextId;',
  '            portalOpeningSequence++;\n'
  '            portalConnectionId = connectionId;\n'
  '            portalOpeningId = nextId;\n'
  '            incursionSpent = false;'),
])

patch(G + 'CompRimroomsGate.cs', [
 # Cleared with the session, so a reopened gate is a fresh opening in every sense.
 ('            activeExpeditionId = null;\n'
  '            portalOpeningId = null;\n'
  '            portalConnectionId = null;',
  '            activeExpeditionId = null;\n'
  '            portalOpeningId = null;\n'
  '            portalConnectionId = null;\n'
  '            ClearIncursionSpent();'),
 # Checked while a session is live, after the ramp and before the countdown.
 ('            // Before the opening block, because a ramp only exists while the gate is closed and\n'
  '            // its completion is what opens one.\n'
  '            TickSpinUp();',
  '            // Before the opening block, because a ramp only exists while the gate is closed and\n'
  '            // its completion is what opens one.\n'
  '            TickSpinUp();\n'
  '            Threats.GateIncursion.Tick(this);'),
])

# ClearIncursionSpent lives beside the latch it clears.
p = G + 'PortalGateOpening.cs'
s = io.open(p, encoding='utf-8').read()
old = '        internal void NoteIncursionSpent() { incursionSpent = true; }'
new = ('        internal void NoteIncursionSpent() { incursionSpent = true; }\n'
       '        private void ClearIncursionSpent() { incursionSpent = false; }')
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('latch reset added')

# Keyed strings.
p = 'Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml'
s = io.open(p, encoding='utf-8-sig').read()
add = (
u'  <RR_Incursion_Label>Something came through the gate</RR_Incursion_Label>\n'
u'  <RR_Incursion_Text>{0} followed your people to the doorway and stepped through {1} behind them. It is in the facility now, and it will behave like anything else that gets inside. Closing a connection before something reaches the threshold is what stops this.</RR_Incursion_Text>\n'
u'  <RR_Incursion_NotEligible>Nothing there can cross.</RR_Incursion_NotEligible>\n'
u'  <RR_Incursion_NoOpening>A closed gate is a wall.</RR_Incursion_NoOpening>\n'
u'  <RR_Incursion_AlreadySpent>Something has already come through on this opening.</RR_Incursion_AlreadySpent>\n'
u'  <RR_Incursion_BandTooLow>This space is not yet bad enough for anything to follow you home.</RR_Incursion_BandTooLow>\n'
u'  <RR_Incursion_TechTooLow>The machine is not advanced enough to hold a connection something else could use.</RR_Incursion_TechTooLow>\n')
assert 'RR_Incursion_Label' not in s
s = s.replace(u'</LanguageData>', add + u'</LanguageData>', 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('keyed strings added')
