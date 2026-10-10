using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimWorld;

public class WorkGiver_TakeBeerOutOfFermentingBarrel : WorkGiver_Scanner
{
	public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForDef(ThingDefOf.FermentingBarrel);

	public override PathEndMode PathEndMode => PathEndMode.Touch;

	public override bool ShouldSkip(Pawn pawn, bool forced = false)
	{
		List<Thing> list = pawn.Map.listerThings.ThingsOfDef(ThingDefOf.FermentingBarrel);
		for (int i = 0; i < list.Count; i++)
		{
			if (((Building_FermentingBarrel)list[i]).Fermented)
			{
				return false;
			}
		}
		return true;
	}

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		if (!(t is Building_FermentingBarrel { Fermented: not false }))
		{
			return false;
		}
		if (t.IsBurning())
		{
			return false;
		}
		if (!pawn.CanReserve(t, 1, -1, null, forced))
		{
			return false;
		}
		return true;
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		return JobMaker.MakeJob(JobDefOf.TakeBeerOutOfFermentingBarrel, t);
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.1.0.9782' (yours is '9.1.0.7988')
