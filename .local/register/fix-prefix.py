import io, re

p = 'tools/check-info-cards.py'
s = io.open(p, encoding='utf-8').read()

# The previous edit wrote a literal backspace byte where a word boundary was meant, so the
# pattern demanded a 0x08 after the keyword and matched nothing. Word boundary is avoided
# entirely now: a negative lookahead for another letter says the same thing and survives
# being written through a shell.
lines = s.split('\n')
for index, line in enumerate(lines):
    if line.startswith('PLACEHOLDER_PREFIX'):
        lines[index] = ('PLACEHOLDER_PREFIX = re.compile('
                        + repr('^\\s*(todo|tbd|tba|fixme|xxx|placeholder)(?![A-Za-z])')
                        + ', re.I)')
        break
else:
    raise AssertionError('PLACEHOLDER_PREFIX line not found')

s = '\n'.join(lines)
assert '\x08' not in s, 'a stray backspace byte is still in the file'
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('prefix rule rewritten without a word-boundary escape')
