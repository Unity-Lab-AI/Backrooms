using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace OgreStack.PersistentData;

public class OgreStackSettings : ModSettings
{
	private bool isLoaded = false;

	private Dictionary<Category, string> _preSettingsWindow = null;

	internal Action ReModify = null;

	internal Vector2 ScrollPosition = new Vector2(0f, 0f);

	public bool IsDebug;

	private Dictionary<Category, CategorySetting> _values = null;

	public Dictionary<Category, CategorySetting> Values
	{
		get
		{
			if (_values == null)
			{
				_values = new Dictionary<Category, CategorySetting>(OgreStackMod._DEFAULTS.Keys.Count);
				foreach (KeyValuePair<Category, CategorySetting> dEFAULT in OgreStackMod._DEFAULTS)
				{
					_values.Add(dEFAULT.Key, new CategorySetting(dEFAULT.Value.Mode, dEFAULT.Value.Value));
				}
			}
			return _values;
		}
	}

	internal void HashCurrentSettings()
	{
		_preSettingsWindow = new Dictionary<Category, string>();
		foreach (KeyValuePair<Category, CategorySetting> value in Values)
		{
			_preSettingsWindow.Add(value.Key, value.Value.ToString());
		}
	}

	public bool DetermineIfModifyStacksIsNeeded()
	{
		if (_preSettingsWindow == null)
		{
			return false;
		}
		foreach (KeyValuePair<Category, CategorySetting> value in Values)
		{
			string strA = _preSettingsWindow[value.Key];
			string strB = value.Value.ToString();
			if (string.Compare(strA, strB, ignoreCase: true) != 0)
			{
				return true;
			}
		}
		return false;
	}

	public override void ExposeData()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Invalid comparison between Unknown and I4
		if ((int)Scribe.mode == 1)
		{
			foreach (KeyValuePair<Category, CategorySetting> value2 in Values)
			{
				Category key = value2.Key;
				CategorySetting value = value2.Value;
				if (OgreStackMod._DEFAULTS[key].Mode != value.Mode || OgreStackMod._DEFAULTS[key].Value != value.Value)
				{
					string text = key.ToString() + "_";
					Scribe_Values.Look<MultiplierMode>(ref value.Mode, text + "Mode", MultiplierMode.Fixed, false);
					Scribe_Values.Look<string>(ref value.Buffer, text + "Value", (string)null, false);
				}
			}
			if (IsDebug)
			{
				Scribe_Values.Look<bool>(ref IsDebug, "IsDebugCSV", false, false);
			}
			if (DetermineIfModifyStacksIsNeeded())
			{
				ReModify();
			}
			HashCurrentSettings();
		}
		else
		{
			if (isLoaded)
			{
				return;
			}
			isLoaded = true;
			foreach (Category key2 in OgreStackMod._DEFAULTS.Keys)
			{
				string text2 = key2.ToString() + "_";
				MultiplierMode mode = MultiplierMode.Fixed;
				string text3 = "0";
				Scribe_Values.Look<MultiplierMode>(ref mode, text2 + "Mode", MultiplierMode.Fixed, false);
				Scribe_Values.Look<string>(ref text3, text2 + "Value", (string)null, false);
				if (!string.IsNullOrEmpty(text3))
				{
					Values[key2] = new CategorySetting(mode, text3);
					Values[key2].ParseBuffer();
				}
				else
				{
					Values[key2] = new CategorySetting(OgreStackMod._DEFAULTS[key2].Mode, OgreStackMod._DEFAULTS[key2].Value.ToString());
				}
			}
			Scribe_Values.Look<bool>(ref IsDebug, "IsDebugCSV", false, false);
			HashCurrentSettings();
		}
	}
}
