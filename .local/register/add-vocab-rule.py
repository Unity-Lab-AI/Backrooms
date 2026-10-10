import io

p = 'tools/check-info-cards.py'
s = io.open(p, encoding='utf-8').read()

block = '''

# --------------------------------------------------------------------------- #
# The vocabulary a player reads
# --------------------------------------------------------------------------- #
#
# Owner direction, 2026-09-29, verbatim: *"ive used alot of differnt terms for the gates..
# from portals, gates, doors , the machine, the gizmo, ect ect we need a unified name
# throught the entire mode in all the equipment information and cards of things items
# resources and buildings and all things that our mod touches"*.
#
# Answered at the fork as three words for three genuinely different things, because one word
# for all of them would have cost the game the ability to say which part failed:
#
#     GATE        the machine in your wall. Always a designated door.
#     CONNECTION  the live link a gate holds open to one coordinate.
#     THRESHOLD   the doorway you arrive at on the far side.
#
# "the gate is fine, the connection dropped" says something true and could not be said at
# all while both were called a portal.
#
# Key NAMES are deliberately not checked. A player never reads `RR_Portals_Heading`, and
# renaming keys is churn with real DefInjected risk for no reader benefit. Only what is
# displayed is held to the vocabulary.
BANNED_TERMS = {
    "portal": "the machine is a 'gate'; the link it holds open is a 'connection'",
    "machine gate": "the machine gate def was retired in 0.9.0-dev; it is a 'gate'",
    "doorway": "a plain door is a 'door'; the far-side arrival point is a 'threshold'",
    "gizmo": "'gizmo' is RimWorld's word for a button, never a name for our gate",
}
BANNED_PATTERNS = [
    (term, re.compile(r"\\b" + term.replace(" ", r"\\s+") + r"s?\\b", re.I))
    for term in BANNED_TERMS
]
'''

anchor = '\n\ndef our_def_type(kind):'
assert anchor in s
s = s.replace(anchor, block + anchor, 1)

# Collect displayed text and check it.
helper = '''

def displayed_text():
    """Every string a player can actually read: keyed values, and def labels and descriptions."""
    found = []
    pattern = os.path.join(MOD, "*", "Languages", "**", "*.xml")
    for path in glob.glob(pattern, recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter():
            if node.text and node.tag != "LanguageData":
                found.append((os.path.relpath(path, REPO).replace(os.sep, "/"), node.tag, node.text))
    for path in glob.glob(os.path.join(MOD, "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter():
            if node.tag in ("label", "description", "jobString", "reportString",
                            "verb", "gerund", "summary") and node.text:
                found.append((os.path.relpath(path, REPO).replace(os.sep, "/"), node.tag, node.text))
    return found


def check_vocabulary(problems):
    for path, tag, text in displayed_text():
        flat = " ".join(text.split())
        for term, pattern in BANNED_PATTERNS:
            match = pattern.search(flat)
            if not match:
                continue
            problems.append("%s <%s> says %r -- %s: %r"
                            % (path, tag, match.group(0), BANNED_TERMS[term], flat[:70]))
'''

anchor2 = '\n\ndef main():'
assert anchor2 in s
s = s.replace(anchor2, helper + anchor2, 1)

old = '''    print("info-cards")
    print("  defs declared        : %d" % len(defs))'''
new = '''    check_vocabulary(problems)

    print("info-cards")
    print("  defs declared        : %d" % len(defs))'''
assert old in s
s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('vocabulary rule added to check-info-cards.py')
