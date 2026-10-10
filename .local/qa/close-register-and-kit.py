# -*- coding: utf-8 -*-
"""Close the field-kit row and the seven public-register rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Six masters never had a Def at all**", "x",
     " -- **FIVE OF THE SIX NOW HAVE ONE, AND THE SIXTH IS A DECISION RATHER THAN AN OMISSION, "
     "0.13.0-dev.** Owner's fork answer: *" + Q + "Build the three items, hold the Pursuer" + Q + "*. "
     "**Each of the three got a job nothing else does, using a standard Core mechanic and no new "
     "C# at all** -- the **field recorder** is a `CompFacility` linked to our own analysis bench "
     "(one per bench, within six cells, 12% off its work), the **survey tag** carries the marker "
     "component Core's glow pod carries and differs in the one way that matters underground (a "
     "glow pod is alive and dies on schedule; a tag does not), and the **sealed evidence case** is "
     "a `Building_Storage` whose fixed filter accepts recordings and books and nothing else, which "
     "is exactly what a designated shelf cannot promise. All three are 1x1 and minifiable, so a "
     "crew uninstalls one, carries it through a gate and sets it down. "
     "**AND THE SURVEY TAG EXPOSED THE THIRD DEF-NAME COUPLING OF THE DAY:** `RouteMarkers.OnMap` "
     "scanned `ThingsOfDef(" + Q + "GlowPod" + Q + ")`, so a tag carrying the marker component would "
     "have been designatable from its own button and then **missing from every route, ledger entry "
     "and distortion count**. It reads a short ours-first def list now, still indexed rather than "
     "walking every thing on the map, because it runs on a site tick. "
     "**The Quiet Pursuer stays held, by the owner's own choice**, and the reason is scope rather "
     "than permission: a creature of ours needs a race `ThingDef` with `lifeStages` and body "
     "graphics rather than a texture, and a malformed race on a 296-mod profile breaks other "
     "people's pawn rendering. `GATE_0_DECISIONS.md` #25 is restated: **the art ban lifted and the "
     "fairness rules did not** -- a sprite may never become how a player is warned."),

    ('**"a similar mod registry as the one we have but this one will be pubvlic facing with all '
     'new writes in it"**', "x",
     " -- **BUILT 0.13.0-dev.** `tools/build-public-register.py` generates `docs/wiki/mods-list.md` "
     "from the engineering register's **structured columns only**, and **not one sentence of its "
     "prose is carried across** -- *" + Q + "all new writes" + Q + "* is the whole instruction and it "
     "is load bearing, because *Planned Use*, *Integration Approach* and *Compatibility Watch* are "
     "written for whoever is about to build something. A player does not need our integration "
     "approach. **It is published**, so the reader-facing rules bind it: no text walls, the "
     "360-character ceiling and the banned vocabulary, and it reaches the site through the same "
     "renderer as the other thirteen pages. **`tools/check-public-register.py` is checker 32**, "
     "which exists because the generator is not a `check-*` and a battery that globs would never "
     "have run it -- the same gap `check-site-generated.py` was written to close."),

    ('**"mod interferances"**', "x",
     " -- **A COLUMN PER MOD, 0.13.0-dev.** *Watch for* is derived from how far each review "
     "actually got, so it can never claim more than was read: **settled** rows say no interference "
     "is expected, **provisional** rows say plainly that it has not been confirmed in a running "
     "game, and anything unread says so. **Six rows carry hand-written warnings instead**, in "
     "`tools/public-register-text.json` -- including Better Electronics, where the thing a player "
     "needs to know is that switching its breakdowns off does not stall a gate, because nothing in "
     "a gate's progress waits on an incident it can suppress."),

    ('**"what if\'s if not used"**', "x",
     " -- **THE COLUMN THE ENGINEERING REGISTER NEVER HAD, 0.13.0-dev.** Every row answers *what "
     "do I lose*, and the answer is almost always **nothing breaks**, because the fallback already "
     "exists in code for every bound provider -- this is simply the first place it is said in a "
     "player's language rather than in a disposition field. The rows that lose something concrete "
     "say what: without Doors Expanded a gate is still reachable up to three cells wide by binding "
     "a run of ordinary Core doors, and that is a sentence a player can act on."),

    ('**"uses in rimrooms"**', "x",
     " -- **ONE READABLE LINE PER MOD, 0.13.0-dev.** Composed from the register's **trace** column, "
     "which names the Rimrooms subsystem a row bears on -- and a player has never heard of a "
     "subsystem and has definitely seen a gate. So `RR-GATE` reads as *gates and their equipment*, "
     "`RR-EVD` as *evidence, journals and analysis*, `RR-COMPAT` as *nothing directly*. The trace "
     "column was the right source precisely because it already answers *what does this bear on* "
     "rather than *what is this mod about*."),

    ('**"required/recommended/(whatever else(s) is needed) as tags per mod in this recommended mod '
     'list for all mods"**', "x",
     " -- **THE OWNER'S OWN WORDS, WITH THE COLLISION SAID OUT LOUD, 0.13.0-dev.** The fork was put "
     "to the owner because a player-facing *Required* and the engineering `stance` column's "
     "*Required* are different claims -- `check-register-compliance.py` refuses the latter on any "
     "row while `About.xml` declares no dependencies. Owner's answer: *" + Q + "Your words, with the "
     "page saying nothing is required to run" + Q + "*. So the tags are **Required, Recommended, "
     "Optional, Visual only, Not needed**, and the page states before the table that **Required "
     "never means required to launch**. Derived rather than typed: visual-only and no-integration "
     "stances map straight across, and a **settled** row whose trace touches a load-bearing feature "
     "becomes Recommended. **83 Recommended, 192 Optional, 4 Visual only, 16 Not needed** -- and "
     "the only thing tagged Required is the game."),

    ('**"for all mods"**', "x",
     " -- **ALL OF THEM, AND THE COUNT RECONCILES EXACTLY, 0.13.0-dev.** The owner's "
     "*" + Q + "i cuttenlty have 296 (6DLCs, Rimbridge , Rimrooms(locally))" + Q + "* resolves "
     "cleanly: the engineering register holds **295 rows -- 294 profile entries plus one for Core** "
     "-- and the six `Data/` folders sit inside the 294 as rows 4 to 9. So **294 + Rimbridge + "
     "Rimrooms = 296**, and the two the engineering register never had are declared in the "
     "overrides file. The page reads **296 mods**, with the base game listed for context and "
     "**stated not to be counted in that number**, because a count that silently includes the game "
     "is the kind of quiet difference this project keeps finding."),

    ('**"and anything else relevant of note"**', "x",
     " -- **HELD OPEN BY CONSTRUCTION AND ANSWERED STRUCTURALLY, 0.13.0-dev.** Like the unnerving "
     "register's *" + Q + "all things" + Q + "*, this cannot be closed by listing. What it gets "
     "instead is **a place to put anything**: `tools/public-register-text.json` overrides any cell "
     "on any row by hand, and the generator prefers a hand-written line over its own every time, so "
     "a fact nobody anticipated needs no code change to publish. **Six rows are hand-written "
     "already.** The generator also **refuses to finish** if any row carries a tag outside the "
     "vocabulary or leaves a cell empty, so *" + Q + "for all mods" + Q + "* cannot quietly become "
     "*for most mods*."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, marker, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if (l.lstrip().startswith("- [ ] ") or l.lstrip().startswith("- [~] ")) and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:60], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        body = raw.lstrip()[6:].rstrip()
        lines[hits[0]] = "%s- [%s] %s%s" % (lead, marker, body, evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
