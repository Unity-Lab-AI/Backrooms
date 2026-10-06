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
        public bool GateFramesEnabled = true;

        /// <summary>
        /// The three exchange rates, as player settings rather than shipped constants.
        ///
        /// **Owner direction, 2026-10-05, asked which way to resolve two open balance rows:**
        /// *"Make them player-visible settings"*. The rows said in their own words that the
        /// numbers were *"a first pass with no play behind them"* — and a first pass nobody can
        /// change without a rebuild is a first pass that stays.
        ///
        /// ## The defaults are the shipped numbers, and that is what keeps this honest
        ///
        /// Each default is the constant it replaces, so **a player who never opens the settings
        /// gets exactly the behaviour that shipped**, and an existing preferences file without
        /// these keys loads as the shipped values rather than as zero. The reasoning behind each
        /// number stays where it was written, on the constant in
        /// <see cref="Company.RimroomsCampaignComponent"/>; this makes it reachable, not arbitrary.
        ///
        /// **Clamped on read, never trusted raw.** A rate of zero would make selling destroy
        /// goods for nothing and a negative one would pay the player to lose them, so the
        /// accessor bounds every value. The ceiling is deliberately generous — somebody who
        /// wants an absurd economy is allowed one, and it cannot corrupt anything.
        /// </summary>
        public float OddExchangeRate = Company.RimroomsCampaignComponent.OddExchangeRate;
        public float OrdinaryExchangeRate = Company.RimroomsCampaignComponent.OrdinaryExchangeRate;
        public float OpenMarketOrdinaryRate = Company.RimroomsCampaignComponent.OpenMarketOrdinaryRate;

        /// <summary>
        /// A rate the exchange will actually use: finite, never negative, never absurd.
        ///
        /// **A guard rather than a preference.** Zero would make selling destroy goods for
        /// nothing, a negative rate would pay a player for losing them, and `NaN` would travel
        /// into a saved ledger balance, which is the one place a bad number becomes permanent.
        /// </summary>
        public static float SaneRate(float value, float fallback)
        {
            if (float.IsNaN(value) || float.IsInfinity(value)) { return fallback; }
            if (value < 0.01f) { return 0.01f; }
            return value > 100f ? 100f : value;
        }

        public float EffectiveOddExchangeRate
        { get { return SaneRate(OddExchangeRate, Company.RimroomsCampaignComponent.OddExchangeRate); } }

        public float EffectiveOrdinaryExchangeRate
        {
            get
            {
                return SaneRate(OrdinaryExchangeRate,
                    Company.RimroomsCampaignComponent.OrdinaryExchangeRate);
            }
        }

        public float EffectiveOpenMarketOrdinaryRate
        {
            get
            {
                return SaneRate(OpenMarketOrdinaryRate,
                    Company.RimroomsCampaignComponent.OpenMarketOrdinaryRate);
            }
        }

        /// <summary>
        /// A multiplier on every corporate supply tier's access fee.
        ///
        /// **Owner direction, 2026-10-05:** *"Make them player-visible settings"*, answering the
        /// catalogue-balance row as well as the exchange-rate one.
        ///
        /// **A multiplier rather than five sliders, and the shape is forced by the data.** Each
        /// tier's fee is `unlockCostCredits` on its own `RimroomsSupplyTierDef` -- content, not
        /// code -- so exposing them individually would mean a settings field per def and a new one
        /// every time a tier is authored. One multiplier scales the whole ladder and keeps the
        /// relative cost of the five tiers, which is the part the design actually decided.
        ///
        /// 1.0 is the shipped economy. Read at both the affordability test and the charge, so the
        /// button a player is offered and the money they are asked for can never disagree.
        /// </summary>
        public float SupplyFeeMultiplier = 1f;

        public float EffectiveSupplyFeeMultiplier
        { get { return SaneRate(SupplyFeeMultiplier, 1f); } }

        public float EffectiveCueVolume
        {
            get
            {
                if (float.IsNaN(CueVolume) || float.IsInfinity(CueVolume)) { return DefaultCueVolume; }
                return Math.Max(0f, Math.Min(1f, CueVolume));
            }
        }

        public void Normalize()
        {
            CueVolume = EffectiveCueVolume;
            OddExchangeRate = EffectiveOddExchangeRate;
            OrdinaryExchangeRate = EffectiveOrdinaryExchangeRate;
            OpenMarketOrdinaryRate = EffectiveOpenMarketOrdinaryRate;
            SupplyFeeMultiplier = EffectiveSupplyFeeMultiplier;
        }

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
            Scribe_Values.Look(ref GateFramesEnabled, "rr_gateFramesEnabled", true);
            // Additive: absent from every earlier preferences file, which loads correctly
            // as "no overrides" and therefore as the shipped priorities.
            Scribe_Collections.Look(ref ConnectedWorkPriorities, "rr_connectedWorkPriorities",
                LookMode.Value, LookMode.Value);
            // Additive, and each default is the shipped constant -- so a preferences file
            // written before these existed loads as the shipped economy rather than as zero,
            // which is the difference between an absent setting and a destructive one.
            Scribe_Values.Look(ref OddExchangeRate, "rr_oddExchangeRate",
                Company.RimroomsCampaignComponent.OddExchangeRate);
            Scribe_Values.Look(ref OrdinaryExchangeRate, "rr_ordinaryExchangeRate",
                Company.RimroomsCampaignComponent.OrdinaryExchangeRate);
            Scribe_Values.Look(ref OpenMarketOrdinaryRate, "rr_openMarketOrdinaryRate",
                Company.RimroomsCampaignComponent.OpenMarketOrdinaryRate);
            Scribe_Values.Look(ref SupplyFeeMultiplier, "rr_supplyFeeMultiplier", 1f);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                ConnectedWorkPriorities = ConnectedWorkPriorities ??
                    new Dictionary<string, int>(StringComparer.Ordinal);
                Normalize();
            }
        }
    }
}
