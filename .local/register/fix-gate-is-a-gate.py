# -*- coding: utf-8 -*-
"""A natural gate has to LOOK like a gate and be WALKED THROUGH like one.

Owner, verbatim: *"its not blue!!! it doesnt have a light aura, and it in no way is a portal to
the back rooms.. wtf!!! im getting tired of this shit... you actually have to plug all the work we
did on the gates into the game so they work and the pawns can walk from tmap to map like the
stargate mod works but with normal does.. wtf!!! ive said stargate mod repeaditly is how the gates
work"*.

Three separate things, and all three are real.

1. **THE LEVEL NEVER GENERATED.** Fixed separately -- a conduit carpet sized for 12x12 rooms blew
   a 512-cell cap eightfold at 80x80, so `MarkLayoutReady` never ran and the door was never
   marked. **An unmarked door is an ordinary steel door**, which is everything the owner is
   looking at.

2. **IT DOES NOT LOOK LIKE A GATE.** Fixed here. `CompGlower` and `CompColorable` are both Core,
   both settable **per instance** (`GlowColor`, `GlowRadius`, `SetColor`), so a live gate can be
   blue and can cast light with **no new texture and no new def**.

   The trap was that adding a glower to `Door` would make **every door in every colony** carry
   one. Core solves it: `CompGlower.ShouldBeLitNow` walks every comp on the parent and asks any
   that implements **`IThingGlower`**. So `CompRimroomsEmergence` implements it and returns false
   unless this door is a live gate -- every ordinary door is **provably** unlit by Core's own
   rule rather than by hoping.

3. **IT IS NOT WALKED THROUGH THE WAY A PLAYER EXPECTS.** The travel job already existed and
   already works like the owner describes -- `PortalTravelService.OrderCrossing` makes a real job
   that walks the pawn to the cell beside the door and crosses to the other map. What was missing
   is that the only way to ask for it was: select pawns, select the door, click a gizmo, pick from
   a float menu. **`ThingComp.CompFloatMenuOptions(Pawn selPawn)`** is the RimWorld idiom for
   *"right-click this with that colonist selected"*, and that is where a player looks. Added.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")


def edit(path, pairs):
    enc = "utf-8-sig" if path.endswith(".xml") else "utf-8"
    text = io.open(path, encoding="utf-8-sig").read()
    problems = []
    for old, _ in pairs:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (os.path.basename(path), text.count(old), old[:64]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM: %s" % problem)
        raise SystemExit(1)
    for old, new in pairs:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding=enc, newline="").write(text)
    print("%s: %d edit(s)" % (os.path.basename(path), len(pairs)))


# ------------------------------------------------------------------ the comps on the door
edit(os.path.join(MOD, "Patches", "RR_NativeGateProviders.xml"), [
    ("""        <xpath>Defs/ThingDef[defName="Door" or defName="Autodoor"]/comps</xpath>
        <value>
          <li Class="RimroomsAsyncIndustries.Portals.CompProperties_RimroomsEmergence" />
        </value>""",
     """        <xpath>Defs/ThingDef[defName="Door" or defName="Autodoor"]/comps</xpath>
        <value>
          <li Class="RimroomsAsyncIndustries.Portals.CompProperties_RimroomsEmergence" />
          <!-- A GATE LOOKS LIKE A GATE. Owner, 2026-09-30: *"its not blue!!! it doesnt have a
               light aura, and it in no way is a portal to the back rooms"*, and repeatedly
               before that, that the Stargate mod is the model for how a gate reads and behaves.

               Both comps are Core and both are settable PER INSTANCE -- `CompGlower.GlowColor`
               and `GlowRadius` have setters backed by per-instance overrides, and
               `CompColorable.SetColor` is per thing. So a live gate is blue and casts light with
               NO new texture and NO new def, which is the existing-content rule kept exactly.

               WHY THIS DOES NOT TOUCH ANY OTHER DOOR IN THE GAME, and this is the load-bearing
               part. `CompGlower.ShouldBeLitNow` walks every comp on the parent and asks any that
               implements `Verse.IThingGlower`. `CompRimroomsEmergence` implements it and answers
               false unless this door is a live gate, so every ordinary door in every colony and
               every door any other mod ships carries an inert glower that Core itself refuses to
               light. That is a guarantee from Core's own rule rather than a hope.

               The radius and colour here are only defaults; the comp overrides both when a gate
               goes live, and the blue is the one the owner asked for. -->
          <li Class="CompProperties_Glower">
            <glowRadius>0</glowRadius>
            <glowColor>(70,130,220,0)</glowColor>
          </li>
          <li Class="CompProperties_Colorable" />
        </value>"""),
])


# ------------------------------------------------------------------ the comp drives both
edit(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs"), [
    ("    public class CompRimroomsEmergence : ThingComp\n    {",
     """    public class CompRimroomsEmergence : ThingComp, IThingGlower
    {
        /// <summary>The blue the owner asked for, and the reach of its light.</summary>
        private static readonly ColorInt LiveGlowColor = new ColorInt(70, 130, 220, 0);
        private const float LiveGlowRadius = 6f;

        /// <summary>
        /// Whether Core should light this door.
        ///
        /// **This one method is why adding a glower to `Door` does not change any other door in
        /// the game.** `CompGlower.ShouldBeLitNow` walks every comp on its parent and asks any
        /// that implements <see cref="IThingGlower"/>; a single false from any of them keeps the
        /// glower dark and unregistered. So every ordinary door in every colony, and every door
        /// any other mod ships, carries an inert glower — refused by Core's own rule rather than
        /// by hoping the radius of zero is enough.
        /// </summary>
        public bool ShouldBeLitNow() { return IsLiveGate; }

        /// <summary>
        /// A marked door on a branch map that the portal network actually has an edge for.
        ///
        /// Stricter than <see cref="IsDesignated"/> on purpose: a door the player marked but
        /// which nothing leads through yet is a plan, not a gate, and lighting it blue would
        /// promise a way through that does not exist.
        /// </summary>
        public bool IsLiveGate
        {
            get
            {
                if (!IsDesignated || parent == null || Verse.Current.Game == null) { return false; }
                RimroomsPortalNetwork network = Verse.Current.Game.GetComponent<RimroomsPortalNetwork>();
                if (network == null || network.Connections == null) { return false; }
                IReadOnlyList<PortalConnectionRecord> edges = network.Connections;
                for (int index = 0; index < edges.Count; index++)
                {
                    PortalConnectionRecord edge = edges[index];
                    if (edge == null) { continue; }
                    if ((edge.First != null && edge.First.Anchor == parent) ||
                        (edge.Second != null && edge.Second.Anchor == parent))
                    { return true; }
                }
                return false;
            }
        }

        /// <summary>
        /// Make the door read as a gate, or stop. Idempotent, and safe to call every rare tick.
        ///
        /// The colour and the radius are set through the per-instance overrides Core exposes, so
        /// nothing here edits a shared `CompProperties` — which would recolour every door at once.
        /// </summary>
        private void RefreshGateAppearance()
        {
            if (parent == null || !parent.Spawned) { return; }
            bool live = IsLiveGate;
            CompGlower glower = parent.TryGetComp<CompGlower>();
            if (glower != null)
            {
                glower.GlowRadius = live ? LiveGlowRadius : 0f;
                glower.GlowColor = LiveGlowColor;
                glower.UpdateLit(parent.Map);
                parent.Map.glowGrid.DirtyCache(parent.Position);
            }
            CompColorable colorable = parent.TryGetComp<CompColorable>();
            if (colorable != null)
            {
                if (live) { colorable.SetColor(LiveGlowColor.ToColor); }
                else if (colorable.Active) { colorable.Disable(); }
            }
        }

        /// <summary>Rare, because a gate going live is an event and not a per-frame question.</summary>
        public override void CompTickRare()
        {
            base.CompTickRare();
            RefreshGateAppearance();
        }

        /// <summary>
        /// Right-click the gate with a colonist selected and walk through it.
        ///
        /// **Owner direction, repeated and then repeated angrily:** *"ive said stargate mod
        /// repeaditly is how the gates work ... the pawns can walk from tmap to map like the
        /// stargate mod works but with normal does"*.
        ///
        /// The order and the job already existed and already did exactly that:
        /// `PortalTravelService.OrderCrossing` makes a real job that walks the pawn to the cell
        /// beside the door and crosses to the other map. **What was missing was the place a
        /// player looks for it.** It was only reachable by selecting pawns, selecting the door,
        /// clicking a gizmo and choosing from a float menu — which is a dispatch console, not a
        /// door you walk through.
        ///
        /// `CompFloatMenuOptions` is Core's own hook for *"right-click this with that colonist
        /// selected"*, and it is the same hook every piece of Core content uses for *go here and
        /// do this*. Nothing is decided here: the order is still
        /// <see cref="PortalTravelService.OrderCrossing"/> and the rule is still
        /// `PortalTraversalPolicy`, so invariant 1 holds — this is where the question is asked,
        /// not a second opinion about the answer.
        /// </summary>
        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption option in base.CompFloatMenuOptions(selPawn))
            { yield return option; }
            if (selPawn == null || parent == null || !parent.Spawned) { yield break; }
            if (!IsLiveGate) { yield break; }
            PortalConnectionRecord edge = EdgeFor();
            if (edge == null) { yield break; }
            // Refusals are shown as a disabled row with the reason, never hidden: a name missing
            // from a menu tells the player nothing, and "drafted" or "in transit" is something
            // they need told.
            string refusal = RimroomsPortalCrossingService.EligibilityFailureKey(selPawn);
            if (refusal != null)
            {
                yield return new FloatMenuOption(
                    "RR_DoorCross_EnterRefused".Translate(refusal.Translate()), null);
                yield break;
            }
            PortalConnectionRecord subject = edge;
            yield return new FloatMenuOption("RR_DoorCross_Enter".Translate(), delegate
            {
                Show(PortalTravelService.OrderCrossing(selPawn, subject));
            });
        }

        /// <summary>The live edge this door is an endpoint of, or null.</summary>
        private PortalConnectionRecord EdgeFor()
        {
            RimroomsPortalNetwork network = Verse.Current.Game == null
                ? null : Verse.Current.Game.GetComponent<RimroomsPortalNetwork>();
            if (network == null || network.Connections == null) { return null; }
            IReadOnlyList<PortalConnectionRecord> edges = network.Connections;
            for (int index = 0; index < edges.Count; index++)
            {
                PortalConnectionRecord edge = edges[index];
                if (edge == null) { continue; }
                if ((edge.First != null && edge.First.Anchor == parent) ||
                    (edge.Second != null && edge.Second.Anchor == parent))
                { return edge; }
            }
            return null;
        }
"""),
])

print("gate appearance and walk-through applied")
