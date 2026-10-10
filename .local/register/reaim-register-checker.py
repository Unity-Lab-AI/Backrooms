# -*- coding: utf-8 -*-
"""Re-aim `check-register-compliance.py`'s dependency rule. The premise it encoded is overruled.

Owner direction, 2026-10-01, verbatim: *"see thats WRONG the mod DOES HAVE HARD DEPENDANCIES SO
GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*, and when
asked which: *"there are alot more depeandacies than just the DLC we have alkinds of mods in the
274 mod list WE ARE USING ALL OF THEM!!!!"*.

The checker refused the new About.xml with *"The package must load and run against Core alone."*
**The checker was not defective; its premise was.** That rule was a true reading of the register's
guidance in September and the owner has now overruled it -- and the register is **guidance, not
law** by the owner's own standing correction, so a register-derived rule is exactly the kind that
an owner decision supersedes.

## A prohibition becomes an assertion

Deleting the rule would leave the strongest surface in the package unchecked. Replacing it with
*"the dependencies you declare must be ones a mod manager can act on"* is the version that can
still catch a real defect:

  * our own packageId is never a dependency of itself,
  * Core is never declared as one -- it is always present and belongs in `loadAfter`,
  * every dependency carries a `displayName`, because a manager shows that to the player,
  * every non-expansion dependency carries a URL, or the player is told to find it themselves,
  * **every dependency also appears in `loadAfter`** -- this is the one that matters. A
    requirement without an ordering constraint is how this package sat at **position 197 of
    296** with 99 mods loading after it,
  * no packageId is declared twice.

The `PatchOperationFindMod` rule below it is **untouched and now more load-bearing, not less**:
the owner's answer to how the code should treat required content was *keep the graceful guards
anyway*, so a patch that is optional by construction is exactly right.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-register-compliance.py")

OLD_DOC = u"""  * **No hard dependency on any mod.** `About.xml` must declare no `modDependencies`. The package
    has to load and run against Core alone. This is the one that matters most, because it is the
    difference between "works with the 294" and "requires some of them".
"""

NEW_DOC = u"""  * **Every declared dependency is one a mod manager can act on.** This rule previously read
    *"About.xml must declare no modDependencies; the package has to load and run against Core
    alone"*. **The owner overruled that on 2026-10-01:** *"the mod DOES HAVE HARD DEPENDANCIES SO
    GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*, and
    *"WE ARE USING ALL OF THEM"*. The old rule was a fair reading of the register's guidance, and
    the register is **guidance, not law** by the owner's own standing correction, so an owner
    decision supersedes it. What is checked now is that each declaration is usable: a
    `displayName` because a manager shows it, a URL on anything that is not an expansion, and
    **a matching `loadAfter` entry** -- a requirement without an ordering constraint is how this
    package came to sit at position 197 of 296 with 99 mods loading after it.
"""

OLD_CHECK = u'''    declared = re.findall(r"<modDependencies>(.*?)</modDependencies>", text, re.S)
    entries = []
    for block in declared:
        entries += re.findall(r"<packageId>([^<]+)</packageId>", block)
    if entries:
        fail("About.xml declares hard mod dependencies: %s. The package must load and run "
             "against Core alone." % ", ".join(entries))
    else:
        notes.append("no hard mod dependencies declared")

    after = re.findall(r"<loadAfter>(.*?)</loadAfter>", text, re.S)
    load_after = []
    for block in after:
        load_after += [v.strip() for v in re.findall(r"<li>([^<]+)</li>", block)]
    unexpected = [v for v in load_after if v.lower() != "ludeon.rimworld"]
    if unexpected:
        notes.append("loadAfter names beyond Core: %s (ordering only, not a dependency)"
                     % ", ".join(unexpected))
    else:
        notes.append("loadAfter names Core only")
'''

NEW_CHECK = u'''    declared_blocks = re.findall(r"<modDependencies>(.*?)</modDependencies>", text, re.S)
    rows = []
    for block in declared_blocks:
        rows += re.findall(r"<li>(.*?)</li>", block, re.S)

    after = re.findall(r"<loadAfter>(.*?)</loadAfter>", text, re.S)
    load_after = []
    for block in after:
        load_after += [v.strip() for v in re.findall(r"<li>([^<]+)</li>", block)]
    load_after_keys = set(v.lower() for v in load_after)

    own = re.search(r"<packageId>([^<]+)</packageId>", text)
    own_key = own.group(1).strip().lower() if own else None

    entries = []
    for row in rows:
        package = re.search(r"<packageId>([^<]+)</packageId>", row)
        if package is None:
            fail("a modDependencies entry declares no packageId")
            continue
        key = package.group(1).strip()
        entries.append({
            "id": key,
            "key": key.lower(),
            "display": (re.search(r"<displayName>([^<]+)</displayName>", row) or [None])
                       and re.search(r"<displayName>([^<]+)</displayName>", row),
            "url": re.search(r"<(?:steamWorkshopUrl|downloadUrl)>([^<]+)</", row),
        })

    if not entries:
        # Still legal, and worth a note rather than a pass in silence: a package that declares
        # nothing is one a manager cannot sort or warn about.
        notes.append("no hard mod dependencies declared")
    else:
        seen = {}
        for entry in entries:
            seen[entry["key"]] = seen.get(entry["key"], 0) + 1
        duplicates = sorted(k for k, n in seen.items() if n > 1)
        if duplicates:
            fail("About.xml declares the same dependency twice: %s" % ", ".join(duplicates))

        if own_key and own_key in seen:
            fail("About.xml declares itself as its own dependency (%s)" % own_key)

        if "ludeon.rimworld" in seen:
            fail("Core is declared as a mod dependency. Core is always present; it belongs in "
                 "loadAfter, not in modDependencies")

        nameless = [e["id"] for e in entries if e["display"] is None]
        if nameless:
            fail("%d dependency row(s) carry no displayName, which is the text a mod manager "
                 "shows the player: %s" % (len(nameless), ", ".join(sorted(nameless)[:8])))

        # An expansion needs no URL: a player who lacks one cannot be sent to a Workshop page
        # for it. Everything else must be findable.
        unreachable = [e["id"] for e in entries
                       if e["url"] is None and not e["key"].startswith("ludeon.rimworld")]
        if unreachable:
            fail("%d dependency row(s) give the player no way to obtain the mod: %s"
                 % (len(unreachable), ", ".join(sorted(unreachable)[:8])))

        unordered = [e["id"] for e in entries if e["key"] not in load_after_keys]
        if unordered:
            fail("%d dependency row(s) are required but never ordered -- no loadAfter entry, so "
                 "this package may load before a mod it depends on: %s"
                 % (len(unordered), ", ".join(sorted(unordered)[:8])))

        if not any(f for f in [None] if False) and not unordered and not unreachable \\
                and not nameless and not duplicates:
            expansions = [e for e in entries if e["key"].startswith("ludeon.rimworld")]
            notes.append("%d hard dependencies declared (%d expansions, %d mods); every one "
                         "carries a displayName, a way to obtain it, and a matching loadAfter"
                         % (len(entries), len(expansions), len(entries) - len(expansions)))

    if "ludeon.rimworld" not in load_after_keys:
        fail("loadAfter does not name Core. Every package loads after Core and saying so is how "
             "a sorting manager knows where the floor is")
    else:
        notes.append("loadAfter names Core plus %d other entries" % (len(load_after) - 1))
'''

text = io.open(CHECKER, encoding="utf-8").read()
problems = []
if text.count(OLD_DOC) != 1:
    problems.append("doc anchor %d" % text.count(OLD_DOC))
if text.count(OLD_CHECK) != 1:
    problems.append("check anchor %d" % text.count(OLD_CHECK))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM %s" % problem)
    raise SystemExit(1)

text = text.replace(OLD_DOC, NEW_DOC, 1)
text = text.replace(OLD_CHECK, NEW_CHECK, 1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text)

after_text = io.open(CHECKER, encoding="utf-8").read()
if u"The package must load and run against Core alone." in after_text:
    print("THE OVERRULED RULE IS STILL ENFORCED")
    raise SystemExit(1)
print("checker re-aimed: a prohibition became an assertion about usable declarations")
