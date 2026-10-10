# -*- coding: utf-8 -*-
"""Repair code_only(), mangled by a shell heredoc collapsing \\n. Seventh time. Use Write."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-incidents.py')
s = io.open(p, encoding='utf-8').read()

broken = 'def code_only(text):\n    text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.S)\n    return "\n".join(line for line in text.split("\n")\n                     if not line.lstrip().startswith("//"))\n'

fixed = (
    'def code_only(text):\n'
    '    text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.S)\n'
    '    kept = [line for line in text.splitlines() if not line.lstrip().startswith("//")]\n'
    '    return chr(10).join(kept)\n'
)

assert broken in s, 'broken block not found'
s = s.replace(broken, fixed, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('code_only repaired')

import ast
ast.parse(s)
print('proof-incidents.py parses clean')
