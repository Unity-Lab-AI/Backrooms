import io

def insert(path, block):
    s = io.open(path, encoding='utf-8-sig').read()
    assert '</LanguageData>' in s, path
    assert block.strip().split('\n')[1].strip() not in s, 'already present: ' + path
    s = s.replace('</LanguageData>', block + '</LanguageData>', 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(s)
    print('updated ' + path)

base = 'Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/'

history = u"""
  <RR_GateHistory_Dial>Dial {0}</RR_GateHistory_Dial>
  <RR_GateHistory_CoordinateGone>That space is no longer on this branch's list of coordinates. The gate still remembers dialling it, but there is nothing left to connect to.</RR_GateHistory_CoordinateGone>
"""

gate = u"""
  <RR_Gate_SpinUpStarted>Bringing up a connection to {0}. The operator must stay on the console until it is open.</RR_Gate_SpinUpStarted>
  <RR_Gate_SpinUpComplete>Connection open.</RR_Gate_SpinUpComplete>
  <RR_Gate_SpinUpLapsed>The connection lost its charge before it opened. The address is still remembered and can be dialled again.</RR_Gate_SpinUpLapsed>
  <RR_Gate_SpinUpAborted>Spin-up stopped. The address is still remembered.</RR_Gate_SpinUpAborted>
  <RR_Gate_SpinUpWaiting>The connection is fully charged and waiting: {0}</RR_Gate_SpinUpWaiting>
  <RR_Gate_SpinUpBusy>This gate is already bringing up a different connection.</RR_Gate_SpinUpBusy>
  <RR_Gate_SpinUpReadout>Spinning up to {0}: {1} / {2} ({3})</RR_Gate_SpinUpReadout>
  <RR_Gate_SpinUpHeldReadout>Charged and waiting to open to {0}.</RR_Gate_SpinUpHeldReadout>
  <RR_Gate_SpinUpClimbing>climbing</RR_Gate_SpinUpClimbing>
  <RR_Gate_SpinUpBleeding>losing charge</RR_Gate_SpinUpBleeding>
  <RR_Gate_AbortSpinUpLabel>Stop spin-up</RR_Gate_AbortSpinUpLabel>
  <RR_Gate_AbortSpinUpDesc>Stop bringing up this connection. The work done so far is lost, but the address stays in this gate's history and can be dialled again.</RR_Gate_AbortSpinUpDesc>
  <RR_Event_GateSpinUpStarted>Gate spin-up started ({0} work required)</RR_Event_GateSpinUpStarted>
  <RR_Event_GateSpinUpCompleted>Gate spin-up completed</RR_Event_GateSpinUpCompleted>
  <RR_Event_GateSpinUpLapsed>Gate spin-up lapsed</RR_Event_GateSpinUpLapsed>
  <RR_Event_GateSpinUpAborted>Gate spin-up stopped</RR_Event_GateSpinUpAborted>
"""

portals = u"""
  <RR_Portals_SpinUpRunning>Bringing up a connection: {0}% charged. The assigned operator must stay on the console.</RR_Portals_SpinUpRunning>
  <RR_Portals_AbortSpinUp>Stop spin-up</RR_Portals_AbortSpinUp>
"""

insert(base + 'RR_GateHistory.xml', history)
insert(base + 'RR_Gate.xml', gate)
insert(base + 'RR_Portals.xml', portals)
