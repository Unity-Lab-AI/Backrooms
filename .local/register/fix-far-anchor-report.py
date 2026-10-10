# -*- coding: utf-8 -*-
"""The likeliest reason the wormhole never opened is the one guard that still says nothing.

Everything else about the gate is confirmed healthy in the owner's paused game:

    cell (160,161)     Door, RimWorld.Building_Door, Steel, 160 hit points -- INTACT
    gizmos             "Stop being a way home", "Send somebody through", and **"Load"**
                       -> the designation is live, the route is live, and our CompTransporter
                          attached, which means Attach() ran and `Available` was true
    right-click        **"Enter the gate"** -- the float menu works exactly as designed
    inspect string     "Please respawn this gate ... as an update has broken it"
                       -> that is `CompStargate.CompInspectStringExtra`, which is UNCONDITIONAL.
                          It is their nag for a gate that is not on `Building_Stargate` (whose
                          own `GetInspectString` calls `sgComp.GetInspectString()` instead and
                          never lets it run). **So their component is attached and healthy.**

So the component is on the door and the route is live, and the gate is simply never ACTIVE --
no `StargateIsActive`, therefore no event horizon, because their `PostDraw` only draws one when
it is open.

**And the one path that can stop the dial without saying a word is the far anchor.** The near
side returns early when `far == null || far.Map == null`, and that is plausible here: the
destination map parent carries `DoorThresholdContentVersion = 4`, and sites below it *"keep their
historical anchor until repaired"* -- an anchor that is not a door at all, which `as
ThingWithComps` turns into null.

That guard now reports like the others. One line, once per gate, and it names what it found --
because the whole reason this took a launch to narrow is that I wrote the failure paths to be
silent.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                    "CompRimroomsEmergence.cs")

OLD = u'''            StargateBridge.Attach(near, true);
            if (far == null || far.Map == null) { return; }
            StargateBridge.Attach(far, true);'''

NEW = u'''            StargateBridge.Attach(near, true);
            if (far == null)
            {
                // **The likeliest silent stop, and it used to say nothing.** A destination below
                // `DoorThresholdContentVersion` keeps a historical anchor that is not a door, so
                // `as ThingWithComps` yields null and the route has no far end to put a gate on.
                ReportGateState("the far end of this route is not a door, so no gate can be "
                                + "attached there");
                return;
            }
            if (far.Map == null)
            {
                ReportGateState("the far end is not on a loaded map");
                return;
            }
            StargateBridge.Attach(far, true);'''

text = io.open(COMP, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(COMP, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the far-anchor guard reports what it found")
