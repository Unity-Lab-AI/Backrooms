using Verse;
using Verse.AI;

namespace RimroomsAsyncIndustries.Threats
{
    // An attackable manifestation with site-directed movement. No native pawn AI or unbounded melee attacks.
    public sealed class Thing_QuietPursuer : ThingWithComps, IAttackTarget
    {
        private Map damageMap;
        Thing IAttackTarget.Thing { get { return this; } }
        public LocalTargetInfo TargetCurrentlyAimingAt { get { return LocalTargetInfo.Invalid; } }
        public float TargetPriorityFactor { get { return 1f; } }
        public bool ThreatDisabled(IAttackTargetSearcher disabledFor) { return Destroyed || !Spawned; }
        public override void PreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            damageMap = Map;
            base.PreApplyDamage(ref dinfo, out absorbed);
        }
        public override void PostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostApplyDamage(dinfo, totalDamageDealt);
            if (totalDamageDealt > 0f) { damageMap?.GetComponent<FirstSliceSiteComponent>().RepelPursuer(); }
        }
    }
}
