using System;
using System.Collections;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;

namespace Verse;

public class ThingOwner<T> : ThingOwner, IList<T>, ICollection<T>, IEnumerable<T>, IEnumerable where T : Thing
{
	private List<T> innerList = new List<T>();

	public List<T> InnerListForReading => innerList;

	public new T this[int index] => innerList[index];

	public override int Count => innerList.Count;

	T IList<T>.this[int index]
	{
		get
		{
			return innerList[index];
		}
		set
		{
			throw new InvalidOperationException("ThingOwner doesn't allow setting individual elements.");
		}
	}

	bool ICollection<T>.IsReadOnly => true;

	public ThingOwner()
	{
	}

	public ThingOwner(IThingHolder owner)
		: base(owner)
	{
	}

	public ThingOwner(IThingHolder owner, LookMode contentsLookMode = LookMode.Deep, bool removeContentsIfDestroyed = true)
		: base(owner)
	{
	}

	public ThingOwner(IThingHolder owner, bool oneStackOnly, LookMode contentsLookMode = LookMode.Deep, bool removeContentsIfDestroyed = true)
		: base(owner, oneStackOnly, contentsLookMode, removeContentsIfDestroyed)
	{
	}

	public override void ExposeData()
	{
		base.ExposeData();
		Scribe_Collections.Look(ref innerList, "innerList", true, contentsLookMode);
		if (Scribe.mode == LoadSaveMode.PostLoadInit)
		{
			int num = innerList.RemoveAll((T x) => x == null || (x is MinifiedThing minifiedThing && minifiedThing.InnerThing == null));
			if (num > 0)
			{
				Log.Warning($"ThingOwner removed {num} invalid entries during PostLoadInit.");
			}
		}
		if (Scribe.mode != LoadSaveMode.LoadingVars && Scribe.mode != LoadSaveMode.PostLoadInit)
		{
			return;
		}
		for (int num2 = 0; num2 < innerList.Count; num2++)
		{
			if (innerList[num2] != null)
			{
				innerList[num2].holdingOwner = this;
			}
		}
	}

	public List<T>.Enumerator GetEnumerator()
	{
		return innerList.GetEnumerator();
	}

	public override int GetCountCanAccept(Thing item, bool canMergeWithExistingStacks = true)
	{
		if (!(item is T))
		{
			return 0;
		}
		return base.GetCountCanAccept(item, canMergeWithExistingStacks);
	}

	public override int TryAdd(Thing item, int count, bool canMergeWithExistingStacks = true)
	{
		if (count <= 0)
		{
			return 0;
		}
		if (item == null)
		{
			Log.Warning("Tried to add null item to ThingOwner.");
			return 0;
		}
		if (Contains(item))
		{
			Log.Warning("Tried to add " + item?.ToString() + " to ThingOwner but this item is already here.");
			return 0;
		}
		if (item.holdingOwner != null)
		{
			Log.Warning("Tried to add " + count + " of " + item.ToStringSafe() + " to ThingOwner but this thing is already in another container. owner=" + owner.ToStringSafe() + ", current container owner=" + item.holdingOwner.Owner.ToStringSafe() + ". Use TryAddOrTransfer, TryTransferToContainer, or remove the item before adding it.");
			return 0;
		}
		if (!CanAcceptAnyOf(item, canMergeWithExistingStacks))
		{
			return 0;
		}
		int stackCount = item.stackCount;
		int num = Mathf.Min(stackCount, count);
		Thing thing = item.SplitOff(num);
		if (!TryAdd((T)thing, canMergeWithExistingStacks))
		{
			if (thing != item)
			{
				int result = stackCount - item.stackCount - thing.stackCount;
				item.TryAbsorbStack(thing, respectStackLimit: false);
				return result;
			}
			return stackCount - item.stackCount;
		}
		CompPushable compPushable = item.TryGetComp<CompPushable>();
		if (compPushable != null && owner is Pawn pawn)
		{
			compPushable.OnStartedCarrying(pawn);
		}
		return num;
	}

	public override bool TryAdd(Thing item, bool canMergeWithExistingStacks = true)
	{
		if (item == null)
		{
			Log.Warning("Tried to add null item to ThingOwner.");
			return false;
		}
		if (!(item is T item2))
		{
			return false;
		}
		if (Contains(item))
		{
			Log.Warning("Tried to add " + item.ToStringSafe() + " to ThingOwner but this item is already here.");
			return false;
		}
		if (item.holdingOwner != null)
		{
			Log.Warning("Tried to add " + item.ToStringSafe() + " to ThingOwner but this thing is already in another container. owner=" + owner.ToStringSafe() + ", current container owner=" + item.holdingOwner.Owner.ToStringSafe() + ". Use TryAddOrTransfer, TryTransferToContainer, or remove the item before adding it.");
			return false;
		}
		if (!CanAcceptAnyOf(item, canMergeWithExistingStacks))
		{
			return false;
		}
		if (canMergeWithExistingStacks)
		{
			for (int i = 0; i < innerList.Count; i++)
			{
				T val = innerList[i];
				if (!val.CanStackWith(item))
				{
					continue;
				}
				int num = Mathf.Min(item.stackCount, val.def.stackLimit - val.stackCount);
				if (num > 0)
				{
					Thing other = item.SplitOff(num);
					int stackCount = val.stackCount;
					val.TryAbsorbStack(other, respectStackLimit: true);
					if (val.stackCount > stackCount)
					{
						NotifyAddedAndMergedWith(val, val.stackCount - stackCount);
					}
					if (item.Destroyed || item.stackCount == 0)
					{
						return true;
					}
				}
			}
		}
		if (Count >= maxStacks)
		{
			return false;
		}
		item.holdingOwner = this;
		innerList.Add(item2);
		NotifyAdded(item2);
		return true;
	}

	protected override void NotifyAdded(Thing item)
	{
		if (owner is IThingHolderEvents<T> thingHolderEvents)
		{
			thingHolderEvents.Notify_ItemAdded(item as T);
		}
		base.NotifyAdded(item);
	}

	protected override void NotifyRemoved(Thing item)
	{
		if (owner is IThingHolderEvents<T> thingHolderEvents)
		{
			thingHolderEvents.Notify_ItemRemoved(item as T);
		}
		base.NotifyRemoved(item);
	}

	public void TryAddRangeOrTransfer(IEnumerable<T> things, bool canMergeWithExistingStacks = true, bool destroyLeftover = false)
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
		if (things is IList<T> list)
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
		foreach (T thing in things)
		{
			if (!TryAddOrTransfer(thing, canMergeWithExistingStacks) && destroyLeftover)
			{
				thing.Destroy();
			}
		}
	}

	public override int IndexOf(Thing item)
	{
		if (!(item is T item2))
		{
			return -1;
		}
		return innerList.IndexOf(item2);
	}

	public override bool Remove(Thing item)
	{
		if (!Contains(item))
		{
			return false;
		}
		if (item.holdingOwner == this)
		{
			item.holdingOwner = null;
		}
		int index = innerList.LastIndexOf((T)item);
		innerList.RemoveAt(index);
		NotifyRemoved(item);
		return true;
	}

	public int RemoveAll(Predicate<T> predicate)
	{
		int num = 0;
		for (int num2 = innerList.Count - 1; num2 >= 0; num2--)
		{
			if (predicate(innerList[num2]))
			{
				Remove(innerList[num2]);
				num++;
			}
		}
		return num;
	}

	protected override Thing GetAt(int index)
	{
		return innerList[index];
	}

	public void GetThingsOfType<J>(List<J> list) where J : Thing
	{
		for (int i = 0; i < innerList.Count; i++)
		{
			if (innerList[i] is J item)
			{
				list.Add(item);
			}
		}
	}

	public int TryTransferToContainer(Thing item, ThingOwner otherContainer, int stackCount, out T resultingTransferredItem, bool canMergeWithExistingStacks = true)
	{
		Thing resultingTransferredItem2;
		int result = TryTransferToContainer(item, otherContainer, stackCount, out resultingTransferredItem2, canMergeWithExistingStacks);
		resultingTransferredItem = (T)resultingTransferredItem2;
		return result;
	}

	public new T Take(Thing thing, int count)
	{
		return (T)base.Take(thing, count);
	}

	public new T Take(Thing thing)
	{
		return (T)base.Take(thing);
	}

	public bool TryDrop(Thing thing, IntVec3 dropLoc, Map map, ThingPlaceMode mode, int count, out T resultingThing, Action<T, int> placedAction = null, Predicate<IntVec3> nearPlaceValidator = null)
	{
		Action<Thing, int> placedAction2 = null;
		if (placedAction != null)
		{
			placedAction2 = delegate(Thing t, int c)
			{
				placedAction((T)t, c);
			};
		}
		Thing resultingThing2;
		bool result = TryDrop(thing, dropLoc, map, mode, count, out resultingThing2, placedAction2, nearPlaceValidator);
		resultingThing = (T)resultingThing2;
		return result;
	}

	public bool TryDrop(Thing thing, ThingPlaceMode mode, out T lastResultingThing, Action<T, int> placedAction = null, Predicate<IntVec3> nearPlaceValidator = null)
	{
		Action<Thing, int> placedAction2 = null;
		if (placedAction != null)
		{
			placedAction2 = delegate(Thing t, int c)
			{
				placedAction((T)t, c);
			};
		}
		Thing lastResultingThing2;
		bool result = TryDrop(thing, mode, out lastResultingThing2, placedAction2, nearPlaceValidator);
		lastResultingThing = (T)lastResultingThing2;
		return result;
	}

	public bool TryDrop(Thing thing, IntVec3 dropLoc, Map map, ThingPlaceMode mode, out T lastResultingThing, Action<T, int> placedAction = null, Predicate<IntVec3> nearPlaceValidator = null)
	{
		Action<Thing, int> placedAction2 = null;
		if (placedAction != null)
		{
			placedAction2 = delegate(Thing t, int c)
			{
				placedAction((T)t, c);
			};
		}
		Thing lastResultingThing2;
		bool result = TryDrop(thing, dropLoc, map, mode, out lastResultingThing2, placedAction2, nearPlaceValidator, playDropSound: true);
		lastResultingThing = (T)lastResultingThing2;
		return result;
	}

	int IList<T>.IndexOf(T item)
	{
		return innerList.IndexOf(item);
	}

	void IList<T>.Insert(int index, T item)
	{
		throw new InvalidOperationException("ThingOwner doesn't allow inserting individual elements at any position.");
	}

	void ICollection<T>.Add(T item)
	{
		TryAdd(item);
	}

	void ICollection<T>.CopyTo(T[] array, int arrayIndex)
	{
		innerList.CopyTo(array, arrayIndex);
	}

	bool ICollection<T>.Contains(T item)
	{
		return innerList.Contains(item);
	}

	bool ICollection<T>.Remove(T item)
	{
		return Remove(item);
	}

	IEnumerator<T> IEnumerable<T>.GetEnumerator()
	{
		return innerList.GetEnumerator();
	}

	IEnumerator IEnumerable.GetEnumerator()
	{
		return innerList.GetEnumerator();
	}
}
