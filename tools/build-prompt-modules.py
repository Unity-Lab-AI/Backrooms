"""Build the autopilot's per-situation prompt modules from the owner's rules.

Owner, 2026-10-13: "can we have differnt plc wearning and information load differnt system prompts like meta prompts
as needed so its not eating a massive file and forgettting 90^ of it while doing the wrong choice?"

docs/playbook.rules.json holds every owner play order, one row each (topic, owner_words, rule). This sorts them into
the ladder's rung families and writes .local/autopilot/modules/<family>.md -- short, one line per rule -- so a turn
only carries the rules for the situation the top rung is in. Re-run after the rules change:

    python tools/build-prompt-modules.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "docs", "playbook.rules.json")
OUT = os.path.join(ROOT, ".local", "autopilot", "modules")
MAX_LINES = 45

# family -> words that put a rule in it (topic + rule text, lower case). A rule can land in several families.
FAMILIES = {
    "setup": ("start", "priorit", "work tab", "schedule", "explore", "unforbid", "assign", "first", "day one", "scenario",
              "crash", "camp", "shelter", "stockpile", "shelf", "bed"),
    "survival": ("food", "meal", "cook", "hunt", "berr", "starv", "stove", "freezer", "cooler", "rot", "roof", "medic",
                 "heal", "tend", "doctor", "temperature", "heat", "cold", "fire", "sick", "butcher", "harvest"),
    "combat": ("raid", "draft", "embrasure", "enemy", "hostile", "fight", "ranged", "melee", "kite", "capture", "prisoner",
               "arm", "rifle", "sidearm", "retreat", "turret", "killbox"),
    "base-and-fortress": ("wall", "door", "hall", "corridor", "room", "base", "architect", "tower", "firebreak", "lane",
                          "lamp", "light", "vent", "mountain", "build"),
    "economy": ("trade", "sell", "silver", "vault", "production", "bill", "crop", "field", "cotton", "smokeleaf", "hops",
                "beer", "drug", "guest", "hospitality", "caravan", "stock"),
    "research": ("research", "electric", "power", "generator", "conduit", "microelectronic", "bench", "fabricat"),
    "growth": ("recruit", "joiner", "hire", "employee", "colonist", "family", "child", "marry", "moral guide", "leader"),
    "space": ("ship", "launch", "reactor", "cryptosleep", "orbit", "space"),
    "backrooms": ("gate", "backroom", "portal", "expedition", "level", "branch", "company"),
    "animals": ("animal", "pen", "tame", "mount", "milk", "fence"),
}
# rung families that share a module
ALIAS = {"start": "setup", "configuration": "setup", "war": "combat", "endgame": "space", "royalty": "growth",
         "ideology-biotech-anomaly": "growth", "meta": "setup"}


def main():
    rules = json.load(open(RULES, encoding="utf-8"))
    by = {f: [] for f in FAMILIES}
    for r in rules:
        text = ((r.get("topic") or "") + " " + (r.get("rule") or "")).lower()
        words = r.get("owner_words") or []
        quote = (words[0] if words else "").strip()
        rule = re.sub(r"owner,? ?\d{4}-\d\d-\d\d[^:]*:?", "", r.get("rule") or "")
        rule = re.sub(r"(\s*[/;:]\s*){2,}", " ", rule)
        rule = re.sub(r"^[\s/;:\-]+|\(\s*\)", "", re.sub(r"\s+", " ", rule)).strip()
        line = "- " + rule
        if quote and quote.lower()[:40] not in line.lower():
            line += '  (owner: "' + quote[:140] + '")'
        for fam, keys in FAMILIES.items():
            if any(re.search("(?<![a-z])" + re.escape(k), text) for k in keys):
                by[fam].append(line)
    os.makedirs(OUT, exist_ok=True)
    for fam, lines in by.items():
        lines = list(dict.fromkeys(lines))[:MAX_LINES]
        body = ("SITUATION RULES -- %s (the owner's own orders for this kind of moment; the live rung says what to do"
                " now, these say how):\n" % fam.upper()) + "\n".join(lines) + "\n"
        with open(os.path.join(OUT, fam + ".md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        print("%-18s %3d rules" % (fam, len(lines)))
    with open(os.path.join(OUT, "aliases.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(ALIAS, f, indent=1)


if __name__ == "__main__":
    main()
