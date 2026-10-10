import io

p = 'tools/check-doc-conformance.py'
lines = io.open(p, encoding='utf-8').read().split('\n')

out = []
replaced_count = False
replaced_phrases = False
skip = 0
for index, line in enumerate(lines):
    if skip:
        skip -= 1
        continue
    if line.startswith('CHECKER_COUNT ='):
        out.append('CHECKER_COUNT = 6')
        replaced_count = True
        continue
    if line.startswith('CHECKER_PHRASES = ('):
        # Replace the whole tuple: it spans to its closing paren.
        end = index
        while not lines[end].strip() == ')':
            end += 1
        skip = end - index
        out.append('CHECKER_PHRASES = (')
        out.append('    re.compile(' + repr(r'\b(all\s+)?four checkers\b') + ', re.I),')
        out.append('    re.compile(' + repr(r'\b(all\s+)?five checkers\b') + ', re.I),')
        out.append(')')
        replaced_phrases = True
        continue
    out.append(line)

assert replaced_count, 'CHECKER_COUNT line not found'
assert replaced_phrases, 'CHECKER_PHRASES tuple not found'
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(out))
print('checker count set to 6 and phrase list widened')
