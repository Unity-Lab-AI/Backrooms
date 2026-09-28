using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Core;
using RimWorld.Planet;
using Verse;
using Verse.Sound;

namespace RimroomsAsyncIndustries.Audio
{
    /// <summary>Optional main-thread presentation. Gameplay must never depend on a cue playing.</summary>
    public static class RimroomsAudio
    {
        private const int WarningLimit = 8;
        private static readonly HashSet<string> Warnings = new HashSet<string>(StringComparer.Ordinal);

        public static void Play(string cueId, Map map, IntVec3 cell, bool field)
        {
            string defName = ResolveNativeCue(cueId);
            try
            {
                if (!UnityData.IsInMainThread || Current.Game == null || Current.ProgramState != ProgramState.Playing ||
                    map == null || map.Disposed || !Find.Maps.Contains(map) || Find.CurrentMap != map ||
                    !WorldRendererUtility.DrawingMap || !cell.IsValid || !cell.InBounds(map)) { return; }

                RimroomsSettings settings = RimroomsMod.Settings;
                if (settings == null) { WarnOnce("settings", "Audio preferences are unavailable; cues remain silent."); return; }
                if ((field ? settings.MuteFieldCues : settings.MuteGateCues) || settings.EffectiveCueVolume <= 0f) { return; }
                if (string.IsNullOrWhiteSpace(defName)) { WarnOnce("name", "An unknown company cue was requested."); return; }

                // Existing Core sounds are referenced at runtime; no Rimrooms sound assets or Def clones.
                bool onCamera = cueId != "RR_GatePowerRise";
                SoundDef definition = DefDatabase<SoundDef>.GetNamedSilentFail(defName);
                if (definition == null || definition.isUndefined || definition.sustain || (!onCamera && definition.context != SoundContext.MapOnly) ||
                    definition.subSounds == null || definition.subSounds.Count == 0)
                { WarnOnce("def:" + defName, "Unavailable or incompatible map cue: " + defName); return; }
                foreach (SubSoundDef subSound in definition.subSounds)
                {
                    // Missing resolved clips have zero duration. Avoid repeated native missing-grain errors.
                    if (subSound == null || subSound.onCamera != onCamera || !(subSound.Duration.TrueMax > 0f))
                    { WarnOnce("grain:" + defName, "A native cue has no compatible resolved clip: " + defName); return; }
                }

                SoundInfo info = onCamera ? SoundInfo.OnCamera() : SoundInfo.InMap(new TargetInfo(cell, map));
                info.volumeFactor = settings.EffectiveCueVolume;
                definition.PlayOneShot(info);
            }
            catch (Exception error)
            {
                WarnOnce("exception:" + (defName ?? "unknown"), "Cue skipped after a presentation error: " + error.GetType().Name);
            }
        }

        private static string ResolveNativeCue(string cueId)
        {
            switch (cueId)
            {
                case "RR_GatePowerRise": return "Power_OnSmall";
                case "RR_GateWarning": return "Message_ThreatSmall";
                case "RR_FieldRadio": return "CommsWindow_Open";
                case "RR_SpatialTell": return "Message_NegativeEvent";
                default: return null;
            }
        }

        internal static void WarnOnce(string key, string message)
        {
            // A warning is also presentation and must not throw back into an action service.
            try
            {
                if (Warnings.Count < WarningLimit && Warnings.Add(key)) { Log.Warning("[Rimrooms][Audio] " + message); }
            }
            catch (Exception) { }
        }
    }
}
