# -*- coding: utf-8 -*-
"""Teach check-package-integrity.py to verify a patch on an abstract inheritance parent.

Until now the checker only understood `defName="X"` in an xpath, so **any** patch targeting an
abstract parent by its `Name` attribute was "selecting no named def" and therefore refused. That
did not check the technique, it ruled it out -- and patching an abstract parent is the only way to
reach a property of every building in the game at once, including buildings belonging to mods this
project has never seen.

The verification is real rather than a waiver: an abstract name is indexed only when the def
actually declares `Abstract="True"`, so a patch aimed at a parent that does not exist still fails.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'tools', 'check-package-integrity.py')

s = io.open(PATH, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:80]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:80]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ 1. index abstract parents
sub('''def index_game_defs():
    """defName -> True for every def the installed game ships, Core and DLC alike."""
    names = {}
    if not os.path.isdir(GAME_DATA):
        return None
    pattern = os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml")
    for path in glob.glob(pattern, recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter("defName"):
            if node.text:
                names[node.text.strip()] = True
    return names''',
'''def index_game_defs():
    """Every def name the installed game ships, Core and DLC alike.

    Two kinds of name, because patches legitimately target both:

      * `defName` -- a concrete def.
      * the `Name` attribute of an **abstract** def, which is an inheritance parent rather than a
        def the game instantiates. Patching one is the only way to reach a property of every
        building in the game at once, including buildings belonging to mods this project has never
        seen. Until 0.12.27-dev this indexer knew nothing about them, so **every patch on an
        abstract parent was unverifiable and therefore refused** -- which ruled the technique out
        rather than checking it.

    An abstract name is indexed only when the def really declares itself abstract. A `Name` on a
    concrete def is an alias, and matching one would prove nothing about what a patch reaches.
    """
    names = {}
    if not os.path.isdir(GAME_DATA):
        return None
    pattern = os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml")
    for path in glob.glob(pattern, recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter("defName"):
            if node.text:
                names[node.text.strip()] = True
        for node in root.iter():
            name = node.get("Name")
            if name and (node.get("Abstract") or "").strip().lower() == "true":
                names[name.strip()] = True
    return names''')

# ------------------------------------------------------------------ 2. recognise the target form
old_pattern = 'XPATH_DEFNAME = re.compile(r"defName\\s*=\\s*[\\"\']([^\\"\']+)[\\"\']")'
new_pattern = (old_pattern + '\n'
               '# An abstract inheritance parent, addressed by its Name attribute. Verified against\n'
               '# the game\'s own abstract defs, so a patch on a parent that does not exist still fails.\n'
               'XPATH_ABSTRACT = re.compile(r"@Name\\s*=\\s*[\\"\']([^\\"\']+)[\\"\']")')
sub(old_pattern, new_pattern)

sub('            targets = XPATH_DEFNAME.findall(xpath)',
    '            targets = XPATH_DEFNAME.findall(xpath) + XPATH_ABSTRACT.findall(xpath)')

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('integrity checker: abstract inheritance parents are now indexed and verifiable')
