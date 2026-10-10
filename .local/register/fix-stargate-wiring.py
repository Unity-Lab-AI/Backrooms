# -*- coding: utf-8 -*-
"""Wire the Stargate mod's own gate onto both ends of a Backrooms route, and dial it ourselves.

Owner, across four messages, each one a requirement:

    "we use the fucjkign stargate MOD but use a normal door im not telling u again"
    "and connect them together to the backrooms and the map"
    "we just use our own dialing converstion in the background"
    "we still use the stargate mod as normal but we also use it for our backrroms purposes"

and the complaint that started it:

    "i shouldnt have to click on the door right to send a pawn through it and how the fuck are
     they suppose to auto pick up materials on one side and use them on the other"

WHAT THEIR SOURCE ACTUALLY PROVIDES, read from the `Source/` folder they ship:

  * `CompStargate : ThingComp` -- so it goes on an ordinary Core `Door`. That is the whole of
    *"but use a normal door"*, and it needs no new ThingDef.
  * `InitGate()` registers the gate's own address on spawn: `parent.Map.Tile` for an ordinary
    map, `parent.Map.Index` for a pocket map. **Both ends register themselves** once attached.
  * `_transComp ??= parent.GetComp<CompTransporter>()` and `JobDriver_BringToStargate` --
    **this is the automatic hauling.** With Core's transporter on the door, colonists haul the
    chosen materials to the gate on their own and the gate sends them through. That is the
    answer to *"auto pick up materials on one side"*, and it is their mod doing it.
  * `OpenStargateDelayed(address, delay, DialMode)` is public -- **our dialling conversion in
    the background** calls it, so the player never touches a DHD for the Backrooms.

ATTACHED PER INSTANCE, NOT PER DEF, AND THAT IS THE LOAD-BEARING DECISION. A `comps` patch
applies to the def, so putting `CompStargate` on Core's `Door` would make **every door in every
colony** a stargate. Their `InitGate` permits one gate per map and hibernates the rest **with a
message**, so a nine-door shop would announce eight hibernating gates on the first tick, and
every existing save would gain gates nobody asked for. `ThingWithComps.AllComps` is a public
list, so the component goes on the **door this company designated** and on nothing else — which
is also what keeps *"we still use the stargate mod as normal"* true.

BOTH ENDS, FROM THE EDGE. The far anchor stands inside a coordinate, which is not an ordinary
branch map, so it can never designate itself. The near side already knows the edge, so it
attaches both.

ONE THING THE OWNER SHOULD KNOW AND CAN VETO: the component borrows the `CompProperties` off
their own `StargateMod_Stargate` def rather than constructing one, so a Backrooms gate is
configured **exactly** as their stargate is — their textures, their draw size, and **their
unstable-vortex pattern**, which vaporises what stands in front of the gate when it opens. That
is their mod behaving as it normally does, which is what was asked for, but it is thirteen cells
of kawoosh on a shop's back wall. Say the word and it becomes a door-sized pattern instead.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                    "CompRimroomsEmergence.cs")

OLD = u"""        /// <summary>How often a gate is asked whether it should look like one.</summary>"""

NEW_METHOD = u'''        /// <summary>
        /// **The Stargate mod's own gate, on both ends of this route, dialled by us.**
        ///
        /// Owner: *"we use the fucjkign stargate MOD but use a normal door"*, *"and connect them
        /// together to the backrooms and the map"*, *"we just use our own dialing converstion in
        /// the background"*, *"we still use the stargate mod as normal but we also use it for our
        /// backrroms purposes"*.
        ///
        /// Three steps, and none of them touches their mod:
        ///
        /// 1. **both ends get their component.** The far anchor stands inside a coordinate, which
        ///    is not an ordinary branch map, so it can never mark itself — the near side knows the
        ///    edge, so it attaches both. Core's transporter goes on with it, and that is what
        ///    makes colonists **haul the chosen materials to the door on their own**.
        /// 2. **we dial.** Their address space is a `PlanetTile`, and this company already knows
        ///    which door leads to which coordinate, so the conversion is reading the destination
        ///    map's own address. No DHD, no player input.
        /// 3. **it stays open**, because a natural gate is permanently open — invariant 12. Their
        ///    wormhole times out on its own, so re-dialling an idle gate is what keeps the route
        ///    a route rather than an appointment.
        ///
        /// Silent and harmless when the Stargate mod is absent: every call answers false and the
        /// Backrooms behave exactly as they did before.
        /// </summary>
        private void RefreshStargate()
        {
            if (!StargateBridge.Available || parent == null || !parent.Spawned) { return; }
            PortalConnectionRecord edge = EdgeFor();
            if (edge == null || !IsLiveGate) { return; }

            ThingWithComps near = parent;
            ThingWithComps far = FarAnchor(edge);
            StargateBridge.Attach(near);
            if (far == null || far.Map == null) { return; }
            StargateBridge.Attach(far);

            // Dialled only from this side, and only when nothing is already open. Their gate is
            // one-way by design, so dialling a receiving end would fight their own rule rather
            // than use it.
            if (StargateBridge.IsOpen(near) || StargateBridge.IsReceiving(near)) { return; }
            if (StargateBridge.IsHibernating(near)) { return; }
            StargateBridge.Dial(near, far.Map, 0);
        }

        /// <summary>The door at the other end of this route, as a thing that can carry comps.</summary>
        private ThingWithComps FarAnchor(PortalConnectionRecord edge)
        {
            if (edge == null) { return null; }
            Thing first = edge.First == null ? null : edge.First.Anchor;
            Thing second = edge.Second == null ? null : edge.Second.Anchor;
            Thing other = first == parent ? second : first;
            return other as ThingWithComps;
        }

        /// <summary>How often a gate is asked whether it should look like one.</summary>'''

text = io.open(COMP, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW_METHOD, 1)

# Called from the same interval tick that paints the gate: one place that asks "is this a gate
# yet", so the appearance and the wormhole can never disagree about the answer.
CALL_OLD = u'''            if (parent == null || !parent.IsHashIntervalTick(AppearanceInterval, delta)) { return; }
            RefreshGateAppearance();'''
CALL_NEW = u'''            if (parent == null || !parent.IsHashIntervalTick(AppearanceInterval, delta)) { return; }
            RefreshGateAppearance();
            // Same tick, same question. If the appearance and the wormhole were refreshed from
            // different places they could disagree about whether this is a gate.
            RefreshStargate();'''
if text.count(CALL_OLD) != 1:
    print("CALL ANCHOR PROBLEM: %d" % text.count(CALL_OLD))
    raise SystemExit(1)
text = text.replace(CALL_OLD, CALL_NEW, 1)

RARE_OLD = u'''        public override void CompTickRare()
        {
            base.CompTickRare();
            RefreshGateAppearance();
        }'''
RARE_NEW = u'''        public override void CompTickRare()
        {
            base.CompTickRare();
            RefreshGateAppearance();
            RefreshStargate();
        }'''
if text.count(RARE_OLD) != 1:
    print("RARE ANCHOR PROBLEM: %d" % text.count(RARE_OLD))
    raise SystemExit(1)
text = text.replace(RARE_OLD, RARE_NEW, 1)

io.open(COMP, "w", encoding="utf-8", newline="").write(text)
print("stargate wiring applied: both ends attached, dialled from our own network")
