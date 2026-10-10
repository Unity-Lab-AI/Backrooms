"""Unify the player-facing vocabulary on gate / connection / threshold.

Owner direction, 2026-09-29, verbatim: *"ive used alot of differnt terms for the gates.. from
portals, gates, doors , the machine, the gizmo, ect ect we need a unified name throught the
entire mode in all the equipment information and cards of things items resources and
buildings and all things that our mod touches"*, answered at the fork as three words for
three genuinely different things.

Key names are not touched. A player never reads `RR_Portals_Heading`, and renaming keys would
be churn with real save and DefInjected risk for no reader benefit. Only displayed text moves.
"""
import glob, io, os, re

ROOTS = ['Mod/Rimrooms - Async Industries/1.6/Languages',
         'Mod/Rimrooms - Async Industries/1.6/Defs']

# Ordered: longer phrases first so a general rule cannot eat a specific one.
GLOBAL = [
    # The machine gate was the retired RR_MachineGate. There is one kind of gate now.
    ('machine gate console', 'gate console'),
    ('the machine gate', 'the gate'),
    ('Machine gate', 'Gate'),
    ('machine gate', 'gate'),
    # The link a gate holds open is a connection, and the pane lists both.
    ('portal network', 'connection network'),
    ('Portal network', 'Gates and connections'),
    ('portal window', 'connection window'),
    ('portal operation', 'gate operation'),
    ('portal aura', 'gate aura'),
    ('portal motion', 'gate motion'),
    ('natural portal', 'natural gate'),
    ('Portal address', 'Gate address'),
    # A plain door is a door. The far side is a threshold. "Doorway" was neither.
    ('doorways', 'doors'),
    ('Doorway', 'Door'),
    ('doorway', 'door'),
]

# Sentences where a word swap alone would read wrong.
EXPLICIT = [
    ('Next objective: prepare the machine,', 'Next objective: prepare the gate,'),
    ('Open Machine operations', 'Open gate operations'),
    ('The gate machine is no longer available.', 'The gate is no longer available.'),
    ('The machine assembly is complete.', 'The gate assembly is complete.'),
    ('The machine calibration is complete.', 'The gate calibration is complete.'),
    ("from the machine's reserve", "from the gate's reserve"),
    ('cell(s) of machine', 'cell(s) of gate'),
    ('No company machine was found', 'No company gate was found'),
    ('View machine and its controls', 'View the gate and its controls'),
    ('in Machine controls', 'in Gate controls'),
    ('company operator to the machine,', 'company operator to the gate,'),
    ('The powered console and machine must remain', 'The powered console and gate must remain'),
    ('That door already has a machine on it.', 'That door is already a gate.'),
    ('The machine is not advanced enough', 'The gate is not advanced enough'),
    ('The machine is still incomplete.', 'The gate is still incomplete.'),
    ('proof that a connection is active', 'proof that a connection is active'),
]

changed = {}
for root in ROOTS:
    for path in sorted(glob.glob(os.path.join(root, '**', '*.xml'), recursive=True)):
        original = io.open(path, encoding='utf-8-sig').read()
        s = original
        for old, new in GLOBAL + EXPLICIT:
            s = s.replace(old, new)
        # Key names and class paths must survive untouched.
        for guard in ('RR_Portals_', 'RR_PortalTravel_', 'RR_PortalAddress_',
                      'RR_PortalCrossing_', 'RR_AssembleMachineGate', 'RR_Frontier_IsAMachineGate',
                      'RimroomsAsyncIndustries'):
            assert original.count(guard) == s.count(guard), \
                '%s: key or class name %r was altered' % (path, guard)
        if s != original:
            io.open(path, 'w', encoding='utf-8-sig', newline='').write(s)
            changed[path] = sum(1 for a, b in zip(original.split('\n'), s.split('\n')) if a != b)

print('files changed: %d' % len(changed))
for path in sorted(changed):
    print('  %-72s %d line(s)' % (os.path.relpath(path).replace(os.sep, '/')[-72:], changed[path]))
