# -*- coding: utf-8 -*-
"""The door was invisible, not destroyed -- alpha zero -- and the dial failed without saying why.

Owner, verbatim: *"okay , i see the blue glow, i do not see the door, i do not see the portal fx
from stargate, i do see the backrooms map option at the top where pawns appear when they travel
there, clicking on where the door and portal should be only gives \\"go here\\" option ... walking a
pawn to the empty spot in the wall where the door used to be"*.

READ FROM THE PAUSED GAME, NOT GUESSED. Cell (160,161) holds a `Door`, `RimWorld.Building_Door`,
Steel, **160 hit points, fully intact.** Its gizmos include *"Stop being a way home"*, *"Send
somebody through"* and **"Load"** -- so the designation is live, the route is live, and our
`CompTransporter` attached. **The door was never destroyed. It was drawn invisible.**

DEFECT ONE, AND IT IS ONE NUMBER.

    private static readonly ColorInt LiveGlowColor = new ColorInt(70, 130, 220, 0);
    ...
    glower.GlowColor = LiveGlowColor;                  // correct
    colorable.SetColor(LiveGlowColor.ToColor);         // ALPHA ZERO

`ColorInt.ToColor` divides every channel by 255, **including alpha**, so `a: 0` becomes a fully
transparent `Color`. `Thing.DrawColor` returns whatever `CompColorable` holds, so the door was
painted with zero opacity and vanished while its glower kept lighting the room -- which is exactly
the pair of symptoms reported.

**A glow colour and a draw colour are not the same kind of colour.** Alpha zero is the convention
for a `ColorInt` glow -- their own stargate def uses `(115,171,224,0)` -- and it is meaningless
for a thing's tint. They are two constants now, and the tint is opaque.

DEFECT TWO, AND IT IS MINE FOR BEING TIDY. Every refusal in the dialling path returns quietly:
`Available` false, no component, no `openMethod`, hibernating, already open, receiving. That is
right for a colony that does not have the Stargate mod -- and **useless the moment something does
not work**, which is now. The log says nothing because I wrote it to say nothing.

So a natural gate that cannot dial now **says which guard stopped it, once per gate**, at
`Log.Message` rather than as an error: it is information, not a fault. One line, the first time,
and never again for that door -- the rule this project already follows for anything that could
repeat on a tick.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
COMP = os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs")

comp = io.open(COMP, encoding="utf-8").read()

EDITS = [
    # ------------------------------------------------------------------ 1. the invisible door
    (u'''        /// <summary>The blue the owner asked for, and the reach of its light.</summary>
        private static readonly ColorInt LiveGlowColor = new ColorInt(70, 130, 220, 0);''',
     u'''        /// <summary>
        /// The blue the owner asked for, as a **glow** colour.
        ///
        /// Alpha zero is the convention for a `ColorInt` handed to `CompGlower` -- their own
        /// stargate def uses `(115,171,224,0)` -- because a glower reads the channels and not the
        /// opacity.
        /// </summary>
        private static readonly ColorInt LiveGlowColor = new ColorInt(70, 130, 220, 0);

        /// <summary>
        /// The same blue as a **tint**, and it has to be opaque.
        ///
        /// **This is the defect the owner reported as a missing door.** `ColorInt.ToColor`
        /// divides every channel by 255 including alpha, so reusing the glow constant here
        /// painted the door with zero opacity: `Thing.DrawColor` returns what `CompColorable`
        /// holds, so the door was drawn fully transparent while its glower kept lighting the
        /// room. It was never destroyed -- the paused game showed it intact with 160 hit points.
        ///
        /// **A glow colour and a draw colour are not the same kind of colour**, and sharing one
        /// constant between them is what hid that.
        /// </summary>
        private static readonly Color LiveTintColor = new Color(70f / 255f, 130f / 255f,
            220f / 255f, 1f);'''),

    (u"                if (live) { colorable.SetColor(LiveGlowColor.ToColor); }",
     u"                if (live) { colorable.SetColor(LiveTintColor); }"),

    # --------------------------------------------------------- 2. the dial stops being silent
    (u'''            // Dialled only from this side, and only when nothing is already open. Their gate is
            // one-way by design, so dialling a receiving end would fight their own rule rather
            // than use it.
            if (StargateBridge.IsOpen(near) || StargateBridge.IsReceiving(near)) { return; }
            if (StargateBridge.IsHibernating(near)) { return; }
            StargateBridge.Dial(near, far.Map, 0);''',
     u'''            // Dialled only from this side, and only when nothing is already open. Their gate is
            // one-way by design, so dialling a receiving end would fight their own rule rather
            // than use it.
            if (StargateBridge.IsOpen(near)) { return; }
            if (StargateBridge.IsReceiving(near)) { ReportGateState("it is the receiving end"); return; }
            if (StargateBridge.IsHibernating(near))
            { ReportGateState("their mod has it hibernating, which means another stargate is on this map"); return; }
            if (StargateBridge.On(near) == null)
            { ReportGateState("their component did not attach to this door"); return; }
            if (!StargateBridge.Dial(near, far.Map, 0))
            { ReportGateState("the dial was refused"); }'''),

    # The reporter, placed beside the method that uses it.
    (u"        /// <summary>The door at the other end of this route, as a thing that can carry comps.</summary>",
     u'''        /// <summary>Whether this gate has already explained itself once.</summary>
        private bool reportedGateState;

        /// <summary>
        /// Say, once, why a live natural gate is not showing a wormhole.
        ///
        /// **Every refusal in this path used to be silent**, which is correct for a colony
        /// without the Stargate mod and useless the moment something does not work. The owner's
        /// report -- *"i do not see the portal fx from stargate"* -- came with a log containing
        /// nothing at all, because this code was written to say nothing at all.
        ///
        /// `Log.Message`, not `Log.Error`: a gate that cannot dial is information, not a fault.
        /// Once per door, because this runs on a tick.
        /// </summary>
        private void ReportGateState(string reason)
        {
            if (reportedGateState) { return; }
            reportedGateState = true;
            Log.Message("[Rimrooms][Stargate] " + parent.LabelShortCap + " at "
                        + parent.Position + " is a live gate but is not showing a wormhole: "
                        + reason + ".");
        }

        /// <summary>The door at the other end of this route, as a thing that can carry comps.</summary>'''),
]

problems = []
for old, _ in EDITS:
    if comp.count(old) != 1:
        problems.append("%d of %r" % (comp.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    comp = comp.replace(old, new, 1)
io.open(COMP, "w", encoding="utf-8", newline="").write(comp)
print("door tint is opaque; the dial names the guard that stopped it")
