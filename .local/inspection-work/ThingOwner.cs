using System;
using System.Collections;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;

namespace Verse;

public abstract class ThingOwner : IExposable, IList<Thing>, ICollection<Thing>, IEnumerable<Thing>, IEnumerable
{
	protected IThingHolder owner;

	protected int maxStacks = 999999;

	public LookMode contentsLookMode = LookMode.Deep;

	public bool removeContentsIfDestroyed = true;

	public bool dontTickContents;

	private const int InfMaxStacks = 999999;

	public IThingHolder Owner => owner;

	public abstract int Count { get; }

	public Thing this[int index] => GetAt(index);

	public bool Any => Count > 0;

	public int TotalStackCount
	{
		get
		{
			int num = 0;
			int count = Count;
			for (int i = 0; i < count; i++)
			{
				num += GetAt(i).stackCount;
			}
			return num;
		}
	}

	public string ContentsString
	{
		get
		{
			if (Any)
			{
				return GenThing.ThingsToCommaList(this);
			}
			return "NothingLower".Translate();
		}
	}

	Thing IList<Thing>.this[int index]
	{
		get
		{
			return GetAt(index);
		}
		set
		{
			throw new InvalidOperationException("ThingOwner doesn't allow setting individual elements.");
		}
	}

	bool ICollection<Thing>.IsReadOnly => true;

	public event Action OnContentsChanged;

	public ThingOwner()
	{
	}

	public ThingOwner(IThingHolder owner)
	{
		this.owner = owner;
	}

	public ThingOwner(IThingHolder owner, LookMode contentsLookMode = LookMode.Deep, bool removeContentsIfDestroyed = true)
	{
		this.owner = owner;
		this.contentsLookMode = contentsLookMode;
		this.removeContentsIfDestroyed = removeContentsIfDestroyed;
	}

	public ThingOwner(IThingHolder owner, bool oneStackOnly, LookMode contentsLookMode = LookMode.Deep, bool removeContentsIfDestroyed = true)
		: this(owner)
	{
		maxStacks = (oneStackOnly ? 1 : 999999);
		this.contentsLookMode = contentsLookMode;
		this.removeContentsIfDestroyed = removeContentsIfDestroyed;
	}

	public virtual void ExposeData()
	{
		Scribe_Values.Look(ref maxStacks, "maxStacks", 999999);
		Scribe_Values.Look(ref contentsLookMode, "contentsLookMode", LookMode.Deep);
		Scribe_Values.Look(ref removeContentsIfDestroyed, "removeContentsIfDestroyed", defaultValue: true);
		Scribe_Values.Look(ref dontTickContents, "dontTickContents", defaultValue: false);
	}

	public void DoTick()
	{
		if (dontTickContents)
		{
			return;
		}
		for (int num = Count - 1; num >= 0; num--)
		{
			Thing at = GetAt(num);
			at.DoTick();
			if (at.Destroyed && removeContentsIfDestroyed)
			{
				Remove(at);
			}
		}
	}

	public void Clear()
	{
		for (int num = Count - 1; num >= 0; num--)
		{
			Remove(GetAt(num));
		}
	}

	public void ClearAndDestroyContents(DestroyMode mode = DestroyMode.Vanish)
	{
		while (Any)
		{
			for (int num = Count - 1; num >= 0; num--)
			{
				Thing at = GetAt(num);
				at.Destroy(mode);
				Remove(at);
			}
		}
	}

	public void ClearAndDestroyContentsOrPassToWorld(DestroyMode mode = DestroyMode.Vanish)
	{
		while (Any)
		{
			for (int num = Count - 1; num >= 0; num--)
			{
				Thing at = GetAt(num);
				at.DestroyOrPassToWorld(mode);
				Remove(at);
			}
		}
	}

	public bool CanAcceptAnyOf(Thing item, bool canMergeWithExistingStacks = true)
	{
		return GetCountCanAccept(item, canMergeWithExistingStacks) > 0;
	}

	public virtual int GetCountCanAccept(Thing item, bool canMergeWithExistingStacks = true)
	{
		if (item == null || item.stackCount <= 0)
		{
			return 0;
		}
		if (maxStacks == 999999)
		{
			return item.stackCount;
		}
		int num = 0;
		if (Count < maxStacks)
		{
			num += (maxStacks - Count) * item.def.stackLimit;
		}
		if (num >= item.stackCount)
		{
			return Mathf.Min(num, item.stackCount);
		}
		if (canMergeWithExistingStacks)
		{
			int i = 0;
			for (int count = Count; i < count; i++)
			{
				Thing at = GetAt(i);
				if (at.stackCount < at.def.stackLimit && at.CanStackWith(item))
				{
					num += at.def.stackLimit - at.stackCount;
					if (num >= item.stackCount)
					{
						return Mathf.Min(num, item.stackCount);
					}
				}
			}
		}
		return Mathf.Min(num, item.stackCount);
	}

	public abstract int TryAdd(Thing item, int count, bool canMergeWithExistingStacks = true);

	public abstract bool TryAdd(Thing item, bool canMergeWithExistingStacks = true);

	public abstract int IndexOf(Thing item);

	public abstract bool Remove(Thing item);

	protected abstract Thing GetAt(int index);

	public bool Contains(Thing item)
	{
		if (item == null)
		{
			return false;
		}
		return item.holdingOwner == this;
	}

	public void RemoveAt(int index)
	{
		if (index < 0 || index >= Count)
		{
			throw new ArgumentOutOfRangeException("index");
		}
		Remove(GetAt(index));
	}

	public int TryAddOrTransfer(Thing item, int count, bool canMergeWithExistingStacks = true)
	{
		if (item == null)
		{
			Log.Warning("Tried to add or transfer null item to ThingOwner.");
			return 0;
		}
		if (item.holdingOwner != null)
		{
			return item.holdingOwner.TryTransferToContainer(item, this, count, canMergeWithExistingStacks);
		}
		return TryAdd(item, count, canMergeWithExistingStacks);
	}

	public bool TryAddOrTransfer(Thing item, bool canMergeWithExistingStacks = true)
	{
		if (item == null)
		{
			Log.Warning("Tried to add or transfer null item to ThingOwner.");
			return false;
		}
		if (item.holdingOwner != null)
		{
			return item.holdingOwner.TryTransferToContainer(item, this, canMergeWithExistingStacks);
		}
		return TryAdd(item, canMergeWithExistingStacks);
	}

	public void TryAddRangeOrTransfer(IEnumerable<Thing> things, bool canMergeWithExistingStacks = true, bool destroyLeftover = false)
	{
		if (things == this)
		{
			return;
		}
		if (things is ThingOwner thingOwner)
		{
			thingOwner.TryTransferAllToContainer(this, canMergeWithExistingStacks);
			if (destroyLeftover)
			{
				thingOwner.ClearAndDestroyContents();
			}
			return;
		}
		if (things is IList<Thing> list)
		{
			for (int i = 0; i < list.Count; i++)
			{
				if (!TryAddOrTransfer(list[i], canMergeWithExistingStacks) && destroyLeftover)
				{
					list[i].Destroy();
				}
			}
			return;
		}
		foreach (Thing thing in things)
		{
			if (!TryAddOrTransfer(thing, canMergeWithExistingStacks) && destroyLeftover)
			{
				thing.Destroy();
			}
		}
	}

	public int RemoveAll(Predicate<Thing> predicate)
	{
		int num = 0;
		for (int num2 = Count - 1; num2 >= 0; num2--)
		{
			if (predicate(GetAt(num2)))
			{
				Remove(GetAt(num2));
				num++;
			}
		}
		return num;
	}

	public bool TryTransferToContainer(Thing item, ThingOwner otherContainer, bool canMergeWithExistingStacks = true)
	{
		return TryTransferToContainer(item, otherContainer, item.stackCount, canMergeWithExistingStacks) == item.stackCount;
	}

	public int TryTransferToContainer(Thing item, ThingOwner otherContainer, int count, bool canMergeWithExistingStacks = true)
	{
		Thing resultingTransferredItem;
		return TryTransferToContainer(item, otherContainer, count, out resultingTransferredItem, canMergeWithExistingStacks);
	}

	public int TryTransferToContainer(Thing item, ThingOwner otherContainer, int count, out Thing resultingTransferredItem, bool canMergeWithExistingStacks = true)
	{
		if (!Contains(item))
		{
			Log.Error("Can't transfer item " + item?.ToString() + " because it's not here. owner=" + owner.ToStringSafe());
			resultingTransferredItem = null;
			return 0;
		}
		if (otherContainer == this && count > 0)
		{
			resultingTransferredItem = item;
			return item.stackCount;
		}
		if (!otherContainer.CanAcceptAnyOf(item, canMergeWithExistingStacks))
		{
			resultingTransferredItem = null;
			return 0;
		}
		if (count <= 0)
		{
			resultingTransferredItem = null;
			return 0;
		}
		if (owner is Map || otherContainer.owner is Map)
		{
			Log.Warning("Can't transfer items to or from Maps directly. They must be spawned or despawned manually. Use TryAdd(item.SplitOff(count))");
			resultingTransferredItem = null;
			return 0;
		}
		int num = Mathf.Min(item.stackCount, count);
		Thing thing = item.SplitOff(num);
		if (Contains(thing))
		{
			Remove(thing);
		}
		if (otherContainer.TryAdd(thing, canMergeWithExistingStacks))
		{
			resultingTransferredItem = thing;
			item.MapHeld?.resourceCounter?.CheckUpdateResource(thing);
			return thing.stackCount;
		}
		resultingTransferredItem = null;
		if (!otherContainer.Contains(thing) && thing.stackCount > 0 && !thing.Destroyed)
		{
			int result = num - thing.stackCount;
			if (item != thing)
			{
				item.TryAbsorbStack(thing, respectStackLimit: false);
			}
			else
			{
				TryAdd(thing, canMergeWithExistingStacks: false);
			}
			Map mapHeld = item.MapHeld;
			if (mapHeld != null)
			{
				ResourceCounter resourceCounter = mapHeld.resourceCounter;
				if (resourceCounter != null)
				{
					resourceCounter.CheckUpdateResource(thing);
					return result;
				}
				return result;
			}
			return result;
		}
		return thing.stackCount;
	}

	public void TryTransferAllToContainer(ThingOwner other, bool canMergeWithExistingStacks = true)
	{
		for (int num = Count - 1; num >= 0; num--)
		{
			TryTransferToContainer(GetAt(num), other, canMergeWithExistingStacks);
		}
	}

	public Thing Take(Thing thing, int count)
	{
		if (!Contains(thing))
		{
			Log.Error("Tried to take " + thing.ToStringSafe() + " but it's not here.");
			return null;
		}
		if (count > thing.stackCount)
		{
			Log.Error("Tried to get " + count + " of " + thing.ToStringSafe() + " while only having " + thing.stackCount);
			count = thing.stackCount;
		}
		if (count == thing.stackCount)
		{
			Remove(thing);
			return thing;
		}
		Thing thing2 = thing.SplitOff(count);
		thing2.holdingOwner = null;
		return thing2;
	}

	public Thing Take(Thing thing)
	{
		return Take(thing, thing.stackCount);
	}

	public bool TryDrop(Thing thing, ThingPlaceMode mode, int count, out Thing lastResultingThing, Action<Thing, int> placedAction = null, Predicate<IntVec3> nearPlaceValidator = null)
	{
		Map rootMap = ThingOwnerUtility.GetRootMap(owner);
		IntVec3 rootPosition = ThingOwnerUtility.GetRootPosition(owner);
		if (rootMap == null || !rootPosition.IsValid)
		{
			Log.Error("Cannot drop " + thing?.ToString() + " without a dropLoc and with an owner whose map is null.");
			lastResultingThing = null;
			return false;
		}
		return TryDrop(thing, rootPosition, rootMap, mode, count, out lastResultingThing, placedAction, nearPlaceValidator);
	}

	public bool TryDrop(Thing thing, IntVec3 dropLoc, Map map, ThingPlaceMode mode, int count, out Thing resultingThing, Action<Thing, int> placedAction = null, Predicate<IntVec3> nearPlaceValidator = null)
	{
		if (!Contains(thing))
		{
			Log.Error("Tried to drop " + thing.ToStringSafe() + " but it's not here.");
			resultingThing = null;
			return false;
		}
		if (thing.stackCount < count)
		{
			Log.Error("Tried to drop " + count + " of " + thing?.ToString() + " while only having " + thing.stackCount);
			count = thing.stackCount;
		}
		if (count == thing.stackCount)
		{
			if (GenDrop.TryDropSpawn(thing, dropLoc, map, mode, out resultingThing, placedAction, nearPlaceValidator))
			{
				Remove(thing);
				return true;
			}
			return false;
		}
		Thing thing2 = thing.SplitOff(count);
		if (GenDrop.TryDropSpawn(thing2, dropLoc, map, mode, out resultingThing, placedAction, nearPlaceValidator))
		{
			return true;
		}
		thing.TryAbsorbStack(thing2, respectStackLimit: false);
		return false;
	}

	public bool TryDrop(Thing thing, ThingPlaceMode mode, out Thing lastResultingThing, Action<Thing, int> placedAction = null, Predicate<IntVec3> nearPlaceValidator = null)
	{
		Map rootMap = ThingOwnerUtility.GetRootMap(owner);
		IntVec3 rootPosition = ThingOwnerUtility.GetRootPosition(owner);
		if (rootMap == null || !rootPosition.IsValid)
		{
			Log.Error("Cannot drop " + thing?.ToString() + " without a dropLoc and with an owner whose map is null.");
			lastResultingThing = null;
			return false;
		}
		return TryDrop(thing, rootPosition, rootMap, mode, out lastResultingThing, placedAction, nearPlaceValidator);
	}

	public bool TryDrop(Thing thing, IntVec3 dropLoc, Map map, ThingPlaceMode mode, out Thing lastResultingThing, Action<Thing, int> placedAction = null, Predicate<IntVec3> nearPlaceValidator = null, bool playDropSound = true)
	{
		if (!Contains(thing))
		{
			Log.Error(owner.ToStringSafe() + " container tried to drop  " + thing.ToStringSafe() + " which it didn't contain.");
			lastResultingThing = null;
			return false;
		}
		if (GenDrop.TryDropSpawn(thing, dropLoc, map, mode, out lastResultingThing, placedAction, nearPlaceValidator, playDropSound))
		{
			Remove(thing);
			return true;
		}
		return false;
	}

	public bool TryDropAll(IntVec3 dropLoc, Map map, ThingPlaceMode mode, Action<Thing, int> placeAction = null, Predicate<IntVec3> nearPlaceValidator = null, bool playDropSound = true)
	{
		bool result = true;
		for (int num = Count - 1; num >= 0; num--)
		{
			if (!TryDrop(GetAt(num), dropLoc, map, mode, out var _, placeAction, nearPlaceValidator, playDropSound))
			{
				result = false;
			}
		}
		return result;
	}

	public bool Contains(ThingDef def)
	{
		return Contains(def, 1);
	}

	public bool Contains(ThingDef def, int minCount)
	{
		if (minCount <= 0)
		{
			return true;
		}
		int num = 0;
		int count = Count;
		for (int i = 0; i < count; i++)
		{
			if (GetAt(i).def == def)
			{
				num += GetAt(i).stackCount;
			}
			if (num >= minCount)
			{
				return true;
			}
		}
		return false;
	}

	public int TotalStackCountOfDef(ThingDef def)
	{
		int num = 0;
		int count = Count;
		for (int i = 0; i < count; i++)
		{
			if (GetAt(i).def == def)
			{
				num += GetAt(i).stackCount;
			}
		}
		return num;
	}

	public void Notify_ContainedItemDestroyed(Thing t)
	{
		if (ThingOwnerUtility.ShouldAutoRemoveDestroyedThings(owner))
		{
			Remove(t);
		}
	}

	protected virtual void NotifyAdded(Thing item)
	{
		if (ThingOwnerUtility.ShouldAutoExtinguishInnerThings(owner) && item.HasAttachment(ThingDefOf.Fire))
		{
			item.GetAttachment(ThingDefOf.Fire).Destroy();
		}
		if (ThingOwnerUtility.ShouldRemoveDesignationsOnAddedThings(owner))
		{
			List<Map> maps = Find.Maps;
			for (int i = 0; i < maps.Count; i++)
			{
				maps[i].designationManager.RemoveAllDesignationsOn(item);
			}
		}
		if ((owner is Thing thing && thing.Faction.IsPlayerSafe()) || (owner is WorldObject worldObject && worldObject.Faction.IsPlayerSafe()) || (owner is Pawn_InventoryTracker pawn_InventoryTracker && pawn_InventoryTracker.pawn.Faction.IsPlayerSafe()))
		{
			item.EverSeenByPlayer = true;
		}
		if (owner is CompTransporter compTransporter)
		{
			compTransporter.Notify_ThingAdded(item);
		}
		if (owner is Caravan caravan)
		{
			caravan.Notify_PawnAdded((Pawn)item);
		}
		if (owner is Pawn_ApparelTracker pawn_ApparelTracker)
		{
			pawn_ApparelTracker.Notify_ApparelAdded((Apparel)item);
			if (pawn_ApparelTracker.pawn.Faction.IsPlayerSafe())
			{
				item.EverSeenByPlayer = true;
			}
		}
		if (owner is Pawn_EquipmentTracker pawn_EquipmentTracker)
		{
			pawn_EquipmentTracker.Notify_EquipmentAdded((ThingWithComps)item);
			if (pawn_EquipmentTracker.pawn.Faction.IsPlayerSafe())
			{
				item.EverSeenByPlayer = true;
			}
		}
		NotifyColonistBarIfColonistCorpse(item);
		this.OnContentsChanged?.Invoke();
	}

	protected void NotifyAddedAndMergedWith(Thing item, int mergedCount)
	{
		if (owner is CompTransporter compTransporter)
		{
			compTransporter.Notify_ThingAddedAndMergedWith(item, mergedCount);
		}
	}

	protected virtual void NotifyRemoved(Thing item)
	{
		if (owner is Pawn_InventoryTracker pawn_InventoryTracker)
		{
			pawn_InventoryTracker.Notify_ItemRemoved(item);
		}
		if (owner is Pawn_ApparelTracker pawn_ApparelTracker)
		{
			pawn_ApparelTracker.Notify_ApparelRemoved((Apparel)item);
		}
		if (owner is Pawn_EquipmentTracker pawn_EquipmentTracker)
		{
			pawn_EquipmentTracker.Notify_EquipmentRemoved((ThingWithComps)item);
		}
		if (owner is Caravan caravan)
		{
			caravan.Notify_PawnRemoved((Pawn)item);
		}
		NotifyColonistBarIfColonistCorpse(item);
		this.OnContentsChanged?.Invoke();
	}

	private void NotifyColonistBarIfColonistCorpse(Thing thing)
	{
		if (thing is Corpse { Bugged: false } corpse && corpse.InnerPawn.Faction != null && corpse.InnerPawn.Faction.IsPlayer && Current.ProgramState == ProgramState.Playing)
		{
			Find.ColonistBar.MarkColonistsDirty();
		}
	}

	void IList<Thing>.Insert(int index, Thing item)
	{
		throw new InvalidOperationException("ThingOwner doesn't allow inserting individual elements at any position.");
	}

	void ICollection<Thing>.Add(Thing item)
	{
		TryAdd(item);
	}

	void ICollection<Thing>.CopyTo(Thing[] array, int arrayIndex)
	{
		for (int i = 0; i < Count; i++)
		{
			array[i + arrayIndex] = GetAt(i);
		}
	}

	IEnumerator<Thing> IEnumerable<Thing>.GetEnumerator()
	{
		for (int i = 0; i < Count; i++)
		{
			yield return GetAt(i);
		}
	}

	IEnumerator IEnumerable.GetEnumerator()
	{
		for (int i = 0; i < Count; i++)
		{
			yield return GetAt(i);
		}
	}
}
