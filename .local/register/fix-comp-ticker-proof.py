# -*- coding: utf-8 -*-
"""Two bugs in the proof I just wrote, both found by running it rather than by reading it.

1. **`Name="` matches inside `ParentName="`.** `<ThingDef ParentName="BuildingBase"
   Name="DoorBase" Abstract="True">` was indexed under `#BuildingBase`, so `#DoorBase` was never
   in the table and `Door`'s parent chain dead-ended — which made every per-def claim report
   *"not found in the installed game's data"* against correct data. The same shape as the
   `CompProperties_Glower` / `…GlowerUnused` prefix trap, in the proof written to catch a
   different one. `(?<![A-Za-z])Name="` requires the attribute to start where an attribute
   starts.

2. **`[^}]*?` cannot cross a method body that contains a `}`.** The claim checking that
   `CompTickInterval` calls `RefreshGateAppearance` failed against correct code because the body
   holds `{ return; }`. Matched on the method and a bounded window instead.

Both are the lesson of this whole checkpoint restated: **the proof must be run, not read.**
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-comp-tickers.py")

EDITS = [
    # 1. The attribute-name prefix trap, in both places it is read.
    ('            name = re.search(r\'Name="([^"]+)"\', attrs)',
     '            # `(?<![A-Za-z])` because `Name="` also matches inside `ParentName="`, which\n'
     '            # indexed `<ThingDef ParentName="BuildingBase" Name="DoorBase">` under\n'
     '            # `#BuildingBase` and dead-ended every door\'s parent chain.\n'
     '            name = re.search(r\'(?<![A-Za-z])Name="([^"]+)"\', attrs)'),

    ('            name = re.search(r\'Name="([^"]+)"\', attrs)\n'
     '            defname = re.search',
     '            name = re.search(r\'(?<![A-Za-z])Name="([^"]+)"\', attrs)\n'
     '            defname = re.search'),

    # 2. A window rather than a character class that cannot cross a brace.
    ('check("the appearance refresh runs on the interval tick a Normal ticker gets",\n'
     '      re.search(r"public override void CompTickInterval\\(int delta\\)[^}]*?"\n'
     '                r"RefreshGateAppearance\\(\\);", emergence, re.S) is not None,',
     '# A bounded window, not `[^}]*?`: the method body contains `{ return; }`, so a character\n'
     '# class excluding braces cannot reach the call and the claim failed against correct code.\n'
     '_interval = emergence.find("public override void CompTickInterval(int delta)")\n'
     'check("the appearance refresh runs on the interval tick a Normal ticker gets",\n'
     '      _interval >= 0\n'
     '      and "RefreshGateAppearance();" in emergence[_interval:_interval + 420],'),
]

text = io.open(PROOF, encoding="utf-8").read()

# Edit 1 is applied with replace_all semantics; edit 2 is the specific pair.
first_old, first_new = EDITS[0]
count = text.count(first_old)
if count < 1:
    print("ANCHOR PROBLEM: 0 of the Name= search")
    raise SystemExit(1)
text = text.replace(first_old, first_new, 1)

third_old, third_new = EDITS[2]
if text.count(third_old) != 1:
    print("ANCHOR PROBLEM: %d of the CompTickInterval claim" % text.count(third_old))
    raise SystemExit(1)
text = text.replace(third_old, third_new, 1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("proof fixed: attribute prefix trap and the brace-crossing window")
