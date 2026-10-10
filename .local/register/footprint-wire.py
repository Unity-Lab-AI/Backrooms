import io

def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:60]
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('patched ' + path.split('/')[-1])

G = 'src/RimroomsAsyncIndustries/Gate/'

patch(G + 'CompRimroomsGate.cs', [
 ('{ get { return IsOpening && !IsEmergency ? GateProps.openingPowerDrawWatts : 0f; } }',
  '{ get { return IsOpening && !IsEmergency ? OpeningPowerDrawWatts : 0f; } }'),
 ('            string ramp = SpinUpReadout();',
  '            string ramp = SpinUpReadout();\n            string footprint = FootprintReadout();'),
 ('new[] { status, operatorText, cutoffText, serviceText, powerText, ramp, active }',
  'new[] { status, footprint, operatorText, cutoffText, serviceText, powerText, ramp, active }'),
])

patch(G + 'GateSpinUp.cs', [
 ('            float required = GateProps.dialSpinUpWorkRequired;',
  '            // Scaled by the whole footprint, for the same reason the power draw is: a bigger\n'
  '            // gate is more machine to energise, and the owner made "costs more to run" a\n'
  '            // condition of the larger sizes rather than a side effect of them.\n'
  '            float required = GateProps.dialSpinUpWorkRequired * GateCellCount;'),
])
