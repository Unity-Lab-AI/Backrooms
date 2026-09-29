using System;
using RimroomsAsyncIndustries.Core;
using RimroomsAsyncIndustries.Gate;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Presentation
{
    /// <summary>Native, cosmetic aura only. Portal state and crossing never depend on this effect.</summary>
    internal static class NativePortalPresentation
    {
        private static bool warned;

        internal static void Tick(CompRimroomsGate gate)
        {
            if (gate == null || !gate.IsNativeProvider || !gate.IsDesignated || !gate.IsOpening ||
                RimroomsMod.Settings == null || !RimroomsMod.Settings.PortalAuraEnabled ||
                RimroomsMod.Settings.PortalReducedMotion || Find.TickManager == null ||
                Find.TickManager.TicksGame % 30 != 0) { return; }
            Thing door = gate.parent;
            if (door == null || !door.Spawned || door.Map != Find.CurrentMap || door.Position.Fogged(door.Map)) { return; }
            try
            {
                // Native HeatGlow, fixed size/color, no random draw or new graphic resources.
                FleckCreationData data = FleckMaker.GetDataStatic(door.DrawPos, door.Map, FleckDefOf.HeatGlow, 1.2f);
                data.instanceColor = gate.IsEmergency ? new Color(0.8f, 0.45f, 0.15f, 0.25f)
                    : new Color(0.2f, 0.65f, 0.7f, 0.2f);
                data.solidTimeOverride = 0.5f;
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
