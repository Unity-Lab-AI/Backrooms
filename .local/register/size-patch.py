import io

p = 'Mod/Rimrooms - Async Industries/1.6/Patches/RR_NativeGateProviders.xml'
s = io.open(p, encoding='utf-8-sig').read()

block = u"""      <!-- Owner direction 2026-09-29: "ther are 1x1 1x2 and 1x3 and 2x3 gate doors that
           allow differnt capabilities". The component is only ever attached here, so this
           file is the allowlist of what may become a gate, and the four legal footprints
           are enforced in code.

           Core's own OrnateDoor is 2x1, which was found by reading the installed game data
           rather than assumed. It means a 1x2 gate needs no mods at all. Dormant until
           designated, exactly like the doors above. -->
      <li Class="PatchOperationConditional">
        <xpath>Defs/ThingDef[defName="OrnateDoor"]/comps</xpath>
        <nomatch Class="PatchOperationAdd">
          <xpath>Defs/ThingDef[defName="OrnateDoor"]</xpath>
          <value><comps /></value>
        </nomatch>
      </li>
      <li Class="PatchOperationAdd">
        <xpath>Defs/ThingDef[defName="OrnateDoor"]/comps</xpath>
        <value>
          <li Class="RimroomsAsyncIndustries.Gate.CompProperties_RimroomsGate" />
        </value>
      </li>
      <!-- Anomaly's security door is also 2x1. Wrapped in a conditional rather than gated by
           name: without the DLC the def simply is not there, the condition does not match,
           and nothing is attempted. An unguarded add against an absent def logs an error. -->
      <li Class="PatchOperationConditional">
        <xpath>Defs/ThingDef[defName="SecurityDoor"]/comps</xpath>
        <match Class="PatchOperationAdd">
          <xpath>Defs/ThingDef[defName="SecurityDoor"]/comps</xpath>
          <value>
            <li Class="RimroomsAsyncIndustries.Gate.CompProperties_RimroomsGate" />
          </value>
        </match>
      </li>
"""

anchor = u'      <li Class="PatchOperationAdd">\n        <xpath>Defs/ThingDef[defName="CommsConsole" or defName="TableMachining"]/comps</xpath>'
assert anchor in s
assert 'OrnateDoor' not in s
s = s.replace(anchor, block + anchor, 1)

# Doors Expanded lives in its own operation outside the sequence: PatchOperationFindMod does
# nothing at all when the mod is absent, and their files are never touched. Defs and sizes
# were enumerated from the installed copy rather than remembered.
closing = u'  </Operation>\n</Patch>'
assert s.rstrip().endswith('</Patch>')
de = u"""  </Operation>
  <!-- Optional compatibility. PatchOperationFindMod applies nothing when Doors Expanded is
       not installed, and modifies none of its files when it is. Def names and footprints
       were read from the installed copy: PH_DoorDouble and PH_AutodoorDouble are 2x1,
       PH_DoorTriple and PH_AutodoorTriple are 3x1, PH_GateDoubleThick and PH_DoorBlastDoor
       are 2x1, and PH_DoorThickBlastDoor is 3x2 -- which is the 2x3 the owner named. The
       cloth curtains and the 1x1 jail door are deliberately not included: a curtain is not a
       gate, and Core already covers 1x1. -->
  <Operation Class="PatchOperationFindMod">
    <mods>
      <li>Doors Expanded</li>
    </mods>
    <match Class="PatchOperationAdd">
      <xpath>Defs/ThingDef[defName="PH_DoorDouble" or defName="PH_DoorTriple" or defName="PH_AutodoorDouble" or defName="PH_AutodoorTriple" or defName="PH_GateDoubleThick" or defName="PH_DoorBlastDoor" or defName="PH_DoorThickBlastDoor"]/comps</xpath>
      <value>
        <li Class="RimroomsAsyncIndustries.Gate.CompProperties_RimroomsGate" />
      </value>
    </match>
  </Operation>
</Patch>"""
s = s.rstrip()
assert s.endswith(closing.rstrip())
s = s[: -len(closing.rstrip())] + de + '\n'
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('patch file updated')

# Keyed string for the size readout.
p = 'Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Gate.xml'
s = io.open(p, encoding='utf-8-sig').read()
key = u'  <RR_Gate_FootprintReadout>Opening {0} wide, {1} cell(s) of machine ({2}).</RR_Gate_FootprintReadout>\n'
assert 'RR_Gate_FootprintReadout' not in s
s = s.replace(u'</LanguageData>', key + u'</LanguageData>', 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('keyed string added')
