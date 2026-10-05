using System;
using System.Reflection;
using RimroomsAsyncIndustries.Audio;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>RR-COMPAT: Core-only bootstrap; no profile changes or runtime patching.</summary>
    public sealed class RimroomsMod : Mod
    {
        public const string PackageId = "Rimrooms.AsyncIndustries";
        private static readonly string CachedModVersion = ResolveModVersion();

        public static string ModVersion { get { return CachedModVersion; } }

        private static string ResolveModVersion()
        {
            Assembly assembly = typeof(RimroomsMod).Assembly;
            var informational = Attribute.GetCustomAttribute(assembly, typeof(AssemblyInformationalVersionAttribute))
                as AssemblyInformationalVersionAttribute;
            if (informational != null && !string.IsNullOrWhiteSpace(informational.InformationalVersion))
            {
                string value = informational.InformationalVersion;
                int metadataIndex = value.IndexOf('+');
                return metadataIndex < 0 ? value : value.Substring(0, metadataIndex);
            }
            Version version = assembly.GetName().Version;
            return version == null ? "unknown" : version.ToString(3);
        }
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
            // Two columns: the priority sliders are tall enough that one column would run
            // off the bottom of the window and become unreachable.
            listing.ColumnWidth = (inRect.width - 34f) / 2f;
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
                listing.GapLine();
                listing.Label("RR_Menu_SettingsTitle".Translate());
                listing.CheckboxLabeled("RR_Menu_SlideshowEnabled".Translate().ToString(), ref Settings.MenuSlideshowEnabled);
                listing.CheckboxLabeled("RR_Menu_ReducedMotion".Translate().ToString(), ref Settings.MenuReducedMotion);
                listing.GapLine();
                listing.CheckboxLabeled("RR_NativeGate_AuraEnabled".Translate().ToString(), ref Settings.PortalAuraEnabled);
                listing.CheckboxLabeled("RR_NativeGate_ReducedMotion".Translate().ToString(), ref Settings.PortalReducedMotion);
                listing.GapLine();
                DrawExchangeRates(listing);

                listing.NewColumn();
                DrawWorkPriorities(listing);
            }
            finally { listing.End(); }
        }

        /// <summary>
        /// What the company pays, as three sliders rather than three constants.
        ///
        /// **Owner direction, 2026-10-05, asked how to resolve two open balance rows:** *"Make
        /// them player-visible settings"*. Both rows said in their own words that the numbers were
        /// *"a first pass with no play behind them"* — and a first pass nobody can change without
        /// a rebuild is a first pass that never gets a second.
        ///
        /// **The same reasoning as the work-priority sliders beside them:** whether a rate feels
        /// right is a play judgement, and a play judgement belongs to whoever is playing. The
        /// shipped numbers stay the defaults, so changing nothing changes nothing.
        ///
        /// The ranges are deliberately wide on the low side and generous on the high: a player who
        /// wants the company to be a worse deal than any trader can have that, and one who wants
        /// an absurd economy can have that too. `RimroomsSettings.SaneRate` is what stops either
        /// from reaching a saved ledger balance as a zero or a `NaN`.
        /// </summary>
        private static void DrawExchangeRates(Listing_Standard listing)
        {
            listing.Label("RR_Settings_ExchangeTitle".Translate());
            listing.Label("RR_Settings_ExchangeDescription".Translate());
            if (Settings == null)
            {
                listing.Label("RR_Settings_AudioUnavailable".Translate());
                return;
            }
            listing.Label("RR_Settings_RateOdd".Translate(
                Settings.EffectiveOddExchangeRate.ToString("0.00")));
            Settings.OddExchangeRate = listing.Slider(Settings.EffectiveOddExchangeRate, 0.1f, 5f);
            listing.Label("RR_Settings_RateOrdinary".Translate(
                Settings.EffectiveOrdinaryExchangeRate.ToString("0.00")));
            Settings.OrdinaryExchangeRate =
                listing.Slider(Settings.EffectiveOrdinaryExchangeRate, 0.1f, 2f);
            listing.Label("RR_Settings_RateOpenMarket".Translate(
                Settings.EffectiveOpenMarketOrdinaryRate.ToString("0.00")));
            Settings.OpenMarketOrdinaryRate =
                listing.Slider(Settings.EffectiveOpenMarketOrdinaryRate, 0.1f, 2f);
            listing.Label("RR_Settings_SupplyFee".Translate(
                Settings.EffectiveSupplyFeeMultiplier.ToString("0.00")));
            Settings.SupplyFeeMultiplier =
                listing.Slider(Settings.EffectiveSupplyFeeMultiplier, 0.1f, 5f);
        }

        /// <summary>
        /// How eagerly colonists cross a gate to work. These are the one part of the
        /// cross-gate layer that cannot be settled by reading source: whether a number
        /// feels right is a play judgement, so it belongs to whoever is playing.
        /// </summary>
        private static void DrawWorkPriorities(Listing_Standard listing)
        {
            listing.Label("RR_Settings_WorkPriorityTitle".Translate());
            listing.Label("RR_Settings_WorkPriorityDescription".Translate());
            if (Settings == null || !ConnectedWorkPriorities.Captured)
            {
                listing.Label("RR_Settings_WorkPriorityUnavailable".Translate());
                return;
            }
            foreach (ConnectedWorkPriorityPair pair in ConnectedWorkPriorities.Families)
            {
                // A family whose givers are not in this game gets no control. Four are gated by
                // `MayRequire` and this pane used to draw all of them regardless -- a slider for
                // work the player does not own, reporting a shipped default of zero because
                // nothing was ever loaded to read one from. See `ConnectedWorkPriorities.Present`.
                if (!ConnectedWorkPriorities.Present(pair)) { continue; }
                listing.Gap(6f);
                listing.Label(pair.LabelKey.Translate());
                DrawPriority(listing, "RR_Settings_PriorityContinue", pair.ContinueDefName);
                DrawPriority(listing, "RR_Settings_PriorityPlan", pair.PlanDefName);
                // Said out loud rather than corrected in silence, so a slider that refuses
                // to stay where it was dragged explains why.
                if (ConnectedWorkPriorities.WasClamped(Settings, pair))
                { listing.Label("RR_Settings_PriorityClamped".Translate()); }
            }
            listing.Gap();
            if (listing.ButtonText("RR_Settings_WorkPriorityReset".Translate()))
            { ConnectedWorkPriorities.ResetToShipped(Settings); }
        }

        private static void DrawPriority(Listing_Standard listing, string labelKey, string giverDefName)
        {
            int current = ConnectedWorkPriorities.Effective(Settings, giverDefName);
            listing.Label(labelKey.Translate(current, ConnectedWorkPriorities.Shipped(giverDefName)));
            int updated = (int)Math.Round(listing.Slider(current,
                ConnectedWorkPriorities.MinimumPriority,
                ConnectedWorkPriorities.Ceiling(giverDefName)));
            if (updated != current) { ConnectedWorkPriorities.Set(Settings, giverDefName, updated); }
        }

        public override void WriteSettings()
        {
            Settings?.Normalize();
            base.WriteSettings();
            // Applied here rather than on every slider frame: pushing the values into the
            // defs re-sorts a work type and invalidates every pawn's cached giver order, so
            // it belongs at the moment the player is finished, not mid-drag. Closing the
            // window is enough — no mod reload and no restart.
            ConnectedWorkPriorities.Apply(Settings);
        }
    }
}
