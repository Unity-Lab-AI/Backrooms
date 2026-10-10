using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml.Linq;
using OgreStack.PersistentData;

namespace OgreStack;

internal class IndividualOverrides
{
	private XDocument _overrides = null;

	private static Dictionary<string, int> _itemLevelOverrides = null;

	private static HashSet<string> _categoryNoStackOverrides = null;

	private static List<KeyValuePair<string, int>> _itemLevelOverridesOrdered = null;

	private static readonly object _lock = new object();

	internal IndividualOverrides()
	{
		lock (_lock)
		{
			if (_itemLevelOverrides != null && _categoryNoStackOverrides != null)
			{
				return;
			}
			_overrides = DataUtil.GetUserOverrides();
			if (_overrides == null)
			{
				return;
			}
			_itemLevelOverrides = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
			_categoryNoStackOverrides = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
			_itemLevelOverridesOrdered = new List<KeyValuePair<string, int>>();
			XElement xElement = _overrides.Root.Element("IndividualItemOverrides");
			if (xElement != null)
			{
				IEnumerable<XElement> enumerable = xElement.Elements("item");
				if (enumerable != null && enumerable.Any())
				{
					foreach (XElement item in enumerable)
					{
						addItemLevelOverride(item);
					}
				}
			}
			XElement xElement2 = _overrides.Root.Element("BanItemsFromStackingByCategory");
			if (xElement2 == null)
			{
				return;
			}
			IEnumerable<XElement> enumerable2 = xElement2.Elements("category");
			if (enumerable2 == null || !enumerable2.Any())
			{
				return;
			}
			foreach (XElement item2 in enumerable2)
			{
				Dictionary<string, string> attributePairs = getAttributePairs(item2);
				string value = string.Empty;
				if (attributePairs.TryGetValue("name", out value))
				{
					value = value.Trim();
					if (!string.IsNullOrEmpty(value))
					{
						_categoryNoStackOverrides.Add(value);
					}
				}
			}
		}
	}

	private static Dictionary<string, string> getAttributePairs(XElement element)
	{
		Dictionary<string, string> dictionary = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
		if (element.HasAttributes)
		{
			foreach (XAttribute item in element.Attributes())
			{
				dictionary.Add(item.Name.ToString(), item.Value);
			}
		}
		return dictionary;
	}

	private void addItemLevelOverride(XElement def)
	{
		Dictionary<string, string> attributePairs = getAttributePairs(def);
		string value = string.Empty;
		string value2 = string.Empty;
		if (!attributePairs.TryGetValue("defName", out value) && !attributePairs.TryGetValue("name", out value))
		{
			return;
		}
		value = value.Trim();
		if (!attributePairs.TryGetValue("stackLimit", out value2))
		{
			return;
		}
		int result = -1;
		if (!int.TryParse(value2, out result) || result <= 0 || string.IsNullOrEmpty(value))
		{
			return;
		}
		if (_itemLevelOverrides.ContainsKey(value))
		{
			_itemLevelOverrides.Remove(value);
			for (int num = _itemLevelOverridesOrdered.Count - 1; num > -1; num--)
			{
				if (string.Compare(_itemLevelOverridesOrdered[num].Key, value, ignoreCase: true) == 0)
				{
					_itemLevelOverridesOrdered.RemoveAt(num);
				}
			}
		}
		_itemLevelOverrides.Add(value, result);
		_itemLevelOverridesOrdered.Add(new KeyValuePair<string, int>(value, result));
	}

	internal List<KeyValuePair<string, int>> ViewInternalOverrides()
	{
		List<KeyValuePair<string, int>> list = new List<KeyValuePair<string, int>>();
		if (_itemLevelOverridesOrdered != null && _itemLevelOverridesOrdered.Count > 0)
		{
			foreach (KeyValuePair<string, int> item in _itemLevelOverridesOrdered)
			{
				list.Add(new KeyValuePair<string, int>(item.Key, item.Value));
			}
		}
		return list;
	}

	internal int GetItemLevelOverride(string defName)
	{
		int value = 0;
		if (_itemLevelOverrides != null)
		{
			return _itemLevelOverrides.TryGetValue(defName, out value) ? value : 0;
		}
		return value;
	}

	internal bool IsCategoryBanned(string category)
	{
		if (string.IsNullOrEmpty(category))
		{
			return false;
		}
		if (_categoryNoStackOverrides == null)
		{
			return false;
		}
		return Enumerable.Contains(_categoryNoStackOverrides, category);
	}

	internal static string GenerateDefaultOverridesXml()
	{
		return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<OgreStack>\r\n\t<IndividualItemOverrides>\r\n\t\t<!--\r\n\t\t\t* This lets you target items by their DefName.\r\n\t\t\t* Set the stackLimit directly\r\n\t\t\t\r\n\t\t\t* Items adjusted here will ignore any additional\r\n\t\t\t* processing rules in OgreStack\r\n\t\t\t\r\n\t\t\t* FORMAT: <item defName=\"<string:DefName>\" stackLimit=\"<int:desiredStackLimit>\" />\r\n\t\t\t* Example: set the stack limit for unfertilized chicken eggs to 2000\r\n\t\t\t\r\n\t\t\t* <item defName=\"EggChickenUnfertilized\" stackLimit=\"2000\" />\r\n\t\t-->\r\n\r\n\t\t<item defName=\"AIPersonaCore\" stackLimit=\"1\" />\r\n\t\t<item defName=\"TechprofSubpersonaCore\" stackLimit=\"1\" />\r\n\t</IndividualItemOverrides>\r\n\r\n\t<BanItemsFromStackingByCategory>\r\n\t\t<!--\r\n\t\t * Lets you ban items that identifies itself\r\n\t\t * in a category named in this section\r\n\t\t \r\n\t\t * Items adjusted here will ignore additional\r\n\t\t * processing rules in OgreStack\r\n\t\t \r\n\t\t * FORMAT: <category name=\"<string:Category>\" />\r\n\t\t * Example: Ban stacking for any egg that is fertilized \r\n\t\t * that categorizes itself 'EggsFertilized'\r\n\t\t \r\n\t\t * <category name=\"EggsFertilized\" />\r\n\t\t-->\r\n\t</BanItemsFromStackingByCategory>\r\n</OgreStack>";
	}
}
