using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace EdB.PrepareCarefully;

public class ManagerEquipment
{
	public delegate void CostAffectedHandler();

	public ModState State { get; set; }

	public EquipmentDatabase EquipmentDatabase { get; set; }

	public event CostAffectedHandler CostAffected;

	public void InitializeStateFromScenarioAndStartingPawns()
	{
		State.Customizations.Equipment = new List<CustomizedEquipment>();
		int num = -1;
		List<ScenPart> fieldValue = ReflectionUtil.GetFieldValue<List<ScenPart>>(Find.Scenario, "parts");
		if (fieldValue == null)
		{
			throw new InitializationException("Could not get list of parts from the scenario.  Part list was null.");
		}
		State.OriginalScenarioParts = fieldValue.ConvertAll((ScenPart p) => p);
		State.ReplacedScenarioParts.Clear();
		foreach (ScenPart allPart in Find.Scenario.AllParts)
		{
			num++;
			if (allPart is ScenPart_ScatterThingsNearPlayerStart obj)
			{
				FieldInfo field = typeof(ScenPart_ScatterThingsNearPlayerStart).GetField("thingDef", BindingFlags.Instance | BindingFlags.NonPublic);
				FieldInfo field2 = typeof(ScenPart_ScatterThingsNearPlayerStart).GetField("stuff", BindingFlags.Instance | BindingFlags.NonPublic);
				FieldInfo field3 = typeof(ScenPart_ScatterThingsNearPlayerStart).GetField("count", BindingFlags.Instance | BindingFlags.NonPublic);
				FieldInfo field4 = typeof(ScenPart_ScatterThingsNearPlayerStart).GetField("quality", BindingFlags.Instance | BindingFlags.NonPublic);
				ThingDef thingDef = (ThingDef)field.GetValue(obj);
				ThingDef thingDef2 = (ThingDef)field2.GetValue(obj);
				QualityCategory? quality = (QualityCategory?)field4.GetValue(obj);
				EquipmentDatabase.PreloadDefinition(thingDef2);
				EquipmentDatabase.PreloadDefinition(thingDef);
				int count = (int)field3.GetValue(obj);
				new EquipmentKey(thingDef, thingDef2);
				EquipmentOption equipmentOption = EquipmentDatabase.FindOptionForThingDef(thingDef);
				if (equipmentOption == null)
				{
					Logger.Warning("Couldn't initialize all scenario equipment.  Didn't find an equipment entry for " + thingDef.defName);
				}
				if (equipmentOption != null)
				{
					AddEquipment(new CustomizedEquipment
					{
						EquipmentOption = equipmentOption,
						StuffDef = thingDef2,
						Count = count,
						SpawnType = EquipmentSpawnType.SpawnsNear,
						Quality = quality
					});
					State.ReplacedScenarioParts.Add(allPart);
				}
			}
			if (allPart is ScenPart_StartingThing_Defined obj2)
			{
				FieldInfo field5 = typeof(ScenPart_StartingThing_Defined).GetField("thingDef", BindingFlags.Instance | BindingFlags.NonPublic);
				FieldInfo field6 = typeof(ScenPart_StartingThing_Defined).GetField("stuff", BindingFlags.Instance | BindingFlags.NonPublic);
				FieldInfo field7 = typeof(ScenPart_StartingThing_Defined).GetField("count", BindingFlags.Instance | BindingFlags.NonPublic);
				FieldInfo field8 = typeof(ScenPart_StartingThing_Defined).GetField("quality", BindingFlags.Instance | BindingFlags.NonPublic);
				ThingDef thingDef3 = (ThingDef)field5.GetValue(obj2);
				ThingDef thingDef4 = (ThingDef)field6.GetValue(obj2);
				QualityCategory? quality2 = (QualityCategory?)field8.GetValue(obj2);
				EquipmentDatabase.PreloadDefinition(thingDef4);
				EquipmentDatabase.PreloadDefinition(thingDef3);
				int count2 = (int)field7.GetValue(obj2);
				EquipmentOption equipmentOption2 = EquipmentDatabase.FindOptionForThingDef(thingDef3);
				if (equipmentOption2 != null)
				{
					AddEquipment(new CustomizedEquipment
					{
						EquipmentOption = equipmentOption2,
						StuffDef = thingDef4,
						Count = count2,
						SpawnType = EquipmentSpawnType.SpawnsWith,
						Quality = quality2
					});
					State.ReplacedScenarioParts.Add(allPart);
				}
				else
				{
					Logger.Warning(string.Format("Couldn't initialize all scenario equipment.  Didn't find an equipment entry for {0} ({1})", thingDef3.defName, (thingDef4 != null) ? thingDef4.defName : "no material"));
				}
			}
			if (allPart is ScenPart_StartingAnimal)
			{
				int privateField = allPart.GetPrivateField<int>("count");
				PawnKindDef privateField2 = allPart.GetPrivateField<PawnKindDef>("animalKind");
				if (privateField2 != null && privateField2.race != null)
				{
					EquipmentDatabase.PreloadDefinition(privateField2.race);
					EquipmentOption equipmentOption3 = EquipmentDatabase.FindOptionForThingDef(privateField2.race);
					if (equipmentOption3 != null)
					{
						AddEquipment(new CustomizedEquipment
						{
							EquipmentOption = equipmentOption3,
							Count = privateField,
							SpawnType = EquipmentSpawnType.Animal
						});
						State.ReplacedScenarioParts.Add(allPart);
					}
				}
				else
				{
					AddEquipment(new CustomizedEquipment
					{
						EquipmentOption = EquipmentDatabase.RandomAnimalEquipmentOption,
						Count = privateField,
						SpawnType = EquipmentSpawnType.Animal
					});
					State.ReplacedScenarioParts.Add(allPart);
				}
			}
			if (!(allPart is ScenPart_StartingMech))
			{
				continue;
			}
			PawnKindDef privateField3 = allPart.GetPrivateField<PawnKindDef>("mechKind");
			float privateField4 = allPart.GetPrivateField<float>("overseenByPlayerPawnChance");
			if (privateField3 != null && privateField3.race != null)
			{
				EquipmentDatabase.PreloadDefinition(privateField3.race);
				EquipmentOption equipmentOption4 = EquipmentDatabase.FindOptionForThingDef(privateField3.race);
				if (equipmentOption4 != null)
				{
					AddEquipment(new CustomizedEquipment
					{
						EquipmentOption = equipmentOption4,
						Count = 1,
						SpawnType = EquipmentSpawnType.Mech,
						OverseenChance = privateField4
					});
					State.ReplacedScenarioParts.Add(allPart);
				}
			}
			else if (EquipmentDatabase.RandomMechEquipmentOption != null)
			{
				AddEquipment(new CustomizedEquipment
				{
					EquipmentOption = EquipmentDatabase.RandomMechEquipmentOption,
					Count = 1,
					SpawnType = EquipmentSpawnType.Mech,
					OverseenChance = privateField4
				});
				State.ReplacedScenarioParts.Add(allPart);
			}
		}
	}

	public bool AddEquipment(CustomizedEquipment equipment)
	{
		if (equipment == null || equipment.EquipmentOption == null)
		{
			return false;
		}
		if (!equipment.SpawnType.HasValue || equipment.EquipmentOption.RestrictedSpawnType)
		{
			equipment.SpawnType = equipment.EquipmentOption.DefaultSpawnType;
		}
		CustomizedEquipment customizedEquipment = FindMatchingEquipment(equipment);
		if (customizedEquipment == null)
		{
			State.Customizations.Equipment.Add(equipment);
			this.CostAffected?.Invoke();
			return true;
		}
		customizedEquipment.Count += equipment.Count;
		this.CostAffected?.Invoke();
		return false;
	}

	public CustomizedEquipment FindMatchingEquipment(CustomizedEquipment entry)
	{
		return State.Customizations.Equipment.Find((CustomizedEquipment e) => object.Equals(e, entry));
	}

	public void UpdateEquipmentCount(CustomizedEquipment equipment, int count)
	{
		if (count >= 0)
		{
			equipment.Count = count;
			this.CostAffected?.Invoke();
		}
	}

	public void RemoveEquipment(CustomizedEquipment equipment)
	{
		State.Customizations.Equipment.Remove(equipment);
		this.CostAffected?.Invoke();
	}

	public void ClearEquipment()
	{
		State.Customizations.Equipment.Clear();
	}
}
