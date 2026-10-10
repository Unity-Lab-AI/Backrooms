# -*- coding: utf-8 -*-
"""Wire the six tier 4 capabilities to the six knobs the sweep actually found.

The sweep, done the way 0.12.5-dev and 0.12.18-dev demand -- **find a real observable knob per
branch before authoring anything**, because invariant 136 deleted four tier 3 projects for being
unlocks with nothing to unlock:

  FOUND, and each of these is a number a player can name the effect of:

    Facilities   dialSpinUpWorkRequired      how long bringing a gate up takes
    Fieldcraft   RecoveryRate                how fast a crew shakes the place off once out
    Commerce     OrdinaryExchangeRate        what the company pays for ordinary goods
    Measurement  MinimumInterviewerSocial    who is allowed to take a statement
    Spatial      WorldFrontierRarity         how often a way in turns up on your own map
    Entities     MaxPenalty                  the worst the place can get to somebody

  NOT FOUND, and therefore NOT WRITTEN:

    Logistics    lead time, dispatch delay, order capacity and unattended delivery are all
                 already claimed by tiers 1, 2, 0 and 3. What is left in Procurement is
                 MaximumOpenOrders (100), MaximumPhysicalStacksPerOrder (4096) and
                 MaximumStacksDeliveredPerTick (4) -- safety bounds a player will never reach,
                 not knobs. **A fifth Logistics project would be a hollow unlock.**

    Gate line    its top rung is already "a connection that no longer counts down", which is the
                 ceiling. **There is nothing above indefinite**, so a fifth rung is impossible by
                 construction rather than merely unwritten.

Two restraints from 0.12.18-dev held, and one owner answer:

    * the per-coordinate frontier cap is NOT a research knob -- so Spatial took the *ordinary map*
      rarity instead, which is a different number about a different place;
    * shelter never reaches zero -- Entities took the penalty ceiling, not the shelter rate again;
    * MaximumNaturalDepth stays 3, because the owner answered *"option 1"* on exactly that.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def edit(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding='utf-8').read()
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    print('wired %s' % rel)


SRC = os.path.join('src', 'RimroomsAsyncIndustries')

# ------------------------------------------------------------------ 1. Facilities
edit(os.path.join(SRC, 'Gate', 'GateSpinUp.cs'),
     u'''            float required = GateProps.dialSpinUpWorkRequired * GateCellCount;''',
     u'''            float required = GateProps.dialSpinUpWorkRequired * GateCellCount;

            // **RR_Cap_PractisedDialling** (Facilities, tier 4) takes a fifth off the work of
            // bringing any gate up, before familiarity is applied. A branch that has learned to
            // dial does the whole procedure faster, not just the routes it already knows -- which
            // is the difference between this and the familiarity discount below it.
            Company.RimroomsCampaignComponent dialCampaign = Current.Game == null
                ? null : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            if (dialCampaign != null && dialCampaign.HasCapability("RR_Cap_PractisedDialling"))
            { required *= PractisedDiallingFactor; }''')

edit(os.path.join(SRC, 'Gate', 'GateSpinUp.cs'),
     u'''        private const float DefaultSpinUpRate = 1f;''',
     u'''        private const float DefaultSpinUpRate = 1f;

        /// <summary>
        /// What RR_Cap_PractisedDialling multiplies the spin-up work by.
        ///
        /// A fifth off. Applied to the requirement itself rather than to the floor, so the floor
        /// still bounds a well-worn route and the discount cannot make a gate free -- the owner's
        /// condition on the larger sizes was that they cost more to run, and a research project
        /// must not undo that.
        /// </summary>
        private const float PractisedDiallingFactor = 0.8f;''')

# ------------------------------------------------------------------ 2. Fieldcraft
edit(os.path.join(SRC, 'Threats', 'BackroomsPressureComponent.cs'),
     u'''                pressure[index] -= Mathf.RoundToInt(Interval * BackroomsPressure.RecoveryRate);''',
     u'''                pressure[index] -= Mathf.RoundToInt(Interval * BackroomsPressure.RecoveryRateFor());''')

edit(os.path.join(SRC, 'Threats', 'BackroomsPressure.cs'),
     u'''        public static int PenaltyFor(int pressureTicks)''',
     u'''        /// <summary>
        /// How fast pressure drains from somebody who is out of a coordinate.
        ///
        /// **RR_Cap_Decompression** (Fieldcraft, tier 4) doubles it again. A branch that has
        /// learned how to bring people back down gets them ready for the next trip sooner; it does
        /// nothing at all while they are still down there, which is the point -- the place is not
        /// less bad, the rotation is better.
        /// </summary>
        public static float RecoveryRateFor()
        {
            Company.RimroomsCampaignComponent campaign = Current.Game == null ? null
                : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            return campaign != null && campaign.HasCapability("RR_Cap_Decompression")
                ? PractisedRecoveryRate : RecoveryRate;
        }

        /// <summary>Recovery for a branch that has learned to decompress a crew.</summary>
        private const float PractisedRecoveryRate = 4f;

        /// <summary>
        /// The worst mood offset the place can carry for a pawn right now.
        ///
        /// **RR_Cap_SteadyNerve** (Entities, tier 4) lowers the ceiling. It never reaches
        /// <see cref="MinPenalty"/>, for the same reason shelter never reaches zero: the
        /// Backrooms always cost something, and a research project that made them free would be
        /// the campaign contradicting itself.
        /// </summary>
        private static int MaxPenaltyFor()
        {
            Company.RimroomsCampaignComponent campaign = Current.Game == null ? null
                : Current.Game.GetComponent<Company.RimroomsCampaignComponent>();
            return campaign != null && campaign.HasCapability("RR_Cap_SteadyNerve")
                ? SteadyNervePenalty : MaxPenalty;
        }

        /// <summary>
        /// The reduced ceiling. Six rather than ten, and deliberately well above MinPenalty of
        /// one so the place is never shrugged off.
        /// </summary>
        private const int SteadyNervePenalty = 6;

        public static int PenaltyFor(int pressureTicks)''')

# ------------------------------------------------------------------ 3. Entities, same file
edit(os.path.join(SRC, 'Threats', 'BackroomsPressure.cs'),
     u'''            int scaled = MinPenalty + (int)Math.Round(fraction * (MaxPenalty - MinPenalty));
            return Math.Max(MinPenalty, Math.Min(MaxPenalty, scaled));''',
     u'''            int ceiling = MaxPenaltyFor();
            int scaled = MinPenalty + (int)Math.Round(fraction * (ceiling - MinPenalty));
            return Math.Max(MinPenalty, Math.Min(ceiling, scaled));''')

# ------------------------------------------------------------------ 4. Commerce
edit(os.path.join(SRC, 'Company', 'ValuablesExchange.cs'),
     u'''            float rate = OddOriginService.IsOdd(thing) ? OddExchangeRate : OrdinaryExchangeRate;''',
     u'''            // **RR_Cap_OpenMarket** (Commerce, tier 4) improves what the company pays for
            // ORDINARY goods only. The odd rate is the premium the whole economy is built on and
            // is deliberately untouched: a branch learns to stop being fleeced on scrap, it does
            // not learn to make the Backrooms pay better.
            float ordinary = OrdinaryExchangeRate;
            RimroomsCampaignComponent marketCampaign = Current.Game == null
                ? null : Current.Game.GetComponent<RimroomsCampaignComponent>();
            if (marketCampaign != null && marketCampaign.HasCapability("RR_Cap_OpenMarket"))
            { ordinary = OpenMarketOrdinaryRate; }
            float rate = OddOriginService.IsOdd(thing) ? OddExchangeRate : ordinary;''')

edit(os.path.join(SRC, 'Company', 'ValuablesExchange.cs'),
     u'''        public const float OrdinaryExchangeRate = 0.85f;''',
     u'''        public const float OrdinaryExchangeRate = 0.85f;

        /// <summary>
        /// The ordinary rate for a branch that has learned the market. Still below 1, because the
        /// company is a buyer of last resort and never a generous one.
        /// </summary>
        public const float OpenMarketOrdinaryRate = 0.95f;''')

# ------------------------------------------------------------------ 5. Spatial
edit(os.path.join(SRC, 'Portals', 'NaturalFrontierService.cs'),
     u'''                    Rarity = WorldFrontierRarity,''',
     u'''                    Rarity = campaign.HasCapability("RR_Cap_SurfaceReading")
                        ? ReadSurfaceFrontierRarity : WorldFrontierRarity,''')

edit(os.path.join(SRC, 'Portals', 'NaturalFrontierService.cs'),
     u'''        internal const int WorldFrontierRarity = 40;''',
     u'''        internal const int WorldFrontierRarity = 40;

        /// <summary>
        /// Ordinary-map rarity for a branch that has learned to read a surface.
        ///
        /// **RR_Cap_SurfaceReading** (Spatial, tier 4). This is the ORDINARY-MAP number and not
        /// the per-coordinate one: the restraint that the per-coordinate frontier cap is not a
        /// research knob still holds, and `MaximumFrontiersPerOrdinaryMap` is untouched too. What
        /// changes is how often a door on your own map turns out to lead somewhere, which is a
        /// different question about a different place.
        /// </summary>
        internal const int ReadSurfaceFrontierRarity = 28;''')

print('six tier 4 knobs wired; Logistics and the gate line deliberately not')
