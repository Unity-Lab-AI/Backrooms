# -*- coding: utf-8 -*-
"""Fix two defects the checkers caught in my own door-run code.

1. **A RUNTIME-BUILT KEYED STRING.** `RefuseRun(string suffix)` assembled `"RR_GateRun_" + suffix`,
   which `check-keyed-strings.py` refuses and is right to: a key made at run time cannot be checked
   in either direction, so a typo in one ships as a raw key on screen. **Fifth time this project
   has caught that pattern**, and `SoloGroupHints` carries a comment saying so about its own.

2. **THE WORD "doorway".** `check-info-cards.py` enforces the vocabulary: a plain door is a
   **door**, and the far-side arrival point is a **threshold**. I used "doorway" five times in
   player-facing text after already being corrected on that exact word earlier in this session.
   The word for what a run makes is the gate's **opening**, which is what `GateEntryCells` already
   calls it in its own documentation.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def edit(rel, pairs):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, '%s: anchor missing %r' % (rel, old[:70])
        assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('fixed %s (%d)' % (rel, len(pairs)))


RUN = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'GateDoorRun.cs')

# ------------------------------------------------------------------ 1. literal keys
edit(RUN, [
    (u'''        private static CompanyActionResult RefuseRun(string suffix)
        { return CompanyActionResult.Refused("RR_GateRun_" + suffix); }''',
     u'''        // Literal keys, never assembled. `check-keyed-strings.py` refused the concatenated
        // version and was right to: a key built at run time cannot be checked in either
        // direction, so a typo in one would ship as a raw key on screen. This is the FIFTH time
        // this project has caught that pattern, which is why the checker exists.'''),

    (u'            if (!IsDesignated) { return RefuseRun("NotAGate"); }\n'
     u'            if (IsRunExtension) { return RefuseRun("AlreadyAnExtension"); }\n'
     u'            if (IsOpening || IsSpinningUp) { return RefuseRun("ActiveCannotExtend"); }\n'
     u'            if (parent == null || !parent.Spawned || parent.Map == null) { return RefuseRun("NotAGate"); }',
     u'            if (!IsDesignated) { return CompanyActionResult.Refused("RR_GateRun_NotAGate"); }\n'
     u'            if (IsRunExtension) { return CompanyActionResult.Refused("RR_GateRun_AlreadyAnExtension"); }\n'
     u'            if (IsOpening || IsSpinningUp) { return CompanyActionResult.Refused("RR_GateRun_ActiveCannotExtend"); }\n'
     u'            if (parent == null || !parent.Spawned || parent.Map == null)\n'
     u'            { return CompanyActionResult.Refused("RR_GateRun_NotAGate"); }'),

    (u'            { return RefuseRun("NotADoor"); }\n'
     u'            if (door == parent) { return RefuseRun("SameDoor"); }\n'
     u'            if (door.def == null || door.def.size.x != 1 || door.def.size.z != 1)\n'
     u'            { return RefuseRun("NotSingleCell"); }',
     u'            { return CompanyActionResult.Refused("RR_GateRun_NotADoor"); }\n'
     u'            if (door == parent) { return CompanyActionResult.Refused("RR_GateRun_SameDoor"); }\n'
     u'            if (door.def == null || door.def.size.x != 1 || door.def.size.z != 1)\n'
     u'            { return CompanyActionResult.Refused("RR_GateRun_NotSingleCell"); }'),

    (u'            if (other == null) { return RefuseRun("NotADoor"); }\n'
     u'            if (other.IsDesignated) { return RefuseRun("AlreadyAGate"); }\n'
     u'            if (other.IsRunExtension) { return RefuseRun("AlreadyAnExtension"); }',
     u'            if (other == null) { return CompanyActionResult.Refused("RR_GateRun_NotADoor"); }\n'
     u'            if (other.IsDesignated) { return CompanyActionResult.Refused("RR_GateRun_AlreadyAGate"); }\n'
     u'            if (other.IsRunExtension)\n'
     u'            { return CompanyActionResult.Refused("RR_GateRun_AlreadyAnExtension"); }'),

    (u'                nativeRunExtensions.Remove(door);\n'
     u'                return RefuseRun("NotASolidRun");',
     u'                nativeRunExtensions.Remove(door);\n'
     u'                return CompanyActionResult.Refused("RR_GateRun_NotASolidRun");'),

    (u'            if (IsOpening || IsSpinningUp) { return RefuseRun("ActiveCannotExtend"); }\n'
     u'            if (nativeRunExtensions == null || nativeRunExtensions.Count == 0)',
     u'            if (IsOpening || IsSpinningUp)\n'
     u'            { return CompanyActionResult.Refused("RR_GateRun_ActiveCannotExtend"); }\n'
     u'            if (nativeRunExtensions == null || nativeRunExtensions.Count == 0)'),
])

# ------------------------------------------------------------------ 2. the vocabulary
KEYED = os.path.join('Mod', 'Rimrooms - Async Industries', '1.6', 'Languages', 'English', 'Keyed',
                     'RR_NativeGate.xml')
edit(KEYED, [
    (u'<RR_GateRun_Label>Doorway: {0} door(s), {1} wide</RR_GateRun_Label>',
     u'<RR_GateRun_Label>Opening: {0} door(s), {1} wide</RR_GateRun_Label>'),
    (u'Bind an ordinary door next to this gate into the same doorway, so a wider opening can be built out of several plain doors.',
     u'Bind an ordinary door next to this gate into the same opening, so a wider gate can be built out of several plain doors.'),
    (u'A doorway cannot be changed while the gate is working.',
     u'A gate’s opening cannot be changed while the gate is working.'),
    (u'That would not make a solid doorway.',
     u'That would not make a solid opening.'),
    (u'{0} is now a doorway of {1} doors, {2} cells wide.',
     u'{0} is now an opening of {1} doors, {2} cells wide.'),
])

# The comments in the C# say "doorway" too, and the checker only reads player-facing text -- but
# the vocabulary rule is about the mod's language, and a comment teaching the wrong word to the
# next reader is how the wrong word gets back into a string.
RUN_TEXT = os.path.join(REPO, RUN)
s = io.open(RUN_TEXT, encoding='utf-8').read()
before = s.count('doorway')
s = s.replace('doorway', 'opening')
io.open(RUN_TEXT, 'w', encoding='utf-8', newline='').write(s)
print('replaced %d comment use(s) of the banned word in %s' % (before, RUN))
