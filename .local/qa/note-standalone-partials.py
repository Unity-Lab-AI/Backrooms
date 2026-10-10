# -*- coding: utf-8 -*-
"""Two rows stay open and now say which half of them shipped.

`.claude/CONSTRAINTS.md`: *"A ROW WHOSE OWN EVIDENCE SAYS *PARTLY* MUST NOT BE
ARCHIVED."* These two are the reason that rule exists -- both are about the
stand-alone direction, both got materially closer this batch, and neither is
done. Written before the archiver runs, so the queue states it rather than a
reader inferring it from the rows that left.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

NOTES = [
 ('- [ ] **"im reiterating the fact that we need to fix the depancy list so that its accurate to what is required and we hope to have the mod as a complete stand alone"**',
  'PARTLY CLOSED 0.12.86-dev, and the two clauses of this reiteration land differently. '
  '*"fix the depancy list so that its accurate to what is required"* **is done**: the 293 hard '
  '`modDependencies` are gone and `loadAfter` carries the 294-row profile, which is accurate — '
  'the assembly references `Assembly-CSharp` and three UnityEngine modules and nothing else. '
  '*"we hope to have the mod as a complete stand alone"* **is not**, and removing a declaration '
  'does not make absence safe; it only stops advertising. The row below names what is left and '
  'this one stays open until it closes.'),

 ('- [ ] **"rework mod to not need any depeancie mods"** — **the guarantee half, and THIS is the *"major major work"* the owner means.**',
  'STILL OPEN, and the declaration half landing at 0.12.86-dev **does not touch it.** What has to '
  'be proved row by row is unchanged: every by-name `GetNamedSilentFail` degrades rather than '
  'returning null into a dereference; both `Patches/` operations stay guarded by '
  '`PatchOperationFindMod` / `PatchOperationConditional` so an absent target applies nothing '
  '(invariant 42); and no Def, scenario grant, recipe, archetype slot or keyed string silently '
  'assumes a DLC or profile def exists. **`ARCHITECTURE.md` now says so in the same sentence as '
  'the change** — the DLC line reads *"that is still not a claim that absence is '
  'supported"* — so the document no longer implies this row is covered by the deletion.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0

for anchor, note in NOTES:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:92]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    if "PARTLY CLOSED 0.12.86" in text[at:line_end] or "declaration half landing at 0.12.86" \
            in text[at:line_end]:
        print("already noted: %s" % anchor[:60])
        continue
    text = text[:line_end] + " — **" + note + "**" + text[line_end:]
    print("noted: %s" % anchor[:68])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("wrote %s" % TODO)
