import io, json, re

P = 'Mod/Rimrooms - Async Industries/About/About.xml'
s = io.open(P, encoding='utf-8-sig').read()

# The description had grown to a single 6,724-character line: one sentence appended per
# checkpoint for twenty-odd checkpoints. That is unreadable in a browser and, far worse,
# unreadable in RimWorld's own mod description panel, which is where players actually meet it.
DESCRIPTION = u"""Development build 0.10.4-dev. Gameplay acceptance is pending; this is not a finished campaign release.

Rimrooms - Async Industries is a company-management campaign about an authorised research branch that investigates, contains and profits from unstable spaces beyond a gate.

--- THE GATE ---

A gate is an ordinary door you designate, not a custom machine. Core's own door and autodoor give you a one-cell gate; its ornate door gives you a two-cell one with no other mods at all. With Doors Expanded installed, its double and triple doors and its big blast door work too.

A wider gate is more machine: it draws more power while open and takes longer to bring up. It also decides what fits through. A one-cell opening passes people, dogs and working animals; two cells passes pack animals like muffalo and dromedaries; three or more passes anything at all.

Opening a connection is work, not a button. Your assigned operator brings the gate up at the console over time, and the console shows the progress while they do it. Walk away and it loses charge. A route your crew has run before comes up faster than one they have never taken.

Every gate keeps its own list of everywhere it has connected to. Rename them, pin the ones that matter, clear the rest. A gate you have designated is a blue door with a blue glow around it, so you can tell one from an ordinary door at a glance.

--- WHAT IS THROUGH IT ---

Each coordinate is a seeded, saved space you can return to. The shallow rooms are the yellow ones, sparse and wrong in the way you expect. Further in it stops pretending: rooms are furnished as laboratories, workshops, nurseries and dormitories, runs of rooms are furnished as one place rather than three, and corridors have benches in them because down there that is normal.

Go back to a space you have been to before and something is sometimes not where you left it. Nothing tells you. Not every time.

People are down there too - wanderers, the missing, the dead, survivors worth bringing home. Nothing starves or rots before you have found it; discovery starts their clock, not your exploring speed.

In the worst coordinates, what lives there stops holding its ground and follows your crew to the doorway. On an advanced gate it can step through behind them, and then it behaves like anything else that gets inside your base. Closing the connection before it arrives is what stops it.

--- THE COMPANY ---

Hire and pay staff, run procurement, keep a facility with the rooms a branch actually needs, take contracts and run company research.

Anything carried out of a coordinate is marked odd and never stacks with the ordinary kind, so a thousand odd cotton is a thing you went and fetched rather than a thing you grew. Buyers turn up wanting goods by origin and paying well over the ordinary rate. Company bonds hold value in denominations from ten up to a quadrillion, a beacon shows what you have, and a corporate trader opens its catalogue as you earn the right to see it.

Your colonists work across a gate the way they work anywhere: hauling, construction, bills, research, medical, cooking, cleaning, mining, hunting, farming, animals and the rest. Every kind of work in the game is either answered or deliberately left local for a stated reason.

--- REQUIREMENTS ---

Core only. Royalty, Ideology, Biotech, Anomaly and Odyssey are optional and used when present. No Harmony, no dependencies.

Original Backrooms menu backgrounds show the mod title and loaded version beside the native version information."""

new_description = DESCRIPTION.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
# The section rules read better as plain dashes than as escaped angle brackets.
new_description = new_description.replace('&lt;', '<').replace('&gt;', '>')

s, n = re.subn(r'<description>.*?</description>',
               '<description>' + new_description + '</description>', s, count=1, flags=re.S)
assert n == 1, 'description not replaced'

# A browser renders XML raw. A stylesheet instruction makes Edge present it as a page, and
# RimWorld's loader reads elements through DirectXmlLoader and ignores processing
# instructions entirely, so the mod still loads exactly as before.
if 'xml-stylesheet' not in s:
    s = s.replace('<?xml version="1.0" encoding="utf-8"?>',
                  '<?xml version="1.0" encoding="utf-8"?>\n'
                  '<?xml-stylesheet type="text/xsl" href="About.xsl"?>', 1)

io.open(P, 'w', encoding='utf-8-sig', newline='').write(s)
print('description restructured and stylesheet linked')

# Allowlist the stylesheet.
p = 'tools/package-files.json'
data = json.loads(io.open(p, encoding='utf-8-sig').read())
key = 'files' if 'files' in data else [k for k, v in data.items() if isinstance(v, list)][0]
if 'About/About.xsl' not in data[key]:
    data[key].append('About/About.xsl')
    data[key].sort()
    io.open(p, 'w', encoding='utf-8-sig', newline='').write(
        json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print('allowlist updated')
