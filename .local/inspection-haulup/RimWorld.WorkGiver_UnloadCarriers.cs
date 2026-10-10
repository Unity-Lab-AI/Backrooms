using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimWorld;

public class WorkGiver_UnloadCarriers : WorkGiver_Scanner
{
	public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.Pawn);

	public override PathEndMode PathEndMode => PathEndMode.Touch;

	public override bool ShouldSkip(Pawn pawn, bool forced = false)
	{
		IReadOnlyList<Pawn> allPawnsSpawned = pawn.Map.mapPawns.AllPawnsSpawned;
		for (int i = 0; i < allPawnsSpawned.Count; i++)
		{
			if (allPawnsSpawned[i].inventory.UnloadEverything)
			{
				return false;
			}
		}
		return true;
	}

	public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
	{
		return pawn.Map.mapPawns.SpawnedPawnsWhoShouldHaveInventoryUnloaded;
	}

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		return UnloadCarriersJobGiverUtility.HasJobOnThing(pawn, t, forced);
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		return JobMaker.MakeJob(JobDefOf.UnloadInventory, t);
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.1.0.9782' (yours is '9.1.0.7988')
