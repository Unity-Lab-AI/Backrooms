using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace StargatesMod;

public class CompDialHomeDevice : ThingComp
{
	private CompFacility _compFacility;

	public PlanetTile QueuedAddress = -1;

	public DialMode DialMode;

	public CompProperties_DialHomeDevice Props => (CompProperties_DialHomeDevice)props;

	public bool IsConnectedToStargate
	{
		get
		{
			if (Props.selfDialler)
			{
				return true;
			}
			return _compFacility.LinkedBuildings.Count != 0;
		}
	}

	public CompStargate GetLinkedStargateComp()
	{
		if (Props.selfDialler)
		{
			return parent.TryGetComp<CompStargate>();
		}
		int count = _compFacility.LinkedBuildings.Count;
		if (count <= 1)
		{
			if (count == 1)
			{
				return _compFacility.LinkedBuildings[0].TryGetComp<CompStargate>();
			}
			return null;
		}
		return _compFacility.LinkedBuildings.Where((Thing t) => !t.TryGetComp<CompStargate>().IsHibernating).FirstOrFallback().TryGetComp<CompStargate>();
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		base.PostSpawnSetup(respawningAfterLoad);
		_compFacility = parent.GetComp<CompFacility>();
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in base.CompGetGizmosExtra())
		{
			yield return item;
		}
		CompStargate compStargate = GetLinkedStargateComp();
		if (compStargate != null)
		{
			Command_Action command_Action = new Command_Action
			{
				defaultLabel = "SGM.CloseStargate".Translate(),
				defaultDesc = "SGM.CloseStargateDesc".Translate(),
				icon = ContentFinder<Texture2D>.Get("UI/Designators/Cancel"),
				action = delegate
				{
					compStargate.CloseStargate(closeOtherGate: true);
				}
			};
			if (!compStargate.StargateIsActive)
			{
				command_Action.Disable("SGM.GateIsNotActive".Translate());
			}
			else if (compStargate.IsReceivingGate)
			{
				command_Action.Disable("SGM.CannotCloseIncoming".Translate());
			}
			yield return command_Action;
		}
	}
}
