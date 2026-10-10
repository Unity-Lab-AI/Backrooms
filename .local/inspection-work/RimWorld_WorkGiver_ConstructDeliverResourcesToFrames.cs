using Verse;
using Verse.AI;

namespace RimWorld;

public class WorkGiver_ConstructDeliverResourcesToFrames : WorkGiver_ConstructDeliverResources
{
	public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.BuildingFrame);

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		if (t.Faction != pawn.Faction)
		{
			return false;
		}
		if (!(t is Frame frame))
		{
			return false;
		}
		if (!GenConstruct.CanTouchTargetFromValidCell(frame, pawn))
		{
			return false;
		}
		if (GenConstruct.FirstBlockingThing(frame, pawn) != null)
		{
			return GenConstruct.HandleBlockingThingJob(frame, pawn, forced) != null;
		}
		if (!GenConstruct.CanConstruct(frame, pawn, def.workType, forced, JobDefOf.HaulToContainer))
		{
			return false;
		}
		if (!GenConstruct.CanGetResources_NewTemp(frame, pawn, forced))
		{
			return false;
		}
		return ResourceDeliverJobFor(pawn, frame, canRemoveExistingFloorUnderNearbyNeeders: true, forced) != null;
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		if (t.Faction != pawn.Faction)
		{
			return null;
		}
		if (!(t is Frame frame))
		{
			return null;
		}
		if (!GenConstruct.CanTouchTargetFromValidCell(frame, pawn))
		{
			return null;
		}
		if (GenConstruct.FirstBlockingThing(frame, pawn) != null)
		{
			return GenConstruct.HandleBlockingThingJob(frame, pawn, forced);
		}
		if (!GenConstruct.CanConstruct(frame, pawn, def.workType, forced, JobDefOf.HaulToContainer))
		{
			return null;
		}
		return ResourceDeliverJobFor(pawn, frame, canRemoveExistingFloorUnderNearbyNeeders: true, forced);
	}
}
