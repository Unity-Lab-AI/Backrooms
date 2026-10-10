"""Prove check-doc-conformance.py fails on each fault it claims to catch, and on nothing else.

A checker that only ever passes manufactures confidence. Each rule is planted separately so
a rule that silently does nothing cannot hide behind a rule that works, and the dated-record
exemption is planted too -- an exemption that leaked would be worse than no check.
"""
import io
import subprocess
import sys

CHECK = ['tools/check-doc-conformance.py']
NL = chr(10)


def run():
    out = subprocess.run([sys.executable] + CHECK, capture_output=True, text=True)
    return out.returncode, out.stdout


def plant(path, needle, replacement, label, expect_fail=True):
    original = io.open(path, encoding='utf-8').read()
    assert needle in original, 'anchor missing in %s for %s' % (path, label)
    io.open(path, 'w', encoding='utf-8', newline='').write(original.replace(needle, replacement, 1))
    code, _ = run()
    io.open(path, 'w', encoding='utf-8', newline='').write(original)
    caught = code != 0
    print('  %-46s %s' % (label, 'CAUGHT' if caught else 'MISSED'))
    if expect_fail:
        assert caught, '%s was NOT caught: the rule does nothing' % label
    else:
        assert not caught, '%s was caught, but it should be exempt' % label


code, _ = run()
assert code == 0, 'the tree does not pass before planting; fix that first'
print('baseline: PASS')
print('')
print('planted faults:')

plant('README.md',
      'Current development version: 0.10.0-dev',
      'Current development version: 0.4.1-dev',
      'a stale version claim')

plant('docs/PUBLISHING.md',
      'feature/connected-colony-portals',
      'feature/preproduction-handoff',
      'a retired working-branch name')

plant('docs/HOWTO.md',
      '## 1. Two documentation layers, one project',
      '## 1. Two documentation layers, one project' + NL + NL + 'Build the RR_MachineGate first.',
      'a retired def named as if it ships')

plant('docs/HOWTO.md',
      '## 2. Starting a session',
      '## 2. Starting a session' + NL + NL + 'Run all four checkers before pushing.' + NL,
      'an out-of-date checker count')

plant('docs/FINALIZED.md',
      '### Build evidence',
      '### Build evidence' + NL + NL
      + '> *"this is a planted owner direction that was never queued anywhere"*' + NL,
      'a direction archived but never queued')

print('')
print('dated records must stay exempt:')

plant('docs/FINALIZED.md',
      '### Build evidence',
      '### Build evidence' + NL + NL
      + 'All four checkers pass and RR_MachineGate is built on '
      + 'feature/preproduction-handoff at 0.4.1-dev.' + NL,
      'four faults planted in a dated record', expect_fail=False)

code, _ = run()
assert code == 0, 'the tree did not return to PASS after restoring'
print('')
print('restored: PASS')
print('PASS: every rule catches its own fault, and dated records are genuinely exempt')
