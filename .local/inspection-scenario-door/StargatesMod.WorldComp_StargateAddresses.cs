using System.Collections.Generic;
using RimWorld.Planet;
using Verse;

namespace StargatesMod;

public class WorldComp_StargateAddresses : WorldComponent
{
	public List<PlanetTile> AddressList = new List<PlanetTile>();

	public List<int> PocketMapAddressList = new List<int>();

	public WorldComp_StargateAddresses(World world)
		: base(world)
	{
	}

	public void AddAddress(PlanetTile address)
	{
		if (AddressList == null)
		{
			AddressList = new List<PlanetTile>();
		}
		if (address.Valid && !AddressList.Contains(address))
		{
			AddressList.Add(address);
		}
	}

	public void RemoveAddress(PlanetTile address)
	{
		if (address.Valid)
		{
			AddressList.Remove(address);
		}
	}

	public void AddPocketMapAddress(int mapIndex)
	{
		if (PocketMapAddressList == null)
		{
			PocketMapAddressList = new List<int>();
		}
		if (mapIndex >= 0 && !PocketMapAddressList.Contains(mapIndex))
		{
			PocketMapAddressList.Add(mapIndex);
		}
	}

	public void RemovePocketMapAddress(int mapIndex)
	{
		if (mapIndex >= 0)
		{
			PocketMapAddressList.Remove(mapIndex);
		}
	}

	public void CleanupAddresses()
	{
		if (!AddressList.NullOrEmpty())
		{
			foreach (PlanetTile item in new List<PlanetTile>(AddressList))
			{
				MapParent mapParent = Find.WorldObjects.MapParentAt(item);
				Site site = mapParent as Site;
				if (mapParent == null || (!mapParent.HasMap && (site == null || !site.MainSitePartDef.tags.Contains("StargateMod_StargateSite")) && !(mapParent is WorldObject_PermSgSite)))
				{
					RemoveAddress(item);
				}
			}
		}
		if (PocketMapAddressList.NullOrEmpty())
		{
			return;
		}
		foreach (int item2 in new List<int>(PocketMapAddressList))
		{
			PocketMapParent pocketMapParent = Find.Maps[item2].PocketMapParent;
			if (pocketMapParent == null || !pocketMapParent.HasMap)
			{
				RemovePocketMapAddress(item2);
			}
		}
	}

	public bool EnoughAddressesToDial()
	{
		int num = 0;
		if (!AddressList.NullOrEmpty())
		{
			num += AddressList.Count;
		}
		if (!PocketMapAddressList.NullOrEmpty())
		{
			num += PocketMapAddressList.Count;
		}
		return num >= 2;
	}

	public bool IsRegistered(PlanetTile address)
	{
		if (!address.Valid)
		{
			return false;
		}
		if (!AddressList.NullOrEmpty() && AddressList.Contains(address))
		{
			return true;
		}
		if (!PocketMapAddressList.NullOrEmpty())
		{
			return PocketMapAddressList.Contains(address.tileId);
		}
		return false;
	}

	public override void ExposeData()
	{
		base.ExposeData();
		Scribe_Collections.Look(ref AddressList, "AddressList", LookMode.Undefined);
		Scribe_Collections.Look(ref PocketMapAddressList, "PocketMapAddressList", LookMode.Undefined);
	}
}
