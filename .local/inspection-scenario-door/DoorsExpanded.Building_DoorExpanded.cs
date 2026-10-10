using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace DoorsExpanded;

public class Building_DoorExpanded : Building_MultiTileDoor
{
	internal class DebugDrawVectors
	{
		public float openPct;

		public Vector3 offsetVector;

		public Vector3 scaleVector;

		public Vector3 graphicVector;
	}

	private CompProperties_DoorExpanded props;

	private CompForbiddable forbiddenComp;

	private const float VisualDoorOffsetStart = 0f;

	internal const float VisualDoorOffsetEnd = 0.45f;

	internal DebugDrawVectors debugDrawVectors = new DebugDrawVectors();

	public virtual bool Forbidden => forbiddenComp?.Forbidden ?? false;

	public CompProperties_DoorExpanded Props
	{
		get
		{
			CompProperties_DoorExpanded compProperties_DoorExpanded = props;
			if (compProperties_DoorExpanded == null)
			{
				CompProperties_DoorExpanded obj = def.GetDoorExpandedProps() ?? throw new Exception("Missing " + typeof(CompProperties_DoorExpanded));
				CompProperties_DoorExpanded compProperties_DoorExpanded2 = obj;
				props = obj;
				compProperties_DoorExpanded = compProperties_DoorExpanded2;
			}
			return compProperties_DoorExpanded;
		}
	}

	protected override void Tick()
	{
		base.Tick();
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		TLog.Log(this, null, "SpawnSetup");
		base.Rotation = DoorRotationAt(def, Props, base.Position, base.Rotation, map);
		base.SpawnSetup(map, respawningAfterLoad);
		powerComp = GetComp<CompPowerTrader>();
		forbiddenComp = GetComp<CompForbiddable>();
		this.SetForbidden(Forbidden);
		ClearReachabilityCache(map);
		if (base.BlockedOpenMomentary)
		{
			DoorOpen();
		}
	}

	public static Rot4 DoorRotationAt(ThingDef def, CompProperties_DoorExpanded props, IntVec3 loc, Rot4 rot, Map map)
	{
		if (!def.rotatable)
		{
			IntVec2 size = def.Size;
			bool flag = size.x == 1 && size.z == 1;
			if (!flag)
			{
				DoorType doorType = props.doorType;
				bool flag2 = ((doorType == DoorType.Stretch || doorType == DoorType.StretchVertical) ? true : false);
				flag = flag2;
			}
			if (flag)
			{
				rot = DoorUtility.DoorRotationAt(loc, map, preferFences: false);
			}
		}
		if (!props.rotatesSouth && rot == Rot4.South)
		{
			rot = Rot4.North;
		}
		return rot;
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		drawLoc.y = AltitudeLayer.DoorMoveable.AltitudeFor();
		Rot4 rot = (base.Rotation = DoorRotationAt(def, Props, base.Position, base.Rotation, base.Map));
		float openPct = OpenPct;
		for (int num = 0; num < 2; num++)
		{
			bool flag = num != 0;
			Graphic graphic;
			if (!flag)
			{
				GraphicData doorAsync = Props.doorAsync;
				if (doorAsync != null)
				{
					graphic = doorAsync.GraphicColoredFor(this);
					goto IL_006d;
				}
			}
			graphic = Graphic;
			goto IL_006d;
			IL_006d:
			Graphic graphic2 = graphic;
			Draw(def, Props, graphic2, drawLoc, rot, openPct, flag);
			graphic2.ShadowGraphic?.DrawWorker(drawLoc, rot, def, this, 0f);
			if (props.singleDoor)
			{
				break;
			}
		}
		if (props.doorFrame != null)
		{
			DrawFrameParams(def, Props, drawLoc, rot, split: false, out var mesh, out var matrix);
			Graphics.DrawMesh(mesh, matrix, props.doorFrame.GraphicColoredFor(this).MatAt(rot), 0);
			if (props.doorFrameSplit != null)
			{
				DrawFrameParams(def, Props, drawLoc, rot, split: true, out mesh, out matrix);
				Graphics.DrawMesh(mesh, matrix, props.doorFrameSplit.GraphicColoredFor(this).MatAt(rot), 0);
			}
		}
		Comps_PostDraw();
	}

	internal static void Draw(ThingDef def, CompProperties_DoorExpanded props, Graphic graphic, Vector3 drawPos, Rot4 rotation, float openPct, bool flipped, DebugDrawVectors drawVectors = null)
	{
		Mesh mesh;
		Quaternion rotQuat;
		Vector3 offsetVector;
		Vector3 scaleVector;
		switch (props.doorType)
		{
		case DoorType.Stretch:
		case DoorType.StretchVertical:
			DrawStretchParams(def, props, rotation, openPct, flipped, out mesh, out rotQuat, out offsetVector, out scaleVector);
			break;
		case DoorType.DoubleSwing:
			DrawDoubleSwingParams(def, props, drawPos, rotation, openPct, flipped, out mesh, out rotQuat, out offsetVector, out scaleVector);
			break;
		default:
			DrawStandardParams(def, props, rotation, openPct, flipped, out mesh, out rotQuat, out offsetVector, out scaleVector);
			break;
		}
		Vector3 vector = drawPos + offsetVector;
		Matrix4x4 matrix = Matrix4x4.TRS(vector, rotQuat, scaleVector);
		Graphics.DrawMesh(mesh, matrix, graphic.MatAt(rotation), 0);
		if (drawVectors != null)
		{
			drawVectors.openPct = openPct;
			drawVectors.offsetVector = offsetVector;
			drawVectors.scaleVector = scaleVector;
			drawVectors.graphicVector = vector;
		}
	}

	private static void DrawStretchParams(ThingDef def, CompProperties_DoorExpanded props, Rot4 rotation, float openPct, bool flipped, out Mesh mesh, out Quaternion rotQuat, out Vector3 offsetVector, out Vector3 scaleVector)
	{
		Vector2 drawSize = def.graphicData.drawSize;
		Vector2 stretchCloseSize = props.stretchCloseSize;
		Vector2 stretchOpenSize = props.stretchOpenSize;
		Vector2 value = props.stretchOffset.Value;
		float num = ((rotation.IsHorizontal && props.fixedPerspective) ? 2f : 1f);
		offsetVector = new Vector3(value.x * openPct * num, 0f, value.y * openPct * num);
		float x = Mathf.LerpUnclamped(stretchOpenSize.x, stretchCloseSize.x, 1f - openPct) / stretchCloseSize.x * drawSize.x * num;
		float z = Mathf.LerpUnclamped(stretchOpenSize.y, stretchCloseSize.y, 1f - openPct) / stretchCloseSize.y * drawSize.y * num;
		scaleVector = new Vector3(x, 1f, z);
		if (rotation == Rot4.South)
		{
			offsetVector.z = 0f - offsetVector.z;
		}
		if (!flipped)
		{
			mesh = MeshPool.plane10;
		}
		else
		{
			offsetVector.x = 0f - offsetVector.x;
			mesh = MeshPool.plane10Flip;
		}
		rotQuat = rotation.AsQuat;
		offsetVector = rotQuat * offsetVector;
	}

	private static void DrawDoubleSwingParams(ThingDef def, CompProperties_DoorExpanded props, Vector3 drawPos, Rot4 rotation, float openPct, bool flipped, out Mesh mesh, out Quaternion rotQuat, out Vector3 offsetVector, out Vector3 scaleVector)
	{
		bool isHorizontal = rotation.IsHorizontal;
		if (!flipped)
		{
			offsetVector = new Vector3(-1f, 0f, 0f);
			if (isHorizontal)
			{
				offsetVector = new Vector3(1.4f, 0f, 1.1f);
			}
			mesh = MeshPool.plane10;
		}
		else
		{
			offsetVector = new Vector3(1f, 0f, 0f);
			if (isHorizontal)
			{
				offsetVector = new Vector3(-1.4f, 0f, 1.1f);
			}
			mesh = MeshPool.plane10Flip;
		}
		if (isHorizontal)
		{
			rotQuat = Quaternion.AngleAxis(rotation.AsAngle + openPct * (flipped ? 90f : (-90f)), Vector3.up);
		}
		else
		{
			rotQuat = rotation.AsQuat;
		}
		offsetVector = rotQuat * offsetVector;
		float num = (0f + props.doorOpenMultiplier * openPct) * (float)def.Size.x;
		offsetVector *= num;
		if (isHorizontal && ((!flipped && rotation == Rot4.East) || (flipped && rotation == Rot4.West)))
		{
			offsetVector.y = Mathf.Max(0f, AltitudeLayer.BuildingOnTop.AltitudeFor() - drawPos.y);
		}
		Vector2 drawSize = def.graphicData.drawSize;
		float num2 = ((isHorizontal && props.fixedPerspective) ? 2f : 1f);
		scaleVector = new Vector3(drawSize.x * num2, 1f, drawSize.y * num2);
	}

	private static void DrawStandardParams(ThingDef def, CompProperties_DoorExpanded props, Rot4 rotation, float openPct, bool flipped, out Mesh mesh, out Quaternion rotQuat, out Vector3 offsetVector, out Vector3 scaleVector)
	{
		bool isHorizontal = rotation.IsHorizontal;
		if (!flipped)
		{
			offsetVector = new Vector3(-1f, 0f, 0f);
			mesh = MeshPool.plane10;
		}
		else
		{
			offsetVector = new Vector3(1f, 0f, 0f);
			mesh = MeshPool.plane10Flip;
		}
		rotQuat = rotation.AsQuat;
		offsetVector = rotQuat * offsetVector;
		float num = (0f + props.doorOpenMultiplier * openPct) * (float)def.Size.x;
		offsetVector *= num;
		Vector2 drawSize = def.graphicData.drawSize;
		float num2 = ((isHorizontal && props.fixedPerspective) ? 2f : 1f);
		scaleVector = new Vector3(drawSize.x * num2, 1f, drawSize.y * num2);
	}

	private static void DrawFrameParams(ThingDef def, CompProperties_DoorExpanded props, Vector3 drawPos, Rot4 rotation, bool split, out Mesh mesh, out Matrix4x4 matrix)
	{
		bool isHorizontal = rotation.IsHorizontal;
		Vector3 vector = new Vector3(-1f, 0f, 0f);
		mesh = MeshPool.plane10;
		if (props.doorFrameSplit != null && rotation == Rot4.West)
		{
			vector.x = 1f;
		}
		Quaternion quaternion = rotation.AsQuat;
		vector = quaternion * vector;
		float num = (0f + props.doorOpenMultiplier * 1f) * (float)def.Size.x;
		vector *= num;
		Vector2 drawSize = props.doorFrame.drawSize;
		float num2 = ((isHorizontal && props.fixedPerspective) ? 2f : 1f);
		Vector3 s = new Vector3(drawSize.x * num2, 1f, drawSize.y * num2);
		Vector3 pos = drawPos;
		pos.y = AltitudeLayer.Blueprint.AltitudeFor();
		if (rotation == Rot4.North || rotation == Rot4.South)
		{
			pos.y = AltitudeLayer.PawnState.AltitudeFor();
		}
		if (!isHorizontal)
		{
			pos.x += num;
		}
		if (rotation == Rot4.East)
		{
			pos.z -= num;
			if (split)
			{
				pos.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
			}
		}
		else if (rotation == Rot4.West)
		{
			pos.z += num;
			if (split)
			{
				pos.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
			}
		}
		pos += vector;
		Vector3 vector2 = props.doorFrameOffset;
		if (props.doorFrameSplit != null && rotation == Rot4.West)
		{
			quaternion = Quaternion.Euler(0f, 270f, 0f);
			pos.z -= 2.7f;
			mesh = MeshPool.plane10Flip;
			vector2 = props.doorFrameSplitOffset;
		}
		pos += vector2;
		matrix = Matrix4x4.TRS(pos, quaternion, s);
	}

	private void ClearReachabilityCache(Map map)
	{
		map.reachability.ClearCache();
	}
}
