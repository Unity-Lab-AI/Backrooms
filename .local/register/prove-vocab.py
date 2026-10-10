"""Prove the vocabulary rule catches each banned term, and leaves key names alone."""
import io
import subprocess
import sys

CHECK = ['tools/check-info-cards.py']
KEYED = 'Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Gate.xml'


def run():
    out = subprocess.run([sys.executable] + CHECK, capture_output=True, text=True)
    return out.returncode, out.stdout


def plant(needle, replacement, label, expect_fail=True):
    original = io.open(KEYED, encoding='utf-8-sig').read()
    assert needle in original, 'anchor missing for ' + label
    io.open(KEYED, 'w', encoding='utf-8-sig', newline='').write(
        original.replace(needle, replacement, 1))
    code, _ = run()
    io.open(KEYED, 'w', encoding='utf-8-sig', newline='').write(original)
    caught = code != 0
    print('  %-44s %s' % (label, 'CAUGHT' if caught else 'MISSED'))
    if expect_fail:
        assert caught, '%s was NOT caught: the rule does nothing' % label
    else:
        assert not caught, '%s was caught, but it must be allowed' % label


code, _ = run()
assert code == 0, 'the tree does not pass before planting'
print('baseline: PASS')
print('')
print('banned terms in displayed text:')

ANCHOR = '<RR_Gate_SpinUpComplete>Connection open.</RR_Gate_SpinUpComplete>'

plant(ANCHOR, '<RR_Gate_SpinUpComplete>Portal open.</RR_Gate_SpinUpComplete>',
      'a displayed value saying "portal"')

plant(ANCHOR, '<RR_Gate_SpinUpComplete>The machine gate is open.</RR_Gate_SpinUpComplete>',
      'a displayed value saying "machine gate"')

plant(ANCHOR, '<RR_Gate_SpinUpComplete>The doorway is open.</RR_Gate_SpinUpComplete>',
      'a displayed value saying "doorway"')

plant(ANCHOR, '<RR_Gate_SpinUpComplete>Use the gizmo to open it.</RR_Gate_SpinUpComplete>',
      'a displayed value saying "gizmo"')

print('')
print('things that must stay allowed:')

plant(ANCHOR, '<RR_Gate_PortalKeyNameIsFine>Connection open.</RR_Gate_PortalKeyNameIsFine>',
      'a KEY NAME containing "portal"', expect_fail=False)

plant(ANCHOR, '<RR_Gate_SpinUpComplete>Connection open at the threshold.</RR_Gate_SpinUpComplete>',
      'the blessed words gate, connection, threshold', expect_fail=False)

code, _ = run()
assert code == 0, 'the tree did not return to PASS'
print('')
print('restored: PASS')
print('PASS: every banned term is caught, key names and the blessed vocabulary are untouched')
