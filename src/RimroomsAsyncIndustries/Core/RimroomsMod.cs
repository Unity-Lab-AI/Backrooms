using Verse;

namespace RimroomsAsyncIndustries.Core
{
    /// <summary>RR-COMPAT: Core-only bootstrap; no profile changes or runtime patching.</summary>
    public sealed class RimroomsMod : Mod
    {
        public const string PackageId = "UnityLabAI.RimroomsAsyncIndustries";
        public const string ModVersion = "0.1.0";

        public RimroomsMod(ModContentPack content) : base(content)
        {
            Log.Message("[Rimrooms] " + ModVersion + " foundation loaded. Campaign gameplay is not yet available.");
        }
    }
}
