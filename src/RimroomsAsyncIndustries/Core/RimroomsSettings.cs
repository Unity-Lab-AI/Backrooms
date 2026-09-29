using System;
using System.Collections.Generic;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>User preferences; these never become campaign or expedition state.</summary>
    public sealed class RimroomsSettings : ModSettings
    {
        /// <summary>
        /// Player overrides for cross-gate work giver priorities, keyed by giver defName.
        ///
        /// Keyed by name rather than held as one field per giver so a work family added
        /// later needs no settings change and no migration. Only values that differ from
        /// the shipped XML are stored, so this is empty for anyone who never touches the
        /// sliders, and a future change to a shipped default is still picked up.
        /// </summary>
        public Dictionary<string, int> ConnectedWorkPriorities =
            new Dictionary<string, int>(StringComparer.Ordinal);

        public const float DefaultCueVolume = 0.5f;
        public bool MuteGateCues;
        public bool MuteFieldCues;
        public float CueVolume = DefaultCueVolume;
        public bool MenuSlideshowEnabled = true;
        public bool MenuReducedMotion;
        public bool PortalAuraEnabled = true;
        public bool PortalReducedMotion;

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
            Scribe_Values.Look(ref PortalAuraEnabled, "rr_portalAuraEnabled", true);
            Scribe_Values.Look(ref PortalReducedMotion, "rr_portalReducedMotion", false);
            // Additive: absent from every earlier preferences file, which loads correctly
            // as "no overrides" and therefore as the shipped priorities.
            Scribe_Collections.Look(ref ConnectedWorkPriorities, "rr_connectedWorkPriorities",
                LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                ConnectedWorkPriorities = ConnectedWorkPriorities ??
                    new Dictionary<string, int>(StringComparer.Ordinal);
                Normalize();
            }
        }
    }
}
