# -*- coding: utf-8 -*-
"""The claim asserted the exact line that made the door invisible.

`proof-gate-links.py` required:

    "if (live) { colorable.SetColor(LiveGlowColor.ToColor); }"

and that call is **the defect the owner reported as a missing door**. `ColorInt.ToColor` divides
alpha by 255 too, so the glow constant's `a: 0` became a fully transparent tint and
`Thing.DrawColor` painted the door at zero opacity.

**This is the second time a proof has held a bug in place by naming it**, after
`proof-gate-links.py` required `Class="CompProperties_Colorable"` at the seventh launch. Same
file, same shape: **asserting an exact line proves we wrote that line, and says nothing about
whether the line is right.**

So the claim now asserts the PROPERTY rather than the line: the tint must be opaque, and must not
be derived from the glow constant. A glow colour and a draw colour are different kinds of colour,
and the proof now knows that.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

OLD = u'''      and "LiveGlowColor" in gatecomp and "LiveGlowRadius" in gatecomp
      and "if (live) { colorable.SetColor(LiveGlowColor.ToColor); }" in gatecomp,'''

NEW = u'''      and "LiveGlowColor" in gatecomp and "LiveGlowRadius" in gatecomp
      # **THE TINT MUST BE OPAQUE, AND IT MUST NOT COME FROM THE GLOW CONSTANT.** This claim used
      # to require `SetColor(LiveGlowColor.ToColor)` -- which is the line that made the door
      # invisible, because `ColorInt.ToColor` divides alpha by 255 and the glow constant is
      # `a: 0`. The second time this file has held a bug in place by naming it exactly. Assert
      # the property, not the line.
      and "if (live) { colorable.SetColor(LiveTintColor); }" in gatecomp
      and "LiveGlowColor.ToColor" not in gatecomp
      and "220f / 255f, 1f)" in gatecomp,'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the tint claim requires opacity, not a particular line")
