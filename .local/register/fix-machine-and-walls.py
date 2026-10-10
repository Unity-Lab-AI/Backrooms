import io, glob, os, re

M = 'Mod/Rimrooms - Async Industries/1.6/'

# --- the last "the machine" leaks ------------------------------------------
LEAKS = [
    ('Languages/English/Keyed/RR_Scenario.xml',
     'Finish the machine, assign a capable operator',
     'Finish the gate, assign a capable operator'),
    ('Languages/English/Keyed/RR_StartupSetup.xml',
     'complete the machine, and prepare a real return route',
     'complete the gate, and prepare a real return route'),
    ('Defs/RimroomsProjectDefs/RR_CompanyProjects.xml',
     "with the machine's timing records",
     "with the gate's timing records"),
]
for path, old, new in LEAKS:
    full = M + path
    s = io.open(full, encoding='utf-8-sig').read()
    assert old in s, path + ' :: ' + old[:40]
    s = s.replace(old, new, 1)
    io.open(full, 'w', encoding='utf-8-sig', newline='').write(s)
    print('vocabulary fixed in ' + os.path.basename(path))


# --- the worst walls, broken into paragraphs -------------------------------
# RimWorld renders newlines in these, so a wall is a choice rather than a limitation.
WALLS = {
 'Defs/ScenarioDefs/RR_Scenarios.xml': [(
   'Lead an authorized research branch of Async Industries. Customize your starting people and supplies with native setup or optional Prepare Carefully, then review company roles and capabilities. Five colonists are the default; the company review supports 1 to 20 selected people without replacing them. A fixed small facility, unfinished machine, first survey and $50 million allocation await at your chosen surface tile. Supplies arrive physically with your people and remain editable separately from the fixed structures. This start uses a compact 60 by 60 headquarters; temperate conditions are recommended. Extra staff need additional beds and supplies. Small teams may need to hire before a full expedition.',
   'Lead an authorised research branch of Async Industries.\n\n'
   'A small facility, an unfinished gate, a first survey and a $50 million allocation wait for you at the surface tile you choose. The headquarters is a fixed 60 by 60 layout, and temperate conditions are recommended.\n\n'
   'Five colonists by default. The company review supports one to twenty selected people without replacing them, so customise your staff and supplies with native setup or Prepare Carefully as you prefer.\n\n'
   'Supplies arrive physically with your people and stay editable separately from the fixed structures. Extra staff need extra beds and food, and a small team may need to hire before it can field a full expedition.')],

 'Languages/English/Keyed/RR_Scenario.xml': [(
   'Finish the gate, assign a capable operator, calibrate it, and prepare the return route before dispatching a crew.',
   'Finish the gate, assign a capable operator, calibrate it, and prepare the return route before dispatching a crew.')],
}
for path, pairs in WALLS.items():
    full = M + path
    s = io.open(full, encoding='utf-8-sig').read()
    for old, new in pairs:
        if old == new:
            continue
        assert old in s, path + ' :: ' + old[:50]
        s = s.replace(old, new, 1)
    io.open(full, 'w', encoding='utf-8-sig', newline='').write(s)
    print('reflowed ' + os.path.basename(path))


# --- a rule so a wall cannot come back -------------------------------------
p = 'tools/check-info-cards.py'
s = io.open(p, encoding='utf-8').read()

s = s.replace(
"""BANNED_TERMS = {
    "portal": "the machine is a 'gate'; the link it holds open is a 'connection'",""",
"""BANNED_TERMS = {
    "the machine": "the gate is a 'gate'; 'machining table' is Core content and stays",
    "portal": "the machine is a 'gate'; the link it holds open is a 'connection'",""", 1)

wall_rule = '''

# --------------------------------------------------------------------------- #
# Walls of text
# --------------------------------------------------------------------------- #
#
# Owner direction, 2026-09-29, verbatim: *"its a massive text wall needs style formating and
# beautiful layout"*, about an About.xml description that had reached a single unbroken line
# of 6,724 characters -- one sentence appended per checkpoint for twenty-odd checkpoints.
#
# RimWorld renders newlines in a description, a letter and a scenario summary, so a wall is
# a choice rather than a limitation. Past this length without a single paragraph break, it
# is a choice nobody made deliberately.
WALL_CHARS = 420
WALL_EXEMPT_TAGS = ("jobString", "reportString", "verb", "gerund", "label")


def check_walls(problems):
    for path, tag, text in displayed_text():
        if tag in WALL_EXEMPT_TAGS:
            continue
        flat = " ".join(text.split())
        if len(flat) <= WALL_CHARS:
            continue
        if "\\n" in text or "\\\\n" in text:
            continue
        problems.append("%s <%s> is %d characters with no paragraph break -- a player meets "
                        "this as a wall (%r)" % (path, tag, len(flat), flat[:60]))
'''

anchor = '\n\ndef main():'
assert anchor in s
s = s.replace(anchor, wall_rule + anchor, 1)

old = '    check_vocabulary(problems)\n'
new = '    check_vocabulary(problems)\n    check_walls(problems)\n'
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('vocabulary widened and a wall rule added')
