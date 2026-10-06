using System;
using System.Collections.Generic;
using RimroomsAsyncIndustries.Core;
using RimWorld.Planet;
using Verse;
using Verse.Sound;

namespace RimroomsAsyncIndustries.Audio
{
    /// <summary>
    /// Optional main-thread presentation. Gameplay must never depend on a cue playing.
    ///
    /// Owner direction, 2026-10-06 -- *"a audio folder! sounds dope!!! how do we do sounds can we?"* --
    /// reversed the existing-content-only direction of 2026-09-28, so the company's four original
    /// cues ship again. The Core sounds they were redirected to in the meantime stay as the fallback
    /// rather than being deleted, because a cue that cannot be found should get quieter, not silent.
    /// </summary>
    public static class RimroomsAudio
    {
        private const int WarningLimit = 8;
        private static readonly HashSet<string> Warnings = new HashSet<string>(StringComparer.Ordinal);

        public static void Play(string cueId, Map map, IntVec3 cell, bool field)
        {
            try
            {
                if (!UnityData.IsInMainThread || Current.Game == null || Current.ProgramState != ProgramState.Playing ||
                    map == null || map.Disposed || !Find.Maps.Contains(map) || Find.CurrentMap != map ||
                    !WorldRendererUtility.DrawingMap || !cell.IsValid || !cell.InBounds(map)) { return; }

                RimroomsSettings settings = RimroomsMod.Settings;
                if (settings == null) { WarnOnce("settings", "Audio preferences are unavailable; cues remain silent."); return; }
                if ((field ? settings.MuteFieldCues : settings.MuteGateCues) || settings.EffectiveCueVolume <= 0f) { return; }

                // **OURS FIRST, CORE'S AS THE FALLBACK.** The company's own SoundDefs carry the same
                // defNames as the cue ids, so a resolved original is simply the cue id itself. A
                // package with no Sounds folder -- or one whose clips failed to resolve -- degrades to
                // the native cue it used while the existing-content-only direction held, instead of
                // going silent. The fallback is announced once so a missing folder is diagnosable.
                //
                // **THE NATIVE LOOKUP MOVED BELOW THIS AND THAT ORDER IS THE POINT.** It used to run
                // first and refuse any cue id it had no Core mapping for -- which was every one of
                // the thirteen cues delivered for the gate cycle. A guard written to catch a typo at
                // a call site was silently rejecting correct, shipped content, and the only symptom
                // would have been a gate that makes no sound.
                SoundDef definition = Usable(cueId);
                string native = ResolveNativeCue(cueId);
                if (definition == null && native != null)
                {
                    definition = Usable(native);
                    if (definition != null)
                    {
                        WarnOnce("fallback:" + cueId, "The company cue " + cueId + " is unavailable; falling back to " + native + ".");
                    }
                }
                if (definition == null)
                {
                    // Still reported, and the message now separates the two cases a reader needs to
                    // tell apart: a name nothing defines is a typo, a name that resolves to an
                    // unusable def is a packaging fault.
                    WarnOnce("def:" + cueId, native == null
                        ? "An unknown company cue was requested: " + cueId
                        : "Unavailable or incompatible map cue: " + cueId);
                    return;
                }

                // Where a cue plays is the def's own property, never a second derivation here. Our
                // cues are MapOnly and positional; the Core fallbacks for three of the four are
                // interface sounds and play at the camera.
                SoundInfo info = definition.subSounds[0].onCamera
                    ? SoundInfo.OnCamera()
                    : SoundInfo.InMap(new TargetInfo(cell, map));
                info.volumeFactor = settings.EffectiveCueVolume;
                definition.PlayOneShot(info);
            }
            catch (Exception error)
            {
                WarnOnce("exception:" + (cueId ?? "unknown"), "Cue skipped after a presentation error: " + error.GetType().Name);
            }
        }

        /// <summary>
        /// Start a looping cue, or return null.
        ///
        /// **THE CALLER MUST CALL `Maintain()` EVERY TICK, AND THAT IS THE SAFETY PROPERTY RATHER
        /// THAN A CHORE.** The sustainer is created with <see cref="MaintenanceType.PerTick"/>, so
        /// RimWorld ends it by itself the moment it stops being maintained. A gate that is
        /// destroyed, despawned, mid-save-load, or simply forgotten by a future edit therefore goes
        /// quiet on its own. **Forgetting to stop one is not a failure mode here** -- which is the
        /// whole reason `Usable` refuses a sustained def on the one-shot path, where forgetting
        /// would mean a hum that runs until the map unloads.
        ///
        /// The volume factor is read once at creation: a sustainer's volume is not re-read, so a
        /// player changing the slider mid-loop sees it apply to the next loop rather than this one.
        /// That is a deliberately small lie compared with restarting the sound under them.
        /// </summary>
        public static Sustainer TryStartSustainer(string cueId, Map map, IntVec3 cell, bool field)
        {
            try
            {
                if (!UnityData.IsInMainThread || Current.Game == null ||
                    Current.ProgramState != ProgramState.Playing || map == null || map.Disposed ||
                    !Find.Maps.Contains(map) || Find.CurrentMap != map ||
                    !cell.IsValid || !cell.InBounds(map)) { return null; }

                RimroomsSettings settings = RimroomsMod.Settings;
                if (settings == null) { return null; }
                if ((field ? settings.MuteFieldCues : settings.MuteGateCues) ||
                    settings.EffectiveCueVolume <= 0f) { return null; }

                SoundDef definition = DefDatabase<SoundDef>.GetNamedSilentFail(cueId);
                // The mirror image of `Usable`: this path takes **only** a sustained def, so a
                // one-shot can never be started as a loop that nothing will ever end.
                if (definition == null || definition.isUndefined || !definition.sustain ||
                    definition.context != SoundContext.MapOnly ||
                    definition.subSounds == null || definition.subSounds.Count == 0)
                { WarnOnce("loop:" + cueId, "Unavailable or non-looping cue requested as a loop: " + cueId); return null; }
                foreach (SubSoundDef subSound in definition.subSounds)
                {
                    // Missing resolved clips have zero duration, exactly as on the one-shot path.
                    if (subSound == null || !(subSound.Duration.TrueMax > 0f))
                    { WarnOnce("loopgrain:" + cueId, "A looping cue has no resolved clip: " + cueId); return null; }
                }

                SoundInfo info = SoundInfo.InMap(new TargetInfo(cell, map), MaintenanceType.PerTick);
                info.volumeFactor = settings.EffectiveCueVolume;
                return definition.TrySpawnSustainer(info);
            }
            catch (Exception error)
            {
                WarnOnce("loopexception:" + (cueId ?? "unknown"),
                    "Looping cue skipped after a presentation error: " + error.GetType().Name);
                return null;
            }
        }

        /// <summary>A def this presentation can actually play as a one shot, or null.</summary>
        private static SoundDef Usable(string defName)
        {
            if (string.IsNullOrWhiteSpace(defName)) { return null; }
            SoundDef definition = DefDatabase<SoundDef>.GetNamedSilentFail(defName);
            if (definition == null || definition.isUndefined || definition.sustain ||
                definition.subSounds == null || definition.subSounds.Count == 0 || definition.subSounds[0] == null)
            { return null; }

            // One SoundInfo is built for the whole def, so every subsound has to agree about where it
            // plays. A def that mixed them would play half of itself in the wrong place.
            bool onCamera = definition.subSounds[0].onCamera;
            if (!onCamera && definition.context != SoundContext.MapOnly) { return null; }
            foreach (SubSoundDef subSound in definition.subSounds)
            {
                // Missing resolved clips have zero duration. Avoid repeated native missing-grain errors.
                if (subSound == null || subSound.onCamera != onCamera || !(subSound.Duration.TrueMax > 0f)) { return null; }
            }
            return definition;
        }

        /// <summary>The Core cue each company cue fell back to while no original audio shipped.</summary>
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
