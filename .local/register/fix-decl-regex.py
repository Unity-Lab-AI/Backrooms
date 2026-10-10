# -*- coding: utf-8 -*-
"""Repair the DECL regex, mangled by a shell heredoc. Eighth time. Write tool only, from now on."""
import ast
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-live-effects.py')
s = io.open(p, encoding='utf-8').read()

broken_start = 'DECL = re.compile(r"public'
i = s.index(broken_start)
j = s.index('exposed = []', i)

# \s* already matches a newline, so the alternation the heredoc destroyed was never needed.
fixed = 'DECL = re.compile(r"public\\s+(?:float|int|bool|string)\\s+(\\w+)\\s*\\{")\n'

s = s[:i] + fixed + s[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('DECL regex repaired')
ast.parse(s)
print('proof-live-effects.py parses clean')
