import io

# --- the message should quote what it actually found ----------------------
p = 'tools/check-doc-conformance.py'
s = io.open(p, encoding='utf-8').read()
old = '''        for pattern in CHECKER_PHRASES:
            if pattern.search(text):
                problems.append("%s says \\"four checkers\\"; there are %d, and a reader will skip one"
                                % (rel, CHECKER_COUNT))
                break'''
new = '''        for pattern in CHECKER_PHRASES:
            found = pattern.search(text)
            if found:
                problems.append("%s says %r; there are %d, and a reader following that will skip one"
                                % (rel, found.group(0), CHECKER_COUNT))
                break'''
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('message now quotes the offending phrase')

# --- the ritual runs six checks now ---------------------------------------
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('| Checkers | **five**, all passing |', '| Checkers | **six**, all passing |'),
 ('6. **All five checkers**: `check-package-integrity.py`, `check-keyed-strings.py`, '
  '`check-dlc-gating.py`, `check-info-cards.py`, `research/audit-gate0.py`.',
  '6. **All six checkers**: `check-package-integrity.py`, `check-keyed-strings.py`, '
  '`check-dlc-gating.py`, `check-info-cards.py`, `check-doc-conformance.py`, '
  '`research/audit-gate0.py`.'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md ritual updated to six')
