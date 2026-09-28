using System;
using RimroomsAsyncIndustries.Audio;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>RR-COMPAT: Core-only bootstrap; no profile changes or runtime patching.</summary>
    public sealed class RimroomsMod : Mod
    {
        public const string PackageId = "UnityLabAI.RimroomsAsyncIndustries";
        public static string ModVersion { get { return typeof(RimroomsMod).Assembly.GetName().Version.ToString(3); } }
        public static RimroomsSettings Settings { get; private set; }

        public RimroomsMod(ModContentPack content) : base(content)
        {
            try { Settings = GetSettings<RimroomsSettings>(); Settings?.Normalize(); }
            catch (Exception) { Settings = null; RimroomsAudio.WarnOnce("settings-load", "Audio preferences could not be loaded; cues remain silent."); }
            Log.Message("[Rimrooms][Build] " + ModVersion + " development package loaded. Gameplay acceptance is pending.");
        }

        public override string SettingsCategory() { return "Rimrooms - Async Industries"; }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            var listing = new Listing_Standard();
            listing.Begin(inRect);
            try
            {
                listing.Label("RR_Settings_AudioTitle".Translate());
                listing.Label("RR_Settings_AudioDescription".Translate());
                listing.Gap();
                if (Settings == null) { listing.Label("RR_Settings_AudioUnavailable".Translate()); return; }
                Settings.Normalize();
                listing.CheckboxLabeled("RR_Settings_MuteGateCues".Translate().ToString(), ref Settings.MuteGateCues);
                listing.CheckboxLabeled("RR_Settings_MuteFieldCues".Translate().ToString(), ref Settings.MuteFieldCues);
                listing.Label("RR_Settings_CueVolume".Translate((int)Math.Round(Settings.CueVolume * 100f)));
                Settings.CueVolume = listing.Slider(Settings.CueVolume, 0f, 1f);
            }
            finally { listing.End(); }
        }

        public override void WriteSettings()
        {
            Settings?.Normalize();
            base.WriteSettings();
        }
    }
}
