using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace StargatesMod;

public class CompStargate : ThingComp
{
	private List<BufferItem> _sendBuffer = new List<BufferItem>();

	private List<BufferItem> _recvBuffer = new List<BufferItem>();

	private int _ticksSinceBufferUnloaded;

	private int _ticksSinceOpened;

	public int TicksUntilOpen = -1;

	private DialMode _dialMode;

	public PlanetTile GateAddress;

	private string _gateDesignation;

	public bool IsInPocketMap;

	public bool StargateIsActive;

	public bool IsReceivingGate;

	public bool IsHibernating;

	public bool HasIris;

	public bool IrisIsActivated;

	private int _prevRingSoundQueue;

	private int _chevronSoundCounter;

	private PlanetTile _queuedAddress = -1;

	private PlanetTile _connectedAddress = -1;

	private Thing _connectedStargate;

	private CompStargate _connectedStargateComp;

	private CompTransporter _transComp;

	private Thing _conflictingGate;

	private int _checkVortexPawnsTick = 120;

	private const int _checkVortexPawnsDelayTick = 10;

	private List<Pawn> _pawnsWatchingStargate;

	private Sustainer _puddleSustainer;

	private readonly StargatesModSettings _modSettings = LoadedModManager.GetMod<StargatesMod>().GetSettings<StargatesModSettings>();

	[CompilerGenerated]
	private WorldComp_StargateAddresses <AddressComp>k__BackingField;

	[CompilerGenerated]
	private Graphic <StargatePuddle>k__BackingField;

	[CompilerGenerated]
	private Graphic <StargateIris>k__BackingField;

	public bool IsExpectingIncomingWormhole
	{
		get
		{
			if (!StargateIsActive && _connectedStargate != null && _connectedStargateComp != null)
			{
				return IsReceivingGate;
			}
			return false;
		}
	}

	private WorldComp_StargateAddresses AddressComp => <AddressComp>k__BackingField ?? (<AddressComp>k__BackingField = Find.World.GetComponent<WorldComp_StargateAddresses>());

	private string GateDesignation
	{
		get
		{
			PlanetTile gateAddress = GateAddress;
			if (!gateAddress.Valid || !AddressComp.IsRegistered(GateAddress))
			{
				return "INVALID - please reinstall stargate";
			}
			return _gateDesignation;
		}
		set
		{
			_gateDesignation = value;
		}
	}

	private bool GateIsLoadingTransporter
	{
		get
		{
			CompTransporter transComp = _transComp;
			if (transComp != null && transComp.LoadingInProgressOrReadyToLaunch)
			{
				return transComp.AnyInGroupHasAnythingLeftToLoad;
			}
			return false;
		}
	}

	public IEnumerable<IntVec3> VortexCells => Props.vortexPattern.Select((IntVec3 offset) => parent.Position + offset.RotatedBy(parent.Rotation));

	public CompProperties_Stargate Props => (CompProperties_Stargate)props;

	private Graphic StargatePuddle => <StargatePuddle>k__BackingField ?? (<StargatePuddle>k__BackingField = GraphicDatabase.Get<Graphic_Single>(Props.puddleTexture, ShaderDatabase.Mote, Props.puddleDrawSize, Color.white));

	private Graphic StargateIris => <StargateIris>k__BackingField ?? (<StargateIris>k__BackingField = GraphicDatabase.Get<Graphic_Single>(Props.irisTexture, ShaderDatabase.Mote, Props.puddleDrawSize, Color.white));

	public void OpenStargateDelayed(PlanetTile address, int delay, DialMode dialMode)
	{
		_queuedAddress = address;
		_dialMode = dialMode;
		TicksUntilOpen = delay;
		_checkVortexPawnsTick = 120;
		if ((int)address <= -1)
		{
			return;
		}
		Map map = _dialMode switch
		{
			DialMode.Map => Find.WorldObjects.MapParentAt(address)?.Map, 
			DialMode.PocketMap => Find.Maps[address.tileId].PocketMapParent.Map, 
			_ => null, 
		};
		if (map != null)
		{
			_connectedStargate = SgUtilities.GetAllStargatesOnMap(map).FirstOrFallback();
		}
		if (_connectedStargate != null)
		{
			_connectedStargateComp = _connectedStargate.TryGetComp<CompStargate>();
			if (!_connectedStargateComp.StargateIsActive)
			{
				_connectedStargateComp._connectedStargate = parent;
				_connectedStargateComp._connectedStargateComp = this;
				_connectedStargateComp.IsReceivingGate = true;
				_connectedStargateComp.TicksUntilOpen = TicksUntilOpen;
			}
		}
	}

	private void OpenStargate(PlanetTile address)
	{
		if (StargateIsActive)
		{
			Log.Error($"[StargatesMod] Tried to open an outgoing connection from {parent} while it was already active.");
			DialFail();
			return;
		}
		MapParent connectedMapParent = null;
		switch (_dialMode)
		{
		case DialMode.None:
			Log.Error("[StargatesMod] Dial failed: No dial mode set.");
			DialFail();
			return;
		case DialMode.IncomingRaid:
			IsReceivingGate = true;
			_ticksSinceBufferUnloaded = -150;
			break;
		case DialMode.Map:
			connectedMapParent = Find.WorldObjects.MapParentAt(address);
			break;
		case DialMode.PocketMap:
			connectedMapParent = Find.Maps.ElementAt(address.tileId).PocketMapParent;
			break;
		}
		if (_dialMode != DialMode.IncomingRaid && connectedMapParent == null)
		{
			Log.Error($"[StargatesMod] Failed to find MapParent at {address} with dial mode {_dialMode}");
			DialFail("SGM.GateDialFailed_NotFound");
		}
		else if (_dialMode == DialMode.Map && connectedMapParent != null && !connectedMapParent.HasMap)
		{
			if (Prefs.LogVerbose || _modSettings.DebugMode)
			{
				Log.Message($"[StargatesMod] generating map for {connectedMapParent}");
			}
			LongEventHandler.QueueLongEvent(delegate
			{
				GetOrGenerateMapUtility.GetOrGenerateMap(connectedMapParent.Tile, (connectedMapParent is WorldObject_PermSgSite) ? new IntVec3(75, 1, 75) : Find.World.info.initialMapSize, connectedMapParent.def);
			}, "SGM.GeneratingStargateSite", doAsynchronously: false, GameAndMapInitExceptionHandlers.ErrorWhileGeneratingMap, showExtraUIInfo: true, forceHideUI: false, delegate
			{
				if (Prefs.LogVerbose || _modSettings.DebugMode)
				{
					Log.Message("[StargatesMod] finished generating map");
				}
				FinishDiallingStargate(address, connectedMapParent);
			});
		}
		else
		{
			FinishDiallingStargate(address, connectedMapParent);
		}
	}

	private void FinishDiallingStargate(PlanetTile address, MapParent connectedMapParent)
	{
		StargateIsActive = true;
		if (_dialMode != DialMode.IncomingRaid)
		{
			Thing thing = SgUtilities.GetAllStargatesOnMap(connectedMapParent.Map).FirstOrFallback();
			_connectedStargateComp = thing?.TryGetComp<CompStargate>();
			if (thing == null || _connectedStargateComp == null || _connectedStargateComp.StargateIsActive || (_connectedStargateComp.TicksUntilOpen > -1 && _connectedStargateComp._connectedStargateComp != this))
			{
				string failReasonKey = "";
				if (thing == null || _connectedStargateComp == null)
				{
					Log.Error($"[StargatesMod] Failed to connect to stargate stargate = {thing}, sgComp = {_connectedStargateComp}:");
					failReasonKey = "SGM.GateDialFailed_NotFound";
				}
				else if (Prefs.LogVerbose || _modSettings.DebugMode)
				{
					Log.Warning("[StargatesMod] failed to dial stargate: target stargate was already active");
					failReasonKey = "SGM.GateDialFailed_IsInUse";
				}
				DialFail(failReasonKey);
				return;
			}
			_connectedStargate = thing;
			_connectedStargateComp.StargateIsActive = true;
			_connectedStargateComp.IsReceivingGate = true;
			_connectedStargateComp._connectedStargate = parent;
			_connectedStargateComp._connectedStargateComp = this;
			switch (_dialMode)
			{
			case DialMode.Map:
				_connectedAddress = address;
				break;
			case DialMode.PocketMap:
				_connectedAddress = address.tileId;
				break;
			}
			_connectedStargateComp._connectedAddress = GateAddress;
			_connectedStargateComp._puddleSustainer = SgSoundDefOf.StargateMod_SGIdle.TrySpawnSustainer(SoundInfo.InMap(_connectedStargateComp.parent));
			SgSoundDefOf.StargateMod_SGOpen.PlayOneShot(SoundInfo.InMap(_connectedStargateComp.parent));
			_connectedStargateComp.parent.GetComp<CompGlower>().PostMapInit();
		}
		_puddleSustainer = SgSoundDefOf.StargateMod_SGIdle.TrySpawnSustainer(SoundInfo.InMap(parent));
		SgSoundDefOf.StargateMod_SGOpen.PlayOneShot(SoundInfo.InMap(parent));
		parent.GetComp<CompGlower>().UpdateLit(parent.Map);
		if (Prefs.LogVerbose || _modSettings.DebugMode)
		{
			Log.Message($"[StargatesMod] finished opening gate {parent}");
		}
	}

	public void CloseStargate(bool closeOtherGate)
	{
		_transComp?.CancelLoad();
		ClearBuffers();
		CompStargate compStargate = null;
		if (closeOtherGate)
		{
			compStargate = _connectedStargate.TryGetComp<CompStargate>();
			if (_connectedStargate == null || compStargate == null)
			{
				Log.Warning("Receiving stargate connected to stargate " + parent.ThingID + " didn't have CompStargate, but this stargate wanted it closed.");
			}
			else
			{
				compStargate.CloseStargate(closeOtherGate: false);
			}
		}
		SoundDef stargateMod_SGClose = SgSoundDefOf.StargateMod_SGClose;
		stargateMod_SGClose.PlayOneShot(SoundInfo.InMap(parent));
		if (compStargate != null)
		{
			stargateMod_SGClose.PlayOneShot(SoundInfo.InMap(compStargate.parent));
		}
		_puddleSustainer?.End();
		if (Props.explodeOnUse)
		{
			CompExplosive compExplosive = parent.TryGetComp<CompExplosive>();
			if (compExplosive == null)
			{
				Log.Warning("Stargate " + parent.ThingID + " has the explodeOnUse tag set to true but doesn't have CompExplosive.");
			}
			else
			{
				compExplosive.StartWick();
			}
		}
		EndStargateWatching();
		ResetDialState();
		parent.GetComp<CompGlower>().UpdateLit(parent.Map);
	}

	private void DialFail(string failReasonKey = null)
	{
		if (!string.IsNullOrEmpty(failReasonKey))
		{
			Messages.Message(failReasonKey.Translate(), MessageTypeDefOf.NegativeEvent);
		}
		SgSoundDefOf.StargateMod_SGFailDial.PlayOneShot(SoundInfo.InMap(parent));
		ResetDialState();
		ClearBuffers();
	}

	private void ResetDialState()
	{
		_dialMode = DialMode.None;
		_ticksSinceBufferUnloaded = -1;
		_ticksSinceOpened = -1;
		TicksUntilOpen = -1;
		StargateIsActive = false;
		IsReceivingGate = false;
		_queuedAddress = -1;
		_connectedAddress = -1;
		_connectedStargate = null;
		_connectedStargateComp = null;
	}

	private void PlayTeleportSound()
	{
		DefDatabase<SoundDef>.GetNamed($"StargateMod_teleport_{Rand.RangeInclusive(1, 4)}").PlayOneShot(SoundInfo.InMap(parent));
	}

	private void ChangeIrisState(bool checkValid = false)
	{
		if (!checkValid || (Props.canHaveIris && HasIris))
		{
			IrisIsActivated = !IrisIsActivated;
			if (IrisIsActivated)
			{
				SgSoundDefOf.StargateMod_IrisOpen.PlayOneShot(SoundInfo.InMap(parent));
			}
			else
			{
				SgSoundDefOf.StargateMod_IrisClose.PlayOneShot(SoundInfo.InMap(parent));
			}
		}
	}

	private void DoUnstableVortex()
	{
		List<Thing> list = new List<Thing>(1) { parent };
		List<IntVec3> list2 = VortexCells.ToList();
		list.AddRange(from pos in list2
			from thing in parent.Map.thingGrid.ThingsAt(pos)
			where thing.def.category == ThingCategory.Building && thing.def.passability == Traversability.Standable && !thing.def.IsDoor
			select thing);
		List<Thing> list3 = new List<Thing>();
		list3.AddRange(from pos in list2
			from thing in parent.Map.thingGrid.ThingsAt(pos)
			where thing.def.IsMetal && !thing.def.useHitPoints
			select thing);
		foreach (IntVec3 item in list2)
		{
			DamageDef stargatesMod_KawooshExplosion = SgDamageDefOf.StargatesMod_KawooshExplosion;
			Explosion obj = (Explosion)GenSpawn.Spawn(ThingDefOf.Explosion, parent.Position, parent.Map);
			obj.damageFalloff = false;
			obj.damAmount = stargatesMod_KawooshExplosion.defaultDamage;
			obj.Position = item;
			obj.radius = 0.5f;
			obj.damType = stargatesMod_KawooshExplosion;
			obj.StartExplosion(null, list);
			foreach (Thing item2 in list3)
			{
				item2.Destroy();
			}
			list3.Clear();
		}
	}

	private void InitGate()
	{
		bool isHibernating = IsHibernating;
		if (SgUtilities.GetAllStargatesOnMap(parent.Map, new List<Thing>(1) { parent }, excludeHibernating: true, includeLinkedMaps: true).Any())
		{
			_conflictingGate = SgUtilities.GetAllStargatesOnMap(parent.Map, new List<Thing>(1) { parent }, excludeHibernating: true, includeLinkedMaps: true).First();
			if (isHibernating)
			{
				Messages.Message("SGM.Notif.CannotWake".Translate(), MessageTypeDefOf.RejectInput);
			}
			else
			{
				Messages.Message("SGM.Notif.GateHibernating".Translate(), MessageTypeDefOf.CautionInput);
			}
			IsHibernating = true;
			return;
		}
		IsInPocketMap = parent.Map.IsPocketMap;
		if (IsInPocketMap)
		{
			GateAddress = parent.Map.Index;
			AddressComp.AddPocketMapAddress(GateAddress);
		}
		else
		{
			GateAddress = parent.Map.Tile;
			AddressComp.AddAddress(GateAddress);
		}
		IsHibernating = false;
		_conflictingGate = null;
		GateDesignation = SgUtilities.GetStargateDesignation((!IsInPocketMap || parent.Map.PocketMapParent.sourceMap == null) ? GateAddress : parent.Map.PocketMapParent.sourceMap.Tile);
		if (_transComp == null)
		{
			_transComp = parent.GetComp<CompTransporter>();
		}
		if (isHibernating)
		{
			SgSoundDefOf.StargateMod_Steam.PlayOneShot(SoundInfo.InMap(parent));
		}
	}

	private void GateDialTick()
	{
		if (!_modSettings.ShortenGateDialSeq)
		{
			int ticksUntilOpen = TicksUntilOpen;
			if (ticksUntilOpen == 300 || ticksUntilOpen == 600 || ticksUntilOpen == 900)
			{
				SgSoundDefOf.StargateMod_RingUsualStart.PlayOneShot(SoundInfo.InMap(parent));
				_prevRingSoundQueue = TicksUntilOpen;
			}
			if (TicksUntilOpen == _prevRingSoundQueue - 240 && _chevronSoundCounter < 3)
			{
				DefDatabase<SoundDef>.GetNamed($"StargateMod_ChevUsual_{_chevronSoundCounter + 1}").PlayOneShot(SoundInfo.InMap(parent));
				_chevronSoundCounter++;
			}
		}
		else if (TicksUntilOpen == 200)
		{
			SgSoundDefOf.StargateMod_RingUsualStart.PlayOneShot(SoundInfo.InMap(parent));
		}
		TicksUntilOpen--;
		if (TicksUntilOpen == 0)
		{
			TicksUntilOpen = -1;
			if (_dialMode != DialMode.None)
			{
				OpenStargate(_queuedAddress);
			}
			_queuedAddress = -1;
			_checkVortexPawnsTick = -1;
			_prevRingSoundQueue = 0;
			_chevronSoundCounter = 0;
		}
	}

	private void CheckVortexPawns()
	{
		if (_pawnsWatchingStargate == null)
		{
			_pawnsWatchingStargate = new List<Pawn>();
		}
		IntVec3 intVec = parent.Position + new IntVec3(0, 0, -1).RotatedBy(parent.Rotation);
		List<IntVec3> source = GenRadial.RadialCellsAround(intVec, 6f, useCenter: true).ToList();
		Map map = parent.Map;
		if (Prefs.LogVerbose || _modSettings.DebugMode)
		{
			Log.Message($"[StargatesMod] Checking on pawns in stargate danger zone.. (on TicksUntilOpen {TicksUntilOpen})");
		}
		if (Prefs.LogVerbose || _modSettings.DebugMode)
		{
			Log.Message($"[StargatesMod] check radius center cell = {intVec}");
		}
		foreach (Thing item in from thing in source.SelectMany((IntVec3 pos) => map.thingGrid.ThingsAt(pos))
			where thing is Pawn { DeadOrDowned: false, Drafted: false } pawn2 && pawn2.Faction == Faction.OfPlayer && !_pawnsWatchingStargate.Contains(pawn2)
			select thing)
		{
			Pawn pawn = (Pawn)item;
			Room pawnRoom = pawn.Position.GetRoom(pawn.Map);
			List<IntVec3> list = (from c in GenRadial.RadialCellsAround(pawn.Position, 6f, useCenter: true)
				where c.InBounds(map) && c.Walkable(map) && c.GetRoom(map) == pawnRoom && !VortexCells.Contains(c)
				select c).ToList();
			if (!list.Any())
			{
				Log.Warning($"[StargatesMod] Could not find any valid cells to send {pawn} to while directing them away from the vortex zone.");
				continue;
			}
			pawn.jobs.StopAll();
			pawn.pather.StopDead();
			IntVec3 intVec2 = list.RandomElement();
			if (Prefs.LogVerbose || _modSettings.DebugMode)
			{
				Log.Message($"[StargatesMod] Directing {pawn} away from vortex to position {intVec2}");
			}
			Job newJob = JobMaker.MakeJob(SgJobDefOf.StargatesMod_WatchStargate, parent, intVec2);
			Pawn_JobTracker jobs = pawn.jobs;
			bool? keepCarryingThingOverride = true;
			jobs.StartJob(newJob, JobCondition.None, null, resumeCurJobAfterwards: true, cancelBusyStances: true, null, null, fromQueue: false, canReturnCurJobToPool: true, keepCarryingThingOverride);
			_pawnsWatchingStargate.Add(pawn);
		}
	}

	private void EndStargateWatching()
	{
		if (_pawnsWatchingStargate.NullOrEmpty())
		{
			return;
		}
		foreach (Pawn item in from pawn in _pawnsWatchingStargate.ToList()
			where !pawn.DeadOrDowned && !pawn.Drafted && pawn.CurJob.def == SgJobDefOf.StargatesMod_WatchStargate
			select pawn)
		{
			item.jobs.StopAll();
		}
		_pawnsWatchingStargate.Clear();
	}

	private void WormholeContentsDisposal(bool isRecvBuffer)
	{
		BufferItem item = (isRecvBuffer ? _recvBuffer[0] : _sendBuffer[0]);
		List<Pawn> list = new List<Pawn>(1) { item.Pawn };
		if (item.CarriedPawn != null)
		{
			list.Add(item.CarriedPawn);
		}
		DamageInfo value = new DamageInfo(isRecvBuffer ? SgDamageDefOf.StargatesMod_IrisCollisionDeath : SgDamageDefOf.StargatesMod_DisintegrationDeath, 99999f, 999f);
		foreach (Pawn item2 in list)
		{
			if (item2.health.hediffSet.HasHediff(HediffDefOf.DeathRefusal))
			{
				item2.health.RemoveHediff(item2.health.hediffSet.hediffs.Find((Hediff hediff) => hediff is Hediff_DeathRefusal));
			}
			item2.Kill(value);
		}
		if (isRecvBuffer)
		{
			_recvBuffer.Remove(item);
			SgSoundDefOf.StargateMod_IrisHit.PlayOneShot(SoundInfo.InMap(parent));
		}
		else
		{
			_sendBuffer.Remove(item);
		}
	}

	public void AddToSendBuffer(BufferItem bufferItem)
	{
		_sendBuffer.Add(bufferItem);
		PlayTeleportSound();
	}

	public void AddToReceiveBuffer(BufferItem bufferItem)
	{
		_recvBuffer.Add(bufferItem);
	}

	private void ClearBuffers()
	{
		List<BufferItem> list = new List<BufferItem>();
		list.AddRange(_sendBuffer);
		list.AddRange(_recvBuffer);
		if (list.NullOrEmpty())
		{
			return;
		}
		foreach (BufferItem item in list)
		{
			GenSpawn.Spawn(item.Thing, parent.InteractionCell, parent.Map);
			Pawn pawn = item.Pawn;
			if (pawn != null)
			{
				Pawn_DraftController drafter = pawn.drafter;
				if (drafter != null)
				{
					drafter.Drafted = item.Drafted;
				}
			}
			if (item.CarriedPawn != null)
			{
				item.Pawn?.carryTracker.innerContainer.TryAdd(item.CarriedPawn, canMergeWithExistingStacks: false);
			}
		}
		_sendBuffer.Clear();
		_recvBuffer.Clear();
	}

	public override void PostDraw()
	{
		base.PostDraw();
		if (IrisIsActivated)
		{
			StargateIris.Draw(parent.Position.ToVector3ShiftedWithAltitude(AltitudeLayer.BuildingOnTop) - Vector3.one * 0.01f, parent.Rotation, parent);
		}
		if (StargateIsActive)
		{
			StargatePuddle.Draw(parent.Position.ToVector3ShiftedWithAltitude(AltitudeLayer.BuildingOnTop) - Vector3.one * 0.02f, parent.Rotation, parent);
		}
	}

	public override void CompTick()
	{
		base.CompTick();
		if (TicksUntilOpen > 0)
		{
			GateDialTick();
		}
		if (!StargateIsActive && TicksUntilOpen > -1)
		{
			if (_checkVortexPawnsTick < 0)
			{
				_checkVortexPawnsTick = 10;
			}
			if (TicksUntilOpen == _checkVortexPawnsTick)
			{
				if (!IrisIsActivated)
				{
					CheckVortexPawns();
				}
				_checkVortexPawnsTick = TicksUntilOpen - 10;
			}
		}
		if (!StargateIsActive)
		{
			return;
		}
		if (!IrisIsActivated && _ticksSinceOpened < 150 && _ticksSinceOpened % 10 == 0)
		{
			DoUnstableVortex();
		}
		if (IsReceivingGate && _ticksSinceOpened < 60 && parent.Fogged())
		{
			FloodFillerFog.FloodUnfog(parent.Position, parent.Map);
		}
		if (_ticksSinceOpened == 210)
		{
			EndStargateWatching();
		}
		if (_connectedStargateComp == null)
		{
			_connectedStargateComp = _connectedStargate?.TryGetComp<CompStargate>();
		}
		if (_transComp == null)
		{
			_transComp = parent.GetComp<CompTransporter>();
		}
		if (_transComp != null)
		{
			Thing thing = _transComp.innerContainer.FirstOrFallback();
			if (thing != null)
			{
				if (thing.Spawned)
				{
					thing.DeSpawn();
				}
				AddToSendBuffer(new BufferItem(thing));
				_transComp.innerContainer.Remove(thing);
			}
			else if (_transComp.LoadingInProgressOrReadyToLaunch && !_transComp.AnyInGroupHasAnythingLeftToLoad)
			{
				_transComp.CancelLoad();
			}
		}
		if (_sendBuffer.Any())
		{
			if (!IsReceivingGate)
			{
				if (_connectedStargateComp != null)
				{
					_connectedStargateComp.AddToReceiveBuffer(_sendBuffer[0]);
					_sendBuffer.Remove(_sendBuffer[0]);
				}
				else
				{
					Log.Error("[StargatesMod] Connected CompStargate was null while trying to send Thing(s) through gate");
					CloseStargate(closeOtherGate: true);
				}
			}
			else
			{
				WormholeContentsDisposal(isRecvBuffer: false);
			}
		}
		if (_recvBuffer.Any() && _ticksSinceBufferUnloaded > Rand.Range(10, 80))
		{
			_ticksSinceBufferUnloaded = 0;
			if (!IrisIsActivated)
			{
				BufferItem item = _recvBuffer[0];
				GenSpawn.Spawn(item.Thing, parent.InteractionCell, parent.Map);
				if (item.Pawn != null)
				{
					if (item.Pawn.Faction == Faction.OfPlayer)
					{
						Pawn_DraftController drafter = item.Pawn.drafter;
						if (drafter != null)
						{
							drafter.Drafted = item.Drafted;
						}
					}
					if (item.CarriedPawn != null && !item.Pawn.carryTracker.innerContainer.TryAdd(item.CarriedPawn, canMergeWithExistingStacks: false))
					{
						GenSpawn.Spawn(item.Pawn, parent.InteractionCell, parent.Map);
					}
				}
				_recvBuffer.Remove(item);
				PlayTeleportSound();
			}
			else
			{
				WormholeContentsDisposal(isRecvBuffer: true);
			}
		}
		_ticksSinceBufferUnloaded++;
		_ticksSinceOpened++;
		if (_dialMode == DialMode.IncomingRaid && !_recvBuffer.Any())
		{
			CloseStargate(closeOtherGate: false);
		}
		if (IsReceivingGate && _ticksSinceBufferUnloaded > 2500 && !_connectedStargateComp.GateIsLoadingTransporter && _sendBuffer.Empty())
		{
			CloseStargate(closeOtherGate: true);
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		base.PostSpawnSetup(respawningAfterLoad);
		if (!respawningAfterLoad)
		{
			InitGate();
		}
		if (StargateIsActive)
		{
			if (_connectedStargate == null && _dialMode <= DialMode.PocketMap && _dialMode != DialMode.None)
			{
				_connectedStargate = SgUtilities.GetAllStargatesOnMap((_dialMode == DialMode.Map) ? Find.WorldObjects.MapParentAt(_connectedAddress).Map : Find.Maps[_connectedAddress.tileId]).FirstOrFallback();
			}
			_puddleSustainer = SgSoundDefOf.StargateMod_SGIdle.TrySpawnSustainer(SoundInfo.InMap(parent));
		}
		CompTransporter transComp = _transComp;
		if (transComp != null && transComp.innerContainer == null)
		{
			_transComp.innerContainer = new ThingOwner<Thing>(_transComp);
		}
		if (Prefs.LogVerbose || _modSettings.DebugMode)
		{
			Log.Message($"[StargatesMod] compsg postspawnssetup: sgactive={StargateIsActive} connectgate={_connectedStargate} connectaddress={_connectedAddress}, mapparent={parent.Map.Parent}");
		}
	}

	public string GetInspectString()
	{
		if (!parent.Spawned)
		{
			return "";
		}
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendLine((!IsHibernating) ? "SGM.GateAddress".Translate(GateDesignation) : "SGM.GateHibernating".Translate());
		if (!StargateIsActive)
		{
			if (TicksUntilOpen <= -1 && !IsHibernating && !IsExpectingIncomingWormhole)
			{
				stringBuilder.AppendLine("SGM.StargateIdle".Translate());
			}
			else if (TicksUntilOpen > -1)
			{
				if (IsExpectingIncomingWormhole)
				{
					stringBuilder.AppendLine("SGM.IncomingWormhole".Translate(_connectedStargateComp.GateDesignation));
				}
				else if (_dialMode == DialMode.IncomingRaid)
				{
					stringBuilder.AppendLine("SGM.IncomingWormhole".Translate("SGM.UnknownAddress".Translate()));
				}
			}
		}
		else
		{
			stringBuilder.AppendLine("SGM.ConnectedToGate".Translate((_connectedStargateComp != null) ? ((NamedArgument)_connectedStargateComp.GateDesignation) : ((NamedArgument)"SGM.Unknown".Translate()), (IsReceivingGate ? "SGM.Incoming" : "SGM.Outgoing").Translate()));
		}
		if (HasIris)
		{
			stringBuilder.AppendLine("SGM.IrisStatus".Translate((IrisIsActivated ? "SGM.IrisClosed" : "SGM.IrisOpen").Translate()));
		}
		if (TicksUntilOpen > 0)
		{
			stringBuilder.AppendLine("SGM.TimeUntilGateLock".Translate(TicksUntilOpen.ToStringTicksToPeriod()));
		}
		if (!_modSettings.DebugMode)
		{
			return stringBuilder.ToString().TrimEndNewlines();
		}
		stringBuilder.AppendLine("=== DebugInfo ===");
		stringBuilder.AppendLine($"TicksSinceOpened = {_ticksSinceOpened}");
		stringBuilder.AppendLine($"TicksUntilOpen = {TicksUntilOpen}");
		stringBuilder.AppendLine($"ticksSinceBufferUnloaded = {_ticksSinceBufferUnloaded}");
		stringBuilder.AppendLine($"IsInPocketMap = {IsInPocketMap}");
		stringBuilder.AppendLine($"_queuedAddress = {_queuedAddress}");
		stringBuilder.AppendLine($"connectedAddress = {_connectedAddress}");
		stringBuilder.AppendLine($"DialMode = {_dialMode}");
		stringBuilder.AppendLine($"IsReceivingGate = {IsReceivingGate}");
		stringBuilder.AppendLine($"_gateAddress = {GateAddress}");
		stringBuilder.AppendLine("_gateDesignation = " + _gateDesignation);
		string text = ((_conflictingGate == null) ? "null" : _conflictingGate.ToString());
		stringBuilder.AppendLine("_conflictingGate = " + text);
		stringBuilder.AppendLine($"_transComp = {_transComp}");
		stringBuilder.AppendLine($"_connectedStargateComp = {_connectedStargateComp}");
		stringBuilder.AppendLine($"GlowComp = {parent.TryGetComp<CompGlower>()}");
		stringBuilder.AppendLine($"GlowRadius = {parent.TryGetComp<CompGlower>().GlowRadius}");
		stringBuilder.AppendLine($"Glows = {parent.TryGetComp<CompGlower>().Glows}");
		string text2 = ((_pawnsWatchingStargate == null || !_pawnsWatchingStargate.Any()) ? "null" : _pawnsWatchingStargate[0].ToString());
		stringBuilder.AppendLine("_PawnsWatchingStargate0 = " + text2);
		return stringBuilder.ToString().TrimEndNewlines();
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in base.CompGetGizmosExtra())
		{
			yield return item;
		}
		if (StargateIsActive && _connectedStargate != null)
		{
			yield return new Command_Action
			{
				defaultLabel = "SGM.SelectConnectedGate".Translate(),
				defaultDesc = "SGM.SelectConnectedGateDesc".Translate(),
				icon = ContentFinder<Texture2D>.Get("UI/Gizmos/SelectStargate"),
				action = delegate
				{
					CameraJumper.TryJumpAndSelect(new GlobalTargetInfo(_connectedStargate));
				}
			};
		}
		if (Props.canHaveIris && HasIris)
		{
			yield return new Command_Action
			{
				defaultLabel = "SGM.OpenCloseIris".Translate(),
				defaultDesc = "SGM.OpenCloseIrisDesc".Translate(),
				icon = ContentFinder<Texture2D>.Get(Props.irisTexture),
				action = delegate
				{
					ChangeIrisState();
				}
			};
		}
		if (!IsReceivingGate && _connectedStargate != null && (int)Faction.OfPlayer.def.techLevel >= 4)
		{
			CompStargate connectedSgComp = _connectedStargate.TryGetComp<CompStargate>();
			if (_connectedStargate.Faction == Faction.OfPlayer && connectedSgComp.Props.canHaveIris && connectedSgComp.HasIris)
			{
				Command_Action command_Action = new Command_Action
				{
					defaultLabel = "SGM.TransmitGDO".Translate(),
					defaultDesc = "SGM.TransmitGDODesc".Translate(),
					icon = ContentFinder<Texture2D>.Get("UI/Gizmos/StargateTransmitGDO"),
					action = delegate
					{
						CameraJumper.TryJumpAndSelect(new GlobalTargetInfo(_connectedStargate));
						connectedSgComp.ChangeIrisState();
					}
				};
				if (!connectedSgComp.IrisIsActivated)
				{
					command_Action.Disable("SGM.CannotGDO".Translate());
				}
				yield return command_Action;
			}
		}
		if (IsHibernating)
		{
			yield return new Command_Action
			{
				defaultLabel = "SGM.WakeHibernation".Translate(),
				defaultDesc = "SGM.WakeHibernationDesc".Translate(),
				icon = ContentFinder<Texture2D>.Get("UI/Gizmos/StargateUnHibernate"),
				action = InitGate
			};
			if (_conflictingGate != null)
			{
				yield return new Command_Action
				{
					defaultLabel = "SGM.SelectGateConflict".Translate(),
					defaultDesc = "SGM.SelectGateConflictDesc".Translate(),
					icon = ContentFinder<Texture2D>.Get("UI/Gizmos/SelectStargate"),
					action = delegate
					{
						CameraJumper.TryJumpAndSelect(new GlobalTargetInfo(_conflictingGate));
					}
				};
			}
		}
		if (StargateIsActive)
		{
			CompTransporter transComp = _transComp;
			if (transComp != null && transComp.LoadingInProgressOrReadyToLaunch)
			{
				yield return new Command_Action
				{
					defaultLabel = "CommandCancelLoad".Translate(),
					defaultDesc = "SGM.CommandCancelLoadStargateDesc".Translate(),
					icon = ContentFinder<Texture2D>.Get("UI/Designators/Cancel"),
					action = delegate
					{
						SoundDefOf.Designate_Cancel.PlayOneShotOnCamera();
						_transComp.CancelLoad();
					}
				};
			}
		}
		if (!Prefs.DevMode)
		{
			yield break;
		}
		yield return new Command_Action
		{
			defaultLabel = "Force close",
			defaultDesc = "Force close this gate to hopefully remove strange behaviours (this will not close gate at the other end).",
			action = delegate
			{
				CloseStargate(closeOtherGate: false);
				Log.Message($"[StargatesMod] Stargate {parent} was force-closed.");
			}
		};
		if (Props.canHaveIris)
		{
			yield return new Command_Action
			{
				defaultLabel = "Add/remove iris",
				action = delegate
				{
					HasIris = !HasIris;
					IrisIsActivated = false;
				}
			};
		}
	}

	private void CleanupGate(Map map)
	{
		if (IsHibernating)
		{
			return;
		}
		if (StargateIsActive)
		{
			CloseStargate(_connectedStargate != null);
		}
		else
		{
			ResetDialState();
		}
		if (IsInPocketMap)
		{
			AddressComp.RemovePocketMapAddress(GateAddress);
		}
		else
		{
			AddressComp.RemoveAddress(GateAddress);
		}
		List<Thing> allStargatesOnMap = SgUtilities.GetAllStargatesOnMap(map, null, excludeHibernating: false, includeLinkedMaps: true);
		if (!allStargatesOnMap.Any())
		{
			return;
		}
		foreach (Thing item in allStargatesOnMap.Where((Thing g) => g.TryGetComp<CompStargate>()._conflictingGate == parent))
		{
			item.TryGetComp<CompStargate>()._conflictingGate = null;
		}
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
	{
		base.PostDeSpawn(map, mode);
		CleanupGate(map);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		base.PostDestroy(mode, previousMap);
		CleanupGate(previousMap);
	}

	public override void PostExposeData()
	{
		base.PostExposeData();
		Scribe_Values.Look(ref StargateIsActive, "StargateIsActive", defaultValue: false);
		Scribe_Values.Look(ref GateAddress, "GateAddress");
		Scribe_Values.Look(ref _gateDesignation, "_gateDesignation");
		Scribe_Values.Look(ref _dialMode, "_dialMode", DialMode.None);
		Scribe_Values.Look(ref _queuedAddress, "_queuedAddress");
		Scribe_Values.Look(ref IsReceivingGate, "IsReceivingGate", defaultValue: false);
		Scribe_Values.Look(ref IsInPocketMap, "IsInPocketMap", defaultValue: false);
		Scribe_Values.Look(ref HasIris, "HasIris", defaultValue: false);
		Scribe_Values.Look(ref IrisIsActivated, "IrisIsActivated", defaultValue: false);
		Scribe_Values.Look(ref TicksUntilOpen, "TicksUntilOpen", 0);
		Scribe_Values.Look(ref _ticksSinceOpened, "TicksSinceOpened", 0);
		Scribe_Values.Look(ref _ticksSinceBufferUnloaded, "_ticksSinceBufferUnloaded", 0);
		Scribe_Values.Look(ref IsHibernating, "IsHibernating", defaultValue: false);
		Scribe_Values.Look(ref _connectedAddress, "_connectedAddress");
		Scribe_Values.Look(ref _prevRingSoundQueue, "_prevRingSoundQueue", 0);
		Scribe_Values.Look(ref _chevronSoundCounter, "_chevronSoundCounter", 0);
		Scribe_References.Look(ref _conflictingGate, "_conflictingGate");
		Scribe_References.Look(ref _connectedStargate, "_connectedStargate");
		Scribe_Collections.Look(ref _recvBuffer, "_recvBuffer", LookMode.GlobalTargetInfo);
		Scribe_Collections.Look(ref _sendBuffer, "_sendBuffer", LookMode.GlobalTargetInfo);
	}

	public override string CompInspectStringExtra()
	{
		return base.CompInspectStringExtra() + "SGM.RespawnGateString".Translate();
	}
}
