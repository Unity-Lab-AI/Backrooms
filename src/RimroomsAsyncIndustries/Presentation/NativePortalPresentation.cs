using System;
using RimroomsAsyncIndustries.Core;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>
    /// Native, cosmetic aura only. Portal state and crossing never depend on this effect.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"yes the gates are just repurosed doors of
    /// the game with a bue tint and maybe a blue light glow hue around it like light through a
    /// glass wall does"*.
    ///
    /// The aura used to appear **only while a connection was open**, which meant a gate was
    /// indistinguishable from any other door for almost all of its life. It is now the gate's
    /// permanent identity: a soft steady blue once designated, brighter and faster while a
    /// connection is live, and amber when something has gone wrong. The door's own blue tint
    /// comes from <see cref="CompRimroomsGate.ForceColor"/>; this is the light around it.
    ///
    /// Still a native fleck at fixed colour and size, so **no new art or graphic resource** is
    /// introduced, and it still respects the aura and reduced-motion settings — a player who
    /// turned the effect off gets a plainly tinted door and nothing moving.
    /// </summary>
    internal static class NativePortalPresentation
    {
        private static bool warned;

        /// <summary>Open: the brightest state, and the fastest pulse.</summary>
        private static readonly Color OpenColor = new Color(0.35f, 0.72f, 1f, 0.28f);

        /// <summary>Designated but closed: present, unmistakable, and not distracting.</summary>
        private static readonly Color IdleColor = new Color(0.35f, 0.72f, 1f, 0.12f);

        /// <summary>Something is wrong. Deliberately not blue, so it reads at a glance.</summary>
        private static readonly Color EmergencyColor = new Color(0.8f, 0.45f, 0.15f, 0.25f);

        internal static void Tick(CompRimroomsGate gate)
        {
            if (gate == null || !gate.IsDesignated ||
                RimroomsMod.Settings == null || !RimroomsMod.Settings.PortalAuraEnabled ||
                RimroomsMod.Settings.PortalReducedMotion || Find.TickManager == null) { return; }

            // A closed gate breathes slowly; a live one is obvious. Both are cheap: one fleck
            // every 30 or 90 ticks on the currently viewed map only.
            int interval = gate.IsOpening ? 30 : 90;
            if (Find.TickManager.TicksGame % interval != 0) { return; }

            Thing door = gate.parent;
            if (door == null || !door.Spawned || door.Map != Find.CurrentMap || door.Position.Fogged(door.Map)) { return; }
            try
            {
                Color color;
                float scale;
                if (gate.IsEmergency) { color = EmergencyColor; scale = 1.2f; }
                else if (gate.IsOpening) { color = OpenColor; scale = 1.2f; }
                else { color = IdleColor; scale = 1f; }

                // Native HeatGlow, fixed size/color, no random draw or new graphic resources.
                FleckCreationData data = FleckMaker.GetDataStatic(door.DrawPos, door.Map, FleckDefOf.HeatGlow, scale);
                data.instanceColor = color;
                data.solidTimeOverride = gate.IsOpening ? 0.5f : 1.2f;
                data.velocitySpeed = 0f;
                data.rotationRate = 0f;
                door.Map.flecks.CreateFleck(data);
            }
            catch (Exception exception)
            {
                if (!warned)
                {
                    warned = true;
                    Log.Warning("[Rimrooms] Native portal aura unavailable; portal text/state remains authoritative: " + exception.Message);
                }
            }
        }
    }
}
