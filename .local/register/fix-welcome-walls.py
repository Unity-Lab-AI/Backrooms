import io

NL = '&#10;'  # RimWorld renders a real newline; the entity keeps the XML on one tidy line.

FIXES = [
 ('Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Scenario.xml',
  'Your Async Industries branch is operational. The gate is still incomplete. Use Operations '
  'to review your staff, materials, branch account, and first survey. Your company allocation '
  'is an account balance; receiving contains your physical supplies. Finish the gate, assign a '
  'capable operator, calibrate it, and prepare the return route before dispatching a crew. '
  'Native Work, Research, Architect, and pawn controls remain available.',

  'Your Async Industries branch is operational. The gate is still incomplete.' + NL + NL +
  'Use Operations to review your staff, materials, branch account and first survey. Your '
  'company allocation is an account balance; receiving holds your physical supplies.' + NL + NL +
  'Finish the gate, assign a capable operator, calibrate it, and prepare the return route '
  'before you dispatch a crew.' + NL + NL +
  'Native Work, Research, Architect and pawn controls all remain available.'),

 ('Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_StartupSetup.xml',
  'Your selected people have arrived and the branch allocation is recorded. Native starting '
  'supplies are near the arrival point; equipped and carried items remain with their owners. '
  'The fixed facility is separate from those supplies. Review Operations, assign a capable '
  'operator, complete the gate, and prepare a real return route. A small or underqualified '
  'roster may need recruitment or training first. Native Work, Research, Architect and pawn '
  'controls remain available.',

  'Your selected people have arrived and the branch allocation is recorded.' + NL + NL +
  'Native starting supplies are near the arrival point, and equipped or carried items stay '
  'with their owners. The fixed facility is separate from those supplies.' + NL + NL +
  'Review Operations, assign a capable operator, complete the gate and prepare a real return '
  'route. A small or underqualified roster may need recruitment or training first.' + NL + NL +
  'Native Work, Research, Architect and pawn controls all remain available.'),
]

for path, old, new in FIXES:
    s = io.open(path, encoding='utf-8-sig').read()
    assert old in s, path + ' :: text not found verbatim'
    s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(s)
    print('reflowed ' + path.split('/')[-1])
