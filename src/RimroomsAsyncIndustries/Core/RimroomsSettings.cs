using System;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>User audio preferences; these never become campaign or expedition state.</summary>
    public sealed class RimroomsSettings : ModSettings
    {
        public const float DefaultCueVolume = 0.5f;
        public bool MuteGateCues;
        public bool MuteFieldCues;
        public float CueVolume = DefaultCueVolume;
        public bool MenuSlideshowEnabled = true;
        public bool MenuReducedMotion;

        public float EffectiveCueVolume
        {
            get
            {
                if (float.IsNaN(CueVolume) || float.IsInfinity(CueVolume)) { return DefaultCueVolume; }
                return Math.Max(0f, Math.Min(1f, CueVolume));
            }
        }

        public void Normalize() { CueVolume = EffectiveCueVolume; }

        public override void ExposeData()
        {
            if (Scribe.mode == LoadSaveMode.Saving) { Normalize(); }
            base.ExposeData();
            Scribe_Values.Look(ref MuteGateCues, "rr_muteGateCues", false);
            Scribe_Values.Look(ref MuteFieldCues, "rr_muteFieldCues", false);
            Scribe_Values.Look(ref CueVolume, "rr_cueVolume", DefaultCueVolume);
            Scribe_Values.Look(ref MenuSlideshowEnabled, "rr_menuSlideshowEnabled", true);
            Scribe_Values.Look(ref MenuReducedMotion, "rr_menuReducedMotion", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) { Normalize(); }
        }
    }
}
