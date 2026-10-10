using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using OgreStack.PersistentData;
using OgreStack.Support;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace OgreStack;

public class OgreStackMod : Mod
{
	public OgreStackSettings settings;

	private Dictionary<string, List<Thing>> _activeThings = null;

	private static readonly List<Category> _PROCESSING_ORDER = new List<Category>
	{
		Category.SmallVolumeResource,
		Category.Resource,
		Category.RawFoodMeat,
		Category.RawFoodPlant,
		Category.PlantMatter,
		Category.Meal,
		Category.FoodForAnimal,
		Category.Food,
		Category.Item,
		Category.BodyPartOrImplant,
		Category.Leather,
		Category.Textile,
		Category.StoneBlock,
		Category.Manufactured,
		Category.Drug,
		Category.Medicine,
		Category.MortarShell,
		Category.Artifact
	};

	public static readonly Dictionary<Category, CategorySetting> _DEFAULTS = new Dictionary<Category, CategorySetting>
	{
		{
			Category.SmallVolumeResource,
			new CategorySetting(MultiplierMode.Scalar, 30f)
		},
		{
			Category.Resource,
			new CategorySetting(MultiplierMode.Fixed, 1000f)
		},
		{
			Category.RawFoodMeat,
			new CategorySetting(MultiplierMode.Fixed, 1000f)
		},
		{
			Category.RawFoodPlant,
			new CategorySetting(MultiplierMode.Fixed, 1000f)
		},
		{
			Category.PlantMatter,
			new CategorySetting(MultiplierMode.Fixed, 2000f)
		},
		{
			Category.Meal,
			new CategorySetting(MultiplierMode.Fixed, 150f)
		},
		{
			Category.FoodForAnimal,
			new CategorySetting(MultiplierMode.Fixed, 2000f)
		},
		{
			Category.Food,
			new CategorySetting(MultiplierMode.Fixed, 1000f)
		},
		{
			Category.Item,
			new CategorySetting(MultiplierMode.Fixed, 20f)
		},
		{
			Category.BodyPartOrImplant,
			new CategorySetting(MultiplierMode.Fixed, 5f)
		},
		{
			Category.Leather,
			new CategorySetting(MultiplierMode.Fixed, 1000f)
		},
		{
			Category.Textile,
			new CategorySetting(MultiplierMode.Fixed, 1000f)
		},
		{
			Category.StoneBlock,
			new CategorySetting(MultiplierMode.Fixed, 2500f)
		},
		{
			Category.Manufactured,
			new CategorySetting(MultiplierMode.Scalar, 10f)
		},
		{
			Category.Drug,
			new CategorySetting(MultiplierMode.Fixed, 4000f)
		},
		{
			Category.Medicine,
			new CategorySetting(MultiplierMode.Fixed, 75f)
		},
		{
			Category.MortarShell,
			new CategorySetting(MultiplierMode.Fixed, 25f)
		},
		{
			Category.Artifact,
			new CategorySetting(MultiplierMode.Fixed, 10f)
		},
		{
			Category.Other,
			new CategorySetting(MultiplierMode.Scalar, 10f)
		}
	};

	private static readonly HashSet<string> _CATEGORIES_BANNED = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "Chunks", "Furniture", "StoneChunks", "WeaponsMelee", "Books" };

	public OgreStackMod(ModContentPack content)
		: base(content)
	{
		settings = ((Mod)this).GetSettings<OgreStackSettings>();
		settings.ReModify = delegate
		{
			Log.Message("[OgreStack]: Remodify From Settings Change");
			_activeThings = new Dictionary<string, List<Thing>>();
			List<Map> maps = Find.Maps;
			if (maps != null)
			{
				foreach (Map item in maps)
				{
					if (item != null && item.listerThings != null)
					{
						List<Thing> allThings = item.listerThings.AllThings;
						foreach (Thing item2 in allThings)
						{
							if (item2 != null && item2.def != null && !string.IsNullOrEmpty(((Def)item2.def).defName) && isStackIncreaseAllowed(item2.def))
							{
								if (!_activeThings.ContainsKey(((Def)item2.def).defName))
								{
									_activeThings.Add(((Def)item2.def).defName, new List<Thing>());
								}
								_activeThings[((Def)item2.def).defName].Add(item2);
							}
						}
					}
				}
			}
			ModifyStackSizes();
			_activeThings.Clear();
			_activeThings = null;
		};
		LongEventHandler.QueueLongEvent((Action)delegate
		{
			LongEventHandler.QueueLongEvent((Action)delegate
			{
				ModifyStackSizes();
			}, "OgreStack_Init_Execute", true, (Action<Exception>)null, true, false, (Action)null);
		}, "OgreStack_Init_Reg", true, (Action<Exception>)null, true, false, (Action)null);
	}

	public override string SettingsCategory()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(Translator.Translate("OgreStack.ModName"));
	}

	public override void DoSettingsWindowContents(Rect rect)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Expected O, but got Unknown
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Expected O, but got Unknown
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Expected O, but got Unknown
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Expected O, but got Unknown
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Expected O, but got Unknown
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Expected O, but got Unknown
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Expected O, but got Unknown
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_015e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_0195: Unknown result type (might be due to invalid IL or missing references)
		//IL_0197: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Unknown result type (might be due to invalid IL or missing references)
		//IL_023e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0243: Unknown result type (might be due to invalid IL or missing references)
		//IL_0245: Unknown result type (might be due to invalid IL or missing references)
		//IL_024c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0269: Unknown result type (might be due to invalid IL or missing references)
		//IL_026e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0270: Unknown result type (might be due to invalid IL or missing references)
		//IL_0275: Unknown result type (might be due to invalid IL or missing references)
		//IL_0277: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_032e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0333: Unknown result type (might be due to invalid IL or missing references)
		//IL_035f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0372: Unknown result type (might be due to invalid IL or missing references)
		//IL_0377: Unknown result type (might be due to invalid IL or missing references)
		//IL_0379: Unknown result type (might be due to invalid IL or missing references)
		//IL_0380: Unknown result type (might be due to invalid IL or missing references)
		//IL_039d: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0404: Unknown result type (might be due to invalid IL or missing references)
		//IL_0409: Unknown result type (might be due to invalid IL or missing references)
		//IL_0418: Unknown result type (might be due to invalid IL or missing references)
		//IL_0421: Unknown result type (might be due to invalid IL or missing references)
		//IL_0462: Unknown result type (might be due to invalid IL or missing references)
		//IL_0467: Unknown result type (might be due to invalid IL or missing references)
		//IL_04a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_04bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_04cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_04d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_04e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_04f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_04f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0553: Unknown result type (might be due to invalid IL or missing references)
		//IL_0568: Unknown result type (might be due to invalid IL or missing references)
		//IL_056d: Unknown result type (might be due to invalid IL or missing references)
		//IL_056f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0576: Unknown result type (might be due to invalid IL or missing references)
		//IL_0580: Unknown result type (might be due to invalid IL or missing references)
		//IL_0591: Unknown result type (might be due to invalid IL or missing references)
		//IL_0598: Unknown result type (might be due to invalid IL or missing references)
		//IL_059d: Unknown result type (might be due to invalid IL or missing references)
		//IL_059f: Unknown result type (might be due to invalid IL or missing references)
		//IL_05a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_05a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_05a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_05af: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_05cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_05dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_05e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_05e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0643: Unknown result type (might be due to invalid IL or missing references)
		//IL_0648: Unknown result type (might be due to invalid IL or missing references)
		//IL_064a: Unknown result type (might be due to invalid IL or missing references)
		//IL_064f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0651: Unknown result type (might be due to invalid IL or missing references)
		//IL_067d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0691: Unknown result type (might be due to invalid IL or missing references)
		//IL_0696: Unknown result type (might be due to invalid IL or missing references)
		//IL_0698: Unknown result type (might be due to invalid IL or missing references)
		//IL_06a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_06a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_06ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_06ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_06b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_06bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_06df: Unknown result type (might be due to invalid IL or missing references)
		//IL_06ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_06f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0715: Unknown result type (might be due to invalid IL or missing references)
		//IL_071a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0725: Unknown result type (might be due to invalid IL or missing references)
		//IL_072c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0731: Unknown result type (might be due to invalid IL or missing references)
		//IL_0733: Unknown result type (might be due to invalid IL or missing references)
		//IL_073a: Unknown result type (might be due to invalid IL or missing references)
		//IL_073f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0741: Unknown result type (might be due to invalid IL or missing references)
		//IL_0743: Unknown result type (might be due to invalid IL or missing references)
		//IL_0748: Unknown result type (might be due to invalid IL or missing references)
		//IL_074d: Unknown result type (might be due to invalid IL or missing references)
		//IL_074f: Unknown result type (might be due to invalid IL or missing references)
		//IL_07af: Unknown result type (might be due to invalid IL or missing references)
		//IL_07db: Unknown result type (might be due to invalid IL or missing references)
		//IL_088c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0891: Unknown result type (might be due to invalid IL or missing references)
		//IL_08a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_08aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_08ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_08b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_08ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_08c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_08d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_08da: Unknown result type (might be due to invalid IL or missing references)
		//IL_08df: Unknown result type (might be due to invalid IL or missing references)
		//IL_08e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_093e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0946: Unknown result type (might be due to invalid IL or missing references)
		//IL_094b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0966: Unknown result type (might be due to invalid IL or missing references)
		//IL_098e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0993: Unknown result type (might be due to invalid IL or missing references)
		//IL_099e: Unknown result type (might be due to invalid IL or missing references)
		//IL_09b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_09b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_09ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_09bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_09c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_09cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_09d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_09ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_09f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_09fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a0c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0829: Unknown result type (might be due to invalid IL or missing references)
		//IL_082e: Unknown result type (might be due to invalid IL or missing references)
		//IL_083f: Unknown result type (might be due to invalid IL or missing references)
		//IL_084a: Unknown result type (might be due to invalid IL or missing references)
		//IL_084c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0859: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a4b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a50: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a52: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a57: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a59: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a85: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a99: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a9e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0aa0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0aa8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0aaf: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ab4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ab6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0abb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ac4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ace: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ad6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0add: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ae2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ae4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ae9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0af2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b01: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b09: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b3d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b72: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b77: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b8b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b90: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b92: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b97: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ba0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ba7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bb8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bc0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bc5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bc7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c24: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c38: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c3d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c3f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c47: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c4e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c53: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c55: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c5a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c63: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c6a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c75: Unknown result type (might be due to invalid IL or missing references)
		//IL_0c7d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ca2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ca7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0cac: Unknown result type (might be due to invalid IL or missing references)
		//IL_0cb7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0cbe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0cc3: Unknown result type (might be due to invalid IL or missing references)
		Color textColor = default(Color);
		((Color)(ref textColor))..ctor(1f, 0.972549f, 0.23921569f, 1f);
		GUIStyleState normal = new GUIStyleState
		{
			textColor = textColor
		};
		GUIStyle val = new GUIStyle(Text.CurFontStyle);
		val.fontStyle = (FontStyle)1;
		val.normal = normal;
		GUIStyle val2 = new GUIStyle(Text.CurFontStyle);
		val2.alignment = (TextAnchor)3;
		val2.fontSize = 11;
		val2.fontStyle = (FontStyle)1;
		val2.normal = new GUIStyleState
		{
			textColor = new Color(1f, 63f / 85f, 0.23921569f, 1f)
		};
		val2.padding = new RectOffset(4, 0, 0, 0);
		Listing_Standard val3 = new Listing_Standard((GameFont)1);
		Listing_Standard val4 = new Listing_Standard((GameFont)1);
		List<KeyValuePair<string, int>> list = new IndividualOverrides().ViewInternalOverrides();
		float num = 3f * (Text.LineHeight + 2f) + 2f * val2.lineHeight + 30f + 23f * (Text.LineHeight + 7f) + (float)list.Count * (Text.LineHeight + 3f) + 40f;
		Rect val5 = default(Rect);
		((Rect)(ref val5))..ctor(0f, 0f, ((Rect)(ref rect)).width - 25f, num);
		Widgets.BeginScrollView(rect, ref settings.ScrollPosition, val5, true);
		Rect val6 = GenUI.LeftPart(val5, 0.78f);
		Rect val7 = GenUI.RightPart(val5, 0.2f);
		((Listing)val4).ColumnWidth = ((Rect)(ref val7)).width;
		((Listing)val4).Begin(val7);
		Rect rect2 = ((Listing)val4).GetRect(Text.LineHeight + 2f, 1f);
		TextAnchor anchor = Text.Anchor;
		Text.Anchor = (TextAnchor)0;
		GUI.Box(rect2, TaggedString.op_Implicit(Translator.Translate("OgreStack.SectionHeader.Presets")), val);
		Text.Anchor = anchor;
		Color color = GUI.color;
		GUI.color = Color.grey;
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 1f, ((Rect)(ref rect2)).width);
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 2f, ((Rect)(ref rect2)).width);
		GUI.color = color;
		rect2 = ((Listing)val4).GetRect(val2.lineHeight, 1f);
		GUI.Box(rect2, TaggedString.op_Implicit(Translator.Translate("OgreStack.Presets.Section.Ogre")), val2);
		rect2 = ((Listing)val4).GetRect(7f, 1f);
		color = GUI.color;
		GUI.color = Color.grey;
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + 3f, ((Rect)(ref rect2)).width);
		GUI.color = color;
		foreach (Preset ogrePreset in Presets.GetOgrePresets())
		{
			rect2 = ((Listing)val4).GetRect(Text.LineHeight, 1f);
			GUI.SetNextControlName(ogrePreset.NameKey);
			if (Widgets.ButtonText(rect2, TaggedString.op_Implicit(Translator.Translate(ogrePreset.NameKey)), true, true, true, (TextAnchor?)null))
			{
				ogrePreset.Modify(settings);
			}
			rect2 = ((Listing)val4).GetRect(1f, 1f);
		}
		((Listing)val4).GetRect(7f, 1f);
		rect2 = ((Listing)val4).GetRect(val2.lineHeight, 1f);
		GUI.Box(rect2, TaggedString.op_Implicit(Translator.Translate("OgreStack.Presets.Section.Scalar")), val2);
		rect2 = ((Listing)val4).GetRect(7f, 1f);
		color = GUI.color;
		GUI.color = Color.grey;
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + 3f, ((Rect)(ref rect2)).width);
		GUI.color = color;
		foreach (Preset scalarPreset in Presets.GetScalarPresets())
		{
			rect2 = ((Listing)val4).GetRect(Text.LineHeight, 1f);
			GUI.SetNextControlName(scalarPreset.NameKey);
			if (Widgets.ButtonText(rect2, TaggedString.op_Implicit(Translator.Translate(scalarPreset.NameKey)), true, true, true, (TextAnchor?)null))
			{
				scalarPreset.Modify(settings);
			}
			rect2 = ((Listing)val4).GetRect(1f, 1f);
		}
		((Listing)val4).End();
		((Listing)val3).ColumnWidth = ((Rect)(ref val6)).width;
		((Listing)val3).Begin(val6);
		rect2 = ((Listing)val3).GetRect(Text.LineHeight + 2f, 1f);
		anchor = Text.Anchor;
		Text.Anchor = (TextAnchor)0;
		GUI.Box(rect2, TaggedString.op_Implicit(Translator.Translate("OgreStack.SectionHeader.Settings")), val);
		Text.Anchor = anchor;
		color = GUI.color;
		GUI.color = Color.grey;
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 1f, ((Rect)(ref rect2)).width);
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 2f, ((Rect)(ref rect2)).width);
		GUI.color = color;
		Rect rect3 = ((Listing)val3).GetRect(val2.lineHeight, 1f);
		GUI.Box(GenUI.LeftPart(rect3, 0.6f), TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.Category")), val2);
		Rect val8 = GenUI.RightPart(rect3, 0.4f);
		Rect val9 = GenUI.LeftHalf(val8);
		GUI.Box(val9, TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.Mode")), val2);
		GUI.Box(GenUI.RightHalf(val8), TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.Value")), val2);
		TooltipHandler.TipRegion(val9, TipSignal.op_Implicit(Translator.Translate("OgreStack.Settings.Mode.Desc")));
		List<Category> list2 = new List<Category>(_PROCESSING_ORDER);
		list2.Add(Category.Other);
		foreach (Category c in list2)
		{
			Rect rect4 = ((Listing)val3).GetRect(7f, 1f);
			color = GUI.color;
			GUI.color = Color.grey;
			Widgets.DrawLineHorizontal(((Rect)(ref rect4)).x, ((Rect)(ref rect4)).y + 3f, ((Rect)(ref rect4)).width);
			GUI.color = color;
			Rect rect5 = ((Listing)val3).GetRect(Text.LineHeight, 1f);
			Widgets.DrawHighlightIfMouseover(rect5);
			Rect val10 = GenUI.LeftPart(rect5, 0.6f);
			anchor = Text.Anchor;
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(val10, Translator.Translate("OgreStack.Settings." + c.ToString() + ".Title"));
			Text.Anchor = anchor;
			TooltipHandler.TipRegion(val10, TipSignal.op_Implicit(Translator.Translate("OgreStack.Settings." + c.ToString() + ".Desc")));
			Rect val11 = GenUI.RightPart(rect5, 0.4f);
			Rect val12 = GenUI.LeftPart(val11, 0.49f);
			Rect val13 = GenUI.Rounded(GenUI.RightHalf(val11));
			Widgets.Dropdown<MultiplierMode, MultiplierMode>(val12, MultiplierMode.Fixed, (Func<MultiplierMode, MultiplierMode>)((MultiplierMode s) => s), (Func<MultiplierMode, IEnumerable<DropdownMenuElement<MultiplierMode>>>)((MultiplierMode s) => new List<DropdownMenuElement<MultiplierMode>>
			{
				new DropdownMenuElement<MultiplierMode>
				{
					option = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.Mode.Scalar")), (Action)delegate
					{
						settings.Values[c].Mode = MultiplierMode.Scalar;
					}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
					payload = MultiplierMode.Scalar
				},
				new DropdownMenuElement<MultiplierMode>
				{
					option = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.Mode.Fixed")), (Action)delegate
					{
						settings.Values[c].Mode = MultiplierMode.Fixed;
					}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
					payload = MultiplierMode.Fixed
				}
			}), TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.Mode." + settings.Values[c].Mode)), (Texture2D)null, (string)null, (Texture2D)null, (Action)null, false);
			settings.Values[c].Buffer = Widgets.TextField(val13, settings.Values[c].Buffer);
			if (!settings.Values[c].ParseBuffer())
			{
				color = GUI.color;
				GUI.color = new Color(0.662745f, 0f, 0f);
				Widgets.DrawBox(GenUI.Rounded(val13), 2, (Texture2D)null);
				GUI.color = color;
			}
		}
		Rect rect6 = ((Listing)val3).GetRect(15f, 1f);
		rect2 = ((Listing)val3).GetRect(Text.LineHeight + 2f, 1f);
		anchor = Text.Anchor;
		Text.Anchor = (TextAnchor)0;
		GUI.Box(rect2, TaggedString.op_Implicit(Translator.Translate("OgreStack.SectionHeader.SingleThingDefTargeting")), val);
		Text.Anchor = anchor;
		color = GUI.color;
		GUI.color = Color.grey;
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 1f, ((Rect)(ref rect2)).width);
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 2f, ((Rect)(ref rect2)).width);
		GUI.color = color;
		anchor = Text.Anchor;
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(((Listing)val3).GetRect(Text.LineHeight * 3f, 1f), TranslatorFormattedStringExtensions.Translate("OgreStack.Settings.SingleThingDefTargeting.Desc", new NamedArgument((object)DataUtil.GenerateFilePath(DataUtil._OVERRIDES_FILE_NAME).Replace("/", "\\"), "{0}")));
		Text.Anchor = anchor;
		rect3 = ((Listing)val3).GetRect(val2.lineHeight, 1f);
		anchor = Text.Anchor;
		Text.Anchor = (TextAnchor)3;
		GUI.Box(GenUI.LeftPart(rect3, 0.35f), TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.DefName")), val2);
		GUI.Box(GenUI.RightPart(rect3, 0.65f), TaggedString.op_Implicit(Translator.Translate("OgreStack.Settings.StackLimit")), val2);
		Text.Anchor = anchor;
		foreach (KeyValuePair<string, int> item in list)
		{
			string key = item.Key;
			int value = item.Value;
			Rect rect7 = ((Listing)val3).GetRect(3f, 1f);
			color = GUI.color;
			GUI.color = Color.grey;
			Widgets.DrawLineHorizontal(((Rect)(ref rect7)).x, ((Rect)(ref rect7)).y + 1f, ((Rect)(ref rect7)).width);
			GUI.color = color;
			Rect rect8 = ((Listing)val3).GetRect(Text.LineHeight, 1f);
			Widgets.DrawHighlightIfMouseover(rect8);
			Rect val14 = GenUI.LeftPart(rect8, 0.35f);
			anchor = Text.Anchor;
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(val14, key);
			Text.Anchor = anchor;
			Rect val15 = GenUI.RightPart(rect8, 0.65f);
			anchor = Text.Anchor;
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(val15, value.ToString());
			Text.Anchor = anchor;
			TooltipHandler.TipRegion(rect8, TipSignal.op_Implicit("From Rule:\n<item defName=\"" + key + "\" stackLimit=\"" + value + "\" />"));
		}
		rect6 = ((Listing)val3).GetRect(15f, 1f);
		rect2 = ((Listing)val3).GetRect(Text.LineHeight + 2f, 1f);
		anchor = Text.Anchor;
		Text.Anchor = (TextAnchor)0;
		GUI.Box(rect2, TaggedString.op_Implicit(Translator.Translate("OgreStack.SectionHeader.Debug")), val);
		Text.Anchor = anchor;
		color = GUI.color;
		GUI.color = Color.grey;
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 1f, ((Rect)(ref rect2)).width);
		Widgets.DrawLineHorizontal(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y + ((Rect)(ref rect2)).height - 2f, ((Rect)(ref rect2)).width);
		GUI.color = color;
		Rect rect9 = ((Listing)val3).GetRect(Text.LineHeight, 1f);
		Widgets.DrawHighlightIfMouseover(rect9);
		Rect val16 = GenUI.LeftPart(rect9, 0.8f);
		anchor = Text.Anchor;
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(val16, Translator.Translate("OgreStack.Settings.CSV.Title"));
		Text.Anchor = anchor;
		TooltipHandler.TipRegion(val16, TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("OgreStack.Settings.CSV.Desc", new NamedArgument((object)DataUtil.GenerateFilePath("OgreStack_DefsList.csv").Replace("/", "\\"), "{0}"))));
		Rect val17 = GenUI.RightPart(rect9, 0.2f);
		Widgets.Checkbox(((Rect)(ref val17)).x + ((Rect)(ref val17)).width - 26f, ((Rect)(ref val17)).y, ref settings.IsDebug, 24f, false, false, (Texture2D)null, (Texture2D)null);
		((Listing)val3).End();
		Widgets.EndScrollView();
	}

	private List<ModDefinition> getSupportedMods()
	{
		List<ModDefinition> list = new List<ModDefinition>
		{
			new VegetableGarden(),
			new RimCuisine2(),
			new CuprosDrinks(),
			new TiberiumRim(),
			new MedievalTimes(),
			new GeneticRim(),
			new ExpandedWoodworking(),
			new RimWorldOfMagic(),
			new Ammunition(),
			new VanillaExpanded(),
			new AestheticMaterials(),
			new AlphaGenes(),
			new MedievalOverhaul(),
			new MiscForbid(),
			new RimWorld()
		};
		foreach (ModDefinition item in list)
		{
			item.Init();
		}
		return list;
	}

	private bool isStackIncreaseAllowed(ThingDef d)
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Invalid comparison between Unknown and I4
		if (d == null || d.thingCategories == null || d.thingCategories.Count <= 0 || d.FirstThingCategory == null)
		{
			return false;
		}
		bool flag = d.IsStuff || d.isTechHediff || ((int)d.category == 2 && !d.isUnfinishedThing && !d.IsCorpse && !d.destroyOnDrop && !d.IsRangedWeapon && !d.IsApparel && !d.Minifiable && !d.IsArt && !d.IsBed);
		if (flag)
		{
			flag = !_CATEGORIES_BANNED.Contains(((object)d.FirstThingCategory).ToString());
		}
		if (flag && d.comps != null && d.comps.Count > 0)
		{
			foreach (CompProperties comp in d.comps)
			{
				if (comp.compClass == typeof(CompQuality))
				{
					flag = d.stackLimit > 1;
					break;
				}
			}
		}
		return flag;
	}

	internal void ModifyStackSizes()
	{
		//IL_03ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b3: Invalid comparison between Unknown and I4
		//IL_03bf: Unknown result type (might be due to invalid IL or missing references)
		List<ModDefinition> supportedMods = getSupportedMods();
		List<Category> list = new List<Category>(_PROCESSING_ORDER);
		supportedMods.Reverse();
		list.Reverse();
		List<string[]> list2 = null;
		IndividualOverrides individualOverrides = new IndividualOverrides();
		bool isDebug = settings.IsDebug;
		if (isDebug)
		{
			list2 = new List<string[]>();
		}
		Dictionary<Category, bool> dictionary = _PROCESSING_ORDER.ToDictionary((Category x) => x, (Category y) => settings.Values[y].ParseBuffer());
		foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
		{
			if (!isStackIncreaseAllowed(allDef))
			{
				continue;
			}
			string text = CategorySetting.GetBaseStackLimit(allDef).ToString();
			string text2 = string.Empty + text;
			string text3 = "Other " + settings.Values[Category.Other].ToString();
			string text4 = string.Empty;
			bool flag = false;
			int itemLevelOverride = individualOverrides.GetItemLevelOverride(((Def)allDef).defName);
			if (itemLevelOverride > 0)
			{
				flag = true;
				allDef.stackLimit = itemLevelOverride;
				text3 = "UserOverride.SetStackLimit(" + ((Def)allDef).defName + ": " + itemLevelOverride + ")";
				text4 = "Overrides.xml";
			}
			if (individualOverrides.IsCategoryBanned(((object)allDef.FirstThingCategory).ToString()))
			{
				flag = true;
				allDef.stackLimit = 1;
				text3 = "UserOverride.BanStacking(Category: " + ((object)allDef.FirstThingCategory).ToString() + ")";
				text4 = "Overrides.xml";
			}
			if (!flag)
			{
				for (int num = supportedMods.Count - 1; num > -1; num--)
				{
					if (supportedMods[num].IsNonStackable(allDef))
					{
						flag = true;
						text3 = "StackChangeForbidden";
						text4 = supportedMods[num].GetType().ToString();
						break;
					}
					for (int num2 = list.Count - 1; num2 > -1; num2--)
					{
						List<Func<ThingDef, bool>> categoryFunctions = supportedMods[num].GetCategoryFunctions(list[num2]);
						if (categoryFunctions != null)
						{
							foreach (Func<ThingDef, bool> item in categoryFunctions)
							{
								flag = item(allDef);
								text2 = allDef.stackLimit.ToString();
								if (flag)
								{
									if (dictionary[list[num2]])
									{
										settings.Values[list[num2]].ProcessThing(allDef, _activeThings);
									}
									text3 = list[num2].ToString() + " " + settings.Values[list[num2]].ToString();
									text4 = supportedMods[num].GetType().Name.ToString();
									num = (num2 = -1);
									break;
								}
							}
						}
					}
				}
			}
			if (!flag)
			{
				settings.Values[Category.Other].ProcessThing(allDef, _activeThings);
				text4 = "OgreStack.Other";
			}
			if (allDef.stackLimit > 1)
			{
				allDef.drawGUIOverlay = true;
				if ((int)allDef.resourceReadoutPriority == 0)
				{
					allDef.resourceReadoutPriority = (ResourceCountPriority)2;
				}
			}
			if (isDebug)
			{
				list2.Add(new string[7]
				{
					((Def)allDef).defName,
					((object)allDef.FirstThingCategory).ToString(),
					text,
					text2,
					text3,
					allDef.stackLimit.ToString(),
					text4
				});
			}
		}
		ResourceCounter.ResetDefs();
		HashSet<string> hashSet = new HashSet<string>(DefDatabase<ThingDef>.AllDefs.Select((ThingDef x) => ((Def)x).defName));
		foreach (TreeNode_ThingCategory allThingCategoryNode in ThingCategoryNodeDatabase.allThingCategoryNodes)
		{
			for (int num3 = allThingCategoryNode.catDef.childThingDefs.Count - 1; num3 > -1; num3--)
			{
				if (!hashSet.Contains(((Def)allThingCategoryNode.catDef.childThingDefs[num3]).defName))
				{
					allThingCategoryNode.catDef.childThingDefs.RemoveAt(num3);
				}
			}
		}
		if (isDebug)
		{
			list2 = (from x in list2
				orderby x[1], x[0]
				select x).ToList();
			list2.Insert(0, new string[7] { "DefName", "RimWorldCategory", "DefaultStackBase", "AlteredBase", "OgreStackCategory(FixedBase)", "FinalStackLimit", "Support" });
			try
			{
				DataUtil.WriteFisherPriceCSV(list2, "OgreStack_DefsList.csv");
				Log.Message("[OgreStack]: Write Defs CSV => [" + DataUtil.GenerateFilePath("OgreStack_DefsList.csv").Replace("/", "\\") + "]");
			}
			catch (IOException ex)
			{
				if (Regex.IsMatch(ex.Message, "sharing violation", RegexOptions.IgnoreCase))
				{
					Log.Warning("[OgreStack]: Cannot Write 'OgreStack_DefsList.csv'. Make sure you don't have the file open so OgreStack can overwrite it.");
					Log.Warning(ex.Message);
				}
			}
			list2.Clear();
			list2 = null;
		}
		Log.Message("[OgreStack]: Modify Stack Sizes Complete");
	}
}
