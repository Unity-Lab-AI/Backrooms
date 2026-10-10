using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace EdB.PrepareCarefully.HarmonyPatches;

[HarmonyPatch(typeof(Page_ConfigureStartingPawns))]
[HarmonyPatch("DoWindowContents")]
[HarmonyPatch(new Type[] { typeof(Rect) })]
internal class PrepareCarefullyButtonPatch
{
	private static void Postfix(Page_ConfigureStartingPawns __instance, ref Rect rect)
	{
		Vector2 vec = new Vector2(150f, 38f);
		float num = 75f;
		float y = rect.height + 55f;
		Rect rect2 = new Rect(rect.width / 2f - num, y, vec.x, vec.y);
		if (ModsConfig.BiotechActive)
		{
			float num2 = rect.width * 0.5f - 16f - vec.HalfX();
			rect2 = new Rect(16f + num2 * 0.5f, y, vec.x, vec.y);
		}
		if (!Widgets.ButtonText(rect2, "EdB.PC.Page.Button.PrepareCarefully".Translate(), drawBackground: true, doMouseoverSound: false))
		{
			return;
		}
		if (VersionControl.CurrentVersion < Mod.MinimumGameVersion)
		{
			Find.WindowStack.Add(new DialogInitializationError(null));
			SoundDefOf.ClickReject.PlayOneShot(null);
			Logger.Warning("Prepare Carefully failed to initialize because it requires at least version " + Mod.MinimumGameVersion?.ToString() + " of RimWorld.  You are running " + VersionControl.CurrentVersionString);
			return;
		}
		try
		{
			Mod.Instance.Start(__instance);
		}
		catch (Exception ex)
		{
			Find.WindowStack.Add(new DialogInitializationError(ex));
			SoundDefOf.ClickReject.PlayOneShot(null);
			throw new InitializationException("Prepare Carefully failed to initialize", ex);
		}
	}
}
