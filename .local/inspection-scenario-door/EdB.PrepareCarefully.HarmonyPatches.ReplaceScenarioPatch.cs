using System;
using HarmonyLib;
using Verse;

namespace EdB.PrepareCarefully.HarmonyPatches;

[HarmonyPatch(typeof(Game))]
[HarmonyPatch("InitNewGame")]
[HarmonyPatch(new Type[] { })]
internal class ReplaceScenarioPatch
{
	[HarmonyPostfix]
	private static void Postfix()
	{
		Mod.Instance.RestoreScenarioParts();
		Mod.ClearInstance();
	}
}
