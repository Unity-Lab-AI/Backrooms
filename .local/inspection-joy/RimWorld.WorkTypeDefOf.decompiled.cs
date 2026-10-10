using Verse;

namespace RimWorld;

[DefOf]
public static class WorkTypeDefOf
{
	public static WorkTypeDef Mining;

	public static WorkTypeDef Growing;

	public static WorkTypeDef Construction;

	public static WorkTypeDef Warden;

	public static WorkTypeDef Doctor;

	public static WorkTypeDef Firefighter;

	public static WorkTypeDef Hunting;

	public static WorkTypeDef Handling;

	public static WorkTypeDef Crafting;

	public static WorkTypeDef Hauling;

	public static WorkTypeDef Cleaning;

	public static WorkTypeDef Research;

	public static WorkTypeDef PlantCutting;

	public static WorkTypeDef Smithing;

	[MayRequireBiotech]
	public static WorkTypeDef Childcare;

	[MayRequireAnomaly]
	public static WorkTypeDef DarkStudy;

	[MayRequireOdyssey]
	public static WorkTypeDef Fishing;

	static WorkTypeDefOf()
	{
		DefOfHelper.EnsureInitializedInCtor(typeof(WorkTypeDefOf));
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.1.0.9782' (yours is '9.1.0.7988')
