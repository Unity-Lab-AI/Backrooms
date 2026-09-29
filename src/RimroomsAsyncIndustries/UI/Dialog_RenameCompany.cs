using RimroomsAsyncIndustries.Company;
using Verse;

namespace RimroomsAsyncIndustries.UI
{
    /// <summary>
    /// Renaming the company through the game's own rename dialog, the same one used for
    /// zones, storage groups and caravans. Every start builds a company and names it
    /// their own, so this is available to all of them at any time.
    /// </summary>
    public sealed class Dialog_RenameCompany : Dialog_Rename<RimroomsCampaignComponent>
    {
        public Dialog_RenameCompany(RimroomsCampaignComponent campaign) : base(campaign) { }

        protected override int MaxNameLength
        { get { return RimroomsCampaignComponent.MaximumCompanyNameLength; } }

        protected override AcceptanceReport NameIsValid(string name)
        {
            AcceptanceReport inherited = base.NameIsValid(name);
            if (!inherited.Accepted) { return inherited; }
            // The company must always have something to be called, so a blank entry is
            // refused here rather than silently leaving the old name in place.
            if (string.IsNullOrWhiteSpace(name))
            { return new AcceptanceReport("RR_Company_InvalidName".Translate()); }
            return AcceptanceReport.WasAccepted;
        }

        protected override void OnRenamed(string name)
        {
            base.OnRenamed(name);
            renaming.NoteRenamed();
        }
    }
}
