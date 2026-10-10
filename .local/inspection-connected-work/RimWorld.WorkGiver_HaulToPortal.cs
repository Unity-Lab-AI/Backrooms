using Verse;
using Verse.AI;

namespace RimWorld;

public class WorkGiver_HaulToPortal : WorkGiver_Scanner
{
	public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.MapPortal);

	public override PathEndMode PathEndMode => PathEndMode.Touch;

	public override Danger MaxPathDanger(Pawn pawn)
	{
		return Danger.Deadly;
	}

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		MapPortal portal = t as MapPortal;
		return EnterPortalUtility.HasJobOnPortal(pawn, portal);
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		MapPortal portal = t as MapPortal;
		return EnterPortalUtility.JobOnPortal(pawn, portal);
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.1.0.9782' (yours is '9.1.0.7988')
